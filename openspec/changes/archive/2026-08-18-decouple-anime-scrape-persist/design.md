## Context

`update_anime_info` (`backend/src/packages/animes/service.py:106-153`) hoy hace, dentro de un único `async with engine.begin() as conn:`:

1. `update_anime_fields` (escritura)
2. `insert_dummy_anime` / `insert_anime_relation` por cada relacionado (escritura)
3. `await asyncio.sleep(1.5)` (pausa deliberada por rate limit del sitio scrapeado, sin tocar la base)
4. `get_max_episode_number` (lectura)
5. `scrape_new_episodes` (HTTP externo hacia AnimeAV1)
6. `insert_new_episodes` (escritura)

Los pasos 3-5 no usan la conexión de Postgres para nada esencial —la lectura del paso 4 podría hacerse fuera de la transacción de escritura, ya que no depende de las escrituras 1-2 (tocan `animes`/`anime_relations`, no `episodes`)— pero mantienen la transacción abierta mientras dura una espera fija de 1.5s más una petición HTTP externa no determinística. Bajo carga concurrente esto retiene conexiones del pool más tiempo del necesario.

`add_new_anime` (línea 57-103) no tiene este problema: scrapea (`scrape_anime_info`, línea 59) antes de abrir `engine.begin()` (línea 67). Sirve como referencia del orden correcto.

El capability `database-access` ya exige atomicidad para operaciones de varias escrituras (`openspec/specs/database-access/spec.md`, requirement "Una operación de varias escrituras es atómica"). Ese requirement se preserva; este cambio agrega uno nuevo sobre el alcance de la conexión frente a I/O externo.

## Goals / Non-Goals

**Goals:**
- Que ninguna transacción de escritura en `update_anime_info` permanezca abierta durante scraping HTTP o esperas artificiales.
- Preservar la atomicidad actual: todas las escrituras de `update_anime_info` siguen confirmándose juntas o ninguna.
- Extraer el mapeo `AnimeInfo` (scraper) → `dict` de columnas a funciones puras, testeables sin mockear red ni base de datos.

**Non-Goals:**
- Tocar `add_new_anime`: ya scrapea antes de abrir la transacción; no tiene el problema de retención de conexión. Fuera de alcance según lo acordado con el usuario.
- Modificar `scraper.py` o `repository.py`: el cambio es de orquestación en `service.py`, no de las funciones de scraping ni de acceso a datos en sí.
- Cambiar la semántica de reintentos, rate-limiting o el propósito del `sleep(1.5)` frente al sitio scrapeado — solo se reubica.
- Cambiar la API pública (`update_anime_controller`) ni el esquema de base de datos.

## Decisions

### 1. Patrón "recolectar todo, luego commitear todo" en lugar de partir en dos transacciones

Se reordena `update_anime_info` en dos fases secuenciales:

- **Fase de recolección** (sin transacción de escritura abierta): `scrape_anime_info(include_episodes=False)`, lectura de `get_max_episode_number` vía una conexión de solo lectura corta (`engine.connect()`), `await asyncio.sleep(1.5)`, y `scrape_new_episodes` con el `last_ep_number` obtenido.
- **Fase de escritura** (una única `engine.begin()`): `update_anime_fields`, `insert_dummy_anime`/`insert_anime_relation` por relacionado, `insert_new_episodes` — todo con los datos ya recolectados, sin I/O externo dentro del bloque.

**Alternativa considerada**: partir en dos transacciones de escritura (una antes del scrape de episodios, otra después). Se descarta porque rompe la atomicidad global — un fallo en la segunda transacción dejaría la primera ya confirmada, violando el requirement existente de `database-access` sobre operaciones de varias escrituras.

### 2. Lectura de `last_ep_number` fuera de la transacción de escritura

`get_max_episode_number` es una lectura de `episodes`, independiente de las escrituras sobre `animes`/`anime_relations`. Se ejecuta con `engine.connect()` (patrón ya usado en `update_anime_controller`, línea 159), no dentro de `engine.begin()`.

**Alternativa considerada**: mantenerla dentro de la transacción de escritura, tal como está hoy. Se descarta porque es exactamente la lectura que hoy fuerza a que la transacción siga abierta hasta después del segundo scrape.

### 3. Extraer mapeo puro `AnimeInfo → dict`

Se extraen funciones puras (p. ej. `_anime_fields_from_info(anime_info, current_time)` y `_episode_values(episodes, anime_id, base_url)`) a partir del código inline en `service.py:110-114` y `144-152`. No hacen I/O; son las mismas transformaciones que ya existen, solo nombradas y aisladas.

**Alternativa considerada**: dejar el mapeo inline como está. Se descarta porque impide testear la lógica de transformación sin levantar scraping o base de datos — codegraph ya señala que ni `upsert_scraped_anime` ni las funciones de `scraper.py` tienen tests que las cubran.

## Risks / Trade-offs

- **[Riesgo]** Si la transacción de escritura falla después de haber scrapeado (p. ej. la base no responde en ese momento), el resultado del scraping se descarta y hay que volver a scrapear en el próximo intento. → **Mitigación**: aceptable — no hay escritura parcial (se preserva atomicidad), y el flujo se dispara por acción del usuario o de un job que puede reintentar; es el mismo costo de "volver a intentar" que ya existe hoy si la transacción actual fallara en su paso final.
- **[Riesgo]** La latencia total de `update_anime_info` no baja (sigue siendo secuencial: red → red → DB), solo baja el tiempo que la conexión de escritura permanece abierta. → **Mitigación**: ninguna necesaria; ese es el objetivo del cambio, no una regresión.
- **[Riesgo]** Extraer funciones de mapeo puede introducir un bug sutil de transcripción si no se testean. → **Mitigación**: `tasks.md` debe incluir tests unitarios para los helpers extraídos.

## Migration Plan

Cambio de código puro, sin migración de datos ni de esquema. Se despliega como cualquier otro cambio de `service.py`. Rollback: revertir el commit: no hay estado intermedio persistido que dependa del nuevo orden.

## Open Questions

Ninguna pendiente. El propósito de `await asyncio.sleep(1.5)` está confirmado: es una pausa deliberada para respetar el rate limit del sitio scrapeado entre el primer y el segundo scrape (no está documentado en el historial de git, pero se confirmó con el autor). El rediseño lo reubica sin cambiar su posición relativa (justo antes de `scrape_new_episodes`), preservando su propósito.
