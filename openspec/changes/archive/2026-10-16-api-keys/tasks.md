## 1. Esquema

- [x] 1.1 Crear `dbmate/migrations/0003_api_keys.sql`: `up` elimina `api_keys` (con `idx_api_keys_expired`) y `api_scopes` y crea la tabla de D1; `down` elimina la nueva y recrea las dos de `0001` tal como estaban. Verificar con `dbmate up`, `dbmate down` y `dbmate up` sobre la base de desarrollo sin errores
- [x] 1.2 Regenerar `dbmate/schema.sql` y verificar que contiene la tabla nueva y ya no contiene `api_scopes`

## 2. Autenticación por key

- [x] 2.1 Renombrar `hash_invitation_token` a `hash_secret_token` en `auth/utils.py` y actualizar `invitations/service.py` y `auth/service.py`; verificar que `test_registration.py` sigue pasando
- [x] 2.2 Extraer de `require_role` una función pura `assert_min_role(current_user, min_role)` en `auth/roles.py`, que `require_role` siga usando; verificar que `test_access_control.py` sigue pasando
- [x] 2.3 Agregar al repositorio de auth la búsqueda de usuario por `key_hash` (join a `users` y `role_types`) y el `UPDATE` condicionado de `last_used_at` (D5)
- [x] 2.4 Implementar `ApiKeyBearer` en `packages/auth/` (D4): Bearer, hash, búsqueda, 401 por header ausente, key inexistente o usuario inactivo, `_current_user()`, sin consultar `AUTH_ENABLED`; exportarlo desde `packages/auth/__init__.py`

## 3. Endpoints de gestión

- [x] 3.1 Crear `packages/api_keys/` (repository, service, schemas, router) con los cinco endpoints de D6 y registrarlo en `routes.py` bajo `/api-keys`; verificar que aparecen en `/docs`
- [x] 3.2 Generar y regenerar con un solo `INSERT ... ON CONFLICT (user_id) DO UPDATE` (D1, D2), devolviendo la key completa solo en esa respuesta, y loguear generación y revocación sin la key

## 4. Tests de backend

- [x] 4.1 `tests/test_api_keys.py`, ciclo de vida: sin key, generar, la respuesta trae la key y la consulta no, la key no aparece en la tabla, regenerar invalida la anterior y valida la nueva, revocar, revocar sin key da 404
- [x] 4.2 Permisos del owner: lista sin key completa, revoca la de un member; admin y member reciben 403 al listar y al revocar ajenas
- [x] 4.3 Autenticación por key con una ruta de prueba que declare `ApiKeyBearer` (app FastAPI mínima en el test): key válida resuelve usuario y rol, sin key y key inexistente dan 401, usuario desactivado da 401 y reactivado vuelve a autenticar, cambio de rol con efecto inmediato vía `assert_min_role`, `last_used_at` se llena en el primer uso y no se reescribe dentro del minuto
- [x] 4.4 Modo un usuario (`auth_settings.AUTH_ENABLED=False`): la ruta con `ApiKeyBearer` da 401 sin key y resuelve al owner con su key; con autenticación habilitada, un endpoint protegido por sesión rechaza una API key con 401
- [x] 4.5 Correr la suite completa del backend (`uv run pytest`) y verificar que pasa

## 5. Frontend

- [x] 5.1 Tipos y funciones en `features/access/` (`types.ts`, `api.ts`): query de la key propia, generar o regenerar, revocar, listado del owner y revocación por usuario
- [x] 5.2 Sección "API key" en el Perfil (D7): estados sin key y con key, confirmación para regenerar y revocar, diálogo que muestra la key una vez con botón de copiar
- [x] 5.3 Columna "API key" y acción "Revocar API key" en `users-tab.tsx`, visibles solo para el owner y alimentadas por `GET /api-keys`
- [x] 5.4 Verificar con `pnpm check`, `pnpm test` y `pnpm build`, y probar a mano en la app: generar, copiar, regenerar y revocar desde el Perfil, y revocar desde Gestión de usuarios como owner
- [x] 5.5 Rediseñar el Perfil con las secciones Cuenta, Seguridad y API key una debajo de otra y un menú interno fijo que hace scroll a cada una (enlazable con `#api-key`), quitar la tarjeta de información duplicada y ocultar Seguridad en modo un usuario; verificar con `pnpm check`, `pnpm build` y a mano en la app

## 6. Documentación y release

- [x] 6.1 `docs/upgrading.md`: la migración elimina `api_keys` y `api_scopes` (sin uso previo). `docs/deployment.md`: en modo un usuario cualquiera con acceso a la UI puede generar la key del owner
- [x] 6.2 Actualizar `docs/roadmap/01-mcp.md` con el estado del change y bumpear `VERSION` de 3.0.0 a 3.1.0
- [x] 6.3 Correr `openspec validate api-keys --strict` y verificar que pasa
