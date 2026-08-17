## Context

`backend/src/database/client.py` expone hoy un objeto `Database` de `databases` y dos funciones de ciclo de vida que `main.py` invoca al arrancar y al cerrar. Las ~40 funciones de repositorio importan ese objeto global y lo usan sin recibir nada por parámetro: `async def upsert_scraped_anime(values: dict)` ejecuta `await db.execute(query, values)`. Los servicios, en 6 lugares, abren `async with db.transaction():` y dentro llaman a esas funciones, que se suman a la transacción porque `databases` asocia la conexión a la task de asyncio.

`worker/src/db.py` define un `Engine` sincrónico de SQLAlchemy y cuatro funciones equivalentes sobre `conn.execute(text(sql), params)`. No abre transacciones de varias sentencias.

Restricciones que enmarcan el diseño:

- **SQLAlchemy Core no propaga la conexión de forma implícita, y su documentación recomienda no hacerlo:** *"As a general rule, keep the lifecycle of the session separate and external from functions and objects that access and/or manipulate database data."* La convención del stack es que la conexión se reciba por parámetro.
- **No existe infraestructura de pruebas.** Ni en `backend/` ni en `worker/` hay pytest, archivos de test ni configuración; los grupos de dependencias de desarrollo contienen únicamente `isort` y `ruff`.
- **Ambos servicios ya ejecutan SQLAlchemy 2.0.49.** No se incorpora una librería nueva; se retira una capa.
- **El worker es sincrónico y sigue siéndolo.** Su conversión está capturada en `worker-async`.

## Goals / Non-Goals

**Goals:**

- Retirar la dependencia archivada adoptando el modelo explícito que la propia SQLAlchemy recomienda.
- Preservar la atomicidad de las 6 transacciones existentes, ahora visible en cada punto de llamada.
- Que `DB_URL` sea una única cadena válida para el backend asincrónico y el worker sincrónico.
- Que la capacidad del pool de conexiones no cambie de forma accidental.

**Non-Goals:**

- Reescribir queries, cambiar el estilo de parámetros o introducir el ORM.
- Convertir el worker a asincrónico.
- Modificar el esquema o los contratos de la API.
- Corregir el alcance excesivo de la transacción de `update_anime_info`, aunque este change lo vuelva visible.

## Decisions

### D1 — Las funciones de repositorio reciben la conexión por parámetro

Las ~40 funciones de repositorio pasan a tomar la conexión como primer parámetro. Los servicios la abren y la propagan; los routers no la ven.

Es el modelo que SQLAlchemy recomienda y el que hace que la pertenencia a una transacción sea legible en el punto de llamada en vez de depender del stack. Un olvido deja de ser un fallo silencioso: la función no compila conceptualmente sin su conexión, y el type checker lo señala.

**Sin excepciones.** Todas las funciones de acceso reciben conexión, incluidas las que hoy nunca participan de una transacción.

*Alternativa considerada:* reimplementar la propagación implícita con `contextvars`, replicando lo que hace `databases`. Concentra el cambio en un solo archivo y no toca ninguna firma, pero deja el mismo mecanismo ambiental que hoy —invisible en el punto de llamada, con un modo de fallo silencioso— y obliga a mantener código sensible a concurrencia escrito a medida. El patrón ambiental es habitual en la industria (Django, Spring, Rails), pero siempre provisto por un framework, nunca escrito por la aplicación.

*Alternativa considerada:* aceptar la conexión como parámetro opcional solo en las funciones que participan de transacciones. Reduce el número de firmas pero introduce dos caminos dentro de cada función y deja ambiguo cuáles la aceptan; además hay funciones —`insert_dummy_anime`, `insert_anime_relation`— que se llaman tanto dentro como fuera de transacciones, de modo que la ambigüedad no desaparece.

### D2 — El servicio es dueño del ciclo de vida de la conexión

La conexión se abre en la función de servicio, que es el nivel donde la unidad de trabajo tiene sentido, y se cierra al salir de ese bloque. Los repositorios la usan; nunca la crean ni la cierran.

