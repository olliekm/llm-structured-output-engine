import os
import asyncio
from parsec.models.adapters.openai_adapter import OpenAIAdapter
from parsec.validators.json_validator import JSONValidator
from parsec.enforcement.engine import EnforcementEngine

async def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Please set OPENAI_API_KEY environment variable before running this example")

    adapter = OpenAIAdapter(api_key=api_key, model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    validator = JSONValidator()
    engine = EnforcementEngine(adapter=adapter, validator=validator, max_retries=2)

    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number"},
            "email": {"type": "string"}
        },
        "required": ["name", "age", "email"]
    }

    prompt = "Extract person info: John is 30 years old, john@example.com"

    print("Running generation against OpenAI (this will use your OPENAI_API_KEY)")
    result = await engine.enforce(prompt=prompt, schema=schema)

    print(f"Success: {result.success}")
    print(f"Retries: {result.retry_count}")
    if result.generation:
        print(f"Provider: {result.generation.provider} Model: {result.generation.model}")
        print(f"Tokens used: {result.generation.tokens_used}")
    print("Validation status:", result.validation.status)
    print("Parsed output:", result.data)

if __name__ == "__main__":
    asyncio.run(main())
