# Phase 1: MCP server for AI agents

**Status:** not started. **Depends on:** Phase 0 (roles, owner, instance settings).

## Goal

Let an AI agent search, organize and download anime through the Model Context Protocol. It is an **instance-level** feature, switched on by the owner, not a per-user toggle.

## Decisions (confirmed)

- **Activation:** a single instance switch that only the owner can change. With MCP off, the endpoint does not exist.
- **Location:** a module inside the API (reuses services and auth, no extra container). Transport: Streamable HTTP, with optional stdio for local use.
- **API keys belong to a user.** The agent acts as someone, because the saved list and download history are per user.
- **Keys never exceed their owner's role.** Suggested scopes: `read`, `library` (save/unsave), `download`, `admin`.
- **Who issues keys:** each user can generate their own while MCP is enabled. The owner can view and revoke any key.
- **Single-user mode** (`AUTH_ENABLED=false`) still requires an API key for the MCP. An unauthenticated MCP on an app with no login would be full access for anyone on the network.
- **Exposed IDs must not assume AnimeAV1**, so the tool contract survives Phase 2 (provider-namespaced ids such as `jkanime:slug`).

## Current state (verified 2026-10-16)

The REST API already covers most of what the tools need:

- Animes: `GET /animes/search`, `/saved`, `/in-emission`, `/{anime_id}`, `PUT /{anime_id}` (refresh), `/{anime_id}/save`, `/{anime_id}/unsave`.
- Episodes: `GET /episodes/downloads`, `/downloads/last`, `/downloads/animes`, `/storage`, `DELETE /storage/{anime_id}`, `GET /stream/status` (SSE), `GET /{anime_id}/{episode_number}/file`, `POST /{anime_id}/download/bulk`.
- Users: `GET /users/statistics`, `/users/me`, and others.
- Franchises: `GET/POST /franchises`, `GET /franchises/animes`.
- `api_keys` (`user_id`, `key`, `expired_at`, `last_used_at`) and `api_scopes` (`name`) tables exist in the initial migration. Usage in code was not verified. `api_keys` has no scope column, so scopes need a link table or a column. The `key` column should hold a **hash**, not the plain key; this needs a migration.

## Proposed tools

- **Read-only:** `search_anime`, `get_anime`, `list_saved`, `list_airing` (filterable by weekday), `list_downloads`, `get_storage_usage`, `get_stats`.
- **Low-risk writes:** `save_anime`, `unsave_anime`, `refresh_anime`.
- **Costly actions:** `download_episodes` (with a per-call cap), `get_download_status`.
- **Destructive:** `delete_anime_files`. Leave it out of the first version, or require explicit confirmation and an admin scope.
- **Resources and prompts:** `aniseek://saved`, `aniseek://calendar`; prompts such as "what am I missing from what I follow".

## Deliverables

- Instance MCP switch (owner only) backed by instance settings from Phase 0.
- API key management: create, list, revoke, scopes, hashed storage, `last_used_at`.
- The MCP module with the tools above, authenticated by API key.
- Tests, `docs/mcp.md`, and example configuration for Claude Desktop and Claude Code.

## Open questions

- Per-tool rate limiting and the cap for `download_episodes`.
- Whether the MCP shares the API process and port or mounts under a prefix.
