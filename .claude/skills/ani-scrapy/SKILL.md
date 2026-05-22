---
name: ani-scrapy
description: "Use when writing Python code that scrapes anime sites with the ani-scrapy library. Triggers when the user mentions AnimeFLV, JKAnime, AnimeAV1, anime search/scraping, downloading anime episodes, getting download links from servers like Streamwish, YourUpload, Mediafire, Pixeldrain or UPNShare, using AnimeFLVScraper / JKAnimeScraper / AnimeAV1Scraper / AsyncBrowser, or imports from ani_scrapy. Always use this skill whenever ani-scrapy is imported, mentioned, or whenever the user asks to automate anime episode info retrieval, get new episodes, or resolve final download URLs from a Spanish anime site."
---

# ani-scrapy

A Python **async-first** library for scraping anime sites (AnimeFLV, JKAnime, AnimeAV1) with a unified API across providers. Some operations are HTTP-only; others need a Playwright-controlled browser. The library handles browser lifecycle for you — your job is to pick the right pattern and close resources.

## Installation

```bash
pip install ani-scrapy
playwright install chromium   # one-time, required for browser-backed methods
```

Python >= 3.10.14.

## Key Imports

```python
from ani_scrapy import (
    AnimeFLVScraper, JKAnimeScraper, AnimeAV1Scraper,
    AsyncBrowser,
    enable_logging,
)
from ani_scrapy import (
    AnimeInfo, EpisodeInfo, EpisodeDownloadInfo, DownloadLinkInfo,
    SearchAnimeInfo, PagedSearchAnimeInfo, RelatedInfo,
    AnimeType, RelatedType,
)
from ani_scrapy import (
    ScraperError, ScraperBlockedError, ScraperParseError, ScraperTimeoutError,
)
```

Everything is exported from the top-level `ani_scrapy` package — prefer those imports over reaching into submodules. The one exception is the per-provider `SUPPORTED_SERVERS` constant, which lives under each provider:

```python
from ani_scrapy.providers.animeflv.constants import SUPPORTED_SERVERS as ANIMEFLV_SUPPORTED_SERVERS
from ani_scrapy.providers.jkanime.constants  import SUPPORTED_SERVERS as JKANIME_SUPPORTED_SERVERS
from ani_scrapy.providers.animeav1.constants import SUPPORTED_SERVERS as ANIMEAV1_SUPPORTED_SERVERS
```

Use these to filter `download_links` down to servers whose final URL can actually be resolved by `get_file_download_link()`.

## Core Pattern — async context manager

All scrapers are async context managers. Use `async with` whenever possible — it guarantees the HTTP session, Playwright browser, and Playwright process are closed cleanly.

```python
import asyncio
from ani_scrapy import AnimeFLVScraper

async def main():
    async with AnimeFLVScraper() as scraper:
        results = await scraper.search_anime("naruto")
        for anime in results.animes[:5]:
            print(anime.id, anime.title, anime.type.value)

asyncio.run(main())
```

`async with` is the default — only reach for manual `start_browser()` / `stop_browser()` / `aclose()` when you genuinely need lifecycle control outside an `async with` block (e.g., long-lived service that holds a browser between requests).

## Public API (identical across all 3 scrapers)

```python
await scraper.search_anime(query: str, page: int = 1) -> PagedSearchAnimeInfo
await scraper.get_anime_info(anime_id: str, include_episodes: bool = True) -> AnimeInfo
await scraper.get_new_episodes(anime_id: str, last_episode_number: int) -> list[EpisodeInfo]
await scraper.get_table_download_links(anime_id: str, episode_number: int) -> EpisodeDownloadInfo
await scraper.get_iframe_download_links(anime_id: str, episode_number: int) -> EpisodeDownloadInfo
await scraper.get_file_download_link(download_info: DownloadLinkInfo) -> str | None
```

`query` must be at least 3 characters. `page`, `episode_number`, and `last_episode_number` must be `>= 0` (page `>= 1`). Invalid arguments raise `ValueError` / `TypeError`.

## Which methods need a browser?

This matters because **opening a browser is the most expensive thing in this library**. If you can stay HTTP-only, do — it's 10–100× faster (see benchmark in the README). Skipping the browser also means no Playwright dependency at runtime for that call.

| Method                       | AnimeFLV   | JKAnime    | AnimeAV1                          |
| ---------------------------- | ---------- | ---------- | --------------------------------- |
| `search_anime`               | HTTP       | HTTP       | HTTP                              |
| `get_anime_info`             | HTTP       | **Browser**| HTTP                              |
| `get_new_episodes`           | HTTP       | **Browser**| HTTP                              |
| `get_table_download_links`   | HTTP       | **Browser**| HTTP                              |
| `get_iframe_download_links`  | **Browser**| **Browser**| HTTP                              |
| `get_file_download_link`     | **Browser**| **Browser**| Browser only for UPNShare server  |

