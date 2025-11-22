from pydantic import BaseModel, Field
from typing import Any, Optional, List
from datetime import datetime
from enum import Enum

class ValidationStatus(str, Enum):
    VALID = "valid"
    INVALID = "invalid"
    REPAIRABLE = "repairable"
    UNREPAIRABLE = "unrepairable"

class ValidationError(BaseModel):
    path: str
    message: str
    expected: Any
    actual: Any
    severity: str = "error"

class ValidationResult(BaseModel):
    status: ValidationStatus
    parsed_output: Optional[Any] = None
    errors: List[ValidationError] = Field(default_factory=list)
    raw_output: str
    repair_attempted: bool = False
    repair_successful: bool = False

class GenerationResponse(BaseModel):
    output: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    latency_ms: float
    timestamp: datetime = Field(default_factory=datetime.now)