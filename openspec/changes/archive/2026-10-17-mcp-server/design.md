## Context

Lo que este change reutiliza:

- **`ApiKeyBearer`** (`packages/auth/middleware.py`) resuelve una API key al mismo `current_user` (`id`, `username`, `isActive`, `role`) que `JWTBearer`. Nunca consulta `AUTH_ENABLED`.
- **`assert_min_role(current_user, min_role)`** (`auth/roles.py`) aplica el rol sin depender de FastAPI.
- **`instance_settings`** es una fila única con `registration_policy`. `GET/PUT /settings` exigen `admin`.
- **Los controllers** de `animes`, `episodes` y `users` reciben `user_id` explícito y lanzan `AppError` (`NotFoundError`, `ConflictError`, `TooManyRequestsError`, ...). Algunas reglas viven solo en `dependencies.py`:
  - `valid_anime_for_update`: el anime está sincronizado y pasaron 5 minutos desde el último refresco
  - `valid_anime_id`: el anime existe
  - `user_not_saved_anime` y `anime_is_saved_by_user`: guardado duplicado y quitar uno no guardado
- **`download_anime_episode_bulk_controller`** ya consulta en lote, con `get_episodes_with_user_download_status`, si cada episodio existe y si el usuario lo pidió. Devuelve `success: false` sin motivo.
- **El worker** escribe en `episodes.status` la secuencia `PENDING`, `GETTING-LINK`, `DOWNLOADING`, `RETRYING`, `SUCCESS` y `FAILED`. Al llegar a `SUCCESS` pone `job_id = NULL` (`worker/src/tasks/download.py:274`).
- **nginx** ya proxea `/api/` con `proxy_buffering off`.

La motivación está en `proposal.md`. Los requisitos están en `specs/mcp-server/spec.md` y `specs/access-control/spec.md`.

## Goals / Non-Goals

**Goals:**

- Que REST y MCP apliquen las mismas reglas de negocio desde un solo lugar.
- Que agregar un tool sea declarar una función con su rol mínimo y sus anotaciones, sin tocar la autenticación ni el montaje.
- Que en la Fase 2 la traducción de ids sea el único punto que cambia para soportar otro proveedor.

**Non-Goals:**

- Resources y prompts MCP: se dejan para un change posterior.
- Notificaciones de progreso y cualquier estado de sesión MCP.
- Cambiar la autenticación de los endpoints REST, incluidos los públicos `stream/status` y `.../file` (Fase 6).

## Decisions

### D1 - SDK oficial `mcp`, con versión mayor fijada y sin su autenticación

Se agrega el SDK oficial de Python (`mcp`, repo `modelcontextprotocol/python-sdk`). Aporta el protocolo (handshake, `tools/list`, `tools/call`, esquemas JSON derivados de los type hints) y el transporte Streamable HTTP.

- **v2 con la versión mayor fijada:** `mcp>=2.3,<3` en `backend/pyproject.toml`, y `uv lock` se regenera. La v2 es estable desde `2.0.0` (2026-07-28); la última es `2.3.0` (2026-10-02), con `requires-python >=3.10`, compatible con el backend. Se escribe contra la API v2: `MCPServer` (`mcp.server.mcpserver`, antes `FastMCP`), y los parámetros de transporte como `json_response` van en `streamable_http_app()`, no en el constructor. Los ejemplos v1 que circulan (`mcp.server.fastmcp`) no aplican.
- **Sin la autenticación del SDK** (`TokenVerifier`, `AuthSettings`). Está diseñada para un resource server OAuth 2.1, con `AccessToken` (`client_id`, `scopes`, `resource`) y `issuer_url` obligatorio. Para meter nuestras keys ahí habría que forzar usuario y rol en campos con otro significado, y el 404 con el MCP apagado igual quedaría afuera. Ver D2.
- **Alternativa descartada:** el paquete `fastmcp` (línea 2.x, independiente). Trae middleware y filtrado de tools listos, pero suma una dependencia que no sigue a la spec al mismo ritmo que el SDK oficial.

### D2 - Wrapper ASGI propio: guard, API key y contextvar

El servidor MCP se registra con `app.add_route("/api/mcp", McpGate())`. Es una ruta y no un `mount`, porque un `Mount("/api/mcp")` no matchea `/api/mcp` sin barra final y Starlette redirigiría a `/api/mcp/`. `McpGate` (`src/mcp_server/gate.py`) es una app ASGI que, por cada request HTTP:

```
request ─▶ ¿instance_settings.mcp_enabled?  no ─▶ 404
                     │ sí
                     ▼
           ApiKeyBearer(Request(scope))     falla ─▶ 401
                     │ current_user
                     ▼
           scope["aniseek.current_user"] = ...  ─▶  session_manager.handle_request
                                                    ─▶ tool lee ctx.request_context.request.scope
```

