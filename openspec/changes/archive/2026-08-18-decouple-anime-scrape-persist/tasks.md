## 1. Extraer helpers de mapeo puro

- [x] 1.1 Crear `_anime_fields_from_info(anime_info, current_time)` en `service.py` que devuelva el dict de columnas de `animes` (`title`, `description`, `poster`, `type`, `is_finished`, `week_day`, `last_scraped_at`) a partir de un `AnimeInfo`, sin I/O.
- [x] 1.2 Crear `_episode_values(episodes, anime_id, base_url)` en `service.py` que devuelva la lista de dicts usada por `insert_episodes`/`insert_new_episodes`, sin I/O.
- [x] 1.3 Reemplazar el código inline equivalente en `add_new_anime` y `update_anime_info` por llamadas a estos helpers, sin cambiar el comportamiento resultante.

## 2. Reordenar `update_anime_info`

- [x] 2.1 Mover la lectura de `get_max_episode_number` fuera de la transacción de escritura, usando `engine.connect()` (conexión de solo lectura corta, mismo patrón que `update_anime_controller`).
- [x] 2.2 Mover `await asyncio.sleep(1.5)` y `scrape_new_episodes` antes de abrir la transacción de escritura, preservando su orden relativo (sleep primero, luego el scrape, para seguir respetando el rate limit del sitio).
- [x] 2.3 Consolidar `update_anime_fields`, el loop de `insert_dummy_anime`/`insert_anime_relation`, e `insert_new_episodes` dentro de una única `engine.begin()` al final, usando los datos ya recolectados en la fase previa.
- [x] 2.4 Revisar el diff final y confirmar que ninguna llamada de red ni `sleep` queda dentro del bloque `engine.begin()`.

## 3. Tests

- [x] 3.1 Actualizar `test_update_anime_info_keeps_previous_fields_on_mid_transaction_failure` (`backend/tests/test_animes_atomicity.py`) para mockear también `scrape_new_episodes` — con el nuevo orden se invoca incondicionalmente antes de la transacción, ya no queda "protegida" por la falla inyectada en `insert_dummy_anime`.
- [x] 3.2 En ese mismo test (o en un fixture compartido), mockear `asyncio.sleep` para que el test no pague la espera real de 1.5s.
- [x] 3.3 Agregar tests unitarios para `_anime_fields_from_info` y `_episode_values` que no requieran red ni base de datos.
- [x] 3.4 Agregar un test que confirme el orden de operaciones: `scrape_anime_info` y `scrape_new_episodes` se invocan antes de que se abra cualquier conexión de escritura (por ejemplo, instrumentando los mocks para registrar el orden de llamadas).
- [x] 3.5 Correr la suite de tests de `backend` y confirmar que pasan, incluyendo `test_animes_atomicity.py`.

## 4. Cierre del change

- [x] 4.1 Correr `openspec validate --changes decouple-anime-scrape-persist` y confirmar que sigue pasando tras la implementación.
