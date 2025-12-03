"""
Live example of TemplateManager with real OpenAI API calls.

This demonstrates the complete workflow with actual LLM inference.
"""

import asyncio
import os
from dotenv import load_dotenv

from parsec.prompts.template import PromptTemplate
from parsec.prompts.registry import TemplateRegistry
from parsec.prompts.manager import TemplateManager
from parsec.models.adapters.openai_adapter import OpenAIAdapter
from parsec.validators.json_validator import JSONValidator
from parsec.enforcement.engine import EnforcementEngine
from parsec.cache.memory import InMemoryCache


async def main():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("Error: OPENAI_API_KEY not found in .env file")
        return

    print("=" * 60)
    print("Parsec TemplateManager - Live Demo")
    print("=" * 60)

    # ===== 1. Setup =====
    print("\n1. Setting up components with cache...")

    cache = InMemoryCache(max_size=100, default_ttl=3600)
    adapter = OpenAIAdapter(api_key=api_key, model="gpt-4o-mini")
    validator = JSONValidator()
    engine = EnforcementEngine(
        adapter=adapter,
        validator=validator,
        max_retries=2,
        cache=cache
    )

    registry = TemplateRegistry()
    manager = TemplateManager(registry=registry, engine=engine)

    print("✓ Created all components with caching enabled")

    # ===== 2. Create templates =====
    print("\n2. Creating and registering templates...")

    person_template = PromptTemplate(
        name="extract_person",
        template="""Extract person information from the following text:
{text}

Please extract:
- Full name
- Age (as a number)
- Email address

Return ONLY valid JSON in this exact format: {{"name": "...", "age": ..., "email": "..."}}""",
        variables={"text": str},
        required=["text"]
    )

    registry.register(person_template, "1.0.0")
    print("✓ Registered extract_person template")

    # ===== 3. Define schema =====
    person_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number"},
            "email": {"type": "string"}
        },
        "required": ["name", "age", "email"]
    }

    # ===== 4. Test with real API call =====
    print("\n3. Making real API call with template...")
    print("   Input: 'Sarah Johnson is 28 years old, email: sarah.j@company.com'")

    try:
        result = await manager.enforce_with_template(
            template_name="extract_person",
            variables={"text": "Sarah Johnson is 28 years old, email: sarah.j@company.com"},
            schema=person_schema,
            temperature=0.0  # Deterministic output
        )

        print(f"\n✓ API call successful!")
        print(f"  Success: {result.success}")
        print(f"  Retry count: {result.retry_count}")
        print(f"  Tokens used: {result.generation.tokens_used}")
        print(f"  Latency: {result.generation.latency_ms}ms")
        print(f"\n  Extracted data:")
        print(f"    Name: {result.data['name']}")
        print(f"    Age: {result.data['age']}")
        print(f"    Email: {result.data['email']}")

    except Exception as e:
        print(f"✗ Error: {e}")
        return

    # ===== 5. Test cache hit =====
    print("\n4. Testing cache (same request again)...")

    print("   Cache stats before:", cache.get_stats())

    try:
        result2 = await manager.enforce_with_template(
            template_name="extract_person",
            variables={"text": "Sarah Johnson is 28 years old, email: sarah.j@company.com"},
            schema=person_schema,
            temperature=0.0
        )

        print(f"\n✓ Second call completed (should be cached)")
        print(f"  Cache stats after:", cache.get_stats())
        print(f"  Data matches: {result.data == result2.data}")

    except Exception as e:
        print(f"✗ Error: {e}")

    # ===== 6. Test with different input =====
    print("\n5. Testing with different input (cache miss)...")

    try:
        result3 = await manager.enforce_with_template(
            template_name="extract_person",
            variables={"text": "Michael Brown, age 35, contact: m.brown@email.com"},
            schema=person_schema,
            temperature=0.0
        )

        print(f"\n✓ Third call successful!")
        print(f"  Extracted data:")
        print(f"    Name: {result3.data['name']}")
        print(f"    Age: {result3.data['age']}")
        print(f"    Email: {result3.data['email']}")

        print(f"\n  Final cache stats:", cache.get_stats())

    except Exception as e:
        print(f"✗ Error: {e}")

    # ===== 7. Demonstrate template versioning =====
    print("\n6. Demonstrating template versioning...")

    # Register improved version
    person_template_v2 = PromptTemplate(
        name="extract_person",
        template="""Extract person information from the following text:
{text}

IMPORTANT VALIDATION RULES:
- Name must be properly capitalized
- Age must be a positive integer between 0 and 150
- Email must be in valid format (user@domain.ext)

Return ONLY valid JSON in this exact format: {{"name": "...", "age": ..., "email": "..."}}

{format_instructions}""",
        variables={"text": str, "format_instructions": str},
        required=["text"],
        defaults={"format_instructions": "Apply strict validation."}
    )

    registry.register(person_template_v2, "2.0.0")
    print("✓ Registered version 2.0.0 with enhanced validation")

    versions = registry.list_versions("extract_person")
    print(f"  Available versions: {versions}")

    # Test with v2
    try:
        result_v2 = await manager.enforce_with_template(
            template_name="extract_person",
            version="2.0.0",  # Explicitly use v2
            variables={"text": "john doe is 25, email: john@test.com"},
            schema=person_schema,
            temperature=0.0
        )

        print(f"\n✓ v2.0.0 call successful!")
        print(f"  Extracted data:")
        print(f"    Name: {result_v2.data['name']} (should be capitalized)")
        print(f"    Age: {result_v2.data['age']}")
        print(f"    Email: {result_v2.data['email']}")

    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("Live demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
