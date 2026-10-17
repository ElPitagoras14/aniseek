## Context

`.github/workflows/release.yml` hoy tiene estos jobs:

```
detect ─▶ publish (matriz: api, worker, web, migrate) ─▶ promote-latest ─▶ release ─▶ deploy
              │ cada leg decide build / promote / stamp
              └ y publica :<versión> apenas termina
```

- **Dónde se rompe la atomicidad.** Cada leg de `publish` sube `:<versión>` por su cuenta. La atomicidad solo existe para `:latest`, en `promote-latest`. Run `39000673829`: `api`, `worker` y `migrate` publicaron `:3.1.0` mientras `web` estaba colgado.
- **Ningún job tiene `timeout-minutes`** (el default de GitHub es 360).
- **Por qué se cuelga `web`.** Las imágenes son multi-arch (`linux/amd64,linux/arm64`) y se construyen en `ubuntu-latest` (amd64), así que arm64 corre emulado con el QEMU que trae el runner. En `frontend/Dockerfile`, la etapa `builder` (`node:20-alpine`: `pnpm install` y `pnpm run build`) corre una vez por arquitectura. Bajo QEMU, Node murió con SIGILL y pnpm quedó esperando al proceso caído.
- **La caché se pisa entre servicios.** `cache-from/cache-to: type=gha` no declara `scope`, así que las cuatro legs comparten el scope por defecto.
- Las corridas están serializadas (`concurrency`, `cancel-in-progress: false`), y la spec exige mantenerlo así.

Motivación en `proposal.md`; requisitos en `specs/release-pipeline/spec.md`.

## Goals / Non-Goals

**Goals:**

- Que ninguna etiqueta `:<versión>` se publique si algún servicio no consiguió su imagen.
- Que un build colgado falle en minutos.
- Que `web` no ejecute Node bajo emulación.

**Non-Goals:**

- Runners arm64 nativos. `api` y `worker` siguen compilando arm64 emulado, pero con QEMU actualizado.
- Limpiar del registro las etiquetas candidatas.
- Cambiar la decisión build / promote / stamp ni el baseline de comparación.

## Decisions

### D1 - Dos fases: `build` prepara candidatas, `publish` las etiqueta

```
detect ─▶ build (matriz, fail-fast) ─▶ publish (1 job) ─▶ release ─▶ deploy
            │                             1. :<versión>  ◀─ :candidate-<sha>  (los 4)
            └ cada leg deja                2. :latest     ◀─ :<versión>        (los 4)
              <imagen>:candidate-<sha>
```

Cada leg de `build` termina siempre con `ghcr.io/…/aniseek-<servicio>:candidate-<github.sha>` publicado, sin importar la acción:

| Acción | Cómo deja la candidata |
|---|---|
| `build` | `build-push-action` con `tags: …:candidate-<sha>` (antes `:<versión>`) |
| `promote` | `imagetools create --tag …:candidate-<sha> …:<previous>`: copia de manifiesto, segundos |
| `stamp` (web) | `Dockerfile.promote` (`FROM …-web:<previous>` + `COPY app-version`) con `tags: …:candidate-<sha>` |

`publish` corre solo si las cuatro legs terminaron bien (`needs: [detect, build]`). Hace dos bucles de `imagetools create`:
1. `:<versión>` para los cuatro servicios, desde su candidata.
2. `:latest` para los cuatro, desde `:<versión>`.

`promote-latest` se integra en `publish`: era un solo bucle, y separarlo en otro job no aporta nada.

- **¿Por qué una etiqueta y no `push-by-digest`?** Pasar digests entre legs de una matriz exige artifacts, porque los outputs de una matriz se pisan entre legs. Una etiqueta derivada de valores conocidos (`github.sha`) la puede reconstruir cualquier job, sin plumbing.
- **¿Por qué `candidate-<sha>` y no una fija `:candidate`?** Las corridas están serializadas, pero "Re-run failed jobs" de una corrida vieja podría correr `publish` después de que una corrida más nueva sobrescribió `:candidate`, y publicaría imágenes de otro commit bajo la versión vieja. Con el sha cada corrida solo ve sus propias candidatas.
- **Ventana no atómica que queda.** Los ocho `imagetools create` de `publish` son copias de manifiesto de pocos segundos cada una. Si uno falla a la mitad del bucle 1, algunos servicios quedan con `:<versión>` y otros no. Pero `:latest` no se movió y no hay tag ni release. "Re-run failed jobs" repite `publish`, que es idempotente (vuelve a apuntar las mismas etiquetas a los mismos digests). Es la misma garantía que hoy da `promote-latest`, aplicada ahora también a las etiquetas de versión.

### D2 - `timeout-minutes` en cada job

