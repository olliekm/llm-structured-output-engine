# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2025-12-04

### Added

#### Prompt Template System
- **PromptTemplate** class with type-safe variable substitution
  - Type checking for variables (str, int, float, bool, list, dict)
  - Required vs optional variables with validation
  - Default values support
  - Serialization to/from dictionaries for persistence
- **TemplateRegistry** for version management
  - Semantic versioning support (1.0.0, 2.0.0, etc.)
  - Register templates with explicit versions
  - Get latest version automatically or specific version
  - List all templates and versions
  - Delete templates or specific versions
  - Save/load templates to/from YAML files
- **TemplateManager** for easy integration
  - `enforce_with_template()` - one-line API for template + enforcement
  - `load_templates_from_directory()` - bulk load YAML files
  - `validate_all_templates()` - check template structure

#### Caching System
- **InMemoryCache** with LRU eviction and TTL support
  - Configurable max size and default TTL
  - Cache statistics (hits, misses, hit rate)
  - Automatic eviction of expired entries
  - Clear cache functionality
- **Cache integration** with EnforcementEngine
  - Automatic caching of successful enforcement results
  - Cache key generation based on prompt + model + schema + parameters
  - Reduces redundant API calls and costs
  - Demonstrated 50% cache hit rate in examples

#### Examples
- `prompt_template_example.py` - Complete template system demo
- `prompt_persistence_example.py` - Save/load templates from YAML
- `template_manager_example.py` - TemplateManager integration
- `template_manager_live_example.py` - Live demo with real API calls

### Fixed
- **Critical**: Fixed AnthropicAdapter to use `AsyncAnthropic` instead of sync client
- **Critical**: Consolidated duplicate ValidationStatus/Error/Result definitions
- Fixed typo: `max_repair_attemps` → `max_repair_attempts`
- Updated Pydantic V1 → V2 patterns in training schemas
- Fixed deprecated `datetime.utcnow()` → `datetime.now(timezone.utc)`
- Replaced bare `except:` catches with `except Exception as e:`
- Added lazy loading for adapter exports to avoid requiring all dependencies

### Improved
- Extracted duplicate repair code to shared `JSONRepairUtils` utility
- Added comprehensive docstrings to cache module
- Updated README with new features and examples
- Improved package exports in `__init__.py` files
- Better error messages throughout

### Documentation
- Comprehensive README update with:
  - Expanded feature list
  - Quick start examples for all major features
  - Code structure documentation
  - Advanced usage patterns
  - Roadmap section
- New examples demonstrating:
  - Caching integration
  - Prompt template usage
  - Template versioning
  - Multi-provider support

## [0.1.0] - 2025-01-XX

### Initial Release
- Core enforcement engine with retry logic
- OpenAI, Anthropic, and Gemini adapters
- JSON Schema and Pydantic validators
- Dataset collection for training
- Basic examples and test suite
