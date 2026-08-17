## Why

El backend y el worker consultan la misma base de datos, escriben SQL crudo con parámetros con nombre (`:anime_id`) y **ya ejecutan la misma versión de SQLAlchemy 2.0.49 Core**: el worker directamente, el backend de forma transitiva porque `databases` lo declara como dependencia (`Requires-Dist: sqlalchemy (>=2.0.7)`). No hay ORM en ninguno de los dos: no existe un solo `declarative_base`, `sessionmaker`, `Session(` ni `relationship(` en todo el repositorio.

Aun así, cada servicio llega a la base por un camino distinto, y cada camino arrastra un problema propio:

1. **El backend depende de una librería archivada.** `databases` 0.9.0 es una fachada async sobre SQLAlchemy Core, escrita cuando SQLAlchemy no tenía async. SQLAlchemy 2.0 incorporó async de forma nativa y el envoltorio perdió su razón de existir; su repositorio fue archivado el 19 de agosto de 2025 y quedó en solo lectura. El backend arrastra entonces una capa sin mantenimiento sobre una librería que ya tiene instalada y que sabe hacer lo mismo.

2. **El worker usa `psycopg2`**, la generación anterior del driver de PostgreSQL, mientras el backend usa `asyncpg`. Dos drivers distintos contra la misma base obligan a que `DB_URL` signifique cosas distintas según quién la lea, y dejan al worker sin la ruta de actualización que sí tiene psycopg3.

El resultado es que dos servicios que hablan el mismo dialecto de SQL sobre la misma librería lo hacen a través de dos capas y dos drivers distintos, y una de esas capas está archivada.

## What Changes

- **El backend deja de usar `databases` y pasa a `create_async_engine` de SQLAlchemy**, que ya tiene instalado. Los 73 puntos de consulta repartidos en 9 archivos **no se reescriben**: el módulo de acceso conserva las mismas funciones (`execute`, `execute_many`, `fetch_one`, `fetch_all`, `fetch_val`) y las mismas queries.

- **La conexión pasa a viajar por parámetro**, que es el modelo que la propia SQLAlchemy recomienda: *"keep the lifecycle of the session separate and external from functions and objects that access and/or manipulate database data"*. Hoy las ~40 funciones de repositorio no reciben conexión y usan el objeto global; `async with db.transaction():` funciona porque `databases` ata la conexión a la task de asyncio y cualquier consulta posterior se suma a la transacción sin que nadie se la pase. Al retirar esa capa, la pertenencia a una transacción pasa a ser explícita en cada llamada, y un olvido deja de ser un fallo silencioso para volverse un error que el type checker señala.

- **Las pruebas de los caminos transaccionales se escriben antes de migrar**, contra la implementación actual, para que verifiquen el comportamiento previo en vez de consagrar el que produzca la migración. El repositorio no tiene hoy ninguna infraestructura de pruebas, de modo que montarla es requisito de este change y conviene tratarla como un change propio y previo. Sin ese mecanismo, cada consulta tomaría su propia conexión con autocommit y la transacción no envolvería nada — **una pérdida de atomicidad silenciosa, sin error alguno**. Se replica con `contextvars`, en unas pocas decenas de líneas dentro del módulo de acceso.

- **Ambos servicios pasan al driver psycopg3** mediante el esquema `postgresql+psycopg://`. SQLAlchemy elige por sí solo la variante sincrónica o asincrónica del dialecto según con qué función se cree el engine, de modo que `DB_URL` pasa a ser **una sola cadena idéntica para los dos servicios**, sin traducción. El backend la usa con `create_async_engine`; el worker sigue usándola con `create_engine`.

- **El worker no cambia de código.** Su `create_engine(DB_URL, ...)` y sus cuatro funciones de acceso ya son SQLAlchemy Core y son agnósticas del driver: el cambio de dialecto se resuelve enteramente por el esquema de la URL. Solo se reemplaza `psycopg2-binary` por psycopg3 en sus dependencias.

- **Se elimina `get_pool_stats()`**, que está definida y exportada pero no se consume en ningún lado, y que además depende de atributos propios de `databases`.

Non-goals: no se reescribe ninguna query ni se cambia el estilo de parámetros; no se adopta el ORM de SQLAlchemy ni ninguna otra abstracción sobre el SQL; no se modifica el esquema de la base; no se toca la lógica de negocio de ningún servicio.

**El worker sigue siendo sincrónico**, y eso es deliberado. Su actor envuelve el controlador en `asyncio.run()` porque los scrapers de `ani-scrapy` son async, y dentro de ese loop hay trabajo bloqueante pesado: la descarga con `requests` dura minutos y `stream_wait_event` hace un `xread(block=0)` que espera indefinidamente. Hoy eso es inofensivo porque cada mensaje tiene su propio loop privado. Convertir el worker a async exigiría reemplazar `requests` por `aiohttp` y el cliente de Redis por `redis.asyncio` —ambos ya instalados, el primero como dependencia transitiva de `ani-scrapy`— y reescribir la lógica de reanudación por `Range` y reintento por chunk, que es la parte más delicada del servicio. Es un objetivo con entidad propia y riesgo distinto, y va en un change aparte.

## Capabilities

### New Capabilities

- `database-access`: cómo los servicios llegan a la base de datos — qué capa ejecuta las consultas, cómo se expresan y se parametrizan, cómo se delimita una transacción que abarca varias consultas, y cómo se configura la conexión de forma que la misma cadena sirva a un servicio asincrónico y a uno sincrónico.

### Modified Capabilities

<!-- Ninguna. `database-migrations` gobierna cómo evoluciona el esquema, no cómo se lo consulta. -->

## Impact

Backend:

- `backend/src/database/client.py` — se reescribe sobre `create_async_engine`, con las cinco funciones auxiliares tomando la conexión como primer parámetro
- `backend/src/database/__init__.py` — deja de exportar `get_pool_stats`
- `backend/src/main.py` — el ciclo de vida pasa de conectar y desconectar a verificar la conectividad al arrancar y liberar el engine al cerrar
- `backend/pyproject.toml` — sale `databases[asyncpg]`, entran `sqlalchemy` como dependencia directa y el driver psycopg3
- Los 9 archivos con puntos de consulta cambian: ~40 funciones de repositorio suman el parámetro de conexión y sus 73 llamadores lo propagan; los servicios abren la conexión y la pasan hacia abajo. Es el diff más grande del change y es enteramente mecánico

Worker:

- `worker/pyproject.toml` — sale `psycopg2-binary`, entra el driver psycopg3
- Sin cambios en `worker/src/`

Configuración:

- `DB_URL` cambia de esquema a `postgresql+psycopg://` en `.env.example`, `compose.yaml` y `compose.dev.yaml`, con el mismo valor para ambos servicios

Sin cambios en el frontend, en el esquema de la base ni en los contratos de la API.
