from enum import Enum

#
# Core enumerations for model providers and output formats.
#

class ModelProviders(Enum):
    """Models providers supported by the system."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    GROQ = "groq"
    LLAMA_CPP = "llama_cpp"

class OutputFormats(Enum):
    """Output formats supported by the system."""
    JSON = "json"
    PYDANTIC = "pydantic"
    XML = "xml"
    YAML = "yaml"


#
# Base classes for adapters and validators.
#

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel

class BaseLLMAdapter(ABC):
    """Abstract base class for LLM adapters."""

    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.config = kwargs
        self._client = None  # Placeholder for the LLM client instance

    @abstractmethod
    async def generate(self, prompt: str, schema: Optional[Dict[str, Any]] = None, temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs) -> str:
        """Generate output from LLM"""
        pass

    @abstractmethod
    def supports_native_structure_output(self) -> bool:
        """Checks whether the adapter supports native structured output."""
        pass
    