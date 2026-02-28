# Build
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app
COPY pyproject.toml ./

RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc libpq-dev libffi-dev libssl-dev libxml2-dev libxslt-dev build-essential \
  && pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -e .

# Runtime
FROM python:3.12-slim-bookworm

WORKDIR /app

ARG ANIMES_FOLDER=/animes

# Libraries for Playwright/Chromium and psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
  libasound2 libatk-bridge2.0-0 libatk1.0-0 libcairo2 libcups2 libdbus-1-3 \
  libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-xcb1 libxcomposite1 libxfixes3 \
  libxkbcommon0 libxdamage1 libxrandr2 libgbm1 libxss1 libxtst6 \
  libpq5 \
  && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin
COPY src /app
COPY entrypoint.sh /entrypoint.sh

# Brave browser
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -fsS https://dl.brave.com/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir playwright

RUN useradd -m appuser

USER appuser

RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
