## 1. Esquema

- [x] 1.1 Crear `dbmate/migrations/0002_users_and_access.sql` con el `up` y el `down` de design D2. Verificar que `dbmate up` y luego `dbmate down` corren sin error contra una base vacía.
- [x] 1.2 Regenerar `dbmate/schema.sql` y verificar que el diff muestre las tablas `instance_settings` e `invitations`, la columna `users.credentials_changed_at` y el índice `uq_users_single_owner`.
- [x] 1.3 Actualizar `backend/tests/test_infra_smoke.py`: el conjunto de roles pasa a `{"owner", "admin", "member"}` y existe una fila en `instance_settings` con `registration_policy = 'invite'`. Agregar `instance_settings` a `PRESERVED_TABLES` en `tests/dbutils.py`. Verificar que la suite pasa.
- [x] 1.4 Agregar un test que inserte dos usuarios con rol `owner` y compruebe que la segunda inserción falla por el índice único.

## 2. Roles por nombre y verificación de rol

- [x] 2.1 Resolver los roles por nombre en el backend: `insert_user` recibe el nombre del rol, y desaparecen `role_id=1` y `role_id=2`. Verificar con `grep` que no quedan ids de rol literales en `backend/src`.
- [x] 2.2 Definir el rango de roles y la dependencia `require_role(min_role)` que lanza `ForbiddenError`. Verificar con tests unitarios de rango (`member` < `admin` < `owner`).
- [x] 2.3 Agregar `assert_can_manage(actor, target)` con las reglas de `user-administration`: el admin solo gestiona members, nadie gestiona al owner ni a sí mismo. Verificar con tests de cada combinación de roles.
- [x] 2.4 Aplicar `require_role("admin")` a `DELETE /episodes/storage/{anime_id}`, `POST /franchises` y `GET /users`, y asegurar que `GET /users` no devuelve hashes. Verificar con tests: 403 para member sin efectos (los archivos y la franquicia no cambian) y éxito para admin y owner.
- [x] 2.5 Agregar el test parametrizado de la matriz de `access-control`: cada endpoint con cada rol, comprobando el 403 o el éxito esperado.

## 3. Sesiones

- [x] 3.1 Hacer que `JWTBearer` rechace con 401 a los usuarios inactivos. Verificar con un test: un token vigente de un usuario desactivado da 401.
- [x] 3.2 Hacer que `refresh_controller` consulte la BD y rechace a los usuarios inexistentes o inactivos. Verificar con un test.
- [x] 3.3 Agregar `iat` a los tokens y rechazar en el middleware y en el refresh los tokens con `iat` anterior a `credentials_changed_at`. Hacer que `PUT /users` (cambio de contraseña propia) actualice ese campo, y comparar truncando `credentials_changed_at` al segundo (design D5). Verificar con tests: el token previo al cambio es rechazado, y el token del login inmediatamente posterior, en el mismo segundo, es aceptado.

## 4. Owner

- [x] 4.1 Agregar `OWNER_USERNAME` y `OWNER_PASSWORD` opcionales a `AuthSettings` y eliminar `ADMIN_USER` y `ADMIN_PASS`. Verificar con `grep` que `admin123` no aparece en `backend/src`.
- [x] 4.2 Reemplazar `_seed_admin_user` por `ensure_owner` (design D3) en el `lifespan`. Verificar con tests de los casos de `instance-owner`:
  - owner existente con variables distintas
  - promoción del admin activo más antiguo, aunque esté renombrado
  - admin más antiguo desactivado (se promueve el siguiente activo)
  - solo admins desactivados (se crea desde el entorno)
  - creación desde el entorno
  - variable ausente, vacía o nombre ocupado (el arranque falla y no se crean usuarios)
- [x] 4.3 Resolver al owner por rol en el modo un usuario de `JWTBearer`. Verificar con un test con `AUTH_ENABLED=false` y el owner renombrado.
- [x] 4.4 Implementar `POST /owner/transfer` con confirmación de contraseña y la transacción de design D8. Verificar con tests: transferencia exitosa, contraseña incorrecta, destinatario inactivo, admin que intenta transferir y atomicidad ante un fallo intermedio (según `backend-testing`).

## 5. Registro e invitaciones

