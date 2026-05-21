# Pulir los endpoints y el código

Carpeta de contexto @backend/src/packages

En los endpoints el resultado de llamar a la función del controller debe ser una variable con nombre `payload`
En el decorador del endpoint eliminar las variables `summary`, `description` y `status_code`

---

## Plan de acción

**Objetivo:** Uniformar los routers para que (1) toda invocación a un `*_controller` se asigne a `payload` y se pase tal cual a `SuccessResponse(payload=payload, ...)`, y (2) los decoradores no contengan `summary`, `description` ni `status_code`.

**Alcance:** 5 routers en `backend/src/packages/<package>/router.py` (`animes`, `auth`, `users`, `franchises`, `episodes`).

**Reglas de transformación:**

1. **Renombrado de variable.** En cada endpoint donde aparezca `data = await <fn>_controller(...)` (o sin `await`), renombrar a `payload`. Actualizar el `return SuccessResponse(payload=data, ...)` para que sea `SuccessResponse(payload=payload, ...)`. En endpoints donde no se almacena el resultado en una variable (p. ej. `SuccessResponse(payload=None, ...)` tras llamar al controller directamente) no hay renombrado.
2. **Limpieza de decoradores.** Quitar `summary=`, `description=` y `status_code=` de los `@router.<verb>(...)`. Conservar `response_model` y la ruta. Aplicar también a endpoints que no devuelven `SuccessResponse` (SSE, `FileResponse`).
3. **Sin cambios funcionales.** No tocar imports, dependencies, lógica del controller, ni el `message` ya existente. No cambiar el status HTTP real (FastAPI usará el default según verbo); si un endpoint dependía de un `status_code` distinto al default, eso queda fuera del alcance de esta tarea — verificar antes de eliminar.

> Verificación previa requerida: cualquier `status_code` distinto a `200` (GET/PUT/DELETE) o `201` (POST por convención) debe documentarse antes de eliminarlo. Si el endpoint es `POST` con `status_code=201`, eliminar la línea es seguro (FastAPI ya devuelve 201 por defecto en POST). Si es `PUT` con `status_code=200`, también seguro (default `PUT` = 200).

---

### Tarea 1: `animes/router.py`

**Archivo:**
- Modificar: `backend/src/packages/animes/router.py`

**Endpoints a tocar:** `search_animes`, `get_saved_animes`, `get_in_emission_animes`, `get_anime`, `update_anime`, `save_anime`, `unsave_anime`.

- [ ] **Paso 1: Renombrar `data` → `payload` en los 5 endpoints que la usan**

`search_animes`:
```python
async def search_animes(
    query: str,
    current_user: dict = Depends(auth_scheme),
):
    payload = await search_anime_controller(query, current_user["id"])
    return SuccessResponse(payload=payload, message="Anime searched")
```

`get_saved_animes`:
```python
async def get_saved_animes(
    current_user: dict = Depends(auth_scheme),
):
    payload = await get_saved_animes_controller(current_user["id"])
    return SuccessResponse(payload=payload, message="Saved animes retrieved")
```

`get_in_emission_animes`:
```python
async def get_in_emission_animes(
    current_user: dict = Depends(auth_scheme),
):
    payload = await get_in_emission_animes_controller(current_user["id"])
    return SuccessResponse(payload=payload, message="In-emission animes retrieved")
```

`get_anime`:
```python
async def get_anime(
    anime_id: str,
    current_user: dict = Depends(auth_scheme),
):
    payload = await get_anime_controller(anime_id, current_user["id"])
    return SuccessResponse(payload=payload, message="Anime retrieved")
```

`update_anime`:
```python
async def update_anime(
    anime_data: dict = Depends(valid_anime_for_update),
):
    anime_id = anime_data["anime_id"]
    user_id = anime_data["user_id"]

    payload = await update_anime_controller(anime_id, user_id)
    return SuccessResponse(payload=payload, message="Anime updated successfully")
```

`save_anime` y `unsave_anime`: no requieren renombrado (no almacenan resultado en variable).

- [ ] **Paso 2: Limpiar decoradores**

```python
@animes_router.get("/search", response_model=SearchAnimeResultListOut)
@animes_router.get("/saved", response_model=SearchAnimeResultListOut)
@animes_router.get("/in-emission", response_model=InEmissionAnimeListOut)
@animes_router.get("/{anime_id}", response_model=AnimeOut)
@animes_router.put("/{anime_id}", response_model=AnimeOut)
@animes_router.put("/{anime_id}/save", response_model=SuccessResponse)
@animes_router.put("/{anime_id}/unsave", response_model=SuccessResponse)
```

- [ ] **Paso 3: Verificar sintaxis**

```powershell
uv run python -c "import ast; ast.parse(open('src/packages/animes/router.py', encoding='utf-8').read())"
```
Esperado: sin output (parseo OK).

---

### Tarea 2: `auth/router.py`

**Archivo:**
- Modificar: `backend/src/packages/auth/router.py`

**Endpoints a tocar:** `login`, `register`, `refresh_token`.

