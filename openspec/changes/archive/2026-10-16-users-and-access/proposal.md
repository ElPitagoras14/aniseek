## Why

Ani Seek tiene roles en la base de datos (`admin`, `member`, `guest`), pero ningún endpoint los aplica: cualquier usuario autenticado puede borrar los archivos globales de un anime o listar a todos los usuarios. El registro está abierto a cualquiera que alcance la instancia, y cada arranque siembra `admin` / `admin123` desde el código. El modo un usuario (`AUTH_ENABLED=false`) no es un modo propio: solo saltea el login y actúa como el usuario `admin`.

Hay que resolverlo ahora porque el MCP (Fase 1 del roadmap, `docs/roadmap/01-mcp.md`) debe ser una función de instancia que solo controla el owner. Antes de exponer una interfaz para agentes tiene que existir un modelo de acceso real.

## What Changes

- **Tres roles: `owner`, `admin` y `member`.** Se agrega `owner` y se elimina `guest`. Los permisos de cada rol quedan definidos en `specs/access-control/spec.md`.
- **Un único owner por instancia:** no se puede borrar, desactivar ni degradar. Puede transferir el rol en una operación atómica.
- **BREAKING (despliegue):** se elimina el seed de `admin` / `admin123`. En una instalación nueva, el owner se crea al arrancar desde `OWNER_USERNAME` y `OWNER_PASSWORD`. Sin owner y sin esas variables, la API no arranca.
- **Actualización de instancias existentes:** al arrancar sin owner, la API promueve a owner al usuario `admin` más antiguo, sin depender de su nombre. Las variables `OWNER_*` solo se usan cuando no hay owner ni admin.
- **Modo un usuario:** con `AUTH_ENABLED=false`, toda request se resuelve como el owner, no como el usuario `admin`.
- **Aplicación de roles en el backend:** los endpoints que modifican o exponen datos globales o de otros usuarios exigen el rol correspondiente y responden 403 si no lo cumple.
- **Usuarios desactivados:** el backend rechaza sus requests y su refresh de token, no solo su login.
- **BREAKING (comportamiento):** política de registro configurable por owner o admin, con dos valores: `invite` (solo con invitación) u `open` (cualquiera se registra como `member`). **`invite` por defecto**, así que el registro libre de hoy deja de funcionar en las instancias actualizadas hasta que se abra la política. Las invitaciones y la creación directa de usuarios funcionan con cualquier política.
- **Invitaciones:** enlaces de un solo uso con rol preasignado y vencimiento. Solo el owner puede invitar o asignar el rol `admin`.
- **Administración de usuarios:** owner y admin pueden listar, crear, desactivar, reactivar, cambiar rol y restablecer contraseña de los usuarios que gestionan. El admin solo gestiona members.
- **Frontend:** página de administración de usuarios, página de registro real (hoy es un stub), y etiquetas de rol para los tres roles.
- **Documentación:** `README.md`, `.env.example`, `compose.yaml`, `docs/deployment.md` y `docs/upgrading.md`.

## Capabilities

### New Capabilities

- `access-control`: los tres roles y qué puede hacer cada uno. Cubre:
  - cómo se identifica al usuario de una request, en modo multiusuario y en modo un usuario
  - el rechazo de usuarios desactivados
  - la matriz de permisos por endpoint y la respuesta ante un permiso insuficiente
- `instance-owner`: ciclo de vida del owner. Cubre:
  - la unicidad del owner
  - su creación al arrancar desde el entorno
  - la promoción en instancias existentes
  - la transferencia del rol
  - las protecciones (no se borra, no se desactiva, no se degrada)
- `user-registration`: cómo se incorpora un usuario nuevo. Cubre:
  - la política de registro y su default
  - el registro abierto
  - las invitaciones (creación, uso, vencimiento, revocación)
  - la consulta pública de la política
- `user-administration`: lo que owner y admin pueden hacer sobre otras cuentas (listar, crear, desactivar, reactivar, cambiar rol, restablecer contraseña) y los límites del admin.

### Modified Capabilities

(ninguna). `database-migrations` ya exige una migración nueva y numerada, junto con el volcado de esquema actualizado, y este change lo respeta. `database-access` ya exige que las operaciones de varias escrituras sean atómicas, lo que aplica a la transferencia de owner y al uso de invitaciones.

## Impact

- **Backend:** `main.py` (startup), `packages/auth/` (`config.py`, `middleware.py`, `service.py`, `repository.py`, `router.py`), `packages/users/`, `packages/episodes/router.py`, `packages/franchises/router.py`. Nuevo módulo de administración de usuarios e invitaciones. `exceptions.py`: `ForbiddenError` pasa a usarse.
- **BD:** migración nueva `0002_*`:
  - agrega el rol `owner` y elimina `guest`
  - `role_types.name` único
  - índice de owner único
  - usuarios `guest` reasignados a `member`
  - tablas `instance_settings` e `invitations`
  - columna `users.credentials_changed_at`

  Además, `dbmate/schema.sql` regenerado.
- **API:**
  - nuevos `GET /auth/registration` (público), endpoints de administración de usuarios e invitaciones, y transferencia de owner
  - cambia `POST /auth/register`, que ahora depende de la política y acepta un token de invitación
  - cambian los permisos de `GET /users`, `DELETE /episodes/storage/{anime_id}` y `POST /franchises`
- **Frontend:** `routes/register.tsx`, nueva ruta de administración, `features/profile/components/profile-info-card.tsx` (`ROLE_LABELS`), navegación según el rol.
- **Tests:** `tests/test_infra_smoke.py` (conjunto de roles), `tests/factories.py`, y tests nuevos de autorización por rol, owner, registro e invitaciones.
- **Despliegue:** nuevas variables `OWNER_USERNAME` y `OWNER_PASSWORD`, obligatorias solo en instalaciones nuevas.
- **Release:** `VERSION` 2.2.0 → 3.0.0, porque es breaking en despliegue y registro.
- **Fuera de alcance:**
  - API keys y scopes (Fase 1)
  - cuotas (Fase 6)
  - autenticación de `GET /episodes/stream/status` y de la descarga pública `GET /episodes/{anime_id}/{episode_number}/file`, que hoy no exigen sesión
  - recuperación de contraseña del owner sin acceso a la UI
