FROM python:3.15-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-install-project
COPY data ./data
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "data/scrapping/reviews/main.py"]
