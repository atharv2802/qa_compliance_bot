"""
Groq provider for LLM calls.

Provides JSON-mode responses using Groq's fast inference.
"""

import os
import json
import time
from typing import Dict, Any, Optional

try:
    from groq import Groq, GroqError
except ImportError:
    Groq = None
    GroqError = Exception

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GroqProvider:
    """Groq LLM provider with JSON-mode support."""
    
    def __init__(
        self,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        timeout: int = 5,
        max_retries: int = 2
    ):
        """
        Initialize Groq provider.
        
        Args:
            model: Model name (default from env or llama-3.1-8b-instant)
            temperature: Sampling temperature (default 0.7 for balanced creativity)
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        if Groq is None:
            raise ImportError(
                "groq package not installed. Install with: pip install groq"
            )
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max_retries
    
    def call_llm(self, prompt_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call Groq API with JSON-mode response.
        
        Args:
            prompt_dict: Dictionary with 'system' and 'user' keys containing prompts
            
        Returns:
            Parsed JSON response as dictionary
            
        Raises:
            ValueError: If response cannot be parsed as JSON
            GroqError: If API call fails after retries
        """
        messages = [
            {"role": "system", "content": prompt_dict.get("system", "")},
            {"role": "user", "content": prompt_dict.get("user", "")}
        ]
        
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Groq supports JSON mode for compatible models
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
                        raise ValueError(
                            f"Failed to parse JSON response: {e}\nContent: {content}"
                        )
            
            except GroqError as e:
                last_error = e
                if attempt < self.max_retries:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    raise ValueError(
                        f"Groq API call failed after {self.max_retries + 1} attempts: {e}"
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
    provider = GroqProvider()
    return provider.call_llm(prompt_dict)
