#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")"

uv run alembic upgrade head

docker compose -p deliverx -f docker-compose-app.yml up --build --remove-orphans
