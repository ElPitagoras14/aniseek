## 1. Esquema y settings

- [x] 1.1 Crear `dbmate/migrations/0004_mcp_enabled.sql`: `up` agrega `instance_settings.mcp_enabled BOOLEAN NOT NULL DEFAULT false` y `down` la elimina. Verificar con `dbmate up`, `dbmate down` y `dbmate up` sobre la base de desarrollo
- [x] 1.2 Regenerar `dbmate/schema.sql` y verificar que incluye `mcp_enabled`
- [x] 1.3 `packages/settings/`: leer `mcp_enabled`, agregar `mcpEnabled` a `GET /settings` y crear `PUT /settings/mcp` (`{ "enabled": bool }`, `require_role("owner")`, registra `updated_by`) según D9. Verificar en `/docs`

## 2. Reglas de negocio al service (D5)

- [x] 2.1 Mover el chequeo de anime sincronizado y el cooldown de 5 min de `valid_anime_for_update` a `update_anime_controller`, y simplificar `PUT /animes/{anime_id}`. Verificar que `test_animes_sync.py` sigue pasando
- [x] 2.2 Crear `assert_anime_exists` en `animes/service.py` y usarla en `download_anime_episode_bulk_controller` y `delete_anime_storage_controller`. Quitar `valid_anime_id` de esos routers y mantener `require_role("admin")` en el decorador del borrado. Verificar que `test_access_control.py` sigue pasando
- [x] 2.3 Mover el chequeo de guardado duplicado a `save_anime_controller` y el de "no guardado" a `unsave_anime_controller`, conservando `ConflictError` y `NotFoundError` con los mismos mensajes. Agregar tests REST de 409 y 404 si no existen
- [x] 2.4 Agregar `reason` (`already_downloaded`, `not_found`, `enqueue_failed` o `null`) a cada ítem de `download_anime_episode_bulk_controller` y al modelo `DownloadTask` como campo opcional, más el tipo en `frontend/src/features/anime/types.ts`. Verificar con un test REST de descarga masiva que mezcle los tres casos
- [x] 2.5 Correr `uv run pytest` en `backend/` y verificar que la suite completa pasa antes de empezar con el MCP

## 3. Servidor MCP

- [x] 3.1 Agregar `mcp>=2.3,<3` a `backend/pyproject.toml` (D1), ejecutar `uv lock` y verificar que `docker compose build api` sigue funcionando
- [x] 3.2 Crear `src/mcp_server/` (D12) con `server.py`: el servidor en modo stateless y respuestas JSON (D3), el contextvar `current_user_var` y el helper de registro de tools con rol mínimo y anotaciones (D4). Verificar que `from mcp...` sigue resolviendo al SDK
- [x] 3.3 Implementar `McpGate` en `src/mcp_server/gate.py` (D2): 404 si `mcp_enabled` es falso, luego `ApiKeyBearer` con 401 en JSON, y fijar el contextvar. Montarlo en `/api/mcp` desde `main.py` y abrir `session_manager.run()` en el `lifespan`. Verificar que la API arranca y que `/api/health` sigue respondiendo
- [x] 3.4 Sobrescribir el handler de `tools/list` para filtrar por rol y envolver cada tool con `assert_min_role` (D4), con la conversión de errores de D10
- [x] 3.5 Crear `src/mcp_server/ids.py` (`parse_anime_id`, `format_anime_id`, `SUPPORTED_PROVIDERS`) y los modelos de salida de `src/mcp_server/schemas.py` (D6). Verificar con tests unitarios de formato válido, proveedor no soportado, id sin proveedor y formato inválido

## 4. Tools

- [x] 4.1 Tools de consulta en `src/mcp_server/tools/catalog.py`: `search_anime`, `get_anime`, `list_saved`, `list_airing`, `list_downloads`, `get_storage_usage` y `get_stats`, llamando a los controllers existentes con el `user_id` del contextvar y devolviendo ids con prefijo, incluidas las relaciones
- [x] 4.2 Tools de biblioteca en `src/mcp_server/tools/library.py`: `save_anime`, `unsave_anime` y `refresh_anime`, apoyados en las reglas movidas en 2.x
- [x] 4.3 En `src/mcp_server/tools/downloads.py`, `download_episodes` con deduplicación, consulta en lote, tope de 25 sobre los restantes y resultado por episodio con su estado (D7)
- [x] 4.4 En `src/mcp_server/tools/downloads.py`, `get_download_status` por anime y números de episodio, con el mapeo de estados y `requested_by_user` (D8)
- [x] 4.5 En `src/mcp_server/tools/library.py`, `delete_anime_files` con rol mínimo `admin` y `destructiveHint`

## 5. Tests del MCP

