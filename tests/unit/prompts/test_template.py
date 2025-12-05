"""Tests for PromptTemplate class."""

import pytest
from parsec.prompts.template import PromptTemplate


class TestPromptTemplateBasics:
    """Test basic template functionality."""

    def test_create_template(self):
        """Test creating a basic template."""
        template = PromptTemplate(
            name="test_template",
            template="Hello {name}",
            variables={"name": str},
            required=["name"]
        )
        assert template.name == "test_template"
        assert template.template == "Hello {name}"

    def test_render_simple(self):
        """Test rendering a simple template."""
        template = PromptTemplate(
            name="greeting",
            template="Hello {name}!",
            variables={"name": str},
            required=["name"]
        )
        result = template.render(name="World")
        assert result == "Hello World!"

    def test_render_multiple_variables(self):
        """Test rendering with multiple variables."""
        template = PromptTemplate(
            name="person",
            template="Name: {name}, Age: {age}",
            variables={"name": str, "age": int},
            required=["name", "age"]
        )
        result = template.render(name="Alice", age=30)
        assert result == "Name: Alice, Age: 30"

    def test_render_with_defaults(self):
        """Test rendering with default values."""
        template = PromptTemplate(
            name="greeting",
            template="Hello {name}, {message}",
            variables={"name": str, "message": str},
            required=["name"],
            defaults={"message": "Welcome!"}
        )
        # Use default
        result1 = template.render(name="Alice")
        assert result1 == "Hello Alice, Welcome!"

        # Override default
        result2 = template.render(name="Bob", message="Goodbye!")
        assert result2 == "Hello Bob, Goodbye!"


class TestPromptTemplateValidation:
    """Test template validation and error handling."""

    def test_missing_required_variable(self):
        """Test error when required variable is missing."""
        template = PromptTemplate(
            name="test",
            template="Hello {name}",
            variables={"name": str},
            required=["name"]
        )
        with pytest.raises(ValueError, match="Missing required variables"):
            template.render()

    def test_wrong_type(self):
        """Test error when variable type is wrong."""
        template = PromptTemplate(
            name="test",
            template="Age: {age}",
            variables={"age": int},
            required=["age"]
        )
        with pytest.raises(TypeError, match="expected int, got str"):
            template.render(age="thirty")

    def test_multiple_type_errors(self):
        """Test type checking with multiple variables."""
        template = PromptTemplate(
            name="test",
            template="{x} + {y}",
            variables={"x": int, "y": int},
            required=["x", "y"]
        )
        # First variable wrong type
        with pytest.raises(TypeError):
            template.render(x="one", y=2)

        # Second variable wrong type
        with pytest.raises(TypeError):
            template.render(x=1, y="two")

    def test_undefined_variable_in_template(self):
        """Test error when template references undefined variable."""
        template = PromptTemplate(
            name="test",
            template="Hello {name}, you are {age} years old",
            variables={"name": str},
            required=["name"]
        )
        with pytest.raises(ValueError, match="undefined variable"):
            template.render(name="Alice")

    def test_required_not_in_variables(self):
        """Test error when required variable not in variables dict."""
        with pytest.raises(ValueError, match="not defined in variables"):
            PromptTemplate(
                name="test",
                template="Hello {name}",
                variables={"age": int},
                required=["name"]
            )


