# instance-owner

## Purpose

Garantiza que cada instancia de Ani Seek tenga un único usuario con control total, el owner. Define cómo se crea sin credenciales por defecto, cómo lo heredan las instancias existentes, cómo se transfiere y qué lo protege.

## Requirements

### Requirement: Owner único

Una instancia SHALL tener a lo sumo un usuario con rol `owner`, y la base de datos SHALL impedir que exista un segundo. Una vez que la API está operativa, SHALL existir exactamente uno.

#### Scenario: Intento de crear un segundo owner

- **WHEN** se intenta asignar el rol `owner` a un usuario mientras ya existe otro owner, fuera de una transferencia
- **THEN** la operación falla y el owner existente se mantiene como único owner

### Requirement: Sin credenciales por defecto

El sistema SHALL NOT crear usuarios con un nombre o una contraseña fijados en el código. Al arrancar SHALL NOT crear ningún usuario distinto del owner.

#### Scenario: Primer arranque de una instalación nueva

- **WHEN** la API arranca por primera vez con `OWNER_USERNAME` y `OWNER_PASSWORD` definidos
- **THEN** el único usuario creado es el owner con esas credenciales
- **AND** no existe un usuario `admin` con contraseña `admin123`

### Requirement: Creación del owner al arrancar

Si al arrancar no existe un owner ni ningún usuario `admin` activo, la API SHALL crear el owner con `OWNER_USERNAME` y `OWNER_PASSWORD`, aplicando las mismas reglas de validación que al registro de un usuario. Una variable definida con valor vacío SHALL tratarse igual que una variable ausente. Si alguna de las dos falta, está vacía o no es válida, la API SHALL NOT arrancar y SHALL informar qué variable es el problema. Si ya existe un owner, la API SHALL ignorar ambas variables y SHALL NOT modificar el nombre ni la contraseña del owner.

#### Scenario: Faltan las variables sin owner

- **WHEN** la API arranca sin owner y `OWNER_PASSWORD` no está definida
- **THEN** la API termina con un error que nombra `OWNER_PASSWORD`
- **AND** no crea ningún usuario

#### Scenario: Variable definida pero vacía

- **WHEN** la API arranca sin owner y `OWNER_PASSWORD` está definida con valor vacío
- **THEN** la API termina con un error que nombra `OWNER_PASSWORD`
- **AND** no crea ningún usuario

#### Scenario: Nombre de owner ya ocupado

- **WHEN** la API arranca sin owner y ya existe un usuario con el nombre de `OWNER_USERNAME`
- **THEN** la API termina con un error que explica el conflicto
- **AND** no modifica a ese usuario

#### Scenario: Owner existente con variables distintas

- **WHEN** la API arranca con un owner ya creado y `OWNER_PASSWORD` tiene un valor distinto de su contraseña actual
- **THEN** la API arranca normalmente
- **AND** la contraseña del owner no cambia

### Requirement: Owner en instancias existentes

Si al arrancar no existe un owner pero sí algún usuario activo con rol `admin`, la API SHALL promover a owner al `admin` activo de creación más antigua, sin importar su nombre de usuario, y SHALL ignorar `OWNER_USERNAME` y `OWNER_PASSWORD`. Los `admin` desactivados SHALL NOT promoverse. La promoción SHALL conservar la contraseña, la lista guardada y el historial del usuario. Al actualizar el esquema, los usuarios con rol `guest` SHALL pasar a `member` antes de que ese rol se elimine.

#### Scenario: Instancia previa con el admin sembrado

- **WHEN** se actualiza una instancia cuyo único `admin` es el usuario sembrado originalmente
- **THEN** ese usuario pasa a ser el owner y conserva su contraseña, su lista y su historial

#### Scenario: Admin renombrado

- **WHEN** se actualiza una instancia cuyo `admin` más antiguo cambió su nombre de usuario
- **THEN** ese usuario pasa a ser el owner

#### Scenario: El admin más antiguo está desactivado

- **WHEN** se actualiza una instancia sin owner cuyo `admin` más antiguo está desactivado y existe otro `admin` activo
- **THEN** el `admin` activo más antiguo pasa a ser el owner
- **AND** el `admin` desactivado conserva su rol y su estado

#### Scenario: Solo hay admins desactivados

- **WHEN** se actualiza una instancia sin owner cuyos únicos `admin` están desactivados
- **THEN** la API crea el owner desde `OWNER_USERNAME` y `OWNER_PASSWORD`, o no arranca si faltan

#### Scenario: Instancia previa con usuarios guest

- **WHEN** se actualiza una instancia que tiene usuarios con rol `guest`
- **THEN** esos usuarios quedan con rol `member`
- **AND** el rol `guest` deja de existir

### Requirement: Protección del owner

Ningún usuario SHALL poder desactivar al owner, cambiar su rol ni restablecer su contraseña mediante la administración de usuarios. El owner solo SHALL dejar de serlo mediante una transferencia.

#### Scenario: Admin intenta desactivar al owner

- **WHEN** un `admin` solicita desactivar al owner
- **THEN** el sistema responde 403 y el owner sigue activo

#### Scenario: Owner intenta degradarse a sí mismo

- **WHEN** el owner solicita cambiar su propio rol a `admin` sin transferir
- **THEN** el sistema rechaza la operación y el owner conserva su rol

### Requirement: Transferencia del owner

Solo el owner SHALL poder transferir su rol, confirmando su contraseña actual. El destinatario SHALL ser otro usuario existente y activo. En una única operación atómica, el destinatario SHALL pasar a `owner` y el owner anterior SHALL pasar a `admin`. Si algún paso falla, ningún rol SHALL cambiar.

#### Scenario: Transferencia exitosa

- **WHEN** el owner transfiere su rol a un `member` activo, confirmando su contraseña
- **THEN** ese usuario pasa a ser el owner
- **AND** el owner anterior pasa a ser `admin`

#### Scenario: Contraseña incorrecta

- **WHEN** el owner intenta transferir su rol con una contraseña incorrecta
- **THEN** el sistema rechaza la operación y ningún rol cambia

#### Scenario: Destinatario desactivado

- **WHEN** el owner intenta transferir su rol a un usuario desactivado
- **THEN** el sistema rechaza la operación y ningún rol cambia

#### Scenario: Un admin intenta transferir

- **WHEN** un `admin` solicita transferir el rol de owner
- **THEN** el sistema responde 403
