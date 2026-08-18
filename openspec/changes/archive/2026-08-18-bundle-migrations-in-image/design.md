## Context

`adopt-dbmate` estableció que el esquema se define en `db/migrations/` y lo aplica un servicio `aniseek-migrate` de un solo uso, antes de que arranquen API y worker. Ese servicio usa la imagen pública `ghcr.io/amacneil/dbmate` y recibe los archivos por un bind mount `./db:/db`.

El mount funciona en `compose.dev.yaml`, donde el repositorio está presente por construcción. No funciona en el modo que el README documenta como recomendado para `compose.yaml`: copiar el compose y el `.env` a la máquina de destino y correr `docker compose up -d` contra imágenes de GHCR. Ahí `./db` es una ruta relativa a un directorio que no contiene el repositorio.

El README ya arrastra esa deuda: el paso 4 de "Upgrading" instruye copiar `db/` al host, y menciona explícitamente el caso de Dokploy (`/dokploy-bk/aniseek/db:/db`), donde el operador solo pega el contenido del compose en un formulario web y no hay checkout del repositorio en ningún momento.

Restricciones que enmarcan el diseño:

- **El pipeline ya sabe hacer esto.** `.github/workflows/docker.yml` construye y publica tres imágenes a GHCR con un patrón repetido (build sin push → publish con tags de versión y `latest`), y solo después crea el tag, la release y dispara el deploy en Dokploy. Agregar una cuarta imagen es replicar ese patrón, no inventar uno.
- **dbmate tiene rutas por defecto configurables.** Busca migraciones en `./db/migrations` y el volcado en `./db/schema.sql`; ambas se pueden cambiar por flag (`--migrations-dir`, `--schema-file`) o por variable de entorno (`DBMATE_MIGRATIONS_DIR`, `DBMATE_SCHEMA_FILE`). El default explica por qué el directorio se llamó `db/` en su momento.
- **Desarrollo y producción tienen necesidades opuestas.** En desarrollo se quiere editar una migración y correrla sin reconstruir nada; en producción se quiere que las migraciones sean inmutables y correspondan a la versión desplegada.
- **El volcado del esquema se versiona, por recomendación explícita de dbmate.** Es parte del flujo de la herramienta y del procedimiento de alta del README. Este diseño lo mueve de directorio y nada más.

## Goals / Non-Goals

**Goals:**

- Que un despliegue con imágenes pre-construidas necesite únicamente `compose.yaml` y `.env`.
- Que las migraciones que se aplican correspondan siempre a la versión de las imágenes que se despliegan, sin que eso dependa de la disciplina del operador.
- Que iterar sobre una migración en desarrollo siga sin requerir reconstruir una imagen.
- Que el nombre del directorio diga qué contiene.

**Non-Goals:**

- Cambiar el motor de migraciones, el formato de los archivos o el orden de arranque. Todo eso lo fijó `adopt-dbmate` y no se toca.
- Cambiar el procedimiento de alta de una base preexistente. Sigue igual, incluida la verificación del esquema contra el volcado versionado; lo único que desaparece es el paso de copiar el directorio al host.
- Cambiar cómo se mantiene el volcado del esquema. Sigue versionado y sigue regenerándose junto con cada migración que modifica el esquema.
- Editar, agregar o quitar migraciones. El esquema resultante es idéntico.

## Decisions

### D1 — Una imagen propia que extiende la de dbmate

`dbmate/Dockerfile` hace `FROM ghcr.io/amacneil/dbmate` y copia el contenido del directorio a `/db`. No define `ENTRYPOINT` ni `CMD`: hereda los de la imagen base, de modo que el `command: ["--no-dump-schema", "up"]` del compose sigue funcionando sin cambios.

Heredar en vez de reimplementar mantiene una sola fuente para el binario de dbmate y su comportamiento; lo único que agrega la imagen propia es contenido estático.

*Alternativa considerada:* copiar las migraciones dentro de `aniseek-api` y compartirlas por volumen. Acopla dos servicios que no tienen relación de ciclo de vida y obliga a coordinar un volumen intermedio para algo que se resuelve con una imagen de contenido estático.

*Alternativa considerada:* que el paso de migración descargue las migraciones en tiempo de arranque (desde el tag de la release, por ejemplo). Agrega una dependencia de red al arranque y un modo de fallo nuevo, para evitar publicar una imagen que el pipeline ya sabe publicar.

### D2 — El directorio pasa a llamarse `dbmate/` en el repositorio; adentro sigue siendo `/db`

`db/` nombra un dominio: cualquier cosa relacionada con la base de datos podría vivir ahí —scripts de backup, configuración del motor, seeds—, y quien lo lee no puede saber qué encontrará adentro. El directorio contiene exclusivamente insumos de dbmate, así que se llama como su consumidor.

El rename aplica al repositorio, que es donde se lee el nombre. La ruta **dentro del contenedor** se queda en `/db`, que es el default de dbmate: así ni la imagen ni ningún compose declaran rutas —el `Dockerfile` copia a `/db` y ya— y el `command` del compose no cambia.

*Alternativa considerada:* renombrar también la ruta interna a `/dbmate`. Elimina el desfase entre los dos nombres, pero obliga a declarar `DBMATE_MIGRATIONS_DIR` y `DBMATE_SCHEMA_FILE` en tres lugares (la imagen propia, el compose de desarrollo que usa la imagen pública, y la suite de tests que también la usa). El desfase es visible en una sola línea de cada compose (`./dbmate:/db`), y no vale tres puntos de configuración que pueden desincronizarse.