*Alternativa considerada:* proveerla mediante una dependencia de FastAPI, una conexión por request inyectada hacia abajo. Es idiomático en FastAPI, pero mantiene la conexión tomada durante todo el request, y hay al menos un caso —`update_anime_info`— que realiza un scraping de red mientras la transacción está abierta. Atar la conexión al request agravaría el agotamiento del pool en lugar de acotarlo. Además el worker no tiene concepto de request, de modo que necesitaría otro camino igual.

### D3 — Se conservan funciones auxiliares delgadas que toman la conexión

En lugar de que cada repositorio escriba `(await conn.execute(text(sql), params)).mappings().first()`, el módulo de acceso conserva `execute`, `execute_many`, `fetch_one`, `fetch_all` y `fetch_val`, con la conexión como primer parámetro.

Concentra en un solo lugar el envoltorio de `text()` y la forma de los resultados, que hoy los repositorios asumen uniforme (`dict(row)`). Es además la misma forma que ya tiene `worker/src/db.py`, lo que refuerza el objetivo de un idioma común.

### D4 — Lecturas sobre `connect()`, escrituras sobre `begin()`

Fuera de una transacción explícita, las lecturas toman la conexión con `connect()` y las escrituras con `begin()`, que confirma al salir del bloque.

La diferencia importa: `begin()` emite `BEGIN` y `COMMIT` alrededor de cada consulta, y son 47 de los 73 puntos los que solo leen.

### D5 — El ciclo de vida pasa de conectar a verificar

`create_async_engine` no abre conexiones al construirse: el pool se llena bajo demanda. Las dos funciones que `main.py` ya invoca cambian de contenido pero no de rol: al arrancar se ejecuta un `SELECT 1` explícito, para conservar la propiedad actual de que el servicio no arranca si la base no responde; al cerrar se libera el engine.

### D6 — Driver psycopg3 con un único esquema de URL

`DB_URL` pasa a `postgresql+psycopg://`. SQLAlchemy resuelve la variante del dialecto según la función que construye el engine: asincrónica con `create_async_engine`, sincrónica con `create_engine`. La misma cadena sirve para los dos servicios sin traducción.

El worker no cambia código: su `create_engine(DB_URL, ...)` y sus cuatro funciones son Core puro y agnósticas del driver. Solo se reemplaza `psycopg2-binary` por `psycopg[binary]`.

*Alternativa considerada:* mantener `asyncpg`, que es más rápido, obligaría a un esquema distinto por servicio o a traducir la URL en código — la asimetría que el change viene a eliminar. La diferencia de rendimiento no es un factor en una instalación personal autoalojada.

### D7 — La capacidad del pool se traduce de forma explícita

El pool actual se declara como `min_size=5, max_size=20`. SQLAlchemy usa otro modelo: `pool_size` conexiones permanentes más `max_overflow` temporales. La traducción tiene que ser deliberada —`pool_size` 5 con `max_overflow` 15 mantiene el techo de 20— porque adoptar los valores por defecto de SQLAlchemy sin decidirlo cambiaría la capacidad del servicio en silencio.

### D8 — La migración se hace detrás de una red de pruebas escrita antes

Son alrededor de 113 ediciones mecánicas, y una conexión olvidada rompe la atomicidad de ese caso sin producir error. En un repositorio sin ninguna prueba, eso es inaceptable.

Las pruebas de los 6 caminos transaccionales se escriben **antes** de migrar, contra la implementación actual con `databases`. El orden no es un detalle: escritas después, no verificarían el comportamiento previo sino que consagrarían el que produjo la migración, que es exactamente lo que no se quiere.

Cada prueba provoca un fallo en medio de la transacción y comprueba que ninguna de sus escrituras persistió.

*Sobre el alcance:* montar pruebas exige infraestructura que no existe —runner, soporte de asincronía y una base de datos de prueba— y esa infraestructura es útil mucho más allá de este change. Conviene tratarla como un change propio y previo, y no como un apéndice de este.

