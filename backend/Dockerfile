FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv --link

WORKDIR /app

COPY pyproject.toml uv.lock .
RUN uv sync --frozen

COPY . .

CMD ["python", "main.py"]
