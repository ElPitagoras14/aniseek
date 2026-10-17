## 1. Frontend sin Node emulado

- [x] 1.1 Cambiar en `frontend/Dockerfile` la etapa `builder` a `FROM --platform=$BUILDPLATFORM node:20-alpine AS builder` (D3). Verificar con `docker buildx build --platform linux/amd64,linux/arm64 ./frontend` que la etapa `builder` aparece una sola vez en la salida, que la imagen se construye para las dos arquitecturas y que ningún paso de Node corre como `linux/arm64`
- [x] 1.2 Verificar que la imagen `web` resultante arranca y sirve la app (contenedor local en `linux/amd64`, `curl` a `/` y a `/config.js` con 200)

## 2. Workflow en dos fases

- [x] 2.1 Renombrar el job `publish` a `build` y hacer que cada acción deje `…:candidate-${{ github.sha }}` en lugar de `:<versión>` (D1): `build` y `stamp` cambian su `tags`, `promote` usa `imagetools create --tag …:candidate-<sha> …:<previous>`
- [x] 2.2 Agregar `docker/setup-qemu-action` antes de `setup-buildx-action` en `build` (D4) y `scope=${{ matrix.image }}` en `cache-from` y `cache-to` (D5)
- [x] 2.3 Reemplazar `promote-latest` por un job `publish` (`needs: [detect, build]`) que primero publique `:<versión>` de los cuatro servicios desde su candidata y después `:latest` desde `:<versión>`, y apuntar `release` a `needs: [detect, publish]` (D1)
- [x] 2.4 Agregar `timeout-minutes` a todos los jobs según D2 (`detect` 5, `build` 30, `publish`/`release`/`deploy` 10)
- [x] 2.5a Cambiar `runs-on: ubuntu-latest` por `runs-on: ubuntu-24.04` en todos los jobs (D6). Verificar con `grep -n "runs-on" .github/workflows/*.yml` que no queda ningún `ubuntu-latest`
- [x] 2.5 Actualizar los comentarios del workflow que describen el flujo (atomicidad, por qué `candidate-<sha>`, por qué el bucle de `publish` es idempotente)
- [x] 2.6 Validar el workflow con `actionlint` (imagen `rhysd/actionlint`) sin errores

## 3. Documentación y release

- [x] 3.1 Revisar `docs/` y `CONTRIBUTING.md` por referencias al flujo de publicación (`promote-latest`, publicación por servicio) y actualizarlas
- [x] 3.2 Bumpear `VERSION` de 3.2.0 a 3.2.1
- [x] 3.3 Correr `openspec validate atomic-release-publish --strict` y verificar que pasa
- [ ] 3.4 Después del merge, seguir la corrida del release 3.2.1: las cuatro candidatas se publican antes que cualquier `:3.2.1`, `publish` mueve versión y `:latest`, y el release y el deploy se crean
