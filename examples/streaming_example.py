"""
Example demonstrating streaming structured outputs.

This example shows how to:
1. Stream tokens from an LLM
2. Parse partial JSON as it arrives
3. Extract specific fields before completion
4. Handle streaming with validation
"""

import asyncio
import os
from parsec.models.adapters.openai_adapter import OpenAIAdapter
from parsec.enforcement.streaming_engine import StreamingEngine


async def basic_streaming():
    """Basic streaming example - just print tokens as they arrive."""
    print("=== Basic Streaming ===\n")

    adapter = OpenAIAdapter(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini"
    )

    engine = StreamingEngine(adapter)

    prompt = """Generate a product description in JSON format with these fields:
    - name: product name
    - description: detailed description
    - price: price in USD
    - features: array of key features
    """

    async for chunk in engine.stream(prompt):
        if not chunk.is_complete:
            print(chunk.delta, end="", flush=True)

    print("\n\n✓ Stream complete\n")


async def streaming_with_parsing():
    """Stream with incremental JSON parsing."""
    print("=== Streaming with Parsing ===\n")

    adapter = OpenAIAdapter(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini"
    )

    engine = StreamingEngine(adapter)

    prompt = """Generate a weather report in JSON:
    {
        "location": "city name",
        "temperature": number,
        "conditions": "description",
        "forecast": ["day1", "day2", "day3"]
    }
    """

    async for chunk, parsed in engine.stream_with_parsing(prompt):
        if parsed:
            print(f"✓ Parsed so far: {parsed}")
        if chunk.is_complete:
            print(f"\n✓ Final result: {parsed}")


async def streaming_specific_field():
    """Stream and extract a specific field as soon as it's available."""
    print("\n=== Streaming Specific Field ===\n")

    adapter = OpenAIAdapter(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini"
    )

    engine = StreamingEngine(adapter)

    prompt = """Generate a user profile in JSON:
    {
        "username": "string",
        "email": "string",
        "bio": "long biography text",
        "interests": ["interest1", "interest2", "interest3"]
    }
    """

    # Extract username as soon as it's available
    username_found = False
    async for chunk, username in engine.stream_field(prompt, "username"):
        if username and not username_found:
            print(f"✓ Username available: {username}")
            username_found = True
        if chunk.is_complete:
            print(f"✓ Full profile complete")


async def main():
    """Run all streaming examples."""
    await basic_streaming()
    await streaming_with_parsing()
    await streaming_specific_field()


if __name__ == "__main__":
    asyncio.run(main())
