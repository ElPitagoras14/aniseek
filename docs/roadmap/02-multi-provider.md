# Phase 2: Multi-provider scraping

**Status:** not started. **Depends on:** nothing (Phase 0 and 1 are independent). **Blocks:** Phases 3 and 4.

## Goal

Stop depending on a single catalog source. AnimeAV1 stays the primary provider; JKAnime becomes a slower fallback.

## Current state (verified 2026-10-16)

- The backend scrapes only through `AnimeAV1Scraper` (`backend/src/packages/animes/scraper.py`), and `_normalize_anime_id` assumes AnimeAV1 slugs/URLs.
- `ani-scrapy==0.8.1` is pinned in `backend/pyproject.toml` and `worker/pyproject.toml` (latest on PyPI, published 2026-10-14). The author of `ani-scrapy` is the same as Ani Seek's, so a missing provider or a bug (for example upstream issue #25) can be contributed upstream.

## Provider facts (from PyPI, the upstream README, releases and issues)

| | AnimeFLV | JKAnime | AnimeAV1 |
|---|---|---|---|
| Status | **Deprecated**: site moved to `animeflv.or.at` with a new structure, provider no longer works, `DeprecationWarning`, to be removed | Supported | Supported, main focus of recent releases |
| `search_anime` | HTTP | HTTP | HTTP |
| `get_anime_info` | HTTP | **Browser** | HTTP |
| `get_new_episodes` | HTTP | **Browser** | HTTP |
| `get_table_download_links` | HTTP | **Browser** | HTTP |
| `get_iframe_download_links` | Browser | **Browser** | HTTP |
| `get_file_download_link` | Browser | **Browser** | Browser only for UPNShare |
| Resolvable servers | Streamwish, YourUpload | Streamwish, Mediafire | Pixeldrain, UPNShare |
| Pagination | no (`total_pages == 1`) | no | yes |

- JKAnime benchmark (README, 2026-04-12): `get_anime_info` about 31 s and `get_iframe_download_links` about 8.8 s.
- JKAnime-specific releases: only 0.6.0 (iframe download links). Open issue #25: `next_episode_date` uses the current year and can be stale, which affects the calendar.
- `ani-scrapy doctor` on the maintainer's machine (2026-10-16): Playwright, Chromium and Brave found; jkanime.net and animeav1.com reachable (HTTP 200). This only checks connectivity, not whether the parser works against today's HTML. A real scrape test was not run.
- Not verified: whether the worker Docker image ships Playwright and a browser.

## Design decisions

- **Provider interface with declared capabilities:** whether it needs a browser, which download servers it resolves, whether it paginates. The worker adjusts timeouts and concurrency per provider.
- **JKAnime as fallback, not a peer:** long timeouts, low concurrency, never used for bulk periodic checks.
- **Schema:** a `provider` field per anime and per episode, and provider-namespaced ids (`jkanime:slug`).
- **Configuration:** enabled providers listed in `.env`, so one can be switched off without a code change.
- **Health:** a healthcheck per provider, visible in the UI. This is a requirement here, not an extra.
- **AnimeFLV is not implemented** while it stays deprecated; assume any provider can be deprecated.
- Server sets differ between providers, so a fallback does not yield the same download servers.

## Tasks

1. Verify the worker image has Playwright and a browser; document it in `docs/development.md` and `docs/deployment.md`.
2. Run a real scrape test of JKAnime (`get_anime_info`, `get_iframe_download_links`) and record timings.
3. Define the provider interface and refactor `scraper.py` and the worker download path behind it.
4. Add `provider` columns (migration) and namespaced ids; keep the MCP contract stable.
5. Provider selection and fallback policy; per-provider health.
6. Tests with a fake provider.
