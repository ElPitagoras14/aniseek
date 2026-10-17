# Phase 0: Users and access

**Status:** in progress (OpenSpec change `users-and-access`). **Depends on:** nothing. **Blocks:** Phase 1.

## Goal

Define a real access model for single-user and multi-user instances, enforce it in the backend, and remove the hard-coded default admin.

## Current state (verified 2026-10-16)

- **Roles exist but are never enforced.** `role_types` is seeded with `admin` (id 1), `member` (id 2) and `guest` (id 3) in `dbmate/migrations/0001_create_initial_schema.sql`. The role travels in the JWT and the UI shows it as a label (`frontend/src/auth.tsx`, `profile-info-card.tsx` `ROLE_LABELS`, `account-menu.tsx`, `nav-user.tsx`). No backend code checks a role; `ForbiddenError` in `backend/src/exceptions.py` is defined and unused.
- **Open registration.** `POST /auth/register` (`backend/src/packages/auth/router.py`, `service.py:45`) creates a `member` with no restriction.
- **Hard-coded admin.** `backend/src/main.py:29-36` seeds `admin` / `admin123` on startup (`auth/config.py:5-6`), using `role_id=1`. `insert_user` defaults to `role_id=2` (`auth/repository.py:47`).
- **Single-user mode is a login bypass.** With `AUTH_ENABLED=false`, `JWTBearer` (`auth/middleware.py:21-34`) always returns the `admin` user. `AUTH_ENABLED` is set in `.env.example:23` and passed to two services in `compose.yaml` (lines 13 and 30); the frontend reads it in `frontend/src/config.ts`.
- **Data scope.** The anime catalog and downloaded files are global. The saved list (`user_save_anime`) and download history (`user_download_episode`) are per user.
- **Authorization gap to check.** `valid_user_id` (`backend/src/packages/users/dependencies.py:10`) receives the current user but does not compare it with the requested one. What a user can read or edit about another user has not been audited.
- **Any logged-in user can delete global files** through `DELETE /episodes/storage/{anime_id}` (`episodes/router.py:82`).
- **API key tables exist** (`api_keys`, `api_scopes` in the initial migration) but whether any code uses them was not verified. `api_keys` has no scope column; `api_scopes` only has `name`.

## Decisions (confirmed)

### Instance modes

1. **Single-user** (`AUTH_ENABLED=false`): no login, an implicit owner. The request context resolves to the owner, not to a seeded `admin`. Meant for local use or a trusted network.
2. **Multi-user** (`AUTH_ENABLED=true`): login, roles, controlled registration.

### Roles: `owner`, `admin`, `member` (`guest` is removed)

| Capability | Owner | Admin | Member |
|---|:-:|:-:|:-:|
| Browse catalog, search, view downloaded content | yes | yes | yes |
| Own saved list and calendar | yes | yes | yes |
| Request downloads | yes | yes | yes |
| Delete global files | yes | yes | no |
| Create, deactivate, change role of users | yes | yes (cannot touch the owner or other admins) | no |
| Registration policy, invitations | yes | yes | no |
| Enable/disable MCP, providers, global settings | yes | no | no |
| Transfer ownership, view and revoke all API keys | yes | no | no |

- **Owner:** exactly one. Created at startup, cannot be deleted or demoted, can transfer the role.
- **Admin:** day-to-day user and content management; cannot change instance-critical settings.
- **Member:** regular user. No management permissions.
- Quotas are **not** part of this phase (see Phase 6).

### No seeded admin; owner created at startup

- The startup no longer seeds `admin` / `admin123`; the `ADMIN_PASS` constant disappears.
- A single `owner` is created from `OWNER_USERNAME` and `OWNER_PASSWORD` (read only at startup).
- Idempotent: if an owner already exists, the variables are ignored. The password is changed from the Profile page, not by editing `.env`.
- No default password: with no owner and missing variables, the API fails to start with a clear error.
- Single-user mode error "Admin user not seeded" becomes "Owner not created".

### Upgrade path for existing instances

- Existing deployments have an `admin` user with the admin role.
- The migration promotes that user to `owner` when no owner exists, and `docs/upgrading.md` tells the operator to change its password.
- `OWNER_*` variables are only required on fresh installs.

### Registration policy

Configurable by the owner or an admin, with two values: **invite** (default; single-use links carrying a preassigned role) or **open** (anyone can sign up as `member`). Invitations and direct user creation work under both. A third `closed` value that rejected invitations was dropped: "nobody gets in" is achieved by not issuing invitations. Invitations need a new table.

## Deviations from this plan

- **The admin is promoted at startup, not in the migration.** The migration only changes the schema (adds `owner`, drops `guest` after reassigning its users). `ensure_owner` runs in the API `lifespan`: it keeps an existing owner, otherwise promotes the oldest *active* admin, otherwise creates one from `OWNER_USERNAME` / `OWNER_PASSWORD`. One idempotent code path that the test suite can exercise, which a promotion inside the migration would not allow.
- **Two registration values, not three** (see "Registration policy" above).

## Implementation notes

- **Migration:** add a new file in `dbmate/migrations/`; do not edit `0001`. Remove `guest` (`users.role_id` is `ON DELETE RESTRICT`, so first reassign any user holding it to `member`), add `owner`, promote the existing `admin`. Role ids are hard-coded in places (`main.py` uses `role_id=1`, `insert_user` defaults to `2`); resolve roles **by name**, not by id.
- **Dependency:** add a reusable `require_role(...)` that raises `ForbiddenError`, and apply it endpoint by endpoint, starting with the ones that delete or modify global data.
- **Tests:** `backend/tests/test_infra_smoke.py:71` asserts the role set `{"admin", "member", "guest"}` and must change. `backend/tests/factories.py` `create_user` defaults to `member`. `backend/tests/dbutils.py` lists `role_types` in `PRESERVED_TABLES`. There is currently no authorization test coverage; add tests per role.
- **Docs:** remove the `admin123` warning from `README.md`, document `OWNER_USERNAME` / `OWNER_PASSWORD` in `.env.example` and `docs/deployment.md`, and pass them to the API service in `compose.yaml`.
- **UI:** a user administration page (list, create, deactivate, change role, invitations, registration policy) and `ROLE_LABELS` updated for the three roles.

## Suggested breakdown into OpenSpec changes

1. Enforce roles in the backend (`require_role`, endpoint audit, authorization tests).
2. Owner role, startup creation from env, migration (drop `guest`, add `owner`, promote `admin`), single-user mode resolving to the owner.
3. Registration policy and invitations.
4. User administration UI.

## Open questions

- Where instance-level settings live (registration policy, later the MCP toggle): a database table is needed if the owner changes them from the UI.
- What a user can read or write about other users today (audit `users/router.py`).
