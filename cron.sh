#!/usr/bin/env bash
set -euo pipefail

# Example cron entry (MSK 08:00 daily):
# 0 5 * * * /usr/bin/env TZ=Europe/Moscow /bin/bash -c '/path/to/typefeed-parser/cron.sh >> /var/log/typefeed.log 2>&1'

cd "$(dirname "$0")"
source .venv/bin/activate 2>/dev/null || true

# Hardcoded for deployment; override via env if needed.
export TYPEFEED_TELEGRAM_BOT_TOKEN="${TYPEFEED_TELEGRAM_BOT_TOKEN:-8210347073:AAHW0QYVVNkELFabPbYfBIYRhc1BV0PubiY}"
export TYPEFEED_TELEGRAM_CHAT_ID="${TYPEFEED_TELEGRAM_CHAT_ID--1003525198405}"

# Skip if no network
if ! ping -c1 -W2 1.1.1.1 >/dev/null 2>&1; then
  echo "$(date -Is) [WARN] No network, skip run" >&2
  exit 1
fi

# Run at most once per ~20h to catch up missed days when machine slept.
LAST_RUN_FILE=".last_run"
now_ts=$(date +%s)
if [[ -f "$LAST_RUN_FILE" ]]; then
  last_ts=$(cat "$LAST_RUN_FILE" 2>/dev/null || echo 0)
  delta=$((now_ts - last_ts))
  if (( delta < 72000 )); then
    echo "$(date -Is) [INFO] Recently ran ($delta s ago), skip."
    exit 0
  fi
fi

python parser.py --collect --notify --json feed.json && echo "$now_ts" > "$LAST_RUN_FILE"

