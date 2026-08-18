## ADDED Requirements

<!-- Capability nueva: `release-pipeline`.
     Los términos normativos SHALL / SHALL NOT se mantienen en inglés por ser palabras
     clave de especificación, igual que los headers de sección. -->

### Requirement: La versión de un release tiene una única fuente en el repositorio

El número de versión de un release SHALL declararse en un solo archivo, ubicado fuera de todo directorio de servicio. Ningún archivo dentro de un directorio de servicio SHALL determinar la versión del release. Cambiar la versión SHALL NOT modificar ningún directorio de servicio, porque esa modificación contaminaría la detección de cambios de la que depende la decisión de reconstruir.

#### Scenario: La versión se lee de un único lugar

- **WHEN** el pipeline necesita saber qué versión se está publicando
- **THEN** la obtiene de un solo archivo del repositorio
- **AND** no consulta ningún manifiesto de dependencias de ningún servicio

#### Scenario: Subir la versión no altera ningún servicio

- **WHEN** se prepara un release cambiando únicamente el número de versión
- **THEN** ningún directorio de servicio aparece como modificado
- **AND** ningún servicio se reconstruye por causa de ese cambio

#### Scenario: Los manifiestos de los servicios no declaran la versión del release

- **WHEN** se inspecciona el manifiesto de dependencias de cualquier servicio
- **THEN** su campo de versión no participa de la decisión de qué release se publica

### Requirement: Una corrida solo procede si la versión declarada supera a la última publicada

El pipeline SHALL comparar la versión declarada contra la versión más alta ya publicada, aplicando precedencia semántica de versiones y no igualdad textual. La corrida SHALL continuar únicamente si la declarada es estrictamente mayor. Cualquier otro caso SHALL omitir la corrida completa sin publicar imágenes, sin crear el tag y sin desplegar.

#### Scenario: Una versión mayor habilita el release

- **WHEN** la versión declarada es estrictamente mayor que la más alta publicada
- **THEN** la corrida continúa

#### Scenario: Una versión repetida no publica nada

- **WHEN** la versión declarada coincide con la más alta publicada
- **THEN** la corrida termina sin publicar imágenes, sin crear el tag y sin desplegar

#### Scenario: Una versión anterior no publica nada

- **WHEN** la versión declarada es menor que la más alta publicada
- **THEN** la corrida termina sin publicar imágenes, sin crear el tag y sin desplegar
- **AND** no se intenta crear un tag que ya existe

#### Scenario: La comparación ordena por precedencia numérica y no alfabética

- **WHEN** la versión más alta publicada es `2.0.9` y la declarada es `2.0.10`
- **THEN** la declarada se reconoce como mayor y la corrida continúa

#### Scenario: El primer release no requiere una versión previa

- **WHEN** no existe ninguna versión publicada
- **THEN** la corrida continúa

### Requirement: Un servicio se reconstruye solo si su directorio cambió desde el último release publicado

El pipeline SHALL decidir por servicio entre reconstruir y reutilizar, comparando el estado actual contra el del último release publicado con éxito. El punto de comparación SHALL ser ese release y SHALL NOT ser el conjunto de commits del último push, para que un release fallido no pierda los cambios pendientes. El alcance de la comparación SHALL ser el directorio del servicio.

#### Scenario: Un servicio con cambios se reconstruye

- **WHEN** el directorio de un servicio tiene cambios respecto del último release publicado
- **THEN** su imagen se construye a partir del código actual

#### Scenario: Un servicio sin cambios no se reconstruye

- **WHEN** el directorio de un servicio no tiene cambios respecto del último release publicado
- **THEN** su imagen no se construye a partir del código

#### Scenario: Un release fallido no pierde los cambios pendientes

- **WHEN** una corrida anterior falló antes de registrar su release
- **AND** una corrida nueva se ejecuta después
- **THEN** la corrida nueva sigue viendo como cambiados los servicios que lo estaban en la corrida fallida

#### Scenario: Un cambio fuera de los directorios de servicio no reconstruye nada

- **WHEN** el único cambio desde el último release está fuera de todo directorio de servicio
- **THEN** ningún servicio se reconstruye
- **AND** todos obtienen la versión nueva por reutilización

### Requirement: El servicio sin cambios obtiene la versión nueva reutilizando la imagen anterior

La imagen de un servicio sin cambios SHALL quedar publicada bajo la etiqueta de la versión nueva sin reconstruirse. La reutilización SHALL preservar todas las arquitecturas que publicaba la imagen anterior. El origen SHALL ser la etiqueta de versión del último release publicado y SHALL NOT ser una etiqueta móvil, cuyo contenido no ofrece garantías sobre a qué versión corresponde.

#### Scenario: La reutilización conserva todas las arquitecturas

- **WHEN** un servicio sin cambios obtiene la etiqueta de la versión nueva
- **THEN** esa etiqueta resuelve para las mismas arquitecturas que la anterior

#### Scenario: El origen de la reutilización es una versión concreta

- **WHEN** se reutiliza la imagen de un servicio sin cambios
- **THEN** el origen es la etiqueta de versión del último release publicado
- **AND** no es una etiqueta móvil

#### Scenario: Sin imagen previa se construye

- **WHEN** un servicio no tiene publicada la imagen del último release, por ser un servicio nuevo o por no existir ya en el registro
- **THEN** su imagen se construye en lugar de reutilizarse

