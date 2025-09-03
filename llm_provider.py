from abc import ABC, abstractmethod
import os
import json
import logging
import re

logger = logging.getLogger(__name__)

def extract_json_from_text(text: str) -> str:
    """Extract JSON from text that might contain other content."""
    if not text:
        return text
    
    # Remove common prefixes that models might add
    text = text.strip()
    prefixes_to_remove = ['<think>', '</think>', '```json', '```JSON', '```', 'json', 'JSON']
    for prefix in prefixes_to_remove:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
        if text.endswith(prefix):
            text = text[:-len(prefix)].strip()
    
    # First try to parse as-is
    try:
        json.loads(text)
        return text
    except:
        pass
    
    # Find the largest valid JSON object
    json_candidates = []
    
    # Try to find JSON between curly braces (greedy)
    brace_level = 0
    start_idx = -1
    
    for i, char in enumerate(text):
        if char == '{':
            if brace_level == 0:
                start_idx = i
            brace_level += 1
        elif char == '}':
            brace_level -= 1
            if brace_level == 0 and start_idx != -1:
                candidate = text[start_idx:i+1]
                try:
                    json.loads(candidate)
                    json_candidates.append(candidate)
                except:
                    pass
    
    # Return the longest valid JSON (likely the most complete)
    if json_candidates:
        return max(json_candidates, key=len)
    
    # Try regex patterns as fallback
    patterns = [
        r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Nested braces pattern
        r'\{.*?\}',  # Simple non-greedy
        r'\{.*\}'    # Greedy
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            try:
                json.loads(match)
                return match
            except:
                continue
    
    # Last resort: try from first { to end of string
    start_idx = text.find('{')
    if start_idx != -1:
        potential_json = text[start_idx:]
        # Remove any trailing text after last }
        last_brace = potential_json.rfind('}')
        if last_brace != -1:
            potential_json = potential_json[:last_brace+1]
            try:
                json.loads(potential_json)
                return potential_json
            except:
                pass
    
    # If all else fails, return original text
    return text

class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generates a response from the LLM."""
        pass

class DeepSeekProvider(LLMProvider):
    """
    LLM provider for DeepSeek (OpenAI-compatible API).
    Uses OpenAI python SDK with a custom base_url.
    """
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        # Import lazily to avoid mandatory dependency if provider not used
        from openai import OpenAI
        # DeepSeek uses OpenAI-compatible endpoint
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        self.model = model

    def generate_response(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant specializing in presentation creation and "
                            "editing. When asked to generate presentation plans, always return valid JSON."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "text"},
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"DeepSeek API error: {str(e)}")

def get_llm_provider() -> LLMProvider:
    """
    Factory function that returns a DeepSeekProvider instance.
    DeepSeek is the sole LLM used by AI PPT Editor.
    Environment variables:
        DEEPSEEK_API_KEY  (required)
        DEEPSEEK_MODEL    (optional, default 'deepseek-chat')
    """
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY environment variable not set")
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    return DeepSeekProvider(api_key, model)