| Job | Timeout | Duración normal |
|---|---|---|
| `detect` | 5 | ~10 s |
| `build` | 30 | 1–2 min con caché; el peor caso sano visto fue un build emulado de 27 min (2026-10-15) que ya no aplica con D3 |
| `publish`, `release`, `deploy` | 10 | segundos |

Si `build` vence su timeout, la leg falla; `fail-fast` (default `true` en la matriz) cancela las demás y `publish` no corre. Como el baseline es el tag más alto y no se creó ninguno, la próxima corrida vuelve a ver los mismos cambios pendientes.

### D3 - La etapa `builder` del frontend corre en la plataforma del runner

`frontend/Dockerfile`:

```dockerfile
FROM --platform=$BUILDPLATFORM node:20-alpine AS builder
```

`pnpm install` y `pnpm run build` producen archivos estáticos (`dist/`, `config.template.js`) que no dependen de la arquitectura. Con `--platform=$BUILDPLATFORM` BuildKit ejecuta esa etapa una sola vez, nativa en amd64, y las dos variantes de la etapa `production` (nginx) copian el mismo resultado. arm64 solo emula `apk add gettext`, `printf` y `chmod` en Alpine, sin Node.

- **Alternativa descartada:** solo actualizar QEMU. Reduce la probabilidad del SIGILL pero no la elimina, y el build emulado de `web` seguiría tardando de 12 a 27 minutos.
- **No aplica a `api` ni `worker`:** instalan wheels de Python nativos de la plataforma destino, así que su build sí necesita la arquitectura real.

### D4 - QEMU actualizado para lo que sigue emulado

El job `build` agrega `docker/setup-qemu-action` antes de `setup-buildx-action`. Registra binfmt con una versión reciente de QEMU en lugar de la del runner. Las versiones viejas son la causa habitual de `Illegal instruction` con binarios arm64 modernos.

### D5 - Caché de build con scope por servicio

`cache-from: type=gha,scope=<imagen>` y `cache-to: type=gha,mode=max,scope=<imagen>`. Hoy las cuatro legs escriben en el mismo scope y cada una pisa la caché de las otras, lo que vuelve más probable que un build arm64 emulado arranque sin caché.

### D6 - Runners fijados a `ubuntu-24.04`

Todos los jobs pasan de `runs-on: ubuntu-latest` a `runs-on: ubuntu-24.04`. GitHub anunció (`actions/runner-images#14748`, avisos en cada job) que `ubuntu-latest` migra a Ubuntu 26 desde el 2026-10-19. Esa migración cambia por debajo Docker, Buildx y el QEMU del runner, que son justo las piezas de las que depende este pipeline. Fijar la versión hace que ese cambio sea un commit explícito y no un efecto lateral en medio de un release.

- **Alternativa descartada:** dejar `ubuntu-latest` y absorber la migración. Funcionaría casi seguro, porque los builds corren dentro de contenedores y D4 trae su propio QEMU, pero un fallo en esa ventana se confundiría con los problemas que este change corrige.
- **Costo:** cuando GitHub anuncie el retiro de `ubuntu-24.04`, hay que subir la etiqueta a mano.

## Risks / Trade-offs

- **[Las etiquetas `candidate-<sha>` se acumulan en GHCR]** → una por servicio y por corrida que llega a `build` (solo cuando `VERSION` sube), así que son pocas. Limpiarlas queda como mejora futura.
- **[Un fallo dentro del bucle de `publish` deja versiones parciales sin `:latest`]** → la ventana es de segundos y el job es idempotente; se arregla con "Re-run failed jobs". Ver D1.
- **[30 minutos podrían cortar un build legítimo de `api` o `worker` emulado sin caché]** → hoy tardan menos de un minuto con caché, y D5 mejora los aciertos. Si alguna vez se acercan al límite, la salida es usar runners arm64 nativos, no subir el timeout.
- **[`ubuntu-24.04` quedará deprecado en algún momento]** → GitHub avisa con meses de anticipación, con anotaciones como las que motivaron D6. Subir de versión es cambiar una línea por job.
- **[El cambio solo se puede probar de verdad en un release real]** → se valida antes con `actionlint` y con un build local multi-arch de `web`. La corrida del 3.2.1 es la prueba final.

## Migration Plan

1. Merge con `VERSION` 3.2.1. El primer release usa ya el workflow nuevo.
2. Si la corrida del 3.2.0 sigue pendiente cuando se mergea esto, se completa o falla con el workflow viejo. Si falla, el 3.2.1 publica todo igual, porque el baseline es el tag más alto (`3.0.0`).
3. **Rollback:** revertir el commit. Las etiquetas candidatas que hayan quedado no las consume nadie.
