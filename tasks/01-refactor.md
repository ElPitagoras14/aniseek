# Refactor endpoints

Carpeta de contexto @backend/src/packages

Se va a refactorizar los endpoints del package `animes` y sus respectivos servicios de acuerdo a la siguiente distribución:

## Endpoints por Package

### `animes`

| Método | Path | Descripción |
|--------|------|-------------|
| `GET` | `/animes/search` | Buscar animes (scraping) |
| `GET` | `/animes/in-emission` | Animes actualmente en emisión |
| `GET` | `/animes/saved` | Animes guardados del usuario actual |
| `GET` | `/animes/{id}` | Detalle de un anime |
| `PUT` | `/animes/{id}` | Forzar actualización de info (cooldown 5 min) |
| `PUT` | `/animes/{id}/save` | Guardar anime en la lista del usuario |
| `PUT` | `/animes/{id}/unsave` | Quitar anime de la lista del usuario |


### `episodes`

| Método | Path | Descripción |
|--------|------|-------------|
| `GET` | `/episodes/downloads` | Lista de episodios descargados |
| `GET` | `/episodes/downloads/last` | Últimas descargas recientes |
| `GET` | `/episodes/downloads/animes` | Animes con descargas |
| `GET` | `/episodes/storage` | Info de almacenamiento por anime |
| `DELETE` | `/episodes/storage/{anime_id}` | Eliminar todos los episodios de un anime |
| `GET` | `/episodes/{id}/file` | Obtener el archivo descargado |
| `POST` | `/episodes/{anime_id}/{ep_number}/download` | Iniciar descarga de un episodio |
| `DELETE` | `/episodes/{anime_id}/{ep_number}/download` | Eliminar descarga de un episodio |
| `POST` | `/episodes/{anime_id}/download/bulk` | Descarga masiva de episodios |
| `GET` | `/episodes/stream/status` | SSE — estado de jobs en progreso |


## Restricciones

- Solo haz el refactor moviendo los endpoints, no hagas refactors internos de los endpoints o de los servicios.
- Agrega al final de este documento un resumen de los resultados obtenidos.

---

## Resumen de resultados

**Fecha de ejecución:** 2026-05-20

### Archivos creados

| Archivo | Contenido |
|---------|-----------|
| `backend/src/packages/episodes/__init__.py` | Export de `episodes_router` |
| `backend/src/packages/episodes/config.py` | `EpisodesSettings` (REDIS_URL, ANIMES_FOLDER) |
| `backend/src/packages/episodes/responses.py` | 13 modelos de descarga y almacenamiento |
| `backend/src/packages/episodes/utils.py` | 9 funciones caster de descarga y almacenamiento |
| `backend/src/packages/episodes/dependencies.py` | 6 validadores de episodio + constante ANIMES_FOLDER |
| `backend/src/packages/episodes/service.py` | 8 controllers + helper `is_folder_empty` |
| `backend/src/packages/episodes/router.py` | 10 endpoints con paths nuevos |

### Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `backend/src/packages/animes/router.py` | Eliminados 10 endpoints; 7 paths renombrados; imports saneados |
| `backend/src/packages/animes/service.py` | Eliminados 8 controllers + `is_folder_empty`; imports saneados |
| `backend/src/packages/animes/dependencies.py` | Eliminados 6 validadores de episodio + ANIMES_FOLDER; imports saneados |
| `backend/src/packages/animes/responses.py` | Eliminados 13 modelos de descarga/almacenamiento |
| `backend/src/packages/animes/utils.py` | Eliminados 9 casters de descarga/almacenamiento |
| `backend/src/routes.py` | Agregado `episodes_router` con prefix `/episodes` |

### Conteo de endpoints

| Package | Antes | Después |
|---------|-------|---------|
| `animes` | 17 | 7 |
| `episodes` | 0 | 10 |
| **Total** | **17** | **17** |

### Tabla de rutas antiguas → nuevas

| Método | Ruta antigua (`/animes/...`) | Ruta nueva |
|--------|------------------------------|------------|
| `GET` | `/animes/info/{anime_id}` | `/animes/{anime_id}` |
| `PUT` | `/animes/info/{anime_id}` | `/animes/{anime_id}` |
| `GET` | `/animes/search` | `/animes/search` _(sin cambio)_ |
| `GET` | `/animes/saved` | `/animes/saved` _(sin cambio)_ |
| `GET` | `/animes/in-emission` | `/animes/in-emission` _(sin cambio)_ |
| `PUT` | `/animes/save/{anime_id}` | `/animes/{anime_id}/save` |
| `PUT` | `/animes/unsave/{anime_id}` | `/animes/{anime_id}/unsave` |
| `GET` | `/animes/download` | `/episodes/downloads` |
| `GET` | `/animes/download/last` | `/episodes/downloads/last` |
| `GET` | `/animes/download/anime` | `/episodes/downloads/animes` |
| `GET` | `/animes/storage` | `/episodes/storage` |
| `DELETE` | `/animes/storage/{anime_id}` | `/episodes/storage/{anime_id}` |
| `GET` | `/animes/download/episode/{episode_id}` | `/episodes/{episode_id}/file` |
| `POST` | `/animes/download/single/{anime_id}/{episode_number}` | `/episodes/{anime_id}/{episode_number}/download` |
| `DELETE` | `/animes/download/single/{anime_id}/{episode_number}` | `/episodes/{anime_id}/{episode_number}/download` |
| `POST` | `/animes/download/bulk/{anime_id}` | `/episodes/{anime_id}/download/bulk` |
| `GET` | `/animes/stream/download` | `/episodes/stream/status` |

### Breaking changes / follow-up pendiente

El frontend y la colección Bruno consumen las rutas antiguas y se romperán tras este refactor. Deben actualizarse antes de hacer deploy:

- **Frontend** (`frontend/src/`): 11 archivos con referencias a rutas viejas.
- **Bruno** (`requests/collections/Anime/`): 17 archivos `.bru` con paths antiguos.