# Python Environment Setup

This guide covers Python version management with pyenv and package management with uv for the Shepherd Pipeline project.

## Python Version Management with pyenv

### Installation

#### macOS
```bash
# Using Homebrew (recommended)
brew update
brew install pyenv
```

#### Linux/Unix
```bash
# Using the official installer
curl -fsSL https://pyenv.run | bash
```

### Shell Configuration

Add these lines to your shell configuration file:

#### Bash (~/.bashrc or ~/.bash_profile)
```bash
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
```

#### Zsh (~/.zshrc)
```bash
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - zsh)"
```

### Python Installation and Management

1. **Restart your shell:**
   ```bash
   exec "$SHELL"
   ```

2. **List available Python versions:**
   ```bash
   pyenv install --list
   ```

3. **Install Python 3.12 (required for this project):**
   ```bash
   pyenv install 3.12
   ```

4. **Set Python version for this project:**
   ```bash
   # Navigate to the project directory
   cd /path/to/shepherd/pipeline

   # Set Python version locally (creates .python-version file)
   pyenv local 3.12
   ```

5. **Verify installation:**
   ```bash
   python --version  # Should show Python 3.12.x
   which python      # Should point to pyenv-managed Python
   ```

## Package Management with uv

### Installation

#### Option 1: Install via pip (recommended after pyenv setup)
```bash
pip install uv
```

#### Option 2: Install via pipx
```bash
pipx install uv
```

#### Option 3: Install via standalone installer
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Project Setup

1. **Create virtual environment:**
   ```bash
   uv venv
   ```

2. **Install project dependencies:**
   ```bash
   uv sync
   ```

3. **Install pre-commit hooks:**
   ```bash
   uv run pre-commit install
   uv run pre-commit install --hook-type commit-msg
   ```

### Common uv Commands

#### Package Management
```bash
# Install a new dependency
uv add <package_name>

# Install development dependency
uv add --dev <package_name>

# Remove a dependency
uv remove <package_name>

# Update dependencies
uv sync --upgrade
```

#### Running Commands
```bash
# Run Python scripts in the project environment
uv run python script.py

# Run any command in the project environment
uv run <command>

# Run the CLI
uv run python -m shepherd_pipeline.cli --help
```

#### Environment Management
```bash
# Show virtual environment information
uv venv --show

# Create environment with specific Python version
uv venv --python 3.12

# Install packages into system Python (use cautiously)
uv pip install --system <package>
```

## Environment Variables

### pyenv Configuration
- `PYENV_ROOT`: Directory where pyenv stores versions (default: `~/.pyenv`)
- `PYENV_VERSION`: Override Python version for current session
- `PYENV_DEBUG`: Enable debug output

### uv Configuration
- `UV_PYTHON`: Specify Python interpreter path
- `UV_VENV`: Specify virtual environment path
- `UV_CACHE_DIR`: Override cache directory location
- `UV_PROJECT_ENVIRONMENT`: Set project environment path

## Troubleshooting

### pyenv Issues

1. **Python version not found:**
   ```bash
   # Update pyenv
   pyenv update  # If using pyenv-installer
   # or
   cd $(pyenv root) && git pull  # If installed via git
   ```

2. **Command not found after installation:**
   ```bash
   # Ensure PATH is correctly set
   echo $PATH | grep pyenv

   # Reinstall shims
   pyenv rehash
   ```

3. **Build failures:**
   ```bash
   # Install build dependencies (Ubuntu/Debian)
   sudo apt-get update
   sudo apt-get install build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git

   # macOS - install Xcode command line tools
   xcode-select --install
   ```

### uv Issues

1. **Virtual environment not found:**
   ```bash
   # Create virtual environment
   uv venv

   # Or specify path
   uv venv .venv
   ```

2. **Package installation failures:**
   ```bash
   # Clear cache and retry
   uv cache clean
   uv sync
   ```

3. **Lock file issues:**
   ```bash
   # Regenerate lock file
   rm uv.lock
   uv lock
   uv sync
   ```

## Performance Tips

1. **Use uv's caching:**
   ```bash
   # Cache is automatically used, but you can check cache status
   uv cache dir
   uv cache info
   ```

2. **Optimize pyenv builds:**
   ```bash
   # Use optimized builds for production
   env PYTHON_CONFIGURE_OPTS='--enable-optimizations --with-lto' \
       PYTHON_CFLAGS='-march=native -mtune=native' \
       pyenv install 3.12
   ```

3. **Use local mirrors (if available):**
   ```bash
   # Set environment variables for faster downloads
   export PYTHON_BUILD_MIRROR_URL="https://your-mirror.com"
   ```

## Quick Setup Summary

For new developers, here's the complete setup sequence:

```bash
# 1. Install pyenv and set up Python
pyenv install 3.12
pyenv local 3.12

# 2. Install uv
pip install uv

# 3. Set up project environment
uv sync
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

## Related Documentation

- **Local Development**: [Local Development Setup](local-dev.md) - Docker infrastructure and project workflow
- **Code Quality**: [Code Quality Guide](code-quality.md) - Development tools and pre-commit setup
- **CLI Usage**: [CLI Usage Guide](cli-usage.md) - Running the pipeline CLI
