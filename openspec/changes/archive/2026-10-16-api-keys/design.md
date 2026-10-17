## Context

La Fase 0 dejó el modelo de acceso que este change reutiliza:

- `JWTBearer` (`backend/src/packages/auth/middleware.py`) resuelve el usuario desde la base de datos en cada request y lo entrega como un dict `current_user` (`id`, `username`, `isActive`, `role`), armado por `_current_user()`. Con `AUTH_ENABLED=false` corta antes de leer el header y devuelve el owner.
- `require_role` y `ROLE_RANK` (`auth/roles.py`) aplican los permisos por rol sobre ese dict.
- Las invitaciones ya resuelven un problema análogo: token aleatorio (`secrets.token_urlsafe(32)`), guardado como SHA-256 (`hash_invitation_token` en `auth/utils.py`), devuelto una sola vez.
- `api_keys` y `api_scopes` existen desde `0001` sin uso en el código.
- Los tests truncan todas las tablas no preservadas antes de cada prueba (`tests/dbutils.py`), así que una tabla nueva queda cubierta sin tocar esa lista.

La motivación está en `proposal.md`; los requisitos, en `specs/api-keys/spec.md`.

## Goals / Non-Goals

**Goals:**

- Que el change `mcp-server` solo tenga que declarar la dependencia de autenticación por key en sus rutas, sin decidir nada sobre credenciales.
- Que la autenticación por key y la sesión web produzcan el mismo `current_user`, para que `require_role` y los controllers no distingan de dónde vino el usuario.

**Non-Goals:**

- Montar la autenticación por key en endpoints REST existentes.
- Gatear la generación de keys con un switch del MCP: el switch no existe todavía y, según el roadmap, las keys sobreviven a que se apague.

## Decisions

### D1 - Una fila por usuario, con `user_id` como clave primaria

```sql
CREATE TABLE api_keys (
  user_id      UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  prefix       VARCHAR(16) NOT NULL,
  key_hash     CHAR(64) UNIQUE NOT NULL,
  created_at   TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_used_at TIMESTAMP WITH TIME ZONE
);
```

La regla "una key por usuario" queda garantizada por la base de datos, no por el código. Regenerar es un `INSERT ... ON CONFLICT (user_id) DO UPDATE` que reemplaza `prefix`, `key_hash` y `created_at` y pone `last_used_at` en `NULL`: una sola sentencia, así que no hay ventana en la que funcionen las dos keys ni ninguna. Revocar es un `DELETE`.

- **Alternativa:** `id` propio, `revoked_at` e índice único parcial por usuario activo. Da historial, pero el roadmap descartó el historial, y obliga a filtrar revocadas en cada consulta.
- **Sin `expires_at`:** el roadmap no pide vencimiento y una sola key regenerable cubre la rotación. Agregarlo después es una columna nullable, sin romper nada.

### D2 - Formato de la key: `ask_` + 32 bytes aleatorios

`ask_` + `secrets.token_urlsafe(32)`. El prefijo fijo hace reconocible la key en un archivo de configuración o en un escáner de secretos. El `prefix` guardado son los primeros 12 caracteres (`ask_` + 8), suficientes para distinguirla en la UI sin aportar nada útil a quien la vea.

### D3 - SHA-256, compartiendo el helper con las invitaciones

La key tiene 256 bits de entropía: no hay nada que forzar por diccionario, así que un hash lento (bcrypt) solo agregaría latencia a cada request. `hash_invitation_token` pasa a llamarse `hash_secret_token` y lo usan invitaciones y keys. La búsqueda es por igualdad sobre `key_hash` (índice único), sin comparar en Python.

### D4 - Dependencia `ApiKeyBearer`, separada de `JWTBearer`

Una clase nueva en `packages/auth/` basada en `HTTPBearer`, que lee `Authorization: Bearer ask_...`, hashea, busca la fila con un join a `users` y `role_types`, y devuelve `_current_user(user)`. Rechaza con 401 si falta el header, si la key no existe o si el usuario está inactivo.

