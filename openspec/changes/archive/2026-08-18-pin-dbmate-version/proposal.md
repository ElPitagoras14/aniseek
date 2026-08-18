## Why

Todas las referencias a la imagen de dbmate en el repositorio están sin tag, es decir apuntan a `:latest`. Es la única excepción: `postgres` está fijado en `18.1-alpine`, `redis` en `8.4.0-alpine`, las imágenes base de los tres servicios propios en una versión concreta de Python o Node.

Con `bundle-migrations-in-image` aplicado, esa referencia flotante queda en el `FROM` de `dbmate/Dockerfile`, que el pipeline **reconstruye en cada bump de versión** y con caché fría. Un commit que solo sube versiones —sin mencionar dbmate en ningún archivo— puede entonces llevar a producción un dbmate distinto al que se probó. El paso donde eso se manifestaría es `aniseek-migrate`: contra la base, en el arranque, bloqueando a la API y al worker.

La asimetría es lo que decide: la superficie de dbmate que este proyecto usa —leer archivos SQL de un directorio, aplicarlos en transacción, registrar la versión— no cambió entre dbmate 1.x y 2.35, así que flotar no compra prácticamente ningún arreglo que importe; y lo que arriesga es el único paso del arranque que escribe en la base. La deriva tampoco es teórica: entre febrero y agosto de 2026 el tag `2` avanzó de `2.29.5` a `2.35.0`, seis releases menores.

Hay un segundo efecto, menos evidente: la imagen no trae solo el binario de dbmate, también el cliente de Postgres. `dbmate dump` genera `dbmate/schema.sql` invocando ese `pg_dump`, y el procedimiento de alta del README pide comparar la base real contra ese archivo usando el mismo binario (`docker run --entrypoint pg_dump ghcr.io/amacneil/dbmate`). El design de `adopt-dbmate` ya tuvo que descontar a mano el ruido cosmético de esa comparación. Con la imagen flotante, un volcado regenerado meses después trae diferencias de formato que no son diferencias de esquema, y la verificación documentada pierde valor.

## What Changes

- Fijar `2.35.0` en las cuatro referencias a `ghcr.io/amacneil/dbmate` que quedan tras `bundle-migrations-in-image`: el `FROM` del Dockerfile propio, la imagen del servicio en `compose.dev.yaml`, la que usa la suite de pruebas para construir su esquema, y el `docker run` del procedimiento de alta del README.
- La versión de dbmate pasa a subirse en el mismo momento en que se suben las versiones de los servicios, no cuando el pipeline decide reconstruir.

Se eligió la versión exacta (`2.35.0`) y no `2` ni `2.35`. Hoy los cuatro tags resuelven al mismo digest, así que la decisión no cambia qué se corre ahora: cambia si el próximo salto lo decide el repositorio o el registry. `2` re-resuelve la versión en cada release del proyecto. `2.35` protege del salto de menor pero no del rebuild de la imagen, que es lo que puede traer otro `pg_dump` y ensuciar el volcado versionado. Solo la versión exacta queda clavada a un digest.

Non-goals: no se fija por digest (`@sha256:…`). El repositorio no tiene Renovate ni Dependabot, y una cadena opaca que nadie va a actualizar es peor que un número legible que se revisa en el ritual de bump que ya existe. Tampoco se cambia el motor de migraciones, ni las migraciones, ni el orden de arranque, ni se sube dbmate a una versión más nueva: `2.35.0` es exactamente lo que se está corriendo hoy.

## Capabilities

### New Capabilities

<!-- Ninguna. -->

### Modified Capabilities

- `database-migrations`: se agregan dos requisitos. (1) La versión de la herramienta que aplica las migraciones está fijada en el repositorio y es la misma en despliegue, desarrollo y pruebas — la capability describe dónde vive el esquema, cómo se identifican las migraciones y cuándo se aplican, pero no dice nada sobre el motor que las aplica. (2) El cliente de Postgres que esa imagen empaqueta debe ser compatible con el servidor: al fijar la versión, esa compatibilidad deja de resolverse sola y pasa a mantenerse de forma explícita.

## Impact

Depende de que `bundle-migrations-in-image` esté aplicado: `dbmate/Dockerfile` no existe todavía, y la referencia de `compose.yaml` desaparece con ese change (pasa a la imagen propia `aniseek-migrate`).

Código afectado:

- `dbmate/Dockerfile` — `FROM ghcr.io/amacneil/dbmate:2.35.0`
- `compose.dev.yaml` — la imagen del servicio `aniseek-migrate`
- `backend/tests/conftest.py` — la imagen que la suite usa para construir el esquema efímero
- `README.md` — el `docker run --entrypoint pg_dump` del procedimiento de alta

Comportamiento afectado:

- Ninguno hoy: `2.35.0` es el digest que las cuatro referencias ya resuelven.
- Un rebuild de `aniseek-migrate` deja de poder cambiar la versión de dbmate por su cuenta.
- Subir dbmate se vuelve un cambio explícito y revisable en el diff.

Sin cambios de API, esquema de base de datos, backend, worker ni frontend.
