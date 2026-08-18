## Why

El servicio `aniseek-migrate` usa la imagen pública `ghcr.io/amacneil/dbmate` y recibe las migraciones por un bind mount (`./db:/db`). Eso funciona cuando quien despliega tiene el repositorio en disco, pero no en el modo de despliegue que este proyecto documenta como recomendado: copiar únicamente `compose.yaml` y correr `docker compose up -d` contra imágenes pre-construidas en GHCR.

En ese modo el operador tiene que conseguir las migraciones por su cuenta y depositarlas en una ruta del host que coincida con el mount — en Dokploy, donde solo se pega el contenido del compose y no hay checkout del repo, ni siquiera hay un lugar natural para hacerlo. El README ya reconoce el problema y lo empuja al operador (paso 4 de "Upgrading": copiar `db/` a `/dokploy-bk/aniseek/db`), lo que convierte un detalle de empaquetado en un paso manual, olvidable y silenciosamente desincronizable: nada garantiza que las migraciones montadas correspondan a la versión de las imágenes que se están desplegando.

Es la misma clase de problema que `fix-frontend-runtime-config` resolvió para `config.js`: un artefacto que el despliegue necesita, entregado por un canal distinto al de las imágenes que lo consumen.

Aprovechando que el change toca ese directorio entero, se corrige también su nombre: `db/` no dice qué contiene.

## What Changes

- Publicar una imagen propia `aniseek-migrate` que extiende `ghcr.io/amacneil/dbmate` con las migraciones y el volcado del esquema ya copiados adentro, versionada y publicada por el mismo pipeline que ya construye `aniseek-api`, `aniseek-worker` y `aniseek-web`.
- `compose.yaml` (despliegue con imágenes de GHCR) pasa a referenciar esa imagen y deja de montar el directorio. Un despliegue vuelve a necesitar únicamente el `compose.yaml` y el `.env`.
- Las migraciones quedan atadas a la versión: la imagen `aniseek-migrate:X.Y.Z` contiene exactamente las migraciones que corresponden a `aniseek-api:X.Y.Z`, y `:latest` avanza junto con las demás.
- `compose.dev.yaml` conserva el bind mount. En desarrollo el repositorio está presente por definición, y montar el directorio permite iterar sobre una migración sin reconstruir una imagen.
- **BREAKING** Renombrar el directorio `db/` a `dbmate/` **en el repositorio**. `db/` describe un dominio —cualquier cosa relacionada con la base de datos— cuando el directorio contiene exclusivamente insumos de dbmate; el nombre nuevo dice qué hay adentro y quién lo consume. La ruta **dentro del contenedor** sigue siendo `/db`: es el default de dbmate, así que ni la imagen ni el compose necesitan declarar rutas.
- El README deja de pedir que se copie el directorio al host para un despliegue con imágenes pre-construidas, y actualiza las rutas al nombre nuevo. El procedimiento de alta de una base preexistente (verificar el esquema contra el volcado, registrar `0001` como aplicada) no cambia.

Non-goals: no cambia el motor de migraciones (sigue dbmate), ni el formato de los archivos de migración, ni su contenido, ni el orden de arranque, ni el procedimiento de alta de bases preexistentes. Los archivos se mueven de directorio, pero no se editan. El volcado del esquema sigue versionado y sigue regenerándose junto con cada migración que modifica el esquema, como recomienda dbmate: este change no toca esa práctica.

## Capabilities

### New Capabilities

<!-- Ninguna. -->

### Modified Capabilities

- `database-migrations`: dos cambios de requisitos. (1) Se agrega cómo llegan las migraciones al despliegue — hoy la capability describe dónde viven y cuándo se aplican, pero no dice nada sobre su entrega. (2) Cambia la ruta donde viven, de `db/migrations/` a `dbmate/migrations/`.

## Impact

Código afectado:

- `db/` → `dbmate/` — el directorio se renombra; `migrations/` y `schema.sql` se mueven con él sin editarse
- `dbmate/Dockerfile` — nuevo; empaqueta el contenido del directorio sobre la imagen de dbmate, en `/db`
- `.github/workflows/docker.yml` — jobs de build y publish para `aniseek-migrate`, siguiendo el patrón de los tres servicios existentes; `release` y `deploy` pasan a depender también de ese publish
- `compose.yaml` — `aniseek-migrate` usa la imagen propia y pierde el mount del directorio
- `compose.dev.yaml` — el bind mount pasa a `./dbmate:/db`
- `backend/tests/conftest.py` — la suite monta el directorio para construir su esquema; se actualiza la ruta del host
- `README.md` — desaparece el paso de copiar el directorio al host; las rutas se actualizan al nombre nuevo
- `dbmate/migrations/`, `dbmate/schema.sql` — sin cambios de contenido

Comportamiento afectado:

- Un despliegue con imágenes de GHCR ya no requiere el directorio de migraciones en el host.
- El pipeline publica una imagen más por versión. `release` y `deploy` no corren hasta que también esa imagen esté publicada, de modo que un despliegue nunca ve migraciones de una versión distinta a la de los servicios.
- **BREAKING para despliegues existentes que ya montaban `./db:/db`**: al pasar a la imagen propia, el mount sobra. Dejarlo puesto montaría un directorio del host sobre el contenido empaquetado, así que hay que quitarlo al actualizar el compose.

Sin cambios de API, esquema de base de datos, backend, worker ni frontend. El esquema que producen las migraciones es idéntico: este change no agrega, quita ni edita ninguna migración.
