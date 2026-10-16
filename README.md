# Ani Seek

[![Release](https://badgen.net/github/release/ElPitagoras14/aniseek)](https://github.com/ElPitagoras14/aniseek/releases)
[![Pipeline](https://github.com/ElPitagoras14/aniseek/actions/workflows/release.yml/badge.svg)](https://github.com/ElPitagoras14/aniseek/actions/workflows/release.yml)
[![License](https://badgen.net/github/license/ElPitagoras14/aniseek)](LICENSE)
[![Docker](https://img.shields.io/badge/ghcr.io-aniseek-2496ED?logo=docker&logoColor=white)](https://github.com/ElPitagoras14?tab=packages&repo_name=aniseek)

Self-hosted app to search, save and download anime episodes. Search by title, keep a personal list, see what is airing this week and download episodes or whole seasons with real-time progress.

https://github.com/user-attachments/assets/f1604c46-6c52-4401-9d66-e5d1b9f932f4

## Features

- **Search** — find anime by title with live scraping from AnimeAV1
- **Save** — bookmark animes to your personal list
- **Calendar** — saved animes currently airing, organized by day of the week
- **Downloads** — single episodes or entire seasons in bulk, with real-time progress (SSE)
- **History & storage** — browse downloaded episodes, monitor disk usage per anime and delete files
- **Dashboard** — download stats, recent episodes and storage consumption
- **Profile** — update your username and password

## Quick Start

**Prerequisites**: [Docker](https://docs.docker.com/get-docker/) and Docker Compose.

1. Download `compose.yaml` and `.env.example` into an empty folder:

   ```bash
   curl -O https://raw.githubusercontent.com/ElPitagoras14/aniseek/main/compose.yaml
   curl -o .env https://raw.githubusercontent.com/ElPitagoras14/aniseek/main/.env.example
   ```

2. Edit `.env` (see [Configuration](#configuration)).
3. Start everything:

   ```bash
   docker compose up -d
   ```

The app is available at **http://localhost:3000**.

> [!WARNING]
> On first startup the API creates an `admin` user with password `admin123`. Log in and change both from the **Profile** page right away.

## Configuration

All configuration lives in `.env`; every variable is listed and commented in `.env.example`. Before any internet-facing deployment, at minimum change `SECRET_KEY` — the JWT signing secret; use a long random string.

Setting `AUTH_ENABLED=false` disables the login screen entirely — useful for local development or trusted single-user setups. If `AUTH_ENABLED` is unset, login is required.

## Tech stack

- **Web**: React, Vite, TypeScript, TanStack Router/Query, shadcn/ui
- **API**: Python, FastAPI, PostgreSQL, Redis
- **Worker**: Dramatiq, [ani-scrapy](https://pypi.org/project/ani-scrapy/)
- **DevOps**: Docker, Docker Compose, GitHub Actions

## Documentation

- [Architecture](docs/architecture.md) — components, data flow and startup order
- [Deployment](docs/deployment.md) — HTTPS and internet-facing setups
- [Upgrading](docs/upgrading.md) — migration notes for existing deployments
- [Development](docs/development.md) — build from source, run locally, tests
- [Contributing](CONTRIBUTING.md) — conventions and maintainer notes

## Disclaimer

This project is intended for **educational purposes only**. The scraping functionality is designed to work with anime sources that permit such access. Users are responsible for ensuring compliance with applicable laws and the terms of service of the websites being scraped. The author assumes no liability for any misuse of this software.

## License

Released under the [Apache License 2.0](LICENSE).

## Author

[Jonathan García](https://github.com/ElPitagoras14) — Computer Science Engineer