- **El guard va primero**, así una request sin key con el MCP apagado recibe 404 y no 401, como pide el spec.
- **`mcp_enabled` se lee de la base en cada request**: un `SELECT` sobre una fila. Sin caché, el cambio tiene efecto en la request siguiente aun con varias réplicas.
- **Se reutiliza `ApiKeyBearer`** construyendo un `starlette.requests.Request` desde el `scope`. Su `HTTPException` se traduce a una respuesta JSON 401. Los exception handlers de FastAPI no cubren una app montada, así que `McpGate` arma sus propias respuestas de error.
- **El usuario viaja en el `scope`, no en un contextvar.** Al implementar se vio que el modo stateless del SDK atiende cada request dentro del task group abierto en el lifespan (`StreamableHTTPSessionManager._handle_stateless_request`), así que un contextvar fijado por el gate no llega al handler. En cambio, el SDK pasa la request HTTP a cada handler (`ServerRequestContext.request`), con el mismo `scope`. El wrapper de cada tool (D4) lo lee desde ahí y recién entonces fija un contextvar, ya dentro del task del tool, para el cuerpo (`current_user()`).
- **Protección contra DNS rebinding desactivada** (`TransportSecuritySettings(enable_dns_rebinding_protection=False)`). El SDK la activa por defecto con hosts `localhost`, lo que rechazaría el `Host` real detrás de nginx. Cada request ya exige una API key.
- `CORSMiddleware` y `TracingMiddleware` son middlewares de la app raíz y también envuelven la app montada.

### D3 - Stateless y respuestas JSON

El servidor se crea con `stateless_http=True` y respuestas JSON (`json_response=True`), sin SSE. Ningún tool necesita streaming ni notificaciones, y sin sesiones no hay afinidad con una réplica.

`mcp.session_manager.run()` se abre en el `lifespan` de `main.py`, después de `connect_db()` y `ensure_owner()`, a través de `mcp_lifespan()`. Sin esto, cada request falla con `RuntimeError: Task group is not initialized`. Un session manager solo puede correr una vez, así que `mcp_lifespan()` crea uno nuevo (`streamable_http_app(...)`) en cada arranque, lo que también permite usarlo en cada test.

### D4 - Registro de tools con rol mínimo y anotaciones

Cada tool se declara en `src/mcp_server/tools/` con su rol mínimo y sus anotaciones MCP:

- `readOnlyHint` en los tools de consulta
- `destructiveHint` en `delete_anime_files`
- `openWorldHint` en los tools que consultan al proveedor

Un helper registra el tool en el servidor y guarda su rol en `TOOL_MIN_ROLE`.

- **Visibilidad:** una subclase de `MCPServer` sobrescribe `_handle_list_tools` para filtrar la lista del SDK con `role_rank(current_user["role"]) >= ROLE_RANK[min_role]`. Es un método privado del SDK; el test de punta a punta lo cubre si cambia en una versión 2.x.
- **Ejecución:** cada tool pasa por un wrapper que llama a `assert_min_role` antes del cuerpo. Así, invocar por nombre un tool oculto también se rechaza.
- **Alternativa descartada:** un servidor por rol. Triplica el montaje y no resuelve un cambio de rol entre requests.

### D5 - Las reglas de negocio bajan al service

Las reglas que hoy viven en `dependencies.py` pasan a funciones del service. Los controllers las llaman al comienzo:

| Regla | Hoy | Pasa a |
|---|---|---|
| Anime sincronizado y cooldown de 5 min | `valid_anime_for_update` | `update_anime_controller` |
| Anime existe | `valid_anime_id` | `assert_anime_exists` en `animes/service.py`, usada por la descarga masiva y el borrado de almacenamiento |
| Guardado duplicado | `user_not_saved_anime` | `save_anime_controller` |
| Quitar uno no guardado | `anime_is_saved_by_user` | `unsave_anime_controller` |

- Las dependencias que solo hacían eso desaparecen, y los routers pasan `anime_id` y `current_user["id"]` directo.
- Las excepciones y los mensajes no cambian, así que las respuestas REST tampoco. Los tests REST existentes (`test_animes_sync.py`, etc.) actúan como red de regresión.
- `require_role("admin")` se queda en el decorador de `DELETE /episodes/storage/{anime_id}`: el 403 tiene que llegar antes que el 404.

### D6 - Traducción de ids en el borde del MCP

`src/mcp_server/ids.py` define `parse_anime_id("animeav1:slug") -> slug` y `format_anime_id(slug) -> "animeav1:slug"`, con `SUPPORTED_PROVIDERS = {"animeav1"}`. La validación es `^[a-z0-9]+:[a-z0-9-]+$` y el error enumera los proveedores soportados.

