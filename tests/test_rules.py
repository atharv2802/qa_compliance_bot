"""
Unit tests for rules engine.
"""

import pytest
from engine.rules import RulesEngine, PolicyHit, find_policy_hits, contains_pii, requires_disclosure


@pytest.fixture
def rules_engine():
    """Create a rules engine instance for testing."""
    return RulesEngine()


class TestPolicyDetection:
    """Tests for policy violation detection."""
    
    def test_guaranteed_returns_detection(self, rules_engine):
        """Test detection of guaranteed returns language."""
        text = "We guarantee 12% returns on your investment."
        hits = rules_engine.find_policy_hits(text)
        
        assert len(hits) > 0
        adv_hits = [h for h in hits if h.policy_id == "ADV-6.2"]
        assert len(adv_hits) > 0
        assert "guarantee" in adv_hits[0].matched_pattern.lower()
    
    def test_risk_free_detection(self, rules_engine):
        """Test detection of risk-free claims."""
        text = "This is a risk-free investment opportunity."
        hits = rules_engine.find_policy_hits(text)
        
        adv_hits = [h for h in hits if h.policy_id == "ADV-6.2"]
        assert len(adv_hits) > 0
        assert "risk" in adv_hits[0].matched_pattern.lower()
    
    def test_no_violation_clean_text(self, rules_engine):
        """Test that clean text doesn't trigger false positives."""
        text = "I can share our historical performance data and explain the risks."
        hits = rules_engine.find_policy_hits(text)
        
        # Should only trigger missing disclosure, not ADV-6.2
        adv_hits = [h for h in hits if h.policy_id == "ADV-6.2"]
        assert len(adv_hits) == 0


class TestPIIDetection:
    """Tests for PII detection."""
    
    def test_ssn_with_dashes(self, rules_engine):
        """Test detection of SSN with dashes."""
        text = "My SSN is 123-45-6789 for verification."
        hits = rules_engine.find_policy_hits(text)
        
        pii_hits = [h for h in hits if h.policy_id == "PII-SSN"]
        assert len(pii_hits) > 0
        assert "123-45-6789" in pii_hits[0].matched_pattern
    
    def test_ssn_without_dashes(self, rules_engine):
        """Test detection of 9-digit SSN."""
        text = "My social security number is 123456789."
        hits = rules_engine.find_policy_hits(text)
        
        pii_hits = [h for h in hits if h.policy_id == "PII-SSN"]
        assert len(pii_hits) > 0
    
    def test_contains_pii_function(self, rules_engine):
        """Test the contains_pii convenience function."""
        assert rules_engine.contains_pii("SSN: 123-45-6789") is True
        assert rules_engine.contains_pii("Call me at 555-1234") is False
    
    def test_no_pii_clean_text(self, rules_engine):
        """Test that numbers that aren't SSNs don't trigger PII."""
        text = "Our account number is 12345."
        assert rules_engine.contains_pii(text) is False


class TestToneDetection:
    """Tests for inappropriate tone detection."""
    
    def test_rude_language_detection(self, rules_engine):
        """Test detection of rude language."""
        rude_texts = [
            "Don't be an idiot about this.",
            "That's a stupid question.",
            "Just shut up and listen."
        ]
        
        for text in rude_texts:
            hits = rules_engine.find_policy_hits(text)
            tone_hits = [h for h in hits if h.policy_id == "TONE"]
            assert len(tone_hits) > 0, f"Failed to detect tone issue in: {text}"
    
    def test_professional_tone_ok(self, rules_engine):
        """Test that professional language doesn't trigger tone violations."""
        text = "I understand your concern. Let me explain the details."
        hits = rules_engine.find_policy_hits(text)
        
        tone_hits = [h for h in hits if h.policy_id == "TONE"]
        assert len(tone_hits) == 0