You don't toggle this manually — the scraper opens the browser on demand and reuses it within the same `async with` block. The point of the table is: if your script only calls HTTP-only methods, `playwright install chromium` is not strictly required at runtime, and the script will be much faster.

## Supported download servers per provider

`get_file_download_link()` only resolves servers the provider knows how to handle. If the link's `server` isn't in this list, resolving will return `None`. Filter before calling.

| Server      | AnimeFLV | JKAnime | AnimeAV1 |
| ----------- | -------- | ------- | -------- |
| Streamwish  | yes      | yes     | -        |
| YourUpload  | yes      | -       | -        |
| Mediafire   | -        | yes     | -        |
| Pixeldrain  | -        | -       | yes      |
| UPNShare    | -        | -       | yes      |

```python
from ani_scrapy.providers.animeflv.constants import SUPPORTED_SERVERS

valid = [l for l in links.download_links if l.server in SUPPORTED_SERVERS]
for link in valid:
    final = await scraper.get_file_download_link(link)
```

## Browser configuration — custom executable (Brave recommended)

Sites with aggressive ads (especially AnimeFLV/JKAnime) sometimes fail or hit captchas with default Chromium. Pointing at a Brave install gives you its native ad-blocker and noticeably better success rates:

```python
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

async with AnimeFLVScraper(headless=True, executable_path=BRAVE_PATH) as scraper:
    info = await scraper.get_anime_info("gachiakuta")
```

Both `headless` and `executable_path` are forwarded to the underlying Playwright launch. Any Chromium-based browser works (Chrome, Edge, Chromium, Brave) — the path must point to the executable, not the install folder.

## Three browser lifecycle patterns

The right pattern depends on how long you need the browser alive and whether you want to share it across scrapers.

### 1. Automatic (default) — recommended

The browser is created lazily on the first call that needs it, and closed when the `async with` exits. Multiple calls within the same block reuse the same browser. This is what you want 90% of the time.

```python
async with JKAnimeScraper(executable_path=BRAVE_PATH) as scraper:
    info  = await scraper.get_anime_info("gachiakuta", include_episodes=True)
    links = await scraper.get_table_download_links("gachiakuta", episode_number=1)
    # one browser instance used for both calls; closed on exit
```

### 2. Manual `start_browser()` / `stop_browser()`

For code that can't use `async with` (e.g., a long-lived service, a framework where the lifecycle is managed elsewhere). You must call `aclose()` to free HTTP session + Playwright resources.

```python
scraper = JKAnimeScraper()
await scraper.start_browser()
try:
    info = await scraper.get_anime_info("gachiakuta")
finally:
    await scraper.stop_browser()
    await scraper.aclose()
```

### 3. Inject an external `AsyncBrowser`

Share one browser across **several scrapers** (different providers, same session). The browser's lifecycle is controlled by the outer `async with` — the scrapers won't close it.

```python
from ani_scrapy import AsyncBrowser, JKAnimeScraper, AnimeAV1Scraper

async with AsyncBrowser(headless=True, executable_path=BRAVE_PATH) as browser:
    async with JKAnimeScraper(external_browser=browser) as jk, \
               AnimeAV1Scraper(external_browser=browser) as av1:
        jk_info  = await jk.get_anime_info("gachiakuta")
        av1_info = await av1.get_anime_info("sousou-no-frieren-2nd-season")
```

## Concurrency

The library is built for concurrent use. Reuse one scraper instance across tasks — don't spin up a fresh scraper per anime, that defeats connection pooling and re-launches the browser each time.

```python
async with AnimeFLVScraper() as scraper:
    results = await asyncio.gather(
        *(scraper.get_anime_info(aid) for aid in anime_ids),
        return_exceptions=True,  # so one failure doesn't sink the batch
    )
```

`return_exceptions=True` is important here — scraping is inherently flaky (timeouts, blocks, parse errors). You want partial success, not an all-or-nothing batch.

## Logging

The library uses **Loguru** and is **silent by default** (no handler installed). Turn it on explicitly when you need to debug:

```python
from ani_scrapy import enable_logging

enable_logging(level="DEBUG")             # to stdout
enable_logging(level="INFO", sink="ani_scrapy.log")  # to file
enable_logging(level="DEBUG", sink=None)  # explicit stdout
```

Do this once at startup, before any scraper call. Calling it inside a tight loop is wasted work.

## Schemas (return types)

All return types are plain `@dataclass`es. Useful fields:

```python
SearchAnimeInfo:   id, title, type: AnimeType, poster
PagedSearchAnimeInfo: page, total_pages, animes: list[SearchAnimeInfo]
                   # total_pages == 1 means the provider doesn't expose
                   # pagination (JKAnime, AnimeFLV). Only AnimeAV1 paginates.

AnimeInfo:         id, title, type, poster, description, is_finished,
                   genres: list[str], related_info: list[RelatedInfo],
                   next_episode_date: datetime | None,
                   episodes: list[EpisodeInfo]

EpisodeInfo:       episode_number, anime_id, image_preview: str | None
EpisodeDownloadInfo: episode_number, download_links: list[DownloadLinkInfo]
DownloadLinkInfo:  server: str, url: str | None
RelatedInfo:       id, title, type: RelatedType
AnimeType:         TV | MOVIE | OVA | SPECIAL
RelatedType:       PREQUEL | SEQUEL | PARALLEL_HISTORY | MAIN_HISTORY
```

