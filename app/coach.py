"""
Core coaching logic with guardrails and LLM integration.

Provides the main suggest() function for generating compliant rewrites.
"""

import os
import re
import time
import random
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass

from engine.rules import RulesEngine, PolicyHit, get_rules_engine, redact_pii
from app.providers.provider_manager import call_llm, get_last_provider_used


@dataclass
class SuggestionResponse:
    """Response from coach suggestion."""
    suggestion: str
    alternates: List[str]
    rationale: str
    policy_refs: List[str]
    confidence: float
    evidence_spans: List[Tuple[int, int]]
    latency_ms: int
    used_safe_template: bool = False


class CoachGuardrails:
    """Guardrails for input/output validation."""
    
    MAX_SUGGESTION_LENGTH = 240
    MAX_SENTENCES = 2
    MIN_CONFIDENCE = 0.3
    
    @staticmethod
    def is_pii_blocked(text: str) -> bool:
        """Check if text contains PII that should block LLM processing."""
        engine = get_rules_engine()
        return engine.contains_pii(text)
    
    @staticmethod
    def validate_output_length(text: str) -> bool:
        """Validate that output meets length constraints."""
        if len(text) > CoachGuardrails.MAX_SUGGESTION_LENGTH:
            return False
        
        # Count sentences (rough heuristic)
        sentences = len(re.findall(r'[.!?]+', text))
        if sentences > CoachGuardrails.MAX_SENTENCES:
            return False
        
        return True
    
    @staticmethod
    def contains_rude_terms(text: str) -> bool:
        """Check if text contains rude/inappropriate terms."""
        rude_patterns = [
            r'\bidiot\b', r'\bstupid\b', r'\bshut up\b',
            r'\bdumb\b', r'\bmoron\b', r'\bfool\b'
        ]
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in rude_patterns)
    
    @staticmethod
    def still_violates_policy(text: str, policy_ids: List[str]) -> bool:
        """Check if text still violates the given policies."""
        engine = get_rules_engine()
        hits = engine.find_policy_hits(text)
        
        # Check if any of the original policy violations are still present
        for hit in hits:
            if hit.policy_id in policy_ids and hit.matched_pattern != "<missing_disclosure>":
                return True
        
        return False


def _check_pii_leakage(original: str, suggestion: str, violations: List[str]) -> bool:
    """
    Check if LLM response leaked PII from the original text.
    
    Args:
        original: Original agent draft (may contain PII)
        suggestion: LLM's suggested rewrite
        violations: List of policy violations detected
        
    Returns:
        True if PII was leaked into the suggestion
    """
    # If no PII violations, skip check
    if not any("PII" in v for v in violations):
        return False
    
    # Extract SSN patterns (with or without dashes)
    ssn_pattern = r'\b\d{3}-?\d{2}-?\d{4}\b'
    
    # Find all SSNs in original
    original_ssns = set(re.findall(ssn_pattern, original))
    if not original_ssns:
        return False
    
    # Check if ANY SSN or partial appears in suggestion
    for ssn in original_ssns:
        # Remove dashes for flexible matching
        ssn_digits = ssn.replace('-', '')
        
        # Check for full SSN (with or without dashes)
        if ssn in suggestion or ssn_digits in suggestion:
            return True
        
        # Check for partial SSN (last 4, middle 2, etc.)
        # Extract groups: XXX-YY-ZZZZ
        if len(ssn_digits) == 9:
            last_4 = ssn_digits[-4:]
            middle_2 = ssn_digits[3:5]
            first_3 = ssn_digits[:3]
            
            if last_4 in suggestion or middle_2 in suggestion or first_3 in suggestion:
                return True
    
    return False


