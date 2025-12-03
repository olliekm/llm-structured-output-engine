from typing import Any, Dict, List
from abc import ABC, abstractmethod
from parsec.core.schemas import ValidationStatus, ValidationError, ValidationResult

class BaseValidator(ABC):
    """Abstract base class for validators."""

    @abstractmethod
    def validate(self, output: str, schema: Dict[str, Any]) -> ValidationResult:
        """Validate the given output against the provided schema."""
        pass

    @abstractmethod
    def repair(self, output: str, errors: List[ValidationError]) -> str:
        """Attempt to repair the given output to conform to the provided schema."""
        pass

    def validate_and_repair(self, output: str, schema: Dict[str, Any], max_repair_attempts: int = 2) -> ValidationResult:
        """Validate the output and attempt repair if invalid."""
        result = self.validate(output, schema)

        if result.status == ValidationStatus.VALID:
            return result

        for attempt in range(max_repair_attempts):
            if result.status == ValidationStatus.UNREPAIRABLE:
                break

            repair_result = self.repair(output, result.errors)
            result = self.validate(repair_result, schema)
            result.repair_attempted = True

            if result.status == ValidationStatus.VALID:
                result.repair_successful = True
                return result

        return result

