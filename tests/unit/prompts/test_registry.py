"""Tests for TemplateRegistry class."""

import pytest
import tempfile
import os
from pathlib import Path

from parsec.prompts.template import PromptTemplate
from parsec.prompts.registry import TemplateRegistry


class TestTemplateRegistryBasics:
    """Test basic registry functionality."""

    def test_create_registry(self):
        """Test creating an empty registry."""
        registry = TemplateRegistry()
        assert registry.list_templates() == []

    def test_register_template(self):
        """Test registering a template."""
        registry = TemplateRegistry()
        template = PromptTemplate(
            name="test",
            template="Hello {name}",
            variables={"name": str},
            required=["name"]
        )
        registry.register(template, "1.0.0")

        assert "test" in registry.list_templates()
        assert registry.exists("test", "1.0.0")

    def test_register_multiple_versions(self):
        """Test registering multiple versions of same template."""
        registry = TemplateRegistry()
        template_v1 = PromptTemplate(
            name="test",
            template="Version 1",
            variables={},
            required=[]
        )
        template_v2 = PromptTemplate(
            name="test",
            template="Version 2",
            variables={},
            required=[]
        )

        registry.register(template_v1, "1.0.0")
        registry.register(template_v2, "2.0.0")

        versions = registry.list_versions("test")
        assert len(versions) == 2
        assert "1.0.0" in versions
        assert "2.0.0" in versions

    def test_register_duplicate_version(self):
        """Test error when registering duplicate version."""
        registry = TemplateRegistry()
        template = PromptTemplate(
            name="test",
            template="Test",
            variables={},
            required=[]
        )

        registry.register(template, "1.0.0")

        with pytest.raises(ValueError, match="already exists"):
            registry.register(template, "1.0.0")


class TestTemplateRegistryRetrieval:
    """Test retrieving templates from registry."""

    def test_get_specific_version(self):
        """Test getting a specific version."""
        registry = TemplateRegistry()
        template_v1 = PromptTemplate(
            name="test",
            template="v1: {text}",
            variables={"text": str},
            required=["text"]
        )
        template_v2 = PromptTemplate(
            name="test",
            template="v2: {text}",
            variables={"text": str},
            required=["text"]
        )

        registry.register(template_v1, "1.0.0")
        registry.register(template_v2, "2.0.0")

        # Get v1
        retrieved_v1 = registry.get("test", "1.0.0")
        assert retrieved_v1.render(text="hello") == "v1: hello"

        # Get v2
        retrieved_v2 = registry.get("test", "2.0.0")
        assert retrieved_v2.render(text="hello") == "v2: hello"

    def test_get_latest_version(self):
        """Test getting latest version without specifying."""
        registry = TemplateRegistry()
        template_v1 = PromptTemplate(
            name="test",
            template="v1",
            variables={},
            required=[]
        )
        template_v2 = PromptTemplate(
            name="test",
            template="v2",
            variables={},
            required=[]
        )

        registry.register(template_v1, "1.0.0")
        registry.register(template_v2, "2.0.0")

        # Should get v2 (latest)
        latest = registry.get("test")
        assert latest.render() == "v2"

    def test_get_nonexistent_template(self):
        """Test error when getting nonexistent template."""
        registry = TemplateRegistry()

        with pytest.raises(KeyError, match="not found"):
            registry.get("nonexistent")

    def test_get_nonexistent_version(self):
        """Test error when getting nonexistent version."""
        registry = TemplateRegistry()
        template = PromptTemplate(
            name="test",
            template="Test",
            variables={},
            required=[]
        )
        registry.register(template, "1.0.0")

        with pytest.raises(KeyError, match="version.*not found"):
            registry.get("test", "2.0.0")


class TestTemplateRegistryVersioning:
    """Test version management."""

    def test_semantic_versioning_order(self):
        """Test that versions are sorted correctly."""
        registry = TemplateRegistry()
        template = PromptTemplate(
            name="test",
            template="Test",
            variables={},
            required=[]
        )

        # Register in random order
        registry.register(template, "1.0.0")
        registry.register(template, "2.0.0")
        registry.register(template, "1.1.0")
        registry.register(template, "1.0.1")

        versions = registry.list_versions("test")

        # Should be sorted newest first
        assert versions == ["2.0.0", "1.1.0", "1.0.1", "1.0.0"]

    def test_latest_version_selection(self):
        """Test that latest version is selected correctly."""
        registry = TemplateRegistry()

        for i, version in enumerate(["1.0.0", "1.1.0", "2.0.0", "1.0.1"]):
            template = PromptTemplate(
                name="test",
                template=f"Version {version}",
                variables={},
                required=[]
            )
            registry.register(template, version)

        # Latest should be 2.0.0
        latest = registry.get("test")
        assert latest.template == "Version 2.0.0"


class TestTemplateRegistryListing:
    """Test listing functionality."""

    def test_list_templates(self):
        """Test listing all template names."""
        registry = TemplateRegistry()

        template1 = PromptTemplate(name="temp1", template="1", variables={}, required=[])
        template2 = PromptTemplate(name="temp2", template="2", variables={}, required=[])

        registry.register(template1, "1.0.0")
        registry.register(template2, "1.0.0")

        templates = registry.list_templates()
        assert len(templates) == 2
        assert "temp1" in templates
        assert "temp2" in templates

    def test_list_versions(self):
        """Test listing versions of a template."""
        registry = TemplateRegistry()
        template = PromptTemplate(name="test", template="Test", variables={}, required=[])

        registry.register(template, "1.0.0")
        registry.register(template, "1.1.0")
        registry.register(template, "2.0.0")

        versions = registry.list_versions("test")
        assert len(versions) == 3

    def test_list_versions_nonexistent(self):
        """Test error when listing versions of nonexistent template."""
        registry = TemplateRegistry()

        with pytest.raises(KeyError, match="not found"):
            registry.list_versions("nonexistent")


