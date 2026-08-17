## Why

El esquema de la base de datos vive únicamente en `postgres/init.sql`, montado en `/docker-entrypoint-initdb.d/` de la imagen de Postgres. Ese directorio **solo se ejecuta cuando el directorio de datos está vacío**, de modo que en cualquier despliegue que ya arrancó una vez, editar ese archivo no produce ningún efecto.

Lo que vuelve el problema difícil de ver es que los dos modos de arranque se comportan al revés:

- `compose.dev.yaml` no declara ningún volumen persistente para `aniseek-db`: al recrear los containers la base se reconstruye desde cero y `init.sql` vuelve a correr. Los cambios de esquema aparecen.
- `compose.yaml` sí declara `postgres-data`: el directorio nunca vuelve a estar vacío y `init.sql` queda inerte para siempre. Los cambios de esquema no llegan.

Editar el esquema parece funcionar en desarrollo y silenciosamente no llega a producción.

Hoy, para cambiar el esquema en un despliegue real, solo quedan dos caminos: borrar el volumen, perdiendo usuarios, listas guardadas e historial de descargas; o aplicar SQL a mano contra la base viva, sin registro de qué se aplicó. El segundo funciona, pero deja `postgres/init.sql` describiendo un esquema que ya no es el real, y esa deriva crece con cada cambio, en silencio y sin forma de verificarla.

No existe un camino de actualización del esquema. El costo de no tenerlo no es constante: cuanto más se difiera, mayor es la distancia entre el archivo commiteado y la base real, y más caro se vuelve reconciliarlos. El momento más barato para adoptar migraciones es mientras `init.sql` todavía describe fielmente la base.

## What Changes

- Adoptar **dbmate** como herramienta de migraciones. Las migraciones son SQL plano en `db/migrations/` en la raíz del repositorio, no dentro de `backend/` ni de `worker/`: el esquema no pertenece a ningún servicio en particular y los dos lo consumen con stacks distintos —el backend con SQL crudo sobre `databases[asyncpg]`, el worker con SQLAlchemy sobre `psycopg2`—, así que una herramienta externa a ambos evita elegir cuál manda.
- La primera migración contiene el esquema actual tal como está hoy en `postgres/init.sql`, incluidas las tablas, los índices y los datos de referencia que la aplicación necesita para funcionar (`role_types`, `related_types`, `avatars`).
- Marcar esa primera migración como ya aplicada en el despliegue existente, insertando su versión en la tabla `schema_migrations`. dbmate no valida checksums ni reconstruye un grafo de revisiones, así que dar de alta una base preexistente es una única fila.
- Ejecutar las migraciones pendientes antes de que la API quede disponible, de modo que el esquema esté al día en cada arranque sin intervención manual.
- Eliminar `postgres/init.sql` y su montaje en `/docker-entrypoint-initdb.d/` de ambos archivos de compose. Conservarlo lo convertiría en una tercera fuente de verdad contradiciendo a las migraciones y al esquema real.
- Reutilizar `DB_URL` sin introducir una variable nueva: dbmate acepta el scheme `postgresql://` que el proyecto ya usa.

Non-goals: este change no modifica el esquema. No agrega, quita ni altera ninguna tabla, columna, índice ni dato de referencia; solo cambia el mecanismo por el que el esquema llega a la base. Tampoco adopta un ORM ni toca el drift de `.env.example` documentado en otros changes.

## Capabilities

### New Capabilities

- `database-migrations`: cómo evoluciona el esquema de la base de datos — dónde vive la definición, cómo se aplica en un despliegue nuevo y en uno existente, cómo se registra lo ya aplicado, y en qué momento del arranque ocurre respecto de los servicios que dependen de ella.

### Modified Capabilities

<!-- Ninguna. `frontend-delivery` y `frontend-runtime-config` no tienen relación con la base de datos. -->

## Impact

Código afectado:

- `db/migrations/` — nuevo, en la raíz del repositorio
- `db/schema.sql` — nuevo; dbmate lo regenera tras cada migración como representación completa del esquema, apta para revisar en un diff
- `postgres/init.sql` — se elimina, junto con el directorio `postgres/` si queda vacío
- `compose.yaml` y `compose.dev.yaml` — se quita el montaje de `init.sql` en `docker-entrypoint-initdb.d` y se agrega la ejecución de migraciones antes de la API
- `README.md` — las instrucciones de arranque mencionan copiar `postgres/init.sql`, que dejará de existir

Sin cambios en el código de aplicación: ni `backend/src/` ni `worker/src/` necesitan modificarse, porque el esquema resultante es idéntico al actual.

Datos y despliegue:

- El despliegue existente conserva todos sus datos; el baseline no ejecuta SQL, solo registra que la primera migración ya está aplicada.
- Un despliegue nuevo construye el esquema ejecutando las migraciones, sin depender de `docker-entrypoint-initdb.d`.
- El sembrado del usuario `admin` en el arranque de la API (`backend/src/main.py`) es independiente de esto y no cambia.
