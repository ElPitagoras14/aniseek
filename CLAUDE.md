# Claude Code Instructions

## Commits

- No hacer commit automáticamente después de cada cambio. Solo hacer commit cuando el usuario lo pida explícitamente.
- No agregar coautor (`Co-Authored-By`) a los commits.

## OpenSpec

- Antes de aplicar un change de OpenSpec (`/opsx:apply`), hay que estar en una rama nueva creada a partir de `main` actualizada. Nunca implementar directamente sobre `main`.
- La rama no debe tener upstream hacia `main`: crearla sin `--track` y, al publicarla, usar `git push -u origin <rama>` para que apunte a su propia rama remota.

## Versiones

- Al cambiar la versión en cualquier `pyproject.toml`, ejecutar `uv lock` en ese directorio para mantener el `uv.lock` sincronizado.
