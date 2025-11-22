"""
Shim package to expose adapters under `src.adapters` for backwards compatibility.
This forwards to the implementations in `models.adapters`.
"""

from .openai_adapter import *  # noqa: F401,F403

