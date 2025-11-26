# llm-structured-output-engine

Lightweight orchestration toolkit to generate, validate, repair and enforce
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

## Quickstart

Requirements: Python 3.8+, [Poetry](https://python-poetry.org/) recommended.

1. Install dependencies:

```bash
poetry install
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

- `src/llm_structured_output_engine/core` — core abstractions and schemas.
- `src/llm_structured_output_engine/models` — provider adapters (OpenAI).
- `src/llm_structured_output_engine/validators` — validator implementations.
- `src/llm_structured_output_engine/enforcement` — enforcement/orchestration logic.
- `examples/` — example runners (real OpenAI example included).
- `tests/` — unit tests.

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
MIT

Updated 26/11/2025

