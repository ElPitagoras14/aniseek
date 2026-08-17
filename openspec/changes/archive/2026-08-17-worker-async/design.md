## Context

El worker declara dos actores sincrónicos. El de descarga envuelve su controlador en `asyncio.run()` porque los scrapers de `ani-scrapy` son asincrónicos; el de reordenación es sincrónico de punta a punta.

El trabajo bloqueante que hoy convive con ese `asyncio.run()` es:

- **La descarga del archivo.** `_download_file` usa `requests` con lectura por trozos y puede durar minutos. Dentro llama a `update_episode_size` —una escritura a la base— y a `_notify_job` —una publicación en Redis— en cada intervalo de progreso. Reintenta cada trozo con `time.sleep(1)`.
- **La comprobación de soporte de rangos.** `_server_supports_range` hace una petición `HEAD` con `requests`.
- **Todas las operaciones de Redis.** El cliente es sincrónico. Hay publicaciones, contadores, comprobaciones de existencia y escrituras de claves repartidas entre los dos tasks, más dos funciones de flujo en `redis_client.py`. Una de ellas, `stream_wait_event`, hace `xread(..., block=0)`: una espera sin límite.
- **Las operaciones de filesystem de la reordenación.** `shutil.move`, creación de directorios, recorrido y renombrado.

Dos restricciones enmarcan el diseño:

- **Dramatiq detecta corrutinas por sí solo.** `Actor.__init__` envuelve la función con un adaptador si es una corrutina, de modo que el mismo decorador sirve para actores sincrónicos y asincrónicos. Ese adaptador exige que el middleware `AsyncIO` esté registrado y falla con un mensaje explícito si no lo está.
- **Las librerías asincrónicas de reemplazo ya están instaladas.** `aiohttp` llega como dependencia transitiva de `ani-scrapy`, que la usa para los scrapers. El cliente asincrónico de Redis viene dentro del mismo paquete `redis` que el worker ya declara.

## Goals / Non-Goals

**Goals:**

- Un único event loop por proceso worker, en lugar de uno por mensaje.
- Que ninguna operación bloqueante quede ejecutándose sobre ese loop compartido.
- Que el comportamiento observable de las descargas y de la reordenación no cambie: mismos reintentos, misma reanudación, mismos estados publicados.

**Non-Goals:**

- Aumentar el paralelismo. La cantidad de mensajes procesados a la vez la determina la configuración de procesos e hilos de Dramatiq y este change no la toca.
- Cambiar la lógica de reintentos de los actores ni la política de reanudación de descargas.
- Modificar el acceso a la base de datos más allá de lo que exija la asincronía; su unificación es de `unify-database-access`.

## Decisions

### D1 — Se registra el middleware y los actores pasan a `async def`

Se agrega el middleware `AsyncIO` a la pila del broker y los dos controladores pasan a ser corrutinas. El `asyncio.run()` por mensaje desaparece.

No hace falta un decorador distinto: Dramatiq inspecciona la función al declarar el actor y la adapta si es una corrutina. Olvidar el middleware no produce un fallo silencioso sino un error explícito al procesar el primer mensaje, que además nombra la causa.

### D2 — El loop compartido cambia el contrato, y de ahí se deriva todo lo demás

Hoy cada mensaje tiene su propio loop y muere con él, así que bloquearlo solo afecta a ese mensaje. Con el middleware hay **un loop por proceso**, compartido por todos sus hilos.

Eso convierte cada llamada bloqueante en un problema colectivo: una descarga de varios minutos detendría el scraping de los demás actores del proceso. Por eso las decisiones que siguen no son mejoras opcionales sino condiciones para que D1 no empeore la situación actual.

El criterio que las ordena es único: **si existe un equivalente asincrónico genuino, se usa; si no existe, se delega a un hilo; si el bloqueo dura microsegundos, se deja como está.**

### D3 — La descarga se reescribe sobre un cliente HTTP asincrónico

`_download_file` y `_server_supports_range` pasan a `aiohttp`, que ya está instalado y pasa a declararse como dependencia directa. `requests` sale: se usa en cuatro lugares y todos están en ese archivo. El `time.sleep` del reintento por trozo pasa a su equivalente asincrónico.

