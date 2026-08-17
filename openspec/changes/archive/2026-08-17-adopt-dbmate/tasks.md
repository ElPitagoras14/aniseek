## 1. Crear la migración inicial

- [x] 1.1 Crear `db/migrations/0001_create_initial_schema.sql` con el contenido íntegro de `postgres/init.sql` bajo la marca `-- migrate:up`: las 13 tablas, los 9 índices y los tres bloques de datos de referencia (`role_types`, `related_types`, `avatars`)
- [x] 1.2 Incluir la marca `-- migrate:down` sin instrucciones debajo, dejando la migración inicial deliberadamente irreversible
- [x] 1.3 Confirmar que el SQL se copió sin modificaciones: este change no altera el esquema, solo el mecanismo por el que se aplica

## 2. Verificar que la migración reproduce el esquema real

- [x] 2.1 Levantar una base de datos limpia con `postgres:18.1-alpine` y aplicarle la migración inicial con `ghcr.io/amacneil/dbmate --no-dump-schema up` — hecho vía `compose.dev.yaml` (su `aniseek-db` no tiene volumen persistente, así que arrancó vacía)
- [x] 2.2 Volcar el esquema de esa base con `pg_dump --schema-only`, usando el binario de la imagen de dbmate (`pg_dump` 18.4, compatible con el servidor 18.1) — es exactamente `db/schema.sql`, generado en la tarea 5.1
- [x] 2.3 Volcar de la misma forma el esquema de la base del despliegue real — hecho contra el `aniseek-db` real en `192.168.1.100:4002` (solo lectura, `pg_dump --schema-only --no-owner --no-privileges` con el binario de la imagen de dbmate)
- [x] 2.4 Comparar ambos volcados y resolver cualquier diferencia antes de continuar — comparados; **cero diferencias estructurales** una vez descontado el ruido cosmético esperado (token `\restrict` aleatorio en cada corrida de `pg_dump`, y el comentario de cabecera que `dbmate dump` omite). El esquema real no derivó de `init.sql`; coincide exactamente con lo que produce la migración
- [x] 2.5 Descartar la base limpia de prueba — no aplica: la base limpia es la del stack de desarrollo (`compose.dev.yaml`), que no tiene volumen persistente y por diseño se reconstruye vacía en cada `up`; se deja corriendo como entorno de dev funcional, no como scratch a descartar

## 3. Agregar el servicio de migraciones a compose

- [x] 3.1 En `compose.yaml`, agregar un servicio que use `ghcr.io/amacneil/dbmate`, monte `./db:/db` y ejecute `--no-dump-schema up`
- [x] 3.2 Pasarle `DATABASE_URL` con el mismo patrón que `DB_URL` de la API, agregando `?sslmode=disable` — el driver de Go exige TLS por defecto y la conexión entre containers no lo usa
- [x] 3.3 Declarar que depende de `aniseek-db` con condición de estar sano
- [x] 3.4 **No** darle política de reinicio: es un servicio de un solo uso y terminar es su comportamiento correcto; `restart: unless-stopped` lo relanzaría indefinidamente
- [x] 3.5 Cambiar `aniseek-api` y `aniseek-worker` para que dependan de que el servicio de migraciones haya terminado con éxito, en lugar de depender solo de la base
- [x] 3.6 Replicar el servicio y las dependencias en `compose.dev.yaml`, con los valores literales que ese archivo ya usa en vez de interpolación de variables

## 4. Eliminar el mecanismo anterior

- [x] 4.1 Quitar el montaje de `postgres/init.sql` en `/docker-entrypoint-initdb.d/` de `compose.yaml` y de `compose.dev.yaml`
- [x] 4.2 Eliminar `postgres/init.sql` y el directorio `postgres/` si queda vacío
- [x] 4.3 Actualizar el `README.md`: la Opción 1 indica copiar `postgres/init.sql`, que dejará de existir
- [x] 4.4 Confirmar por búsqueda que no queda ninguna referencia a `init.sql` ni a `docker-entrypoint-initdb.d` en el repositorio

## 5. Generar el volcado del esquema

- [x] 5.1 Construir una base limpia desde las migraciones y generar `db/schema.sql` con el volcado de dbmate
- [x] 5.2 Versionar `db/schema.sql` junto con la migración inicial

## 6. Verificar en un entorno limpio

- [x] 6.1 Levantar todo con `docker compose -f compose.dev.yaml up -d --build` sobre una base vacía y confirmar que el esquema se construye enteramente desde las migraciones
- [x] 6.2 Confirmar en los logs que el servicio de migraciones corre después de que la base está sana, aplica la migración inicial y termina
- [x] 6.3 Confirmar que el servicio de migraciones no se relanza tras terminar
- [x] 6.4 Confirmar que la API y el worker arrancan después del servicio de migraciones, no en paralelo con él
- [x] 6.5 Confirmar que la aplicación funciona: login, búsqueda y listado — el esquema y los datos de referencia deben ser equivalentes a los que producía `init.sql`
- [x] 6.6 Provocar un fallo deliberado en la migración y confirmar que la API y el worker no arrancan; revertir el fallo después

## 7. Dar de alta el despliegue existente

El despliegue real es `aniseek-db` en `192.168.1.100:4002` (Dokploy). Su esquema ya se comparó contra la migración en 2.3/2.4 y coincide exactamente. Alta ya realizada (7.1-7.3); 7.4/7.5 quedan pendientes porque requieren desplegar el `compose.yaml` nuevo en Dokploy, algo fuera del alcance de este entorno.

- [x] 7.1 Respaldar la base del despliegue real antes de tocarla — `pg_dump` completo guardado localmente (13 tablas con datos, ~550KB)
- [x] 7.2 **Antes de levantar la versión nueva**, crear la tabla de registro de migraciones e insertar la versión `0001` — hecho: `CREATE TABLE IF NOT EXISTS public.schema_migrations` + `INSERT ('0001')`
- [x] 7.3 Confirmar que el paso de migración contra esa base no aplica nada y termina con código 0 — confirmado: `dbmate --no-dump-schema up` contra la base real, exit 0, sin aplicar ninguna migración
- [ ] 7.4 Levantar la versión nueva y confirmar que la API y el worker arrancan normalmente — **pendiente**: requiere desplegar el `compose.yaml` actualizado en Dokploy (192.168.1.100), fuera del alcance de este entorno
- [ ] 7.5 Confirmar que los datos siguen intactos: usuarios, listas guardadas e historial de descargas — parcialmente verificado ya (1 usuario, 101 animes, 2375 episodios, 74 descargas, 28 guardados, sin cambios tras 7.2/7.3); confirmar de nuevo después del deploy de 7.4

## 8. Cerrar

- [x] 8.1 Documentar el procedimiento de alta en el `README.md` o en las notas de la versión, para quien actualice desde una versión anterior
- [x] 8.2 Subir la versión de los servicios siguiendo la convención del repositorio de versionarlos en conjunto
