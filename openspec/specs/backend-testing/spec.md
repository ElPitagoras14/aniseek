# backend-testing

## Purpose

Gobierna cómo se verifica automáticamente el comportamiento del backend: qué se ejecuta, contra qué
base de datos, cómo se aísla una prueba de otra, y qué garantías debe poder comprobar una prueba que
no son observables leyendo el código ni usando la aplicación.

## Requirements

<!-- Los términos normativos SHALL / SHALL NOT / MUST se mantienen en inglés por ser palabras
     clave de especificación. -->

### Requirement: La suite se ejecuta con un solo comando

Ejecutar las pruebas SHALL requerir un único comando, sin pasos manuales previos de preparación de servicios ni de datos. La suite SHALL provisionar por sí misma todo lo que necesita y liberarlo al terminar.

#### Scenario: Una ejecución desde cero no requiere preparación

- **WHEN** se ejecuta el comando de pruebas sin haber levantado ningún servicio antes
- **THEN** la base de datos de prueba queda disponible, con su esquema creado
- **AND** las pruebas se ejecutan sin intervención

#### Scenario: Los recursos se liberan al terminar

- **WHEN** la ejecución de la suite finaliza, con éxito o con fallos
- **THEN** la base de datos de prueba se descarta
- **AND** no queda ningún servicio en ejecución atribuible a la suite

### Requirement: Las pruebas corren contra PostgreSQL real con el esquema de producción

La base de datos de prueba SHALL ser PostgreSQL de la misma versión mayor que la de producción, y su esquema SHALL construirse a partir del mismo artefacto que construye el de producción. No SHALL usarse un motor sustituto.

#### Scenario: El esquema proviene de la fuente canónica

- **WHEN** se provisiona la base de prueba
- **THEN** su esquema se crea aplicando el mismo artefacto que se aplica en un despliegue nuevo
- **AND** cambiar esa fuente requiere modificar un único punto de la infraestructura de pruebas

#### Scenario: La semántica específica del motor se preserva

- **WHEN** una prueba ejercita una consulta con `ON CONFLICT ... DO UPDATE`, `EXCLUDED` o columnas `UUID`
- **THEN** se comporta igual que en producción
- **AND** el resultado no depende de una emulación

#### Scenario: Los datos de referencia están disponibles

- **WHEN** una prueba necesita un rol, un tipo de relación o un avatar
- **THEN** esos datos existen en la base de prueba, sembrados junto con el esquema

### Requirement: Cada prueba parte de un estado conocido sin envolverse en una transacción

El aislamiento entre pruebas SHALL lograrse vaciando los datos mutables entre una y otra. **NO SHALL** implementarse abriendo una transacción alrededor de cada prueba y revirtiéndola, porque eso degradaría a savepoint la transacción del código bajo prueba y volvería inobservable la propiedad que la suite existe para verificar.

#### Scenario: Una prueba no ve lo que escribió la anterior

- **WHEN** una prueba escribe filas y termina
- **AND** se ejecuta la prueba siguiente
- **THEN** esas filas no están presentes

#### Scenario: La transacción del código bajo prueba es de primer nivel

- **WHEN** el código bajo prueba abre una transacción
- **THEN** es una transacción de primer nivel y no un punto de guardado anidado
- **AND** revertirla deshace efectivamente sus escrituras

#### Scenario: Los datos de referencia sobreviven al vaciado

- **WHEN** se vacían los datos mutables entre pruebas
- **THEN** las tablas de referencia y la de control de migraciones conservan su contenido

#### Scenario: Una tabla nueva queda cubierta sin tocar la infraestructura

- **WHEN** se agrega una tabla al esquema
- **THEN** el vaciado entre pruebas la incluye automáticamente
- **AND** solo la incorporación de datos de referencia nuevos exige declararlo explícitamente

### Requirement: La atomicidad de las operaciones de varias sentencias es verificable

La suite SHALL poder comprobar, para cada operación que abarca varias escrituras, que un fallo intermedio no deja ninguna de ellas confirmada. SHALL comprobar también el caso sin fallo, para que una implementación que nunca confirmara nada no pasara inadvertida.

#### Scenario: Un fallo intermedio no deja escrituras parciales

- **WHEN** una operación de varias escrituras falla después de la primera
- **THEN** ninguna de sus escrituras está presente en la base

#### Scenario: Sin fallo, todas las escrituras persisten

- **WHEN** la misma operación se ejecuta sin provocar ningún fallo
- **THEN** todas sus escrituras están presentes en la base

#### Scenario: El fallo se provoca sin depender del esquema

- **WHEN** una prueba necesita interrumpir una operación a mitad
- **THEN** lo consigue sustituyendo una de las funciones que la operación invoca
- **AND** no depende de violar una restricción concreta, que cambiaría con el esquema

#### Scenario: Una operación que captura sus propios fallos también se verifica

- **WHEN** la operación bajo prueba captura la excepción en lugar de propagarla
- **THEN** la prueba comprueba que la operación continúa y registra el elemento como fallido
- **AND** comprueba igualmente que ninguna escritura de ese elemento persistió

### Requirement: Las pruebas no dependen de servicios externos ni producen efectos fuera de la base

Ninguna prueba SHALL requerir servicios más allá de su propia base de datos, ni SHALL producir efectos observables fuera de ella.

#### Scenario: Encolar trabajo no publica mensajes reales

- **WHEN** una prueba ejercita un camino que encola una tarea en la cola de trabajo
- **THEN** no se publica ningún mensaje real
- **AND** la prueba no requiere que la cola esté disponible

#### Scenario: Un camino que consulta sitios externos no sale a la red

- **WHEN** una prueba ejercita un camino que obtiene datos de un sitio externo
- **THEN** no se emite ninguna petición de red

### Requirement: Las pruebas y sus dependencias quedan fuera de la imagen de producción

Ni los archivos de prueba ni las dependencias que solo ellas necesitan SHALL formar parte de la imagen que se despliega.

#### Scenario: La imagen no contiene las pruebas

- **WHEN** se construye la imagen del backend
- **THEN** no incluye el directorio de pruebas

#### Scenario: La imagen no contiene las dependencias de prueba

- **WHEN** se construye la imagen del backend
- **THEN** el entorno resultante no contiene el runner de pruebas ni las librerías que solo ellas usan