`include_episodes=False` on `get_anime_info` skips the per-episode listing — useful when you only need metadata. On JKAnime this also avoids opening the browser entirely (the metadata page is HTTP, the episode list is JS-rendered).

## Error handling

Hierarchy: `ScraperError` is the base; everything else inherits from it. Catch the specific ones if you have a sensible recovery, otherwise catch `ScraperError`.

```python
from ani_scrapy import (
    ScraperError, ScraperTimeoutError, ScraperParseError, ScraperBlockedError,
)

try:
    info = await scraper.get_anime_info(anime_id)
except ScraperTimeoutError:
    # transient — retry with backoff
    ...
except ScraperBlockedError:
    # bot detection — switch to Brave, slow down, or back off
    ...
except ScraperParseError:
    # site HTML changed — not retryable, file a bug
    ...
except ScraperError as e:
    # everything else from the library
    ...
```

`ValueError`/`TypeError` are raised for bad arguments (query too short, negative episode number, wrong type) — those are programmer errors, not retryable.

### Retry guidance

`ScraperTimeoutError` and `ScraperBlockedError` are transient; `ScraperParseError` is not (the site changed; fix the parser). Use exponential backoff for the transient ones — don't hammer a site that just blocked you.

```python
import asyncio
import functools
from ani_scrapy import ScraperTimeoutError, ScraperBlockedError

def with_retry(max_retries=3, base_delay=2):
    def deco(fn):
        @functools.wraps(fn)
        async def wrapper(*a, **kw):
            for attempt in range(max_retries):
                try:
                    return await fn(*a, **kw)
                except (ScraperTimeoutError, ScraperBlockedError):
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(base_delay * (2 ** attempt))
        return wrapper
    return deco
```

## Windows: harmless ProactorEventLoop warnings

On Windows, you may see `Exception ignored in: _ProactorBasePipeTransport.__del__` / `ValueError: I/O operation on closed pipe` on exit. These are **cosmetic only** — the script ran correctly and resources were closed. They come from Python's ProactorEventLoop racing Playwright's subprocess teardown.

Workaround (suppresses the noise without changing behavior):

```python
import asyncio
asyncio.get_event_loop().run_until_complete(main())
```

Don't refactor anything else around these warnings; they're not bugs in your code.

## Diagnostics CLI

The package ships a `doctor` command — useful when something's not working:

```bash
ani-scrapy doctor                     # human-readable
ani-scrapy doctor --output json       # for CI
ani-scrapy doctor --timeout 10        # slower networks
```

It checks Python version, Playwright + Chromium install, Brave presence, and site reachability for all three providers. Exit codes: `0` ok, `1` warnings, `2` errors.

## End-to-end: search → info → download URL

The full pipeline, showing one scraper, one browser, many operations:

```python
import asyncio
from ani_scrapy import AnimeFLVScraper
from ani_scrapy.providers.animeflv.constants import SUPPORTED_SERVERS

async def fetch_download_url(query: str, episode: int) -> str | None:
    async with AnimeFLVScraper() as scraper:
        results = await scraper.search_anime(query)
        if not results.animes:
            return None

        anime = results.animes[0]
        info  = await scraper.get_anime_info(anime.id, include_episodes=False)
        print(f"Found: {info.title} ({info.type.value})")

        links = await scraper.get_iframe_download_links(anime.id, episode)
        for link in links.download_links:
            if link.server in SUPPORTED_SERVERS:
                final = await scraper.get_file_download_link(link)
                if final:
                    return final
        return None

print(asyncio.run(fetch_download_url("gachiakuta", episode=24)))
```

## Common pitfalls

- **Opening a new scraper per anime in a loop.** Re-launches the browser every iteration. Open one `async with`, reuse the scraper across calls and across `asyncio.gather`.
- **Forgetting to filter by `SUPPORTED_SERVERS`.** `get_file_download_link()` returns `None` for unsupported servers — looks like a bug, isn't one. Filter first.
- **Calling `get_anime_info` with `include_episodes=True` on JKAnime when you only need metadata.** It opens the browser unnecessarily. Pass `include_episodes=False`.
- **Catching `Exception` broadly.** Mask retryable errors. Catch `ScraperTimeoutError` / `ScraperBlockedError` specifically and only fall back to `ScraperError` for the catch-all.
- **Assuming pagination.** Only AnimeAV1 returns real `total_pages`. For AnimeFLV/JKAnime, you'll always see `total_pages == 1`.
- **Running without `playwright install chromium`** the first time — only matters for browser-backed methods, but the failure is opaque. Run `ani-scrapy doctor` if something seems off.
