## 1. Inventariar los puntos bloqueantes

Este grupo decide si el resto sale bien: una llamada bloqueante que quede sin clasificar degrada a todos los actores del proceso y no se nota revisando código.

- [ ] 1.1 Enumerar las llamadas a Redis: la construcción del cliente y las dos funciones de flujo en `redis_client.py`, más las de `download.py` (publicación de progreso, decremento del contador, comprobación de existencia, incremento) y las de `order.py` (dos escrituras de clave y un borrado)
- [ ] 1.2 Enumerar las llamadas HTTP: la petición `HEAD` de comprobación de rangos y la descarga por trozos, ambas en `download.py`, más el manejo de su excepción de estado
- [ ] 1.3 Enumerar las esperas y pausas: el `sleep` del reintento por trozo y la lectura de flujo sin límite de tiempo
- [ ] 1.4 Enumerar las operaciones de sistema de archivos de `order.py`: mover, comprobar existencia, crear directorio, recorrer, renombrar y eliminar directorio vacío
- [ ] 1.5 Clasificar cada punto según el criterio del diseño: equivalente asincrónico genuino, delegación a un hilo, o ejecución directa por duración despreciable
- [ ] 1.6 Confirmar que las funciones que solo construyen claves de Redis quedan sincrónicas: son funciones puras sin entrada/salida

## 2. Convertir Redis

- [ ] 2.1 Construir el cliente con la variante asincrónica del paquete `redis` ya instalado, sin agregar dependencias
- [ ] 2.2 Convertir `stream_add_event` y `stream_wait_event` a corrutinas
- [ ] 2.3 Preservar en `stream_wait_event` el criterio de lectura del flujo tal como está, cursor incluido: no avanzarlo ni cambiar desde dónde lee. Corregir su carrera es un change aparte
- [ ] 2.4 Convertir a `await` las llamadas directas al cliente en `download.py` y en `order.py`
- [ ] 2.5 Verificar que el cliente asincrónico queda asociado al event loop en funcionamiento y no a uno inexistente en el momento de su construcción

## 3. Reescribir la descarga sobre un cliente HTTP asincrónico

- [ ] 3.1 Convertir `_server_supports_range` al cliente asincrónico, preservando el tiempo límite y el seguimiento de redirecciones
- [ ] 3.2 Convertir `_download_file` a corrutina con lectura por trozos asincrónica, preservando el tamaño de trozo
- [ ] 3.3 Preservar la detección de soporte de rangos y el cálculo de reanudación desde el byte ya obtenido
- [ ] 3.4 Preservar el descarte del archivo parcial cuando su tamaño es igual o mayor al informado por el servidor
- [ ] 3.5 Preservar el reintento por trozo con su cantidad máxima, cambiando el `sleep` por su equivalente asincrónico
- [ ] 3.6 Preservar el tratamiento de la respuesta de rango no satisfacible: eliminar el archivo parcial y reportar la descarga como fallida
- [ ] 3.7 Preservar la cadencia de las notificaciones de progreso y los valores que informan
- [ ] 3.8 Convertir a `await` la escritura de tamaño a la base y la publicación de progreso que ocurren dentro de la función
- [ ] 3.9 Dejar las escrituras de trozos y las operaciones de metadatos de `download.py` ejecutándose directamente, sin delegar: duran microsegundos y ocurren miles de veces por descarga

## 4. Delegar el sistema de archivos de la reordenación

- [ ] 4.1 Delegar a un hilo las operaciones de `_move_anime_folders`: mover, comprobar existencia, recorrer, renombrar y eliminar el directorio raíz vacío
- [ ] 4.2 Delegar la creación del directorio de la franquicia en `order_franchise_controller`
- [ ] 4.3 Confirmar que el orden relativo de esas operaciones no cambia respecto de la versión actual

## 5. Convertir los actores

- [ ] 5.1 Registrar el middleware que provee el event loop del proceso en la pila del broker, junto al que ya está
- [ ] 5.2 Convertir `download_anime_episode` a `async def` y quitar el `asyncio.run()`
- [ ] 5.3 Convertir `order_franchise_controller` a corrutina y su actor a `async def`
- [ ] 5.4 Quitar el import de `asyncio` de `main.py` si deja de usarse
- [ ] 5.5 Confirmar que no hace falta ningún decorador distinto: el declarador de actores detecta corrutinas por sí solo

## 6. Acceso a la base de datos

- [ ] 6.1 Confirmar si `unify-database-access` está aplicado. Si no lo está, omitir este grupo y dejar el acceso sincrónico delegado a un hilo, anotándolo como deuda
- [ ] 6.2 Si está aplicado: cambiar el engine del worker a su variante asincrónica con la misma cadena de conexión
- [ ] 6.3 Convertir las cuatro funciones de acceso a corrutinas, sin tocar ninguna consulta
- [ ] 6.4 Convertir a `await` sus llamadas en `download.py` y `order.py`

## 7. Dependencias

- [ ] 7.1 En `worker/pyproject.toml`: quitar el cliente HTTP sincrónico y declarar el asincrónico como dependencia directa, que hoy llega solo de forma transitiva
- [ ] 7.2 Ejecutar `uv lock` en `worker/` para mantener el `uv.lock` sincronizado; un lock desfasado rompe el build de Docker, que instala con `--locked`
- [ ] 7.3 Confirmar por búsqueda que no queda ninguna referencia al cliente HTTP sincrónico en `worker/src/`

## 8. Verificar

- [ ] 8.1 Levantar el worker y confirmar que arranca sin el error de event loop ausente
- [ ] 8.2 Descargar un episodio completo y confirmar que el archivo queda íntegro y con los estados publicados esperados
- [ ] 8.3 **Interrumpir una descarga a mitad y relanzarla**, confirmando que se reanuda desde el byte alcanzado y no desde cero. Es la verificación de la lógica más delicada del change
- [ ] 8.4 Ejecutar una reordenación de franquicia y confirmar que los archivos quedan movidos y renombrados correctamente
- [ ] 8.5 Lanzar una descarga de una franquicia mientras su reordenación está en curso, y confirmar que la descarga espera y luego procede
- [ ] 8.6 **Con una descarga larga en curso, confirmar que otro actor del mismo proceso progresa.** Es la comprobación directa de que no quedó trabajo bloqueante sobre el loop compartido
- [ ] 8.7 Confirmar que la cantidad de mensajes procesados en paralelo sigue siendo la misma, para no dar por buena una mejora que el change no produce

## 9. Cerrar

- [ ] 9.1 Anotar en las notas de la versión que el modelo de ejecución del worker cambió, que el paralelismo no aumenta, y que corregir la carrera de la espera de eventos queda pendiente
- [ ] 9.2 Subir la versión de los servicios siguiendo la convención del repositorio de versionarlos en conjunto, ejecutando `uv lock` en cada directorio cuyo `pyproject.toml` cambie
