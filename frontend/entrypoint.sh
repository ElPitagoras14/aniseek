#!/bin/sh
set -e

envsubst < /config.template.js > /usr/share/nginx/html/config.js

exec "$@"
