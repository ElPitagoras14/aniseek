## Why

El MCP de la Fase 1 (`docs/roadmap/01-mcp.md`) necesita que un agente se identifique como un usuario concreto, porque la lista de guardados y el historial de descargas son por usuario. Los JWT de la sesión web no sirven para eso: vencen en minutos y en modo un usuario ni siquiera existen. Hace falta una credencial de larga duración, ligada a un usuario, que se pueda revocar.

Las tablas `api_keys` y `api_scopes` de la migración `0001` no sirven tal como están: guardan la key en claro, no tienen forma de vincular scopes y ningún código las usa. Este change las reemplaza y deja lista la autenticación por API key antes de montar el MCP, que llega en el change siguiente (`mcp-server`).

## What Changes

- **Una API key por usuario.** Cada usuario puede generar su key, regenerarla (la anterior deja de funcionar en el acto) y revocarla. La key completa se muestra una sola vez; solo se guarda su hash SHA-256 y un prefijo visible para reconocerla.
- **La key hereda el rol actual del usuario.** No tiene permisos propios ni scopes: en cada uso se resuelve el usuario y su rol desde la base de datos. Un cambio de rol o una desactivación tienen efecto en el uso siguiente.
- **El owner ve y revoca las keys de todos.** Puede listar qué usuarios tienen key, con su prefijo y su último uso, y revocar cualquiera.
- **Autenticación por API key en el backend**, como dependencia reutilizable que produce el mismo usuario de request que la sesión web. Exige la key también en modo un usuario: no pasa por el atajo que resuelve toda request como el owner.
- **La key no autentica la REST API.** Solo la usará el MCP. Este change deja la dependencia lista y probada, sin montarla en ningún endpoint existente.
- **BREAKING (esquema):** migración nueva que elimina `api_keys` y `api_scopes` y crea `api_keys` desde cero. No hay datos que preservar porque ningún código las usaba.
- **Frontend:** sección "API key" en el Perfil (generar, regenerar, revocar, copiar la key recién creada) y columna de API key con acción de revocar, solo para el owner, en Gestión de usuarios.

## Capabilities

### New Capabilities

- `api-keys`: ciclo de vida de la API key de un usuario y su uso como credencial. Cubre:
  - generación, regeneración y revocación por el propio usuario
  - almacenamiento con hash y prefijo visible, y que la key se muestra una sola vez
  - listado y revocación por el owner
  - autenticación por key: resolución del usuario y su rol actual, rechazo de keys inválidas, revocadas o de usuarios desactivados, y que también se exige en modo un usuario
  - registro del último uso

### Modified Capabilities

- `access-control`: la tabla de permisos por operación suma las operaciones de API key (gestionar la propia: `member`; listar y revocar las de otros: `owner`).

## Impact

- **Backend:** paquete nuevo `packages/api_keys/` (router, service, repository, schemas) registrado en `routes.py` bajo `/api-keys`. Dependencia de autenticación por key en `packages/auth/`. `auth/utils.py`: el helper SHA-256 de invitaciones pasa a ser genérico y lo comparten ambos.
- **BD:** migración nueva `0003_*` que reemplaza `api_keys` y elimina `api_scopes`. `dbmate/schema.sql` regenerado.
- **API:** `GET/POST/DELETE /api-keys/me` (cualquier usuario) y `GET /api-keys`, `DELETE /api-keys/{user_id}` (owner).
- **Frontend:** `features/profile/` (sección nueva), `features/user-management/components/users-tab.tsx` (columna y acción), `features/access/api.ts` y `types.ts`.
- **Tests:** tests nuevos de ciclo de vida, permisos del owner y autenticación por key, incluido el modo un usuario. La tabla nueva queda cubierta por la limpieza entre tests sin cambios en `tests/dbutils.py`.
- **Release:** `VERSION` 3.0.0 → 3.1.0. El cambio de esquema no afecta a nadie porque las tablas no se usaban.
- **Fuera de alcance:**
  - el MCP, el switch `mcp_enabled` y cualquier endpoint que acepte la key (change `mcp-server`)
  - scopes o restricciones por key por debajo del rol
  - vencimiento de keys y más de una key por usuario
  - rate limiting (Fase 6)
