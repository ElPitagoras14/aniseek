# Phase 1: MCP server for AI agents

**Status:** done. OpenSpec changes `api-keys` (3.1.0) and `mcp-server` (3.2.0). Usage in [`docs/mcp.md`](../mcp.md). **Depends on:** Phase 0 (done).

## Goal

Let an AI agent search, organize and download anime through the Model Context Protocol. It is an **instance-level** feature, switched on by the owner, not a per-user toggle.

## Decisions (confirmed 2026-10-16)

### Identity and permissions

- **An API key belongs to a user and inherits that user's role.** The role is read on every call, never stored in the key, so a role change or deactivation takes effect on the next call.
- **No scopes in v1.** A key can do exactly what its user can do through the REST API. Restricting a key below its user's role may come later as an optional limit.
- **One key per user, no expiration in v1.** Regenerating replaces it (the old key stops working immediately; the new one is shown once). Revoking deletes it. No history of revoked keys.
- **Hashed storage.** Only a SHA-256 hash and a short display prefix are stored. Keys are long random tokens, so a slow hash is not needed.
- **Who manages keys:** each user generates, regenerates and revokes their own. The owner can view and revoke any user's key.
- **Deactivated users:** their key stops working (checked on every call, like `JWTBearer` does for JWTs).
- **Single-user mode** (`AUTH_ENABLED=false`) still requires an API key for the MCP. The owner generates it from the Profile page. An unauthenticated MCP on an app with no login would be full access for anyone on the network.

### Activation

- **A single instance switch, owner only:** `instance_settings.mcp_enabled`, changed through a dedicated `PUT /settings/mcp` guarded by `require_role("owner")`. `PUT /settings` stays admin-level for the registration policy.
- **Always mounted, guarded:** with MCP off, a guard answers 404, so the endpoint behaves as if it did not exist. Turning it on takes effect without a restart.
- **Keys survive the switch:** turning MCP off keeps existing keys; they just do not work until it is turned back on.

### Transport and location

- A module inside the API (reuses services and auth, no extra container).
- **Streamable HTTP only**, mounted at `/api/mcp`. `frontend/nginx.conf` already proxies `/api/` with `proxy_buffering off`, so no proxy or compose change is needed.
- **No stdio in v1.** Clients that only speak stdio can use a bridge such as `mcp-remote`.
- The MCP session manager runs inside the API `lifespan` (`backend/src/main.py`).

### Tools

- Tools call the existing service controllers directly with the user id, not the REST API over HTTP.
- **Exposed ids are provider-namespaced (`animeav1:slug`) in the MCP only.** A translation layer parses them and rejects unsupported providers; the REST API keeps plain slugs for now. This keeps the tool contract stable for Phase 2.
- **No administration tools in v1** (users, invitations, settings stay in the UI).
- **`download_episodes`:** at most 25 episodes per call, fixed in code. A larger request is rejected whole with a message telling the agent to split it. Episodes already downloaded are skipped and reported, and do not count against the cap. Quotas belong to Phase 6.
- **`delete_anime_files`:** admin and owner only, annotated as destructive (`destructiveHint`) so clients ask for confirmation. No `confirm` parameter, since an agent would fill it in by itself.
- Tools a role cannot use are hidden from `list_tools`; the role is still checked at execution time because it can change mid-session.

## State before implementation (verified 2026-10-16)

Kept as the starting point the plan was written against; what changed is under "Deviations" below. The REST API already covered most of what the tools need:

- Animes: `GET /animes/search`, `/saved`, `/in-emission`, `/{anime_id}`, `PUT /{anime_id}` (refresh), `/{anime_id}/save`, `/{anime_id}/unsave`.
- Episodes: `GET /episodes/downloads`, `/downloads/last`, `/downloads/animes`, `/storage`, `DELETE /storage/{anime_id}` (admin), `GET /stream/status` (SSE), `GET /{anime_id}/{episode_number}/file`, `POST /{anime_id}/download/bulk`.
- Users: `GET /users/statistics`, `/users/me`, and others.
- Franchises: `GET/POST /franchises`, `GET /franchises/animes`.
- Phase 0 left `instance_settings` (single row, `registration_policy`), `require_role` / `ROLE_RANK` in `backend/src/packages/auth/roles.py`, and `JWTBearer` building the `current_user` dict in `auth/middleware.py`. API key auth must build the same dict and must **not** go through the single-user shortcut in `JWTBearer`.
- `api_keys` (`id SERIAL`, plain `key`, `expired_at`, `last_used_at`) and `api_scopes` (`name`) exist in `0001` but no code uses them. They are dropped and replaced by a new `api_keys` table (one row per user, `prefix`, `key_hash`, `created_at`, `last_used_at`; no expiration in v1) in a new migration.
- The `mcp` Python SDK is not a dependency yet.

## Proposed tools

| Tool | Member | Admin | Owner |
|---|:-:|:-:|:-:|
| `search_anime`, `get_anime`, `list_saved`, `list_airing` (by weekday), `list_downloads`, `get_storage_usage`, `get_stats` | yes | yes | yes |
| `save_anime`, `unsave_anime`, `refresh_anime` | yes | yes | yes |
| `download_episodes` (cap 25), `get_download_status` | yes | yes | yes |
| `delete_anime_files` | no | yes | yes |

Resources and prompts: `aniseek://saved`, `aniseek://calendar`; prompts such as "what am I missing from what I follow".

## Breakdown into OpenSpec changes

1. **`api-keys`:** migration (drop old tables, create the new one), generate / regenerate / revoke endpoints, owner listing and revocation, API key authentication building `current_user`, UI in Profile and in User management. No new dependency.
2. **`mcp-server`:** `mcp_enabled` column and `PUT /settings/mcp`, 404 guard, MCP session manager in the lifespan, tools and id translation, `mcp` SDK dependency, toggle in the Settings tab, `docs/mcp.md` with Claude Desktop and Claude Code examples.

Both deserve a `VERSION` bump.

## Deviations from this plan (`mcp-server`)

- **Location:** `backend/src/mcp_server/`, next to `routes.py`, not a package under `packages/`: the MCP is a second interface over the domain services, not a domain. Not named `mcp`, which would shadow the SDK on the import path.
- **SDK:** official `mcp` 2.x (`MCPServer`), without its OAuth-oriented auth. A small ASGI gate at `/api/mcp` checks `mcp_enabled` (404) and then the API key (401).
- **User propagation:** the SDK serves stateless requests from a task group opened in the lifespan, so a contextvar set by the gate does not reach the tools. The gate stores the user in the ASGI scope and the tools read it from the request the SDK hands them.
- **Business rules moved to the services** (refresh cooldown, anime existence, double save/unsave) so REST and MCP share them. The bulk download reports a `reason` per failed episode.
- **`get_download_status` works by anime and episode number,** not by job id: the worker clears the job id when a download succeeds.
- **Instance Settings page:** the registration policy, the MCP switch and the ownership transfer moved from a User Management tab to a new **Instance Settings** page (`/instance-settings`, admin and owner) above **Profile** in the sidebar. In single-user mode it only shows the MCP switch.
- **Profile → AI agents** replaces the API key section: the key, the endpoint and a ready-to-copy Claude Code command, dimmed while the MCP is off. Any user reads that state from `GET /settings/mcp`.
- **Resources and prompts** (`aniseek://saved`, etc.) were left for later.

## Open questions

- Per-tool rate limiting (deferred to Phase 6 with quotas).
- Resources (`aniseek://saved`, `aniseek://calendar`) and prompts ("what am I missing from what I follow"): not built in `mcp-server`; a follow-up change if agents need them.
