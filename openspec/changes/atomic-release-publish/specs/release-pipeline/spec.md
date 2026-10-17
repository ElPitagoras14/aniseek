## MODIFIED Requirements

### Requirement: Un release publica la etiqueta de versión en todos los servicios

Un release SHALL dejar publicada la etiqueta de la versión nueva en todos los servicios del sistema, sin importar si cada uno se construyó o se reutilizó. Un release SHALL NOT considerarse completo si falta la etiqueta de versión de algún servicio.

La publicación SHALL ser todo o nada entre servicios. Ningún servicio SHALL recibir la etiqueta de la versión nueva hasta que todos tengan lista la imagen que la llevará. Si la preparación de la imagen de cualquier servicio falla, ningún servicio SHALL recibir la etiqueta de esa versión. Preparar la imagen de un servicio SHALL NOT publicar nada bajo la etiqueta de versión ni bajo la etiqueta móvil.

#### Scenario: Todas las etiquetas de versión quedan publicadas

- **WHEN** un release se completa con éxito
- **THEN** todos los servicios tienen publicada la etiqueta de esa versión

#### Scenario: Un servicio faltante detiene el release

- **WHEN** falla la publicación de la etiqueta de versión de algún servicio
- **THEN** el release no se completa
- **AND** no se registra ni se despliega

#### Scenario: Un servicio que falla al prepararse no deja versiones a medias

- **WHEN** la imagen de un servicio no logra prepararse
- **AND** las de los demás servicios sí
- **THEN** ningún servicio tiene publicada la etiqueta de la versión nueva
- **AND** las etiquetas de versión ya publicadas no cambian

#### Scenario: La versión se publica recién con todas las imágenes listas

- **WHEN** un servicio termina de preparar su imagen antes que los demás
- **THEN** su etiqueta de versión no se publica hasta que todos terminaron

## ADDED Requirements

### Requirement: Cada etapa del release termina en un tiempo acotado

Cada etapa del pipeline SHALL tener un tiempo máximo de ejecución. Una etapa que no termina dentro de ese tiempo SHALL fallar, con las mismas consecuencias que cualquier otro fallo de esa etapa. El tiempo máximo de la preparación de imágenes SHALL ser de 30 minutos o menos. El de las etapas que solo mueven etiquetas, registran o despliegan SHALL ser de 10 minutos o menos.

#### Scenario: Un build colgado falla

- **WHEN** la preparación de la imagen de un servicio deja de avanzar
- **THEN** la etapa falla al alcanzar su tiempo máximo
- **AND** ningún servicio recibe la etiqueta de la versión nueva

#### Scenario: Un fallo por tiempo libera la cola

- **WHEN** una corrida falla por alcanzar el tiempo máximo de una etapa
- **THEN** la siguiente corrida en espera puede comenzar
- **AND** un release posterior sigue viendo como pendientes los cambios de la corrida fallida
