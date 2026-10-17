## MODIFIED Requirements

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
| Ver, generar, regenerar y revocar la API key propia | `member` |
| Borrar los archivos descargados de un anime (`DELETE /episodes/storage/{anime_id}`) | `admin` |
| Crear franquicias (`POST /franchises`) | `admin` |
| Listar todos los usuarios (`GET /users`) | `admin` |
| Administrar usuarios, invitaciones y la política de registro | `admin` (con los límites de `user-administration` y `user-registration`) |
| Listar las API keys de todos los usuarios y revocar las ajenas | `owner` |
| Transferir el rol de owner | `owner` |
| Activar y desactivar el MCP de la instancia | `owner` |

Una operación hecha a través del MCP SHALL exigir el mismo rol mínimo que la operación equivalente de esta tabla.

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

#### Scenario: Member gestiona su API key

- **WHEN** un `member` genera, consulta o revoca su propia API key
- **THEN** la operación se ejecuta con éxito

#### Scenario: Admin revoca una API key ajena

- **WHEN** un `admin` solicita revocar la API key de otro usuario
- **THEN** el sistema responde 403

#### Scenario: Admin intenta activar el MCP

- **WHEN** un `admin` solicita activar o desactivar el MCP de la instancia
- **THEN** el sistema responde 403 y el estado del MCP no cambia

#### Scenario: Member borra archivos desde el MCP

- **WHEN** un `member` invoca a través del MCP la operación de borrar los archivos descargados de un anime
- **THEN** la operación se rechaza por permisos insuficientes y los archivos permanecen intactos