- [x] 5.1 Implementar `GET /settings` y `PUT /settings` (`registration_policy`, solo admin y owner). Verificar con tests: 403 para member y persistencia del valor.
- [x] 5.2 Implementar `GET /auth/registration` público. Verificar con un test sin token que devuelve solo la política.
- [x] 5.3 Implementar `GET`, `POST` y `DELETE /invitations`: token SHA-256 mostrado una sola vez, vencimiento de 7 días por defecto y 30 como máximo, rol `admin` solo para el owner, y el admin restringido a invitaciones de `member`. Verificar con tests de cada límite, y que el listado no expone el token.
- [x] 5.4 Rehacer `POST /auth/register` según la política y con el uso atómico de invitación de design D8. Verificar con tests:
  - `invite` sin token responde 403
  - `open` sin token crea un member
  - con un token válido se crea con el rol de la invitación, con cualquiera de las dos políticas
  - en modo un usuario responde 403 siempre
  - un token usado, vencido o revocado se rechaza
  - un nombre repetido responde 409 y no consume la invitación
  - con dos registros concurrentes, uno solo crea usuario

## 6. Administración de usuarios

- [x] 6.1 Implementar `POST /users` (creación directa con los límites de rol). Verificar con tests: admin crea un member con la política `invite` sin invitación, admin no puede crear un admin y nadie puede crear un owner.
- [x] 6.2 Implementar `PATCH /users/{user_id}`: `is_active` para admin y owner, `role` solo para el owner y solo entre `member` y `admin`. Verificar con tests: el cambio de rol tiene efecto en la siguiente request, el owner está protegido y nadie se desactiva a sí mismo.
- [x] 6.3 Implementar `PUT /users/{user_id}/password`, que actualiza `credentials_changed_at`. Verificar con tests: login con la contraseña nueva, sesiones previas rechazadas y 403 sobre el owner.

## 7. Frontend

- [x] 7.1 Implementar `routes/register.tsx` (formulario con `?invite=`) y mostrar el enlace de registro en `login-header.tsx` solo cuando `GET /auth/registration` informa `open`. Sin token y con la política `invite`, la página explica que hace falta una invitación. Verificar a mano las dos políticas, con y sin enlace de invitación.
- [x] 7.2 Tomar el rol desde `GET /users/me` y actualizar `ROLE_LABELS` para `owner`, `admin` y `member`. Verificar que el perfil muestra la etiqueta correcta para cada rol.
- [x] 7.3 Crear la ruta de administración (usuarios, invitaciones, política de registro), visible solo para admin y owner, y la transferencia de owner, visible solo para el owner. Verificar a mano con un usuario de cada rol, también en la vista móvil.
- [x] 7.4 Agregar el helper de rol del frontend (design D9) y mostrar el botón de borrar de Almacenamiento (`delete-anime-dialog.tsx`) solo a admin y owner. Verificar a mano: un member no ve el botón, y un admin lo ve y puede borrar.
- [x] 7.5 Verificar que `npm run build` y el lint del frontend pasan.

## 8. Despliegue y documentación

- [x] 8.1 Agregar `OWNER_USERNAME` y `OWNER_PASSWORD` a `.env.example`, con un comentario, y pasarlas al servicio de la API en `compose.yaml` como `${OWNER_USERNAME:-}` y `${OWNER_PASSWORD:-}`. En `compose.dev.yaml`, que usa valores literales, reemplazar `ADMIN_USER=admin` y `ADMIN_PASS=admin123` (el código no los lee) por credenciales literales de desarrollo `OWNER_USERNAME` y `OWNER_PASSWORD`. Verificar que `docker compose config` las muestra en ambos archivos, que sin esas variables en el `.env` no aparece la advertencia "variable is not set", y que el entorno de desarrollo arranca desde una base vacía.
- [x] 8.2 Actualizar `README.md`: quitar el aviso de `admin123` y explicar el owner y la política de registro. En `docs/deployment.md`, documentar el síntoma de una instalación nueva sin `OWNER_*`: la API se reinicia en ciclo, la web no arranca, y el error aparece en `docker compose logs aniseek-api`.
- [x] 8.3 Agregar a `docs/upgrading.md` la sección 3.0.0: promoción del admin a owner, registro solo por invitación por defecto, `guest` pasa a `member`, consulta SQL de recuperación del owner y procedimiento de rollback.
- [x] 8.4 Marcar la Fase 0 como en curso en `docs/roadmap/00-users-and-access.md` y anotar la desviación respecto del roadmap: la promoción del admin ocurre al arrancar, no en la migración.

## 9. Cierre

- [x] 9.1 Bumpear `VERSION` de 2.2.0 a 3.0.0.
- [x] 9.2 Probar el despliegue completo con `docker compose up` en dos escenarios: una instalación nueva con `OWNER_*`, y una base existente con el admin sembrado (debe quedar promovido y con la política `invite`).
- [x] 9.3 Correr la suite completa del backend y `openspec validate users-and-access --strict`, y verificar que ambos pasan.
