#!/usr/bin/env bash
set -euo pipefail

docker compose -f compose/docker-compose.yml --env-file compose/.env down
