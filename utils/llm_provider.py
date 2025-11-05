"""LLM provider abstraction layer."""

import os
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, model_name: str, temperature: float = 0.1):
        self.model_name = model_name
        self.temperature = temperature
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text from prompt."""
        pass
    
    @abstractmethod
    def generate_structured(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate structured output (JSON)."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""
    
    def __init__(self, model_name: Optional[str] = None, temperature: float = 0.1):
        from openai import OpenAI
        
        model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        super().__init__(model_name, temperature)
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text from prompt."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
        )
        
        return response.choices[0].message.content
    
    def generate_structured(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate structured output (JSON)."""
        import json
        
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add instruction for JSON output
        json_instruction = "\n\nPlease respond with valid JSON only."
        messages.append({"role": "user", "content": prompt + json_instruction})
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
            response_format={"type": "json_object"} if response_format else None
        )
        
        content = response.choices[0].message.content
        return json.loads(content)


class AnthropicProvider(LLMProvider):
    """Anthropic Claude LLM provider."""
    
    def __init__(self, model_name: Optional[str] = None, temperature: float = 0.1):
        from anthropic import Anthropic
        
        model_name = model_name or os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
        super().__init__(model_name, temperature)
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = Anthropic(api_key=api_key)
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text from prompt."""
        message = self.client.messages.create(
            model=self.model_name,
            max_tokens=4096,
            temperature=self.temperature,
            system=system_prompt if system_prompt else "",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
    
    def generate_structured(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate structured output (JSON)."""
        import json
        
        # Add instruction for JSON output
        json_instruction = "\n\nPlease respond with valid JSON only."
        
        message = self.client.messages.create(
            model=self.model_name,
            max_tokens=4096,
            temperature=self.temperature,
            system=system_prompt if system_prompt else "",
            messages=[
                {"role": "user", "content": prompt + json_instruction}
            ]
        )
        
        content = message.content[0].text
        return json.loads(content)


def get_llm_provider(
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None
) -> LLMProvider:
    """
    Factory function to get LLM provider.
    
    Args:
        provider: Provider name ('openai' or 'anthropic'). Defaults to env var.
        model_name: Model name. Defaults to env var.
        temperature: Temperature setting. Defaults to env var or 0.1.
    
    Returns:
        LLMProvider instance
    """
    provider = provider or os.getenv("MODEL_PROVIDER", "openai")
    
    if temperature is None:
        temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
    
    if provider.lower() == "openai":
        return OpenAIProvider(model_name=model_name, temperature=temperature)
    elif provider.lower() == "anthropic":
        return AnthropicProvider(model_name=model_name, temperature=temperature)
    else:
        raise ValueError(f"Unknown provider: {provider}. Choose 'openai' or 'anthropic'.")
