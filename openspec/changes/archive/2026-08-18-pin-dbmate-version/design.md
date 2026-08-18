## Context

`bundle-migrations-in-image` dejó el esquema empaquetado en una imagen propia `aniseek-migrate`, construida sobre `ghcr.io/amacneil/dbmate`. Tras ese change, `compose.yaml` ya no referencia la imagen pública: quedan cuatro referencias, todas sin tag, es decir todas a `:latest`.

```
dbmate/Dockerfile:1            FROM ghcr.io/amacneil/dbmate      ← motor de producción
compose.dev.yaml:91            image: ghcr.io/amacneil/dbmate    ← motor de desarrollo
backend/tests/conftest.py:58   DockerContainer("...dbmate")      ← motor de los tests
README.md:183                  --entrypoint pg_dump ...dbmate    ← verificación del alta
```

Restricciones del entorno donde esto vive:

- **El `FROM` se re-resuelve en cada release.** El pipeline reconstruye `aniseek-migrate` en cada bump de versión, con caché fría en el runner. La versión de dbmate que llega a producción la decide el momento del rebuild, no el repositorio.
- **La imagen trae el cliente de Postgres, no solo el binario de dbmate.** Verificado: `dbmate:2.35.0` empaqueta `pg_dump (PostgreSQL) 18.4`, contra un servidor fijado en `postgres:18.1-alpine`. Ese `pg_dump` es el que `dbmate dump` usa para generar `dbmate/schema.sql`, y el que el README pide usar para comparar la base de un despliegue existente contra ese archivo.
- **El resto del proyecto ya fija versiones**: `postgres:18.1-alpine`, `redis:8.4.0-alpine`, `python:3.12-slim-bookworm`, `node:20-alpine`. dbmate es la única excepción.
- **No hay Renovate ni Dependabot.** Verificado: no existen `renovate.json`, `.renovaterc*` ni `.github/dependabot.yml`. Cualquier actualización de una versión fijada es manual.
- **Sí existe un ritual de versionado.** El repositorio sube las versiones de todos los servicios en conjunto (`chore: bump all services to vX.Y.Z`), lo que da un momento natural y recurrente donde revisar pins.

## Goals / Non-Goals

**Goals:**

- Que la versión de dbmate que corre en producción esté escrita en el repositorio y solo cambie por un commit que la mencione.
- Que el volcado `dbmate/schema.sql` sea reproducible: regenerarlo dentro de un año no debe producir diferencias de formato que no sean diferencias de esquema.
- Que las cuatro referencias corran la misma versión, de modo que desarrollo, tests y producción no difieran en el motor que construye el esquema.

**Non-Goals:**

- Subir dbmate. `2.35.0` es exactamente lo que las cuatro referencias resuelven hoy; este change no cambia ningún comportamiento.
- Introducir un bot de actualización de dependencias. Es una discusión aparte y más amplia que dbmate.
- Fijar el resto de las imágenes del proyecto: ya están fijadas.
- Unificar las cuatro referencias en una sola fuente de verdad. Ver D3.

## Decisions

### D1 — Versión exacta (`2.35.0`), no `2` ni `2.35`

El registry publica los tres tags y hoy los tres resuelven al mismo digest (`sha256:ff5696af…`), así que la elección no cambia nada en el presente: define quién decide el próximo salto.

`2` lo decide el registry, y la deriva no es teórica: entre febrero y agosto de 2026 ese tag avanzó de `2.29.5` a `2.35.0`, seis releases menores. Combinado con el re-resolve en cada rebuild, significa que un commit que solo sube versiones puede llevar un dbmate distinto a producción sin aparecer en el diff.

`2.35` parece el punto medio razonable —"solo parches"— pero no lo es acá, porque una release de parche es un rebuild completo de la imagen: base nueva, paquetes nuevos, posible `pg_dump` distinto. Como ese `pg_dump` genera un archivo versionado del repositorio, `2.35` deja abierta justamente la puerta que este change quiere cerrar. No hay evidencia de que haya pasado; el punto es que el tag no lo impide.

La asimetría cierra el argumento. La superficie de dbmate que este proyecto usa —leer archivos SQL de un directorio, aplicarlos en transacción, registrar la versión— no cambió entre dbmate 1.x y 2.35, así que flotar casi no compra arreglos que importen. Y lo que arriesga es el único paso del arranque que escribe en la base, con la API y el worker bloqueados detrás.

### D2 — Un tag de versión, no un digest

