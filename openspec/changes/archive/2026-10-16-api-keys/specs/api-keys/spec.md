## Purpose

Definir la API key de un usuario: cómo se genera, regenera y revoca, cómo se guarda, qué puede ver y hacer el owner sobre las keys de otros, y cómo se usa como credencial para actuar en nombre de su usuario con el rol que tenga en ese momento.

## ADDED Requirements

### Requirement: Una API key por usuario

Cada usuario SHALL tener como máximo una API key. La key SHALL pertenecer a ese usuario y SHALL NOT poder transferirse a otro.

#### Scenario: Usuario sin key

- **WHEN** un usuario que nunca generó una key consulta su API key
- **THEN** el sistema informa que no tiene key

#### Scenario: Generar la primera key

- **WHEN** un usuario sin key solicita generar una
- **THEN** el sistema crea la key y la asocia a ese usuario

### Requirement: La key completa se muestra una sola vez

El sistema SHALL devolver la key completa únicamente en la respuesta que la genera o la regenera. SHALL guardar solo un hash de la key y un prefijo corto que permita reconocerla. Ninguna consulta posterior SHALL devolver la key completa.

#### Scenario: Respuesta de generación

- **WHEN** un usuario genera su key
- **THEN** la respuesta incluye la key completa y su prefijo

#### Scenario: Consulta posterior

- **WHEN** un usuario con key consulta su API key
- **THEN** la respuesta incluye el prefijo, la fecha de creación y la fecha de último uso
- **AND** no incluye la key completa

#### Scenario: Almacenamiento

- **WHEN** se inspecciona la base de datos después de generar una key
- **THEN** la key completa no aparece almacenada en ninguna columna

### Requirement: Regenerar la key

Un usuario con key SHALL poder regenerarla. La regeneración SHALL reemplazar la key anterior en una sola operación: desde ese momento la key anterior SHALL NOT autenticar y la nueva SHALL hacerlo.

#### Scenario: La key anterior deja de funcionar

- **WHEN** un usuario regenera su key
- **AND** a continuación se presenta la key anterior como credencial
- **THEN** el sistema rechaza la credencial

#### Scenario: La key nueva funciona

- **WHEN** un usuario regenera su key
- **AND** a continuación se presenta la key nueva como credencial
- **THEN** el sistema la acepta y resuelve a ese usuario

### Requirement: Revocar la propia key

Un usuario SHALL poder revocar su key. Una key revocada SHALL NOT autenticar y SHALL desaparecer: el usuario queda sin key hasta que genere otra.

#### Scenario: Revocar la key

- **WHEN** un usuario revoca su key
- **THEN** la key deja de autenticar
- **AND** la consulta de su API key informa que no tiene key

#### Scenario: Revocar sin tener key

- **WHEN** un usuario sin key solicita revocarla
- **THEN** el sistema responde 404

### Requirement: Gestión de keys por el owner

El owner SHALL poder listar los usuarios que tienen key, con el nombre de usuario, el prefijo, la fecha de creación y la fecha de último uso de cada una. El owner SHALL poder revocar la key de cualquier usuario. Ningún otro rol SHALL poder listar ni revocar keys ajenas. El listado SHALL NOT incluir la key completa.

#### Scenario: Owner lista las keys

- **WHEN** el owner solicita el listado de keys
- **THEN** el sistema devuelve una entrada por cada usuario con key, sin la key completa

#### Scenario: Owner revoca la key de otro usuario

- **WHEN** el owner revoca la key de un `member`
- **THEN** esa key deja de autenticar

#### Scenario: Admin intenta listar keys

- **WHEN** un `admin` solicita el listado de keys
- **THEN** el sistema responde 403

#### Scenario: Admin intenta revocar una key ajena

- **WHEN** un `admin` solicita revocar la key de un `member`
- **THEN** el sistema responde 403
- **AND** la key sigue autenticando

### Requirement: Autenticación por API key

Una request autenticada por API key SHALL ejecutarse como el usuario dueño de la key, con el rol que ese usuario tenga en la base de datos en ese momento. La key SHALL NOT tener permisos propios. El sistema SHALL rechazar con 401, sin ejecutar la operación, una request que no presente key, que presente una key inexistente o revocada, o cuya key pertenezca a un usuario desactivado.

#### Scenario: Key válida

- **WHEN** una request presenta la key vigente de un usuario activo
- **THEN** la operación se ejecuta como ese usuario y con su rol

#### Scenario: Cambio de rol con efecto inmediato

- **WHEN** a un `admin` con key se le cambia el rol a `member`
- **AND** a continuación una request con su key invoca una operación que exige `admin`
- **THEN** el sistema responde 403

#### Scenario: Key inexistente

- **WHEN** una request presenta una key que no corresponde a ningún usuario
- **THEN** el sistema responde 401

#### Scenario: Request sin key

- **WHEN** una request a una operación que exige API key no presenta ninguna
- **THEN** el sistema responde 401

#### Scenario: Usuario desactivado

- **WHEN** un usuario con key es desactivado
- **AND** a continuación una request presenta su key
- **THEN** el sistema responde 401
- **AND** la key no se borra: vuelve a autenticar si el usuario se reactiva

### Requirement: La key se exige en modo un usuario

Con la autenticación deshabilitada, las operaciones que exigen API key SHALL seguir exigiéndola. SHALL NOT resolverse como el owner por el solo hecho de estar en modo un usuario.

#### Scenario: Modo un usuario sin key

- **WHEN** la autenticación está deshabilitada
- **AND** una request a una operación que exige API key no presenta ninguna
- **THEN** el sistema responde 401

#### Scenario: Modo un usuario con key

- **WHEN** la autenticación está deshabilitada
- **AND** una request presenta la key del owner
- **THEN** la operación se ejecuta como el owner

### Requirement: La key no autentica la sesión web

La API key SHALL NOT aceptarse como credencial en los endpoints que exigen la sesión web. Solo las operaciones que declaran autenticación por API key SHALL aceptarla.

#### Scenario: Key en un endpoint de la sesión web

- **WHEN** la autenticación está habilitada
- **AND** una request a un endpoint protegido por sesión presenta una API key en lugar de un token de acceso
- **THEN** el sistema responde 401

### Requirement: Registro del último uso

El sistema SHALL registrar la fecha de último uso de cada key cuando autentica una request. El registro MAY agruparse en intervalos de hasta un minuto, de modo que varias requests seguidas no generen una escritura cada una.

#### Scenario: Primer uso

- **WHEN** una key recién generada autentica su primera request
- **THEN** su fecha de último uso deja de estar vacía

#### Scenario: Uso visible para el owner

- **WHEN** un usuario usa su key
- **AND** el owner consulta el listado de keys
- **THEN** la entrada de ese usuario muestra la fecha de ese uso, con una precisión de hasta un minuto
