#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:-$PWD}"
MODEL_NAME="${MODEL_NAME:-Qwen/Qwen3-4B-Instruct-2507}"
POST_SUCCESS_SLEEP_SECS="${POST_SUCCESS_SLEEP_SECS:-180}"
BUILD_DATASETS="${BUILD_DATASETS:-1}"

TRAIN_EXAMPLES_PATH="${TRAIN_EXAMPLES_PATH:-src/prime_td_env/data/actual_game_command/train_examples.json}"
EVAL_EXAMPLES_PATH="${EVAL_EXAMPLES_PATH:-src/prime_td_env/data/actual_game_command/eval_examples.json}"

TRAIN_JSONL_PATH="${TRAIN_JSONL_PATH:-artifacts/x532_actual_game_command_sft_inputs/train_messages.jsonl}"
EVAL_JSONL_PATH="${EVAL_JSONL_PATH:-artifacts/x532_actual_game_command_sft_inputs/eval_messages.jsonl}"
TRAIN_EXPORT_REPORT_PATH="${TRAIN_EXPORT_REPORT_PATH:-artifacts/x532_actual_game_command_sft_inputs/train_export_report.json}"
EVAL_EXPORT_REPORT_PATH="${EVAL_EXPORT_REPORT_PATH:-artifacts/x532_actual_game_command_sft_inputs/eval_export_report.json}"

OUTPUT_ROOT="${OUTPUT_ROOT:-artifacts/x533_actual_game_command_sft_run}"
OUTPUT_DIR="${OUTPUT_DIR:-$OUTPUT_ROOT/adapter}"
TRAIN_REPORT_PATH="${TRAIN_REPORT_PATH:-$OUTPUT_ROOT/train_report.json}"
EVAL_REPORT_PATH="${EVAL_REPORT_PATH:-$OUTPUT_ROOT/eval_report.json}"
EVAL_PREDICTIONS_OUT="${EVAL_PREDICTIONS_OUT:-$OUTPUT_ROOT/eval_predictions.jsonl}"
EVAL_ROWS_OUT="${EVAL_ROWS_OUT:-$OUTPUT_ROOT/eval_rows.jsonl}"

cd "$ROOT_DIR"

mkdir -p \
  "$(dirname "$TRAIN_JSONL_PATH")" \
  "$(dirname "$EVAL_JSONL_PATH")" \
  "$(dirname "$TRAIN_EXPORT_REPORT_PATH")" \
  "$(dirname "$EVAL_EXPORT_REPORT_PATH")" \
  "$OUTPUT_ROOT"

ensure_python_pip() {
  if python3 -m pip --version >/dev/null 2>&1; then
    return 0
  fi

  python3 -m ensurepip --upgrade >/dev/null 2>&1 || true
  if python3 -m pip --version >/dev/null 2>&1; then
    return 0
  fi

  if command -v apt-get >/dev/null 2>&1; then
    export DEBIAN_FRONTEND=noninteractive
    apt_get_retry update
    apt_get_retry install -y python3-pip
  fi

  python3 -m pip --version >/dev/null 2>&1
}

apt_get_retry() {
  local attempt
  local log_file
  log_file="$(mktemp)"
  for attempt in $(seq 1 30); do
    if apt-get "$@" >"$log_file" 2>&1; then
      cat "$log_file"
      rm -f "$log_file"
      return 0
    fi
    cat "$log_file" >&2
    if ! grep -qi "Could not get lock" "$log_file"; then
      rm -f "$log_file"
      return 1
    fi
    sleep 5
  done
  rm -f "$log_file"
  return 1
}

ensure_python_pip

python3 -m pip install --no-compile --upgrade pip
python3 -m pip install --no-compile \
  "torch>=2.6" \
  "transformers>=4.49" \
  "accelerate>=1.5" \
  "datasets>=3.0" \
  "peft>=0.14" \
  "bitsandbytes>=0.45" \
  "jinja2>=3.1.0"

if [[ "$BUILD_DATASETS" == "1" ]]; then
  python3 scripts/export_actual_game_command_sft_dataset.py \
    --examples "$TRAIN_EXAMPLES_PATH" \
    --output "$TRAIN_JSONL_PATH" \
    --report "$TRAIN_EXPORT_REPORT_PATH"

  python3 scripts/export_actual_game_command_sft_dataset.py \
    --examples "$EVAL_EXAMPLES_PATH" \
    --output "$EVAL_JSONL_PATH" \
    --report "$EVAL_EXPORT_REPORT_PATH"
else
  test -f "$TRAIN_JSONL_PATH"
  test -f "$EVAL_JSONL_PATH"
fi

python3 scripts/train_actual_game_command_sft.py \
  --model "$MODEL_NAME" \
  --train-jsonl "$TRAIN_JSONL_PATH" \
  --eval-jsonl "$EVAL_JSONL_PATH" \
  --train-examples-path "$TRAIN_EXAMPLES_PATH" \
  --train-export-report "$TRAIN_EXPORT_REPORT_PATH" \
  --examples "$EVAL_EXAMPLES_PATH" \
  --output-dir "$OUTPUT_DIR" \
  --report "$TRAIN_REPORT_PATH" \
  --eval-report "$EVAL_REPORT_PATH" \
  --eval-predictions-out "$EVAL_PREDICTIONS_OUT" \
  --eval-rows-out "$EVAL_ROWS_OUT" \
  --epochs 6 \
  --learning-rate 2e-4 \
  --batch-size 4 \
  --eval-batch-size 4 \
  --grad-accum 4 \
  --max-seq-len 2048 \
  --load-in-4bit

du -sh "$OUTPUT_DIR"
ls -lh "$OUTPUT_ROOT"

if [[ "$POST_SUCCESS_SLEEP_SECS" =~ ^[0-9]+$ ]] && [ "$POST_SUCCESS_SLEEP_SECS" -gt 0 ]; then
  echo "Holding pod open for ${POST_SUCCESS_SLEEP_SECS}s to allow artifact extraction."
  sleep "$POST_SUCCESS_SLEEP_SECS"
fi
