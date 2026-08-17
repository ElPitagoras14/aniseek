## Why

El worker declara actores sincrónicos y envuelve el controlador de descarga en `asyncio.run()` en cada mensaje, porque los scrapers de `ani-scrapy` son asincrónicos. El propio código lo explica:

```python
# asyncio.run only because the controller drives async scrapers; everything
# else (db, redis, file I/O) is sync and runs directly on the worker thread.
```

Eso crea y destruye un event loop por cada episodio procesado, y deja un servicio que ya ejecuta código asincrónico expresado como si no lo hiciera.

**Conviene ser explícito sobre la magnitud del beneficio: hoy esto no causa ningún problema observable.** Cada mensaje tiene su loop privado, así que el trabajo bloqueante que hay dentro —la descarga, las esperas de Redis, el I/O de disco— no interfiere con nada. Este change no arregla un defecto: reordena el modelo de ejecución. Lo que gana es:

- Un solo event loop por proceso en lugar de uno por mensaje, eliminando el costo de crearlo y destruirlo repetidamente.
- Un modelo de ejecución coherente con el backend, en lugar de código asincrónico disfrazado de sincrónico.
- La base para subir la concurrencia de descargas sin sumar hilos del sistema operativo, que hoy es la única forma de hacerlo.

Y conviene ser igual de explícito sobre lo que **no** gana. Dramatiq bloquea el hilo llamador hasta que la corrutina termina —así lo documenta `async_to_sync`: *"run it on the event loop thread and synchronously wait for its result on the calling thread"*—, de modo que la cantidad de mensajes procesados en paralelo sigue siendo `DRAMATIQ_PROCESSES × DRAMATIQ_THREADS`. Este change por sí solo no aumenta el paralelismo.

Es, entonces, un change de arquitectura sin urgencia. Está capturado para que el análisis no se pierda y para que la decisión de implementarlo pueda tomarse con el costo a la vista.

## What Changes

- **Se registra el middleware `AsyncIO`** que Dramatiq 2.1.0 ya incluye. Levanta un `EventLoopThread` por proceso worker, compartido por todos sus hilos.
- **El actor de descarga pasa a `async def`** y desaparece el `asyncio.run()`. No hace falta un decorador distinto: `Actor.__init__` detecta corrutinas y las envuelve automáticamente.
- **La descarga de archivos pasa a `aiohttp`.** Es el cambio de mayor riesgo del change: `_download_file` concentra la lógica de reanudación por `Range`, la detección de soporte de rangos, el reintento por chunk y el manejo del `416`. `aiohttp` ya está instalado como dependencia transitiva de `ani-scrapy` y pasa a declararse de forma directa; `requests` sale, porque se usa en solo cuatro lugares y todos están en ese archivo.
- **El acceso a Redis pasa a `redis.asyncio`**, que viene dentro del paquete `redis` ya instalado. Son nueve llamadas repartidas en tres archivos, mecánicas, salvo `stream_wait_event`, que hace un `xread(block=0)` —una espera indefinida— y es la que más importa que deje de bloquear el loop compartido.
- **Las operaciones de filesystem se delegan a un hilo.** `shutil.move`, `mkdir`, `iterdir` y `rename` no tienen equivalente asincrónico real en CPython, y envolverlas en una librería que use hilos por debajo no cambiaría nada. Se resuelven explícitamente con `asyncio.to_thread`. Dentro del mismo volumen son operaciones de metadata y duran milisegundos.
- **Las escrituras de chunks a disco se dejan sincrónicas.** No existe I/O de archivos asincrónico nativo en CPython y cada escritura dura microsegundos; delegarla a un hilo costaría más que ejecutarla.

**El motivo por el que todo esto es obligatorio y no opcional:** al pasar de un loop por mensaje a uno por proceso, cualquier llamada bloqueante deja de afectar solo a su propio mensaje y pasa a congelar a todos los actores del proceso. Una descarga de varios minutos detendría el scraping de los demás. Registrar el middleware sin convertir el trabajo bloqueante sería estrictamente peor que la situación actual.

Non-goals: no se cambia la cantidad de procesos ni de hilos de Dramatiq, ni la lógica de reintentos de los actores, ni el acceso a la base de datos —que es responsabilidad de `unify-database-access`—, ni el comportamiento observable de las descargas.

## Capabilities

### New Capabilities

- `worker-execution-model`: cómo el worker ejecuta el trabajo de cada mensaje — cuántos event loops existen y con qué alcance de vida, qué operaciones pueden ejecutarse directamente sobre un loop compartido y cuáles deben delegarse a un hilo, y qué garantías de no interferencia existen entre actores que corren en el mismo proceso.

### Modified Capabilities

<!-- Ninguna. `database-access` gobierna cómo se consulta la base, no cómo se ejecutan los actores. -->

## Impact

- `worker/src/main.py` — se registra el middleware `AsyncIO` y el actor de descarga pasa a `async def`
- `worker/src/tasks/download.py` — `_download_file` y `_server_supports_range` se reescriben sobre `aiohttp`; `time.sleep` del reintento por chunk pasa a `asyncio.sleep`; las llamadas a Redis pasan a `await`
- `worker/src/tasks/order.py` — el controlador pasa a `async def`, las llamadas a Redis a `await` y las operaciones de filesystem se delegan a un hilo
- `worker/src/redis_client.py` — el cliente pasa a `redis.asyncio`; `stream_add_event` y `stream_wait_event` pasan a asincrónicos
- `worker/pyproject.toml` — sale `requests`, entra `aiohttp` como dependencia directa

Dependencia con otros changes:

- Se aplica **después** de `unify-database-access`. Si el acceso a la base ya quedó sobre SQLAlchemy, este change puede además pasar el engine del worker a `create_async_engine`, con la misma `DB_URL` y sin tocar las queries. Hacerlo antes obligaría a resolver dos veces el mismo módulo.

Sin cambios en el backend, el frontend, el esquema de la base ni los contratos de la API.
