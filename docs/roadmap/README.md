# Roadmap

Planning notes for Ani Seek, agreed on 2026-10-16. Each phase has its own file with the context, decisions and open questions needed to pick it up in a new session.

| Phase | Deliverable | Effort | Depends on |
|---|---|---|---|
| [0](00-users-and-access.md) | Users and access: roles, owner, controlled registration | Medium-high | — |
| [1](01-mcp.md) | MCP server for AI agents, enabled per instance | Medium | Phase 0 |
| [2](02-multi-provider.md) | Multi-provider scraping (AnimeAV1 + JKAnime fallback) | High | — |
| [3](03-anilist-metadata.md) | AniList metadata and cross-provider identity | Medium | Phase 2 |
| [4](04-automation.md) | Auto-download, notifications, download queue | Medium | Phases 2, 3 |
| [5](05-player-and-progress.md) | Built-in player and watch progress | Medium-high | — |
| [6](06-platform-and-resilience.md) | Quotas, observability, backups, test coverage | Continuous | Cross-cutting |

## Order rationale

- **Phase 0 first:** roles exist in the database but are not enforced anywhere, and the MCP must be an instance-level feature controlled by the owner. The access model has to be settled before exposing an agent interface.
- **Phase 2 before Phase 4:** automating on a single provider multiplies the damage when it goes down. AnimeFLV is deprecated in `ani-scrapy`, so AnimeAV1 is the only fully working source today.
- **Phase 3 after Phase 2:** AniList gives an anime an identity that is independent of the provider.

## Working rules (from `CLAUDE.md`)

- Each phase is implemented as one or more OpenSpec changes (`/opsx:propose`, then `/opsx:apply`).
- Apply a change only on a new branch created from an up-to-date `main`, without `--track`; publish it with `git push -u origin <branch>`.
- Bump `VERSION` (repo root, strictly greater semver) in the same PR when it deserves a release.
- Conventional commits in English, short description, no `Co-Authored-By`, and only when the user asks.
- Explore code with `codegraph_explore` before `Grep`/`Read`.

## Verified facts vs. assumptions

The phase files cite file paths and line numbers as of 2026-10-16. Line numbers drift; re-check them before editing. Anything marked "not verified" was not checked in the codebase or upstream during planning.
