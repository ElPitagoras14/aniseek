FROM ghcr.io/amacneil/dbmate

# El directorio del repositorio viaja adentro de la imagen: un despliegue con
# imagenes pre-construidas no necesita las migraciones en el host.
# La ruta interna es /db, el default de dbmate, asi que no hace falta declarar
# DBMATE_MIGRATIONS_DIR ni DBMATE_SCHEMA_FILE.
COPY migrations/ /db/migrations/
COPY schema.sql /db/schema.sql

# Sin ENTRYPOINT ni CMD: se heredan los de la imagen base para que el `command`
# del compose (["--no-dump-schema", "up"]) siga funcionando sin cambios.
