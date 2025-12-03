from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .openai_adapter import OpenAIAdapter
    from .anthropic_adapter import AnthropicAdapter
    from .gemini_adapter import GeminiAdapter

def __getattr__(name: str):
    """Lazy import adapters to avoid requiring all dependencies."""
    if name == "OpenAIAdapter":
        from .openai_adapter import OpenAIAdapter
        return OpenAIAdapter
    elif name == "AnthropicAdapter":
        from .anthropic_adapter import AnthropicAdapter
        return AnthropicAdapter
    elif name == "GeminiAdapter":
        from .gemini_adapter import GeminiAdapter
        return GeminiAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["OpenAIAdapter", "AnthropicAdapter", "GeminiAdapter"]
