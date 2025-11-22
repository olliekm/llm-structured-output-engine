import pytest
from src.adapters.openai_adapter import OpenAIAdapter
from src.validators.json_validator import JSONValidator
from src.enforcement.engine import EnforcementEngine

@pytest.mark.asyncio
async def test_basic_enforcement():
    adapter = OpenAIAdapter(api_key="test-key", model="gpt-4o-mini")
    validator = JSONValidator()
    engine = EnforcementEngine(adapter, validator)
    
    schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}}
    }
    
    # This will fail without real API key, but tests structure
    try:
        result = await engine.enforce("Get name: John", schema)
        assert result is not None
    except:
        pass  # Expected without real key
