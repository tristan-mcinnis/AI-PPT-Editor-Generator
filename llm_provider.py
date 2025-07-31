from abc import ABC, abstractmethod
import os
import json
import requests
import logging
import re
from typing import Optional

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
            # Add system context to prompt - balance between JSON requirement and content generation
            system_prompt = """You are a helpful assistant specializing in presentation creation and editing. 

IMPORTANT: Your response must be valid JSON format. Generate the complete JSON response with all the required content.

Format your response as a JSON object with the structure requested in the prompt. Make sure to:
1. Include all slides and content from the input
2. Follow the exact JSON schema required
3. Provide complete, detailed content for each slide
4. Start with { and end with }

Example format:
{
  "slides": [
    {
      "slide_number": 1,
      "title": "Slide Title",
      "content": ["Point 1", "Point 2", "Point 3"],
      "layout": "title_and_content"
    }
  ]
}"""
            
            full_prompt = system_prompt + "\n\n" + prompt
            
            # For longer prompts, use a longer timeout and warn up the model
            estimated_timeout = min(max(60, len(full_prompt) // 100), 180)  # 60-180 seconds based on prompt length
            
            logger.info(f"Starting Ollama request - Model: {self.model}, Prompt length: {len(full_prompt)}, Timeout: {estimated_timeout}s")
            
            # Try to warm up the model first for better response times
            if len(full_prompt) > 500:
                logger.info(f"Warming up Ollama model {self.model}...")
                warm_up_success = self._warm_up_model()
                logger.info(f"Warm-up result: {'Success' if warm_up_success else 'Failed'}")
            
            # Prepare the request
            request_data = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.5,  # Slightly higher for more creative content
                    "num_predict": 4000,  # Increase for longer responses
                    "top_k": 40,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1,
                    "seed": -1  # Random seed for variety
                }
            }
            
            logger.info(f"Making Ollama API request to {self.host}/api/generate")
            logger.info(f"Request data: model={self.model}, stream=False, num_predict=4000, temp=0.5")
            
            response = requests.post(
                f"{self.host}/api/generate",
                json=request_data,
                timeout=estimated_timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            logger.info(f"Received response with status code: {response.status_code}")
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Response keys: {list(result.keys())}")
            
            if 'response' not in result:
                logger.error(f"Invalid response format from Ollama: {result}")
                raise Exception(f"Invalid response format from Ollama: {result}")
            
            response_text = result['response']
            logger.info(f"Generated response length: {len(response_text)}")
            logger.info(f"Response preview: {response_text[:200]}...")
            
            # Check if response is too short (likely empty or incomplete)
            if len(response_text.strip()) < 50:
                logger.warning(f"Response too short ({len(response_text)} chars), attempting retry with different settings")
                # Try one more time with higher temperature and different approach
                retry_request = {
                    "model": self.model,
                    "prompt": f"Generate a detailed JSON response for the following request. Be thorough and complete:\n\n{prompt}",
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "num_predict": 4000,
                        "top_k": 50,
                        "top_p": 0.95
                    }
                }
                
                retry_response = requests.post(
                    f"{self.host}/api/generate",
                    json=retry_request,
                    timeout=estimated_timeout,
                    headers={'Content-Type': 'application/json'}
                )
                retry_response.raise_for_status()
                retry_result = retry_response.json()
                response_text = retry_result.get('response', response_text)
                logger.info(f"Retry response length: {len(response_text)}")
            
            # Extract JSON from the response for Ollama
            cleaned_response = extract_json_from_text(response_text)
            logger.info(f"Cleaned response length: {len(cleaned_response)}")
            logger.info(f"Cleaned response preview: {cleaned_response[:200]}...")
            
            # Final check - if still too short, raise an error
            if len(cleaned_response.strip()) < 20:
                raise Exception(f"Ollama generated insufficient content (only {len(cleaned_response)} characters). Try using a larger model like qwen3:7b or llama2:7b")
                
            return cleaned_response
            
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