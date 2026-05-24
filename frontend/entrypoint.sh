#!/bin/sh
set -e

envsubst < /usr/share/nginx/html/config.template.js > /usr/share/nginx/html/config.js

exec "$@"