Los tools no devuelven los modelos REST tal cual. Usan modelos de salida propios (`src/mcp_server/schemas.py`) que se arman con `format_anime_id`, incluido `related_info[].id`. Así, ningún id sin prefijo se escapa por un campo olvidado, y estos modelos no tienen ningún campo de URL de archivo.

En la Fase 2, `ids.py` pasa a resolver el proveedor y el resto de los tools no cambia.

### D7 - `download_episodes`: tope antes de encolar y motivo por episodio

1. Se quitan los números repetidos y se resuelve el anime (D5, 404 si no existe).
2. Una consulta en lote con `get_episodes_with_user_download_status` separa los ya pedidos por el usuario de los restantes. Los restantes incluyen los inexistentes, que no se pueden saber sin consultar y que igual cuentan como trabajo pedido.
3. Si los restantes superan `MCP_DOWNLOAD_CAP = 25`, se rechaza el pedido sin encolar.
4. Si no, se llama a `download_anime_episode_bulk_controller`, que ahora devuelve `reason` en cada ítem: `already_downloaded`, `not_found` o `enqueue_failed`, y `null` cuando el ítem fue encolado. En REST es un campo opcional nuevo de `DownloadTaskStatus`.

El tope vive en el tool y no en el controller: la REST API no tiene tope en v1.

### D8 - `get_download_status` por anime y episodio, no por `job_id`

El worker borra el `job_id` cuando la descarga termina con éxito, así que una consulta por `job_id` perdería justo el estado final. El tool recibe `anime_id` y una lista de números, reutiliza `get_episodes_with_user_download_status` y devuelve `status` (`NULL` → `not_downloaded`, `SUCCESS` → `downloaded`, el resto en minúsculas) junto con `requested_by_user` (el flag `already_downloaded`). El estado es global, porque el archivo es uno solo, y el flag es por usuario.

### D9 - `mcp_enabled` en `instance_settings` y endpoint propio del owner

La migración nueva agrega `mcp_enabled BOOLEAN NOT NULL DEFAULT false`.

- `PUT /settings/mcp` recibe `{ "enabled": bool }` con `require_role("owner")` y registra `updated_by` y `updated_at`.
- `GET /settings` (admin) suma `mcpEnabled` para que la UI muestre el estado.
- **Endpoint aparte y no un campo opcional en `PUT /settings`:** el rol queda declarado en la ruta y no depende de qué campos trae el body.

### D10 - Errores de tool

Los `AppError` lanzados por service o controllers se convierten en un error de tool (`isError: true`) con el mensaje original. Así el agente lee "Anime was updated recently. Please wait 120 seconds..." y puede actuar en consecuencia.

Un `ForbiddenError` de D4 se trata igual. Una excepción inesperada se registra con su traza y devuelve un mensaje genérico, sin detalles internos.

Los errores de autenticación y el 404 del switch no llegan al protocolo: son respuestas HTTP de `McpGate`.

### D11 - Frontend: página Instance Settings propia, con menú interno

La configuración de la instancia sale de la pestaña Settings de User Management y pasa a una página propia, `/instance-settings`. Su entrada en el sidebar va en la navegación secundaria, encima de Profile:

```
 Sidebar                         /settings
 ┌──────────────────┐   ┌──────────────┬──────────────────────────────┐
 │ Anime            │   │ Registration │ Registration                 │
 │  Home … Downloads│   │ MCP server   │  ( ) Invitation only  (•) …  │
 │ Administration   │   │ Ownership    │ ──────────────────────────── │
 │  Storage         │   │              │ MCP server                   │
 │  User Management │   │  (sticky,    │  [■] Enabled   /api/mcp      │
 │ ──────────────── │   │   enlazable  │  → Generar API key (#api-key)│
 │ ⚙ Settings  ◀ new│   │   #mcp)      │ ──────────────────────────── │
 │ 👤 Profile       │   │              │ Ownership (danger)           │
 └──────────────────┘   └──────────────┴──────────────────────────────┘
```

- **Entrada de navegación:** `secondaryNavigationData` suma `{ title: "Instance Settings", icon: Settings, url: "/instance-settings", minRole: "admin", mobile: "account" }` antes de Profile. En móvil aparece en el menú de cuenta.
- **Secciones según el rol:**

  | Sección | Contenido | Visible para |
  |---|---|---|
  | Registration | política `invite` / `open` (lo que hoy es `SettingsTab`) | admin, owner |
  | MCP server | switch y enlace a `/profile#ai-agents` | owner |
  | Ownership | transferencia (hoy `TransferOwnerCard`), con tono de peligro y al final | owner |

  Un `member` no ve la entrada. Si entra por URL, la página lo redirige a `/home`, como hace User Management.
