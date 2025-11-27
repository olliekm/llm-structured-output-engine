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

class StreamChunk(BaseModel):
    """A single chunk in a streaming response"""
    delta: str  # The new content in this chunk
    accumulated: str  # All content so far
    is_complete: bool = False  # Whether this is the final chunk
    provider: str
    model: str
    timestamp: datetime = Field(default_factory=datetime.now)

class StreamValidationResult(BaseModel):
    """Validation result for a streaming chunk"""
    status: ValidationStatus
    parsed_output: Optional[Any] = None
    errors: List[ValidationError] = Field(default_factory=list)
    is_partial: bool = True  # Whether this is a partial validation
    accumulated_text: str
