FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv --link

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_HTTP_TIMEOUT=300 \
    PYTHONUNBUFFERED="true"

# this readme is necessary otherwise uv install might complain if it's in pyproject.toml
# and instead of actual readme we're echoing a dummy one
# to remove dependency of the actual readme file on the
# the docker build cache
RUN echo "cartostrophe backend service" > README.md
COPY pyproject.toml uv.lock* ./

# Install dependencies using the cache mount
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

COPY . /app/

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
