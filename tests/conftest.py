"""
This file provides:
- Mock LLM responses
- Common test schemas
- Adapter mocks
- Helper utilities
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from openai import AsyncOpenAI
from anthropic import Anthropic

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI SDK client for testing."""
    mock_client = AsyncMock(spec=AsyncOpenAI)

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(
        message=MagicMock(content='{"name": "John", "age": 30}', role="assistant"),
        finish_reason="stop"
    )]

    mock_response.usage = MagicMock(
        prompt_tokens=10, 
        completion_tokens=15,
        total_tokens=25
    )

    mock_response.model = "gpt-4o-mini"
    mock_client.chat.completions.create.return_value = mock_response

    return mock_client

@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing."""
    mock_client = AsyncMock(spec=Anthropic)

    mock_response = MagicMock()
    mock_response.content = [MagicMock(type="text", text='{"name": "Jane", "age": 25}')]
    mock_response.usage = MagicMock(
        input_tokens=12,
        output_tokens=18
    )

    mock_response.model = "claude-3-5-sonnet-20241022"
    mock_response.stop_reason = "end_turn"

    mock_client.messages.create.return_value = mock_response

    return mock_client

@pytest.fixture
def mock_openai_streaming_client():
    """Mock OpenAI SDK client for streaming tests."""
    mock_client = AsyncMock(spec=AsyncOpenAI)

    async def mock_stream_generator():
        chunks = [
            '{"name": "John", ',
            '"age": 30',
            '}'
        ]
        for chunk_text in chunks:
            chunk = MagicMock()
            chunk.choices = [MagicMock(
                delta=MagicMock(content=chunk_text),
                finish_reason=None
            )]
            yield chunk

        final_chunk = MagicMock()
        final_chunk.choices = [MagicMock(
            delta=MagicMock(content=""),
            finish_reason="stop"
        )]
        yield final_chunk


    mock_client.chat.completions.create.return_value = mock_stream_generator()

    return mock_client

@pytest.fixture
def mock_anthropic_streaming_client():
    """Mock Anthropic client for streaming tests."""
    mock_client = AsyncMock(spec=Anthropic)

    async def mock_stream_generator():
        chunks = [
            '{"name": "Jane", ',
            '"age": 25',
            '}'
        ]
        for chunk_text in chunks:
            chunk = MagicMock()
            chunk.type = "content_block_delta"
            chunk.delta = MagicMock(type="text_delta", text=chunk_text)
            yield chunk

        final_chunk = MagicMock()
        final_chunk.type = "message_stop"
        yield final_chunk

    mock_client.messages.create.return_value = mock_stream_generator()

    return mock_client

@pytest.fixture
def simple_person_schema():
    """A simple JSON schema for a person object."""
    return {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number"}
        },
        "required": ["name"]
    }

@pytest.fixture
def complex_nested_schema():
    """A complex nested JSON schema."""
    return {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "profile": {
                        "type": "object",
                        "properties": {
                            "bio": {"type": "string"},
                            "interests": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["bio"]
                    }
                },
                "required": ["id", "profile"]
            }
        },
        "required": ["user"]
    }

@pytest.fixture
def malformed_schema():
    """Various malformed JSON strings for repair testing."""
    return {
        "trailing_comma": '{"name": "Alice", "age": 30,}',
        "markdown_wrapped": '```json\n{"name": "Bob", "age": 25}\n```',
        "with_prose": 'Here is the data: {"name": "Charlie", "age": 35}',
        "incomplete": '{"name": "Dave", "age": ',
        "smart_quotes": '{"name": "Eve"}',  # Would have curly quotes
    }

@pytest.fixture
def valid_json_samples():
    """Valid JSON strings for testing."""
    return [
        '{"name": "Frank", "age": 40}',
        '{"user": {"id": "u123", "profile": {"bio": "Hello!", "interests": ["coding", "music"]}}}'
    ]