## Risks / Trade-offs

- **Una conexión olvidada en alguna de las ~113 ediciones rompe la atomicidad de ese caso.** → Es el riesgo dominante, y la razón de D8. A diferencia del enfoque ambiental, el fallo no es invisible: la firma exige el parámetro y el type checker señala la ausencia. Lo que puede pasar desapercibido es pasar una conexión distinta de la de la transacción en curso, y eso es lo que las pruebas de D8 tienen que cubrir.

- **El diff es el más grande del repositorio, en un change cuyo objetivo es no cambiar comportamiento.** → Se acepta a conciencia: es la convención del stack y el modelo que la propia SQLAlchemy recomienda. El tamaño se concentra en cambios mecánicos de firma, no en lógica.

- **Una de las transacciones existentes retiene la conexión durante un scraping de red.** → `update_anime_info` ejecuta `await asyncio.sleep(1.5)` y `await scrape_new_episodes(...)` con la transacción abierta. No es una regresión —hoy ocurre igual— y corregirlo queda fuera de alcance, pero este change lo vuelve **visible**: con la conexión explícita se ve en el código que está tomada mientras se espera a internet. Interactúa además con el dimensionamiento de D7. Buen candidato a un change propio.

- **Cambiar el esquema de `DB_URL` rompe las imágenes anteriores.** → Un despliegue que actualice la variable antes que las imágenes deja al backend viejo con un esquema que `databases` no entiende. Variable e imágenes viajan en el mismo despliegue.

- **psycopg3 y asyncpg no se comportan igual en todos los bordes.** → SQLAlchemy normaliza tipos y parámetros, pero conviene ejercitar las consultas con `ON CONFLICT`, las de `execute_many` y las que devuelven `COUNT` antes de dar el change por bueno.

- **El worker cambia de driver sin cambiar una línea de código.** → Es lo que abarata su lado del change, pero también significa que nada en el repositorio señala el cambio salvo la dependencia. Su verificación tiene que ser funcional.

## Migration Plan

1. Disponer de la infraestructura de pruebas y de las pruebas de los 6 caminos transaccionales, escritas contra la implementación actual y en verde (D8).
2. Reescribir `backend/src/database/client.py`: engine asincrónico, funciones auxiliares con conexión como primer parámetro, ciclo de vida. Eliminar `get_pool_stats` y su export.
3. Migrar las funciones de repositorio archivo por archivo, agregando el parámetro de conexión y actualizando a sus llamadores.
4. Migrar los servicios: abrir la conexión en el nivel de servicio y propagarla; los 6 bloques de transacción pasan a `async with engine.begin() as conn`.
5. Correr las pruebas de D8 y confirmar que siguen en verde.
6. Actualizar dependencias: sale `databases[asyncpg]` del backend y `psycopg2-binary` del worker; entran `sqlalchemy` directa y `psycopg[binary]` en ambos.
7. Cambiar `DB_URL` a `postgresql+psycopg://` en `.env.example` y en los dos archivos de compose.
8. Ejercitar el worker de punta a punta contra psycopg3: encolar una descarga y una reordenación de franquicia.
9. Ejercitar en el backend las rutas con `execute_many` y `ON CONFLICT`.

**Rollback:** revertir el commit y volver a las imágenes anteriores, incluida `DB_URL` con su esquema previo. No hay migración de datos ni cambio de esquema, así que la base sirve a ambas versiones sin conversión.

## Open Questions

- El sembrado del usuario `admin` en `backend/src/main.py` corre dentro del arranque y usa el objeto global. Con el modelo explícito necesita su propia conexión; conviene definir si la abre él mismo o la recibe del ciclo de vida.
- ¿Conviene alinear la restricción de versión de `sqlalchemy` entre backend y worker para que no diverjan?
- ¿Las pruebas de D8 corren contra una base de datos real levantada para la ocasión, o contra una instancia efímera? Es la decisión que define la infraestructura y corresponde al change que la introduzca.
