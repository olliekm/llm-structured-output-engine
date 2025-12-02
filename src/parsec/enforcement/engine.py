from parsec.core import BaseLLMAdapter, GenerationResponse, ValidationResult, ValidationStatus
from parsec.validators.base_validator import BaseValidator
from pydantic import BaseModel
from typing import Any, Optional, TYPE_CHECKING
from dataclasses import asdict, is_dataclass

if TYPE_CHECKING:
    from parsec.training.collector import DatasetCollector

class EnforcedOutput(BaseModel):
    data: Any
    generation: GenerationResponse
    validation: ValidationResult
    retry_count: int = 0
    success: bool

class EnforcementEngine:
    """Main orchestrator"""
    
    def __init__(
        self,
        adapter: BaseLLMAdapter,
        validator: BaseValidator,
        max_retries: int = 3,
        collector: Optional['DatasetCollector'] = None
    ):
        self.adapter = adapter
        self.validator = validator
        self.max_retries = max_retries
        self.collector = collector
    
    async def enforce(
        self,
        prompt: str,
        schema: Any,
        **kwargs
    ) -> EnforcedOutput:
        """Generate and validate output with retries"""
        
        retry_count = 0
        last_validation = None
        
        for attempt in range(self.max_retries + 1):
            # Generate from LLM
            generation = await self.adapter.generate(prompt, schema, **kwargs)
            
            # Validate and repair
            validation = self.validator.validate_and_repair(
                generation.output,
                schema
            )

            # If validator returned a dataclass-based ValidationResult (from
            # `validators.base_validator`), convert it to the pydantic
            # `ValidationResult` model expected by `EnforcedOutput` so pydantic
            # validation succeeds and enum/value comparisons work.
            if not isinstance(validation, BaseModel) and is_dataclass(validation):
                # asdict will recursively convert dataclasses to dicts which
                # pydantic can parse into the expected model types.
                validation = ValidationResult(**asdict(validation))
            
            last_validation = validation
            
            if validation.status == ValidationStatus.VALID:
                if self.collector:
                    self.collector.collect({
                        "prompt": prompt,
                        "json_schema": schema,
                        "response": generation.output,
                        "parsed_output": validation.parsed_output,
                        "success": True,
                        "validation_errors": [],
                        "metadata": {
                            "retry_count": retry_count,
                            "tokens_used": generation.tokens_used,
                            "latency_ms": generation.latency_ms
                        }
                    })
                return EnforcedOutput(
                    data=validation.parsed_output,
                    generation=generation,
                    validation=validation,
                    retry_count=retry_count,
                    success=True
                )
            

            # Add errors to next prompt
            if attempt < self.max_retries:
                error_msg = "\n".join(e.message for e in validation.errors)
                prompt = f"{prompt}\n\nPrevious attempt had errors:\n{error_msg}"
                retry_count += 1
    
        if self.collector:
            self.collector.collect({
                "prompt": prompt,
                "json_schema": schema,
                "response": generation.output,
                "parsed_output": last_validation.parsed_output if last_validation else None,
                "success": False,
                "validation_errors": [e.message for e in last_validation.errors] if last_validation else [],
                "metadata": {
                    "retry_count": retry_count,
                    "tokens_used": generation.tokens_used,
                    "latency_ms": generation.latency_ms
                }
            })
            
        # All retries failed
        return EnforcedOutput(
            data=None,
            generation=generation,
            validation=last_validation,
            retry_count=retry_count,
            success=False
        )