## Purpose

Permite que un agente de IA use Ani Seek a través del Model Context Protocol en nombre de un usuario: buscar y consultar animes, gestionar su lista guardada y pedir descargas. El owner lo habilita a nivel de instancia.

## ADDED Requirements

### Requirement: Activación del MCP por el owner

La instancia SHALL tener un estado del MCP, activado o desactivado. Por defecto SHALL estar desactivado, también en las instancias que se actualizan. Solo el owner SHALL poder cambiarlo. Cualquier usuario autenticado SHALL poder consultar si está activado. El valor SHALL persistir entre reinicios. Un cambio SHALL tener efecto en la request siguiente, sin reiniciar la API. Desactivar el MCP SHALL NOT eliminar ni modificar las API keys existentes.

#### Scenario: Instancia nueva

- **WHEN** se consulta el estado del MCP en una instancia recién instalada o recién actualizada
- **THEN** el MCP está desactivado

#### Scenario: Owner activa el MCP

- **WHEN** el owner activa el MCP
- **THEN** la request MCP siguiente con una API key válida se atiende, sin reiniciar la API

#### Scenario: Member consulta el estado

- **WHEN** un `member` consulta si el MCP está activado
- **THEN** recibe el estado actual, sin poder cambiarlo

#### Scenario: Las keys sobreviven al apagado

- **WHEN** el owner desactiva el MCP y luego lo vuelve a activar
- **THEN** las API keys que existían antes siguen autenticando

### Requirement: MCP desactivado responde como inexistente

Con el MCP desactivado, toda request al endpoint del MCP SHALL responder 404, presente o no una API key válida. SHALL NOT revelar que el endpoint existe ni ejecutar ninguna operación.

#### Scenario: Request con key válida y MCP apagado

- **WHEN** un cliente envía una request al endpoint del MCP con una API key válida y el MCP está desactivado
- **THEN** el sistema responde 404 y no ejecuta ninguna operación

#### Scenario: Request sin key y MCP apagado

- **WHEN** un cliente envía una request al endpoint del MCP sin credenciales y el MCP está desactivado
- **THEN** el sistema responde 404, no 401

### Requirement: Autenticación por API key en cada request

Con el MCP activado, cada request al endpoint del MCP SHALL autenticarse por API key según `api-keys`, de forma independiente de las requests anteriores. El MCP SHALL NOT aceptar el token de la sesión web. Con la autenticación de la instancia deshabilitada, el MCP SHALL seguir exigiendo la API key. Una request rechazada SHALL responder 401 sin ejecutar ninguna operación.

#### Scenario: Request sin key

- **WHEN** un cliente envía una request al MCP activado sin API key
- **THEN** el sistema responde 401

#### Scenario: Token de sesión web

- **WHEN** un cliente envía una request al MCP activado con un token de acceso de la sesión web en lugar de una API key
- **THEN** el sistema responde 401

#### Scenario: Modo un usuario sin key

- **WHEN** la autenticación de la instancia está deshabilitada y un cliente envía una request al MCP activado sin API key
- **THEN** el sistema responde 401

#### Scenario: Key revocada entre dos llamadas

- **WHEN** un agente hace una llamada con éxito, la key se revoca y el agente hace otra llamada con la misma key
- **THEN** la segunda llamada responde 401

### Requirement: Ejecución con el rol actual del usuario

Cada operación del MCP SHALL ejecutarse como el usuario dueño de la API key, con el rol que tenga en la base de datos en el momento de esa request. Los datos por usuario (lista guardada, historial de descargas, estadísticas) SHALL ser los de ese usuario.

#### Scenario: Lista guardada propia

- **WHEN** el agente de un `member` pide su lista guardada
- **THEN** recibe los animes guardados por ese `member` y no los de otros usuarios

#### Scenario: Cambio de rol durante una sesión

- **WHEN** un `admin` usa el MCP, el owner lo cambia a `member` y el agente invoca una operación que exige `admin`
- **THEN** la operación se rechaza por permisos insuficientes

### Requirement: Catálogo de tools

El MCP SHALL ofrecer estos tools, con el rol mínimo indicado:

