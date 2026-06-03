#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
RAW_DIR="$SCRIPT_DIR/raw"
LOG_FILE="$SCRIPT_DIR/harvest.log"

DELAY_SECONDS="${ARXIV_HARVEST_DELAY_SECONDS:-30}"
INITIAL_COOLDOWN_SECONDS="${ARXIV_INITIAL_COOLDOWN_SECONDS:-1800}"

IDS=(
  "2605.26289"
  "2605.03375"
  "2605.18071"
  "2604.26557"
  "2603.17803"
  "2605.18421"
  "2604.15774"
  "2508.09442"
  "2508.08438"
  "2511.16682"
  "2511.07885"
)

mkdir -p "$RAW_DIR"

log() {
  printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$LOG_FILE"
}

log "rate-safe arXiv harvest starting"
log "delay_seconds=$DELAY_SECONDS initial_cooldown_seconds=$INITIAL_COOLDOWN_SECONDS"
log "arxiv_version=$(arxiv-pp-cli --version)"

if (( INITIAL_COOLDOWN_SECONDS > 0 )); then
  log "cooling down before first request"
  sleep "$INITIAL_COOLDOWN_SECONDS"
fi

for id in "${IDS[@]}"; do
  out_file="$RAW_DIR/arxiv-$id.json"
  if [[ -s "$out_file" ]]; then
    log "skip id=$id existing=$out_file"
    continue
  fi

  log "fetch id=$id"
  set +e
  output="$(
    arxiv-pp-cli query \
      --id-list "$id" \
      --max-results 1 \
      --timeout 60s \
      --agent \
      --deliver "file:$out_file" 2>&1
  )"
  status=$?
  set -e

  printf '%s\n' "$output" >> "$LOG_FILE"

  if [[ "$status" -ne 0 ]]; then
    if printf '%s\n' "$output" | grep -q 'HTTP 429\|Rate exceeded\|rate limited'; then
      log "stop id=$id status=$status reason=rate-limited"
      exit 75
    fi
    log "stop id=$id status=$status reason=provider-error"
    exit "$status"
  fi

  log "saved id=$id file=$out_file"
  sleep "$DELAY_SECONDS"
done

log "rate-safe arXiv harvest complete"
