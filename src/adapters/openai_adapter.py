"""Compatibility shim for `src.adapters.openai_adapter`.

This file re-exports `OpenAIAdapter` from the real implementation
located at `models.adapters.openai_adapter` so existing imports
(`from src.adapters.openai_adapter import OpenAIAdapter`) continue
to work without changing tests or examples.
"""

from models.adapters.openai_adapter import OpenAIAdapter  # type: ignore

__all__ = ["OpenAIAdapter"]
