"""
Example demonstrating template persistence (save/load to YAML).
"""

from parsec.prompts.template import PromptTemplate
from parsec.prompts.registry import TemplateRegistry
import tempfile
import os


def main():
    print("=" * 60)
    print("Parsec Template Persistence Example")
    print("=" * 60)

    # Create a temporary file for testing
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    temp_path = temp_file.name
    temp_file.close()

    try:
        # ===== 1. Create and register templates =====
        print("\n1. Creating templates...")

        registry = TemplateRegistry()

        template_v1 = PromptTemplate(
            name="extract_person",
            template="Extract person info from: {text}",
            variables={"text": str},
            required=["text"]
        )

        template_v2 = PromptTemplate(
            name="extract_person",
            template="Extract person info from: {text}\n\n{instructions}",
            variables={"text": str, "instructions": str},
            required=["text"],
            defaults={"instructions": "Return as JSON"}
        )

        sentiment_template = PromptTemplate(
            name="classify_sentiment",
            template="Classify sentiment: {text}",
            variables={"text": str},
            required=["text"]
        )

        registry.register(template_v1, "1.0.0")
        registry.register(template_v2, "2.0.0")
        registry.register(sentiment_template, "1.0.0")

        print(f"✓ Registered {len(registry.list_templates())} templates")
        print(f"  Templates: {registry.list_templates()}")

        # ===== 2. Save to disk =====
        print(f"\n2. Saving to disk: {temp_path}")

        registry.save_to_disk(temp_path)

        print("✓ Templates saved successfully")

        # Show file contents
        with open(temp_path, 'r') as f:
            content = f.read()
        print(f"\n--- YAML file contents ---")
        print(content)
        print("--- End file ---")

        # ===== 3. Create new registry and load from disk =====
        print("\n3. Loading from disk into new registry...")

        new_registry = TemplateRegistry()
        print(f"New registry templates before load: {new_registry.list_templates()}")

        new_registry.load_from_disk(temp_path)

        print(f"✓ Loaded successfully")
        print(f"New registry templates after load: {new_registry.list_templates()}")

        # ===== 4. Verify loaded templates work correctly =====
        print("\n4. Verifying loaded templates...")

        # Get and render template
        loaded_template = new_registry.get("extract_person", "2.0.0")
        rendered = loaded_template.render(text="John is 30 years old")

        print(f"✓ Template retrieved and rendered successfully")
        print(f"\n--- Rendered prompt ---")
        print(rendered)
        print("--- End prompt ---")

        # ===== 5. Verify versions =====
        print("\n5. Verifying versions...")

        versions = new_registry.list_versions("extract_person")
        print(f"✓ extract_person versions: {versions}")

        # Get latest version
        latest = new_registry.get("extract_person")
        print(f"✓ Latest version retrieved: {latest.name}")

        # ===== 6. Test type checking still works =====
        print("\n6. Verifying type checking works after load...")

        try:
            loaded_template.render(text=12345)  # Wrong type
            print("✗ Type checking failed!")
        except TypeError as e:
            print(f"✓ Type checking works: {e}")

        print("\n" + "=" * 60)
        print("Persistence example completed successfully!")
        print("=" * 60)

    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"\nCleaned up temporary file: {temp_path}")


if __name__ == "__main__":
    main()
