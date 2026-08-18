## ADDED Requirements

<!-- Delta sobre la capability existente `database-migrations`.
     Los términos normativos SHALL / SHALL NOT se mantienen en inglés por ser palabras
     clave de especificación. -->

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

## MODIFIED Requirements

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
