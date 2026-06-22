# Claude Code Instructions

## Commits

- No hacer commit automáticamente después de cada cambio. Solo hacer commit cuando el usuario lo pida explícitamente.
- No agregar coautor (`Co-Authored-By`) a los commits.

## Versiones

- Al cambiar la versión en cualquier `pyproject.toml`, ejecutar `uv lock` en ese directorio para mantener el `uv.lock` sincronizado.