# DEPRECATED: Hardcoded fallbacks removed - now relying purely on LLM responses
# def _generate_safe_fallback(violations: List[str]) -> SuggestionResponse:
#     """
#     Generate a safe fallback response when PII leaks or other critical issues occur.
#     
#     Args:
#         violations: List of policy violations detected
#         
#     Returns:
#         SuggestionResponse with safe, pre-approved content
#     """
#     # Determine primary violation type
#     primary_policy = "UNKNOWN"
#     if violations:
#         if any("PII" in v for v in violations):
#             primary_policy = "PII-SSN"
#         elif any("ADV" in v for v in violations):
#             primary_policy = "ADV-6.2"
#         elif any("DISC" in v for v in violations):
#             primary_policy = "DISC-1.1"
#         elif any("TONE" in v for v in violations):
#             primary_policy = "TONE"
#     
#     safe_text = get_safe_template(primary_policy)
#     
#     return SuggestionResponse(
#         suggestion=safe_text,
#         alternates=[safe_text, safe_text],
#         rationale=f"PII leakage detected in LLM response. Using safe template for {primary_policy}.",
#         policy_refs=violations,
#         confidence=1.0,
#         evidence_spans=[(0, 0)],
#         latency_ms=0,
#         used_safe_template=True
#     )


# DEPRECATED: Hardcoded templates removed - now relying purely on LLM responses
# def get_safe_template(policy_id: str = "UNKNOWN") -> str:
#     """
#     Return a safe fallback template for blocked cases.
#     
#     Used when PII is detected or LLM fails. Now returns policy-specific fallbacks.
#     
#     Args:
#         policy_id: The policy violation type (e.g., PII-SSN, ADV-6.2)
#         
#     Returns:
#         A safe, pre-approved response for the given policy type
#     """
#     # Policy-specific safe responses
#     fallbacks = {
#         "PII-SSN": "I've verified your information successfully. How can I help you today?",
#         "ADV-6.2": "Past performance isn't indicative of future results. Would you like to discuss your current investment goals?",
#         "DISC-1.1": "For transparency, we can't guarantee specific returns. Investments may lose value; I can share the risk overview if helpful.",
#         "TONE": "I understand your concern. Let me provide clear information to help.",
#     }
#     
#     # Return specific fallback or default
#     return fallbacks.get(policy_id, fallbacks["DISC-1.1"])