- **Modo un usuario:** como no hay login, la política de registro y la transferencia (que pide contraseña) no tienen efecto. La página muestra solo MCP server, igual que Profile oculta Security.
- **Menú interno reutilizado:** el layout de Profile (aside fijo con botones, scroll suave, sección activa según el scroll y hash enlazable) se extrae a un componente compartido, `components/sectioned-page.tsx`, con `useActiveSection`. Profile y Settings lo usan. Cada uno pasa su lista de secciones, ya filtrada por rol y modo.
- **Código movido:** nace `features/settings/` con `registration-section.tsx`, `mcp-section.tsx` y `ownership-section.tsx`. Sale de `features/user-management/` todo lo que solo servía a la pestaña: `settings-tab.tsx`, `settings-section.tsx` y `transfer-owner-card.tsx`. User Management queda con las pestañas Users e Invitations.
- **Conexión de agentes en Profile:** la sección "API key" de Profile pasa a ser "AI agents" (`#ai-agents`), con la API key, el endpoint y el comando `claude mcp add` listo para copiar. Todo eso le sirve a cualquier usuario, no solo al owner. El endpoint y el comando se ven deshabilitados mientras el MCP está apagado, con un aviso que al owner le enlaza a Settings. Al generar una key, el diálogo muestra el comando con la key ya incluida. Como `GET /settings` es de admin, el estado se lee de `GET /settings/mcp` (`{ "enabled": bool }`), abierto a cualquier usuario autenticado.
- **Alternativa descartada:** dejar la configuración en una pestaña de User Management y sumarle el MCP. El MCP no es gestión de usuarios, y la pestaña ya mezclaba registro con ownership.

### D12 - Ubicación: `src/mcp_server/`, al lado de `routes.py`

`packages/` agrupa dominios, y cada uno tiene su propio router, service y repository. El MCP no es un dominio: es una segunda interfaz, como la REST API (`routes.py`), que llama a los services de varios dominios. Por eso vive en `src/`:

```
src/
├── main.py          ← monta REST y MCP, lifespan
├── routes.py        ← interfaz REST  ──┐
├── mcp_server/      ← interfaz MCP   ──┼──▶ packages/<dominio>/service.py
└── packages/        ← dominios
```

```
src/mcp_server/
├── __init__.py   # expone la app ASGI montable y el session manager
├── server.py     # instancia del SDK, contextvar y registro de tools con rol (D3, D4)
├── gate.py       # McpGate (D2)
├── ids.py        # traducción de ids (D6)
├── schemas.py    # modelos de salida (D6)
└── tools/        # catalog.py, library.py, downloads.py
```

- **No se llama `mcp`:** `src` está en el `sys.path` (`pythonpath = ["src"]` en pytest, imports absolutos como `from database import ...`). Una carpeta `src/mcp/` taparía al SDK, y `from mcp.server... import ...` resolvería a nuestro paquete con un error que recién aparece en runtime.
- **`PUT /settings/mcp` se queda en `packages/settings/`:** es configuración de la instancia, un dominio. `gate.py` lee `mcp_enabled` a través del repository de settings.

## Risks / Trade-offs

- **[La API del SDK cambia entre mayores]** → versión mayor fijada (D1) y un test de integración que hace `initialize`, `tools/list` y `tools/call` por HTTP contra la app real, así una actualización que rompa se detecta en CI.
- **[La sub-app montada no hereda los exception handlers ni el lifespan]** → `McpGate` arma sus respuestas de error (D2) y `session_manager.run()` va en el lifespan raíz (D3). El test de integración lo cubre.
- **[Una consulta a la base por request para leer `mcp_enabled`]** → es una fila con clave primaria y el pool ya existe. Si llegara a pesar, alcanza con una caché de pocos segundos, a costa de la inmediatez que pide el spec.
- **[Dos llamadas concurrentes pueden superar 25 episodios en total]** → aceptado: el tope protege contra un pedido desmedido, no es una cuota. Las cuotas son de la Fase 6.
- **[`search_anime` y `get_anime` scrapean y pueden tardar varios segundos]** → declarado con `openWorldHint`. Si el proveedor falla, el tool devuelve el mismo mensaje que la REST API (404, 429, 502 traducidos a error de tool).
- **[Mover validaciones al service cambia la firma de routers con tests existentes]** → las excepciones y los mensajes se conservan, y la suite REST completa corre antes del MCP (tasks 2.x).
- **[En modo un usuario, cualquiera con acceso a la UI puede generar la key del owner]** → ya está documentado por `api-keys`. `docs/mcp.md` lo repite junto al switch.

## Migration Plan

1. La migración agrega la columna con `DEFAULT false`, así ninguna instancia expone el MCP al actualizar.
2. Se despliega la API. `/api/mcp` responde 404 hasta que el owner lo active.
3. **Rollback:** el `down` elimina la columna. Volver a la versión anterior deja `/api/mcp` sin montar, y las keys siguen intactas porque viven en `api_keys`.