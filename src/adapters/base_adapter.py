from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel

class LLMAdapter(ABC):
    """Abstract base class for LLM adapters."""

    @abstractmethod
    async def generate(self, prompt: str, schema: Optional[Dict[str, Any]] = None, **kwargs) -> str:
        """Generate output from LLM"""
        pass

    @abstractmethod
    def supports_native_structure_output(self) -> bool:
        """Checks whether the adapter supports native structured output."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Performs a health check on the adapter."""
        pass