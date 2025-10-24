"""
Tests for coach guardrails and core functionality.
"""

import pytest
from app.coach import (
    CoachGuardrails,
    get_safe_template,
    build_prompt,
    inject_disclosure_if_needed,
    suggest
)


class TestGuardrails:
    """Tests for guardrail validations."""
    
    def test_pii_blocking(self):
        """Test that PII is detected and blocks processing."""
        text_with_ssn = "My SSN is 123-45-6789"
        assert CoachGuardrails.is_pii_blocked(text_with_ssn) is True
        
        text_without_pii = "Let me help you with that"
        assert CoachGuardrails.is_pii_blocked(text_without_pii) is False
    
    def test_output_length_validation(self):
        """Test output length constraints."""
        # Valid length
        short_text = "This is a valid response."
        assert CoachGuardrails.validate_output_length(short_text) is True
        
        # Too long
        long_text = "x" * 300
        assert CoachGuardrails.validate_output_length(long_text) is False
        
        # Too many sentences
        many_sentences = ". ".join(["Sentence"] * 5) + "."
        assert CoachGuardrails.validate_output_length(many_sentences) is False
    
    def test_rude_terms_detection(self):
        """Test detection of inappropriate language."""
        rude_texts = [
            "Don't be an idiot",
            "That's stupid",
            "Just shut up"
        ]
        
        for text in rude_texts:
            assert CoachGuardrails.contains_rude_terms(text) is True
        
        polite_text = "I understand your concern"
        assert CoachGuardrails.contains_rude_terms(polite_text) is False
    
    def test_still_violates_policy(self):
        """Test that rewritten text is validated against policies."""
        # Text that still violates
        text = "We guarantee 10% returns"
        assert CoachGuardrails.still_violates_policy(text, ["ADV-6.2"]) is True
        
        # Compliant text
        compliant = "Returns may vary based on market conditions"
        assert CoachGuardrails.still_violates_policy(compliant, ["ADV-6.2"]) is False


class TestSafeTemplate:
    """Tests for safe template fallback."""
    
    def test_safe_template_returned(self):
        """Test that safe template is valid."""
        template = get_safe_template()
        assert len(template) > 0
        assert "guarantee" not in template.lower() or "can't guarantee" in template.lower()
        assert len(template) <= CoachGuardrails.MAX_SUGGESTION_LENGTH


class TestPromptBuilding:
    """Tests for prompt construction."""
    
    def test_build_prompt_structure(self):
        """Test that prompt is built correctly."""
        prompt = build_prompt(
            agent_draft="We guarantee profits",
            context="Customer asking about returns",
            policy_hits=["ADV-6.2"],
            brand_tone="professional",
            required_disclosures=["Investments may lose value"]
        )
        
        assert "system" in prompt
        assert "user" in prompt
        assert "ADV-6.2" in prompt["user"]
        assert "We guarantee profits" in prompt["user"]
        assert "professional" in prompt["user"]
    
    def test_build_prompt_no_policy_hits(self):
        """Test prompt building with no policy violations."""
        prompt = build_prompt(
            agent_draft="Hello, how can I help?",
            context="",
            policy_hits=[],
            brand_tone="friendly",
            required_disclosures=[]
        )
        
        assert "system" in prompt
        assert "user" in prompt


class TestDisclosureInjection:
    """Tests for automatic disclosure injection."""
    
    def test_disclosure_injected_when_needed(self):
        """Test that disclosure is added when talking about investments."""
        suggestion = "Our fund has shown good returns historically."
        result = inject_disclosure_if_needed(suggestion, "investment returns")
        
        # Should add disclosure
        assert len(result) > len(suggestion)
        assert "may lose value" in result.lower() or "not financial advice" in result.lower()
    
    def test_disclosure_not_duplicated(self):
        """Test that disclosure is not added if already present."""
        suggestion = "Returns vary. Investments may lose value."
        result = inject_disclosure_if_needed(suggestion, "returns")
        
        # Should not add duplicate
        assert result.count("may lose value") == 1
    
    def test_no_disclosure_for_general_text(self):
        """Test that non-financial text doesn't get disclosure."""
        suggestion = "Thank you for contacting us."
        result = inject_disclosure_if_needed(suggestion, "general inquiry")
        
        # Should not add disclosure
        assert result == suggestion


