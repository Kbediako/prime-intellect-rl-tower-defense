#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:-$PWD}"
BUNDLE_PATH="${BUNDLE_PATH:?}"
TRAIN_EXITCODE_PATH="${TRAIN_EXITCODE_PATH:?}"
OUTPUT_ROOT="${OUTPUT_ROOT:?}"

cd "$ROOT_DIR"

set +e
bash scripts/run_actual_game_command_sft_prime_pod.sh "$ROOT_DIR"
status="$?"
set -e

printf '%s\n' "$status" > "$TRAIN_EXITCODE_PATH"
if [[ "$status" -eq 0 ]]; then
  tar -czf "$BUNDLE_PATH" "$OUTPUT_ROOT"
fi

exit "$status"