*Alternativa considerada y descartada:* delegar `_download_file` a un hilo con la función estándar de asyncio. Parece más barato porque no toca la lógica de descarga, pero rompe algo: la función escribe en la base y publica en Redis desde adentro, y desde un hilo ajeno al loop no puede esperar corrutinas. Habría que sostener un acceso sincrónico a la base en paralelo al asincrónico, o reestructurar la función para que notifique hacia afuera. Convertirla de verdad es más trabajo de escritura y menos complejidad resultante.

Es la parte más delicada del change: ahí viven la detección de soporte de rangos, la reanudación por byte, el reintento por trozo y el tratamiento del `416`. La conversión debe preservar cada uno de esos comportamientos.

### D4 — Redis pasa al cliente asincrónico del mismo paquete

El cliente se construye con la variante asincrónica de `redis`, sin agregar dependencias.

Cambian las funciones que hacen entrada/salida —la escritura de eventos de flujo y la espera— y las llamadas directas repartidas en los dos tasks. **No cambian** las que construyen claves: son funciones puras que devuelven cadenas y volverlas asincrónicas sería ruido.

La que más importa es la espera de eventos: hoy hace una lectura de flujo sin límite de tiempo, que retiene el hilo hasta que llegue el evento. Convertida, esa espera libera el loop para que atienda a los demás actores mientras tanto — que es exactamente lo que el change busca.

### D5 — Solo el filesystem se delega a un hilo

CPython no ofrece entrada/salida de archivos asincrónica real, y las librerías que lo aparentan usan hilos por debajo. Delegarlo explícitamente es más honesto que envolverlo en una capa que hace lo mismo sin decirlo.

Se delegan las operaciones de filesystem de la reordenación: mover, crear directorios, recorrer y renombrar. Dentro del mismo volumen son operaciones de metadatos y duran milisegundos, pero se delegan igual porque el costo de hacerlo es una línea.

**No se delegan las escrituras de trozos del archivo descargado.** Cada una dura microsegundos y ocurre miles de veces por descarga; delegarlas costaría más que ejecutarlas.

### D6 — La espera de eventos se convierte sin corregir su carrera

El bucle que espera eventos de flujo fija su cursor en "solo lo que llegue de ahora en adelante" y nunca lo avanza. Cada iteración vuelve a esperar desde el momento de la llamada, de modo que un evento publicado entre el retorno de una lectura no coincidente y la siguiente llamada no se ve.

La conversión **preserva ese comportamiento exactamente**, cursor incluido. Corregirlo —llevando el cursor al último identificador leído— es un ajuste funcional legítimo, pero mezclarlo con una migración que promete no cambiar comportamiento haría imposible atribuir cualquier problema posterior a una causa u otra. Queda como candidato a un change propio, con la ventaja de que entonces sí sería el único cambio bajo observación.

### D7 — Si el acceso a la base ya es asincrónico, el worker lo adopta

Aplicado `unify-database-access`, el worker queda con un engine sincrónico de SQLAlchemy sobre psycopg3. Con el loop persistente de D1, ese engine puede pasar a su variante asincrónica con la misma cadena de conexión, sin tocar ninguna consulta.

Esto **no era posible antes**: un pool asincrónico atado a un loop que se destruye en cada mensaje no reutilizaría ninguna conexión. Es el loop persistente lo que lo habilita, y es la única ganancia concreta de rendimiento que el change ofrece.

Si `unify-database-access` no estuviera aplicado, este paso se omite y el worker conserva su acceso sincrónico, que desde el loop compartido habría que delegar a un hilo — razón adicional para respetar el orden entre ambos changes.

## Risks / Trade-offs

- **Una sola llamada bloqueante que quede sin convertir degrada a todos los actores del proceso.** → Es el riesgo dominante, y es difícil de detectar revisando código: la llamada olvidada funciona igual que antes, solo que ahora frena a los demás. El inventario de puntos bloqueantes tiene que ser exhaustivo antes de empezar, no descubrirse sobre la marcha.

- **La reescritura de la descarga toca la lógica más delicada del worker.** → Reanudación por rangos, reintento por trozo y tratamiento del `416` son comportamientos que solo se manifiestan ante fallos de red o descargas interrumpidas, es decir, difíciles de ejercitar deliberadamente. Conviene probar al menos una descarga interrumpida y reanudada antes de dar el change por bueno.