class TestPromptTemplateTypes:
    """Test different variable types."""

    def test_string_type(self):
        """Test string type validation."""
        template = PromptTemplate(
            name="test",
            template="{text}",
            variables={"text": str},
            required=["text"]
        )
        result = template.render(text="hello")
        assert result == "hello"

    def test_int_type(self):
        """Test int type validation."""
        template = PromptTemplate(
            name="test",
            template="{num}",
            variables={"num": int},
            required=["num"]
        )
        result = template.render(num=42)
        assert result == "42"

    def test_float_type(self):
        """Test float type validation."""
        template = PromptTemplate(
            name="test",
            template="{value}",
            variables={"value": float},
            required=["value"]
        )
        result = template.render(value=3.14)
        assert result == "3.14"

    def test_bool_type(self):
        """Test bool type validation."""
        template = PromptTemplate(
            name="test",
            template="{flag}",
            variables={"flag": bool},
            required=["flag"]
        )
        result = template.render(flag=True)
        assert result == "True"

    def test_list_type(self):
        """Test list type validation."""
        template = PromptTemplate(
            name="test",
            template="{items}",
            variables={"items": list},
            required=["items"]
        )
        result = template.render(items=[1, 2, 3])
        assert result == "[1, 2, 3]"

    def test_dict_type(self):
        """Test dict type validation."""
        template = PromptTemplate(
            name="test",
            template="{data}",
            variables={"data": dict},
            required=["data"]
        )
        result = template.render(data={"key": "value"})
        assert "key" in result


class TestPromptTemplateSerialization:
    """Test template serialization."""

    def test_to_dict(self):
        """Test converting template to dictionary."""
        template = PromptTemplate(
            name="test",
            template="Hello {name}",
            variables={"name": str, "age": int},
            required=["name"],
            defaults={"age": 0}
        )
        data = template.to_dict()

        assert data["name"] == "test"
        assert data["template"] == "Hello {name}"
        assert data["variables"] == {"name": "str", "age": "int"}
        assert data["required"] == ["name"]
        assert data["defaults"] == {"age": 0}

    def test_from_dict(self):
        """Test creating template from dictionary."""
        data = {
            "name": "test",
            "template": "Hello {name}",
            "variables": {"name": "str"},
            "required": ["name"],
            "defaults": {}
        }
        template = PromptTemplate.from_dict(data)

        assert template.name == "test"
        assert template.template == "Hello {name}"
        assert template.variables == {"name": str}
        assert template.required == ["name"]
        assert template.defaults == {}

    def test_roundtrip(self):
        """Test converting to dict and back."""
        original = PromptTemplate(
            name="roundtrip",
            template="{x} + {y} = {result}",
            variables={"x": int, "y": int, "result": str},
            required=["x", "y"],
            defaults={"result": "?"}
        )

        # Convert to dict and back
        data = original.to_dict()
        restored = PromptTemplate.from_dict(data)

        # Test they behave the same
        assert original.render(x=1, y=2) == restored.render(x=1, y=2)


class TestPromptTemplateEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_template(self):
        """Test template with no variables."""
        template = PromptTemplate(
            name="empty",
            template="Hello World",
            variables={},
            required=[]
        )
        result = template.render()
        assert result == "Hello World"

    def test_complex_template(self):
        """Test template with complex formatting."""
        template = PromptTemplate(
            name="complex",
            template="""Extract person information from:
{text}

Requirements:
- Name: {name_format}
- Age: {age_format}

Return as JSON.""",
            variables={"text": str, "name_format": str, "age_format": str},
            required=["text"],
            defaults={
                "name_format": "Full name",
                "age_format": "Integer"
            }
        )
        result = template.render(text="John Doe is 30")
        assert "John Doe is 30" in result
        assert "Full name" in result
        assert "Integer" in result

    def test_optional_variables(self):
        """Test template with all optional variables."""
        template = PromptTemplate(
            name="optional",
            template="{greeting} {name}",
            variables={"greeting": str, "name": str},
            required=[],
            defaults={"greeting": "Hello", "name": "World"}
        )
        # All defaults
        assert template.render() == "Hello World"

        # Override one
        assert template.render(name="Alice") == "Hello Alice"

        # Override all
        assert template.render(greeting="Hi", name="Bob") == "Hi Bob"

    def test_none_defaults(self):
        """Test template with None as defaults parameter."""
        template = PromptTemplate(
            name="test",
            template="{text}",
            variables={"text": str},
            required=["text"],
            defaults=None
        )
        assert template.defaults == {}
        result = template.render(text="hello")
        assert result == "hello"