class TestTemplateRegistryExistence:
    """Test existence checking."""

    def test_exists_template(self):
        """Test checking if template exists."""
        registry = TemplateRegistry()
        template = PromptTemplate(name="test", template="Test", variables={}, required=[])

        assert not registry.exists("test")

        registry.register(template, "1.0.0")

        assert registry.exists("test")
        assert not registry.exists("other")

    def test_exists_version(self):
        """Test checking if specific version exists."""
        registry = TemplateRegistry()
        template = PromptTemplate(name="test", template="Test", variables={}, required=[])

        registry.register(template, "1.0.0")

        assert registry.exists("test", "1.0.0")
        assert not registry.exists("test", "2.0.0")


class TestTemplateRegistryDeletion:
    """Test deleting templates."""

    def test_delete_specific_version(self):
        """Test deleting a specific version."""
        registry = TemplateRegistry()
        template = PromptTemplate(name="test", template="Test", variables={}, required=[])

        registry.register(template, "1.0.0")
        registry.register(template, "2.0.0")

        registry.delete("test", "1.0.0")

        assert not registry.exists("test", "1.0.0")
        assert registry.exists("test", "2.0.0")

    def test_delete_all_versions(self):
        """Test deleting all versions of a template."""
        registry = TemplateRegistry()
        template = PromptTemplate(name="test", template="Test", variables={}, required=[])

        registry.register(template, "1.0.0")
        registry.register(template, "2.0.0")

        registry.delete("test")

        assert not registry.exists("test")

    def test_delete_last_version_removes_template(self):
        """Test that deleting last version removes template entirely."""
        registry = TemplateRegistry()
        template = PromptTemplate(name="test", template="Test", variables={}, required=[])

        registry.register(template, "1.0.0")

        registry.delete("test", "1.0.0")

        assert not registry.exists("test")
        assert "test" not in registry.list_templates()

    def test_delete_nonexistent_template(self):
        """Test error when deleting nonexistent template."""
        registry = TemplateRegistry()

        with pytest.raises(KeyError, match="not found"):
            registry.delete("nonexistent")

    def test_delete_nonexistent_version(self):
        """Test error when deleting nonexistent version."""
        registry = TemplateRegistry()
        template = PromptTemplate(name="test", template="Test", variables={}, required=[])

        registry.register(template, "1.0.0")

        with pytest.raises(KeyError, match="version.*not found"):
            registry.delete("test", "2.0.0")


class TestTemplateRegistryPersistence:
    """Test saving and loading templates."""

    def test_save_to_disk(self):
        """Test saving templates to YAML file."""
        registry = TemplateRegistry()
        template = PromptTemplate(
            name="test",
            template="Hello {name}",
            variables={"name": str},
            required=["name"]
        )
        registry.register(template, "1.0.0")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name

        try:
            registry.save_to_disk(temp_path)

            # Verify file exists and has content
            assert os.path.exists(temp_path)
            with open(temp_path, 'r') as f:
                content = f.read()
                assert "test:" in content
                assert "1.0.0:" in content
        finally:
            os.remove(temp_path)

    def test_load_from_disk(self):
        """Test loading templates from YAML file."""
        # Create and save
        registry1 = TemplateRegistry()
        template = PromptTemplate(
            name="test",
            template="Hello {name}",
            variables={"name": str},
            required=["name"]
        )
        registry1.register(template, "1.0.0")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name

        try:
            registry1.save_to_disk(temp_path)

            # Load into new registry
            registry2 = TemplateRegistry()
            registry2.load_from_disk(temp_path)

            # Verify loaded correctly
            assert registry2.exists("test", "1.0.0")
            loaded_template = registry2.get("test", "1.0.0")
            assert loaded_template.render(name="World") == "Hello World"
        finally:
            os.remove(temp_path)

    def test_load_nonexistent_file(self):
        """Test error when loading nonexistent file."""
        registry = TemplateRegistry()

        with pytest.raises(FileNotFoundError):
            registry.load_from_disk("/nonexistent/path.yaml")

    def test_save_multiple_templates(self):
        """Test saving and loading multiple templates."""
        registry1 = TemplateRegistry()

        template1 = PromptTemplate(name="temp1", template="T1", variables={}, required=[])
        template2 = PromptTemplate(name="temp2", template="T2", variables={}, required=[])

        registry1.register(template1, "1.0.0")
        registry1.register(template1, "2.0.0")
        registry1.register(template2, "1.0.0")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name

        try:
            registry1.save_to_disk(temp_path)

            registry2 = TemplateRegistry()
            registry2.load_from_disk(temp_path)

            # Verify all loaded
            assert len(registry2.list_templates()) == 2
            assert len(registry2.list_versions("temp1")) == 2
            assert len(registry2.list_versions("temp2")) == 1
        finally:
            os.remove(temp_path)

    def test_load_empty_file(self):
        """Test loading empty YAML file."""
        registry = TemplateRegistry()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name
            f.write("")  # Empty file

        try:
            registry.load_from_disk(temp_path)
            # Should not error, just load nothing
            assert registry.list_templates() == []
        finally:
            os.remove(temp_path)
