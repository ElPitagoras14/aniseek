# Franchises

**Status:** partial. Only creation and listing exist. **Depends on:** nothing. **Related:** [anilist-metadata](anilist-metadata.md) (automatic grouping from relations), [mcp](mcp.md) (franchise tools).

## Goal

Full franchise support: create, update and delete franchises, and relate animes to them (add, remove, change season, move between franchises), from the API, the UI and the MCP. A franchise groups the seasons and sequels of one series under a single folder on disk.

## Current state (verified 2026-11-11)

- **Schema:** `franchises (id, name, created_at)`; `animes.franchise_id` references it with `ON DELETE SET NULL`, and `animes.season` defaults to 1 (`dbmate/migrations/0001_create_initial_schema.sql`).
- **API** (`backend/src/packages/franchises/router.py`):
  - `GET /franchises`: franchises with their animes. Any logged-in user.
  - `POST /franchises`: creates a franchise from `{franchise, animes: [{id, season}]}`. `require_role("admin")`.
  - `GET /franchises/animes`: animes with a poster and no franchise, to pick from.
  - There is no endpoint to read one franchise, update it, delete it, or add/remove animes afterwards.
- **Create flow** (`service.py`): the franchise id is the kebab-case name; it is rejected with `ConflictError` if it equals one of the anime ids (the franchise folder would collide with an anime folder). It inserts the franchise, assigns the animes with a plain `UPDATE`, and dispatches the `order_franchise` task to the worker.
- **Gaps in the create flow:** it does not use `get_franchise_by_id`, `get_animes_by_ids` or `get_anime_without_franchise` (all exist in `repository.py`), so it does not check that the franchise id is free, that the animes exist, or that they have no franchise yet; an anime that already belongs to another franchise would be silently reassigned.
- **Worker ordering** (`worker/src/tasks/order.py`): waits for in-flight downloads of the franchise (Redis lock and `downloads_done` event), moves `ANIMES_FOLDER/<anime_id>/Season NN` to `ANIMES_FOLDER/<franchise_id>/Season MM`, renames files from `SNNE` to `SMME`, and updates `animes.season`. Downloads made after an anime joins a franchise already go to the franchise folder (`tasks/download.py`).
- **Limits of the ordering:** it only knows how to move out of the anime's own folder. For an anime already inside a franchise, the source folder does not exist, so it logs "Folder not found" and still updates the season in the database (disk and database diverge). Two animes mapped to the same season would be moved onto the same destination folder. The worker has no tests.
- **Bug found:** `is_saved` in `GET /franchises` and `GET /franchises/animes` is computed as `anime_id in user_id` (`service.py`), a substring check against the user id string, not a lookup in the user's saved list. It is wrong for every anime.
- **UI:** `frontend/src/routes/_app/franchise.tsx` is a placeholder (`Hello "/_app/franchise"!`); there is no franchise screen yet.
- **MCP:** no franchise tools.
- **Tests:** only `backend/tests/test_franchises_atomicity.py` (creation).

## Scope

- **Create:** keep the current contract and harden it: unique franchise id, existing animes, animes without a franchise (or an explicit move), unique seasons inside the franchise.
- **Read:** `GET /franchises/{id}` with animes ordered by season; fix `is_saved`.
- **Update:** rename the franchise; change an anime's season.
- **Delete:** remove a franchise and ungroup its animes.
- **Relate animes:** add animes to an existing franchise, remove an anime from it, move it to another franchise. Optionally suggest candidates from the scraper's `related_info` (prequel, sequel) when the user opens a franchise.
- **Disk consistency:** every operation that changes membership or season goes through the worker, which moves and renames files, reusing the existing lock that pauses downloads of the franchise while it runs. The ordering has to handle moves between franchises, ungrouping, and season collisions.
- **Permissions:** read for any member; create, update, delete and relate for admin and owner, like creation today.
- **UI:** a franchise page (list, create, edit, delete, add/remove animes, set seasons), built on the existing route.
- **MCP:** tools to list franchises and, for admin and owner, create, update, delete and relate. Deleting is annotated as destructive.
- **Tests:** repository and service tests per operation, and tests for the worker ordering (move in, move between, ungroup, collision).

## Open questions

- **Franchise id on rename:** the id is the folder name. Keeping the id stable and changing only `name` avoids moving files, at the cost of a folder name that no longer matches the title. The alternative is renaming the folder through the worker.
- **What deleting does to files:** move the files back to `ANIMES_FOLDER/<anime_id>/Season NN` (and renumber), leave them in place, or refuse to delete while the franchise has downloaded episodes.
- **Season semantics:** whether an anime's season inside a franchise must be unique, and whether movies, OVAs and specials need their own numbering.
- **Removing one anime** from a franchise: whether its season resets to 1.
- **Operations while downloads are running:** wait (as ordering does today) or reject.
- **Failure handling:** what the user sees if the worker fails halfway, and whether the database change is applied before or after the files move.
