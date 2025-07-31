from abc import ABC, abstractmethod
import os
import json
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

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
        # Test connection and check if model exists
        try:
            test_response = requests.get(f"{self.host}/api/tags", timeout=10)
            test_response.raise_for_status()
            
            # Check if the model exists
            models_data = test_response.json()
            available_models = [m.get('name', '') for m in models_data.get('models', [])]
            if self.model not in available_models:
                raise Exception(f"Model '{self.model}' not found. Available models: {', '.join(available_models)}. Install with: ollama pull {self.model}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Cannot connect to Ollama at {self.host}: {str(e)}")
        except Exception as e:
            if "not found" in str(e):
                raise e  # Re-raise model not found errors
            raise Exception(f"Error checking Ollama models: {str(e)}")

    def _warm_up_model(self):
        """Warm up the model with a small request to ensure it's loaded."""
        try:
            warm_up_response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": "Hello",
                    "stream": False,
                    "options": {
                        "num_predict": 5
                    }
                },
                timeout=30
            )
            warm_up_response.raise_for_status()
            return True
        except Exception as e:
            logger.warning(f"Model warm-up failed: {e}")
            return False

    def generate_response(self, prompt: str) -> str:
        try:
            # Add system context to prompt
            full_prompt = "You are a helpful assistant specializing in presentation creation and editing. When asked to generate presentation plans, always return valid JSON.\n\n" + prompt
            
            # For longer prompts, use a longer timeout and warn up the model
            estimated_timeout = min(max(60, len(full_prompt) // 100), 180)  # 60-180 seconds based on prompt length
            
            # Try to warm up the model first for better response times
            if len(full_prompt) > 500:
                logger.info(f"Warming up Ollama model {self.model}...")
                self._warm_up_model()
            
            logger.info(f"Generating response with Ollama model '{self.model}' (timeout: {estimated_timeout}s)")
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 3000,  # Increased for longer responses
                        "top_k": 40,
                        "top_p": 0.9
                    }
                },
                timeout=estimated_timeout
            )
            response.raise_for_status()
            result = response.json()
            
            if 'response' not in result:
                raise Exception(f"Invalid response format from Ollama: {result}")
                
            return result['response']
            
        except requests.exceptions.Timeout:
            raise Exception(f"Ollama request timed out after {estimated_timeout}s. Try using a smaller/faster model or reduce your content length.")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Cannot connect to Ollama at {self.host}. Make sure Ollama is running.")
        except Exception as e:
            if "model" in str(e).lower() and "not found" in str(e).lower():
                raise Exception(f"Model '{self.model}' not found. Install it with: ollama pull {self.model}")
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

def get_llm_provider(provider_type: Optional[str] = None, ollama_model: Optional[str] = None) -> LLMProvider:
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
        # Use provided model or fall back to environment variable
        model = ollama_model or os.environ.get('OLLAMA_MODEL', 'qwen3:1.7b')
        return OllamaProvider(host, model)
    
    elif provider_type == 'anthropic':
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        model = os.environ.get('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')
        return AnthropicProvider(api_key, model)
    
    else:
        raise ValueError(f"Unknown LLM provider: {provider_type}")