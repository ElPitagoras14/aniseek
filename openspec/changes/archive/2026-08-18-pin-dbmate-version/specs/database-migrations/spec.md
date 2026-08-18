## ADDED Requirements

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
