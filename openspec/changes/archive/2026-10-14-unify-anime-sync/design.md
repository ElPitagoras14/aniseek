## Context

Ver `proposal.md` (Why). El estado actual relevante:

- `backend/src/packages/animes/service.py` cumple tres papeles: mapeadores puros (`_anime_fields_from_info`, `_episode_values`, `get_anime_info_to_dict`), flujos (`add_new_anime`, `update_anime_info`) y controladores HTTP (`*_controller`). `scraper.py` y `repository.py` no se conocen entre sí; toda la composición ocurre en `service.py`.
- ani-scrapy (`AnimeAV1Scraper`): `get_anime_info` hace 1 GET a `media/{id}`, y otro a `/horario` si el anime está en emisión y no trae fecha. `include_episodes` solo afecta al parseo. `get_new_episodes` repite el GET a la misma página y filtra en memoria.
- `insert_episodes`, `insert_genres`, `insert_dummy_anime` e `insert_anime_relation` ya usan `ON CONFLICT DO NOTHING`. `insert_new_episodes` tiene el mismo SQL que `insert_episodes`.
- El backend corre en un solo proceso: `uvicorn.run` sin `workers` y un contenedor con `container_name` fijo en `compose.yaml`.
- La spec `database-access` exige que el I/O externo ocurra antes de abrir la transacción. Este diseño la mantiene.

## Goals / Non-Goals

**Goals:**
- Un solo flujo de sync (scrape → persist) reutilizado por crear y refrescar.
- Mapeadores puros testeables sin red ni BD; repositorio en lote.
- Un único lugar para el proveedor del catálogo y la URL del episodio.
- Que la Fase 2 (errores) se pueda aplicar sin tocar los flujos, solo el borde del scraper.

**Non-Goals:**
- Mover el sync al worker o agregar un refresh periódico (change futuro).
- Soportar más de un proveedor de catálogo.
- Refrescar o reemplazar géneros y relaciones que el proveedor haya quitado. La persistencia solo agrega.
- Cambios en el código del worker. En la Fase 2 solo se actualiza su dependencia de ani-scrapy (D9).

## Decisions

### D1. Un solo flujo: `_scrape_snapshot` + `_persist_snapshot`

```
 _scrape_snapshot(anime_id) ─► AnimeInfo           (1 GET, include_episodes=True; sin conexión abierta)
 _persist_snapshot(conn, info, now)                (dentro de engine.begin())
    ├─ upsert_scraped_anime        campos + last_scraped_at
    ├─ insert_genres               ON CONFLICT DO NOTHING
    ├─ upsert_relations            lote: placeholders + relaciones
    └─ insert_episodes             lote, ON CONFLICT DO NOTHING
 sync_anime(anime_id) = scrape → begin() → persist
```

`add_new_anime` y `update_anime_info` se reemplazan por `sync_anime`, o pasan a ser alias de él durante la transición. El refresh usa `upsert_scraped_anime` en lugar de `update_anime_fields`. Así el mismo SQL sirve para ambos casos, y la precondición "existe" la garantiza la capa de entrada (D4), no el `UPDATE`.

- *Alternativa descartada:* mantener `scrape_new_episodes` con la lectura de `max(ep_number)`. Cuesta un GET extra, el sleep y una lectura que puede quedar obsoleta. El filtrado ya lo hace la BD con `ON CONFLICT`.
- *Costo aceptado:* en cada refresh se envía la lista completa de episodios a `execute_many`. Para ~1000 filas son milisegundos, frente a los 1.5 s de sleep más un GET que se eliminan.

Se eliminan:
- `scraper.scrape_new_episodes`
- `repository.get_max_episode_number`
- `repository.insert_new_episodes`
- `repository.update_anime_fields`, si queda sin callers
- `asyncio.sleep(1.5)` e `import asyncio`, si quedan sin uso

### D2. Relaciones en lote desde un mapeador puro

