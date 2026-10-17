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
