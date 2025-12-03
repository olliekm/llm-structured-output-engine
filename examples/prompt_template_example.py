"""
Example demonstrating the PromptTemplate and TemplateRegistry system.

This example shows how to:
1. Create templates with variables and type checking
2. Register templates with versions
3. Retrieve and render templates
4. Manage template versions
"""

from parsec.prompts.template import PromptTemplate
from parsec.prompts.registry import TemplateRegistry


def main():
    print("=" * 60)
    print("Parsec Prompt Template System Example")
    print("=" * 60)

    # ===== 1. Create templates =====
    print("\n1. Creating prompt templates...")

    # Simple extraction template
    extraction_template_v1 = PromptTemplate(
        name="extract_person",
        template="Extract person information from the following text:\n{text}\n\nReturn valid JSON.",
        variables={"text": str},
        required=["text"],
        defaults=None
    )

    # Improved version with format instructions
    extraction_template_v2 = PromptTemplate(
        name="extract_person",
        template="""Extract person information from the following text:
{text}

Requirements:
- Name must be a full name
- Age must be a positive integer
- Email must be valid format

{format_instructions}""",
        variables={"text": str, "format_instructions": str},
        required=["text"],
        defaults={"format_instructions": "Return as valid JSON matching the schema."}
    )

    # Classification template
    sentiment_template = PromptTemplate(
        name="classify_sentiment",
        template="Classify the sentiment of the following text as positive, negative, or neutral:\n\n{text}\n\nSentiment:",
        variables={"text": str},
        required=["text"]
    )

    print("✓ Created 3 templates (2 versions of extract_person, 1 classify_sentiment)")

    # ===== 2. Create registry and register templates =====
    print("\n2. Registering templates...")

    registry = TemplateRegistry()

    registry.register(extraction_template_v1, "1.0.0")
    registry.register(extraction_template_v2, "2.0.0")
    registry.register(sentiment_template, "1.0.0")

    print(f"✓ Registered templates: {registry.list_templates()}")

    # ===== 3. List versions =====
    print("\n3. Listing versions...")

    versions = registry.list_versions("extract_person")
    print(f"✓ extract_person versions: {versions}")

    # ===== 4. Retrieve and render templates =====
    print("\n4. Retrieving and rendering templates...")

    # Get latest version (2.0.0)
    template = registry.get("extract_person")
    print(f"✓ Retrieved latest version of extract_person")

    # Render with required variable
    sample_text = "John Smith is 30 years old and his email is john@example.com"
    rendered = template.render(text=sample_text)
    print(f"\n--- Rendered prompt (latest version) ---")
    print(rendered)
    print("--- End prompt ---")

    # Get specific version (1.0.0)
    template_v1 = registry.get("extract_person", "1.0.0")
    rendered_v1 = template_v1.render(text=sample_text)
    print(f"\n--- Rendered prompt (v1.0.0) ---")
    print(rendered_v1)
    print("--- End prompt ---")

    # ===== 5. Type checking demo =====
    print("\n5. Demonstrating type checking...")

    try:
        # This should fail - passing int instead of str
        template.render(text=12345)
    except TypeError as e:
        print(f"✓ Type checking works! Error: {e}")

    # ===== 6. Missing required variable demo =====
    print("\n6. Demonstrating required variable validation...")

    try:
        # This should fail - missing required 'text' variable
        template.render()
    except ValueError as e:
        print(f"✓ Required variable checking works! Error: {e}")

    # ===== 7. Template existence checking =====
    print("\n7. Checking template existence...")

    exists = registry.exists("extract_person", "2.0.0")
    print(f"✓ extract_person v2.0.0 exists: {exists}")

    exists = registry.exists("extract_person", "3.0.0")
    print(f"✓ extract_person v3.0.0 exists: {exists}")

    exists = registry.exists("nonexistent_template")
    print(f"✓ nonexistent_template exists: {exists}")

    # ===== 8. Using sentiment template =====
    print("\n8. Using sentiment classification template...")

    sentiment_tmpl = registry.get("classify_sentiment")
    rendered_sentiment = sentiment_tmpl.render(text="I love this product! It's amazing!")
    print(f"\n--- Sentiment classification prompt ---")
    print(rendered_sentiment)
    print("--- End prompt ---")

    # ===== 9. Delete template version =====
    print("\n9. Deleting template version...")

    print(f"Versions before delete: {registry.list_versions('extract_person')}")
    registry.delete("extract_person", "1.0.0")
    print(f"✓ Deleted extract_person v1.0.0")
    print(f"Versions after delete: {registry.list_versions('extract_person')}")

    # ===== 10. Default values demo =====
    print("\n10. Demonstrating default values...")

    template_v2 = registry.get("extract_person", "2.0.0")

    # Render without optional format_instructions (uses default)
    rendered_default = template_v2.render(text=sample_text)
    print("✓ Rendered with default format_instructions")

    # Render with custom format_instructions
    rendered_custom = template_v2.render(
        text=sample_text,
        format_instructions="Return as JSON with fields: name, age, email"
    )
    print("✓ Rendered with custom format_instructions")
    print(f"\n--- Custom format instructions ---")
    print(rendered_custom)
    print("--- End prompt ---")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
