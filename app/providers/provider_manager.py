"""
Unified LLM provider manager with automatic fallback support.

Supports OpenAI, Anthropic, and Groq with configurable primary and fallback providers.
"""

import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()


class ProviderManager:
    """
    Manages multiple LLM providers with automatic fallback.
    
    Configuration via environment variables:
    - LLM_PROVIDER: Primary provider (openai|anthropic|groq)
    - LLM_FALLBACK_PROVIDERS: Comma-separated fallback providers
    - LLM_MODEL: Model name for primary provider
    
    Example .env:
        LLM_PROVIDER=openai
        LLM_FALLBACK_PROVIDERS=anthropic,groq
        LLM_MODEL=gpt-4o-mini
        OPENAI_API_KEY=sk-...
        ANTHROPIC_API_KEY=sk-ant-...
        GROQ_API_KEY=gsk_...
    """
    
    def __init__(self):
        """Initialize provider manager with configuration from environment."""
        self.primary_provider = os.getenv("LLM_PROVIDER", "openai").lower()
        
        # Parse fallback providers
        fallback_str = os.getenv("LLM_FALLBACK_PROVIDERS", "")
        self.fallback_providers = [
            p.strip() for p in fallback_str.split(",") if p.strip()
        ]
        
        # Build provider chain: [primary, fallback1, fallback2, ...]
        self.provider_chain = [self.primary_provider] + self.fallback_providers
        
        # Initialize provider instances (lazy loading)
        self._provider_instances = {}
        
        # Track which provider was used for last call
        self.last_provider_used = None
    
    def _get_provider_instance(self, provider_name: str):
        """
        Get or create a provider instance.
        
        Args:
            provider_name: Name of provider (openai|anthropic|groq)
            
        Returns:
            Provider instance with call_llm method
            
        Raises:
            ValueError: If provider is not supported or not configured
        """
        if provider_name in self._provider_instances:
            return self._provider_instances[provider_name]
        
        try:
            if provider_name == "openai":
                from app.providers.openai_provider import OpenAIProvider
                instance = OpenAIProvider()
            elif provider_name == "anthropic":
                from app.providers.anthropic_provider import AnthropicProvider
                instance = AnthropicProvider()
            elif provider_name == "groq":
                from app.providers.groq_provider import GroqProvider
                instance = GroqProvider()
            else:
                raise ValueError(f"Unsupported provider: {provider_name}")
            
            self._provider_instances[provider_name] = instance
            return instance
        
        except ImportError as e:
            raise ValueError(
                f"Provider {provider_name} not available. "
                f"Install required package or check API key. Error: {e}"
            )
        except ValueError as e:
            # API key missing or other config issue
            raise ValueError(f"Provider {provider_name} configuration error: {e}")
    
    def call_llm(self, prompt_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call LLM with automatic fallback to alternate providers.
        
        Tries primary provider first, then falls back to configured
        fallback providers in order if the primary fails.
        
        Args:
            prompt_dict: Dictionary with 'system' and 'user' prompts
            
        Returns:
            Parsed JSON response from whichever provider succeeded
            
        Raises:
            ValueError: If all providers fail
        """
        errors = {}
        
        for provider_name in self.provider_chain:
            try:
                provider = self._get_provider_instance(provider_name)
                result = provider.call_llm(prompt_dict)
                
                # Success! Track which provider worked
                self.last_provider_used = provider_name
                
                # Add metadata about which provider was used
                if isinstance(result, dict):
                    result["_provider_used"] = provider_name
                
                return result
            
            except Exception as e:
                errors[provider_name] = str(e)
                # Continue to next provider in chain
                continue
        
        # All providers failed
        error_msg = "All LLM providers failed:\n"
        for provider, error in errors.items():
            error_msg += f"  - {provider}: {error}\n"
        
        raise ValueError(error_msg)
    
    def get_provider_status(self) -> Dict[str, Any]:
        """
        Get status of all configured providers.
        
        Returns:
            Dictionary with provider availability status
        """
        status = {
            "primary": self.primary_provider,
            "fallbacks": self.fallback_providers,
            "providers": {}
        }
        
        for provider_name in self.provider_chain:
            try:
                self._get_provider_instance(provider_name)
                status["providers"][provider_name] = "available"
            except Exception as e:
                status["providers"][provider_name] = f"unavailable: {str(e)}"
        
        return status


# Global instance
_manager: Optional[ProviderManager] = None


def get_provider_manager() -> ProviderManager:
    """Get or create the global provider manager instance."""
    global _manager
    if _manager is None:
        _manager = ProviderManager()
    return _manager


def call_llm(prompt_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to call LLM with automatic fallback.
    
    This is the main entry point for all LLM calls in the application.
    It will try the primary provider first, then fall back to alternates.
    
    Args:
        prompt_dict: Dictionary with 'system' and 'user' prompts
        
    Returns:
        Parsed JSON response
    """
    manager = get_provider_manager()
    return manager.call_llm(prompt_dict)


def get_last_provider_used() -> Optional[str]:
    """Get the name of the provider that was used for the last successful call."""
    manager = get_provider_manager()
    return manager.last_provider_used


def reset_provider_manager():
    """Reset the global provider manager (useful for testing)."""
    global _manager
    _manager = None