| Tool | Qué hace | Rol mínimo |
|---|---|---|
| `search_anime` | Busca animes en el proveedor por texto | `member` |
| `get_anime` | Devuelve la ficha de un anime con sus episodios y su estado de descarga | `member` |
| `list_saved` | Lista los animes guardados por el usuario | `member` |
| `list_airing` | Lista los animes en emisión guardados por el usuario, con su día de emisión | `member` |
| `list_downloads` | Lista el historial de descargas del usuario | `member` |
| `get_storage_usage` | Devuelve el uso de almacenamiento por anime | `member` |
| `get_stats` | Devuelve las estadísticas del usuario | `member` |
| `save_anime` | Guarda un anime en la lista del usuario | `member` |
| `unsave_anime` | Quita un anime de la lista del usuario | `member` |
| `refresh_anime` | Vuelve a sincronizar un anime desde el proveedor | `member` |
| `download_episodes` | Pide la descarga de episodios de un anime | `member` |
| `get_download_status` | Devuelve el estado de descarga de episodios de un anime | `member` |
| `delete_anime_files` | Borra los archivos descargados de un anime | `admin` |

El MCP SHALL NOT ofrecer tools de administración de usuarios, invitaciones ni ajustes de la instancia. Los tools SHALL NOT devolver URLs para descargar archivos de episodios.

#### Scenario: Agente de un member lista los tools

- **WHEN** el agente de un `member` pide la lista de tools
- **THEN** recibe todos los tools de la tabla salvo `delete_anime_files`

#### Scenario: Sin tools de administración

- **WHEN** el agente del owner pide la lista de tools
- **THEN** la lista no incluye ningún tool para gestionar usuarios, invitaciones ni ajustes de la instancia

### Requirement: Visibilidad de tools según el rol

La lista de tools que recibe un agente SHALL incluir solo los tools que el rol actual de su usuario puede usar. Al ejecutar un tool, el sistema SHALL volver a comprobar el rol. Si el rol no alcanza, SHALL rechazar la llamada con un error de permisos insuficientes y SHALL NOT producir ningún efecto, aunque el agente conozca el nombre del tool.

#### Scenario: Member invoca un tool oculto

- **WHEN** el agente de un `member` invoca `delete_anime_files` por su nombre
- **THEN** la llamada se rechaza por permisos insuficientes y los archivos permanecen intactos

#### Scenario: Admin ve el tool destructivo

- **WHEN** el agente de un `admin` pide la lista de tools
- **THEN** la lista incluye `delete_anime_files`

### Requirement: Ids de anime con proveedor

Todo id de anime que el MCP reciba o devuelva SHALL tener la forma `<proveedor>:<slug>`. Hoy el único proveedor es `animeav1`. Esto incluye los ids dentro de relaciones y listados. Un id sin proveedor, con un proveedor no soportado o con formato inválido SHALL rechazarse con un error que indique el formato esperado, sin ejecutar la operación. Este formato SHALL aplicar solo al MCP; la REST API SHALL NOT cambiar sus ids.

#### Scenario: Id válido

- **WHEN** el agente invoca `get_anime` con `animeav1:one-piece`
- **THEN** recibe la ficha del anime `one-piece`, con su id expresado como `animeav1:one-piece`

#### Scenario: Ids en relaciones

- **WHEN** el agente recibe la ficha de un anime que tiene animes relacionados
- **THEN** cada id de anime relacionado tiene la forma `animeav1:<slug>`

#### Scenario: Proveedor no soportado

- **WHEN** el agente invoca un tool con el id `jkanime:one-piece`
- **THEN** la llamada se rechaza con un error que indica los proveedores soportados y no se ejecuta ninguna operación

#### Scenario: Id sin proveedor

- **WHEN** el agente invoca un tool con el id `one-piece`
- **THEN** la llamada se rechaza con un error que indica el formato `<proveedor>:<slug>`

### Requirement: Tope y resultado de `download_episodes`

