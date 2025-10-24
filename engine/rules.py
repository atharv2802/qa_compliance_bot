"""
Rules engine for policy detection and compliance checking.

Loads policies from YAML and provides:
- find_policy_hits(text): Detect policy violations in text
- contains_pii(text): Check for PII patterns
- requires_disclosure(text): Check if disclosure is required
"""

import re
import yaml
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class PolicyHit:
    """Represents a detected policy violation."""
    policy_id: str
    policy_name: str
    severity: str
    matched_pattern: str
    span: tuple[int, int]  # Start and end positions in text


@dataclass
class Policy:
    """Represents a compliance policy."""
    id: str
    name: str
    severity: str
    patterns: List[str] = None
    required_phrases: List[str] = None
    
    def __post_init__(self):
        if self.patterns is None:
            self.patterns = []
        if self.required_phrases is None:
            self.required_phrases = []


class RulesEngine:
    """Engine for detecting policy violations using regex patterns."""
    
    def __init__(self, policies_path: Optional[str] = None):
        """Initialize the rules engine with policies from YAML file."""
        if policies_path is None:
            policies_path = Path(__file__).parent.parent / "policies" / "policies.yaml"
        else:
            policies_path = Path(policies_path)
        
        self.policies = self._load_policies(policies_path)
        self.pii_policy_ids = ["PII-SSN"]  # Critical PII policies
        self.disclosure_policy_ids = ["DISC-1.1"]  # Disclosure requirements
    
    def _load_policies(self, path: Path) -> List[Policy]:
        """Load policies from YAML file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        policies = []
        for p in data.get('policies', []):
            policy = Policy(
                id=p['id'],
                name=p['name'],
                severity=p['severity'],
                patterns=p.get('patterns', []),
                required_phrases=p.get('required_phrases', [])
            )
            policies.append(policy)
        
        return policies
    
    def find_policy_hits(self, text: str) -> List[PolicyHit]:
        """
        Find all policy violations in the given text.
        
        Args:
            text: The text to check for policy violations
            
        Returns:
            List of PolicyHit objects with violation details
        """
        hits = []
        text_lower = text.lower()
        
        for policy in self.policies:
            # Check pattern-based policies
            for pattern in policy.patterns:
                try:
                    regex = re.compile(pattern, re.IGNORECASE)
                    for match in regex.finditer(text):
                        hit = PolicyHit(
                            policy_id=policy.id,
                            policy_name=policy.name,
                            severity=policy.severity,
                            matched_pattern=match.group(0),
                            span=(match.start(), match.end())
                        )
                        hits.append(hit)
                except re.error as e:
                    # Log pattern compilation errors but continue
                    print(f"Warning: Invalid regex pattern in {policy.id}: {pattern} - {e}")
            
            # Check required phrase policies (inverse logic - violation if missing)
            if policy.required_phrases:
                has_required = any(
                    phrase.lower() in text_lower 
                    for phrase in policy.required_phrases
                )
                if not has_required:
                    # Create a pseudo-hit indicating missing disclosure
                    hit = PolicyHit(
                        policy_id=policy.id,
                        policy_name=policy.name,
                        severity=policy.severity,
                        matched_pattern="<missing_disclosure>",
                        span=(0, 0)
                    )
                    hits.append(hit)
        
        return hits
    
    def contains_pii(self, text: str) -> bool:
        """
        Check if text contains PII patterns (e.g., SSN).
        
        Args:
            text: The text to check
            
        Returns:
            True if PII is detected, False otherwise
        """
        hits = self.find_policy_hits(text)
        return any(hit.policy_id in self.pii_policy_ids for hit in hits)
    
    def redact_pii(self, text: str) -> tuple[str, dict]:
        """
        Redact PII from text, replacing with descriptive placeholders.
        
        Args:
            text: The text to redact
            
        Returns:
            Tuple of (redacted_text, redaction_map)
            redaction_map contains {placeholder: original_value} for restoration if needed
        """
        redacted = text
        redaction_map = {}
        
        # Redact SSN patterns (XXX-XX-XXXX or XXXXXXXXX)
        ssn_pattern = r'\b\d{3}-?\d{2}-?\d{4}\b'
        ssn_matches = list(re.finditer(ssn_pattern, redacted))
        
        for i, match in enumerate(ssn_matches, 1):
            ssn_value = match.group()
            placeholder = f"[SSN_REDACTED_{i}]"
            redaction_map[placeholder] = ssn_value
            redacted = redacted[:match.start()] + placeholder + redacted[match.end():]
        
        # Redact account numbers (6-12 digits, not already matched as SSN)
        # Avoid matching phone numbers by requiring word boundaries or spaces
        account_pattern = r'\b(?:account|acct)[\s#:]*(\d{6,12})\b'
        account_matches = list(re.finditer(account_pattern, redacted, re.IGNORECASE))
        
        for i, match in enumerate(account_matches, 1):
            account_value = match.group(1)
            placeholder = f"[ACCOUNT_REDACTED_{i}]"
            # Only replace the number part, keep the "account" prefix
            redacted = redacted[:match.start(1)] + placeholder + redacted[match.end(1):]
            redaction_map[placeholder] = account_value
        
        return redacted, redaction_map
    
    def requires_disclosure(self, text: str) -> bool:
        """
        Check if text requires disclosure based on content.
        
        This checks if the text mentions financial topics that would
        trigger disclosure requirements.
        
        Args:
            text: The text to check
            
        Returns:
            True if disclosure is required, False otherwise
        """
        # Keywords that trigger disclosure requirements
        disclosure_triggers = [
            r'\b(return|profit|yield|gain|earning|income)s?\b',
            r'\b(invest(?:ment)?|stock|bond|fund|portfolio)\b',
            r'\b(risk|loss|lose|volatile)\b',
            r'\b(performance|historical)\b'
        ]
        
        text_lower = text.lower()
        for pattern in disclosure_triggers:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def has_disclosure(self, text: str) -> bool:
        """
        Check if text contains required disclosure phrases.
        
        Args:
            text: The text to check
            
        Returns:
            True if disclosure phrases are present, False otherwise
        """
        disclosure_policy = next(
            (p for p in self.policies if p.id in self.disclosure_policy_ids),
            None
        )
        
        if not disclosure_policy or not disclosure_policy.required_phrases:
            return True  # No disclosure requirement
        
        text_lower = text.lower()
        return any(
            phrase.lower() in text_lower 
            for phrase in disclosure_policy.required_phrases
        )
    
    def get_policy_by_id(self, policy_id: str) -> Optional[Policy]:
        """Get a policy by its ID."""
        return next((p for p in self.policies if p.id == policy_id), None)
    
    def get_disclosure_phrases(self) -> List[str]:
        """Get all required disclosure phrases."""
        phrases = []
        for policy in self.policies:
            if policy.id in self.disclosure_policy_ids:
                phrases.extend(policy.required_phrases)
        return phrases


# Global instance for easy import
_engine = None

def get_rules_engine() -> RulesEngine:
    """Get or create the global rules engine instance."""
    global _engine
    if _engine is None:
        _engine = RulesEngine()
    return _engine


# Convenience functions
def find_policy_hits(text: str) -> List[PolicyHit]:
    """Find policy violations in text."""
    return get_rules_engine().find_policy_hits(text)


def contains_pii(text: str) -> bool:
    """Check if text contains PII."""
    return get_rules_engine().contains_pii(text)


def requires_disclosure(text: str) -> bool:
    """Check if text requires disclosure."""
    return get_rules_engine().requires_disclosure(text)


def redact_pii(text: str) -> tuple[str, dict]:
    """Redact PII from text, replacing with placeholders."""
    return get_rules_engine().redact_pii(text)
