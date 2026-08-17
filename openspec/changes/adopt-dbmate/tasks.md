## 1. Crear la migración inicial

- [ ] 1.1 Crear `db/migrations/0001_create_initial_schema.sql` con el contenido íntegro de `postgres/init.sql` bajo la marca `-- migrate:up`: las 13 tablas, los 9 índices y los tres bloques de datos de referencia (`role_types`, `related_types`, `avatars`)
- [ ] 1.2 Incluir la marca `-- migrate:down` sin instrucciones debajo, dejando la migración inicial deliberadamente irreversible
- [ ] 1.3 Confirmar que el SQL se copió sin modificaciones: este change no altera el esquema, solo el mecanismo por el que se aplica

## 2. Verificar que la migración reproduce el esquema real

- [ ] 2.1 Levantar una base de datos limpia con `postgres:18.1-alpine` y aplicarle la migración inicial con `ghcr.io/amacneil/dbmate --no-dump-schema up`
- [ ] 2.2 Volcar el esquema de esa base con `pg_dump --schema-only`, usando el binario de la imagen de dbmate (`pg_dump` 18.4, compatible con el servidor 18.1)
- [ ] 2.3 Volcar de la misma forma el esquema de la base del despliegue real
- [ ] 2.4 Comparar ambos volcados y resolver cualquier diferencia antes de continuar — si el esquema real derivó de `init.sql`, este es el momento de descubrirlo
- [ ] 2.5 Descartar la base limpia de prueba

## 3. Agregar el servicio de migraciones a compose

- [ ] 3.1 En `compose.yaml`, agregar un servicio que use `ghcr.io/amacneil/dbmate`, monte `./db:/db` y ejecute `--no-dump-schema up`
- [ ] 3.2 Pasarle `DATABASE_URL` con el mismo patrón que `DB_URL` de la API, agregando `?sslmode=disable` — el driver de Go exige TLS por defecto y la conexión entre containers no lo usa
- [ ] 3.3 Declarar que depende de `aniseek-db` con condición de estar sano
- [ ] 3.4 **No** darle política de reinicio: es un servicio de un solo uso y terminar es su comportamiento correcto; `restart: unless-stopped` lo relanzaría indefinidamente
- [ ] 3.5 Cambiar `aniseek-api` y `aniseek-worker` para que dependan de que el servicio de migraciones haya terminado con éxito, en lugar de depender solo de la base
- [ ] 3.6 Replicar el servicio y las dependencias en `compose.dev.yaml`, con los valores literales que ese archivo ya usa en vez de interpolación de variables

## 4. Eliminar el mecanismo anterior

- [ ] 4.1 Quitar el montaje de `postgres/init.sql` en `/docker-entrypoint-initdb.d/` de `compose.yaml` y de `compose.dev.yaml`
- [ ] 4.2 Eliminar `postgres/init.sql` y el directorio `postgres/` si queda vacío
- [ ] 4.3 Actualizar el `README.md`: la Opción 1 indica copiar `postgres/init.sql`, que dejará de existir
- [ ] 4.4 Confirmar por búsqueda que no queda ninguna referencia a `init.sql` ni a `docker-entrypoint-initdb.d` en el repositorio

## 5. Generar el volcado del esquema

- [ ] 5.1 Construir una base limpia desde las migraciones y generar `db/schema.sql` con el volcado de dbmate
- [ ] 5.2 Versionar `db/schema.sql` junto con la migración inicial

## 6. Verificar en un entorno limpio

- [ ] 6.1 Levantar todo con `docker compose -f compose.dev.yaml up -d --build` sobre una base vacía y confirmar que el esquema se construye enteramente desde las migraciones
- [ ] 6.2 Confirmar en los logs que el servicio de migraciones corre después de que la base está sana, aplica la migración inicial y termina
- [ ] 6.3 Confirmar que el servicio de migraciones no se relanza tras terminar
- [ ] 6.4 Confirmar que la API y el worker arrancan después del servicio de migraciones, no en paralelo con él
- [ ] 6.5 Confirmar que la aplicación funciona: login, búsqueda y listado — el esquema y los datos de referencia deben ser equivalentes a los que producía `init.sql`
- [ ] 6.6 Provocar un fallo deliberado en la migración y confirmar que la API y el worker no arrancan; revertir el fallo después

## 7. Dar de alta el despliegue existente

- [ ] 7.1 Respaldar la base del despliegue real antes de tocarla
- [ ] 7.2 **Antes de levantar la versión nueva**, crear la tabla de registro de migraciones e insertar la versión `0001`
- [ ] 7.3 Confirmar que el paso de migración contra esa base no aplica nada y termina con código 0
- [ ] 7.4 Levantar la versión nueva y confirmar que la API y el worker arrancan normalmente
- [ ] 7.5 Confirmar que los datos siguen intactos: usuarios, listas guardadas e historial de descargas

## 8. Cerrar

- [ ] 8.1 Documentar el procedimiento de alta en el `README.md` o en las notas de la versión, para quien actualice desde una versión anterior
- [ ] 8.2 Subir la versión de los servicios siguiendo la convención del repositorio de versionarlos en conjunto
