## Context

Ver `proposal.md` (Why). Estado actual que condiciona el diseño:

- **Roles:** `role_types` (`id SERIAL`, `name`, sin `UNIQUE` en `name`) tiene `admin`=1, `member`=2 y `guest`=3, sembrados en `0001`. `users.role_id` referencia la tabla con `ON DELETE RESTRICT`. El código usa ids fijos: `main.py` siembra con `role_id=1` e `insert_user` usa `role_id=2` por defecto.
- **Middleware:** `JWTBearer` (`auth/middleware.py`) ya relee el usuario y su rol desde la BD en cada request, pero no rechaza a los usuarios inactivos. `refresh_controller` reemite el token a partir del payload sin consultar la BD. Los tokens no llevan `iat`.
- **Modo un usuario:** con `AUTH_ENABLED=false` se busca el usuario por el nombre fijo `admin`.
- **Endpoints sin protección por rol** que cambian de permiso: `GET /users` (lo lista todo, y el frontend no lo usa), `DELETE /episodes/storage/{anime_id}` y `POST /franchises`.
- **Frontend:** `routes/register.tsx` es un stub ("Hello /register!"), y el rol se muestra como etiqueta.
- **Restricciones:** `database-access` exige SQL con parámetros, conexión recibida por parámetro y escrituras múltiples en una sola transacción. `database-migrations` exige una migración numerada nueva y `dbmate/schema.sql` regenerado.

## Goals / Non-Goals

**Goals:**

- Un único punto de verificación de rol que se declare por endpoint y se pueda probar con una matriz.
- Un esquema que garantice en la propia BD las invariantes críticas: un solo owner, política válida, invitación de un solo uso.
- Una actualización sin pasos manuales para las instancias existentes.

**Non-Goals:**

- Roles personalizados o permisos editables desde la UI.
- API keys y scopes (Fase 1), aunque `instance_settings` queda lista para sumar `mcp_enabled`.
- Proteger `GET /episodes/stream/status` y la descarga pública `GET /episodes/{anime_id}/{episode_number}/file`. Los navegadores no envían el header `Authorization` en un `<a href>` ni en `EventSource`, así que hace falta otro mecanismo, como URLs firmadas. Queda para un change propio.
- Recuperar la contraseña del owner sin acceso a la UI.

## Decisions

### D1 - Esquema: roles como catálogo, permisos en código

No hay tabla de permisos. Los tres roles siguen en `role_types`, y la jerarquía y los permisos viven en el backend como un rango: `member` < `admin` < `owner`.

- **Por qué:** los roles son fijos y no hay UI para editarlos. Con una tabla `permissions` / `role_permissions`, cada permiso nuevo exigiría una migración, y el permiso efectivo dejaría de ser legible en el código del endpoint.
- **Alternativa descartada:** RBAC en tablas. Se reconsidera si algún día aparecen roles personalizados.

### D2 - Migración `0002_users_and_access.sql`

```sql
-- migrate:up
ALTER TABLE role_types ADD CONSTRAINT uq_role_types_name UNIQUE (name);
INSERT INTO role_types (name) VALUES ('owner');

UPDATE users SET role_id = (SELECT id FROM role_types WHERE name = 'member')
WHERE role_id = (SELECT id FROM role_types WHERE name = 'guest');
DELETE FROM role_types WHERE name = 'guest';

-- A lo sumo un owner: índice único parcial sobre una expresión constante.
DO $$
BEGIN
  EXECUTE format(
    'CREATE UNIQUE INDEX uq_users_single_owner ON users ((true)) WHERE role_id = %s',
    (SELECT id FROM role_types WHERE name = 'owner')
  );
END $$;

ALTER TABLE users ADD COLUMN credentials_changed_at TIMESTAMP WITH TIME ZONE;

CREATE TABLE instance_settings (
  id BOOLEAN PRIMARY KEY DEFAULT TRUE CHECK (id),
  registration_policy TEXT NOT NULL DEFAULT 'invite'
    CHECK (registration_policy IN ('invite', 'open')),
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO instance_settings DEFAULT VALUES;

CREATE TABLE invitations (
  id UUID PRIMARY KEY,
  token_hash CHAR(64) UNIQUE NOT NULL,
  role_id INTEGER NOT NULL REFERENCES role_types(id) ON DELETE RESTRICT,
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  used_at TIMESTAMP WITH TIME ZONE,
  used_by UUID REFERENCES users(id) ON DELETE SET NULL,
  revoked_at TIMESTAMP WITH TIME ZONE,
  CHECK (used_at IS NULL OR revoked_at IS NULL)
);
CREATE INDEX idx_invitations_pending ON invitations (expires_at)
  WHERE used_at IS NULL AND revoked_at IS NULL;
```

