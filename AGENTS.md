# Agent Coding Guidelines

## 1. Project Overview

This is a modular monorepo composed of 4 isolated, self-contained folders. Each project has its own dependencies, configuration, and Dockerfile. There is no shared code between them.

External services (PostgreSQL, Redis) are managed via Docker Compose.

---

## 2. Repository Structure

```
/
├── backend/       # FastAPI REST API (Python 3.10.14)
├── queue/         # Dramatiq workers (Python 3.10.14)
├── frontend/      # Next.js 15 / React 19 application
├── requests/      # Bruno API collection — DOCUMENTATION ONLY, do not modify
└── docker-compose.yaml
```

- **`backend/`**: Main API. Handles business logic, auth, database access, and dispatches tasks to the queue via Dramatiq.
- **`queue/`**: Dramatiq workers that consume tasks from Redis. Communicates with backend exclusively through Dramatiq/Redis.
- **`frontend/`**: Next.js app that consumes the backend API.
- **`requests/`**: Bruno API request collection for documentation purposes. **Never modify any file in this folder.**

---

## 3. Services & Docker

Services are orchestrated via `docker-compose.yaml` in the root. Startup dependencies:

- `backend` and `queue` depend on **postgres** and **redis**
- `frontend` depends on **backend**

To start only the external services needed for local development, run from the root:

```bash
docker compose up db redis -d
```

The agent may run `docker compose up` when external services are required to complete a task.

---

## 4. Commands per Project

### Backend (`backend/`)

```bash
# Install / sync dependencies
uv sync

# Run development server
uv run src/main.py
```

- Python version: **3.10.14**
- The virtual environment (`.venv`) is git-ignored. Run `uv sync` if it does not exist.

### Queue (`queue/`)

```bash
# Install / sync dependencies
uv sync

# Run Dramatiq worker
uv run dramatiq main --processes 2 --threads 4
```

- Python version: **3.10.14**
- The virtual environment (`.venv`) is git-ignored. Run `uv sync` if it does not exist.

### Frontend (`frontend/`)

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Validate build — ALWAYS run before considering a task complete
npm run build
```

---

## 5. Backend Architecture (FastAPI)

Every domain module under `backend/src/packages/` **must** follow this structure:

```
packages/
└── <module>/
    ├── router.py      # Route definitions (APIRouter)
    ├── service.py     # Business logic
    ├── schemas.py     # Pydantic models (request/response)
    ├── responses.py   # Standardized response definitions
    └── utils.py       # Module-specific helpers
```

- **Never** skip or merge these files when creating a new module.
- Responses and exceptions are **centralized** in `backend/src/utils/`:
  - `exceptions.py` — custom exception classes
  - `exception_handlers.py` — FastAPI exception handlers
  - `responses.py` — shared response helpers
- Always reuse centralized utilities instead of duplicating logic inside modules.

---

## 6. Queue Architecture (Dramatiq)

- The queue communicates with the backend **exclusively via Dramatiq/Redis**. No direct HTTP calls or shared imports between `backend/` and `queue/`.
- Task definitions used by the backend are in `backend/src/worker.py`.
- Worker execution logic lives in `queue/src/main.py`.

---

## 7. Environment Variables

- A `.env` file exists in the project root and is git-ignored.
- Use `.env.example` as reference for required variables.
- **Never hardcode** sensitive values (credentials, secrets, URLs) anywhere in the codebase.

---

## 8. Code Style

### Python (`backend/`, `queue/`)

- Follow **PEP 8**.
- Naming: `snake_case` for variables, functions, modules; `PascalCase` for classes.
- Always use **type hints**.
- Formatter: **Black** — managed via VSCode extension, do not run manually.

### TypeScript (`frontend/`)

- Follow Next.js and React best practices.
- Naming: `camelCase` for variables and functions; `PascalCase` for components and types.
- Always use explicit types; avoid `any`.
- Formatter: **Prettier** — managed via VSCode extension, do not run manually.

### General

- Organize imports: standard library → third-party → local.
- Implement robust error handling with clear, descriptive messages.

---

## 9. Git Conventions

Use **Conventional Commits** for all commit messages:

```
<type>: <short description>
```

**Types**: `feat`, `fix`, `chore`, `refactor`, `docs`, `style`, `perf`, `ci`

Commit with title only:

```bash
git commit -m "feat: add episode download endpoint"
```

Commit with title and optional description:

```bash
git commit -m "feat: add episode download endpoint" -m "Supports both single and bulk downloads. Dispatches tasks to the queue via Dramatiq."
```

---

## 10. Files & Folders — Never Modify

The following must **never** be modified by the agent:

- `backend/src/databases/postgres/init.sql` — initial database schema, managed manually.
- `requests/` — Bruno API collection, documentation only.
