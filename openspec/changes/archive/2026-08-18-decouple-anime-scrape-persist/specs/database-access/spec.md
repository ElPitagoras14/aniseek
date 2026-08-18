## ADDED Requirements

### Requirement: La conexión no permanece abierta durante I/O externo ajeno a la base de datos

Una vez abierta una transacción, SHALL NOT permanecer abierta mientras se espera una respuesta de un sistema externo (por ejemplo, una petición HTTP a un sitio de terceros) ni mientras transcurre una espera deliberada (por ejemplo, una pausa para respetar un rate limit). Todo dato que dependa de un sistema externo SHALL obtenerse antes de abrir la transacción que lo persiste.

#### Scenario: El resultado de una llamada externa se obtiene antes de abrir la transacción

- **WHEN** una operación necesita datos obtenidos de un sistema externo para completar sus escrituras
- **THEN** esos datos se obtienen antes de abrir la transacción de escritura
- **AND** la transacción, una vez abierta, no espera ninguna respuesta externa

#### Scenario: Una espera deliberada ocurre fuera de cualquier transacción abierta

- **WHEN** una operación necesita una pausa deliberada (por ejemplo, para respetar el rate limit de un sitio externo)
- **THEN** esa pausa transcurre sin ninguna transacción abierta
- **AND** ninguna conexión del pool queda retenida durante esa pausa

#### Scenario: La transacción abierta solo contiene operaciones de base de datos

- **WHEN** se inspecciona el código dentro de un bloque de transacción
- **THEN** todas las llamadas dentro de ese bloque son operaciones de lectura o escritura sobre la base de datos
- **AND** ninguna es una llamada de red externa ni una espera artificial