- **`UNIQUE (name)`:** el código pasa a resolver los roles **por nombre**, nunca por id. Se eliminan los `role_id=1` y `role_id=2` hardcodeados.
- **Owner único en la BD:** el índice parcial sobre `(true)` admite a lo sumo una fila que cumpla el predicado. El id del rol se resuelve dentro de la migración porque un índice parcial no puede usar una subconsulta. Alternativas descartadas: una columna `users.is_owner` (duplica el rol y puede desincronizarse) y un trigger (más código para la misma garantía).
- **`instance_settings` como fila única tipada:** con `id BOOLEAN CHECK (id)`. Se prefiere a una tabla clave-valor porque cada ajuste conserva su tipo, su `CHECK` y su default. La Fase 1 agrega `mcp_enabled BOOLEAN NOT NULL DEFAULT FALSE` con otra migración.
- **`invitations`:**
  - `token_hash` es el SHA-256 de un token aleatorio de 32 bytes (`secrets.token_urlsafe`). No hace falta bcrypt, porque el token tiene entropía alta y no lo elige una persona.
  - El rol `owner` en una invitación se rechaza en la aplicación. Un `CHECK` no puede consultar el nombre en otra tabla.
  - Se conservan las invitaciones usadas y revocadas como registro.
- **`credentials_changed_at`:** ver D5.
- **`migrate:down`:** revierte en orden inverso. Borra las tablas y la columna, recrea `guest`, pasa el owner a `admin` y elimina el rol `owner` y el `UNIQUE`. Los usuarios que eran `guest` no se pueden reconstruir y quedan como `member`.

### D3 - Promoción del admin y creación del owner al arrancar

`_seed_admin_user` se reemplaza por `ensure_owner`, que corre en el `lifespan` dentro de una transacción:

1. Si existe un owner, no hace nada.
2. Si no, y existe algún `admin` activo, promueve al activo más antiguo (`WHERE is_active ORDER BY created_at, id`). Un admin desactivado no se promueve, porque la instancia quedaría con un owner que no puede entrar.
3. Si no hay ninguno de los dos, crea el owner desde `OWNER_USERNAME` y `OWNER_PASSWORD`, o falla con un error que nombra la variable. Una variable vacía cuenta como ausente (ver "Arranque fallido").

- **Por qué en el arranque y no en la migración:** es una única ruta de código, idempotente y probable con la suite actual. Una promoción dentro de la migración no se puede probar sin una base a medio migrar, que `backend-testing` no provee. La migración se limita al esquema y a reasignar `guest`, que debe ocurrir antes de borrar el rol.
- **Configuración:** `OWNER_USERNAME` y `OWNER_PASSWORD` se agregan a `AuthSettings` como opcionales. Se eliminan `ADMIN_USER` y `ADMIN_PASS`.
- **Arranque fallido:** `ensure_owner` lanza una excepción en el `lifespan` y uvicorn termina el proceso con un código distinto de cero. En `compose.yaml`, `aniseek-api` tiene `restart: unless-stopped`, así que Docker la reinicia en ciclo, con una espera creciente entre intentos, y el error se repite en `docker compose logs aniseek-api`. Como `aniseek-web` depende de que la API esté `service_healthy`, la web nunca arranca y `docker compose up -d` termina informando que la dependencia falló. `docs/deployment.md` documenta este síntoma y su causa.
- **Variables vacías:** `compose.yaml` pasa el entorno de forma explícita (`- VAR=${VAR}`). Si `OWNER_USERNAME` no está en el `.env`, Compose no la omite: la define vacía y advierte "variable is not set" en cada `up`. Por eso:
  - la API trata un valor vacío como ausente;
  - `compose.yaml` usa `${OWNER_USERNAME:-}` y `${OWNER_PASSWORD:-}`, para que las instancias existentes, que no necesitan estas variables, no vean la advertencia en cada arranque.

