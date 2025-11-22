import asyncio
from pydantic import BaseModel
from models.adapters.openai_adapter import OpenAIAdapter
from llm_structured_output_engine.validators.json_validator import JSONValidator
from llm_structured_output_engine.enforcement.engine import EnforcementEngine

class Person(BaseModel):
    name: str
    age: int
    email: str

async def main():
    # Setup
    adapter = OpenAIAdapter(
        api_key="your-key-here",
        model="gpt-4o-mini"
    )
    
    validator = JSONValidator()
    
    engine = EnforcementEngine(
        adapter=adapter,
        validator=validator,
        max_retries=3
    )
    
    # Define schema
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number"},
            "email": {"type": "string"}
        },
        "required": ["name", "age", "email"]
    }
    
    # Enforce
    result = await engine.enforce(
        prompt="Extract person info: John is 30 years old, john@example.com",
        schema=schema
    )
    
    print(f"Success: {result.success}")
    print(f"Data: {result.data}")
    print(f"Retries: {result.retry_count}")
    print(f"Tokens used: {result.generation.tokens_used}")

if __name__ == "__main__":
    asyncio.run(main())