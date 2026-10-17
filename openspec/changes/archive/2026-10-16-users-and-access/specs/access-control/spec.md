## Purpose

Define quién puede hacer qué en una instancia de Ani Seek: los roles que existen, cómo se identifica al usuario de cada request en modo multiusuario y en modo un usuario, y qué operaciones exige cada rol.

## ADDED Requirements

### Requirement: Roles de la instancia

El sistema SHALL tener exactamente tres roles: `owner`, `admin` y `member`. Cada usuario SHALL tener exactamente un rol. Los roles SHALL formar una jerarquía: todo lo permitido a `member` SHALL estar permitido a `admin`, y todo lo permitido a `admin` SHALL estar permitido a `owner`. No SHALL existir el rol `guest`.

#### Scenario: Conjunto de roles disponible

- **WHEN** se consultan los roles definidos en la instancia
- **THEN** el resultado es exactamente `owner`, `admin` y `member`

#### Scenario: Un admin puede lo que puede un member

- **WHEN** un `admin` invoca una operación permitida a `member`
- **THEN** la operación se ejecuta igual que para un `member`

### Requirement: Identificación del usuario en modo multiusuario

Con la autenticación habilitada, toda request a un endpoint protegido SHALL presentar un token de acceso válido. El sistema SHALL resolver el usuario y su rol desde la base de datos en cada request, no desde el contenido del token, de modo que un cambio de rol o una desactivación tengan efecto en la request siguiente.

#### Scenario: Request sin token

- **WHEN** una request llega a un endpoint protegido sin token de acceso
- **THEN** el sistema responde 401 y no ejecuta la operación

#### Scenario: Cambio de rol con efecto inmediato

- **WHEN** a un `admin` se le cambia el rol a `member` mientras su token sigue vigente
- **AND** ese usuario invoca a continuación una operación que exige `admin`
- **THEN** el sistema responde 403

#### Scenario: Usuario inexistente

- **WHEN** una request presenta un token válido de un usuario que ya no existe
- **THEN** el sistema responde 401

### Requirement: Usuarios desactivados

Un usuario desactivado SHALL NOT poder iniciar sesión, renovar su token ni usar un endpoint protegido, aunque conserve un token vigente.

#### Scenario: Token vigente de un usuario desactivado

- **WHEN** un usuario desactivado presenta un token de acceso todavía vigente
- **THEN** el sistema responde 401 y no ejecuta la operación

#### Scenario: Renovación de token de un usuario desactivado

- **WHEN** un usuario desactivado presenta un refresh token todavía vigente
- **THEN** el sistema rechaza la renovación y no emite un token nuevo

### Requirement: Modo un usuario

Con la autenticación deshabilitada, el sistema SHALL tratar toda request como hecha por el owner de la instancia. SHALL NOT depender de un usuario con un nombre fijo.

#### Scenario: Request sin login en modo un usuario

- **WHEN** la autenticación está deshabilitada y llega una request sin token
- **THEN** la operación se ejecuta como el owner, con sus permisos

#### Scenario: Owner renombrado en modo un usuario

- **WHEN** la autenticación está deshabilitada y el owner cambió su nombre de usuario
- **THEN** las requests se siguen resolviendo como ese owner

### Requirement: Respuesta ante permisos insuficientes

Cuando el usuario de una request no tiene el rol que la operación exige, el sistema SHALL responder 403 y SHALL NOT producir ningún efecto: ni escrituras en la base de datos, ni archivos borrados, ni tareas encoladas.

#### Scenario: Member intenta borrar archivos globales

- **WHEN** un `member` solicita borrar los archivos descargados de un anime
- **THEN** el sistema responde 403
- **AND** los archivos y sus registros permanecen intactos

### Requirement: Permisos por operación

Cada operación SHALL exigir como mínimo el rol indicado:

| Operación | Rol mínimo |
|---|---|
| Buscar y ver animes, refrescar un anime, ver el calendario | `member` |
| Guardar y quitar animes de la lista propia | `member` |
| Solicitar descargas, ver y borrar el historial de descargas propio | `member` |
| Ver el uso de almacenamiento | `member` |
| Ver franquicias | `member` |
| Ver y editar el perfil propio, ver estadísticas propias | `member` |
| Borrar los archivos descargados de un anime (`DELETE /episodes/storage/{anime_id}`) | `admin` |
| Crear franquicias (`POST /franchises`) | `admin` |
| Listar todos los usuarios (`GET /users`) | `admin` |
| Administrar usuarios, invitaciones y la política de registro | `admin` (con los límites de `user-administration` y `user-registration`) |
| Transferir el rol de owner | `owner` |

#### Scenario: Member crea una franquicia

- **WHEN** un `member` solicita crear una franquicia
- **THEN** el sistema responde 403 y no crea la franquicia

#### Scenario: Admin borra archivos globales

- **WHEN** un `admin` solicita borrar los archivos descargados de un anime
- **THEN** el sistema borra los archivos y responde con éxito

#### Scenario: Member lista usuarios

- **WHEN** un `member` solicita el listado de todos los usuarios
- **THEN** el sistema responde 403

#### Scenario: Member usa la biblioteca propia

- **WHEN** un `member` guarda un anime, solicita una descarga o consulta sus estadísticas
- **THEN** la operación se ejecuta con éxito
