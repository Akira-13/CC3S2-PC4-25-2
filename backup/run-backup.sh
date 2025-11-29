#!/usr/bin/env bash
set -euo pipefail

# Ejecuta el contenedor de backup una sola vez y deja el artefacto en ./backups
docker compose -f compose/docker-compose.yml --env-file compose/.env run --rm backup
