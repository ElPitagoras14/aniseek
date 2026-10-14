> Sesiones: los grupos 1–6 y 9 son de **backend**, el 7 es de **frontend**, el 8 de **ambos** y el 10 de **worker**. La Fase 2 (grupos 9 y 10) se ejecuta solo cuando ani-scrapy 0.8.0 esté publicado en PyPI.

## 1. [backend] Módulo de catálogo y mapeadores puros

- [x] 1.1 Crear `backend/src/packages/animes/catalog.py` con `PROVIDER_BASE_URL`, `media_url(anime_id)` y `episode_url(anime_id, n)`. Verificar con un test unitario que `episode_url("x", 3) == "https://animeav1.com/media/x/3"`.
- [x] 1.2 Cambiar `_episode_values(episodes, anime_id)` para que use `episode_url` y no reciba `base_url`. Verificar con un test unitario sin red ni BD.
- [x] 1.3 Crear `_relation_rows(anime_info)`, que devuelva `(placeholders, relations)` y omita con `logger.warning` los tipos que no estén en `related_types_id`. Verificar con un test unitario de un tipo conocido y uno desconocido.

## 2. [backend] Repositorio en lote

- [x] 2.1 Agregar `repository.upsert_relations(conn, placeholders, relations)` con dos `execute_many` (SQL actual de `insert_dummy_anime` e `insert_anime_relation`, `ON CONFLICT DO NOTHING`). Verificar con un test de BD que insertar dos veces no duplica filas.
- [x] 2.2 Eliminar `insert_dummy_anime`, `insert_anime_relation`, `insert_new_episodes`, `get_max_episode_number` y `update_anime_fields` cuando queden sin callers. Verificar con `grep` que no queden referencias.

## 3. [backend] Flujo único de sync

- [x] 3.1 Implementar `_scrape_snapshot(anime_id)`: una sola llamada a `scrape_anime_info(include_episodes=True)`, sin conexión abierta. Verificar con un test que el scraper se invoca exactamente una vez.
- [x] 3.2 Implementar `_persist_snapshot(conn, info, now)`: `upsert_scraped_anime`, `insert_genres`, `upsert_relations` e `insert_episodes`. Verificar con un test de BD que un refresh con episodios nuevos los agrega sin duplicar los existentes.
- [x] 3.3 Implementar `sync_anime(anime_id)` = scrape → `engine.begin()` → persist, y reemplazar `add_new_anime` y `update_anime_info` por él. Verificar que el test de orden scrape-antes-de-transacción pasa.
- [x] 3.4 Eliminar `scrape_new_episodes` de `scraper.py`, junto con `asyncio.sleep(1.5)` y los imports sin uso. Verificar con `grep` que no queden referencias.
- [x] 3.5 Reescribir `tests/test_animes_atomicity.py` y `tests/test_animes_scrape_persist_order.py` sobre el flujo nuevo. Verificar que un fallo a mitad de `_persist_snapshot` no deja escrituras confirmadas.

## 4. [backend] Regla "scrapeado" y endpoints

- [x] 4.1 Agregar `is_scraped(row)` y `ensure_anime_scraped(anime_id)`, y usarlos en `get_anime_controller` y `save_anime_controller`. Verificar con un test que un placeholder dispara el sync.
- [x] 4.2 Usar `is_scraped` en `valid_anime_for_update` y corregir su mensaje de 404 a `GET /animes/{anime_id}`. Verificar con un test que un placeholder da 404 con ese mensaje y que el cooldown sigue dando 429.
- [x] 4.3 Quitar la construcción de `base_url` de los tres controladores. Verificar con `grep "animeav1.com"` que solo aparece en `catalog.py`.

## 5. [backend] Single-flight

- [x] 5.1 Envolver `sync_anime` con `_sync_inflight: dict[str, asyncio.Task]`, `add_done_callback` para limpiar la entrada y `asyncio.shield` en los que esperan. Agregar un comentario con el supuesto de un solo proceso.
- [x] 5.2 Escribir tests: dos llamadas concurrentes del mismo `anime_id` invocan el scraper una sola vez y reciben el mismo resultado; tras un fallo, la siguiente llamada vuelve a scrapear.

## 6. [backend] Contrato de respuesta

