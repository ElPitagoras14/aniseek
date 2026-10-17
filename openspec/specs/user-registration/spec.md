# user-registration

## Purpose

Controla cómo se incorporan usuarios nuevos a una instancia de Ani Seek: la política de registro que decide owner o admin, el registro abierto, y las invitaciones de un solo uso con rol preasignado.

## Requirements

### Requirement: Política de registro

La instancia SHALL tener una política de registro con uno de dos valores: `invite` u `open`. El default SHALL ser `invite`, también en las instancias que se actualizan. Solo owner y admin SHALL poder cambiarla. El valor SHALL persistir entre reinicios. Ninguna política SHALL impedir el uso de una invitación válida ni la creación directa de usuarios por owner o admin.

#### Scenario: Instalación nueva

- **WHEN** se consulta la política de una instancia recién instalada
- **THEN** la política es `invite`

#### Scenario: Instancia actualizada

- **WHEN** se consulta la política de una instancia que se actualizó desde una versión con registro abierto
- **THEN** la política es `invite`

#### Scenario: Member intenta cambiar la política

- **WHEN** un `member` solicita cambiar la política de registro
- **THEN** el sistema responde 403 y la política no cambia

#### Scenario: La política sobrevive a un reinicio

- **WHEN** un admin cambia la política a `open` y la API se reinicia
- **THEN** la política sigue siendo `open`

### Requirement: Consulta pública de la política

El sistema SHALL exponer la política de registro sin autenticación, para que la interfaz decida si ofrece registrarse sin invitación. La respuesta SHALL NOT incluir invitaciones ni datos de usuarios.

#### Scenario: Visitante sin sesión

- **WHEN** un visitante sin sesión consulta la política de registro
- **THEN** recibe el valor de la política y nada más

### Requirement: Registro según la política

Con la política `invite`, el registro SHALL exigir una invitación válida. Con `open`, el registro sin invitación SHALL crear un usuario con rol `member`. En modo un usuario, el registro SHALL rechazarse siempre, con o sin invitación. Un registro rechazado SHALL NOT crear ningún usuario. El nombre de usuario SHALL ser único, y la contraseña SHALL tener al menos 6 caracteres.

#### Scenario: Registro sin invitación con la política por invitación

- **WHEN** alguien se registra sin invitación con la política `invite`
- **THEN** el sistema responde 403 y no crea el usuario

#### Scenario: Registro abierto

- **WHEN** alguien se registra sin invitación con la política `open`
- **THEN** el sistema crea un usuario activo con rol `member`

#### Scenario: Registro en modo un usuario

- **WHEN** la autenticación está deshabilitada y alguien intenta registrarse
- **THEN** el sistema responde 403 y no crea el usuario

#### Scenario: Nombre de usuario repetido

- **WHEN** alguien se registra con un nombre de usuario que ya existe
- **THEN** el sistema responde 409 y no crea el usuario

### Requirement: Invitaciones

Owner y admin SHALL poder crear invitaciones. Cada invitación SHALL tener un rol preasignado: `member` si la crea un admin, `member` o `admin` si la crea el owner, y nunca `owner`. SHALL tener un vencimiento: 7 días por defecto y como máximo 30. El enlace o token SHALL mostrarse una sola vez al crearla. El sistema SHALL guardarlo de forma que, con acceso a la base de datos, no se pueda reconstruir un token utilizable.

#### Scenario: Admin invita a un admin

- **WHEN** un `admin` intenta crear una invitación con rol `admin`
- **THEN** el sistema responde 403 y no crea la invitación

#### Scenario: Owner invita a un admin

- **WHEN** el owner crea una invitación con rol `admin`
- **THEN** el sistema crea la invitación y devuelve su token una única vez

#### Scenario: Vencimiento excesivo

- **WHEN** alguien crea una invitación con un vencimiento mayor a 30 días
- **THEN** el sistema rechaza la creación

### Requirement: Uso de una invitación

Con cualquier política, registrarse con una invitación válida SHALL crear el usuario con el rol de la invitación. En la misma operación atómica, la invitación SHALL quedar consumida. Una invitación SHALL usarse a lo sumo una vez. Una invitación vencida, revocada o ya usada SHALL rechazarse.

#### Scenario: Registro con invitación válida

- **WHEN** alguien se registra con una invitación válida de rol `admin`
- **THEN** se crea un usuario con rol `admin`
- **AND** la invitación queda consumida

#### Scenario: Invitación con la política abierta

- **WHEN** alguien se registra con una invitación válida de rol `admin` y la política `open`
- **THEN** se crea un usuario con rol `admin`, no `member`

#### Scenario: Reutilizar una invitación

- **WHEN** alguien se registra con una invitación que ya se usó
- **THEN** el sistema rechaza el registro y no crea el usuario

#### Scenario: Invitación vencida

- **WHEN** alguien se registra con una invitación vencida
- **THEN** el sistema rechaza el registro y no crea el usuario

#### Scenario: Usos simultáneos

- **WHEN** dos registros usan la misma invitación al mismo tiempo
- **THEN** a lo sumo uno crea un usuario

### Requirement: Listado y revocación de invitaciones

Owner y admin SHALL poder listar las invitaciones pendientes y las ya usadas, y revocar las pendientes. Una invitación usada SHALL mostrar quién la usó y cuándo. Las invitaciones revocadas y las vencidas sin usar SHALL NOT aparecer. El admin solo SHALL ver y revocar invitaciones de rol `member`. El listado SHALL NOT revelar el token.

#### Scenario: Invitación usada en el listado

- **WHEN** alguien se registró con una invitación y un admin lista las invitaciones
- **THEN** la invitación aparece con el usuario que la usó y la fecha de uso
- **AND** las invitaciones pendientes aparecen sin esos datos

#### Scenario: Revocar una invitación pendiente

- **WHEN** un admin revoca una invitación pendiente de rol `member`
- **THEN** la invitación deja de poder usarse

#### Scenario: Admin intenta revocar una invitación de admin

- **WHEN** un `admin` intenta revocar una invitación de rol `admin`
- **THEN** el sistema responde 403 y la invitación sigue vigente
