from llm_structured_output_engine.core import BaseLLMAdapter, GenerationResponse, ValidationResult, ValidationStatus
from llm_structured_output_engine.validators.base_validator import BaseValidator
from typing import Any, Optional
from pydantic import BaseModel
from dataclasses import asdict, is_dataclass

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
        max_retries: int = 3
    ):
        self.adapter = adapter
        self.validator = validator
        self.max_retries = max_retries
    
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
        
        # All retries failed
        return EnforcedOutput(
            data=None,
            generation=generation,
            validation=last_validation,
            retry_count=retry_count,
            success=False
        )