def load_prompt_template() -> str:
    """Load the coach prompt template from file. Tries v3_enhanced first, then v2, then v1."""
    # Try v3_enhanced (best of v2 + v3) first
    template_v3_enhanced_path = Path(__file__).parent / "prompts" / "coach_prompt_v3_enhanced.txt"
    if template_v3_enhanced_path.exists():
        with open(template_v3_enhanced_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Fallback to v2 (PII-aware)
    template_v2_path = Path(__file__).parent / "prompts" / "coach_prompt_v2.txt"
    if template_v2_path.exists():
        with open(template_v2_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Final fallback to v1
    template_path = Path(__file__).parent / "prompts" / "coach_prompt_v1.txt"
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def build_prompt(
    agent_draft: str,
    context: str,
    policy_hits: List[str],
    brand_tone: str,
    required_disclosures: List[str]
) -> Dict[str, str]:
    """
    Build the prompt for the LLM.
    
    Args:
        agent_draft: The risky agent draft text
        context: Additional context about the conversation
        policy_hits: List of policy IDs that were violated
        brand_tone: Desired brand tone
        required_disclosures: Required disclosure phrases
        
    Returns:
        Dict with 'system' and 'user' prompts
    """
    template = load_prompt_template()
    
    # Build policies summary
    engine = get_rules_engine()
    policies_summary = []
    for policy_id in policy_hits:
        policy = engine.get_policy_by_id(policy_id)
        if policy:
            policies_summary.append(f"- {policy.id}: {policy.name} (severity: {policy.severity})")
    
    policies_text = "\n".join(policies_summary) if policies_summary else "No specific policies triggered"
    
    # Get first disclosure or default
    disclosure_text = required_disclosures[0] if required_disclosures else "Investments may lose value."
    
    # Enhance context to make responses more situational
    enhanced_context = context if context else "General inquiry"
    
    # Fill template
    prompt = template.format(
        brand_tone=brand_tone,
        policies_summary=policies_text,
        disclosure_text=disclosure_text,
        agent_draft=agent_draft,
        context=enhanced_context
    )
    
    # Add context-specific guidance to make responses more dynamic
    if context:
        prompt += f"\n\nIMPORTANT: The customer's situation is: '{context}'. Tailor your response to address this specific context while remaining compliant."
    
    return {
        "system": "You are a compliance QA coach for financial support. Return STRICT JSON only.",
        "user": prompt
    }


def inject_disclosure_if_needed(suggestion: str, agent_draft: str) -> str:
    """
    Inject disclosure if the suggestion talks about returns/investments but lacks disclosure.
    
    Args:
        suggestion: The suggested rewrite
        agent_draft: Original agent draft
        
    Returns:
        Suggestion with disclosure injected if needed
    """
    engine = get_rules_engine()
    
    # Check if we're talking about financial topics
    if not engine.requires_disclosure(suggestion):
        return suggestion
    
    # Check if disclosure is already present
    if engine.has_disclosure(suggestion):
        return suggestion
    
    # Inject disclosure
    disclosure_phrases = engine.get_disclosure_phrases()
    if disclosure_phrases:
        # Use a shortened version for brevity
        disclosure = "Investments may lose value."
        return f"{suggestion} {disclosure}"
    
    return suggestion


def suggest(
    agent_draft: str,
    context: str = "",
    policy_hits: Optional[List[str]] = None,
    brand_tone: str = "professional, clear, empathetic",
    required_disclosures: Optional[List[str]] = None
) -> SuggestionResponse:
    """
    Generate a compliant suggestion for a risky agent draft.
    
    NEW BEHAVIOR: Redacts PII before sending to LLM, lets LLM handle all rewrites.
    No more hardcoded fallback templates.
    
    Args:
        agent_draft: The agent's draft message that may have compliance issues
        context: Additional context about the conversation
        policy_hits: List of policy IDs that were violated (if known)
        brand_tone: Desired brand tone for suggestions
        required_disclosures: Required disclosure phrases
        
    Returns:
        SuggestionResponse with suggestion, alternates, rationale, etc.
    """
    start_time = time.time()
    
    if policy_hits is None:
        policy_hits = []
    if required_disclosures is None:
        required_disclosures = []
    
    # NEW: Redact PII before processing instead of blocking
    redacted_draft, redaction_map = redact_pii(agent_draft)
    has_pii = len(redaction_map) > 0
    
    if has_pii:
        print(f"🔒 PII detected and redacted: {list(redaction_map.keys())}")
    
    # Detect policy hits if not provided (use redacted version)
    if not policy_hits:
        engine = get_rules_engine()
        hits = engine.find_policy_hits(redacted_draft)
        policy_hits = list(set([h.policy_id for h in hits]))
        evidence_spans = [(h.span[0], h.span[1]) for h in hits if h.span != (0, 0)]
    else:
        # Build evidence spans from detected patterns
        engine = get_rules_engine()
        all_hits = engine.find_policy_hits(redacted_draft)
        evidence_spans = [(h.span[0], h.span[1]) for h in all_hits if h.policy_id in policy_hits and h.span != (0, 0)]
    
    if not evidence_spans:
        evidence_spans = [(0, 0)]
    
    # Build prompt with REDACTED version
    prompt_dict = build_prompt(redacted_draft, context, policy_hits, brand_tone, required_disclosures)
    
    # Call LLM with retry logic - LLM now handles ALL cases
    try:
        response = call_llm(prompt_dict)
        provider_used = get_last_provider_used()
        
        # Extract fields with defaults
        suggestion = response.get("suggestion", "")
        alternates = response.get("alternates", [])
        rationale = response.get("rationale", "")
        policy_refs = response.get("policy_refs", policy_hits)
        confidence = float(response.get("confidence", 0.5))
        
        # Ensure we have 2 alternates
        while len(alternates) < 2:
            alternates.append(suggestion)
        alternates = alternates[:2]
        
        # ENHANCEMENT: Rotate through all suggestions for variety
        # Collect all valid options (primary + alternates)
        all_suggestions = [suggestion] + alternates
        
        # Filter out duplicates and empty strings
        unique_suggestions = []
        seen = set()
        for s in all_suggestions:
            if s and s not in seen:
                unique_suggestions.append(s)
                seen.add(s)
        
        # Use a different suggestion each time for variety (60% chance to rotate)
        if len(unique_suggestions) > 1 and random.random() > 0.4:
            # Pick a random alternate
            chosen_idx = random.randint(0, len(unique_suggestions) - 1)
            suggestion = unique_suggestions[chosen_idx]
            # Rearrange alternates
            alternates = [s for i, s in enumerate(unique_suggestions) if i != chosen_idx][:2]
        
        # CRITICAL: Validate LLM didn't leak the redacted placeholders
        for placeholder in redaction_map.keys():
            if placeholder in suggestion:
                raise ValueError(f"LLM leaked PII placeholder: {placeholder}")
        
    except Exception as e:
        # On LLM failure, raise error - no hardcoded fallbacks
        print(f"❌ LLM call failed: {e}")
        # Return a minimal error response
        latency_ms = int((time.time() - start_time) * 1000)
        return SuggestionResponse(
            suggestion="I apologize, but I'm unable to process this request at the moment. Please try again.",
            alternates=["I'm experiencing technical difficulties. Please retry your request.", 
                       "System temporarily unavailable. Please try again shortly."],
            rationale=f"LLM error: {str(e)}",
            policy_refs=policy_hits,
            confidence=0.0,
            evidence_spans=evidence_spans,
            latency_ms=latency_ms,
            used_safe_template=False
        )
    
    # Guardrail 2: Validate output length and content
    if not CoachGuardrails.validate_output_length(suggestion):
        # Truncate to first sentence or max length
        suggestion = suggestion[:CoachGuardrails.MAX_SUGGESTION_LENGTH]
        if '.' in suggestion:
            suggestion = suggestion[:suggestion.index('.') + 1]
    
    # Guardrail 3: Check for rude terms in output (shouldn't happen with good LLM)
    if CoachGuardrails.contains_rude_terms(suggestion):
        # Try first alternate instead
        if alternates and not CoachGuardrails.contains_rude_terms(alternates[0]):
            suggestion = alternates[0]
        else:
            # Ask LLM to try again
            print(f"⚠️ Rude terms detected in LLM output: {suggestion}")
            suggestion = "I'd be happy to help you with that. Let me provide some information."
    
    # Guardrail 4: Verify suggestion doesn't still violate policies
    if CoachGuardrails.still_violates_policy(suggestion, policy_hits):
        # Try first alternate
        if alternates and not CoachGuardrails.still_violates_policy(alternates[0], policy_hits):
            suggestion = alternates[0]
        else:
            print(f"⚠️ Suggestion still violates policy: {suggestion}")
            # Use generic professional response
            suggestion = "I understand your question. Let me provide you with accurate information about this."
    
    # Post-process: Inject disclosure if needed
    suggestion = inject_disclosure_if_needed(suggestion, agent_draft)
    alternates = [inject_disclosure_if_needed(alt, agent_draft) for alt in alternates]
    
    latency_ms = int((time.time() - start_time) * 1000)
    
    return SuggestionResponse(
        suggestion=suggestion,
        alternates=alternates,
        rationale=rationale,
        policy_refs=policy_refs,
        confidence=confidence,
        evidence_spans=evidence_spans,
        latency_ms=latency_ms,
        used_safe_template=False
    )
