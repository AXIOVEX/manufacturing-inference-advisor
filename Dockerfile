# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:0.10.0 AS uv
FROM python:3.12-slim-trixie AS runtime
COPY --from=uv /uv /usr/local/bin/uv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_LINK_MODE=copy PATH="/app/.venv/bin:$PATH" INFERENCE_DATA_DIR=/data
WORKDIR /app
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml uv.lock LICENSE README.md ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src ./src
COPY catalog ./catalog
RUN uv sync --frozen --no-dev && useradd --uid 10001 --create-home advisor && mkdir -p /data/artifacts && chown -R advisor:advisor /data /app
LABEL org.opencontainers.image.title="Manufacturing Inference Advisor MCP" \
      org.opencontainers.image.description="Evidence-aware, vendor-neutral infrastructure sizing and sourcing workflow" \
      org.opencontainers.image.licenses="MIT" \
      io.modelcontextprotocol.server.name="manufacturing-inference-advisor" \
      com.docker.mcp.packaging.version="v1.0"
USER advisor
ENTRYPOINT ["inference-advisor-mcp"]

FROM runtime AS ci
USER root
RUN uv sync --frozen --extra dev
COPY tests ./tests
COPY scripts ./scripts
COPY spec-kit-extensions.lock.json ./
COPY .specify/extensions/aee/extension.yml ./.specify/extensions/aee/extension.yml
COPY .specify/extensions/evaluator/extension.yml ./.specify/extensions/evaluator/extension.yml
RUN chown -R advisor:advisor /app
USER advisor
ENTRYPOINT []
CMD ["sh", "-c", "python scripts/verify_extensions.py && pytest -p no:cacheprovider --cov=inference_advisor --cov-report=term-missing --cov-fail-under=85 && ruff check src tests scripts && mypy src/inference_advisor"]