- **El worker no tiene pruebas y este change no las agrega.** → `add-backend-testing` cubre el backend. Toda la verificación de este change es manual y funcional. Es una asimetría incómoda en un change que reescribe su función más compleja.

- **El cliente asincrónico de Redis y el loop.** → Construirlo al importar el módulo, antes de que exista el loop, es lo natural dado cómo está escrito hoy. Conviene confirmar que el cliente queda asociado al loop correcto en el primer uso y no a uno inexistente en el momento de la construcción.

- **La conversión ensancha una carrera preexistente en la espera de eventos.** → El bucle de espera mantiene su cursor en "solo lo que llegue de ahora en adelante" y nunca lo avanza, de modo que cualquier evento publicado entre el retorno de una lectura no coincidente y la siguiente llamada se pierde. Hoy esa ventana es de microsegundos porque el bucle vuelve a bloquear de inmediato. Al convertirlo, entre el retorno y la iteración siguiente el loop puede atender a otras tareas, y la ventana se vuelve dependiente de la carga del proceso. La conversión no debe intentar arreglarlo —ver la decisión correspondiente— pero conviene saber que el escenario en que dos descargas de la misma franquicia esperan simultáneamente se vuelve algo más probable de lo que ya era.

- **El change no mejora el rendimiento observable.** → Dramatiq bloquea el hilo llamador hasta que la corrutina termina, así que la cantidad de mensajes simultáneos no cambia. Quien espere más descargas en paralelo tras aplicarlo no las va a ver; lo que gana es un loop por proceso en lugar de uno por mensaje, y la reutilización de conexiones de D6.

## Migration Plan

1. Inventariar exhaustivamente los puntos bloqueantes del worker y clasificarlos según el criterio de D2. Es el paso que decide si el resto sale bien.
2. Convertir el cliente de Redis y sus funciones de entrada/salida (D4), dejando intactas las que construyen claves.
3. Reescribir la descarga sobre el cliente HTTP asincrónico, preservando rangos, reanudación, reintento por trozo y tratamiento del `416` (D3).
4. Delegar a un hilo las operaciones de filesystem de la reordenación (D5).
5. Convertir los dos controladores a corrutinas y registrar el middleware, quitando el `asyncio.run()` (D1).
6. Si `unify-database-access` está aplicado, pasar el engine del worker a su variante asincrónica y las cuatro funciones de acceso a corrutinas (D6).
7. Actualizar dependencias: sale el cliente HTTP sincrónico, entra el asincrónico como directa; sincronizar el archivo de bloqueo.
8. Verificar funcionalmente: una descarga completa, una descarga interrumpida y reanudada, una reordenación de franquicia, y una descarga que espera a que otra termine.
9. Verificar la ausencia de bloqueo: con una descarga larga en curso, confirmar que otro actor del mismo proceso progresa.

**Rollback:** revertir el commit y reconstruir la imagen del worker. No hay estado persistido ni cambio de esquema; los mensajes en cola son compatibles con ambas versiones porque su forma no cambia.

## Open Questions

Ninguna abierta. Las tres se cerraron como decisiones:

- **El cursor de la espera de eventos** pasó a ser D6: se preserva tal cual, y corregir su carrera queda como candidato a un change propio. La interacción con este change está anotada en los riesgos.
- **Pruebas del worker: no en este change.** Una prueba con valor real de la descarga exigiría separar las decisiones —detección de rangos, cálculo de reanudación, política de reintento— de la entrada/salida, o levantar un servidor HTTP de prueba. Lo primero es una reestructuración que se solaparía con la reescritura y volvería imposible distinguir qué cambió por qué; lo segundo es infraestructura equivalente a la de `add-backend-testing`, que fue un change propio precisamente por su tamaño. Extender la capacidad de pruebas al worker queda como candidato a un change propio, y este change compensa con una verificación funcional explícita: además del camino feliz, se ejercitan una descarga interrumpida y reanudada, y una descarga que espera a que otra termine.
- **Configuración de procesos e hilos: fuera de alcance.** Revisarla exige medir el comportamiento con el loop compartido en funcionamiento, lo que solo es posible después de aplicar este change. Decidirlo ahora sería adivinar.
