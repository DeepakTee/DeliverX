#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")"

docker compose -p deliverx-setup -f docker-compose-setup.yml up -d --wait