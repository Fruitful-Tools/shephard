name: "Shepherd Pipeline PRP Template - Context-Rich with Validation Loops"
description: |

## Purpose
Template optimized for AI agents to implement features in the Shepherd Pipeline project with sufficient context and self-validation capabilities to achieve working code through iterative refinement.

## Core Principles
1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the Shepherd Pipeline codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **Global rules**: Be sure to follow all rules in CLAUDE.md
6. **Prefect First**: All processing flows use Prefect tasks and flows with proper error handling

---

## Goal
[What needs to be built - be specific about the end state and desires]

## Why
- [Business value and user impact]
- [Integration with existing features]
- [Problems this solves and for whom]

## What
[User-visible behavior and technical requirements]

### Success Criteria
- [ ] [Specific measurable outcomes]

## All Needed Context

### Documentation & References (list all context needed to implement the feature)
```yaml
# MUST READ - Include these in your context window
- file: llms.txt
  why: Primary project overview and architecture understanding

- file: CLAUDE.md
  why: Development workflow and essential commands

- file: shepherd_pipeline/flows/main_flows.py
  why: Existing flow patterns and error handling

- file: shepherd_pipeline/models/pipeline.py
  why: Pydantic model patterns and validation

- file: shepherd_pipeline/services/mock_apis.py
  why: Mock service patterns for development

- file: shepherd_pipeline/config/settings.py
  why: Configuration patterns using Pydantic Settings

- docfile: [llm-docs/*.md relevant to feature]
  why: Project-specific documentation and patterns

- url: [External API docs if integrating new services]
  why: [Specific integration requirements]

```

### Current Codebase tree (run `tree` in the root of the project) to get an overview of the codebase
```bash

```

### Desired Codebase tree with files to be added and responsibility of file
```bash

```

### Known Gotchas of Shepherd Pipeline Codebase & Library Quirks
```python
# CRITICAL: Prefect 3.0+ patterns - all flows are async
# Use @task and @flow decorators with proper retry configuration
# Always use get_run_logger() for task logging, not standard logging

# CRITICAL: Pydantic v2 patterns
# Use Field(...) for validation, model_validator for complex validation
# ConfigDict for model configuration, not Config class

# CRITICAL: Mock-first development
# All external APIs have mocks in services/mock_apis.py
# Use --mock flag for development, controlled by settings.USE_MOCKS

# CRITICAL: uv dependency management
# Use 'uv sync' not 'pip install', 'uv run' for all commands
# Dependencies defined in pyproject.toml, not requirements.txt

# CRITICAL: Chinese language processing
# Use OpenCC for Traditional Chinese conversion
# Christian content optimization patterns in translation_service.py

# CRITICAL: Artifact management
# Use SHA-256 hashing for deduplication in artifact_manager.py
# Temporary files cleaned up in flow-level try/finally blocks
```

## Implementation Blueprint

### Data models and structure

Create the core data models following Shepherd Pipeline patterns for type safety and consistency.
```python
# Shepherd Pipeline model patterns:

# 1. Pipeline Input/Output models (see models/pipeline.py)
class FeatureInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # Use discriminator fields for different input types

# 2. Task-specific result models
class FeatureResult(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time: float

# 3. Service models for external APIs
class ExternalServiceRequest(BaseModel):
    # Follow patterns in services/*.py

# 4. Configuration models (see config/settings.py)
class FeatureSettings(BaseModel):
    # Environment-based configuration

```

### list of tasks to be completed to fulfill the PRP in the order they should be completed

```yaml
Task 1:
CREATE shepherd_pipeline/models/[feature].py:
  - MIRROR pattern from: shepherd_pipeline/models/pipeline.py
  - USE Pydantic v2 with ConfigDict
  - INCLUDE proper validation and error models

Task 2:
CREATE shepherd_pipeline/services/[feature]_service.py:
  - MIRROR pattern from: shepherd_pipeline/services/mistral_service.py
  - IMPLEMENT both real and mock versions
  - USE async patterns with proper error handling

Task 3:
UPDATE shepherd_pipeline/services/mock_apis.py:
  - ADD mock implementation for new service
  - FOLLOW existing mock patterns
  - PROVIDE realistic test data

Task 4:
CREATE shepherd_pipeline/tasks/[feature]_tasks.py:
  - USE @task decorator with retry configuration
  - IMPLEMENT atomic, stateless operations
  - USE get_run_logger() for logging

Task 5:
UPDATE shepherd_pipeline/flows/main_flows.py:
  - ADD new flow or extend existing flows
  - USE try/finally for cleanup
  - RETURN PipelineResult with proper error handling

Task 6:
UPDATE shepherd_pipeline/config/settings.py:
  - ADD configuration for new feature
  - USE Pydantic Settings patterns
  - INCLUDE environment variable bindings

```


### Per task pseudocode as needed added to each task
```python

# Task 1 - Shepherd Pipeline Prefect Task Pattern
# Pseudocode with CRITICAL details dont write entire code
@task(retries=3, retry_delay_seconds=2)
async def new_feature_task(input_data: FeatureInput) -> FeatureResult:
    logger = get_run_logger()
    logger.info(f"Processing feature with input: {input_data.model_dump()}")

    try:
        # PATTERN: Input validation with Pydantic
        validated = input_data  # Already validated by Pydantic

        # PATTERN: Service instantiation via factory
        service = get_service_instance("feature_service", mock=settings.USE_MOCKS)

        # PATTERN: Process with timeout and error handling
        result = await asyncio.wait_for(
            service.process(validated),
            timeout=settings.FEATURE_TIMEOUT
        )

        logger.info("Feature processing completed successfully")
        return FeatureResult(
            success=True,
            data=result,
            processing_time=time.time() - start_time
        )

    except Exception as e:
        logger.error(f"Feature processing failed: {str(e)}")
        return FeatureResult(
            success=False,
            error_message=str(e),
            processing_time=time.time() - start_time
        )
```

