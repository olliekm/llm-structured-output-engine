from typing import Any, Dict, List, Optional
from .base_validator import BaseValidator, ValidationResult, ValidationStatus, ValidationError
import jsonschema
import json


class JSONValidator(BaseValidator):
    """Validator that checks if the output is valid JSON and conforms to a given schema."""

    def __init__(self):
        self.validator = jsonschema.Draft7Validator

    def validate(self, output: str, schema: Dict[str, Any]) -> ValidationResult:
        errors = []

        try:
            parsed = json.loads(output)
        except json.JSONDecodeError as e:
            errors.append(ValidationError(
                path="",
                message="Invalid JSON format",
                expected="Valid JSON",
                actual=str(e),
                severity="error"
            ))
            return ValidationResult(
                status=ValidationStatus.INVALID,
                errors=errors,
                raw_output=output
            )
        
        schema_validator = self.validator(schema)
        schema_errors = list(schema_validator.iter_errors(parsed))

        if not schema_errors:
            return ValidationResult(
                status=ValidationStatus.VALID,
                parsed_output=parsed,
                raw_output=output
            )
        
        for err in schema_errors:
            path = "$.".join(str(p) for p in err.path) or "$"
            errors.append(ValidationError(
                path=path,
                message=err.message,
                expected=err.schema.get("type", "unknown"),
                actual=type(err.instance).__name__,
                severity="error"
            ))

        return ValidationResult(
            status=ValidationStatus.INVALID,
            errors=errors,
            raw_output=output,
            parsed_output=parsed
        )
        
    def repair(self, output: str, errors: List[ValidationError]) -> str:
        """Repair common JSON issues"""
        repaired = output
        
        # Remove markdown code blocks
        if repaired.startswith("```"):
            repaired = repaired.split("```")[1]
            if repaired.startswith("json"):
                repaired = repaired[4:]
        
        # Remove trailing commas
        repaired = self._remove_trailing_commas(repaired)
        
        # Fix common quote issues
        repaired = self._fix_quotes(repaired)
        
        # Try to extract JSON from text
        if not repaired.strip().startswith("{"):
            repaired = self._extract_json(repaired)
        
        return repaired
    
    def _remove_trailing_commas(self, text: str) -> str:
        """Remove trailing commas before ] or }"""
        import re
        return re.sub(r',(\s*[}\]])', r'\1', text)
    
    def _fix_quotes(self, text: str) -> str:
        """Fix smart quotes, missing quotes, etc."""
        # Replace smart quotes with regular quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace("'", "'").replace("'", "'")
        return text
    
    def _extract_json(self, text: str) -> str:
        """Try to find JSON in surrounding text"""
        import re
        # Look for {...} or [...]
        match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        return match.group(1) if match else text