- [x] 6.1 Agregar `url: str` a `responses.EpisodeInfo` y propagarlo desde `get_anime_info_to_dict` (`ep["url"]`, confirmando que `get_anime_with_relations` lo incluye). Verificar con un test que el detalle trae `episodes[].url`.
- [x] 6.2 Eliminar `Anime.platform` y `platform="AnimeAV1"` de `cast_anime_info`. Verificar con un test que la respuesta no contiene `platform`.
- [x] 6.3 Correr la suite completa del backend y confirmar que pasa.

## 7. [frontend] Consumo del contrato y limpieza

- [x] 7.1 En `features/anime/types.ts`, agregar `EpisodeInfo.url: string` y quitar `AnimeDetail.platform`. Verificar que `tsc` compila.
- [x] 7.2 Eliminar `features/anime/lib/build-episode-url.ts`. Hacer que `EpisodesTable` use `ep.url` y quitar la prop `platform` de `EpisodesTable`, `EpisodesTab` y `routes/_app/anime.$slug.tsx`. Verificar con `tsc` y lint, y en la app que el botón Play abre la URL del episodio.
- [x] 7.3 Alinear `translateRelatedType` (`info-tab.tsx`) con los valores que emite la API (`prequel`, `sequel`, `alternative`, `spin_off`, de la tabla `related_types`), con el valor original capitalizado como fallback. Verificar visualmente en un anime con relaciones.
- [x] 7.4 Quitar AnimeFLV de `LANDING_SOURCES` y del texto sobre los mirrors en `features/landing/data.ts`. Verificar con `grep -i animeflv frontend/src` que no quedan menciones.
- [x] 7.5 Correr el build y el lint del frontend y confirmar que pasan.

## 8. [ambos] Cierre de la Fase 1

- [x] 8.1 Bumpear `VERSION` a `2.1.0`. Verificar con `cat VERSION`.
- [x] 8.2 Hacer una prueba integrada local (compose dev): abrir el detalle de un anime nuevo, refrescarlo pasado el cooldown, pulsar Play en un episodio y guardarlo. Confirmar que todo funciona sin errores en la consola ni en los logs. _(Validado con Chrome sobre kaijuu-8-gou-2nd-season. El refresh exitoso pasado el cooldown queda cubierto por los tests del backend; en vivo se comprobó el 429.)_
- [x] 8.3 Correr `openspec validate unify-anime-sync` y confirmar que pasa.

## 9. [backend] Fase 2: ani-scrapy 0.8.0 (bloqueada hasta su release)

- [x] 9.1 Subir ani-scrapy a `>=0.8.0` en `backend/pyproject.toml` y correr `uv lock`. Verificar que `uv.lock` resuelve 0.8.x y que la imagen Docker del backend se construye.
- [x] 9.2 En `scraper.py`, traducir `ScraperNotFoundError` → `NotFoundError`, `ScraperBlockedError` → `TooManyRequestsError` y el resto de `ScraperError` → `ExternalServiceError`, sin asumir que `status_code` es entero. Verificar con tests que mockean cada excepción y comprueban 404, 429 y 502.
- [x] 9.3 Escribir un test donde el scraper lanza `ScraperParseError`: la respuesta es 502 y el anime no queda con `last_scraped_at`.
- [x] 9.4 Si la Fase 2 sale en un PR aparte, bumpear `VERSION` (patch) en ese PR. Correr la suite del backend y `openspec validate unify-anime-sync`. _(No aplica: la Fase 2 sale en el mismo PR que la Fase 1.)_

## 10. [worker] Fase 2: ani-scrapy 0.8.0 en el worker (bloqueada hasta su release)

- [x] 10.1 Subir ani-scrapy a `>=0.8.0` en `worker/pyproject.toml` y correr `uv lock`. Verificar que `uv.lock` resuelve la misma versión que el backend y que la imagen Docker del worker se construye.
- [x] 10.2 Confirmar que `worker/src/tasks/download.py` no usa nada de la API que cambió en 0.7.0 ni en 0.8.0 (enums renombrados, `EpisodeInfo.number`, tipos de excepción). Verificar con `grep` sobre `worker/src`.
- [x] 10.3 Hacer una prueba de humo en compose dev: descargar un episodio por AnimeAV1/PDrain y forzar la caída a JKAnime con un episodio que no exista en AV1. Confirmar en los logs del worker que la cadena de fallback y la finalización del job funcionan. _(Fallback AV1 → JKAnime validado con ScraperNotFoundError real. La rama AV1/PDrain no se puede ejercitar: AnimeAV1 ya no ofrece PDrain.)_
