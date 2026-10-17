## Why

El release 3.1.0 nunca se registró. El job que construía `web` se colgó 1 h 23 min y hubo que cancelarlo (run `39000673829`). La causa: la parte arm64 de la imagen se construye emulada con QEMU, y Node se cayó dentro del emulador durante `pnpm install` (`qemu: uncaught target signal 4 (Illegal instruction)`). pnpm se quedó esperando al proceso caído y, como el job no tiene `timeout-minutes`, nada lo cortaba antes de las 6 h.

La misma corrida mostró un segundo problema. Cada servicio publica su etiqueta de versión por su cuenta, apenas termina. `api`, `worker` y `migrate` dejaron publicado `:3.1.0` mientras `web` seguía colgado, así que el registro quedó con un release a medias: tres servicios con la versión y uno sin ella, sin tag ni release en GitHub.

## What Changes

- **Release atómico en dos fases.** Primero, todos los servicios preparan su imagen candidata (construida, reutilizada o estampada) bajo una etiqueta temporal propia de la corrida. Recién cuando las cuatro están listas, un único job publica la etiqueta de versión en todos y después mueve `:latest`. Si cualquier servicio falla en la primera fase, ningún servicio recibe la etiqueta de versión.
- **Tiempo máximo por etapa.** Cada job declara `timeout-minutes`, así un build que deja de avanzar falla en minutos y no bloquea la cola durante horas.
- **El frontend ya no corre Node emulado.** La etapa que instala dependencias y compila la app web se ejecuta una sola vez, en la arquitectura del runner, porque su resultado (archivos estáticos) es igual para cualquier arquitectura. Por arm64 solo pasa la etapa de nginx, que no ejecuta Node.
- **QEMU actualizado** para los builds que sí siguen emulando arm64 (`api`, `worker`), en lugar del que trae el runner.
- **Caché de build separada por servicio**, para que los cuatro builds no se pisen la caché entre sí.
- **Runners fijados a `ubuntu-24.04`** en lugar de `ubuntu-latest`, que migra a Ubuntu 26 desde el 2026-10-19 (aviso en cada job). El cambio de sistema operativo del runner pasa a ser una decisión explícita y no algo que ocurre solo entre dos releases.
- `VERSION` 3.2.0 → 3.2.1, para que el merge ejercite el pipeline nuevo y publique con la imagen web corregida.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `release-pipeline`:
  - la publicación de etiquetas de versión pasa a ser todo o nada entre servicios;
  - se agrega un tiempo máximo a cada etapa, para que un fallo que no termina igual cuente como fallo.

## Impact

- **CI:** `.github/workflows/release.yml`, el único workflow del repo. El job `publish` se divide en `build` (matriz, sube candidatas) y `publish` (un job, mueve tags). `promote-latest` se integra en `publish`. Agrega `timeout-minutes`, `docker/setup-qemu-action` y alcance de caché por servicio.
- **Frontend:** `frontend/Dockerfile` (etapa `builder` con `--platform=$BUILDPLATFORM`). Cambiar ese archivo hace que `web` se reconstruya en el próximo release.
- **Registro (GHCR):** aparece una etiqueta candidata por servicio y por corrida que llega a la fase de build. El resto de las etiquetas no cambia: `:<versión>` y `:latest` siguen siendo las que consumen `compose.yaml` y Dokploy.
- **Sin cambios** en la API, el worker, la base de datos ni en la decisión de reconstruir o reutilizar.
- **Fuera de alcance:**
  - runners arm64 nativos (`ubuntu-24.04-arm`);
  - limpieza automática de las etiquetas candidatas;
  - cambiar el disparador o la serialización de corridas.
