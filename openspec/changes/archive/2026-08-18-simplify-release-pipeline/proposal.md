## Why

El pipeline de release ejecuta **8 builds multi-arquitectura para 4 servicios**: cuatro jobs `build-*` con `push: false` que solo calientan la caché y actúan de barrera, y cuatro jobs `publish-*` que reconstruyen lo mismo para empujarlo. De las 309 líneas del workflow, unas 200 son copy-paste entre jobs que solo difieren en el `context` y el nombre de la imagen.

Peor: reconstruye los cuatro servicios en cada release aunque solo haya cambiado uno, y no puede evitarlo. La versión vive en tres archivos (`backend/pyproject.toml`, `worker/pyproject.toml`, `frontend/package.json`) que se bumpean en lockstep, así que el commit `chore: bump all services to vX` toca los tres directorios de servicio y cualquier detección de cambios por diff siempre responde "cambió todo".

La lógica de versión además compara por desigualdad (`CURRENT != LATEST`) contra `git describe --tags --abbrev=0`, que devuelve el tag alcanzable más cercano y no el semver más alto. Faltan los tags `2.0.16`, `2.0.17`, `2.0.18`, `2.0.5`, `1.0.2` y `1.0.3` pese a existir los commits de bump correspondientes: el gate actual falla en silencio.

## What Changes

- **BREAKING** La versión de release pasa a un archivo `VERSION` en la raíz del repositorio, única fuente de verdad. `backend/pyproject.toml`, `worker/pyproject.toml` y `frontend/package.json` dejan de participar del versionado de release y quedan congelados.
- **BREAKING** Desaparece el bump por servicio. Se bumpea un solo archivo, que no vive en ningún directorio de servicio, de modo que el commit de release nunca contamina la detección de cambios.
- El gate de versión pasa a comparar **semver estricto**: solo continúa si la versión del archivo es mayor que el tag más alto publicado. Igual o menor omite toda la corrida.
- Cada servicio se reconstruye solo si `git diff <último-tag>..HEAD` reporta cambios en su directorio. El que no cambió obtiene el tag nuevo por **promoción de manifiesto** (`docker buildx imagetools create`), una copia del lado del registry que preserva multi-arquitectura sin pull ni build.
- Los ocho jobs de build/publish colapsan en **un job con `matrix`** sobre los cuatro servicios.
- `:latest` se mueve para los cuatro servicios en un paso posterior a que todos hayan publicado su tag de versión, eliminando la ventana en que `compose.yaml` —que referencia `:latest` en los cuatro— podría levantar una mezcla de versiones.
- El tag de git deja de crearse con pasos manuales de `git tag` / `git push`: lo crea `softprops/action-gh-release`, que ya está en uso, a partir de `tag_name`.
- El workflow se renombra a algo que describa lo que hace y no la herramienta que usa: `docker.yml` → `release.yml`, y el campo `name` de `Build and Push Docker Images` a `Release`. El nombre actual describe dos de las cinco etapas e ignora el gate de versión, el tag, la release y el despliegue.
- La imagen web lleva adentro un archivo con el release al que pertenece, escrito tanto por una construcción real como por la promoción. El frontend deja de hornear `__APP_VERSION__` desde `package.json` y pasa a leer ese valor por la capa de configuración de runtime, de modo que la UI muestra el release aunque la imagen se haya promovido en vez de reconstruido.
- La promoción de la imagen web usa una capa `COPY` sobre la imagen anterior en vez de copiar el manifiesto, que es lo que permite estampar el release nuevo. `api`, `worker` y `migrate` conservan la copia pura de manifiesto.
- Se elimina de `CLAUDE.md` la regla de ejecutar `uv lock` tras cambiar la versión en un `pyproject.toml`: esas versiones dejan de cambiar.

## Capabilities

### New Capabilities

- `release-pipeline`: Cómo se determina la versión de un release y cuándo una corrida procede o se omite; qué hace que la imagen de un servicio se reconstruya o se promueva; en qué orden se publican las imágenes, el tag, el release y el despliegue; y qué garantías de atomicidad ofrece cada frontera.

### Modified Capabilities

- `frontend-runtime-config`: Se agrega `APP_VERSION` como clave de configuración de runtime, con su propia regla de qué cuenta como valor configurado y su default. Hoy la versión no es una clave de configuración: se inyecta en build time vía `define` de Vite.

## Impact

**Código y configuración**
- `.github/workflows/docker.yml` → `.github/workflows/release.yml` — renombrado y reescritura completa (309 líneas → estimado ~120).
- `VERSION` (nuevo, raíz) — fuente única de la versión de release.
- `frontend/config.template.js`, `frontend/entrypoint.sh` — nueva clave `APP_VERSION`, leída del archivo que trae la imagen.
- `frontend/Dockerfile` — escribe el archivo de versión durante la construcción.
- `frontend/vite.config.ts` — deja de definir `__APP_VERSION__`.
- `frontend/src/features/landing/components/landing-footer.tsx`, `frontend/src/features/root/components/app-sidebar.tsx`, `frontend/src/types/config.d.ts` — pasan a leer la versión por la capa de runtime.
- `backend/pyproject.toml`, `worker/pyproject.toml`, `frontend/package.json` — versión congelada.
- `CLAUDE.md` — se elimina la sección "Versiones".

**Specs**
- `database-migrations` ya exige que la imagen de migrate se publique con la misma versión que el resto de los servicios, en el mismo proceso y ejecución, y que un fallo detenga el release completo. El diseño lo respeta: la promoción publica ese tag igual que un build, y la barrera previa al tag se conserva. No requiere modificación.

**Operación**
- Ningún cambio en los nombres de las imágenes publicadas ni en las referencias de `compose.yaml`. El despliegue a Dokploy no cambia.
- El compose de Dokploy está en modo Raw: el YAML vive en su UI y el repositorio no se clona al desplegar, así que el `compose.yaml` versionado no es el que corre. Este change no lo necesita —la versión viaja dentro de la imagen— pero conviene registrarlo: ningún cambio a ese archivo llega a producción sin un paso manual.
- El historial de la pestaña Actions se indexa por path de archivo: las corridas previas quedan bajo el nombre viejo y el workflow renombrado arranca con historial vacío. Ninguna referencia dentro del repositorio apunta a `docker.yml` salvo documentos de changes ya archivados, que no se tocan. Queda por confirmar fuera del repositorio que ninguna regla de protección de rama lo exija como status check.
- Los tags de versión ya publicados siguen siendo válidos como baseline del primer diff.
