#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/root/realbehind-funnel}"
cd "$APP_DIR"

if [ -d .git ]; then
  git fetch origin main
  git reset --hard origin/main
else
  echo "WARN: $APP_DIR is not a Git checkout; using current files on server."
fi

mkdir -p data
docker compose up -d --build realbehind

for attempt in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:8010/health; then
    break
  fi
  if [ "$attempt" -eq 30 ]; then
    echo "Healthcheck failed after $attempt attempts."
    docker compose ps
    docker compose logs --tail=80 realbehind
    exit 1
  fi
  sleep 1
done

echo
curl -fsS https://realbehind.com/health

echo
echo "Deploy complete."
