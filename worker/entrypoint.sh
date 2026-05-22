#!/bin/sh
set -e

ANIMES_FOLDER=${ANIMES_FOLDER:-/animes}
DRAMATIQ_PROCESSES=${DRAMATIQ_PROCESSES:-2}
DRAMATIQ_THREADS=${DRAMATIQ_THREADS:-4}

mkdir -p ${ANIMES_FOLDER}
chown -R appuser:appuser ${ANIMES_FOLDER}

exec su appuser -c "dramatiq main --processes ${DRAMATIQ_PROCESSES} --threads ${DRAMATIQ_THREADS}"