- **Nunca consulta `AUTH_ENABLED`.** Es la forma de cumplir que la key se exige también en modo un usuario.
- **Bearer y no un header propio (`X-API-Key`):** es lo que los clientes MCP saben enviar por configuración y lo que la especificación MCP asume para HTTP.
- **Separada y no un fallback dentro de `JWTBearer`:** así una key no abre la REST API (requisito "La key no autentica la sesión web") y cada ruta declara explícitamente qué credencial acepta.
- **`require_role` hoy depende de `auth_scheme`.** Para que el MCP pueda aplicar roles sobre un usuario autenticado por key, se separa la comprobación en una función pura (`assert_min_role(current_user, min_role)`) que `require_role` sigue usando. El change `mcp-server` la usará dentro de las tools.

### D5 - `last_used_at` con escritura condicionada

```sql
UPDATE api_keys SET last_used_at = now()
WHERE user_id = :id
  AND (last_used_at IS NULL OR last_used_at < now() - interval '1 minute')
```

Una sesión MCP hace ráfagas de llamadas; sin la condición, cada una sería una escritura. Se ejecuta en la misma conexión que la búsqueda, después de validar.

### D6 - Endpoints bajo `/api-keys`

| Método y ruta | Rol | Respuesta |
|---|---|---|
| `GET /api-keys/me` | `member` | `{prefix, createdAt, lastUsedAt}` o `null` |
| `POST /api-keys/me` | `member` | genera o regenera; `{key, prefix, createdAt}` (única vez que viaja `key`) |
| `DELETE /api-keys/me` | `member` | revoca; 404 si no hay key |
| `GET /api-keys` | `owner` | `{items: [{userId, username, prefix, createdAt, lastUsedAt}], total}` |
| `DELETE /api-keys/{user_id}` | `owner` | revoca la key de ese usuario; 404 si no tiene |

Todos se autentican con la sesión web (`auth_scheme` / `require_role`): gestionar la key es una acción de la UI. Un solo `POST` para generar y regenerar, porque con una key por usuario son la misma operación. El owner puede usar `DELETE /api-keys/{user_id}` sobre sí mismo, equivalente a `DELETE /api-keys/me`.

- **Alternativa:** colgarlos de `/users/me/api-key` y `/users/{id}/api-key`. Se descartó para que el paquete `api_keys` sea autocontenido, igual que `invitations`.

### D7 - UI

- **Perfil:** una sección "API key" junto a usuario y contraseña. Sin key: botón "Generar". Con key: prefijo, creada y último uso, con botones "Regenerar" y "Revocar", ambos con confirmación. Al generar o regenerar, un diálogo muestra la key con botón de copiar y el aviso de que no se volverá a mostrar.
- **Gestión de usuarios (solo owner):** la tabla de usuarios suma una columna "API key" (prefijo y último uso, o "—") y una acción "Revocar API key". Los datos salen de `GET /api-keys`, que se consulta solo si el usuario actual es owner (`useHasRole("owner")`), y se cruzan por `userId`.
- Funciona igual en modo un usuario, donde todas las requests de la UI resuelven al owner.

## Risks / Trade-offs

- [Cualquiera con acceso a la UI en modo un usuario puede generar una key] → Es coherente con lo que ya significa ese modo (red de confianza, la UI entera es del owner). Se documenta en `docs/deployment.md`.
- [La key viaja en cada request] → Igual que el JWT. Se recomienda HTTPS en la documentación del MCP (change `mcp-server`).
- [`last_used_at` tiene precisión de un minuto] → Aceptado en el spec; alcanza para saber si una key está en uso.
- [Borrar `api_keys` y `api_scopes` en la migración] → No hay código que las use; una instancia con filas cargadas a mano las perdería. Se menciona en `docs/upgrading.md`.
- [Hasta que llegue `mcp-server`, la key no sirve para nada visible] → La sección del Perfil lo dice ("para conectar agentes por MCP"). Si se prefiere, el release de este change puede esperar al siguiente.

## Migration Plan

1. Migración `0003_api_keys.sql`: `up` elimina `api_keys` (con su índice) y `api_scopes`, y crea la tabla de D1. `down` elimina la tabla nueva y recrea las dos de `0001` tal como estaban.
2. Regenerar `dbmate/schema.sql`.
3. Despliegue sin pasos manuales: no hay datos que migrar ni variables nuevas.
4. Rollback: `dbmate down` y volver a la imagen anterior. Las keys generadas se pierden, lo cual es aceptable porque nada las consume todavía.
