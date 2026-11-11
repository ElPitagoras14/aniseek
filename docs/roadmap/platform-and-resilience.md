# Platform and resilience

**Status:** continuous. Items can be picked up independently, and test coverage is worth having before the large items.

## Quotas (moved here from `users-and-access`)

Per-user limits that keep one member from saturating the instance:

- **Simultaneous downloads** (for example 3). Protects the worker and the providers.
- **Disk** (for example 50 GB of episodes attributed to the user).
- **Requests per day** (for example 50 episodes).
- Bulk downloads (`POST /episodes/{anime_id}/download/bulk`) can fill the shared disk with one request.

**Unresolved design problem:** files are global. If user A and user B request the same episode, who is charged for the disk? `user_download_episode` records both users, so a rule has to be defined (charge the first requester, split, or charge none for shared files). If a minimal limit is wanted earlier, make it simultaneous downloads only.

Quotas are configured by the owner (roles from [users-and-access](users-and-access.md)).

## Test coverage

Known gaps found during planning (codegraph reported no covering tests):

- The `Anime` response model (`backend/src/packages/animes/responses.py`).
- The login flow (`backend/src/packages/auth/router.py`).
- Frontend episode components (`episodes-tab.tsx`, `episodes-table.tsx`).
- Authorization by role: added by `users-and-access`.

Existing backend tests include `backend/tests/test_animes_sync.py` and `test_infra_smoke.py`.

## Unauthenticated endpoints (found while building the MCP)

Two REST endpoints answer without any credential, by design or by omission. Decide whether they stay public:

- `GET /episodes/stream/status?job_ids=...` (SSE of download progress): anyone who knows or guesses a job id can follow it.
- `GET /episodes/{anime_id}/{episode_number}/file` (`valid_downloaded_episode_by_number_public`): serves any downloaded episode file to anyone who can reach the API.

The MCP does not return file URLs, so the MCP does not widen this surface.

## Observability

- Metrics and alerts when a provider fails (builds on the per-provider health from [multi-provider](multi-provider.md)).
- Structured logs of scraper errors; the backend already translates `ani-scrapy` errors into API errors in `scraper.py`.

## Backups and export

- Backup and export of the PostgreSQL data and of the saved list.
- Document volume handling in `docs/deployment.md` (`postgres-data`, `redis-data`, `anime-data`).

## Dependencies

- `ani-scrapy` is pinned to `==0.10.0` in `backend/` and `worker/`. Review upstream releases regularly and watch for the removal of AnimeFLV.
