FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY uv.lock* .

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv /opt/venv && \
    uv pip install --system -r pyproject.toml

# Copy application code
COPY . .

# Install the package
RUN uv pip install --system -e .

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Default command
CMD ["prefect", "worker", "start", "--pool", "default-pool", "--type", "process"]
