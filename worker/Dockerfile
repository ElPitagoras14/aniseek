FROM python:3.12-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:0.9.15 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev --no-install-project

FROM python:3.12-slim-bookworm AS production

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -fsS https://dl.brave.com/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN playwright install --with-deps chromium

COPY src /app
COPY entrypoint.sh /entrypoint.sh

RUN useradd -m appuser \
    && chmod +x /entrypoint.sh \
    && chown -R appuser:appuser /ms-playwright

ENTRYPOINT ["/entrypoint.sh"]