### Requirement: La imagen que expone su versión lleva el release estampado aunque no se reconstruya

Un servicio que muestre su versión SHALL llevarla dentro de la imagen, y esa versión SHALL corresponder al release bajo el que la imagen se publica, no al release en que se construyó su contenido. Cuando ese servicio se reutiliza, la reutilización SHALL actualizar ese valor. Actualizarlo SHALL NOT implicar reconstruir la aplicación.

#### Scenario: Una imagen reutilizada declara el release nuevo

- **WHEN** un servicio que expone su versión no cambió y obtiene la etiqueta de la versión nueva
- **THEN** el valor que lleva dentro de la imagen es el de la versión nueva
- **AND** no es el de la versión bajo la que se construyó su contenido

#### Scenario: Estampar la versión no reconstruye la aplicación

- **WHEN** se actualiza la versión de un servicio que no cambió
- **THEN** no se ejecuta el proceso de construcción de la aplicación

#### Scenario: Una imagen construida declara el release que la produjo

- **WHEN** un servicio que expone su versión se construye por tener cambios
- **THEN** el valor que lleva dentro de la imagen es el de la versión que se está publicando

### Requirement: Un release publica la etiqueta de versión en todos los servicios

Un release SHALL dejar publicada la etiqueta de la versión nueva en todos los servicios del sistema, sin importar si cada uno se construyó o se reutilizó. Un release SHALL NOT considerarse completo si falta la etiqueta de versión de algún servicio.

#### Scenario: Todas las etiquetas de versión quedan publicadas

- **WHEN** un release se completa con éxito
- **THEN** todos los servicios tienen publicada la etiqueta de esa versión

#### Scenario: Un servicio faltante detiene el release

- **WHEN** falla la publicación de la etiqueta de versión de algún servicio
- **THEN** el release no se completa
- **AND** no se registra ni se despliega

### Requirement: La etiqueta móvil avanza solo cuando todos los servicios publicaron su versión

La etiqueta móvil que consume el despliegue SHALL avanzar para todos los servicios en un paso posterior a que todos tengan publicada su etiqueta de versión. SHALL NOT existir un estado observable en que la etiqueta móvil de unos servicios apunte a la versión nueva y la de otros a la anterior, porque el despliegue referencia esa etiqueta en todos.

#### Scenario: La etiqueta móvil avanza al final

- **WHEN** todos los servicios tienen publicada la etiqueta de la versión nueva
- **THEN** recién entonces la etiqueta móvil de cada uno pasa a apuntar a esa versión

#### Scenario: Un fallo deja la etiqueta móvil intacta

- **WHEN** algún servicio no logra publicar la etiqueta de la versión nueva
- **THEN** la etiqueta móvil de todos los servicios sigue apuntando a la versión anterior
- **AND** un despliegue en ese momento levanta la versión anterior de forma consistente

#### Scenario: El despliegue nunca levanta una mezcla de versiones

- **WHEN** se despliega el sistema en cualquier momento
- **THEN** todos los servicios resuelven a la misma versión

### Requirement: El registro del release y el despliegue ocurren después de publicar las imágenes

El release SHALL registrarse —tag y notas— únicamente después de que todas las imágenes estén publicadas y la etiqueta móvil haya avanzado. El despliegue SHALL dispararse únicamente después de registrar el release. Un fallo en cualquier etapa previa SHALL impedir las siguientes.

#### Scenario: El orden va de imágenes a registro y de registro a despliegue

- **WHEN** un release avanza sin errores
- **THEN** primero quedan publicadas las imágenes, después se registra el release y por último se despliega

#### Scenario: Sin imágenes publicadas no hay registro

- **WHEN** falla la publicación de alguna imagen
- **THEN** no se crea el tag ni las notas del release

#### Scenario: Sin registro no hay despliegue

- **WHEN** falla el registro del release
- **THEN** no se dispara el despliegue

### Requirement: Una corrida de release no se interrumpe por la llegada de otra

Las corridas del pipeline SHALL serializarse: mientras una está en curso, otra SHALL esperar en lugar de reemplazarla. Una corrida en curso SHALL NOT cancelarse por la llegada de un cambio nuevo, porque una interrupción a mitad del avance de la etiqueta móvil produce exactamente el estado mixto que este pipeline garantiza que no ocurre.

#### Scenario: Un cambio nuevo espera su turno

- **WHEN** llega un cambio a la rama principal mientras una corrida está en curso
- **THEN** la corrida en curso llega a su fin
- **AND** la nueva comienza después

#### Scenario: El avance de la etiqueta móvil no se interrumpe

- **WHEN** una corrida está avanzando la etiqueta móvil de los servicios
- **THEN** ningún evento externo la deja a medias

### Requirement: El release se dispara únicamente por la integración a la rama principal

El pipeline SHALL ejecutarse en respuesta a la integración de cambios a la rama principal y SHALL NOT ofrecer un disparador manual. La condición para que un release ocurra SHALL ser exclusivamente que la versión declarada supere a la última publicada.

#### Scenario: No existe una vía manual de publicación

- **WHEN** se inspecciona la configuración del pipeline
- **THEN** no declara ningún disparador manual

#### Scenario: Republicar exige declarar una versión nueva

- **WHEN** se quiere publicar un conjunto de imágenes nuevo
- **THEN** la única vía es integrar a la rama principal una versión mayor que la última publicada
