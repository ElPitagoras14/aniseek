# database-migrations

## Purpose

Gobierna cómo evoluciona el esquema de la base de datos: dónde se define, cómo se aplica, cómo se
registra lo aplicado y en qué momento del arranque ocurre.
## Requirements
### Requirement: El esquema se define exclusivamente en migraciones versionadas

El esquema de la base de datos SHALL estar definido en archivos de migración versionados bajo `dbmate/migrations/`, en la raíz del repositorio. No SHALL existir ningún otro mecanismo que cree o modifique el esquema durante el despliegue.

#### Scenario: Una base nueva se construye desde las migraciones

- **WHEN** se levanta el sistema contra una base de datos vacía
- **THEN** el esquema completo queda creado aplicando las migraciones en orden
- **AND** los datos de referencia que la aplicación necesita para funcionar quedan sembrados

#### Scenario: No queda ningún mecanismo de creación alternativo

- **WHEN** se inspecciona el repositorio y los archivos de compose
- **THEN** no existe ningún archivo de inicialización de esquema fuera de `dbmate/migrations/`
- **AND** ningún servicio monta archivos en el directorio de inicialización de la imagen de Postgres

#### Scenario: Un cambio de esquema llega a un despliegue con datos

- **WHEN** se agrega una migración y se actualiza un despliegue cuya base ya contiene datos
- **THEN** el cambio se aplica sobre la base existente
- **AND** no se requiere borrar el volumen ni ejecutar SQL a mano

#### Scenario: El nombre del directorio identifica a su consumidor

- **WHEN** se inspecciona la raíz del repositorio
- **THEN** el directorio que contiene las migraciones se llama según la herramienta que las aplica, no según el dominio al que pertenecen

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

### Requirement: Las migraciones llegan al despliegue empaquetadas, no montadas desde el host

El paso de migración SHALL obtener las migraciones desde su propia imagen publicada, y SHALL NOT depender de que existan archivos en el host donde corre. Un despliegue que usa imágenes pre-construidas SHALL requerir únicamente el archivo de compose y su configuración de entorno.

#### Scenario: Un despliegue no necesita el repositorio en disco

- **WHEN** se despliega el sistema disponiendo solo del archivo de compose y del archivo de entorno
- **THEN** el paso de migración encuentra las migraciones dentro de su imagen
- **AND** no se requiere copiar ningún directorio de migraciones al host

#### Scenario: El paso de migración no monta el directorio de migraciones

- **WHEN** se inspecciona la definición del paso de migración para un despliegue con imágenes pre-construidas
- **THEN** no declara ningún montaje que aporte las migraciones desde el host

#### Scenario: La ubicación de las migraciones viaja con la imagen

- **WHEN** se ejecuta la imagen del paso de migración
- **THEN** encuentra sus migraciones sin que el compose le indique dónde buscarlas

#### Scenario: En desarrollo las migraciones se montan desde el repositorio

- **WHEN** se levanta el sistema en modo desarrollo, donde el repositorio está presente
- **THEN** el paso de migración lee las migraciones del repositorio montado
- **AND** agregar o editar una migración surte efecto sin reconstruir ninguna imagen

### Requirement: Las migraciones se versionan junto con los servicios que dependen de ellas

La imagen del paso de migración SHALL publicarse con la misma versión que las imágenes de los servicios de la aplicación, por el mismo proceso y en la misma ejecución. La publicación de la versión SHALL NOT completarse si alguna de esas imágenes falta.

#### Scenario: Una versión publica todas sus imágenes

- **WHEN** se publica una versión del sistema
- **THEN** la imagen del paso de migración se publica con esa misma versión, junto a las de los servicios de la aplicación

#### Scenario: Las migraciones corresponden a la versión desplegada

- **WHEN** se despliega una versión determinada del sistema
- **THEN** las migraciones que se aplican son exactamente las que acompañan a esa versión
- **AND** no puede ocurrir que el esquema se migre con archivos de una versión distinta a la de los servicios

#### Scenario: Un fallo al publicar detiene la versión completa

- **WHEN** falla la publicación de la imagen del paso de migración
- **THEN** la versión no se marca como liberada
- **AND** no se dispara el despliegue

### Requirement: La versión de la herramienta de migraciones está fijada en el repositorio

Toda referencia a la imagen de la herramienta que aplica las migraciones SHALL declarar una versión exacta. Ninguna referencia SHALL usar una etiqueta móvil —ni implícita ni de línea de versión—, de modo que la versión que corre la decida el repositorio y no el registry ni el momento de la reconstrucción. Todas las referencias SHALL declarar la misma versión.

#### Scenario: Cada referencia declara una versión exacta

- **WHEN** se inspecciona cualquier referencia a la imagen de la herramienta de migraciones en el repositorio
- **THEN** la referencia incluye una versión exacta
- **AND** no queda ninguna referencia sin versión ni con una etiqueta que pueda avanzar sola

#### Scenario: Todos los entornos aplican las migraciones con la misma versión

- **WHEN** se comparan las referencias que usan el despliegue, el modo desarrollo y la suite de pruebas
- **THEN** las tres declaran la misma versión de la herramienta
- **AND** el esquema se construye con el mismo motor en los tres casos

#### Scenario: Reconstruir la imagen del paso de migración no cambia la herramienta

- **WHEN** se reconstruye la imagen del paso de migración sin que el repositorio haya cambiado
- **THEN** la herramienta que queda dentro es la misma versión que antes de reconstruir

#### Scenario: Subir la herramienta es un cambio visible

- **WHEN** la versión de la herramienta de migraciones cambia
- **THEN** el cambio aparece en el diff del repositorio
- **AND** no puede llegar a un despliegue sin haber pasado por un commit que lo declare

#### Scenario: El volcado del esquema es reproducible

- **WHEN** se regenera el volcado del esquema sin haber agregado ni modificado migraciones
- **THEN** el resultado no introduce diferencias de formato atribuibles a otra versión de la herramienta

### Requirement: El cliente de Postgres empaquetado es compatible con el servidor

La herramienta de migraciones genera el volcado del esquema con el cliente de Postgres que trae su propia imagen. Al quedar esa versión fijada, la compatibilidad con el servidor deja de resolverse sola: el cliente empaquetado SHALL ser de una versión igual o más nueva que la del servidor de base de datos que el proyecto usa. Un cambio en la versión del servidor SHALL ir acompañado de la verificación de que el cliente empaquetado sigue alcanzándolo.

#### Scenario: El volcado del esquema puede generarse

- **WHEN** se regenera el volcado del esquema contra la versión de servidor que el proyecto usa
- **THEN** el cliente empaquetado en la imagen fijada lo genera sin rechazar la versión del servidor

#### Scenario: Subir el servidor obliga a revisar el cliente

- **WHEN** se sube la versión del servidor de base de datos del proyecto
- **THEN** se verifica que el cliente que empaqueta la imagen fijada sea igual o más nuevo que el servidor nuevo
- **AND** si no lo es, la versión de la herramienta de migraciones se sube junto con el servidor

#### Scenario: La verificación del alta usa el mismo cliente que produjo el volcado

- **WHEN** se compara el esquema de un despliegue existente contra el volcado versionado
- **THEN** el volcado de la base real se genera con el cliente de la misma versión fijada de la herramienta
- **AND** la comparación no queda sesgada por una diferencia de versión entre clientes

