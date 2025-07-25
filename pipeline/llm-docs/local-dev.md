# Local Development Setup

This guide covers Docker infrastructure setup and project configuration for the Shepherd Pipeline.

> **Python Environment**: For Python version management (pyenv) and package management (uv), see [Python Environment Setup](python-env.md).

## Initial Project Setup

After setting up your Python environment, configure the project:

```bash
# Set up project environment (after following python-env.md)
uv sync
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg

# Copy environment configuration
cp .env.example .env
```

### Docker Infrastructure Setup

The project uses Docker Compose to run Prefect server and PostgreSQL locally:

```bash
# Start infrastructure
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f prefect-server

# Stop infrastructure
docker compose down
```

**Network Configuration**:
- **Prefect Server**: Accessible at `http://localhost:4200` (web UI) and `http://localhost:4200/api` (API)
- **PostgreSQL**: Accessible at `localhost:5432`
- **Internal Docker Network**: Worker uses `http://prefect-server:4200/api` for internal communication
- **Host Applications**: Use `http://localhost:4200/api` (configured in `.env` file)

### Daily Development
```bash
# Start Docker infrastructure (PostgreSQL + Prefect Server + Worker)
docker compose up -d

# Run the CLI (see CLI Usage Guide for detailed commands)
uv run python -m shepherd_pipeline.cli --help

# Access Prefect UI in browser
open http://localhost:4200

# Run tests
uv run pytest

# Code quality checks (see Code Quality Guide for details)
uv run pre-commit run --all-files

# Stop infrastructure when done
docker compose down
```

> **CLI Usage**: For detailed CLI commands, model selection, and examples, see [CLI Usage Guide](cli-usage.md).
> **Code Quality**: For detailed code quality workflows, linting configuration, and troubleshooting, see [Code Quality Guide](code-quality.md).

## Environment Configuration

### Project Environment Variables

The project uses environment variables for configuration. Key variables include:

- `MISTRAL_API_KEY`: Required for Mistral models in production
- `OPENAI_API_KEY`: Required for OpenAI models in production
- `PREFECT_API_URL`: Prefect server URL (default: `http://localhost:4200/api`)
- `DATABASE_URL`: PostgreSQL connection string

### Adding New Dependencies

```bash
# Production dependency
uv add package-name

# Development dependency
uv add --dev package-name

# Optional dependency group
uv add --optional-dependency extra package-name
```

## Troubleshooting

### Docker Issues

1. **Port conflicts:**
   ```bash
   # Check what's using port 4200 or 5432
   lsof -i :4200
   lsof -i :5432

   # Stop conflicting services
   docker compose down
   ```

2. **Container startup failures:**
   ```bash
   # Check container logs
   docker compose logs -f prefect-server
   docker compose logs -f postgres

   # Restart specific service
   docker compose restart prefect-server
   ```

3. **Database connection issues:**
   ```bash
   # Reset database
   docker compose down
   docker volume rm pipeline_postgres_data
   docker compose up -d
   ```

### Project Configuration Issues

1. **Missing environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Pre-commit hook issues:**
   ```bash
   # Reinstall hooks
   uv run pre-commit uninstall
   uv run pre-commit install
   uv run pre-commit install --hook-type commit-msg
   ```

## IDE Integration

For detailed IDE setup with Ruff, mypy, and other development tools, see [Code Quality Guide - IDE Integration](code-quality.md#integration-with-ides).

**Quick Setup**:
- **VS Code**: Point interpreter to `.venv/bin/python` and install Ruff extension
- **PyCharm**: Set interpreter to `.venv/bin/python` and install Ruff plugin

## Related Documentation

- **Python Environment**: [Python Environment Setup](python-env.md) - pyenv and uv installation and configuration
- **Code Quality**: [Code Quality Guide](code-quality.md) - Development tools and pre-commit workflows
- **CLI Usage**: [CLI Usage Guide](cli-usage.md) - Running pipeline commands
