# Code Quality Guide

Modern Python development tools and practices for the Shepherd Pipeline project.

> **Environment Setup**: For initial project setup including pyenv, uv, and Docker infrastructure, see [Local Development Setup](local-dev.md).

## Tools Overview

Our code quality stack uses modern, high-performance tools:

- **[Ruff](https://docs.astral.sh/ruff/)**: Ultra-fast Python linter and formatter (replaces Black, isort, flake8, etc.)
- **[mypy](https://mypy.readthedocs.io/)**: Static type checker with strict configuration
- **[pytest](https://docs.pytest.org/)**: Testing framework with comprehensive configuration
- **[typos](https://github.com/crate-ci/typos)**: Lightning-fast spell checker for source code
- **[pre-commit](https://pre-commit.com/)**: Git hooks for automated quality checks

**Configuration Files**:
- `pyproject.toml` - Tool configuration (Ruff, mypy, pytest)
- `.pre-commit-config.yaml` - Pre-commit hooks and versions
- `.typos.toml` - Spell checker configuration

## Essential Commands

### Code Quality Workflow
```bash
# Daily development
uv run ruff check --fix .    # Lint with auto-fix
uv run ruff format .         # Format code
uv run mypy .                # Type checking
uv run typos                 # Spell checking

# All-in-one check
uv run pre-commit run --all-files
```

### Testing
```bash
uv run pytest                    # All tests
uv run pytest tests/unit/        # Unit tests only
uv run pytest tests/integration/ # Integration tests only
uv run pytest -v -s             # Verbose with output
```

### Pre-commit Setup
```bash
# One-time setup
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg

# Manual run
uv run pre-commit run --all-files
```

## Development Workflow

### Before Committing (Essential Steps)
```bash
# 1. Stage files first (pre-commit requires staged files)
git add -A

# 2. Fix formatting and linting
uv run ruff format .
uv run ruff check --fix .

# 3. Fix any remaining type issues manually, then check
uv run mypy .

# 4. Run all pre-commit checks
uv run pre-commit run --all-files

# 5. If pre-commit made changes, stage and run again
git add -A
uv run pre-commit run --all-files

# 6. Commit (use conventional format)
git commit -m "feat: add new feature"
# or interactive: uv run cz commit
```

### During Development
```bash
# Check code quality frequently
uv run ruff check --fix .
uv run mypy .

# Run relevant tests
uv run pytest tests/unit/test_models.py
```

## Code Standards

### Python Style
- **88 character line length** (Black/Ruff compatible)
- **Double quotes** for strings
- **Type annotations required** for all functions
- **Modern union syntax**: `str | None` instead of `Optional[str]`
- **Import order**: Standard library → Third-party → Local imports

### Example Code Style
```python
from pathlib import Path
from collections.abc import Sequence

import httpx
from pydantic import BaseModel

from shepherd_pipeline.models import JobStatus

def process_audio(file_path: Path, chunk_size: int = 60) -> list[str]:
    """Process audio file into chunks.

    Args:
        file_path: Path to the audio file
        chunk_size: Chunk size in seconds

    Returns:
        List of processed chunks
    """
    return []
```

## Conventional Commits

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```bash
# Format: <type>[scope]: <description>
git commit -m "feat: add user authentication"
git commit -m "fix(api): handle timeout errors"
git commit -m "docs: update setup guide"

# Interactive helper
uv run cz commit
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`, `perf`, `build`

## Common Troubleshooting

### Pre-commit Hook Failures
```bash
# Always stage files first
git add -A

# Run tools in order
uv run ruff format .
uv run ruff check --fix .
uv run mypy .

# Check specific hooks
uv run pre-commit run ruff-format --all-files
uv run pre-commit run mypy --all-files
```

### Type Annotation Issues
```bash
# Common fixes:
# - Add type annotations: def func(x: str) -> str:
# - Use modern syntax: str | None instead of Optional[str]
# - Prefix unused args: def func(_unused: str) -> None:
# - Allow flexible kwargs: def func(**kwargs: Any) -> None:  # noqa: ANN401
```

### Performance Issues
```bash
# Check only changed files
git diff --name-only | xargs uv run ruff check

# Check specific files
uv run ruff check shepherd_pipeline/models.py
```

## IDE Integration

### VS Code
Install extensions: **Ruff**, **Python**, **mypy**

`.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "ruff.enable": true,
    "editor.formatOnSave": true,
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff"
    }
}
```

### PyCharm
1. Install Ruff plugin
2. Set interpreter to `.venv/bin/python`
3. Enable "Optimize imports on the fly"

## Configuration Reference

**Tool configurations are defined in**:
- `pyproject.toml` - Ruff rules, mypy settings, pytest configuration
- `.pre-commit-config.yaml` - Hook versions and configuration
- `.typos.toml` - Spell checker dictionary and exclusions

**Key settings**:
- **Ruff**: PEP 8, import sorting, type checking, modern Python syntax
- **mypy**: Strict mode with test-specific overrides
- **pytest**: Unit/integration test organization with coverage

## Related Documentation

- **Python Environment**: [Python Environment Setup](python-env.md) - pyenv and uv installation and configuration
- **Local Development**: [Local Development Setup](local-dev.md) - Docker infrastructure and project setup
- **CLI Usage**: [CLI Usage Guide](cli-usage.md) - Testing workflows and commands
- **Chinese Translation**: [Chinese Translation Service](chinese-translation.md) - Language service testing