- [x] 5.1 `tests/test_mcp.py`, switch: 404 con el MCP apagado, con y sin key; el owner lo activa vía `PUT /settings/mcp` y la request siguiente se atiende; admin y member reciben 403 en `PUT /settings/mcp`; las keys siguen funcionando después de apagar y volver a encender
- [x] 5.2 Autenticación: sin key 401, token JWT de sesión 401, key revocada 401 en la llamada siguiente, usuario desactivado 401, y modo un usuario (`AUTH_ENABLED=False`) 401 sin key y éxito con la key del owner
- [x] 5.3 Protocolo de punta a punta por HTTP contra la app real: `initialize`, `tools/list` y `tools/call` de `list_saved`. Verifica el montaje, el lifespan y que cada tool expone las anotaciones esperadas
- [x] 5.4 Roles: un member no ve `delete_anime_files` y recibe error de permisos al invocarlo por nombre, con los archivos intactos; un admin lo ve; un admin degradado a member entre dos llamadas queda rechazado en la segunda
- [x] 5.5 Reglas y resultados: cooldown de `refresh_anime`, guardado duplicado, `unsave_anime` sin guardar, anime inexistente en `download_episodes`; tope (30 nuevos se rechazan sin encolar, 30 con 10 ya pedidos encola 20); episodio inexistente informado; `get_download_status` después de `SUCCESS`; ids con prefijo en la salida, incluidas las relaciones. El scraping y el encolado se mockean como en los tests existentes
- [x] 5.6 Correr `uv run pytest` y verificar que la suite completa pasa

## 6. Frontend

- [x] 6.1 `features/access/types.ts` y `api.ts`: `mcpEnabled` en la respuesta de settings y `updateMcpEnabled(enabled)` contra `PUT /settings/mcp`
- [x] 6.2 Extraer el layout con menú interno de `profile-page.tsx` a `components/sectioned-page.tsx` (aside fijo, `useActiveSection`, scroll y hash) y migrar Profile a ese componente. Verificar a mano que Profile se ve y navega igual, incluido `/profile#api-key`
- [x] 6.3 Crear `features/settings/` y la ruta `/instance-settings` sobre `sectioned-page.tsx`, con las secciones Registration (admin+), MCP server (owner) y Ownership (owner) según D11. En modo un usuario se muestra solo MCP server, y un `member` se redirige a `/home`
- [x] 6.4 Mover la política de registro y la transferencia de ownership desde `features/user-management/` a las secciones nuevas, borrar `settings-tab.tsx`, `settings-section.tsx` y `transfer-owner-card.tsx`, y dejar User Management con las pestañas Users e Invitations
- [x] 6.5 Sección MCP server: switch contra `PUT /settings/mcp` y enlace a `/profile#ai-agents`
- [x] 6.5b Sección "AI agents" en Profile (reemplaza a "API key"): API key, endpoint y comando de Claude Code, deshabilitados con el MCP apagado y con el comando con la key real en el diálogo de key nueva; `GET /settings/mcp` para cualquier usuario autenticado, cubierto en `test_mcp.py`. Verificado a mano con el MCP apagado y encendido
- [x] 6.6 Agregar la entrada Instance Settings (`minRole: "admin"`, `mobile: "account"`) a `secondaryNavigationData`, antes de Profile. Verificar que aparece en el sidebar encima de Profile y en el menú de cuenta móvil, y que un `member` no la ve
- [x] 6.7 Verificar con `pnpm check`, `pnpm test` y `pnpm build`, y a mano en la app: como owner, ver las tres secciones y activar y desactivar el MCP; como admin, ver solo Registration; en modo un usuario, ver solo MCP server; en 390px, entrar desde el menú de cuenta

## 7. Documentación y release

- [x] 7.1 Crear `docs/mcp.md`: activación, generación de la key, configuración de Claude Code (`claude mcp add --transport http ... --header "Authorization: Bearer ..."`) y de Claude Desktop (vía `mcp-remote`), lista de tools por rol, formato de ids y la advertencia del modo un usuario. Enlazarlo desde `README.md`
- [x] 7.2 `docs/upgrading.md`: la migración agrega `mcp_enabled` desactivado por defecto
- [x] 7.3 Actualizar `docs/roadmap/01-mcp.md` (estado de `api-keys` y `mcp-server`) y `docs/roadmap/README.md`, y anotar en `docs/roadmap/06-platform-and-resilience.md` que `GET /episodes/stream/status` y `GET /episodes/{anime_id}/{n}/file` no tienen autenticación
- [x] 7.4 Bumpear `VERSION` de 3.1.0 a 3.2.0
- [x] 7.5 Correr `openspec validate mcp-server --strict` y verificar que pasa
