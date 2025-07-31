from abc import ABC, abstractmethod
import os
import json
import requests
from typing import Optional

class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generates a response from the LLM."""
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_response(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant specializing in presentation creation and editing. When asked to generate presentation plans, always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "text"}  # Explicitly request text format
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

class OllamaProvider(LLMProvider):
    def __init__(self, host: str = "http://localhost:11434", model: str = "qwen3:1.7b"):
        self.host = host.rstrip('/')  # Remove trailing slash
        self.model = model
        # Test connection
        try:
            test_response = requests.get(f"{self.host}/api/tags")
            test_response.raise_for_status()
        except Exception as e:
            raise Exception(f"Cannot connect to Ollama at {self.host}: {str(e)}")

    def generate_response(self, prompt: str) -> str:
        try:
            # Add system context to prompt
            full_prompt = "You are a helpful assistant specializing in presentation creation and editing. When asked to generate presentation plans, always return valid JSON.\n\n" + prompt
            
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 2000
                    }
                },
                timeout=60  # 60 second timeout for local models
            )
            response.raise_for_status()
            return response.json()['response']
        except requests.exceptions.Timeout:
            raise Exception(f"Ollama request timed out. The model might be too slow or not loaded.")
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        import anthropic
        import httpx
        
        # Create a custom httpx client without proxy settings
        http_client = httpx.Client(
            follow_redirects=True,
            timeout=httpx.Timeout(60.0)
        )
        
        self.client = anthropic.Anthropic(
            api_key=api_key,
            http_client=http_client
        )
        self.model = model

    def generate_response(self, prompt: str) -> str:
        try:
            # Add system prompt to the user message for Anthropic
            enhanced_prompt = "You are a helpful assistant specializing in presentation creation and editing. When asked to generate presentation plans, always return valid JSON.\n\n" + prompt
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": enhanced_prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

def get_llm_provider(provider_type: Optional[str] = None) -> LLMProvider:
    """Factory function to get the configured LLM provider."""
    
    # Use provided provider type or fall back to environment variable
    if provider_type is None:
        provider_type = os.environ.get('LLM_PROVIDER', 'anthropic').lower()
    else:
        provider_type = provider_type.lower()
    
    if provider_type == 'openai':
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        model = os.environ.get('OPENAI_MODEL', 'gpt-4o')
        return OpenAIProvider(api_key, model)
    
    elif provider_type == 'ollama':
        host = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
        model = os.environ.get('OLLAMA_MODEL', 'qwen3:1.7b')
        return OllamaProvider(host, model)
    
    elif provider_type == 'anthropic':
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        model = os.environ.get('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')
        return AnthropicProvider(api_key, model)
    
    else:
        raise ValueError(f"Unknown LLM provider: {provider_type}")