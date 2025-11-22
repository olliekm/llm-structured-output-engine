from openai import AsyncOpenAI
from llm_structured_output_engine.core import BaseLLMAdapter, GenerationResponse, ModelProviders
import time
import json

class OpenAIAdapter(BaseLLMAdapter):
    """OpenAI implementation"""
    
    def _initialize_client(self):
        return AsyncOpenAI(api_key=self.api_key)
    
    @property
    def provider(self) -> ModelProviders:
        return ModelProviders.OPENAI
    
    def supports_native_structure_output(self) -> bool:
        return True  # OpenAI has JSON mode
    
    async def generate(self, prompt: str, schema=None, temperature=0.7, 
                      max_tokens=None, **kwargs) -> GenerationResponse:
        client = self.get_client()
        start = time.perf_counter()
        
        messages = [{"role": "user", "content": prompt}]
        
        # Use JSON mode if schema provided
        extra_args = {}
        if schema and self.supports_native_structure_output():
            extra_args["response_format"] = {"type": "json_object"}
            # Add schema to prompt
            messages[0]["content"] = f"{prompt}\n\nReturn valid JSON matching this schema: {json.dumps(schema)}"
        
        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **extra_args,
            **kwargs
        )
        
        latency = (time.perf_counter() - start) * 1000
        
        return GenerationResponse(
            output=response.choices[0].message.content,
            provider=self.provider.value,
            model=self.model,
            tokens_used=response.usage.total_tokens,
            latency_ms=latency
        )
    
    async def health_check(self) -> bool:
        try:
            client = self.get_client()
            await client.models.list()
            return True
        except:
            return False
