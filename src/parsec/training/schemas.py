from typing import Any, List, Dict, Optional
from pydantic import BaseModel, Field
import datetime
import uuid

class CollectedExample(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    prompt: str
    schema: Dict[str, Any] # schema used
    response: str # Raw llm output
    parsed_output: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    success: bool
    validation_errors: List[str] = Field(default_factory=list)

    class Config:
        json_encoders = {
            datetime.datetime: lambda v: v.isoformat()
        }