- [ ] **Paso 1: Renombrar `data` → `payload`**

```python
async def login(login_info: LoginInfo):
    payload = await login_controller(login_info.username, login_info.password)
    return SuccessResponse(payload=payload, message="User logged in successfully")


async def register(register_info: CreateInfo):
    payload = await register_controller(register_info.username, register_info.password)
    return SuccessResponse(payload=payload, message="User registered successfully")


async def refresh_token(refresh_token: str):
    payload = refresh_controller(refresh_token)
    return SuccessResponse(payload=payload, message="Token refreshed successfully")
```

- [ ] **Paso 2: Limpiar decoradores**

```python
@auth_router.post("/login", response_model=TokenOut)
@auth_router.post("/register", response_model=SuccessResponse)
@auth_router.post("/refresh", response_model=AccessTokenOut)
```

- [ ] **Paso 3: Verificar sintaxis**

```powershell
uv run python -c "import ast; ast.parse(open('src/packages/auth/router.py', encoding='utf-8').read())"
```

---

### Tarea 3: `users/router.py`

**Archivo:**
- Modificar: `backend/src/packages/users/router.py`

**Endpoints a tocar:** `get_users`, `get_me`, `check_username`, `update_user`, `get_avatars`, `get_user_statistics`.

> Nota: los decoradores aquí ya están limpios (no contienen `summary`/`description`/`status_code`). Solo aplica el renombrado.

- [ ] **Paso 1: Renombrar `data` → `payload` en los 6 endpoints**

```python
async def get_users(current_user: dict = Depends(auth_scheme)):
    payload = await get_users_controller(current_user["id"])
    return SuccessResponse(payload=payload, message="Users retrieved")


async def get_me(current_user: dict = Depends(auth_scheme)):
    payload = await get_me_controller(current_user["id"])
    return SuccessResponse(payload=payload, message="User retrieved")


async def check_username(username: str):
    payload = await check_username_controller(username)
    return SuccessResponse(payload=payload, message="Username checked")


async def update_user(
    user_info: UserInfo,
    current_user: dict = Depends(auth_scheme),
):
    payload = await update_user_controller(user_info, current_user["id"])
    return SuccessResponse(payload=payload, message="User updated")


async def get_avatars(current_user: dict = Depends(auth_scheme)):
    payload = await get_avatars_controller()
    return SuccessResponse(payload=payload, message="Avatars retrieved")


async def get_user_statistics(current_user: dict = Depends(auth_scheme)):
    payload = await get_user_statistics_controller(current_user["id"])
    return SuccessResponse(payload=payload, message="User statistics retrieved")
```

- [ ] **Paso 2: Verificar sintaxis**

```powershell
uv run python -c "import ast; ast.parse(open('src/packages/users/router.py', encoding='utf-8').read())"
```

---

### Tarea 4: `franchises/router.py`

**Archivo:**
- Modificar: `backend/src/packages/franchises/router.py`

**Endpoints a tocar:** `get_franchises`, `create_franchise`, `get_animes_for_franchises`.

- [ ] **Paso 1: Renombrar `data` → `payload`**

```python
async def get_franchises(current_user: dict = Depends(auth_scheme)):
    payload = await get_franchises_controller(current_user["id"])
    return SuccessResponse(payload=payload, message="Franchises retrieved")


async def create_franchise(
    franchise_info: CreateFranchise,
    current_user: dict = Depends(auth_scheme),
):
    payload = await create_franchise_controller(franchise_info)
    return SuccessResponse(payload=payload, message="Franchise created successfully")


async def get_animes_for_franchises(current_user: dict = Depends(auth_scheme)):
    payload = await get_animes_for_franchises_controller(current_user["id"])
    return SuccessResponse(payload=payload, message="Animes retrieved")
```

- [ ] **Paso 2: Limpiar decoradores**

```python
@franchises_router.get("", response_model=FranchiseListOut)
@franchises_router.post("", response_model=SuccessResponse)
@franchises_router.get("/animes", response_model=AnimeFranchiseListOut)
```

- [ ] **Paso 3: Verificar sintaxis**

```powershell
uv run python -c "import ast; ast.parse(open('src/packages/franchises/router.py', encoding='utf-8').read())"
```

---

### Tarea 5: `episodes/router.py`

**Archivo:**
- Modificar: `backend/src/packages/episodes/router.py`

**Endpoints a tocar:** `get_download_episodes`, `get_last_downloaded_episodes`, `get_downloaded_animes`, `get_animes_storage`, `delete_anime_storage`, `get_download_status`, `get_download_episode`, `download_anime_episode`, `delete_download_episode`, `download_anime_episode_bulk`.

> Nota 1: `get_download_status` y `get_download_episode` no usan `SuccessResponse` (devuelven `StreamingResponse` / `FileResponse`). Solo aplica la limpieza de decorador.
>
> Nota 2: en `get_download_status` hay una variable local `payload = json.loads(message["data"])` dentro del `event_generator`. **No tocar** — es independiente del renombrado de esta tarea.

