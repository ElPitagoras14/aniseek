# Bandera para lógica de autenticación

Carpeta de contexto @backend/src

He creado una variable de entorno booleana `AUTH_ENABLED` para activar/desactivar la lógica de autenticación.

## Valor False

Si `AUTH_ENABLED=false` en el entorno, el middleware asume un usuario owner fijo. Debe crear un usuario con el username `admin` y el password `admin123` de forma dummy.

Se debe deshabilitar la lógica de autenticación en todos los endpoints o utilizar siempre este usuario en caso de que no exista un token en la petición o usar un token que no expire.

## Valor True

Si `AUTH_ENABLED=true` en el entorno, el middleware asume que la lógica de autenticación está activada y el comportamiento es como está actualmente el código.

Poner los resultados obtenidos a este documento.

## Resultados

### Archivos modificados

| Archivo | Cambio |
|---|---|
| `backend/src/packages/auth/config.py` | +3 campos: `AUTH_ENABLED: bool = True`, `ADMIN_USER: str = "admin"`, `ADMIN_PASS: str = "admin123"` |
| `backend/src/packages/auth/middleware.py` | `JWTBearer.__call__` cortocircuita con usuario admin cuando `AUTH_ENABLED=False` |
| `backend/src/main.py` | Función `_seed_admin_user()` llamada en `lifespan` cuando `AUTH_ENABLED=False` |
| `.env.example` | Añadida línea `AUTH_ENABLED=true` junto a las credenciales admin |

### Comportamiento implementado

**AUTH_ENABLED=false:**
- Al arrancar, el lifespan crea el usuario `admin`/`admin123` con `role_id=1` (admin) si no existe.
- Cada petición a cualquier endpoint protegido retorna el usuario `admin` sin validar token. No se requiere header `Authorization`.
- Si se envía un token (válido o inválido) es ignorado por completo.

**AUTH_ENABLED=true (default):**
- Comportamiento original inalterado. Se requiere `Authorization: Bearer <token>` válido.
- El seeder no se ejecuta al arrancar.

### Notas

- **Mapeo owner → admin**: el task menciona "usuario owner fijo"; se mapeó al rol `admin` (id=1 en `role_types`), el de mayor privilegio disponible.
- **Default seguro**: `AUTH_ENABLED=True` por defecto — si la variable no existe en `.env`, la autenticación permanece activa.
- **Punto de control único**: el bypass está en `JWTBearer` (singleton `auth_scheme`). No fue necesario tocar ningún router ni endpoint individual.