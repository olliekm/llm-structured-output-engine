from typing import Any, Optional
import hashlib
import json

def generate_cache_key(prompt: str, model: str, schema: Optional[Any] = None, temperature: float = 0.7, **kwargs) -> str:
    """Generate a unique cache key based on input parameters."""
    normalized_prompt = prompt.strip()
    key_components = {
        "prompt": normalized_prompt,
        "model": model,
        "schema": json.dumps(schema, sort_keys=True) if schema else "",
        "temperature": temperature,
        **kwargs
    }
    key_string = json.dumps(key_components, sort_keys=True)
    return hashlib.sha256(key_string.encode()).hexdigest()