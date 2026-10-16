# Phase 4: Automation

**Status:** not started. **Depends on:** Phase 2 (provider fallback) and Phase 3 (stable identity).

## Goal

Make the app proactive: new episodes are detected and downloaded without the user asking, and the user is told when something happens.

## Scope

- **Auto-download** of new episodes for saved animes that are airing. A periodic worker job compares against `last_scraped_at` and uses `get_new_episodes`.
- **Provider priority:** use AnimeAV1 (HTTP, fast) and fall back to JKAnime only on failure. JKAnime needs a browser and was measured at about 31 s per info call, so the periodic check over all saved animes must not run on it.
- **Per-anime rules:** preferred server, retention.
- **Notifications:** webhook, Telegram or Discord when an episode appears or a download finishes.
- **Visible queue:** pause, cancel and retry downloads from the UI. Today downloads are dispatched through Dramatiq and reported over SSE (`GET /episodes/stream/status`).
- **With the MCP:** an agent configures rules and the app runs them unattended.

## Notes

- The download flow is documented in `docs/architecture.md` (API creates a task in PostgreSQL, dispatches to the worker through Redis, the worker updates status).
- Who owns an auto-download (which user it is attributed to) must be defined; downloads are recorded per user in `user_download_episode`, while files are global.
- Downloads are limited by the disk shared at `ANIMES_FOLDER`; disk quotas arrive in Phase 6.

## Open questions

- Scheduling mechanism (Dramatiq periodiq, cron in the worker, or an external scheduler).
- Notification channels to support first.
- Whether rules are per user or per anime, and who can create instance-wide rules (owner/admin per Phase 0).
