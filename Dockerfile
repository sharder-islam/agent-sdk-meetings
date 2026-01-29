# Build stage: install dependencies with uv
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./
RUN uv sync --frozen --no-dev --no-install-project 2>/dev/null || uv sync --no-dev --no-install-project

# Runtime stage
FROM python:3.11-slim
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY pyproject.toml ./
COPY src/ ./src/

# Create output and logs directories
RUN mkdir -p output logs

# Bot Framework expects /api/messages; default port for Agents SDK is often 3978
ENV PORT=3978
EXPOSE 3978

# Run the agent (aiohttp server)
CMD ["python", "-m", "meeting_agent"]
