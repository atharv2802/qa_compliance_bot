"""
OpenAI provider    def __init__(
        self,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        timeout: int = 30,
        max_retries: int = 2
    ): calls.

Provides JSON-mode responses for compliance suggestions.
"""

import os
import json
import time
from typing import Dict, Any, Optional
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class OpenAIProvider:
    """OpenAI LLM provider with JSON-mode support."""
    
    def __init__(
        self,
        model: str = None,
        temperature: float = 0,
        max_tokens: int = 160,
        timeout: int = 5,
        max_retries: int = 2
    ):
        """
        Initialize OpenAI provider.
        
        Args:
            model: Model name (default from env or gpt-4o-mini)
            temperature: Sampling temperature (default 0 for deterministic)
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max_retries
    
    def call_llm(self, prompt_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call OpenAI API with JSON-mode response.
        
        Args:
            prompt_dict: Dictionary with 'system' and 'user' keys containing prompts
            
        Returns:
            Parsed JSON response as dictionary
            
        Raises:
            ValueError: If response cannot be parsed as JSON
            OpenAIError: If API call fails after retries
        """
        messages = [
            {"role": "system", "content": prompt_dict.get("system", "")},
            {"role": "user", "content": prompt_dict.get("user", "")}
        ]
        
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Use JSON mode if available (GPT-4 Turbo and later)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    timeout=self.timeout,
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content
                
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
                        messages.append({
                            "role": "assistant",
                            "content": content
                        })
                        messages.append({
                            "role": "user",
                            "content": "Please respond with valid JSON only, no additional text."
                        })
                        continue
                    else:
                        raise ValueError(f"Failed to parse JSON response: {e}\nContent: {content}")
            
            except OpenAIError as e:
                last_error = e
                if attempt < self.max_retries:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    raise ValueError(f"OpenAI API call failed after {self.max_retries + 1} attempts: {e}")
        
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
        # Try to find JSON in markdown code blocks
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


# Global instance
_provider: Optional[OpenAIProvider] = None


def get_provider() -> OpenAIProvider:
    """Get or create global provider instance."""
    global _provider
    if _provider is None:
        _provider = OpenAIProvider()
    return _provider


def call_llm(prompt_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to call LLM with prompt.
    
    Args:
        prompt_dict: Dictionary with 'system' and 'user' prompts
        
    Returns:
        Parsed JSON response
    """
    return get_provider().call_llm(prompt_dict)
