"""
Tests for provider manager and fallback logic.
"""

import os
import pytest
from unittest.mock import Mock, patch
from app.providers.provider_manager import (
    ProviderManager,
    get_provider_manager,
    reset_provider_manager
)


class TestProviderManager:
    """Tests for ProviderManager class."""
    
    def setup_method(self):
        """Reset provider manager before each test."""
        reset_provider_manager()
    
    def test_default_provider_is_groq(self):
        """Test that default provider is Groq."""
        with patch.dict(os.environ, {"LLM_PROVIDER": "groq"}, clear=False):
            manager = ProviderManager()
            assert manager.primary_provider == "groq"
    
    def test_fallback_providers_parsing(self):
        """Test that fallback providers are parsed correctly."""
        with patch.dict(os.environ, {
            "LLM_PROVIDER": "groq",
            "LLM_FALLBACK_PROVIDERS": "openai"
        }, clear=False):
            manager = ProviderManager()
            assert manager.fallback_providers == ["openai"]
            assert manager.provider_chain == ["groq", "openai"]
    
    def test_fallback_providers_with_spaces(self):
        """Test that fallback providers handle spaces."""
        with patch.dict(os.environ, {
            "LLM_PROVIDER": "groq",
            "LLM_FALLBACK_PROVIDERS": " openai "
        }, clear=False):
            manager = ProviderManager()
            assert manager.fallback_providers == ["openai"]
    
    def test_no_fallback_providers(self):
        """Test manager with no fallback providers."""
        with patch.dict(os.environ, {
            "LLM_PROVIDER": "groq",
            "LLM_FALLBACK_PROVIDERS": ""
        }, clear=False):
            manager = ProviderManager()
            assert manager.fallback_providers == []
            assert manager.provider_chain == ["groq"]
    
    @patch("app.providers.groq_provider.GroqProvider")
    def test_successful_primary_call(self, mock_groq_provider):
        """Test successful call with primary provider."""
        # Mock the provider
        mock_instance = Mock()
        mock_instance.call_llm.return_value = {
            "suggestion": "Test suggestion",
            "alternates": ["Alt 1", "Alt 2"],
            "rationale": "Test rationale",
            "policy_refs": ["TEST"],
            "confidence": 0.9
        }
        mock_groq_provider.return_value = mock_instance
        
        with patch.dict(os.environ, {"LLM_PROVIDER": "groq"}, clear=False):
            manager = ProviderManager()
            result = manager.call_llm({"system": "test", "user": "test"})
            
            assert result["suggestion"] == "Test suggestion"
            assert result["_provider_used"] == "groq"
            assert manager.last_provider_used == "groq"
    
    @patch("app.providers.openai_provider.OpenAIProvider")
    @patch("app.providers.groq_provider.GroqProvider")
    def test_fallback_to_openai(self, mock_groq_provider, mock_openai_provider):
        """Test fallback when primary provider fails."""
        # Mock Groq to fail
        mock_groq_instance = Mock()
        mock_groq_instance.call_llm.side_effect = Exception("Groq failed")
        mock_groq_provider.return_value = mock_groq_instance
        
        # Mock OpenAI to succeed
        mock_openai_instance = Mock()
        mock_openai_instance.call_llm.return_value = {
            "suggestion": "OpenAI suggestion",
            "alternates": ["Alt 1", "Alt 2"],
            "rationale": "Test rationale",
            "policy_refs": ["TEST"],
            "confidence": 0.85
        }
        mock_openai_provider.return_value = mock_openai_instance
        
        with patch.dict(os.environ, {
            "LLM_PROVIDER": "groq",
            "LLM_FALLBACK_PROVIDERS": "openai"
        }, clear=False):
            manager = ProviderManager()
            result = manager.call_llm({"system": "test", "user": "test"})
            
            assert result["suggestion"] == "OpenAI suggestion"
            assert result["_provider_used"] == "openai"
            assert manager.last_provider_used == "openai"
    
    @patch("app.providers.openai_provider.OpenAIProvider")
    @patch("app.providers.groq_provider.GroqProvider")
    def test_fallback_chain(self, mock_groq, mock_openai):
        """Test full fallback chain through all providers."""
        # Mock Groq to fail
        mock_groq_instance = Mock()
        mock_groq_instance.call_llm.side_effect = Exception("Groq failed")
        mock_groq.return_value = mock_groq_instance
        
        # Mock OpenAI to succeed
        mock_openai_instance = Mock()
        mock_openai_instance.call_llm.return_value = {
            "suggestion": "OpenAI suggestion",
            "alternates": ["Alt 1", "Alt 2"],
            "rationale": "Test rationale",
            "policy_refs": ["TEST"],
            "confidence": 0.8
        }
        mock_openai.return_value = mock_openai_instance
        
        with patch.dict(os.environ, {
            "LLM_PROVIDER": "groq",
            "LLM_FALLBACK_PROVIDERS": "openai"
        }, clear=False):
            manager = ProviderManager()
            result = manager.call_llm({"system": "test", "user": "test"})
            
            assert result["suggestion"] == "OpenAI suggestion"
            assert result["_provider_used"] == "openai"
            assert manager.last_provider_used == "openai"
    
    @patch("app.providers.groq_provider.GroqProvider")
    def test_all_providers_fail(self, mock_groq_provider):
        """Test error when all providers fail."""
        # Mock Groq to fail
        mock_groq_instance = Mock()
        mock_groq_instance.call_llm.side_effect = Exception("Groq failed")
        mock_groq_provider.return_value = mock_groq_instance
        
        with patch.dict(os.environ, {"LLM_PROVIDER": "groq"}, clear=False):
            manager = ProviderManager()
            
            with pytest.raises(ValueError) as exc_info:
                manager.call_llm({"system": "test", "user": "test"})
            
            assert "All LLM providers failed" in str(exc_info.value)
            assert "groq" in str(exc_info.value).lower()
    
    def test_get_provider_status(self):
        """Test getting provider status."""
        with patch.dict(os.environ, {
            "LLM_PROVIDER": "groq",
            "LLM_FALLBACK_PROVIDERS": "openai"
        }, clear=False):
            manager = ProviderManager()
            status = manager.get_provider_status()
            
            assert status["primary"] == "groq"
            assert status["fallbacks"] == ["openai"]
            assert "providers" in status


class TestGlobalFunctions:
    """Tests for module-level convenience functions."""
    
    def setup_method(self):
        """Reset provider manager before each test."""
        reset_provider_manager()
    
    def test_get_provider_manager_singleton(self):
        """Test that get_provider_manager returns singleton."""
        manager1 = get_provider_manager()
        manager2 = get_provider_manager()
        assert manager1 is manager2
    
    def test_reset_provider_manager(self):
        """Test that reset creates new instance."""
        manager1 = get_provider_manager()
        reset_provider_manager()
        manager2 = get_provider_manager()
        assert manager1 is not manager2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
