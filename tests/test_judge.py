"""
Tests for LLM-as-a-judge evaluation system.
"""

import pytest
from unittest.mock import Mock, patch

from app.evals.judge import Judge, JudgeResponse, evaluate_suggestion, get_judge


class TestJudge:
    """Tests for the Judge class."""
    
    def test_judge_initialization(self):
        """Test that judge initializes with correct provider."""
        with patch.dict("os.environ", {"JUDGE_PROVIDER": "openai", "JUDGE_MODEL": "gpt-4o-mini"}):
            judge = Judge()
            assert judge.provider_name == "openai"
            assert judge.model_name == "gpt-4o-mini"
    
    def test_judge_with_custom_provider(self):
        """Test judge with different provider configurations."""
        with patch.dict("os.environ", {"JUDGE_PROVIDER": "groq", "JUDGE_MODEL": "llama-3.1-8b-instant"}):
            judge = Judge()
            assert judge.provider_name == "groq"
            assert judge.model_name == "llama-3.1-8b-instant"
    
    def test_evaluate_returns_valid_response(self):
        """Test that evaluate returns properly structured response."""
        mock_provider = Mock()
        mock_provider.call_llm.return_value = """{
            "overall_score": 8.5,
            "compliance_score": 9.0,
            "clarity_score": 8.0,
            "tone_score": 8.5,
            "completeness_score": 8.5,
            "feedback": "Good rewrite with minor improvements needed",
            "strengths": ["Clear compliance", "Professional tone"],
            "weaknesses": ["Could be more concise"]
        }"""
        
        with patch.dict("os.environ", {"JUDGE_PROVIDER": "openai"}):
            judge = Judge()
            judge.provider = mock_provider
            
            result = judge.evaluate(
                agent_draft="We guarantee 12% returns.",
                suggestion="Historical performance has varied, and past results don't guarantee future returns.",
                policy_refs=["ADV-6.2"],
                context="Customer asking about returns"
            )
        
        assert isinstance(result, JudgeResponse)
        assert result.overall_score == 8.5
        assert result.compliance_score == 9.0
        assert result.pass_threshold is True
        assert len(result.strengths) == 2
        assert len(result.weaknesses) == 1
    
    def test_evaluate_below_threshold(self):
        """Test that scores below 7.0 fail threshold."""
        mock_provider = Mock()
        mock_provider.call_llm.return_value = """{
            "overall_score": 6.0,
            "compliance_score": 5.0,
            "clarity_score": 7.0,
            "tone_score": 6.0,
            "completeness_score": 6.0,
            "feedback": "Needs significant improvement",
            "strengths": ["Readable"],
            "weaknesses": ["Missing disclosures", "Vague language"]
        }"""
        
        with patch.dict("os.environ", {"JUDGE_PROVIDER": "openai"}):
            judge = Judge()
            judge.provider = mock_provider
            
            result = judge.evaluate(
                agent_draft="Buy now!",
                suggestion="Consider our product.",
                policy_refs=[],
                context=""
            )
        
        assert result.overall_score == 6.0
        assert result.pass_threshold is False
        assert len(result.weaknesses) > 0
    
    def test_evaluate_with_required_disclosures(self):
        """Test evaluation with required disclosures."""
        mock_provider = Mock()
        mock_provider.call_llm.return_value = """{
            "overall_score": 9.0,
            "compliance_score": 9.5,
            "clarity_score": 8.5,
            "tone_score": 9.0,
            "completeness_score": 9.0,
            "feedback": "Excellent rewrite with all disclosures",
            "strengths": ["All disclosures included", "Clear", "Professional"],
            "weaknesses": []
        }"""
        
        with patch.dict("os.environ", {"JUDGE_PROVIDER": "openai"}):
            judge = Judge()
            judge.provider = mock_provider
            
            result = judge.evaluate(
                agent_draft="This is a great investment.",
                suggestion="This product may be suitable for your needs. For important disclosures, visit our website.",
                policy_refs=["DISC-1.1"],
                context="Customer inquiry",
                required_disclosures=["For important disclosures, visit our website."]
            )
        
        assert result.overall_score >= 7.0
        assert result.pass_threshold is True
        assert result.compliance_score >= 9.0
        
        # Verify that required_disclosures was passed to the prompt
        call_args = mock_provider.call_llm.call_args
        assert "Required Disclosures" in call_args[1]["prompt"]
    
    def test_evaluate_handles_malformed_json(self):
        """Test that malformed JSON is handled gracefully."""
        mock_provider = Mock()
        mock_provider.call_llm.return_value = "This is not JSON at all!"
        
        with patch.dict("os.environ", {"JUDGE_PROVIDER": "openai"}):
            judge = Judge()
            judge.provider = mock_provider
            
            result = judge.evaluate(
                agent_draft="Test",
                suggestion="Test suggestion",
                policy_refs=[],
                context=""
            )
        
        assert result.overall_score == 0.0
        assert result.pass_threshold is False
        assert "failed to parse" in result.feedback.lower() or "malformed" in result.feedback.lower()
    
    def test_evaluate_handles_json_in_markdown(self):
        """Test that JSON wrapped in markdown code blocks is extracted."""
        mock_provider = Mock()
        mock_provider.call_llm.return_value = """```json
{
    "overall_score": 7.5,
    "compliance_score": 8.0,
    "clarity_score": 7.0,
    "tone_score": 7.5,
    "completeness_score": 7.5,
    "feedback": "Solid rewrite",
    "strengths": ["Compliant"],
    "weaknesses": []
}
```"""
        
        with patch.dict("os.environ", {"JUDGE_PROVIDER": "openai"}):
            judge = Judge()
            judge.provider = mock_provider
            
            result = judge.evaluate(
                agent_draft="Test",
                suggestion="Test suggestion",
                policy_refs=["TEST"],
                context=""
            )
        
        assert result.overall_score == 7.5
        assert result.pass_threshold is True
    
    def test_judge_prompt_includes_context(self):
        """Test that evaluation prompt includes all necessary context."""
        mock_provider = Mock()
        mock_provider.call_llm.return_value = """{
            "overall_score": 8.0,
            "compliance_score": 8.0,
            "clarity_score": 8.0,
            "tone_score": 8.0,
            "completeness_score": 8.0,
            "feedback": "Good",
            "strengths": ["Clear"],
            "weaknesses": []
        }"""
        
        with patch.dict("os.environ", {"JUDGE_PROVIDER": "openai"}):
            judge = Judge()
            judge.provider = mock_provider
            
            judge.evaluate(
                agent_draft="Original draft",
                suggestion="Suggested rewrite",
                policy_refs=["POLICY-1", "POLICY-2"],
                context="Important context here"
            )
        
        # Verify the prompt contains key elements
        call_args = mock_provider.call_llm.call_args
        prompt = call_args[1]["prompt"]
        
        assert "Original draft" in prompt
        assert "Suggested rewrite" in prompt
        assert "POLICY-1" in prompt
        assert "POLICY-2" in prompt
        assert "Important context here" in prompt
        assert "Compliance" in prompt
        assert "Clarity" in prompt
        assert "Tone" in prompt
        assert "Completeness" in prompt


class TestJudgeConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_get_judge_returns_singleton(self):
        """Test that get_judge returns the same instance."""
        with patch.dict("os.environ", {"JUDGE_PROVIDER": "openai"}):
            judge1 = get_judge()
            judge2 = get_judge()
            assert judge1 is judge2
    
    def test_evaluate_suggestion_convenience_function(self):
        """Test the evaluate_suggestion convenience function."""
        mock_provider = Mock()
        mock_provider.call_llm.return_value = """{
            "overall_score": 8.0,
            "compliance_score": 8.0,
            "clarity_score": 8.0,
            "tone_score": 8.0,
            "completeness_score": 8.0,
            "feedback": "Good suggestion",
            "strengths": ["Compliant", "Clear"],
            "weaknesses": []
        }"""
        
        with patch.dict("os.environ", {"JUDGE_PROVIDER": "openai"}):
            with patch("app.evals.judge.Judge") as MockJudge:
                mock_judge = Mock()
                mock_judge.evaluate.return_value = JudgeResponse(
                    overall_score=8.0,
                    compliance_score=8.0,
                    clarity_score=8.0,
                    tone_score=8.0,
                    completeness_score=8.0,
                    feedback="Good suggestion",
                    strengths=["Compliant", "Clear"],
                    weaknesses=[],
                    pass_threshold=True
                )
                MockJudge.return_value = mock_judge
                
                # Clear singleton
                import app.evals.judge
                app.evals.judge._judge_instance = None
                
                result = evaluate_suggestion(
                    agent_draft="Test draft",
                    suggestion="Test suggestion",
                    policy_refs=["TEST"],
                    context="Test context"
                )
                
                assert isinstance(result, JudgeResponse)
                assert result.overall_score == 8.0
                assert result.pass_threshold is True


class TestJudgeResponseDataclass:
    """Tests for JudgeResponse dataclass."""
    
    def test_judge_response_creation(self):
        """Test creating a JudgeResponse."""
        response = JudgeResponse(
            overall_score=8.5,
            compliance_score=9.0,
            clarity_score=8.0,
            tone_score=8.5,
            completeness_score=8.5,
            feedback="Excellent work",
            strengths=["Clear", "Compliant"],
            weaknesses=["Minor tone issue"],
            pass_threshold=True
        )
        
        assert response.overall_score == 8.5
        assert response.compliance_score == 9.0
        assert len(response.strengths) == 2
        assert len(response.weaknesses) == 1
        assert response.pass_threshold is True
    
    def test_judge_response_pass_threshold_logic(self):
        """Test that pass_threshold reflects the correct logic."""
        # Passing
        response1 = JudgeResponse(
            overall_score=7.0,
            compliance_score=7.0,
            clarity_score=7.0,
            tone_score=7.0,
            completeness_score=7.0,
            feedback="Passing",
            strengths=[],
            weaknesses=[],
            pass_threshold=True
        )
        assert response1.pass_threshold is True
        
        # Failing
        response2 = JudgeResponse(
            overall_score=6.9,
            compliance_score=6.0,
            clarity_score=7.0,
            tone_score=7.0,
            completeness_score=7.0,
            feedback="Not passing",
            strengths=[],
            weaknesses=["Below threshold"],
            pass_threshold=False
        )
        assert response2.pass_threshold is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
