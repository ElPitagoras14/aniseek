## 1. Renombrar el directorio

- [x] 1.1 Renombrar `db/` a `dbmate/` con `git mv`, sin editar el contenido de `migrations/` ni de `schema.sql`
- [x] 1.2 Confirmar que el diff muestra los archivos como renombrados, no como reescritos
- [x] 1.3 Buscar en el repositorio referencias a la ruta vieja (`db/`, `/db`, `./db`) y listar las que haya que actualizar en los pasos siguientes

## 2. Empaquetar el directorio en una imagen

- [x] 2.1 Crear `dbmate/Dockerfile` con `FROM ghcr.io/amacneil/dbmate`, copiando `migrations/` y `schema.sql` a `/db`
- [x] 2.2 No declarar rutas: `/db` es el default de dbmate, así que ni la imagen ni el compose necesitan `DBMATE_MIGRATIONS_DIR`/`DBMATE_SCHEMA_FILE` (decisión revisada — ver D2)
- [x] 2.3 No declarar `ENTRYPOINT` ni `CMD`: heredar los de la imagen base para que el `command` del compose siga funcionando
- [x] 2.4 Construir la imagen localmente y confirmar que `/db/migrations/0001_create_initial_schema.sql` y `/db/schema.sql` existen adentro
- [x] 2.5 Correr la imagen contra una base vacía y confirmar que aplica la migración sin recibir ninguna ruta por argumento

## 3. Publicar la imagen desde el pipeline

- [x] 3.1 Agregar el job `build-migrate` a `.github/workflows/docker.yml` siguiendo el patrón de los tres builds existentes, con `context: ./dbmate`
- [x] 3.2 Agregar el job `publish-migrate`, con los tags de versión y `latest` bajo `ghcr.io/elpitagoras14/aniseek-migrate`
- [x] 3.3 Sumar `build-migrate` a los `needs` de los tres `publish-*` existentes, para conservar la regla de que nada se publica hasta que todo compile
- [x] 3.4 Sumar `publish-migrate` a los `needs` de `release`, de modo que una versión no se libere sin su imagen de migraciones
- [x] 3.5 Confirmar que `deploy` sigue colgando de `release` y por lo tanto tampoco corre antes de que la imagen esté publicada

## 4. Consumir la imagen en el despliegue

- [x] 4.1 En `compose.yaml`, cambiar la imagen de `aniseek-migrate` a `ghcr.io/elpitagoras14/aniseek-migrate:latest`
- [x] 4.2 Quitar el mount del directorio de `aniseek-migrate` en `compose.yaml` — dejarlo puesto anularía el empaquetado en silencio
- [x] 4.3 En `compose.dev.yaml`, cambiar el bind mount a `./dbmate:/db`, conservando la imagen pública de dbmate
- [x] 4.4 No declarar variables de entorno en `compose.dev.yaml`: la ruta interna sigue siendo el default de dbmate (decisión revisada — ver D2)
- [x] 4.5 Confirmar que ambos compose conservan `--no-dump-schema` en el `command`, para que el runtime no reescriba el volcado versionado
- [x] 4.6 Confirmar que ningún otro servicio de ninguno de los dos compose montaba el directorio viejo
- [x] 4.7 (fuera del plan original) Actualizar `backend/tests/conftest.py`: la suite monta el directorio para construir su esquema y el rename la rompía

## 5. Verificar el comportamiento

- [x] 5.1 Levantar el sistema con `compose.yaml` contra una base vacía, sin el directorio `dbmate/` presente en el host, y confirmar que el esquema se construye
- [x] 5.2 Confirmar que el paso de migración termina con éxito y no se reinicia, y que API y worker arrancan después
- [x] 5.3 Levantar el sistema con `compose.dev.yaml` y confirmar que editar una migración surte efecto sin reconstruir ninguna imagen
- [x] 5.4 Tras correr las migraciones en desarrollo, confirmar con `git status` que `schema.sql` no quedó modificado

## 6. Documentar

- [x] 6.1 En el README, quitar de "Upgrading" el paso de copiar el directorio al host para despliegues con imágenes pre-construidas (y el mismo pedido en "Quick Start")
- [x] 6.2 Actualizar las rutas del README (`db/migrations/`, `db/schema.sql`, el ejemplo de Dokploy) al nombre nuevo
- [x] 6.3 Anotar que un despliegue existente debe quitar el mount del directorio al pasar a la imagen propia
- [x] 6.4 Confirmar que el resto del procedimiento de alta de una base preexistente queda intacto

## 7. Cerrar

- [x] 7.1 Subir la versión siguiendo la convención del repositorio de versionar los servicios en conjunto (2.0.19 → 2.0.20, con `uv lock` en backend y worker)
