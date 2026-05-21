# Eliminación de ORM

Carpeta de contexto @backend/src/packages

Debido a la complejidad de las queries y relaciones, se ha decidido eliminar el ORM de la capa de aplicación y usar directamente raw queries optimizados.

En cada endpoint que haya usado ORM reemplazar por una raw query usando la librería `databases`. Estas queries deben existir en un archivo `repository.py` en el package correspondiente.

Al momento de insertar en la tabla `animes`, en caso de conflicto en la lógica de agregar `dummy` animes se debe hacer nada. En caso que el conflicto se de al scrapear el anime entonces se debe actualizar los campos de la tabla `animes` de acuerdo a como se tenía la lógica.

Tienes el schema de la base de datos en @postgres/init.sql.

Agrega los resultados obtenidos a este documento.

---

## Resultados

### Archivos creados

| Package | Archivo | Descripción |
|---|---|---|
| `auth` | `repository.py` | Queries de login, registro y lookup por id/username |
| `users` | `repository.py` | CRUD de usuarios, avatars, conteos de estadísticas |
| `franchises` | `repository.py` | CRUD de franquicias, queries de animes sin franquicia |
| `animes` | `repository.py` | Upsert scrapeado/dummy, genres, relations, episodes, user_save_anime |
| `episodes` | `repository.py` | Downloads, storage, bulk operations |

### Archivos modificados

| Package | Archivo |
|---|---|
| `auth` | `service.py`, `middleware.py` |
| `users` | `service.py`, `dependencies.py` |
| `franchises` | `service.py`, `dependencies.py` |
| `animes` | `service.py`, `dependencies.py` |
| `episodes` | `service.py`, `dependencies.py` |

### Verificación de imports residuales

```
Select-String -Path backend\src\packages -Recurse -Pattern "databases\.postgres|from sqlalchemy|import sqlalchemy"
→ Sin resultados (0 archivos con imports residuales)
```

43 archivos `.py` dentro de `backend/src/packages` con sintaxis válida.

### Lógica de upsert en `animes`

Implementada en `animes/repository.py`:

- **Anime scrapeado** → `upsert_scraped_anime()`: `INSERT ... ON CONFLICT (id) DO UPDATE SET title, description, poster, type, is_finished, week_day, last_scraped_at`
- **Anime dummy** (relaciones) → `insert_dummy_anime()`: `INSERT ... ON CONFLICT (id) DO NOTHING`
- **Genres** → `insert_genres()`: `ON CONFLICT (anime_id, name) DO NOTHING`
- **Anime relations** → `insert_anime_relation()`: `ON CONFLICT (anime_id, related_anime_id, type_related_id) DO NOTHING`
- **Episodes** → `insert_episodes()`: `ON CONFLICT (anime_id, ep_number) DO NOTHING`

Los flujos multi-query (`add_new_anime`, `update_anime_info`, `create_franchise`, `download_anime_episode`, `delete_anime_storage`) envueltos en `async with db.transaction()`.

### Patrones utilizados

- Queries: SQL plano con bind params `:param` y dicts
- Acceso a DB: import directo de la instancia global `db` desde `database.client`
- Resultado de queries: `db.fetch_one()` → `dict | None`, `db.fetch_all()` → `list[dict]`, `db.fetch_val()` → scalar
- Arrays PostgreSQL: `= ANY(:ids)` con `list` (soporte nativo asyncpg)

### Commits

| Hash | Descripción |
|---|---|
| `c4f63c2` | refactor(auth): replace ORM with raw queries via databases lib |
| `2cdfed1` | refactor(users): replace ORM with raw queries via databases lib |
| `17b208e` | refactor(franchises): replace ORM with raw queries via databases lib |
| `1fe0f7e` | feat(animes): add repository with raw queries |
| `bf24351` | refactor(animes): replace ORM in service with raw queries |
| `57fd3c8` | refactor(animes): replace ORM in dependencies with raw queries |
| `450fd96` | refactor(episodes): add repository and replace ORM in dependencies |
| `713d67b` | refactor(episodes): replace ORM in service with raw queries |