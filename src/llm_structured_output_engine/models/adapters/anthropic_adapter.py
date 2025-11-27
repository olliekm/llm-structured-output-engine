import anthropic
from llm_structured_output_engine.core import BaseLLMAdapter, GenerationResponse, ModelProviders
from typing import AsyncIterator
import time

class AnthropicAdapter(BaseLLMAdapter):
    """Adapter for Anthropic's API with custom configurations."""

    def _initialize_client(self):
        return anthropic.Anthropic(api_key=self.api_key)

    @property
    def provider(self) -> ModelProviders:
        return ModelProviders.ANTHROPIC

    def supports_native_structure_output(self) -> bool:
        return True

    def supports_streaming(self) -> bool:
        return True

    async def generate(self, prompt: str, schema=None, temperature=0.7,
                        max_tokens=None, **kwargs) -> GenerationResponse:
            if max_tokens is None:
                max_tokens = 4096
            start = time.perf_counter()

            message_params = {
                "model": self.model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }

            if schema:
                message_params["response_format"] = {
                    "type": "json_schema"
                }

            message_params.update(kwargs)

            client = self.get_client()

            response = await client.messages.create(**message_params)

            # Extract text from content blocks
            output = ""
            for block in response.content:
                if block.type == "text":
                    output += block.text

            latency = (time.perf_counter() - start) * 1000

            return GenerationResponse(
                output=output,
                provider=self.provider.value,
                model=self.model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                latency_ms=latency
            )

    async def generate_stream(
        self,
        prompt: str,
        schema=None,
        temperature=0.7,
        max_tokens=None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream tokens from Anthropic API"""
        if max_tokens is None:
            max_tokens = 4096

        message_params = {
            "model": self.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": True
        }

        if schema:
            message_params["response_format"] = {
                "type": "json_schema"
            }

        message_params.update(kwargs)

        client = self.get_client()

        async with client.messages.stream(**message_params) as stream:
            async for text in stream.text_stream:
                yield text

    async def health_check(self) -> bool:
        try:
            client = self.get_client()
            await client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[
                    {"role": "user", "content": "Hello, are you there?"}
                ])
            return True
        except:
            return False