### Integration Points
```yaml
CONFIG:
  - add to: shepherd_pipeline/config/settings.py
  - pattern: "feature_timeout: int = Field(default=30, description='Feature processing timeout')"
  - pattern: "feature_model: str = Field(default='mistral-small-latest', description='AI model for feature')"

CLI:
  - add to: shepherd_pipeline/cli/main.py
  - pattern: "Add new command group following youtube/models pattern"
  - pattern: "@click.group() and @click.command() decorators"

FLOWS:
  - add to: shepherd_pipeline/flows/main_flows.py
  - pattern: "@flow decorator with proper error handling"
  - pattern: "Return PipelineResult with comprehensive metadata"

SERVICES:
  - add to: shepherd_pipeline/services/model_factory.py
  - pattern: "Register new service in get_service_instance()"
  - pattern: "Support both real and mock implementations"

DOCUMENTATION:
  - update: llms.txt with new component descriptions
  - create: llm-docs/[feature]-integration.md if external service
  - update: CLAUDE.md if new CLI commands added
```

## Validation Loop

### Level 1: Syntax & Style (Shepherd Pipeline Standards)
```bash
# ALWAYS follow this order for pre-commit fixes:
git add -A                          # Stage files first (required)
uv run ruff format .               # Format code
uv run ruff check --fix .          # Fix linting issues
uv run mypy .                      # Type checking
uv run pre-commit run --all-files  # Final validation

# Expected: No errors. If errors, READ the error and fix.
# NOTE: MyPy rules relaxed for test files (no untyped decorator warnings)
```

### Level 2: Unit Tests each new feature/file/function use existing test patterns
```python
# CREATE tests/unit/test_[feature].py following Shepherd Pipeline patterns:
import pytest
from prefect.testing.utilities import prefect_test_harness
from shepherd_pipeline.models.pipeline import PipelineInput
from shepherd_pipeline.tasks.[feature]_tasks import new_feature_task
from tests.conftest import sample_feature_input

def test_feature_task_success(sample_feature_input):
    """Test feature task with valid input"""
    with prefect_test_harness():
        result = new_feature_task.fn(sample_feature_input)
        assert result.success is True
        assert result.data is not None

def test_feature_input_validation():
    """Test Pydantic validation"""
    with pytest.raises(ValidationError):
        PipelineInput(entry_point_type="INVALID")

def test_feature_mock_service(monkeypatch):
    """Test with mock service"""
    monkeypatch.setenv("USE_MOCKS", "true")
    with prefect_test_harness():
        result = new_feature_task.fn(sample_feature_input)
        assert result.success is True
        # Mock should return predictable data
```

```bash
# Run Shepherd Pipeline test patterns:
uv run pytest tests/unit/test_[feature].py -v     # Unit tests
uv run pytest tests/integration/ -v               # Integration tests
uv run pytest -v -s                              # All tests with verbose output

# If failing: Read error, understand root cause, fix code, re-run
# Use pytest markers: -m "not slow" for faster iteration
```

### Level 3: Integration Test (Shepherd Pipeline CLI)
```bash
# Start Prefect infrastructure
docker compose up -d

# Test CLI command with mock mode
uv run python -m shepherd_pipeline.cli [feature] \
  --mock \
  --model mistral-small-latest \
  [feature-specific-args]

# Test with real APIs (if configured)
uv run python -m shepherd_pipeline.cli [feature] \
  --model mistral-small-latest \
  [feature-specific-args]

# Check Prefect UI for flow execution
open http://localhost:4200

# Expected: PipelineResult with success=True and comprehensive metadata
# If error: Check Prefect logs and get_run_logger() output
```

## Final validation Checklist (Shepherd Pipeline)
- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] No linting errors: `uv run ruff check . && uv run ruff format .`
- [ ] No type errors: `uv run mypy .`
- [ ] Pre-commit hooks pass: `uv run pre-commit run --all-files`
- [ ] CLI command works with --mock: `uv run python -m shepherd_pipeline.cli [feature] --mock`
- [ ] CLI command works with real APIs (if configured)
- [ ] Prefect flow executes successfully in UI: http://localhost:4200
- [ ] Error cases return proper PipelineResult with error details
- [ ] Logs use get_run_logger() and are informative but not verbose
- [ ] Mock service added to services/mock_apis.py
- [ ] Configuration added to config/settings.py
- [ ] Models follow Pydantic v2 patterns
- [ ] llms.txt updated with new components
- [ ] CLAUDE.md updated if new CLI commands added

---

## Anti-Patterns to Avoid
- ❌ Don't create new patterns when existing ones work
- ❌ Don't skip validation because "it should work"
- ❌ Don't ignore failing tests - fix them
- ❌ Don't use sync functions in async context
- ❌ Don't hardcode values that should be config
- ❌ Don't catch all exceptions - be specific
