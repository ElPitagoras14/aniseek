## ADDED Requirements

<!-- Delta sobre la capability existente `frontend-runtime-config`.
     Los términos normativos SHALL / SHALL NOT se mantienen en inglés por ser palabras
     clave de especificación. -->

### Requirement: La versión de la aplicación es una clave de configuración más

La versión que muestra la interfaz SHALL resolverse como cualquier otra clave de configuración, por el mismo orden de precedencia y declarada en la misma plantilla. SHALL NOT inyectarse en tiempo de construcción desde el manifiesto de paquetes del frontend, cuyo campo de versión deja de identificar release alguno.

Su regla de interpretación es la de una clave donde la cadena vacía cuenta como ausencia: un valor vacío SHALL tratarse como no configurado y descender a las capas siguientes. El default SHALL ser un identificador que denote ejecución fuera de un release publicado, de modo que una aplicación que corre sin versión asignada no aparente tener una.

#### Scenario: La versión se declara en la plantilla junto al resto de las claves

- **WHEN** se inspecciona la plantilla de configuración
- **THEN** la versión figura como una clave más, junto a las demás

#### Scenario: La versión no se toma del manifiesto de paquetes

- **WHEN** se construye el bundle de producción
- **THEN** la versión mostrada no proviene del campo de versión del manifiesto de paquetes

#### Scenario: Una versión vacía cuenta como ausencia

- **WHEN** la versión se resuelve a la cadena vacía en la capa de runtime
- **THEN** la aplicación la trata como no configurada y desciende a las capas siguientes

#### Scenario: Sin versión configurada la interfaz no aparenta un release

- **WHEN** la versión no está configurada en ninguna capa
- **THEN** la interfaz muestra el identificador que denota ejecución fuera de un release publicado

#### Scenario: En desarrollo la versión sale del entorno local

- **WHEN** se corre el servidor de desarrollo con la versión definida en el `.env` de la raíz
- **THEN** la interfaz muestra ese valor

### Requirement: El valor de la versión lo provee la imagen y no el entorno de despliegue

En un container, el valor de la versión SHALL provenir de un dato que la propia imagen transporta, y SHALL prevalecer sobre cualquier valor homónimo heredado del entorno del despliegue.

Esta es la única clave cuyo valor no lo decide quien despliega. La razón es que la capa de runtime gana sobre las demás: un valor fijado a mano en la configuración del despliegue quedaría congelado y enmascararía al correcto en cada release posterior. Que la imagen sea la autoridad elimina esa vía de fallo, y además permite que el valor sea exacto en una imagen que se publicó bajo una versión nueva sin reconstruirse.

#### Scenario: El arranque toma la versión de la imagen

- **WHEN** el container arranca
- **THEN** el archivo de configuración generado contiene la versión que transporta la imagen

#### Scenario: El entorno del despliegue no puede sobrescribir la versión

- **WHEN** el entorno del despliegue define un valor para la versión
- **AND** la imagen transporta un valor distinto
- **THEN** prevalece el de la imagen

#### Scenario: Una versión configurada a mano no se congela

- **WHEN** se publica un release posterior y se despliega
- **THEN** la interfaz muestra la versión de ese release
- **AND** no muestra un valor fijado previamente en la configuración del despliegue
