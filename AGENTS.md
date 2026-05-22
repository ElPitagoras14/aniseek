# Agent Coding Guidelines

## Repository Structure

```
/
├── backend/   # FastAPI REST API (Python 3.10.14)
├── worker/    # Dramatiq workers (Python 3.10.14)
├── frontend/  # Next.js 15 / React 19
└── requests/  # Bruno API collection — DO NOT MODIFY
```

No shared code between projects. Each has its own dependencies and Dockerfile.

---

## Backend Module Structure

Every module under `backend/src/packages/<module>/` **must** include these files — never skip or merge them:

```
config.py / dependencies.py / router.py / service.py / schemas.py / responses.py / utils.py
```

Centralized utilities in `backend/src/utils/` (`exceptions.py`, `exception_handlers.py`, `responses.py`) — always reuse, never duplicate.

---

## Worker

Communicates with backend **exclusively via Dramatiq/Redis** — no HTTP calls or shared imports.

- Backend task definitions: `backend/src/worker.py`
- Worker logic: `worker/src/main.py`

---

## Rules

- **Never hardcode** secrets or URLs — use `.env` (see `.env.example`).
- **Never modify**: `backend/src/databases/postgres/init.sql` or anything in `requests/`.
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
