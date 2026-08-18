# Claude Code Instructions

## Idioma

- Responder siempre en español, en toda la conversación.

## Exploración del código

Usar **codegraph** (`codegraph_explore`) como herramienta por defecto para explorar el proyecto, antes de recurrir a `Grep` o `Read`.

- Vale tanto para responder preguntas ("cómo funciona X", "dónde está Y") como **antes de editar**: una sola llamada devuelve el código fuente verbatim con números de línea, además de quién llama a ese símbolo y qué depende de él. Eso permite editar viendo el radio de impacto, no a ciegas.
- Una llamada suele responder toda la pregunta. Un ciclo de `Grep` + `Read` para lo mismo cuesta decenas de llamadas y rehace un trabajo que el índice ya hizo.
- Sigue saltos que `grep` no puede seguir: callbacks, dispatch dinámico, re-render de React, children de JSX.
- No delegar la búsqueda a un subagente que lea archivos: repite lo que codegraph ya resolvió y sale más caro para la misma respuesta.
- El índice va ~1s detrás de las escrituras. Tras editar, esperar ese margen antes de volver a consultar.

Recurrir a `Grep` o `Read` cuando codegraph no aplica: archivos que no son código (`.env`, `compose.yaml`, `Dockerfile`, `.gitignore`, Markdown), búsquedas de texto literal en configuración, o inspección de dependencias en `node_modules` y `.venv`.

## Commits

- No hacer commit automáticamente después de cada cambio. Solo hacer commit cuando el usuario lo pida explícitamente.
- No agregar coautor (`Co-Authored-By`) a los commits.
- Los mensajes de commit siguen conventional commits en inglés, con descripción corta (sin cuerpo extenso salvo que se pida explícitamente).

## OpenSpec

- Antes de aplicar un change de OpenSpec (`/opsx:apply`), hay que estar en una rama nueva creada a partir de `main` actualizada. Nunca implementar directamente sobre `main`.
- La rama no debe tener upstream hacia `main`: crearla sin `--track` y, al publicarla, usar `git push -u origin <rama>` para que apunte a su propia rama remota.

## Versiones

- El número de versión de un release vive únicamente en `VERSION`, en la raíz del repositorio. Los campos `version` de `backend/pyproject.toml`, `worker/pyproject.toml` y `frontend/package.json` quedan congelados y no participan del release.
- Para publicar un release: bumpear `VERSION` a un valor estrictamente mayor (semver) e integrarlo a `main`. El pipeline de release (`release.yml`) se dispara con ese push y compara contra el tag más alto ya publicado.