### D4 - Verificación de rol

El backend expone una dependencia `require_role(min_role)` que reutiliza `auth_scheme`. Si el rango del usuario es menor que `min_role`, lanza `ForbiddenError` (403). Cada endpoint declara su mínimo en la firma, y la matriz de `access-control` se prueba con tests parametrizados sobre los endpoints.

- **Límites finos:** las reglas que dependen del destinatario (un admin solo gestiona members, nadie gestiona al owner) van en la capa de servicio, porque requieren cargar al usuario objetivo. Se centralizan en una función `assert_can_manage(actor, target)`.
- **Alternativa descartada:** un middleware global con una tabla de rutas. Separa el permiso del endpoint y falla en silencio si una ruta no está en la tabla.

### D5 - Validez de las sesiones

- **Usuarios inactivos:** `JWTBearer` rechaza con 401 a los usuarios con `is_active = false`. `refresh_controller` pasa a consultar la BD y rechaza a los usuarios inexistentes o inactivos.
- **Invalidación por cambio de credenciales:** los tokens incluyen `iat`. Al restablecer o cambiar una contraseña se actualiza `users.credentials_changed_at`, y el middleware y el refresh rechazan los tokens con `iat` anterior a esa fecha.
- **Precisión de la comparación:** `iat` tiene resolución de segundos y `credentials_changed_at` de microsegundos. La comparación trunca `credentials_changed_at` al segundo y rechaza solo si `iat` es estrictamente menor. Así, el token que se emite justo después del cambio, en el mismo segundo, no se rechaza por error. El costo es que un token emitido en ese mismo segundo pero antes del cambio sigue siendo válido: una ventana menor a un segundo, aceptable.
- **Por qué esto y no una lista de tokens revocados:** el middleware ya carga al usuario en cada request, así que la comparación no agrega consultas. Una lista de revocación exigiría almacenamiento y limpieza.

### D6 - Modo un usuario

`JWTBearer` resuelve el usuario con rol `owner` en lugar del nombre `admin`. Como `ensure_owner` garantiza que exista uno, el error "Admin user not seeded" desaparece. En este modo, `POST /auth/register` responde 403 con o sin invitación. `GET /auth/registration` devuelve la política guardada, pero el frontend no muestra login ni registro en este modo, porque ya conoce `AUTH_ENABLED` por su configuración de runtime.

### D7 - Dos valores de política, no tres

Se descartó un valor `closed` que rechazara también las invitaciones. Si un admin crea una invitación es porque quiere que funcione, y "nadie entra" se logra simplemente no creándolas. Con dos valores, la política solo decide si existe el registro sin invitación.

### D8 - Superficie de la API

| Método y ruta | Rol | Notas |
|---|---|---|
| `GET /auth/registration` | público | `{ policy }` |
| `POST /auth/register` | público | Acepta un `invitation_token` opcional. Según la política, responde 403, crea un `member` o crea con el rol de la invitación |
| `GET /users` | admin | Listado sin datos de contraseña. Hoy no lo usa el frontend |
| `POST /users` | admin | Creación directa |
| `PATCH /users/{user_id}` | admin | `is_active` (admin u owner) y `role` (solo owner) |
| `PUT /users/{user_id}/password` | admin | Restablecimiento |
| `PUT /users` | member | Sin cambios (perfil propio). Ahora actualiza `credentials_changed_at` al cambiar la contraseña |
| `GET /invitations`, `POST /invitations`, `DELETE /invitations/{id}` | admin | El admin solo ve y opera invitaciones de `member` |
| `GET /settings`, `PUT /settings` | admin | `registration_policy`. La Fase 1 suma `mcp_enabled`, solo owner |
| `POST /owner/transfer` | owner | `{ target_user_id, current_password }` |

