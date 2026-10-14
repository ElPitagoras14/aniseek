## Why

La composición de scraping y persistencia de animes vive en `backend/src/packages/animes/service.py` y tiene varias inconsistencias:

- Crear (`add_new_anime`) y refrescar (`update_anime_info`) son dos flujos distintos que escriben conjuntos de datos distintos. El refresh hace dos GET a la misma página de AnimeAV1, con un `sleep(1.5)` y una lectura de BD intermedia. ani-scrapy expone toda la ficha en un solo request (`include_episodes` solo cambia el parseo), así que basta con uno.
- El bucle de relaciones está duplicado y hace 2N viajes a la BD.
- La regla "el anime ya está scrapeado" se repite en tres lugares.
- La plataforma (AnimeAV1) y la URL de un episodio están fijas en el backend (×3) y además duplicadas en el frontend. `episodes.url` se escribe pero nunca se lee.
- Dos requests concurrentes sobre el mismo anime scrapean dos veces.
- Los errores de ani-scrapy llegan al cliente como un 500 genérico. Un HTML sin datos se persiste como un anime válido.

## What Changes

**Fase 1 (backend + frontend, mismo PR):**

- Unificar crear y refrescar en un solo flujo de sync: un único scrape (1 GET) y una única persistencia transaccional con el mismo conjunto de escritura (anime, relaciones, episodios, géneros) en ambos casos. Se eliminan:
  - el wrapper `scrape_new_episodes`
  - `repository.get_max_episode_number`
  - `repository.insert_new_episodes`
  - el `sleep(1.5)`
- Persistir las relaciones (anime dummy + relación) en lote desde un mapeador puro. Un tipo de relación desconocido se registra en el log y se omite, en vez de abortar la transacción.
- Centralizar la regla "está scrapeado" (`is_scraped` / `ensure_anime_scraped`) para los controladores de detalle y de guardado y para la validación del `PUT`.
- Corregir el mensaje del 404 de `PUT /animes/{id}`, que apunta a una ruta inexistente (`/animes/info/{id}`).
- Centralizar el proveedor del catálogo y la construcción de la URL del episodio en un único módulo del backend. Se quita el parámetro `base_url` de controladores y flujos.
- **BREAKING (API)**: exponer `url` en cada episodio de `GET`/`PUT /animes/{id}` y **eliminar `platform`** de la respuesta.
- Single-flight en proceso: los requests concurrentes que sincronizan el mismo anime comparten un único scrape.
- Frontend:
  - usar `episode.url` en lugar de construir la URL; borrar `build-episode-url.ts` y quitar `platform` de los tipos y componentes
  - alinear `translateRelatedType` con los valores que la API emite de verdad, que salen de la tabla `related_types`: `prequel`, `sequel`, `alternative`, `spin_off`
  - quitar AnimeFLV de la landing (`LANDING_SOURCES` y texto de mirrors)

**Fase 2 (backend + worker; depende de ani-scrapy 0.8.0):**

- Subir ani-scrapy a 0.8.0 (`uv lock`) en el backend y traducir sus excepciones en el borde del scraper:
  - `ScraperNotFoundError` → 404
  - `ScraperBlockedError` → 429
  - el resto de `ScraperError` → 502
- Subir también el worker de 0.6.2 a 0.8.0 (`uv lock`), para que ambos servicios usen la misma versión de la librería. El worker solo usa la API de descargas, que no cambia entre esas versiones, y atrapa `Exception` en cada intento de su cadena AV1 → JKAnime, así que su flujo se mantiene.

**Dependencia externa:** la Fase 2 espera el release **ani-scrapy 0.8.0**, que se gestiona como change propio en el repo de la librería. De ese release, aniseek asume:

- una jerarquía plana bajo `ScraperError` (con `status_code: int | None`) con las subclases hermanas `ScraperNotFoundError`, `ScraperBlockedError`, `ScraperHTTPError`, `ScraperTimeoutError` y `ScraperParseError`
- que el parser de AnimeAV1 lanza `ScraperParseError` cuando la página no trae datos, en vez de devolver un `AnimeInfo` vacío

La Fase 1 no depende de ese release.

## Capabilities

### New Capabilities

- `anime-catalog`: cómo el backend sincroniza un anime desde el proveedor del catálogo y lo expone. Cubre:
  - flujo único de sync y su conjunto de escritura
  - regla de "scrapeado"
  - semántica de `GET`/`PUT` (404 y cooldown)
  - deduplicación de syncs concurrentes
  - contrato de la respuesta (`url` por episodio, sin `platform`)
  - traducción de los errores del proveedor a códigos HTTP

### Modified Capabilities

(ninguna). `database-access` ya exige que el I/O externo ocurra antes de abrir la transacción. Este change lo respeta sin modificar sus requirements.

## Impact

- **Backend:** `packages/animes/service.py`, `scraper.py`, `repository.py`, `dependencies.py`, `responses.py`, `utils.py`, y un nuevo módulo de catálogo. Tests: `tests/test_animes_atomicity.py`, `tests/test_animes_scrape_persist_order.py` y tests nuevos de mapeadores y single-flight. Fase 2: `pyproject.toml` / `uv.lock` (ani-scrapy 0.8.0).
- **Frontend:** `features/anime/types.ts`, `features/anime/lib/build-episode-url.ts` (se elimina), `features/anime/components/episodes-tab.tsx`, `episodes-table.tsx`, `info-tab.tsx`, `features/landing/data.ts`.
- **API:** `GET`/`PUT /animes/{id}` agregan `episodes[].url` y eliminan `platform`. Backend y frontend deben desplegarse juntos.
- **BD:** sin migraciones. `episodes.url` ya existe y todas las filas tienen formato AnimeAV1.
- **Worker (Fase 2):** `worker/pyproject.toml` / `uv.lock` (ani-scrapy 0.6.2 → 0.8.0). No cambia el código.
- **Release:** `VERSION` 2.0.21 → 2.1.0.
- **Fuera de alcance:** refresh periódico de animes en emisión desde el worker (change futuro: requerirá lock en Redis en lugar del single-flight en proceso).
