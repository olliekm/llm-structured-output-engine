"""
Parsec - Lightweight orchestration toolkit for structured LLM output.

Provides adapters, validators, enforcement engine, prompt templates, and caching
for generating validated structured output from large language models.
"""

"""
Note: Adapters (OpenAIAdapter, AnthropicAdapter, GeminiAdapter) are not imported
at package level to avoid requiring all optional dependencies. Import them directly:

    from parsec.models.adapters import OpenAIAdapter
    from parsec.models.adapters import AnthropicAdapter
    from parsec.models.adapters import GeminiAdapter
"""

from parsec.core import BaseLLMAdapter
from parsec.validators.base_validator import BaseValidator
from parsec.enforcement.engine import EnforcementEngine, EnforcedOutput
from parsec.validators import JSONValidator, PydanticValidator
from parsec.cache import InMemoryCache
from parsec.prompts import PromptTemplate, TemplateRegistry, TemplateManager
from parsec.training import DatasetCollector

__version__ = "0.2.0"

__all__ = [
    # Core
    "BaseLLMAdapter",
    "BaseValidator",
    "EnforcementEngine",
    "EnforcedOutput",

    # Validators
    "JSONValidator",
    "PydanticValidator",

    # Cache
    "InMemoryCache",

    # Prompts
    "PromptTemplate",
    "TemplateRegistry",
    "TemplateManager",

    # Training
    "DatasetCollector",
]