- [ ] **Paso 1: Renombrar `data` → `payload` en los endpoints que asignan resultado del controller**

```python
async def get_download_episodes(
    anime_id: str | None = None,
    limit: int = 10,
    page: int = 1,
    current_user: dict = Depends(auth_scheme),
):
    payload = await get_download_episodes_controller(
        current_user["id"], anime_id, limit, page
    )
    return SuccessResponse(payload=payload, message="Downloads retrieved")


async def get_last_downloaded_episodes(current_user: dict = Depends(auth_scheme)):
    payload = await get_last_downloaded_episodes_controller(current_user["id"])
    return SuccessResponse(payload=payload, message="Last downloaded episodes retrieved")


async def get_downloaded_animes(current_user: dict = Depends(auth_scheme)):
    payload = await get_downloaded_animes_controller(current_user["id"])
    return SuccessResponse(payload=payload, message="Downloaded animes retrieved")


async def get_animes_storage(
    limit: int = 10,
    page: int = 1,
    current_user: dict = Depends(auth_scheme),
):
    payload = await get_animes_storage_controller(limit, page)
    return SuccessResponse(payload=payload, message="Animes storage retrieved")


async def download_anime_episode(
    episode_data: dict = Depends(valid_episode_by_number),
    force_download: bool = False,
    current_user: dict = Depends(auth_scheme),
):
    payload = await download_anime_episode_controller(
        episode_data["episode_id"],
        force_download,
        current_user["id"],
    )
    return SuccessResponse(payload=payload, message="Anime download enqueued successfully")


async def download_anime_episode_bulk(
    anime_id: str,
    episodes: list[int],
    current_user: dict = Depends(auth_scheme),
    anime_data: dict = Depends(valid_anime_id),
):
    payload = await download_anime_episode_bulk_controller(
        anime_data["anime_id"],
        episodes,
        current_user["id"],
    )
    return SuccessResponse(payload=payload, message="Anime downloaded successfully")
```

`delete_anime_storage` y `delete_download_episode`: no requieren renombrado (no almacenan resultado en variable).

- [ ] **Paso 2: Limpiar decoradores**

```python
@episodes_router.get("/downloads", response_model=EpisodeDownloadListOut)
@episodes_router.get("/downloads/last", response_model=EpisodeDownloadListOut)
@episodes_router.get("/downloads/animes", response_model=AnimeDownloadInfoListOut)
@episodes_router.get("/storage", response_model=AnimeDownloadInfoListOut)
@episodes_router.delete("/storage/{anime_id}", response_model=SuccessResponse)
@episodes_router.get("/stream/status")
@episodes_router.get("/{episode_id}/file")
@episodes_router.post("/{anime_id}/{episode_number}/download", response_model=DownloadTaskOut)
@episodes_router.delete("/{anime_id}/{episode_number}/download", response_model=SuccessResponse)
@episodes_router.post("/{anime_id}/download/bulk", response_model=DownloadTaskListOut)
```

- [ ] **Paso 3: Verificar sintaxis**

```powershell
uv run python -c "import ast; ast.parse(open('src/packages/episodes/router.py', encoding='utf-8').read())"
```

---

### Tarea 6: Verificación global y commit

- [ ] **Paso 1: Confirmar que no quedan `summary=`/`description=`/`status_code=` en routers**

```powershell
# Desde la raíz del repo
rg -n "summary=|description=|status_code=" backend/src/packages --type py
```
Esperado: sin resultados.

- [ ] **Paso 2: Confirmar que ningún endpoint pasa `payload=data` a `SuccessResponse`**

```powershell
rg -n "SuccessResponse\(payload=data" backend/src/packages --type py
```
Esperado: sin resultados.

- [ ] **Paso 3: Confirmar que el resto de `SuccessResponse(payload=...)` usa `payload=payload` o `payload=None`**

```powershell
rg -n "SuccessResponse\(payload=" backend/src/packages --type py
```
Esperado: solo apariciones de `payload=payload` o `payload=None`.

- [ ] **Paso 4: Arrancar la app para validar que importa sin errores**

```powershell
uv run python -c "from main import app; print('OK')"
```
Esperado: `OK`. (Ejecutar desde `backend/src/`.)

- [ ] **Paso 5: Commit único**

```powershell
git add backend/src/packages/animes/router.py backend/src/packages/auth/router.py backend/src/packages/users/router.py backend/src/packages/franchises/router.py backend/src/packages/episodes/router.py tasks/03-polish.md
git commit -m "refactor(routers): rename controller result to payload, drop decorator metadata"
```

---

### Resumen de impacto

| Router | Endpoints | Renombrados `data→payload` | Decoradores limpiados |
|---|---|---|---|
| `animes` | 7 | 5 | 7 |
| `auth` | 3 | 3 | 3 |
| `users` | 6 | 6 | 0 (ya limpios) |
| `franchises` | 3 | 3 | 3 |
| `episodes` | 10 | 6 | 10 |
| **Total** | **29** | **23** | **23** |