`@sha256:…` es la única forma de inmutabilidad real: un tag, incluso de versión exacta, puede re-publicarse. Se descarta de todas formas.

Sin Renovate ni Dependabot, un digest se convierte en una cadena que nadie lee y nadie actualiza: al revisar el archivo no se puede saber si está al día sin consultar el registry. `2.35.0` se lee de un vistazo y se compara mentalmente con la última release. El riesgo que el digest cubre —que el autor re-publique un tag de versión ya liberado— es marginal frente al costo de volver el pin ilegible.

### D3 — Cuatro literales, sin fuente única

Los cuatro consumidores son de naturaleza distinta: un `Dockerfile`, un `compose`, código Python de tests y un bloque de shell en el README. No hay un mecanismo que los cubra a los cuatro sin inventar uno.

*Alternativa considerada:* que la suite de pruebas use la imagen propia `aniseek-migrate` en vez de la pública. Dejaría un solo pin, y alinearía los tests con producción de forma más fuerte que compartir versión —correrían exactamente la misma imagen—. Se rechaza porque los tests montan `dbmate/` del repositorio (`conftest.py:39`) para construir su esquema, igual que `compose.dev.yaml`: cambiar a la imagen propia obligaría a reconstruirla antes de cada corrida y a mantener el mount de todas formas, ya que sin él una migración nueva no se vería hasta el rebuild. El costo de iteración supera al de mantener cuatro literales sincronizados.

La sincronización se apoya en que `grep -rn "amacneil/dbmate"` los encuentra todos, y en que el bump vive en el ritual de versionado.

### D4 — Fijar y actualizar son dos cosas; este change solo fija

`2.35.0` es la versión que ya corre en las cuatro referencias, lo que hace que el change sea verificable de una forma poco común: si el comportamiento cambia en algo, el change está mal. Mezclarlo con una subida de dbmate perdería esa propiedad y convertiría un cambio de cero riesgo en uno que hay que probar de verdad.

### D5 — El bump de dbmate vive en el ritual de versionado conjunto

Fijar una versión sin decidir dónde se revisa es cómo un pin se vuelve deuda. El lugar es el commit que sube las versiones de todos los servicios: ya es un momento recurrente, ya lo hace una persona mirando versiones, y es el mismo commit que dispara el rebuild de `aniseek-migrate`. Revisar ahí el pin de dbmate lo pone exactamente donde antes ocurría el salto silencioso.

## Risks / Trade-offs

**El pin se pudre.** Sin bot de actualizaciones, `2.35.0` puede seguir escrito dentro de tres años. → Mitigación: D5 le da un lugar de revisión. Y el costo real es bajo: dbmate es un binario de un solo uso, sin superficie de red, que corre milisegundos en una red interna de compose; correr una versión vieja no expone nada. La deuda se paga cuando hay una razón para pagarla.

**Cuatro literales pueden divergir.** Alguien sube uno y olvida los otros tres, y entonces tests, desarrollo y producción construyen el esquema con motores distintos —el escenario que el pin venía a evitar—. → Mitigación: un solo `grep` los encuentra; el procedimiento de bump los toca juntos.

**Acoplamiento con la versión de Postgres.** `pg_dump` debe ser igual o más nuevo que el servidor. Hoy son 18.4 contra 18.1, con margen. Si en el futuro se sube `postgres` a una mayor sin revisar el pin de dbmate, `dbmate dump` dejaría de poder volcar el esquema. Antes, con la imagen flotante, eso se resolvía solo. → Mitigación: subir Postgres pasa a implicar revisar que el `pg_dump` de la imagen fijada alcance al servidor nuevo; queda anotado en el README junto al pin.

**Un tag no es inmutable.** Aceptado explícitamente en D2.

## Migration Plan

No hay migración: el cambio no altera ningún comportamiento observable. El despliegue siguiente reconstruye `aniseek-migrate` con el mismo digest que ya venía usando.

Verificación de que efectivamente no cambió nada: confirmar que el digest de `ghcr.io/amacneil/dbmate:2.35.0` coincide con el de `:latest` antes de fijar, correr la suite de pruebas del backend, y levantar `compose.dev.yaml` contra una base vacía.

Rollback: quitar el tag de las cuatro referencias. No hay estado que deshacer.

## Open Questions

Ninguna abierta. La única que había —si los tests deberían usar la imagen propia en vez de la pública— se resolvió en D3 y queda fuera de alcance.
