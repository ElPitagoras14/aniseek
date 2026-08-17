# worker-execution-model

## Purpose

Gobierna cómo el worker ejecuta el trabajo de cada mensaje: cuántos event loops existen y con qué
alcance de vida, qué puede ejecutarse sobre un loop compartido y qué debe delegarse, y qué
garantías de no interferencia hay entre actores del mismo proceso. No se solapa con
`database-access`, que gobierna cómo se consulta la base.

## Requirements

<!-- Los términos normativos SHALL / SHALL NOT / MUST se mantienen en inglés por ser palabras
     clave de especificación. -->

### Requirement: Existe un event loop por proceso worker, no uno por mensaje

Cada proceso worker SHALL disponer de un único event loop, creado al iniciarse y vivo hasta que el proceso termina. Procesar un mensaje SHALL NOT crear ni destruir un event loop.

#### Scenario: Procesar varios mensajes no crea loops nuevos

- **WHEN** un proceso worker procesa varios mensajes en sucesión
- **THEN** todos se ejecutan sobre el mismo event loop
- **AND** no se crea ni se destruye ninguno entre mensajes

#### Scenario: El loop existe antes del primer mensaje

- **WHEN** el proceso worker termina de iniciarse
- **THEN** su event loop ya está en funcionamiento
- **AND** está disponible para el primer mensaje que llegue

#### Scenario: La ausencia del soporte necesario falla de forma explícita

- **WHEN** se declara un actor asincrónico sin que el proceso disponga de su event loop
- **THEN** el procesamiento del primer mensaje falla con un error que nombra la causa
- **AND** no se produce un fallo silencioso ni un comportamiento degradado

### Requirement: Ninguna operación de duración perceptible se ejecuta sobre el loop compartido

Las operaciones que bloquearían el loop por un tiempo perceptible SHALL ejecutarse de forma asincrónica cuando exista un equivalente asincrónico genuino, y SHALL delegarse a un hilo cuando no exista. Las operaciones cuya duración es del orden de microsegundos MAY ejecutarse directamente sobre el loop.

#### Scenario: Una descarga en curso no detiene a los demás actores

- **WHEN** un actor del proceso está descargando un archivo que tarda minutos
- **AND** otro actor del mismo proceso tiene trabajo pendiente
- **THEN** el segundo actor progresa mientras la descarga continúa

#### Scenario: Una espera de evento no detiene a los demás actores

- **WHEN** un actor está esperando indefinidamente un evento de coordinación
- **AND** otro actor del mismo proceso tiene trabajo pendiente
- **THEN** el segundo actor progresa mientras la espera continúa

#### Scenario: Las operaciones de sistema de archivos se delegan a un hilo

- **WHEN** el worker mueve, crea, recorre o renombra directorios y archivos
- **THEN** esas operaciones se ejecutan fuera del loop compartido
- **AND** el loop queda disponible para las demás tareas mientras se realizan

#### Scenario: Las escrituras de trozos se ejecutan directamente

- **WHEN** el worker escribe un trozo del archivo que descarga
- **THEN** la escritura se ejecuta directamente, sin delegarse
- **AND** su duración no afecta de forma perceptible a las demás tareas

### Requirement: La descarga conserva su comportamiento observable

La conversión del mecanismo de descarga SHALL NOT alterar su comportamiento observable: las mismas decisiones ante las mismas respuestas del servidor y los mismos estados publicados.

#### Scenario: Una descarga interrumpida se reanuda desde donde quedó

- **WHEN** existe un archivo parcial y el servidor admite peticiones por rango
- **THEN** la descarga se reanuda solicitando a partir del byte ya obtenido
- **AND** el contenido previo no se vuelve a descargar

#### Scenario: Un servidor sin soporte de rangos obliga a descargar de nuevo

- **WHEN** el servidor no admite peticiones por rango y no existe archivo parcial
- **THEN** la descarga se realiza completa

#### Scenario: Un archivo local igual o mayor al remoto se descarta

- **WHEN** el archivo parcial es igual o mayor que el tamaño informado por el servidor
- **THEN** se elimina y la descarga comienza desde el principio

#### Scenario: Un trozo que falla se reintenta antes de abandonar

- **WHEN** la escritura de un trozo falla
- **THEN** se reintenta hasta el máximo previsto antes de dar la descarga por fallida

#### Scenario: Un rango no satisfacible descarta el archivo parcial

- **WHEN** el servidor responde que el rango solicitado no es satisfacible
- **THEN** el archivo parcial se elimina
- **AND** la descarga se reporta como fallida para que el reintento del actor la retome

#### Scenario: El progreso se publica con la misma cadencia

- **WHEN** una descarga avanza
- **THEN** se publican notificaciones de progreso con el mismo intervalo que antes
- **AND** informan el tamaño total y el porcentaje alcanzado

### Requirement: La espera de eventos de coordinación conserva su comportamiento observable

La conversión de la espera de eventos SHALL NOT alterar qué eventos la terminan ni cuáles ignora, ni el criterio con el que decide desde qué punto del flujo lee.

#### Scenario: Un evento de otro tipo no termina la espera

- **WHEN** llega un evento cuyo tipo no es el esperado
- **THEN** la espera continúa

#### Scenario: El evento esperado termina la espera

- **WHEN** llega el evento del tipo esperado
- **THEN** la espera termina y el actor continúa su trabajo

#### Scenario: El criterio de lectura del flujo no cambia

- **WHEN** se compara la conversión con la implementación previa
- **THEN** ambas leen el flujo desde el mismo punto de referencia
- **AND** la conversión no introduce ni elimina por su cuenta la posibilidad de no ver un evento

### Requirement: La cantidad de mensajes procesados en paralelo no cambia

El paralelismo SHALL seguir determinado por la configuración de procesos e hilos del worker. Pasar los actores a asincrónicos SHALL NOT alterarlo por sí mismo.

#### Scenario: El paralelismo sigue dependiendo de la configuración

- **WHEN** se procesan mensajes con una configuración dada de procesos e hilos
- **THEN** la cantidad de mensajes atendidos simultáneamente es la misma que antes de la conversión

#### Scenario: Un actor asincrónico ocupa su hilo hasta terminar

- **WHEN** un hilo del worker toma un mensaje cuyo actor es asincrónico
- **THEN** ese hilo queda ocupado hasta que el trabajo del mensaje concluye
- **AND** no toma otro mensaje mientras tanto
