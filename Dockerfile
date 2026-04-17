# Build stage
FROM python:3.14-slim AS builder

WORKDIR /app

# Install uv for blazingly fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment and install dependencies
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml .
RUN uv pip install --no-cache .

# Runtime stage
FROM python:3.14-slim

# Create a non-root user for security
RUN useradd -m -U appuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Ensure the virtual environment is in the PATH
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=appuser:appuser . .

# Use non-root user
USER appuser

# Expose API port
EXPOSE 8000

# Run the API
CMD ["uvicorn", "entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
