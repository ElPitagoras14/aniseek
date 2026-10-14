# anime-catalog

## Purpose

Define cómo el backend sincroniza un anime desde el proveedor del catálogo (hoy AnimeAV1), qué persiste al hacerlo, cuándo lo hace y cómo expone el resultado y los errores del proveedor a los clientes de la API.

## Requirements

### Requirement: Una sincronización consulta la ficha del proveedor una sola vez

Sincronizar un anime, sea la primera vez o un refresh, SHALL obtener la ficha completa del proveedor (metadatos, géneros, relaciones y lista de episodios) con una única consulta a la página del anime. SHALL NOT repetir la consulta a la misma página dentro de la misma sincronización ni introducir esperas deliberadas entre consultas.

#### Scenario: Primera sincronización de un anime

- **WHEN** se sincroniza un anime que no está en la base
- **THEN** el proveedor recibe una sola petición por la página de ese anime
- **AND** no transcurre ninguna espera deliberada durante la sincronización

#### Scenario: Refresh de un anime existente

- **WHEN** se refresca un anime que ya está sincronizado
- **THEN** el proveedor recibe una sola petición por la página de ese anime
- **AND** no transcurre ninguna espera deliberada durante la sincronización

### Requirement: Crear y refrescar persisten el mismo conjunto de datos

Toda sincronización exitosa SHALL persistir, en una única unidad de trabajo, los mismos datos: los campos del anime (con la marca de cuándo se sincronizó), sus géneros, sus relaciones (registrando como placeholder cada anime relacionado que aún no exista) y sus episodios. La persistencia SHALL ser idempotente: repetirla con los mismos datos SHALL NOT duplicar episodios, géneros ni relaciones, y SHALL agregar los episodios nuevos que el proveedor publique.

#### Scenario: Un refresh incorpora episodios nuevos

- **WHEN** un anime sincronizado con 10 episodios se refresca y el proveedor ya publica 12
- **THEN** el anime queda con 12 episodios
- **AND** los 10 episodios previos no se duplican

#### Scenario: Un refresh sin novedades no altera colecciones

- **WHEN** se refresca un anime y el proveedor devuelve los mismos episodios, géneros y relaciones
- **THEN** la cantidad de episodios, géneros y relaciones del anime no cambia

#### Scenario: Un fallo durante la persistencia no deja escrituras parciales

- **WHEN** una escritura falla a mitad de la persistencia de una sincronización
- **THEN** ninguno de los datos de esa sincronización queda confirmado
- **AND** el anime conserva el estado previo a la sincronización

### Requirement: Un tipo de relación desconocido no impide la sincronización

Si el proveedor informa una relación con un tipo que el sistema no reconoce, la sincronización SHALL omitir esa relación, dejarla registrada en el log y completar el resto de la persistencia.

#### Scenario: Relación con tipo no soportado

- **WHEN** la ficha del proveedor incluye una relación de un tipo no reconocido junto con relaciones de tipos conocidos
- **THEN** la sincronización termina con éxito
- **AND** se persisten las relaciones de tipos conocidos y se omite la desconocida

### Requirement: Un anime placeholder se trata como no sincronizado

Un anime SHALL considerarse sincronizado solo si tiene registrada una sincronización exitosa. Un anime presente únicamente como placeholder (registrado por ser relacionado de otro) SHALL tratarse igual que uno inexistente en todos los puntos de entrada.

#### Scenario: Consultar el detalle de un placeholder

- **WHEN** un usuario consulta el detalle de un anime que solo existe como placeholder
- **THEN** el sistema lo sincroniza completo antes de responder
- **AND** la respuesta contiene sus datos completos

#### Scenario: Guardar un anime inexistente

- **WHEN** un usuario guarda un anime que no está en la base o que solo existe como placeholder
- **THEN** el sistema lo sincroniza antes de registrarlo como guardado

### Requirement: El refresh manual exige un anime sincronizado y respeta un cooldown

`PUT /animes/{anime_id}` SHALL responder 404 si el anime no está sincronizado (inexistente o placeholder), indicando que se cree primero con `GET /animes/{anime_id}`. SHALL responder 429 si la última sincronización ocurrió hace menos de 5 minutos, indicando los segundos restantes.

#### Scenario: Refresh de un anime no sincronizado

- **WHEN** se invoca `PUT /animes/{anime_id}` sobre un anime inexistente o placeholder
- **THEN** la respuesta es 404
- **AND** el mensaje remite a `GET /animes/{anime_id}`

#### Scenario: Refresh dentro del cooldown

- **WHEN** se invoca `PUT /animes/{anime_id}` 2 minutos después de su última sincronización
- **THEN** la respuesta es 429 con los segundos restantes del cooldown
- **AND** el proveedor no recibe ninguna petición

### Requirement: Las sincronizaciones concurrentes del mismo anime se comparten

Mientras una sincronización de un anime está en curso, toda otra solicitud que requiera sincronizar ese mismo anime SHALL esperar el resultado de la sincronización en curso en lugar de iniciar otra. Si la sincronización en curso falla, las solicitudes que la esperaban SHALL recibir ese mismo fallo, y una solicitud posterior SHALL poder iniciar una sincronización nueva.

#### Scenario: Dos consultas simultáneas de un anime nuevo

- **WHEN** dos usuarios consultan al mismo tiempo el detalle de un anime que no está en la base
- **THEN** el proveedor recibe una sola petición por la página de ese anime
- **AND** ambos reciben el detalle completo

#### Scenario: Un fallo no queda memorizado

- **WHEN** una sincronización falla y luego llega una nueva solicitud para el mismo anime
- **THEN** la nueva solicitud inicia una sincronización nueva contra el proveedor

### Requirement: El detalle expone la URL de cada episodio y no expone la plataforma

La respuesta de `GET /animes/{anime_id}` y `PUT /animes/{anime_id}` SHALL incluir en cada episodio la URL de su página en el proveedor del catálogo. La respuesta SHALL NOT incluir un campo `platform`. La construcción de esa URL SHALL residir solo en el backend; los clientes SHALL usar la URL recibida.

#### Scenario: Episodio con URL

- **WHEN** un cliente consulta el detalle de un anime sincronizado
- **THEN** cada episodio de la respuesta incluye `url` con la dirección de ese episodio en el proveedor

#### Scenario: Sin campo platform

- **WHEN** un cliente consulta el detalle de un anime sincronizado
- **THEN** la respuesta no contiene el campo `platform`

### Requirement: Los errores del proveedor se traducen a códigos HTTP significativos

Cuando una sincronización o búsqueda falla por causa del proveedor del catálogo, la API SHALL responder:

- 404 si el proveedor indica que el anime no existe
- 429 si el proveedor bloquea o limita las peticiones
- 502 ante cualquier otro fallo del proveedor (error HTTP, timeout, falla de conexión o página sin los datos esperados)

Una ficha que el proveedor entrega sin datos SHALL NOT persistirse.

#### Scenario: Anime inexistente en el proveedor

- **WHEN** un usuario consulta el detalle de un identificador que el proveedor no reconoce
- **THEN** la respuesta es 404
- **AND** no se persiste ningún anime con ese identificador

#### Scenario: Proveedor bloqueando peticiones

- **WHEN** el proveedor responde que la petición fue bloqueada o limitada
- **THEN** la respuesta es 429

#### Scenario: Página sin datos

- **WHEN** el proveedor responde con éxito pero la página no contiene los datos del anime
- **THEN** la respuesta es 502
- **AND** el anime no queda marcado como sincronizado
