## Why

La Fase 1 del roadmap (`docs/roadmap/01-mcp.md`) busca que un agente de IA pueda buscar, organizar y descargar anime a través del Model Context Protocol. El change `api-keys` ya dejó la credencial lista: una key por usuario que hereda su rol. Falta el servidor MCP que la acepte, el switch con el que el owner lo habilita y los tools que exponen el catálogo y las descargas.

## What Changes

- **Servidor MCP en `/api/mcp`**, dentro de la API (sin contenedor nuevo), con transporte Streamable HTTP y sin estado entre requests. No hay stdio en v1; los clientes que solo hablan stdio pueden usar un puente como `mcp-remote`.
- **Switch de instancia `mcp_enabled`, solo para el owner.** Con el MCP apagado, `/api/mcp` responde 404, como si no existiera. Encenderlo o apagarlo tiene efecto en la request siguiente, sin reiniciar. Apagarlo conserva las API keys.
- **Autenticación por API key en cada request MCP**, también en modo un usuario. Cada llamada se ejecuta como el dueño de la key, con su rol actual.
- **Tools de v1**: `search_anime`, `get_anime`, `list_saved`, `list_airing`, `list_downloads`, `get_storage_usage`, `get_stats`, `save_anime`, `unsave_anime`, `refresh_anime`, `download_episodes`, `get_download_status` y `delete_anime_files`. Este último es solo para admin y owner y se anuncia como destructivo. Un rol no ve los tools que no puede usar, y el rol se vuelve a comprobar al ejecutar cada tool.
- **Ids con proveedor** (`animeav1:<slug>`) en todo lo que entra y sale del MCP. La REST API sigue usando el slug solo.
- **`download_episodes` acepta como máximo 25 episodios por llamada.** Un pedido mayor se rechaza entero. Los episodios ya descargados se informan aparte y no cuentan para el tope.
- **Las reglas de negocio pasan de las dependencias de FastAPI al service.** El cooldown de refresco, la existencia del anime y el guardado duplicado quedan en el service, así REST y MCP aplican las mismas reglas. Las respuestas REST no cambian.
- **La descarga masiva informa el motivo de cada fallo** (`already_downloaded`, `not_found`, `enqueue_failed`). En REST es un campo nuevo y opcional, que no rompe a los clientes actuales.
- **Frontend: página Instance Settings propia.** Tiene una entrada en el sidebar encima de Profile (y en el menú de cuenta en móvil) y un menú interno como el de Profile. Reúne la política de registro (admin y owner), el switch del MCP (owner) y la transferencia de ownership (owner). Estas opciones salen de User Management, que queda con Users e Invitations.
- **Docs:** `docs/mcp.md` con la configuración para Claude Desktop y Claude Code.

## Capabilities

### New Capabilities

- `mcp-server`: el servidor MCP de la instancia. Cubre:
  - activación por el owner y respuesta 404 con el MCP apagado
  - autenticación por API key y ejecución con el rol actual del usuario
  - el catálogo de tools, su visibilidad por rol y la comprobación al ejecutar
  - el formato de ids con proveedor
  - el tope y el informe por episodio de `download_episodes`
  - el estado de descarga por episodio
  - las anotaciones de tools destructivos

### Modified Capabilities

- `access-control`: la tabla de permisos suma "Activar y desactivar el MCP de la instancia" con rol mínimo `owner`, y aclara que las operaciones hechas desde el MCP exigen el mismo rol que su equivalente REST.
- `app-navigation`: el menú de cuenta móvil suma Instance Settings y deja explícito User Management, ambos solo para admin y owner.

## Impact

- **Backend:**
  - paquete nuevo `src/mcp_server/` (servidor, tools, traducción de ids, wrapper ASGI). Va al lado de `routes.py` porque es una interfaz, no un dominio de `packages/`. No se llama `mcp` para no tapar al SDK en el `sys.path`
  - montaje en `main.py` y `session_manager.run()` en el `lifespan`
  - `packages/settings/`: lectura de `mcp_enabled` y `PUT /settings/mcp` con `require_role("owner")`
  - `packages/animes/` y `packages/episodes/`: validaciones movidas de `dependencies.py` a `service.py`, `reason` en el resultado de la descarga masiva, y una consulta de estado por anime y episodios
- **BD:** migración nueva que agrega `instance_settings.mcp_enabled BOOLEAN NOT NULL DEFAULT false`. `dbmate/schema.sql` regenerado.
- **API:**
  - `PUT /settings/mcp` (owner)
  - `GET /settings` incluye `mcpEnabled`
  - `/api/mcp` (MCP Streamable HTTP)
  - campo opcional `reason` en `POST /episodes/{anime_id}/download/bulk`
- **Dependencias:** SDK oficial de MCP para Python (`mcp>=2.3,<3`) en `backend/pyproject.toml` y `uv.lock` actualizado.
- **Frontend:**
  - ruta y feature nuevas `/instance-settings` y `features/settings/`
  - layout compartido `components/sectioned-page.tsx`, extraído de Profile
  - `features/root/sidebar-data.ts`
  - `features/user-management/` pierde la pestaña Settings
  - `features/access/api.ts` y `types.ts`
- **Tests:**
  - switch y 404
  - autenticación por key en el MCP, incluido el modo un usuario
  - visibilidad y permisos de tools por rol
  - tope de 25
  - traducción de ids
  - regresión de las validaciones movidas al service
- **Release:** `VERSION` 3.1.0 → 3.2.0.
- **Fuera de alcance:**
  - stdio
  - tools de administración (usuarios, invitaciones, settings)
  - resources y prompts MCP
  - notificaciones de progreso
  - scopes por key
  - rate limiting y cuotas (Fase 6)
  - autenticación de `GET /episodes/stream/status` y `GET /episodes/{anime_id}/{n}/file` (anotado para la Fase 6)
