FROM python:3.11

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_PROJECT_ENVIRONMENT=/usr/local
ENV UV_PYTHON_DOWNLOADS=never

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-managed-python

COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "deliverx.main:app", "--host", "0.0.0.0", "--port", "8000"]