`_relation_rows(anime_info) -> tuple[list[dict], list[dict]]` produce las filas de placeholders y de relaciones. Resuelve el tipo con `related_types_id.get(...)`; si el tipo no existe, emite un `logger.warning` y omite la relación. `repository.upsert_relations(conn, placeholders, relations)` hace dos `execute_many` sobre el SQL actual de `insert_dummy_anime` e `insert_anime_relation`, y estas dos funciones se eliminan.

- *Alternativa descartada:* un helper que encapsule el bucle actual. Elimina la duplicación pero sigue costando 2N viajes a la BD.

### D3. Módulo de catálogo

Nuevo `backend/src/packages/animes/catalog.py` con:

```python
PROVIDER_BASE_URL = "https://animeav1.com"
def media_url(anime_id: str) -> str: ...
def episode_url(anime_id: str, episode_number: int) -> str: ...
```

`_episode_values(episodes, anime_id)` usa `episode_url` y pierde el parámetro `base_url`. Los tres controladores dejan de construir `base_url`. Por ahora `scraper.py` sigue instanciando `AnimeAV1Scraper`; el módulo concentra lo que el resto del backend necesita saber del proveedor.

### D4. Regla "scrapeado" centralizada

- `is_scraped(row: dict | None) -> bool`: la fila existe y `last_scraped_at` no es nulo.
- `ensure_anime_scraped(anime_id)`: lee con una conexión corta y, si `not is_scraped`, ejecuta `sync_anime`.
- Se usa en `get_anime_controller` y `save_anime_controller`, mientras que `valid_anime_for_update` (`dependencies.py`) usa `is_scraped`. El mensaje de su 404 pasa a `GET /animes/{anime_id}`.

### D5. Single-flight en proceso

```python
_sync_inflight: dict[str, asyncio.Task] = {}

async def sync_anime(anime_id):
    task = _sync_inflight.get(anime_id)
    if task is None:
        task = asyncio.create_task(_do_sync(anime_id))
        _sync_inflight[anime_id] = task
        task.add_done_callback(lambda _: _sync_inflight.pop(anime_id, None))
    return await asyncio.shield(task)
```

- La entrada se elimina al terminar la tarea, sea con éxito o con error. Así un error no queda memorizado.
- `asyncio.shield` evita que, si el cliente que inició la tarea se desconecta, se cancele el sync que los demás están esperando.
- El supuesto de un solo proceso queda escrito en un comentario junto a `_sync_inflight`.
- *Alternativas descartadas:*
  - lock en Redis: aporta multi-proceso, que hoy no existe, a cambio de más código y de manejar TTL
  - advisory lock de Postgres: retiene una conexión durante el scrape y contradice `database-access`
  - no hacer nada: es idempotente, pero duplica requests al proveedor y aumenta el riesgo de 429

### D6. Contrato de respuesta: `url` sí, `platform` no

- `responses.EpisodeInfo` agrega `url: str`. `get_anime_info_to_dict` lo toma de `ep["url"]`, que `get_anime_with_relations` ya selecciona como `e.url`; si no viniera en el mapeo, hay que agregarlo.
- `Anime.platform` y `platform="AnimeAV1"` en `cast_anime_info` se eliminan.
- No hace falta backfill: todas las filas de `episodes.url` tienen formato AnimeAV1.

### D7. Frontend

- `types.ts`: `EpisodeInfo.url: string`; se quita `AnimeDetail.platform`.
- Se elimina `lib/build-episode-url.ts`. En `EpisodesTable` el botón Play usa `ep.url`, y `EpisodesTab` y `EpisodesTable` pierden la prop `platform`. También hay que quitarla en quien renderiza `EpisodesTab` (`routes/_app/anime.$slug.tsx`).
- `info-tab.tsx`: `translateRelatedType` mapea los valores que emite la API, que son los nombres de `related_types` en la BD (`prequel`, `sequel`, `alternative`, `spin_off`; migración `0001`), a sus etiquetas, con el valor original capitalizado como fallback. Los valores del enum de ani-scrapy (`Prequel`, `Parallel History`…) no llegan al frontend: el backend los convierte a id con `related_types_id` (`Parallel History`→`alternative`, `Main History`→`spin_off`).
- `features/landing/data.ts`: quitar AnimeFLV de `LANDING_SOURCES` y del texto sobre los mirrors.

