# Changelog

Every release has a `## X.Y.Z` section, where `X.Y.Z` is the content of `VERSION`. The release pipeline publishes that section as the body of the GitHub release, and fails before building anything if it is missing. Earlier releases are summarized below by milestone; the rest are listed in [GitHub Releases](https://github.com/ElPitagoras14/aniseek/releases). Upgrade steps for each milestone are in [`docs/upgrading.md`](docs/upgrading.md).

## 3.3.0

### Added

- **The worker downloads from MP4Upload.** When AnimeAV1 offers no Pixeldrain link for an episode, the worker now tries its MP4Upload link before falling back to JKAnime. MP4Upload answers 403 to downloads without a `Referer` header, so the worker sends `Referer: https://www.mp4upload.com/` on the range check and on the download.

### Changed

- **`ani-scrapy` is now 0.10.0** in the API and the worker (it was 0.8.1). Nothing in the API needed to change.
- **Python 3.11 or newer** is required to run the API and the worker outside Docker, as `ani-scrapy` 0.9.0 dropped Python 3.10. The Docker images already use Python 3.12, so deployments are not affected.
- The `ani-scrapy` skill is no longer copied into the repository; it is read from the upstream repository.

### What Ani Seek includes at this version

- **Catalog:** search anime by title (AnimeAV1), save a personal list, and see saved animes that are airing, by weekday.
- **Downloads:** single episodes or whole seasons, queued through Dramatiq and Redis, with live progress over SSE. The worker tries AnimeAV1 (Pixeldrain, then MP4Upload) and falls back to JKAnime (Mediafire, Streamwish), retrying failed downloads.
- **Storage:** download history, disk usage per anime, and deletion of files (admin and owner).
- **Franchises:** group animes under one franchise with a season each; the worker moves and renames the files on disk. Only creating and listing exist so far.
- **Users and access:** one owner, admins and members; registration by invitation (default) or open; instance settings; single-user mode without login.
- **MCP server for AI agents:** off by default, switched on by the owner, authenticated with a per-user API key that inherits the user's role.
- **Deployment:** four images (`api`, `worker`, `web`, `migrate`) published to GHCR with the same version, run with Docker Compose.

## 3.2.0

### Added

- **MCP server for AI agents.** Off by default; the owner switches it on in the new **Instance Settings** page. Agents act as the user whose API key they use, with that user's current role. See [`docs/mcp.md`](docs/mcp.md).
- **Instance Settings page**, next to Profile in the sidebar. The registration policy and the ownership transfer moved there from User Management.

### Notes

- 3.1.0 was tagged on the same commit and published a minute earlier, so it has the same content as 3.2.0.

## 3.1.0

### Added

- **Per-user API keys.** Each user generates, regenerates and revokes their own key from a redesigned Profile page; the owner can revoke any key.

### Changed

- Migration `0003` replaces the unused `api_keys` and `api_scopes` tables with a new `api_keys` table.

## 3.0.0

### Breaking changes

- **The `admin` / `admin123` account is no longer seeded.** On upgrade, the oldest active admin becomes the **owner**. A fresh install needs `OWNER_USERNAME` and `OWNER_PASSWORD`; without them (and without an existing owner or admin) the API refuses to start.
- **The `guest` role is gone.** Users that had it become `member`.
- **Registration is by invitation by default.** `POST /auth/register` answers 403 without an invitation unless the owner or an admin switches the policy to open.

### Added

- **Roles enforced in the API:** owner (exactly one), admin and member.
- **User management:** create accounts, invitations, deactivate users and change roles.

Steps and rollback in [`docs/upgrading.md`](docs/upgrading.md#300-users-and-access).

## 2.2.0

### Added

- **Mobile layout:** bottom navigation and responsive views.

## 2.0.20

### Changed

- **The database schema is managed with dbmate.** A one-shot `aniseek-migrate` service applies the migrations before the API and worker start, and `postgres/init.sql` is gone. The migrations ship in the `aniseek-migrate` image, published with the same version as the other services.
- **One version for every service**, kept in `VERSION`.

Deployments created before this release need the steps in [`docs/upgrading.md`](docs/upgrading.md#migration-to-dbmate-2020-and-later).
