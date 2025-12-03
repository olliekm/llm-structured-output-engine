# parsec

[![PyPI version](https://badge.fury.io/py/parsec-llm.svg)](https://badge.fury.io/py/parsec-llm)
[![Python Versions](https://img.shields.io/pypi/pyversions/parsec-llm.svg)](https://pypi.org/project/parsec-llm/)
[![Tests](https://github.com/olliekm/parsec/actions/workflows/test.yml/badge.svg)](https://github.com/olliekm/parsec/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/olliekm/parsec/branch/main/graph/badge.svg)](https://codecov.io/gh/olliekm/parsec)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-parsec.olliekm.com-blue)](https://parsec.olliekm.com)

⚡ Lightweight orchestration toolkit to generate, validate, repair and enforce
structured output from large language models (LLMs). The project provides a
provider-agnostic adapter interface, validators (JSON/pydantic), and an
enforcement engine that retries and repairs LLM output until it conforms to a
schema.

This repository contains:
- Adapter abstractions and a concrete OpenAI adapter.
- Validation and repair utilities for JSON output.
- An `EnforcementEngine` that generates, validates, repairs, and retries.
- Examples and tests demonstrating usage.

## Features

- Provider-agnostic adapter interface for plugging different LLMs.
- Native-structured output support (when providers allow JSON responses).
- JSON validation with schema-based repair heuristics.
- Retry loop with feedback to the model for progressive repair.
- Small test suite and example runner using the OpenAI adapter.

## Installation

```bash
pip install parsec-llm
```

Or for development:

```bash
git clone https://github.com/olliekm/parsec.git
cd parsec
pip install -e ".[dev]"
```

## Quick Example

```python
from parsec.models.adapters import OpenAIAdapter
from parsec.validators import JSONValidator
from parsec.enforcement import EnforcementEngine

# Set up components
adapter = OpenAIAdapter(api_key="your-api-key", model="gpt-4o-mini")
validator = JSONValidator()
engine = EnforcementEngine(adapter, validator)

# Define your schema
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    },
    "required": ["name"]
}

# Enforce structured output
result = await engine.enforce(
    "Extract: John Doe is 30 years old",
    schema
)

print(result.parsed_output)  # {"name": "John Doe", "age": 30}
```

## Development Setup

Requirements: Python 3.9+

1. Install dependencies:

```bash
pip install -e ".[dev]"
```

2. Run tests:

```bash
poetry run pytest -q
```

3. Run the OpenAI example (requires `OPENAI_API_KEY`):

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="gpt-4o-mini"  # optional
poetry run python examples/run_with_openai.py
```

The example demonstrates using `OpenAIAdapter`, `JSONValidator` and
`EnforcementEngine` to extract structured data using a JSON schema.

## Code Structure

- `src/parsec/core` — core abstractions and schemas.
- `src/parsec/models` — provider adapters (OpenAI, Anthropic).
- `src/parsec/validators` — validator implementations.
- `src/parsec/enforcement` — enforcement/orchestration logic.
- `src/parsec/cache` — caching implementations.
- `src/parsec/utils` — utility functions (partial JSON parsing).
- `examples/` — example runners (real OpenAI example included).
- `tests/` — unit tests with pytest.

## Testing

Run the test suite with:

```bash
poetry run pytest -q
```

## Notes & Next Steps

- The OpenAI example performs real API calls — be mindful of API keys and
	costs when running it.
- Consider mocking adapters for offline or CI-safe tests.
- This project is intentionally minimal and modular — adapters and validators
	can be extended to support additional providers and formats.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Oliver Kwun-Morfitt

