## ADDED Requirements

<!-- Capability nueva. Gobierna cómo evoluciona el esquema de la base de datos: dónde se define,
     cómo se aplica, cómo se registra lo aplicado y en qué momento del arranque ocurre.
     Los términos normativos SHALL / SHALL NOT / MUST se mantienen en inglés por ser palabras
     clave de especificación. -->

### Requirement: El esquema se define exclusivamente en migraciones versionadas

El esquema de la base de datos SHALL estar definido en archivos de migración versionados bajo `db/migrations/`, en la raíz del repositorio. No SHALL existir ningún otro mecanismo que cree o modifique el esquema durante el despliegue.

#### Scenario: Una base nueva se construye desde las migraciones

- **WHEN** se levanta el sistema contra una base de datos vacía
- **THEN** el esquema completo queda creado aplicando las migraciones en orden
- **AND** los datos de referencia que la aplicación necesita para funcionar quedan sembrados

#### Scenario: No queda ningún mecanismo de creación alternativo

- **WHEN** se inspecciona el repositorio y los archivos de compose
- **THEN** no existe ningún archivo de inicialización de esquema fuera de `db/migrations/`
- **AND** ningún servicio monta archivos en el directorio de inicialización de la imagen de Postgres

#### Scenario: Un cambio de esquema llega a un despliegue con datos

- **WHEN** se agrega una migración y se actualiza un despliegue cuya base ya contiene datos
- **THEN** el cambio se aplica sobre la base existente
- **AND** no se requiere borrar el volumen ni ejecutar SQL a mano

### Requirement: Las migraciones se identifican por un número secuencial

Cada migración SHALL nombrarse `NNNN_descripción.sql`, con el número rellenado con ceros a cuatro dígitos. La versión registrada SHALL ser ese número. Las migraciones SHALL aplicarse en orden ascendente de versión.

#### Scenario: El nombre declara la versión

- **WHEN** se registra una migración como aplicada
- **THEN** lo que queda almacenado es el número inicial del nombre del archivo, sin la descripción

#### Scenario: El relleno con ceros preserva el orden

- **WHEN** existen migraciones cuyos números tienen distinta cantidad de dígitos significativos
- **THEN** el relleno a cuatro dígitos hace que el orden textual coincida con el numérico
- **AND** la migración `0010` se aplica después de la `0009`

#### Scenario: El número de una migración aplicada no cambia

- **WHEN** se renombra la parte descriptiva de una migración ya aplicada
- **THEN** su estado de aplicación no se altera

#### Scenario: Cada migración declara ambas secciones

- **WHEN** se inspecciona cualquier archivo de migración
- **THEN** contiene las marcas de aplicación y de reversión, aunque alguna quede sin instrucciones

#### Scenario: La migración inicial no es reversible

- **WHEN** se inspecciona la sección de reversión de la migración inicial
- **THEN** está vacía a propósito, de modo que revertirla no destruye el esquema completo

### Requirement: Los servicios arrancan con el esquema al día

Las migraciones pendientes SHALL aplicarse antes de que la API y el worker queden operativos. Ambos servicios SHALL esperar a que ese paso termine con éxito, no solamente a que la base de datos responda.

#### Scenario: El orden de arranque es base, migraciones, servicios

- **WHEN** se levanta el sistema
- **THEN** el paso de migración espera a que la base de datos esté sana antes de correr
- **AND** la API y el worker esperan a que el paso de migración haya terminado con éxito

#### Scenario: Un fallo en las migraciones detiene el arranque

- **WHEN** el paso de migración termina con error
- **THEN** ni la API ni el worker arrancan
- **AND** el error queda visible en los logs como un paso propio, no escondido dentro de otro servicio

#### Scenario: El paso de migración termina y no se reinicia

- **WHEN** el paso de migración aplica lo pendiente y finaliza correctamente
- **THEN** el proceso termina y no vuelve a lanzarse
- **AND** su finalización no se interpreta como una caída que deba reintentarse

#### Scenario: El worker no consulta tablas inexistentes

- **WHEN** el worker arranca en un despliegue nuevo
- **THEN** el esquema ya está creado
- **AND** no depende de que la API haya arrancado antes

### Requirement: Un despliegue existente se incorpora sin perder datos ni recrear el esquema

Dar de alta una base preexistente SHALL consistir en registrar como aplicadas las migraciones que su esquema ya refleja. Ese registro SHALL NOT ejecutar SQL de esquema ni modificar los datos existentes.

#### Scenario: El alta no toca el esquema ni los datos

- **WHEN** se da de alta una base preexistente
- **THEN** solo se escribe el registro de migraciones aplicadas
- **AND** las tablas, los índices y los datos quedan exactamente como estaban

#### Scenario: Tras el alta no queda nada pendiente

- **WHEN** se ejecuta el paso de migración sobre la base recién dada de alta
- **THEN** no se aplica ninguna migración
- **AND** el paso termina con éxito

#### Scenario: El esquema preexistente equivale al que producen las migraciones

- **WHEN** se compara el esquema de la base preexistente con el de una base limpia construida aplicando las migraciones
- **THEN** ambos son equivalentes
- **AND** cualquier diferencia se resuelve antes de considerar el alta completada

#### Scenario: Un alta omitida falla de forma ruidosa

- **WHEN** el paso de migración corre contra una base preexistente que no fue dada de alta
- **THEN** falla al intentar crear objetos que ya existen
- **AND** no deja la base en un estado parcialmente modificado

### Requirement: El esquema tiene una representación revisable en el repositorio

El repositorio SHALL contener un volcado del esquema vigente, actualizado junto con las migraciones que lo modifican, para que un cambio de esquema pueda revisarse como diff sin reconstruir la base.

#### Scenario: El volcado acompaña a la migración

- **WHEN** se agrega una migración que modifica el esquema
- **THEN** el volcado del esquema se regenera y se versiona junto con ella

#### Scenario: El paso de migración en runtime no reescribe el volcado

- **WHEN** el paso de migración corre durante el arranque del sistema
- **THEN** no modifica el archivo de volcado del repositorio
