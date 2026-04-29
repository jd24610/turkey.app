FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libpq-dev \
    unzip \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV PATH="/app/.venv/bin:$PATH"

# Install Python dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project
COPY . .
RUN uv sync --frozen

# Build the Reflex frontend (generates .web/out/)
RUN uv run reflex export --frontend-only --no-zip 2>&1 || true

EXPOSE 8000

# Run full app (backend serves the pre-built frontend)
CMD ["uv", "run", "reflex", "run", "--env", "prod", "--backend-only", "--backend-port", "8000"]
