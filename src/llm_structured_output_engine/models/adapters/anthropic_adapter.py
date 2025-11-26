import anthropic
from llm_structured_output_engine.core import BaseLLMAdapter, GenerationResponse, ModelProviders

class AnthropicAdapter(BaseLLMAdapter):
    """Adapter for Anthropic's API with custom configurations."""

    def _initialize_client(self):
        return anthropic.Anthropic(api_key=self.api_key)
    
    @property
    def provider(self) -> ModelProviders:
        return ModelProviders.ANTHROPIC
    
    def supports_native_structure_output(self) -> bool:
        return False  # Anthropic does not have native JSON mode
    
    async def generate(self, prompt: str, schema=None, temperature=0.7,
                        max_tokens=None, **kwargs) -> GenerationResponse:
            client = self.get_client()
            
            # Construct the full prompt
            full_prompt = f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}"
            
            response = await client.completions.create(
                model=self.model,
                prompt=full_prompt,
                temperature=temperature,
                max_tokens_to_sample=max_tokens,
                **kwargs
            )
            
            return GenerationResponse(
                output=response.completion,
                provider=self.provider.value,
                model=self.model,
                tokens_used=response.usage.total_tokens,
                latency_ms=response.latency_ms
            )
    
    async def health_check(self) -> bool:
        try:
            client = self.get_client()
            await client.models.list()
            return True
        except:
            return False
        
    