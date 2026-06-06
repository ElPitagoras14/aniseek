# Agent Coding Guidelines

## Repository Structure

```
/
├── backend/   # FastAPI REST API (Python 3.10.14)
├── worker/    # Dramatiq workers (Python 3.10.14)
├── frontend/  # Vite / React / TanStack Router (TypeScript)
└── requests/  # Bruno API collection — DO NOT MODIFY
```

No shared code between projects. Each has its own dependencies and Dockerfile.

---

## Backend Module Structure

Every module under `backend/src/packages/<module>/` includes these files:

```
__init__.py / config.py* / dependencies.py / repository.py / router.py / service.py / schemas.py* / responses.py / utils.py
```

> `*` optional — not all modules require `config.py` or `schemas.py`.
> Some modules add extra files (e.g. `scraper.py`, `middleware.py`).

Centralized utilities at `backend/src/` root: `exceptions.py`, `handlers.py`, `responses.py`, `utils.py` — always reuse, never duplicate.

Database client and config live under `backend/src/database/`.

---

## Worker

Communicates with backend **exclusively via Dramatiq/Redis** — no HTTP calls or shared imports.

- Backend task definitions: `backend/src/worker.py`
- Worker logic: `worker/src/main.py`

---

## Frontend Structure

Feature-based architecture: each feature under `src/features/<name>/` owns its `api.ts`, `components/`, `types.ts`, `lib/`, and `hooks/`.

Shared pieces: `src/components/` (UI), `src/hooks/`, `src/lib/`.

File-based routing via TanStack Router — routes live in `src/routes/`.

---

## Rules

- **Never hardcode** secrets or URLs — use `.env` (see `.env.example`).
- **Never modify**: `backend/src/database/postgres/init.sql` or anything in `requests/`.
- Python: PEP 8, type hints, `snake_case`/`PascalCase`. Formatter: Black (VSCode only).
- TypeScript: explicit types, no `any`, `camelCase`/`PascalCase`. Formatter: Prettier (VSCode only).
- Imports order: stdlib → third-party → local, alphabetical.
- Commits: Conventional Commits (`feat: description`).

## Git Conventions

### Commit Convention

Header format: `<type>(scope): <short description>`

Rules:

- lowercase
- imperative mood
- max ~72 chars
- scope optional
- use body description for longer descriptions
- make small but complete commits
- commit `pyproject.toml` in the last commit when it changes

Minimal types:

- `feat` -> new feature
- `fix` -> bug fix
- `refactor` -> code improvement without behavior change
- `chore` -> maintenance, dependencies, CI, docs

Examples:

```
feat(auth): add JWT authentication
```

```
feat(discovery): implement SNMP device discovery

Adds SNMP-based discovery to automatically detect devices
in a network segment.

This allows network engineers to bootstrap inventory faster.
```

Optional body:

```bash
git commit -m "feat(auth): add JWT authentication" -m "Adds JWT middleware and token validation."
```

Git CLI:

```bash
git add <file> <file> ...
git commit -m "feat(auth): add JWT authentication"
git push
```

---

### Pull Request Convention

Title format: Same as commit convention

Body: PR description template

Labels: Recommended labels

- `feature` - new features (type: feat)
- `bug` - bug fixes (type: fix)
- `maintenance` - refactor, chore, docs, etc.

GitHub CLI:

```bash
# Create PR
gh pr create --fill --label feature
```