`download_episodes` SHALL recibir un anime y una lista de números de episodio. Los números repetidos SHALL contarse una sola vez. Los episodios que el usuario ya tiene pedidos o descargados SHALL omitirse, SHALL informarse como ya descargados y SHALL NOT contar para el tope. Si los episodios restantes superan 25, el sistema SHALL rechazar el pedido entero, sin encolar ninguno, con un error que pida dividirlo en pedidos de hasta 25. En otro caso, el resultado SHALL informar cada episodio pedido con uno de estos estados: encolado, ya descargado, inexistente o fallo al encolar.

#### Scenario: Pedido dentro del tope

- **WHEN** el agente pide 10 episodios que existen y que el usuario no tiene descargados
- **THEN** los 10 se encolan y el resultado informa cada uno como encolado

#### Scenario: Pedido que supera el tope

- **WHEN** el agente pide 30 episodios que el usuario no tiene descargados
- **THEN** la llamada se rechaza, ningún episodio se encola y el error pide dividir el pedido en tramos de hasta 25

#### Scenario: Ya descargados fuera del tope

- **WHEN** el agente pide 30 episodios de los que el usuario ya tiene 10 descargados
- **THEN** se encolan los 20 restantes y el resultado informa los otros 10 como ya descargados

#### Scenario: Episodio inexistente

- **WHEN** el agente pide los episodios 1 y 9999 de un anime que solo tiene 12
- **THEN** el episodio 1 se encola y el 9999 se informa como inexistente

### Requirement: Estado de descarga por episodio

`get_download_status` SHALL recibir un anime y una lista de números de episodio, y SHALL devolver para cada uno su estado de descarga actual: sin descargar, pendiente, obteniendo enlace, descargando, reintentando, descargado o fallido. El estado SHALL ser consultable también después de que la descarga termine. Para cada episodio SHALL indicar además si el usuario lo pidió.

#### Scenario: Seguimiento después de pedir descargas

- **WHEN** el agente pide descargar episodios y más tarde consulta su estado por anime y número
- **THEN** recibe el estado de cada episodio, incluido el de los que ya terminaron de descargarse

#### Scenario: Episodio nunca pedido

- **WHEN** el agente consulta un episodio que nadie pidió descargar
- **THEN** su estado es sin descargar y no figura como pedido por el usuario

### Requirement: Anotaciones de los tools

Cada tool SHALL declarar si solo lee datos o si los modifica. `delete_anime_files` SHALL declararse destructivo, para que el cliente pida confirmación al usuario. Ningún tool SHALL depender de un parámetro de confirmación que el agente pueda completar por su cuenta. Los tools que consultan al proveedor externo (`search_anime`, `get_anime`, `refresh_anime`) SHALL declararlo.

#### Scenario: Cliente recibe la lista de tools de un admin

- **WHEN** el agente de un `admin` pide la lista de tools
- **THEN** `delete_anime_files` figura como destructivo y `list_saved` figura como de solo lectura

### Requirement: Mismas reglas de negocio que la REST API

Cada tool SHALL aplicar las mismas reglas que la operación REST equivalente, incluidas la espera mínima entre refrescos de un anime, la existencia del anime y la imposibilidad de guardar dos veces el mismo anime o quitar uno no guardado. Cuando una regla o el proveedor rechazan la operación, el tool SHALL devolver un error con un mensaje que explique el motivo y SHALL NOT dejar efectos parciales.

#### Scenario: Refresco dentro de la espera mínima

- **WHEN** el agente invoca `refresh_anime` sobre un anime sincronizado hace menos de 5 minutos
- **THEN** el tool devuelve un error que indica los segundos que faltan y el anime no se vuelve a sincronizar

#### Scenario: Guardar un anime ya guardado

- **WHEN** el agente invoca `save_anime` sobre un anime que el usuario ya tiene guardado
- **THEN** el tool devuelve un error que indica que ya está guardado

#### Scenario: Quitar un anime no guardado

- **WHEN** el agente invoca `unsave_anime` sobre un anime que el usuario no tiene guardado
- **THEN** el tool devuelve un error que indica que no está guardado

#### Scenario: Descargar episodios de un anime inexistente

- **WHEN** el agente invoca `download_episodes` con un id de anime que no existe
- **THEN** el tool devuelve un error de anime no encontrado y no encola nada