class TestDisclosureRequirements:
    """Tests for disclosure requirement detection."""
    
    def test_requires_disclosure_with_investment_terms(self, rules_engine):
        """Test that investment language triggers disclosure requirement."""
        text = "Our fund has shown strong returns over the past year."
        assert rules_engine.requires_disclosure(text) is True
    
    def test_requires_disclosure_with_risk_terms(self, rules_engine):
        """Test that risk language triggers disclosure requirement."""
        text = "There is some risk involved in this strategy."
        assert rules_engine.requires_disclosure(text) is True
    
    def test_no_disclosure_for_general_text(self, rules_engine):
        """Test that general text doesn't require disclosure."""
        text = "Thank you for your inquiry. How can I help?"
        assert rules_engine.requires_disclosure(text) is False
    
    def test_has_disclosure_detection(self, rules_engine):
        """Test detection of disclosure phrases."""
        text = "Returns may vary. This is not financial advice."
        assert rules_engine.has_disclosure(text) is True
        
        text_no_disclosure = "We expect good performance."
        assert rules_engine.has_disclosure(text_no_disclosure) is False


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""
    
    def test_find_policy_hits_function(self):
        """Test the find_policy_hits convenience function."""
        text = "We guarantee profits."
        hits = find_policy_hits(text)
        assert len(hits) > 0
    
    def test_contains_pii_function(self):
        """Test the contains_pii convenience function."""
        assert contains_pii("SSN: 123-45-6789") is True
        assert contains_pii("No PII here") is False
    
    def test_requires_disclosure_function(self):
        """Test the requires_disclosure convenience function."""
        assert requires_disclosure("Our investment returns") is True
        assert requires_disclosure("Hello there") is False


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_text(self, rules_engine):
        """Test handling of empty text."""
        hits = rules_engine.find_policy_hits("")
        # Should only have missing disclosure hit
        assert all(h.policy_id in ["DISC-1.1"] for h in hits) or len(hits) == 0
    
    def test_case_insensitive_matching(self, rules_engine):
        """Test that pattern matching is case-insensitive."""
        texts = [
            "We GUARANTEE returns.",
            "we guarantee returns.",
            "We Guarantee Returns."
        ]
        
        for text in texts:
            hits = rules_engine.find_policy_hits(text)
            adv_hits = [h for h in hits if h.policy_id == "ADV-6.2"]
            assert len(adv_hits) > 0, f"Failed case-insensitive match: {text}"
    
    def test_multiple_violations_same_policy(self, rules_engine):
        """Test detection of multiple violations of the same policy."""
        text = "We guarantee profits and guarantee returns with risk-free investing."
        hits = rules_engine.find_policy_hits(text)
        
        adv_hits = [h for h in hits if h.policy_id == "ADV-6.2"]
        assert len(adv_hits) >= 2  # Should detect multiple violations
    
    def test_span_positions(self, rules_engine):
        """Test that span positions are correct."""
        text = "We guarantee returns."
        hits = rules_engine.find_policy_hits(text)
        
        adv_hits = [h for h in hits if h.policy_id == "ADV-6.2"]
        if adv_hits:
            hit = adv_hits[0]
            assert hit.span[0] < hit.span[1]
            assert text[hit.span[0]:hit.span[1]].lower() in hit.matched_pattern.lower()


class TestPolicyMetadata:
    """Tests for policy metadata access."""
    
    def test_get_policy_by_id(self, rules_engine):
        """Test retrieving policy by ID."""
        policy = rules_engine.get_policy_by_id("ADV-6.2")
        assert policy is not None
        assert policy.id == "ADV-6.2"
        assert policy.severity == "high"
    
    def test_get_nonexistent_policy(self, rules_engine):
        """Test retrieving non-existent policy."""
        policy = rules_engine.get_policy_by_id("NONEXISTENT")
        assert policy is None
    
    def test_get_disclosure_phrases(self, rules_engine):
        """Test getting disclosure phrases."""
        phrases = rules_engine.get_disclosure_phrases()
        assert len(phrases) > 0
        assert any("financial advice" in p.lower() for p in phrases)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
