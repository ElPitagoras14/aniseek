#!/bin/sh
set -e

# La imagen es la autoridad para APP_VERSION: se pisa cualquier valor
# heredado del entorno del despliegue, para que un release posterior nunca
# quede enmascarado por un valor fijado a mano.
export APP_VERSION="$(cat /app-version)"

envsubst < /config.template.js > /usr/share/nginx/html/config.js

exec "$@"
