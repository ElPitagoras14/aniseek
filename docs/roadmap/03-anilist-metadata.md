# Phase 3: AniList metadata

**Status:** not started. **Depends on:** Phase 2 (provider-namespaced ids).

## Goal

Give every anime an identity that is independent of the scraping provider, and enrich the catalog with reliable metadata.

## Why

- Switching provider must not lose history or downloads; a stable common id lets the same anime map across sources.
- `related_info` currently depends on whatever the scraper returns. AniList relations enable automatic franchises (franchises are created manually today via `POST /franchises`).
- JKAnime's `next_episode_date` can be stale (upstream issue #25); AniList airing schedules are a better source for the calendar.

## Scope

- Link each anime to an AniList id and store it next to the provider id.
- Enriched data: scores, genres, seasons, relations, trailers.
- Automatic franchise grouping from relations.
- Import a user's list from AniList or MAL.
- Correct calendar data from AniList airing schedules.
- Recommendations: later, and an agent can reason over history through the MCP.

## Open questions (not decided)

- Matching strategy between provider results and AniList entries (title matching, manual confirmation, both).
- Caching and rate limits of the AniList API.
- Whether MAL is supported in addition to AniList.
- What happens to animes with no match.
