from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

class ValidationStatus(Enum):
    """Possible validation statuses."""
    VALID = "valid"
    INVALID = "invalid"
    REPAIRABLE = "repairable"
    UNREPAIRABLE = "unrepairable"

@dataclass
class ValidationError:
    """Class representing a validation error."""
    path: str
    message: str
    expected: Any
    actual: Any
    severity: str  # e.g., 'error', 'warning', 'info'

@dataclass
class ValidationResult:
    """Class representing the result of a validation."""
    status: ValidationStatus
    parsed_output: Optional[Any] = None
    errors: List[ValidationError] = None
    raw_output: str = ""
    repair_attempted: bool = False
    repair_successful: bool = False

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

    def validate_and_repair(self, output: str, schema: Dict[str, Any], max_repair_attemps: int = 2) -> ValidationResult:
        """Validate the output and attempt repair if invalid."""
        result = self.validate(output, schema)

        if result.status == ValidationStatus.VALID:
            return result

        for attempt in range(max_repair_attemps):
            if result.status == ValidationStatus.UNREPAIRABLE:
                break

            repair_result = self.repair(output, result.errors)
            result = self.validate(repair_result, schema)
            result.repair_attempted = True

            if result.status == ValidationStatus.VALID:
                result.repair_successful = True
                return result

        return result

