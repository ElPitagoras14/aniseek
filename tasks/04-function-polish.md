# Pulir las funciones

Carpeta de contexto: @backend/src/packages

Quiero que elimines el uso de la función `create_caster` en las funciones `cast_*` de cada package y que hagas el casteo directo con el modelo de respuesta.

Los modelos de respuesta en `schemas.py` deben tener nombres representativos y significativos. Quiero que identifiques modelos que pueda mejorar su nombre

Elimine archivos de la carpeta `utils` y necesito que verifiques que no queden import huerfanos o imports no existentes

Escribe los resultados obtenidos a este documento.

## Resultados

### 1. `create_caster` eliminado

- Eliminado de: `animes/utils.py`, `episodes/utils.py`, `franchises/utils.py`, `users/utils.py`.
- Reemplazado por construcción directa (`Model(**dict)` o constructor explícito) en cada `cast_*`.
- `cast_user` y `cast_statistics` (users) se mantienen como funciones nombradas porque son consumidas por `users/service.py`.
- `cast_avatar` (singular, users) fue inlineado dentro de `cast_avatars`.

### 2. Renombres de modelos

| Antes | Después | Archivo | Motivo |
|---|---|---|---|
| `CreateInfo` | `RegisterInfo` | `auth/schemas.py` | El nombre no comunicaba "registro" |
| `CreateFranchise` | `FranchiseCreate` | `franchises/schemas.py` | Convención `<Recurso><Acción>` |
| `UserInfo` | `UserUpdateInfo` | `users/schemas.py` | Solo se usa para PATCH; el nombre era ambiguo |

Modelos auditados sin renombrar (nombres considerados representativos): `SearchAnimeResult`, `AnimeDownloadInfo`, `DownloadTask`, `DownloadTaskStatus`, `PasswordInfo`, `AnimeInfo`, `LoginInfo`.

### 3. Carpeta `utils/` eliminada

- Eliminados: `cast.py` y `__pycache__/`.
- Módulos raíz en `backend/src/`: `exceptions.py` (con `ConflictError` agregado), `responses.py`, `utils.py`, `models.py` (nuevo, contiene `CamelCaseModel`).
- 23+ imports huérfanos corregidos en los 5 paquetes (animes, auth, episodes, franchises, users).
- Verificación: `grep -rn "from utils\." backend/src` retorna 0 coincidencias.
- Smoke test: módulos cargan sin errores (DB_URL bloqueado es esperado en entorno sin base de datos).

### Mapeo de excepciones (antiguo → nuevo)

| Antiguo | Nuevo |
|---|---|
| `NotFoundException` | `NotFoundError` |
| `BadRequestException` | `BadRequestError` |
| `ConflictException` | `ConflictError` (agregado a `exceptions.py`) |
| `CustomHTTPException` | `AppError` |
| `InternalServerErrorException` | `AppError` (status 500 por defecto) |

### Archivos nuevos creados

- `backend/src/models.py` — contiene `CamelCaseModel` (recuperado del historial git)