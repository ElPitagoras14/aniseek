# Version exacta a proposito: esta imagen se reconstruye en cada bump de version
# del proyecto, asi que sin tag el rebuild traeria un dbmate distinto en silencio.
# Las otras tres referencias a la imagen publica —compose.dev.yaml, la suite de
# pruebas del backend y el README— declaran esta misma version; subirla implica
# tocar las cuatro (`grep -rn "amacneil/dbmate"`).
FROM ghcr.io/amacneil/dbmate:2.35.0

# El directorio del repositorio viaja adentro de la imagen: un despliegue con
# imagenes pre-construidas no necesita las migraciones en el host.
# La ruta interna es /db, el default de dbmate, asi que no hace falta declarar
# DBMATE_MIGRATIONS_DIR ni DBMATE_SCHEMA_FILE.
COPY migrations/ /db/migrations/
COPY schema.sql /db/schema.sql

# Sin ENTRYPOINT ni CMD: se heredan los de la imagen base para que el `command`
# del compose (["--no-dump-schema", "up"]) siga funcionando sin cambios.