### D3 — `schema.sql` se empaqueta aunque el paso de migración no lo use

El comando de runtime es `--no-dump-schema`, así que el volcado no se lee ni se escribe al aplicar migraciones. Aun así se copia a la imagen: es el archivo que dbmate usa para `dbmate dump` y `dbmate load`, y tenerlo adentro permite correr esas operaciones contra la misma imagen sin conseguir el repositorio — incluido el paso de verificación del procedimiento de alta.

El costo son unos pocos KB. La alternativa —copiar solo `migrations/`— los ahorra a cambio de que la imagen sea una copia parcial del directorio que dice contener, y de que `DBMATE_SCHEMA_FILE` apunte a un archivo inexistente.

### D4 — `compose.dev.yaml` conserva el bind mount

Los dos modos divergen a propósito. En desarrollo, `./dbmate:/db` sobre la imagen pública permite agregar una migración y aplicarla de inmediato. Empaquetarla exigiría reconstruir la imagen en cada iteración, que es exactamente el ciclo que el bind mount evita.

Esto no rompe la equivalencia entre modos: el contenido es el mismo directorio del repositorio, y por D2 aterriza en la misma ruta interna; solo cambia el mecanismo de entrega. Y el requisito de que las migraciones correspondan a la versión desplegada aplica a despliegues versionados, no a un checkout de trabajo donde la noción de versión no existe.

La suite de tests del backend levanta la imagen pública de la misma forma (`backend/tests/conftest.py`), así que sigue el mismo patrón: monta `dbmate/` del repositorio en `/db`.

*Consecuencia aceptada:* un cambio en el `Dockerfile` no se ejercita en desarrollo. Es superficie mínima, y el pipeline construye la imagen en cada push a `main`, así que un error se detecta ahí.

### D5 — El deploy espera a que la imagen de migraciones esté publicada

`release` y `deploy` pasan a depender también de `publish-migrate`. Sin eso, el webhook de Dokploy podría dispararse con `aniseek-migrate:latest` apuntando todavía a la versión anterior mientras los servicios ya son nuevos, que es precisamente el desajuste que este change existe para eliminar.

El patrón ya está en el workflow: los tres `publish-*` actuales dependen de los tres `build-*`, y `release` depende de los tres `publish-*`. Se extiende la lista, no se cambia la forma.

### D6 — Quitar el mount del directorio es parte de la migración, no un detalle opcional

Un bind mount sobre `/db` anula el contenido empaquetado. Un despliegue que actualice la imagen pero conserve el mount aplicaría las migraciones del host sin ningún error visible: el paso correría normalmente, con los archivos equivocados.

Por eso el mount tiene que quitarse al actualizar el compose, y por eso el change lo marca como breaking en `proposal.md` en vez de tratarlo como limpieza.

## Risks / Trade-offs

- **Una imagen más que mantener y publicar en cada versión.** → Es contenido estático sobre una base pública; no tiene dependencias propias que actualizar. El costo real es un job más en el pipeline y unos segundos de build.

- **La imagen de migraciones queda atada a `:latest` de la imagen base de dbmate.** → Igual que hoy: `compose.yaml` ya referencia `ghcr.io/amacneil/dbmate` sin tag. Este change no empeora la situación, pero tampoco la arregla; fijar una versión de dbmate es un cambio aparte.

- **Un despliegue que conserve el mount del directorio sigue funcionando en apariencia, con las migraciones equivocadas.** → Mitigado por D6 y por la nota de breaking change: hay que quitar el mount al actualizar. No hay forma de detectarlo automáticamente desde el compose, así que queda como paso documentado.

- **El renombrado toca rutas en tres archivos a la vez (Dockerfile, ambos compose) más el README.** → Un renombrado incompleto falla de forma ruidosa: dbmate no encuentra migraciones y el paso termina con error antes de que arranquen API y worker. No hay un modo silencioso de equivocarse acá.

- **En desarrollo no se ejercita el empaquetado.** → Aceptado en D4. El pipeline construye la imagen en cada push a `main`.

## Migration Plan

1. Renombrar el directorio primero, en un paso propio: es un movimiento de archivos que conviene ver aislado en el diff, sin mezclarse con los cambios de lógica.
2. Agregar `dbmate/Dockerfile` y los jobs del workflow en el mismo commit: publicar la imagen antes de que ningún compose la referencie evita una ventana donde `compose.yaml` apunte a una imagen inexistente.
3. Actualizar `compose.yaml` para usar `ghcr.io/elpitagoras14/aniseek-migrate:latest` y quitar el mount; actualizar `compose.dev.yaml` y `backend/tests/conftest.py` a `./dbmate:/db`.
4. Actualizar el README: desaparece el paso de copiar el directorio al host, y las rutas pasan al nombre nuevo.
5. Al actualizar un despliegue existente, quitar el mount del directorio del compose desplegado en el mismo cambio en que se pasa a la imagen propia.

**Rollback:** volver a `ghcr.io/amacneil/dbmate` con el mount al directorio y asegurarse de que esté presente en el host. No hay estado persistido: la imagen de migraciones no guarda nada, y el registro de lo aplicado vive en la tabla `schema_migrations` de la base, que este change no toca.

## Open Questions

Ninguna abierta.
