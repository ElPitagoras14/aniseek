## Why

`update_anime_info` (`backend/src/packages/animes/service.py`) abre una transacción de escritura (`engine.begin()`) y, dentro de ella, hace un `asyncio.sleep(1.5)` y una segunda llamada de scraping HTTP (`scrape_new_episodes`) antes de escribir los episodios nuevos. Eso retiene una conexión de Postgres del pool durante I/O externo lento y no determinístico, lo que agota el pool bajo carga concurrente y alarga locks sin necesidad. `add_new_anime` no tiene este problema (scrapea antes de abrir la transacción), pero ambos flujos entrelazan el mapeo `AnimeInfo → dict` de columnas inline con las llamadas a `repository`, dificultando testear cada capa por separado.

## What Changes

- Reordenar `update_anime_info` para que todo el I/O externo (los dos scrapes y el `sleep` de cortesía entre ellos) ocurra **antes** de abrir la transacción de escritura. La lectura de `get_max_episode_number` pasa a hacerse con una conexión de solo lectura corta (`engine.connect()`), independiente de la transacción de escritura.
- Consolidar todas las escrituras (`update_anime_fields`, `insert_dummy_anime`, `insert_anime_relation`, `insert_new_episodes`) en una única transacción corta al final, sin I/O de red ni `sleep` dentro de su alcance.
- Extraer el mapeo `AnimeInfo` (scraper) → `dict` de columnas de `animes`/`episodes` a funciones puras, testeables sin mockear red ni base de datos.
- Sin cambios en `scraper.py` ni `repository.py`: la separación es de orquestación en `service.py`.

## Capabilities

### New Capabilities

(ninguna)

### Modified Capabilities

- `database-access`: nuevo requirement — una unidad de trabajo (transacción) no permanece abierta durante I/O externo ajeno a la base de datos (llamadas de red, esperas artificiales). El requirement existente de atomicidad de escrituras múltiples se preserva sin cambios.

## Impact

- `backend/src/packages/animes/service.py`: reescritura de `update_anime_info` (orden de operaciones) y extracción de helpers de mapeo puro.
- `openspec/specs/database-access/spec.md`: nuevo requirement sobre alcance de la conexión frente a I/O externo.
- Sin cambios de API pública, de schema de base de datos, ni de comportamiento observable para el usuario final (mismo resultado final, misma atomicidad de escritura).
