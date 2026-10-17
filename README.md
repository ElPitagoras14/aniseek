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
- **MCP server** — let AI agents search, save and download anime with a per-user API key ([docs](docs/mcp.md))

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

> [!IMPORTANT]
> A fresh install needs `OWNER_USERNAME` and `OWNER_PASSWORD` in `.env`: on first startup the API creates the **owner** with them. Without them (and without an existing owner or admin) the API refuses to start. There are no default credentials.

## Configuration

All configuration lives in `.env`; every variable is listed and commented in `.env.example`. Before any internet-facing deployment, at minimum change `SECRET_KEY` — the JWT signing secret; use a long random string.

Setting `AUTH_ENABLED=false` disables the login screen entirely — useful for local development or trusted single-user setups: every request is then treated as the owner. If `AUTH_ENABLED` is unset, login is required.

### Users and access

There are three roles:

- **Owner**: exactly one per instance. Full control; can't be deleted, deactivated or demoted, and can hand the role to someone else (Instance Settings → Ownership).
- **Admin**: manages members, invitations and the registration policy, and can delete downloaded files and create franchises.
- **Member**: browses, saves and downloads.

Registration is **by invitation** by default: an owner or admin creates a single-use link (User Management → Invitations) and shares it. They can also create accounts directly, or switch the registration policy to **open** so anyone can sign up as a member.

`OWNER_USERNAME` and `OWNER_PASSWORD` are only read when the instance has no owner yet. Upgrading an existing instance needs no new variables: see [`docs/upgrading.md`](docs/upgrading.md).

### AI agents (MCP)

Ani Seek includes an [MCP](https://modelcontextprotocol.io) server so AI agents can search, save and download anime for you. It is **off by default**:

1. The owner turns it on in **Instance Settings → MCP server**.
2. Each user generates an API key in **Profile → AI agents**. The agent acts as that user, with their current role.
3. Add it to Claude Code (the same section shows this command ready to copy):

   ```bash
   claude mcp add --transport http aniseek https://<your-instance>/api/mcp \
     --header "Authorization: Bearer <your-api-key>"
   ```

Claude Desktop, the full list of tools and other details are in [`docs/mcp.md`](docs/mcp.md).

## Tech stack

- **Web**: React, Vite, TypeScript, TanStack Router/Query, shadcn/ui
- **API**: Python, FastAPI, PostgreSQL, Redis
- **Worker**: Dramatiq, [ani-scrapy](https://pypi.org/project/ani-scrapy/)
- **DevOps**: Docker, Docker Compose, GitHub Actions

## Roadmap

| Phase | Deliverable |
|---|---|
| 0 | **Users and access** — owner, admin and member roles, controlled registration |
| 1 | **MCP server** for AI agents, enabled per instance by the owner |
| 2 | **Multi-provider** scraping with fallback |
| 3 | **AniList metadata** and provider-independent identity |
| 4 | **Automation** — auto-download, notifications, download queue |
| 5 | **Player and watch progress** |
| 6 | **Platform** — quotas, observability, backups, test coverage |

Details for each phase live in [docs/roadmap](docs/roadmap/README.md).

## Documentation

- [Roadmap](docs/roadmap/README.md) — planned phases, one file per phase
- [Architecture](docs/architecture.md) — components, data flow and startup order
- [Deployment](docs/deployment.md) — HTTPS and internet-facing setups
- [MCP server](docs/mcp.md) — connect AI agents (Claude Code, Claude Desktop)
- [Upgrading](docs/upgrading.md) — migration notes for existing deployments
- [Development](docs/development.md) — build from source, run locally, tests
- [Contributing](CONTRIBUTING.md) — conventions and maintainer notes

## Disclaimer

This project is intended for **educational purposes only**. The scraping functionality is designed to work with anime sources that permit such access. Users are responsible for ensuring compliance with applicable laws and the terms of service of the websites being scraped. The author assumes no liability for any misuse of this software.

## License

Released under the [Apache License 2.0](LICENSE).

## Author

[Jonathan García](https://github.com/ElPitagoras14) — Computer Science Engineer
