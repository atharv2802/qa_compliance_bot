"""
Anthropic provider fo    def __init__(
        self,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        timeout: int = 30,
        max_retries: int = 2
    ):lls.

Provides JSON-mode responses using Claude models.
"""

import os
import json
import time
from typing import Dict, Any, Optional

try:
    from anthropic import Anthropic, AnthropicError
except ImportError:
    Anthropic = None
    AnthropicError = Exception

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AnthropicProvider:
    """Anthropic Claude LLM provider with JSON-mode support."""
    
    def __init__(
        self,
        model: str = None,
        temperature: float = 0,
        max_tokens: int = 160,
        timeout: int = 5,
        max_retries: int = 2
    ):
        """
        Initialize Anthropic provider.
        
        Args:
            model: Model name (default from env or claude-3-haiku-20240307)
            temperature: Sampling temperature (default 0 for deterministic)
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        if Anthropic is None:
            raise ImportError(
                "anthropic package not installed. Install with: pip install anthropic"
            )
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = Anthropic(api_key=api_key)
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max_retries
    
    def call_llm(self, prompt_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call Anthropic API with JSON-mode response.
        
        Args:
            prompt_dict: Dictionary with 'system' and 'user' keys containing prompts
            
        Returns:
            Parsed JSON response as dictionary
            
        Raises:
            ValueError: If response cannot be parsed as JSON
            AnthropicError: If API call fails after retries
        """
        system_prompt = prompt_dict.get("system", "")
        user_prompt = prompt_dict.get("user", "")
        
        # Add JSON formatting instruction to system prompt
        enhanced_system = (
            f"{system_prompt}\n\n"
            "You must respond with valid JSON only. No markdown, no explanation, "
            "just the JSON object."
        )
        
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=enhanced_system,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ],
                    timeout=self.timeout
                )
                
                # Extract text content
                content = response.content[0].text
                
                # Parse JSON response
                try:
                    result = json.loads(content)
                    return result
                except json.JSONDecodeError as e:
                    # Try to extract JSON if wrapped in markdown or other text
                    result = self._extract_json(content)
                    if result:
                        return result
                    
                    # If this is not the last attempt, retry with format reminder
                    if attempt < self.max_retries:
                        user_prompt = (
                            f"{user_prompt}\n\n"
                            f"Previous response was not valid JSON: {content}\n"
                            f"Please respond with valid JSON only, no additional text."
                        )
                        continue
                    else:
                        raise ValueError(
                            f"Failed to parse JSON response: {e}\nContent: {content}"
                        )
            
            except AnthropicError as e:
                last_error = e
                if attempt < self.max_retries:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    raise ValueError(
                        f"Anthropic API call failed after {self.max_retries + 1} attempts: {e}"
                    )
        
        if last_error:
            raise last_error
        
        raise ValueError("Unexpected error in call_llm")
    
    def _extract_json(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to extract JSON from text that may contain markdown or other wrapping.
        
        Args:
            content: Raw content that may contain JSON
            
        Returns:
            Parsed JSON dict if found, None otherwise
        """
        import re
        
        # Look for ```json...``` or ```...```
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Look for bare JSON object
        json_pattern = r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})'
        match = re.search(json_pattern, content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        return None


def call_llm(prompt_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to call LLM with prompt.
    
    Args:
        prompt_dict: Dictionary with 'system' and 'user' prompts
        
    Returns:
        Parsed JSON response
    """
    provider = AnthropicProvider()
    return provider.call_llm(prompt_dict)
