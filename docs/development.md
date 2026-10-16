# Development

## Build from source with Docker

Builds all images locally. Useful for testing changes.

```bash
git clone https://github.com/ElPitagoras14/aniseek.git
cd aniseek
cp .env.example .env
docker compose -f compose.dev.yaml up -d
```

The app is available at **http://localhost:3000**.

## Run services natively

Runs each service on the host, with only PostgreSQL and Redis in Docker.

**Prerequisites**: Docker, [uv](https://docs.astral.sh/uv/getting-started/installation/), [pnpm](https://pnpm.io/installation), [VS Code](https://code.visualstudio.com/)

```bash
cp .env.example .env

# install dependencies
cd backend  && uv sync && cd ..
cd worker   && uv sync && cd ..
cd frontend && pnpm install && cd ..

# start infrastructure only
docker compose -f compose.dev.yaml up aniseek-db aniseek-redis -d
```

Then launch the three services from VS Code via **Tasks: Run Task** — `Run Backend`, `Run Dramatiq`, and `Run Frontend`.

## Testing

The backend has an automated test suite covering the atomicity of its transactional paths. It requires Docker running — the suite provisions its own ephemeral PostgreSQL database (schema built via the dbmate migrations under `dbmate/migrations/`) and tears it down when it finishes, successfully or not.

```bash
cd backend
uv run pytest
```

No other setup is needed: the suite does not use the development database, Redis, or the network.
