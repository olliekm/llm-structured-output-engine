from llm_structured_output_engine.core import BaseLLMAdapter, StreamChunk
from llm_structured_output_engine.utils.partial_json import PartialJSONParser
from typing import AsyncIterator, Any, Optional
import time


class StreamingEngine:
    """
    Engine for streaming structured outputs with progressive validation.

    This engine coordinates:
    - Token-by-token streaming from LLM adapters
    - Partial JSON parsing as tokens arrive
    - Progressive validation of incomplete data
    - Completion detection
    """

    def __init__(self, adapter: BaseLLMAdapter):
        """
        Initialize the streaming engine.

        Args:
            adapter: LLM adapter that supports streaming
        """
        if not adapter.supports_streaming():
            raise ValueError(f"{adapter.__class__.__name__} does not support streaming")

        self.adapter = adapter
        self.parser = PartialJSONParser()

    async def stream(
        self,
        prompt: str,
        schema: Optional[Any] = None,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """
        Stream structured output from the LLM.

        Args:
            prompt: The prompt to send to the LLM
            schema: Optional schema for structured output
            **kwargs: Additional arguments to pass to the adapter

        Yields:
            StreamChunk: Each chunk of the streaming response with accumulated content
        """
        accumulated = ""
        start_time = time.time()

        async for delta in self.adapter.generate_stream(prompt, schema, **kwargs):
            accumulated += delta

            yield StreamChunk(
                delta=delta,
                accumulated=accumulated,
                is_complete=False,
                provider=self.adapter.provider.value,
                model=self.adapter.model
            )

        # Final chunk marking completion
        yield StreamChunk(
            delta="",
            accumulated=accumulated,
            is_complete=True,
            provider=self.adapter.provider.value,
            model=self.adapter.model
        )

    async def stream_with_parsing(
        self,
        prompt: str,
        schema: Optional[Any] = None,
        **kwargs
    ) -> AsyncIterator[tuple[StreamChunk, Optional[Any]]]:
        """
        Stream with incremental JSON parsing.

        Args:
            prompt: The prompt to send to the LLM
            schema: Optional schema for structured output
            **kwargs: Additional arguments to pass to the adapter

        Yields:
            tuple[StreamChunk, Optional[Any]]: Chunk and parsed partial JSON (if parseable)
        """
        async for chunk in self.stream(prompt, schema, **kwargs):
            parsed = self.parser.parse(chunk.accumulated)
            yield chunk, parsed

    async def stream_field(
        self,
        prompt: str,
        field_name: str,
        schema: Optional[Any] = None,
        **kwargs
    ) -> AsyncIterator[tuple[StreamChunk, Optional[Any]]]:
        """
        Stream and extract a specific field as it becomes available.

        Useful for getting specific values before the full response completes.

        Args:
            prompt: The prompt to send to the LLM
            field_name: Name of the field to extract
            schema: Optional schema for structured output
            **kwargs: Additional arguments to pass to the adapter

        Yields:
            tuple[StreamChunk, Optional[Any]]: Chunk and field value (if available)
        """
        async for chunk in self.stream(prompt, schema, **kwargs):
            field_value = self.parser.extract_field(chunk.accumulated, field_name)
            yield chunk, field_value

    async def collect_stream(
        self,
        prompt: str,
        schema: Optional[Any] = None,
        **kwargs
    ) -> str:
        """
        Convenience method to collect entire stream into final string.

        Args:
            prompt: The prompt to send to the LLM
            schema: Optional schema for structured output
            **kwargs: Additional arguments to pass to the adapter

        Returns:
            str: Complete accumulated response
        """
        final_chunk = None
        async for chunk in self.stream(prompt, schema, **kwargs):
            final_chunk = chunk

        return final_chunk.accumulated if final_chunk else ""