**Uso atómico de una invitación:** en una sola transacción se ejecuta `UPDATE invitations SET used_at = now() WHERE token_hash = :h AND used_at IS NULL AND revoked_at IS NULL AND expires_at > now() RETURNING id, role_id`. Si no devuelve fila, se rechaza. Si devuelve, se inserta el usuario con ese rol y se completa `used_by`. El `UPDATE` bloquea la fila, así que de dos registros simultáneos solo uno la consume, y si falla la inserción (nombre repetido) la invitación no queda consumida.

**Transferencia atómica:** en una sola transacción, primero se pasa al owner actual a `admin` y después al destinatario a `owner`, para que el índice único nunca vea dos owners.

### D9 - Frontend

- **Registro:** `register.tsx` deja de ser un stub. Consulta `GET /auth/registration`, muestra el enlace de registro en `login-header.tsx` solo cuando la política es `open`, y lee el token de invitación desde `?invite=`. Con `invite`, la página de registro solo es útil cuando llega con un token: sin él, explica que hace falta una invitación.
- **Administración:** una ruta nueva, visible solo para admin y owner, con usuarios, invitaciones y política de registro. La transferencia de owner solo aparece para el owner.
- **Rol en la UI:** se toma de `GET /users/me`, no del JWT, porque el rol del token puede quedar desactualizado tras un cambio. La UI solo oculta o muestra, y el backend es quien aplica.
- **Etiquetas:** `ROLE_LABELS` para `owner`, `admin` y `member`.
- **Acciones que el rol no permite:** la interfaz no las ofrece. En Almacenamiento, el botón que abre `DeleteAnimeDialog` (`features/storage/components/delete-anime-dialog.tsx`) solo se muestra a admin y owner, para que un member no llegue a un 403 en un toast. La comprobación de rol en el frontend vive en un único helper que lee el rol de `/users/me`, para que cada nueva acción restringida no repita la lógica.

## Risks / Trade-offs

- **Las instancias actualizadas quedan con registro solo por invitación** → `docs/upgrading.md` lo explica, junto con cómo abrirlo o crear invitaciones.
- **Una instalación nueva sin `OWNER_*` no arranca** → el error nombra las variables, `.env.example` las incluye con un comentario y `compose.yaml` las pasa al servicio de la API.
- **Un owner que pierde su contraseña no tiene recuperación desde la UI** → fuera de alcance. Mientras tanto, `docs/upgrading.md` documenta una consulta SQL manual. Un comando de recuperación puede ser un change aparte.
- **`POST /franchises` pasa a exigir admin**, y un member que hoy agrupa franquicias pierde esa función. Es deliberado, porque las franquicias son catálogo global. El frontend no tiene hoy una llamada a `POST /franchises`.
- **Rol del JWT desactualizado en la UI** → mitigado leyendo el rol desde `/users/me`.
- **`ensure_owner` concurrente** si arrancan varias réplicas de la API → el índice único hace fallar a la segunda inserción. Ese error se trata como "el owner ya existe" y se vuelve a leer.

## Migration Plan

1. **Despliegue:** `aniseek-migrate` aplica `0002` (los roles y las tablas nuevas). Después arranca la API, y `ensure_owner` promueve al admin más antiguo o crea el owner desde el entorno.
2. **Instancias existentes:** no requieren variables nuevas. Hay que revisar la política de registro después de actualizar.
3. **Rollback:** detener la API, `dbmate down` de `0002` y volver a la imagen anterior. Las invitaciones, los ajustes de instancia y el rol `guest` original no se recuperan. Los usuarios siguen existiendo y el owner vuelve a ser `admin`.
4. **Release:** `VERSION` 2.2.0 → 3.0.0 en el mismo PR.
