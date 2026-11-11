# Roadmap

Planning notes for Ani Seek, agreed on 2026-10-16 and reorganized on 2026-11-11. The items below are an **unordered pool**: there are no phases and no required sequence. Each item has its own file with the context, decisions and open questions needed to pick it up in a new session. "Related" notes say which items touch each other, not which must come first.

## Pool

| Item | Deliverable | Effort | Status |
|---|---|---|---|
| [multi-provider](multi-provider.md) | Multi-provider scraping (AnimeAV1 + JKAnime fallback) | High | Not started |
| [anilist-metadata](anilist-metadata.md) | AniList metadata and cross-provider identity | Medium | Not started |
| [automation](automation.md) | Auto-download of new episodes, notifications, visible download queue | Medium | Not started |
| [franchises](franchises.md) | Full franchise support: create, update, delete, relate animes | Medium-high | Partial (create and list only) |
| [platform-and-resilience](platform-and-resilience.md) | Quotas, observability, backups, test coverage | Continuous | Not started |

## Done

- [users-and-access](users-and-access.md): roles (owner, admin, member), controlled registration.
- [mcp](mcp.md): MCP server for AI agents, enabled per instance.

## Dropped

- Built-in player and watch progress: removed from the roadmap on 2026-11-11.

## Working rules (from `CLAUDE.md`)

- Each item is implemented as one or more OpenSpec changes (`/opsx:propose`, then `/opsx:apply`).
- Apply a change only on a new branch created from an up-to-date `main`, without `--track`; publish it with `git push -u origin <branch>`.
- Bump `VERSION` (repo root, strictly greater semver) in the same PR when it deserves a release.
- Conventional commits in English, short description, no `Co-Authored-By`, and only when the user asks.
- Explore code with `codegraph_explore` before `Grep`/`Read`.

## Verified facts vs. assumptions

The item files cite file paths and line numbers as of the date written in each one (mostly 2026-10-16; `franchises` and the provider versions 2026-11-11). Line numbers drift; re-check them before editing. Anything marked "not verified" was not checked in the codebase or upstream during planning.
