from typing import Any, List, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from datetime import datetime, timezone
import uuid

class CollectedExample(BaseModel):
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()}
    )

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    prompt: str
    json_schema: Dict[str, Any] # schema used
    response: str # Raw llm output
    parsed_output: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    success: bool
    validation_errors: List[str] = Field(default_factory=list)

    @field_serializer('timestamp')
    def serialize_timestamp(self, dt: datetime, _info):
        return dt.isoformat()


