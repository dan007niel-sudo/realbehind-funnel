#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/root/realbehind-funnel}"
cd "$APP_DIR"

wait_for_url() {
  local url="$1"
  local label="$2"

  for attempt in $(seq 1 30); do
    if response=$(curl -fsS "$url" 2>/tmp/realbehind-healthcheck.err); then
      echo "$response"
      return 0
    fi
    if [ "$attempt" -eq 30 ]; then
      echo "$label healthcheck failed after $attempt attempts."
      cat /tmp/realbehind-healthcheck.err
      docker compose ps
      docker compose logs --tail=80 realbehind
      exit 1
    fi
    sleep 1
  done
}

if [ -d .git ]; then
  git fetch origin main
  git reset --hard origin/main
else
  echo "WARN: $APP_DIR is not a Git checkout; using current files on server."
fi

mkdir -p data
docker compose up -d --build realbehind

wait_for_url "http://127.0.0.1:8010/health" "Internal"
wait_for_url "https://realbehind.com/health" "Public"

echo
echo "Deploy complete."