### D8. Fase 2: traducción de errores en el borde del scraper

Con ani-scrapy 0.8.0, `scraper.py` envuelve cada llamada al scraper:

| ani-scrapy 0.8.0 | Backend (`exceptions.py`) | HTTP |
|---|---|---|
| `ScraperNotFoundError` | `NotFoundError` | 404 |
| `ScraperBlockedError` | `TooManyRequestsError` | 429 |
| `ScraperError` (resto: HTTP, Timeout, Parse) | `ExternalServiceError` | 502 |

Como la traducción ocurre dentro de `_scrape_snapshot`, la excepción se lanza antes de abrir cualquier transacción, y una página sin datos (Parse) nunca llega a persistirse. `status_code` puede ser `None` y no debe asumirse entero.

- *Alternativa descartada:* un guard `title == ""` en el backend. Queda redundante una vez que la librería lanza `ScraperParseError`.

### D9. Fase 2: el worker sube a ani-scrapy 0.8.0

El backend y el worker deben usar la misma versión de la librería. El worker (`worker/src/tasks/download.py`) usa solo:
- `AnimeAV1Scraper` y `JKAnimeScraper` con `executable_path`
- `get_table_download_links`, `get_iframe_download_links` y `get_file_download_link`
- `info.download_links` y `link.server`

Los cambios incompatibles de 0.7.0 (renombrado de enums, `EpisodeInfo.number` → `episode_number`, tipado de listas) no tocan esa API. 0.8.0 cambia los tipos de excepción, pero el worker atrapa `except Exception` en cada intento de la cadena AV1 → JKAnime. Un `ScraperNotFoundError` en AV1 sigue pasando a JKAnime, y el reintento de Dramatiq se comporta igual. Las dependencias de la librería (Playwright incluido) no cambian, así que el `Dockerfile` del worker tampoco.

- *Alternativa descartada:* dejar el worker en 0.6.2 hasta el change de refresh periódico. Mantiene dos versiones con jerarquías de excepciones distintas en el mismo sistema.

## Risks / Trade-offs

- [Cambio de contrato de la API: se elimina `platform`] → backend y frontend en el mismo PR y release; `VERSION` pasa a 2.1.0.
- [El single-flight deja de proteger si el backend se escala a varios procesos o réplicas] → supuesto documentado en el código; la migración a un lock en Redis queda anotada para el change de refresh periódico.
- [La persistencia solo agrega: si el proveedor quita un género o una relación, se conserva] → aceptado; en la práctica no ocurre.
- [La Fase 2 depende de un release externo] → la Fase 1 es independiente. Si ani-scrapy 0.8.0 no está publicado al cerrar el PR, la Fase 2 sale en un PR propio con su propio bump de `VERSION`.
- [Subir el worker dos versiones de golpe (0.6.2 → 0.8.0) puede alterar el scraping de descargas con Playwright (cambios internos en `browser.py`, `http.py` y el scraper de JKAnime)] → prueba de humo de una descarga real por cada fuente de la cadena antes de cerrar la Fase 2.
- [Los tests existentes mockean `scrape_new_episodes` y el orden de las llamadas] → se reescriben sobre `_scrape_snapshot` y `_persist_snapshot`.

## Migration Plan

1. Rama nueva desde `main` actualizada, sin `--track`. Las sesiones `backend` y `frontend` trabajan sobre la misma rama, cada una en su directorio.
2. Fase 1: implementar backend y frontend, bumpear `VERSION` a 2.1.0, abrir PR y desplegar los dos juntos.
3. Fase 2: cuando ani-scrapy 0.8.0 esté en PyPI, actualizar la dependencia (`uv lock`) en backend y worker y la traducción de errores del backend, en el mismo PR si todavía está abierto o en uno nuevo con un bump de patch.
4. Rollback: revertir el PR. No hay migraciones de BD.
