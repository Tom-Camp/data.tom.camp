FROM ghcr.io/civicactions/pyction:latest

WORKDIR /app

COPY pyproject.toml uv.lock ./
ENV UV_PROJECT_ENVIRONMENT=/tmp/venv
RUN uv sync --no-dev

COPY . .
RUN chmod +x entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]
