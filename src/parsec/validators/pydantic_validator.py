from typing import Any, Dict, List, Type
from pydantic import BaseModel, ValidationError as PydanticValidationError
import json

from .base_validator import BaseValidator, ValidationResult, ValidationStatus, ValidationError
from .repair_utils import JSONRepairUtils

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
        """Repair common JSON issues using shared repair utilities."""
        return JSONRepairUtils.repair(output)


