#!/bin/sh
set -e

ANIMES_FOLDER=${ANIMES_FOLDER:-/animes}

mkdir -p ${ANIMES_FOLDER}
chown -R appuser:appuser ${ANIMES_FOLDER}

exec su appuser -c "python main.py"
