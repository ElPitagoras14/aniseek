## 1. Fuente única de versión

- [x] 1.1 Crear `VERSION` en la raíz con el valor actual `2.0.20`, número plano sin prefijo `v`
- [x] 1.2 Confirmar que `backend/pyproject.toml`, `worker/pyproject.toml` y `frontend/package.json` conservan su campo `version` sin cambios, y que por lo tanto no hace falta regenerar ningún `uv.lock`
- [x] 1.3 Eliminar la sección "Versiones" de `CLAUDE.md`, que exige `uv lock` tras cambiar la versión en un `pyproject.toml`
- [x] 1.4 Documentar en `CLAUDE.md` el procedimiento de release nuevo: se bumpea únicamente `VERSION` y se integra a `main`

## 2. La versión viaja dentro de la imagen web

- [x] 2.1 En `frontend/Dockerfile`, declarar `ARG APP_VERSION` en la etapa de producción y escribir su valor en `/app-version`, fuera del directorio que sirve nginx
- [x] 2.2 En `frontend/entrypoint.sh`, exportar `APP_VERSION` leyendo `/app-version` antes de invocar `envsubst`, de forma incondicional para que pise cualquier valor heredado del entorno
- [x] 2.3 Agregar `APP_VERSION: "${APP_VERSION}"` a `frontend/config.template.js`
- [x] 2.4 Verificar que el archivo `/app-version` no queda alcanzable desde el navegador, igual que `config.template.js`

## 3. El frontend resuelve la versión por la capa de runtime

- [x] 3.1 En `frontend/src/config.ts`, agregar `parseAppVersion` siguiendo el patrón de `parseAuthEnabled`: la cadena vacía cuenta como ausencia
- [x] 3.2 En `frontend/src/config.ts`, exportar `appVersion` usando `resolve` con `config?.APP_VERSION` como único candidato y `"dev"` como default
- [x] 3.3 En `frontend/src/types/config.d.ts`, agregar `APP_VERSION` al tipo `AppConfig` y eliminar la declaración de `__APP_VERSION__`
- [x] 3.4 En `frontend/vite.config.ts`, eliminar la entrada `__APP_VERSION__` de `define` y la lectura de `version` desde `package.json` con `readFileSync`
- [x] 3.5 Reemplazar `__APP_VERSION__` por `appVersion` en `frontend/src/features/landing/components/landing-footer.tsx` y `frontend/src/features/root/components/app-sidebar.tsx`
- [x] 3.6 Verificar que el servidor de desarrollo sirve `/config.js` con la clave nueva, tomando el valor del `.env` de la raíz o dejándola vacía para que caiga al default `"dev"`

## 4. Workflow: renombrado, gate de versión y detección

- [x] 4.1 Renombrar `.github/workflows/docker.yml` a `.github/workflows/release.yml` con `git mv` y cambiar el campo `name` a `Release`
- [x] 4.2 Cambiar `cancel-in-progress` a `false` conservando el grupo de concurrencia
- [x] 4.3 Escribir el job de detección: leer la versión de `VERSION` y obtener el baseline con `git tag --sort=-v:refname | head -1`, con `fetch-depth: 0` en el checkout
- [x] 4.4 Implementar la comparación semver estricta con `sort -V`, de modo que solo una versión estrictamente mayor continúe, y que la ausencia de tags previos también continúe
- [x] 4.5 Exponer `version`, `previous` y la condición de continuar como salidas del job, y condicionar los jobs siguientes a esa condición

## 5. Workflow: publicación de las imágenes

- [x] 5.1 Reemplazar los ocho jobs `build-*` y `publish-*` por un único job con `matrix` sobre las cuatro entradas `{image, dir}`: `api/backend`, `worker/worker`, `web/frontend`, `migrate/dbmate`
- [x] 5.2 En cada leg, decidir entre construir y reutilizar con `git diff --quiet <previous>..HEAD -- <dir>`
- [x] 5.3 Rama de construcción: `docker/build-push-action` con `context: ./<dir>`, ambas plataformas y caché `gha`, publicando solo `<imagen>:<version>` y sin tocar la etiqueta móvil
- [x] 5.4 Rama de reutilización para `api`, `worker` y `migrate`: `docker buildx imagetools create` desde `<imagen>:<previous>` hacia `<imagen>:<version>`
- [x] 5.5 Rama de reutilización para `web`: construir un Dockerfile mínimo con `FROM <imagen>:<previous>` y `COPY app-version /app-version`, sin ningún `RUN`, para ambas plataformas
- [x] 5.6 Antes de reutilizar, verificar con `docker buildx imagetools inspect` que existe `<imagen>:<previous>`, y construir en su lugar si falta
- [x] 5.7 Agregar el login a GHCR en todas las legs, ya que tanto construir como reutilizar escriben en el registro

## 6. Workflow: etiqueta móvil, release y despliegue

- [x] 6.1 Agregar un job que dependa de las cuatro legs y mueva `:latest` a `<version>` en los cuatro servicios con `imagetools create`, en un único runner recorriéndolos en bucle
- [x] 6.2 Reescribir el job de release para que dependa del anterior y delegue la creación del tag en `softprops/action-gh-release` vía `tag_name`, eliminando los pasos de `git config`, `git tag` y `git push`
- [x] 6.3 Quitar el checkout con `fetch-depth: 0` del job de release, que solo existía para el tageo manual
- [x] 6.4 Confirmar que el job de deploy sigue dependiendo del release y que su llamada a Dokploy no cambia

## 7. Verificación

- [ ] 7.1 Verificar que un push sin subir `VERSION` omite la corrida completa sin publicar imágenes ni crear tag
- [ ] 7.2 Verificar en el primer release real que los cuatro tags de versión quedan publicados y que los cuatro `:latest` avanzan, restableciendo el invariante del que depende la reutilización
- [ ] 7.3 En el segundo release, verificar que un servicio sin cambios obtiene la etiqueta nueva sin reconstruirse y que la etiqueta resuelve para `linux/amd64` y `linux/arm64`
- [ ] 7.4 Verificar que la imagen web reutilizada muestra en la UI el release nuevo y no aquel bajo el que se construyó su contenido
- [ ] 7.5 Confirmar en la configuración de GitHub que ninguna regla de protección de rama exige el workflow por su nombre anterior como status check requerido
- [x] 7.6 Comprobar si la API de Dokploy admite pasar variables de entorno en `compose.deploy`; si no lo admite, dejar constancia de que la versión de la UI depende exclusivamente del dato que transporta la imagen