class TestSuggestFunction:
    """Integration tests for the main suggest() function."""
    
    def test_suggest_with_pii_returns_safe_template(self):
        """Test that PII in draft triggers safe template."""
        response = suggest(
            agent_draft="Your SSN 123-45-6789 is verified",
            context="Verification"
        )
        
        assert response.used_safe_template is True
        assert "PII-SSN" in response.policy_refs
        assert response.confidence >= 0.9
    
    def test_suggest_basic_violation(self):
        """Test basic suggestion flow."""
        response = suggest(
            agent_draft="We guarantee 15% returns every year",
            context="Customer asking about returns",
            policy_hits=["ADV-6.2"]
        )
        
        # Should return a suggestion
        assert len(response.suggestion) > 0
        assert len(response.alternates) == 2
        assert len(response.rationale) > 0
        assert "ADV-6.2" in response.policy_refs
        
        # Suggestion should not violate policy
        assert "guarantee" not in response.suggestion.lower()
    
    def test_suggest_with_clean_text(self):
        """Test that clean text gets minimal changes."""
        response = suggest(
            agent_draft="I can share our historical performance and risk factors.",
            context="Customer inquiry"
        )
        
        assert len(response.suggestion) > 0
        assert response.confidence > 0.3
    
    def test_suggest_output_constraints(self):
        """Test that output meets length and format constraints."""
        response = suggest(
            agent_draft="We absolutely guarantee you'll make money with zero risk whatsoever.",
            context="Sales pitch"
        )
        
        # Check length constraints
        assert len(response.suggestion) <= CoachGuardrails.MAX_SUGGESTION_LENGTH
        
        # Check we have alternates
        assert len(response.alternates) == 2
        for alt in response.alternates:
            assert len(alt) <= CoachGuardrails.MAX_SUGGESTION_LENGTH
    
    def test_suggest_latency_tracked(self):
        """Test that latency is tracked."""
        response = suggest(
            agent_draft="Test draft",
            context=""
        )
        
        assert response.latency_ms > 0
    
    def test_suggest_with_multiple_policy_hits(self):
        """Test handling of multiple policy violations."""
        response = suggest(
            agent_draft="Don't be stupid, we guarantee profits.",
            context="",
            policy_hits=["ADV-6.2", "TONE"]
        )
        
        # Should address both violations
        assert len(response.policy_refs) >= 1
        assert "guarantee" not in response.suggestion.lower()
        assert not CoachGuardrails.contains_rude_terms(response.suggestion)


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_agent_draft(self):
        """Test handling of empty draft."""
        response = suggest(
            agent_draft="",
            context=""
        )
        
        assert len(response.suggestion) > 0
    
    def test_very_long_agent_draft(self):
        """Test handling of very long draft."""
        long_draft = "We guarantee returns. " * 50
        response = suggest(
            agent_draft=long_draft,
            context=""
        )
        
        assert len(response.suggestion) > 0
        assert len(response.suggestion) <= CoachGuardrails.MAX_SUGGESTION_LENGTH
    
    def test_special_characters_in_draft(self):
        """Test handling of special characters."""
        response = suggest(
            agent_draft="We guarantee 100% returns!!! $$$",
            context=""
        )
        
        assert len(response.suggestion) > 0
    
    def test_unicode_in_draft(self):
        """Test handling of unicode characters."""
        response = suggest(
            agent_draft="We guarantee great returns 🚀💰",
            context=""
        )
        
        assert len(response.suggestion) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
