import pytest
import json
from llm_structured_output_engine.validators.json_validator import JSONValidator
from llm_structured_output_engine.validators.base_validator import (
    ValidationStatus,
    ValidationError,
    ValidationResult,
)

class TestJSONValidator:

    @pytest.fixture
    def validator(self):
        """Fixture for JSONValidator instance."""
        return JSONValidator()
    
    def test_validate_valid_json_simple(self, validator, simple_person_schema):
        """Test validating a simple valid JSON against the schema."""
        valid_json = '{"name": "Alice", "age": 30}'
        
        result = validator.validate(valid_json, simple_person_schema)
        
        assert result.status == ValidationStatus.VALID
        assert result.errors == []
        assert result.parsed_output == {"name": "Alice", "age": 30}
        assert result.raw_output == valid_json

    def test_validate_valid_json_minimal(self, validator, simple_person_schema):
        """Test validating minimal valid JSON."""
        valid_json = '{"name": "Bob"}'
        
        result = validator.validate(valid_json, simple_person_schema)
        
        assert result.status == ValidationStatus.VALID
        assert result.parsed_output == {"name": "Bob"}

    def test_validate_missing_required_field(self, validator, simple_person_schema):
        """Test validating JSON missing a required field."""
        invalid_json = '{"age": 25}'
        
        result = validator.validate(invalid_json, simple_person_schema)
        
        assert result.status == ValidationStatus.INVALID
        assert len(result.errors) > 0
        assert any("name" in err.message.lower() or "required" in err.message.lower() for err in result.errors)

    def test_validate_wrong_type(self, validator, simple_person_schema):
        """Test validating JSON with wrong data type."""
        invalid_json = '{"name": "Charlie", "age": "thirty"}'
        
        result = validator.validate(invalid_json, simple_person_schema)
        
        assert result.status == ValidationStatus.INVALID
        assert len(result.errors) > 0

    def test_validate_complex_nested_json(self, validator, complex_nested_schema):
        """Test validating a complex nested JSON structure."""
        valid_json = '''
        {
            "user": {
                "id": "user_123",
                "profile": {
                    "bio": "Hello world!",
                    "interests": ["coding", "music"]
                }
            }
        }
        '''
        
        result = validator.validate(valid_json, complex_nested_schema)
        
        assert result.status == ValidationStatus.VALID
        assert result.parsed_output["user"]["id"] == "user_123"

    def test_completely_invalid_json(self, validator, simple_person_schema):
        """Test validating a completely invalid JSON string."""
        invalid_json = 'This is not JSON!'
        
        result = validator.validate(invalid_json, simple_person_schema)
        
        assert result.status == ValidationStatus.INVALID
        assert len(result.errors) > 0
        assert result.errors[0].message.startswith("Invalid JSON format")
        assert result.parsed_output is None

    def test_validate_empty_string(self, validator, simple_person_schema):
        """Test validating an empty string."""
        invalid_json = ''
        
        result = validator.validate(invalid_json, simple_person_schema)
        
        assert result.status == ValidationStatus.INVALID
        assert len(result.errors) > 0

class TestJSONRepairHeuristics:
    
    @pytest.fixture
    def validator(self):
        """Fixture for JSONValidator instance."""
        return JSONValidator()

    def test_repair_trailing_comma(self, validator, malformed_schema):
        """Test repairing JSON with trailing comma."""
        malformed_json = malformed_schema["trailing_comma"]
        
        repaired_json = validator.repair(malformed_json, [])

        parsed = json.loads(repaired_json)
        assert parsed == {"name": "Alice", "age": 30}

    def test_repair_markdown_wrapped(self, validator, malformed_schema):
        """Test repairing JSON wrapped in markdown."""
        malformed_json = malformed_schema["markdown_wrapped"]
        
        repaired_json = validator.repair(malformed_json, [])
        
        parsed = json.loads(repaired_json)
        assert parsed == {"name": "Bob", "age": 25}

    def test_repair_with_prose(self, validator, malformed_schema):
        """Test repairing JSON with surrounding prose."""
        malformed_json = malformed_schema["with_prose"]
        
        repaired_json = validator.repair(malformed_json, [])
        
        parsed = json.loads(repaired_json)
        assert parsed == {"name": "Charlie", "age": 35}

    def test_repair_smart_quotes(self, validator, malformed_schema):
        """Test repairing JSON with smart quotes."""
        malformed_json = malformed_schema["smart_quotes"]
        
        repaired_json = validator.repair(malformed_json, [])
        
        parsed = json.loads(repaired_json)
        assert parsed == {"name": "Eve"}