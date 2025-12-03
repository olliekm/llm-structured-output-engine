"""
Example demonstrating the TemplateManager for easy template + enforcement integration.

This shows how to use templates with the enforcement engine in production.
"""

import asyncio
import tempfile
import os
from pathlib import Path

from parsec.prompts.template import PromptTemplate
from parsec.prompts.registry import TemplateRegistry
from parsec.prompts.manager import TemplateManager
from parsec.models.adapters.openai_adapter import OpenAIAdapter
from parsec.validators.json_validator import JSONValidator
from parsec.enforcement.engine import EnforcementEngine


async def main():
    print("=" * 60)
    print("Parsec TemplateManager Example")
    print("=" * 60)

    # ===== 1. Setup components =====
    print("\n1. Setting up components...")

    # Create adapter (mock for this example - would use real API key in production)
    adapter = OpenAIAdapter(
        api_key="sk-test-key",  # Mock key for example
        model="gpt-4o-mini"
    )

    validator = JSONValidator()
    engine = EnforcementEngine(adapter=adapter, validator=validator)

    registry = TemplateRegistry()
    manager = TemplateManager(registry=registry, engine=engine)

    print("✓ Created adapter, validator, engine, registry, and manager")

    # ===== 2. Create and register templates =====
    print("\n2. Creating templates...")

    person_template = PromptTemplate(
        name="extract_person",
        template="""Extract person information from the following text:
{text}

Please extract:
- Full name
- Age (as number)
- Email address

Return as valid JSON matching this format: {{"name": "...", "age": ..., "email": "..."}}""",
        variables={"text": str},
        required=["text"]
    )

    sentiment_template = PromptTemplate(
        name="classify_sentiment",
        template="""Analyze the sentiment of the following text:
{text}

Classify as: positive, negative, or neutral
Provide a confidence score between 0 and 1

Return as JSON: {{"sentiment": "...", "confidence": ...}}""",
        variables={"text": str},
        required=["text"]
    )

    registry.register(person_template, "1.0.0")
    registry.register(sentiment_template, "1.0.0")

    print(f"✓ Registered {len(registry.list_templates())} templates")

    # ===== 3. Validate all templates =====
    print("\n3. Validating templates...")

    validation_results = manager.validate_all_templates()

    for result in validation_results:
        status_icon = "✓" if result["status"] == "valid" else "✗"
        print(f"  {status_icon} {result['template']} v{result['version']}: {result['status']}")
        if result["error"]:
            print(f"    Error: {result['error']}")

    # ===== 4. Save templates to files =====
    print("\n4. Saving templates to files...")

    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    templates_dir = Path(temp_dir) / "templates"
    templates_dir.mkdir(exist_ok=True)

    # Save each template to separate file
    person_file = templates_dir / "person.yaml"
    sentiment_file = templates_dir / "sentiment.yaml"

    # Create temporary registries to save individual templates
    temp_registry1 = TemplateRegistry()
    temp_registry1.register(person_template, "1.0.0")
    temp_registry1.save_to_disk(str(person_file))

    temp_registry2 = TemplateRegistry()
    temp_registry2.register(sentiment_template, "1.0.0")
    temp_registry2.save_to_disk(str(sentiment_file))

    print(f"✓ Saved templates to {templates_dir}")
    print(f"  - {person_file.name}")
    print(f"  - {sentiment_file.name}")

    # ===== 5. Load templates from directory =====
    print("\n5. Loading templates from directory...")

    # Create new registry and manager
    new_registry = TemplateRegistry()
    new_manager = TemplateManager(registry=new_registry, engine=engine)

    loaded_count = new_manager.load_templates_from_directory(str(templates_dir))

    print(f"✓ Loaded {loaded_count} template files")
    print(f"  Templates in registry: {new_registry.list_templates()}")

    # ===== 6. Use enforce_with_template (SIMULATION) =====
    print("\n6. Demonstrating enforce_with_template API...")
    print("   (Note: This would make real API calls with valid credentials)")

    # Define schema
    person_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number"},
            "email": {"type": "string"}
        },
        "required": ["name", "age", "email"]
    }

    print("\n   Example call (commented out - requires valid API key):")
    print("   ```python")
    print("   result = await manager.enforce_with_template(")
    print("       template_name='extract_person',")
    print("       variables={'text': 'John Smith is 30, email: john@example.com'},")
    print("       schema=person_schema")
    print("   )")
    print("   print(f'Success: {result.success}')")
    print("   print(f'Data: {result.data}')")
    print("   ```")

    # Show what the rendered prompt would look like
    print("\n   Rendered prompt would be:")
    template = new_registry.get("extract_person")
    rendered = template.render(text="John Smith is 30, email: john@example.com")
    print("   ---")
    print("   " + rendered.replace("\n", "\n   "))
    print("   ---")

    # ===== 7. Template versioning example =====
    print("\n7. Demonstrating version management...")

    # Register improved version
    person_template_v2 = PromptTemplate(
        name="extract_person",
        template="""Extract person information from the following text:
{text}

IMPORTANT:
- Ensure name is properly capitalized
- Age must be a positive integer
- Email must be in valid format (user@domain.com)

Return as valid JSON matching this format: {{"name": "...", "age": ..., "email": "..."}}

{format_instructions}""",
        variables={"text": str, "format_instructions": str},
        required=["text"],
        defaults={"format_instructions": "Use strict validation."}
    )

    new_registry.register(person_template_v2, "2.0.0")

    print(f"✓ Registered new version")
    versions = new_registry.list_versions("extract_person")
    print(f"  Available versions: {versions}")

    # Compare versions
    print("\n  Comparing versions:")
    v1 = new_registry.get("extract_person", "1.0.0")
    v2 = new_registry.get("extract_person", "2.0.0")

    print(f"  v1.0.0: {len(v1.template)} chars, {len(v1.required)} required vars")
    print(f"  v2.0.0: {len(v2.template)} chars, {len(v2.required)} required vars")

    # Get latest automatically
    latest = new_registry.get("extract_person")
    print(f"\n  Latest version (auto): 2.0.0")

    # ===== 8. Production workflow example =====
    print("\n8. Production workflow summary:")
    print("   1. Create templates in code or YAML")
    print("   2. Save to templates/ directory")
    print("   3. Version control the YAML files")
    print("   4. Load templates on app startup:")
    print("      manager.load_templates_from_directory('./templates')")
    print("   5. Use throughout app:")
    print("      result = await manager.enforce_with_template(...)")
    print("   6. Iterate on templates, bump versions")
    print("   7. Monitor performance with analytics (future feature)")

    # ===== Cleanup =====
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)

    # Clean up temp files
    import shutil
    shutil.rmtree(temp_dir)
    print(f"\nCleaned up temporary directory: {temp_dir}")


if __name__ == "__main__":
    asyncio.run(main())
