# user-administration

## Purpose

Define lo que owner y admin pueden hacer sobre las cuentas de otros usuarios de Ani Seek (listar, crear, desactivar, reactivar, cambiar rol, restablecer contraseña) y los límites que impiden a un admin escalar privilegios.

## Requirements

### Requirement: Usuarios gestionables

El owner SHALL gestionar a los `admin` y a los `member`. Un admin SHALL gestionar solo a los `member`. Nadie SHALL gestionar al owner mediante estas operaciones. Ninguna operación de este capability SHALL aplicarse a la propia cuenta de quien la invoca, que se edita desde el perfil propio.

#### Scenario: Admin intenta gestionar a otro admin

- **WHEN** un `admin` solicita desactivar a otro `admin`
- **THEN** el sistema responde 403 y el otro admin sigue activo

#### Scenario: Admin intenta desactivarse a sí mismo

- **WHEN** un `admin` solicita desactivar su propia cuenta
- **THEN** el sistema rechaza la operación y la cuenta sigue activa

### Requirement: Listado de usuarios

Owner y admin SHALL poder listar todos los usuarios con su nombre, rol, estado activo y fecha de creación. El listado SHALL NOT incluir contraseñas ni sus hashes.

#### Scenario: Admin lista usuarios

- **WHEN** un `admin` solicita el listado de usuarios
- **THEN** recibe todos los usuarios, incluido el owner, sin datos de contraseña

### Requirement: Creación directa de usuarios

Owner y admin SHALL poder crear un usuario indicando nombre, contraseña y rol, sin invitación y con cualquier política de registro. El admin solo SHALL crear `member`. El owner SHALL crear `member` o `admin`. Nadie SHALL crear un `owner`. Aplican las mismas validaciones de nombre y contraseña que en el registro.

#### Scenario: Admin crea un member con el registro por invitación

- **WHEN** un `admin` crea un usuario `member` con la política `invite`, sin invitación
- **THEN** el sistema crea el usuario activo

#### Scenario: Admin intenta crear un admin

- **WHEN** un `admin` intenta crear un usuario con rol `admin`
- **THEN** el sistema responde 403 y no crea el usuario

### Requirement: Desactivación y reactivación

Owner y admin SHALL poder desactivar y reactivar a los usuarios que gestionan. Desactivar SHALL conservar la lista guardada y el historial de descargas del usuario. A partir de la desactivación, sus requests SHALL rechazarse según `access-control`.

#### Scenario: Desactivar a un member

- **WHEN** un `admin` desactiva a un `member`
- **THEN** ese member no puede iniciar sesión ni usar su token vigente
- **AND** su lista guardada se conserva

#### Scenario: Reactivar a un member

- **WHEN** un `admin` reactiva a un `member` desactivado
- **THEN** ese member puede volver a iniciar sesión

### Requirement: Cambio de rol

Solo el owner SHALL poder cambiar el rol de un usuario, y solo entre `member` y `admin`. Un admin SHALL NOT cambiar roles. El rol `owner` solo se asigna mediante la transferencia (`instance-owner`).

#### Scenario: Owner promueve a un member

- **WHEN** el owner cambia el rol de un `member` a `admin`
- **THEN** ese usuario tiene permisos de `admin` desde su siguiente request

#### Scenario: Admin intenta promover a un member

- **WHEN** un `admin` intenta cambiar el rol de un `member` a `admin`
- **THEN** el sistema responde 403 y el rol no cambia

#### Scenario: Asignar owner por cambio de rol

- **WHEN** el owner intenta asignar el rol `owner` a otro usuario mediante el cambio de rol
- **THEN** el sistema rechaza la operación

### Requirement: Restablecimiento de contraseña

Owner y admin SHALL poder fijar una contraseña nueva a los usuarios que gestionan, sin conocer la anterior. La contraseña nueva SHALL cumplir las mismas reglas que en el registro. Los tokens de acceso y de renovación emitidos antes del cambio SHALL dejar de ser válidos. Lo mismo SHALL ocurrir cuando un usuario cambia su propia contraseña desde el perfil.

#### Scenario: Admin restablece la contraseña de un member

- **WHEN** un `admin` fija una contraseña nueva a un `member`
- **THEN** ese member puede iniciar sesión con la contraseña nueva y no con la anterior

#### Scenario: Sesiones previas tras el restablecimiento

- **WHEN** un `admin` restablece la contraseña de un `member` que tenía una sesión abierta
- **THEN** el token de acceso y el refresh token anteriores de ese member son rechazados

#### Scenario: Admin intenta restablecer la contraseña del owner

- **WHEN** un `admin` intenta fijar una contraseña nueva al owner
- **THEN** el sistema responde 403 y la contraseña del owner no cambia
