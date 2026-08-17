# database-access

## Purpose

Gobierna cómo los servicios llegan a la base de datos: cómo se expresan las consultas, cómo viaja
la conexión, cómo se delimita una unidad de trabajo y cómo se configura la conexión. No se solapa
con `database-migrations`, que gobierna cómo evoluciona el esquema, ni con `backend-testing`, que
gobierna cómo se verifica este comportamiento.

## Requirements

### Requirement: Las consultas se expresan en SQL crudo con parámetros por nombre

Las consultas SHALL escribirse como SQL, no construirse mediante un lenguaje de expresiones ni derivarse de modelos. Los valores SHALL pasarse como parámetros con nombre y SHALL NOT interpolarse en el texto de la consulta. Ambos servicios SHALL usar la misma forma.

#### Scenario: Los valores viajan como parámetros, no dentro del texto

- **WHEN** una consulta necesita un valor provisto por quien la invoca
- **THEN** el valor se pasa como parámetro con nombre
- **AND** el texto de la consulta no contiene ese valor

#### Scenario: Los dos servicios comparten el mismo dialecto

- **WHEN** se compara una consulta del backend con una del worker
- **THEN** ambas usan la misma sintaxis de parámetros con nombre
- **AND** una consulta puede moverse de un servicio al otro sin reescribirse

#### Scenario: No se derivan consultas de modelos

- **WHEN** se inspecciona el código de acceso a datos
- **THEN** no existen modelos declarativos, sesiones de mapeo objeto-relacional ni relaciones declaradas

### Requirement: Las funciones de acceso reciben la conexión y no la administran

Toda función que ejecute consultas SHALL recibir la conexión como parámetro. SHALL NOT abrirla, cerrarla ni obtenerla de un estado compartido implícito. El nivel que abre la conexión SHALL ser el que define el alcance de la unidad de trabajo.

#### Scenario: Una función de acceso no crea su propia conexión

- **WHEN** se invoca una función que ejecuta una consulta
- **THEN** utiliza la conexión que recibió
- **AND** no abre ni cierra ninguna por su cuenta

#### Scenario: La pertenencia a una transacción se ve en el punto de llamada

- **WHEN** se lee el código que invoca a una función de acceso
- **THEN** puede determinarse si esa llamada participa de una transacción observando únicamente la conexión que se le pasa
- **AND** no hace falta inspeccionar la pila de llamadas para averiguarlo

#### Scenario: Omitir la conexión es un error detectable antes de ejecutar

- **WHEN** una llamada a una función de acceso no provee la conexión
- **THEN** el error se manifiesta como una firma incompleta
- **AND** no se produce una ejecución que parezca correcta

### Requirement: Una operación de varias escrituras es atómica

Cuando una operación abarca varias escrituras, todas SHALL ejecutarse sobre la misma conexión y dentro de la misma transacción. Un fallo intermedio SHALL NOT dejar ninguna de ellas confirmada.

#### Scenario: Un fallo intermedio no deja escrituras parciales

- **WHEN** una operación de varias escrituras falla después de la primera
- **THEN** ninguna de sus escrituras queda confirmada

#### Scenario: Sin fallo, todas las escrituras quedan confirmadas

- **WHEN** la misma operación se completa sin fallos
- **THEN** todas sus escrituras quedan confirmadas

#### Scenario: Las escrituras de una operación comparten conexión

- **WHEN** una operación abarca varias escrituras
- **THEN** todas se ejecutan sobre la misma conexión
- **AND** ninguna se ejecuta sobre una conexión distinta de la que abrió la transacción

### Requirement: Una única cadena de conexión sirve a ambos servicios

La configuración de conexión SHALL expresarse en una sola variable, con un valor idéntico para el servicio asincrónico y el sincrónico. SHALL NOT requerir traducción, variantes por servicio ni variables separadas.

#### Scenario: El mismo valor configura los dos servicios

- **WHEN** se configura la conexión a la base de datos
- **THEN** el backend y el worker reciben el mismo valor
- **AND** ninguno lo transforma antes de usarlo

#### Scenario: El modo de ejecución lo determina quien construye la conexión

- **WHEN** el backend construye su acceso a la base
- **THEN** obtiene una variante asincrónica
- **WHEN** el worker construye el suyo con la misma cadena
- **THEN** obtiene una variante sincrónica

### Requirement: Los límites del pool de conexiones están declarados

La cantidad de conexiones permanentes y el máximo alcanzable SHALL declararse de forma explícita. SHALL NOT quedar librados a los valores por defecto de la capa de acceso, para que un cambio de capa no altere la capacidad del servicio de forma inadvertida.

#### Scenario: Los límites son explícitos

- **WHEN** se inspecciona la construcción del acceso a la base
- **THEN** la cantidad de conexiones permanentes y el techo total están declarados

#### Scenario: Cambiar de capa de acceso no cambia la capacidad

- **WHEN** se reemplaza la capa que ejecuta las consultas
- **THEN** el techo de conexiones simultáneas se mantiene igual al anterior

### Requirement: El servicio no arranca si la base de datos no responde

El backend SHALL verificar la conectividad con la base durante su arranque y SHALL fallar si no la obtiene. Al cerrar, SHALL liberar las conexiones que mantenga.

#### Scenario: Una base inalcanzable impide el arranque

- **WHEN** el backend arranca y la base de datos no responde
- **THEN** el arranque falla con un error explícito
- **AND** el servicio no queda aceptando peticiones que fallarían al consultar

#### Scenario: Al cerrar se liberan las conexiones

- **WHEN** el backend se detiene ordenadamente
- **THEN** las conexiones que mantenía quedan liberadas
