from typing import Any, Dict, List, Type
from pydantic import BaseModel, ValidationError as PydanticValidationError
import json
import re

from .base_validator import BaseValidator, ValidationResult, ValidationStatus, ValidationError

class PydanticValidator(BaseValidator):
    """ Validator that checks for valid Pydantic schema ouput """

    def __init__(self):
        pass
        
    def validate(self, output: str, schema: Type[BaseModel]) -> ValidationResult:
        errors =[]

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

        try:
            model_instance = schema(**parsed)
            return ValidationResult(
                status=ValidationStatus.VALID,
                parsed_output=model_instance.model_dump(),
                raw_output=output
            )
        except PydanticValidationError as e:
            for error in e.errors():

                path = ".".join(str(loc) for loc in error['loc'])
                errors.append(ValidationError(
                    path=path,
                    message=error['msg'],
                    expected=error['type'],
                    actual=str(error.get('input', 'N/A')),
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
        return re.sub(r',(\s*[}\]])', r'\1', text)
    
    def _fix_quotes(self, text: str) -> str:
        """Fix smart quotes, missing quotes, etc."""
        # Replace smart quotes with regular quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace("'", "'").replace("'", "'")
        return text
    
    def _extract_json(self, text: str) -> str:
        """Try to find JSON in surrounding text"""
        # Look for {...} or [...]
        match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        return match.group(1) if match else text


