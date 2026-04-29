FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libpq-dev \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV PATH="/app/.venv/bin:$PATH"

# Install Python dependencies only
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project
COPY . .
RUN uv sync --frozen

EXPOSE 8000

# Run BACKEND ONLY to save RAM
CMD ["uv", "run", "reflex", "run", "--env", "prod", "--backend-only", "--backend-port", "8000"]
