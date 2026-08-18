## 1. Establecer la línea base

- [x] 1.1 Confirmar que `ghcr.io/amacneil/dbmate:2.35.0` resuelve al mismo digest que `:latest`, `2` y `2.35`, para que el change no cambie ninguna versión en uso
- [x] 1.2 Confirmar la versión del cliente de Postgres que empaqueta esa imagen y que sea igual o más nueva que el servidor del proyecto (`postgres:18.1-alpine`)
- [x] 1.3 Listar con `grep -rn "amacneil/dbmate"` todas las referencias a la imagen pública, para no dejar ninguna fuera

## 2. Fijar la versión en cada referencia

- [x] 2.1 En `dbmate/Dockerfile`, fijar `FROM ghcr.io/amacneil/dbmate:2.35.0`
- [x] 2.2 En `compose.dev.yaml`, fijar la imagen del servicio `aniseek-migrate` a `ghcr.io/amacneil/dbmate:2.35.0`
- [x] 2.3 En `backend/tests/conftest.py`, fijar la imagen que la suite usa para construir su esquema efímero
- [x] 2.4 En `README.md`, fijar la imagen del `docker run --entrypoint pg_dump` del procedimiento de alta
- [x] 2.5 Repetir el `grep` de 1.3 y confirmar que no queda ninguna referencia a la imagen pública sin versión
- [x] 2.6 Confirmar que las referencias a la imagen propia (`ghcr.io/elpitagoras14/aniseek-migrate:latest`) quedan intactas: siguen el versionado del proyecto, no el de dbmate
- [x] 2.7 Confirmar que `.github/workflows/docker.yml` no necesita cambios: el job `build-migrate` toma la versión del `FROM` del Dockerfile

## 3. Verificar que nada cambió

- [x] 3.1 Construir `dbmate/Dockerfile` localmente y confirmar que el binario de dbmate adentro reporta `2.35.0`
- [x] 3.2 Correr la suite de pruebas del backend y confirmar que pasa con la imagen fijada
- [x] 3.3 Levantar `compose.dev.yaml` contra una base vacía y confirmar que el paso de migración aplica el esquema y termina con código 0
- [x] 3.4 Regenerar el volcado del esquema con la imagen fijada y confirmar con `git diff` que `dbmate/schema.sql` no cambia más allá del token `\restrict` que `pg_dump` aleatoriza en cada corrida
- [x] 3.5 Confirmar que las cuatro referencias declaran la misma versión

## 4. Documentar

- [x] 4.1 Anotar en el README que la versión de dbmate está fijada a propósito, y dónde están las referencias que hay que tocar para subirla
- [x] 4.2 Anotar que subir la versión de Postgres obliga a verificar que el cliente empaquetado en la imagen fijada siga alcanzando al servidor
- [x] 4.3 Anotar que el pin de dbmate se revisa en el commit que sube las versiones de todos los servicios, que es el mismo que dispara el rebuild de `aniseek-migrate`

## 5. Cerrar

- [x] 5.1 Subir la versión siguiendo la convención del repositorio de versionar los servicios en conjunto — sin bump nuevo: `bundle-migrations-in-image` ya dejó los tres servicios en `2.0.20` y esa versión no está publicada (el tag más alto es `2.0.19`), así que ambos changes se liberan juntos en `2.0.20`
- [x] 5.2 Ejecutar `uv lock` en cada directorio cuyo `pyproject.toml` haya cambiado de versión — no aplica: este change no toca ningún `pyproject.toml`; ambos `uv.lock` ya están en `2.0.20`, verificado
