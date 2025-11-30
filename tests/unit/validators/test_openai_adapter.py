import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from parsec.models.adapters.openai_adapter import OpenAIAdapter
from parsec.core import GenerationResponse, ModelProviders
import json

class TestOpenAIAdapter:
        
    @pytest.mark.asyncio
    @patch('parsec.models.adapters.openai_adapter.AsyncOpenAI')
    async def test_generate(self, mock_class):
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(
            message=MagicMock(content='{"name": "John"}'),
            finish_reason="stop"
            )]
        
        mock_response.usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=15,
            total_tokens=25
        )
        mock_client.chat.completions.create.return_value = mock_response
        mock_class.return_value = mock_client

        adapter = OpenAIAdapter(api_key="test", model="gpt-4")
        result = await adapter.generate("Hello")
        assert isinstance(result, GenerationResponse)
        assert result.output == '{"name": "John"}'
        assert result.model == "gpt-4"
        assert result.tokens_used == 25
        assert result.provider == ModelProviders.OPENAI.value
        
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs['model'] == "gpt-4"
        assert call_args.kwargs['messages'][0]['content'] == "Hello"


    @pytest.mark.asyncio
    @patch('parsec.models.adapters.openai_adapter.AsyncOpenAI')
    async def test_generate_with_schema(self, mock_class):
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(
            message=MagicMock(content='{"name": "John"}'),
            finish_reason="stop"
            )]
        
        mock_response.usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=15,
            total_tokens=25
        )
        mock_client.chat.completions.create.return_value = mock_response
        mock_class.return_value = mock_client

        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            },
            "required": ["name"]
        }

        adapter = OpenAIAdapter(api_key="test", model="gpt-4")
        result = await adapter.generate("Hello", schema=schema)

        assert isinstance(result, GenerationResponse)
        assert result.output == '{"name": "John"}'
        assert result.model == "gpt-4"
        assert result.tokens_used == 25
        assert result.provider == ModelProviders.OPENAI.value
        
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        expected_content = f"Hello\n\nReturn valid JSON matching this schema: {json.dumps(schema)}"
        assert call_args.kwargs['model'] == "gpt-4"
        assert 'response_format' in call_args.kwargs
        assert call_args.kwargs['messages'][0]['content'] == expected_content
        assert call_args.kwargs['response_format']['type'] == 'json_object'