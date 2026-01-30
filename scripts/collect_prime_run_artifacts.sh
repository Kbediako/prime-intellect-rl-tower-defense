#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <RUN_ID> [OUT_DIR]" >&2
  exit 1
fi

RUN_ID="$1"
OUT_DIR="${2:-artifacts/$RUN_ID}"

mkdir -p "$OUT_DIR"
export OUT_DIR

warn() {
  echo "warn: $*" >&2
}

if ! prime rl progress "$RUN_ID" > "$OUT_DIR/progress.json"; then
  warn "progress unavailable"
fi

if ! prime rl metrics "$RUN_ID" > "$OUT_DIR/metrics.json"; then
  warn "metrics unavailable"
fi

if ! prime rl logs "$RUN_ID" -n 2000 > "$OUT_DIR/logs.txt"; then
  warn "logs unavailable"
fi

steps=$(python3 - <<'PY'
import json
import os
from pathlib import Path
out_dir = Path(os.environ.get("OUT_DIR", ""))
if not out_dir:
    print("")
    raise SystemExit(0)
path = out_dir / "progress.json"
if not path.exists():
    print("")
    raise SystemExit(0)
try:
    data = json.loads(path.read_text())
except Exception:
    print("")
    raise SystemExit(0)
steps = data.get("steps_with_samples", []) or []
if not steps:
    print("")
    raise SystemExit(0)
steps = sorted(steps)
if len(steps) <= 3:
    chosen = steps
else:
    chosen = [steps[0], steps[len(steps)//2], steps[-1]]
print(" ".join(str(s) for s in chosen))
PY
)

if [[ -n "$steps" ]]; then
  for step in $steps; do
    if ! prime rl rollouts "$RUN_ID" -s "$step" -n 100 > "$OUT_DIR/rollouts_step_${step}.json"; then
      warn "rollouts missing for step $step"
    fi
  done
else
  warn "no sample steps detected; skipping rollout download"
fi

OUT_DIR="$OUT_DIR" python3 - <<'PY'
import json
import re
import os
from pathlib import Path

out_dir = Path(os.environ.get("OUT_DIR", ""))
if not out_dir:
    raise SystemExit("OUT_DIR not set")
summary_path = out_dir / "summary.md"

metrics_path = out_dir / "metrics.json"
progress_path = out_dir / "progress.json"

lines = ["# Run Artifacts Summary", ""]

if progress_path.exists():
    try:
        progress = json.loads(progress_path.read_text())
        lines.append(f"- latest_step: {progress.get('latest_step')}")
        lines.append(f"- steps_with_samples: {progress.get('steps_with_samples')}")
    except Exception:
        lines.append("- latest_step: <parse failed>")

if metrics_path.exists():
    try:
        data = json.loads(metrics_path.read_text())
        metrics = data.get("metrics", [])
        def avg(key):
            vals = [m.get(key) for m in metrics if m.get(key) is not None]
            return sum(vals) / len(vals) if vals else None
        lines.append("")
        lines.append("## Metric Averages")
        for key in ["reward/mean", "metrics/_reward_from_action", "metrics/_format_reward", "error/mean", "is_truncated/mean"]:
            value = avg(key)
            lines.append(f"- {key}: {value}")
    except Exception:
        lines.append("- metrics: <parse failed>")

MAX_ACTION_CHARS = 400
ACTION_TYPES = {"build", "upgrade", "sell", "start_round", "noop"}

def _coerce_int(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    if isinstance(v, str) and v.isdigit():
        return int(v)
    return None


def _normalize_action(action):
    if not isinstance(action, dict):
        return None
    action_type = action.get("type")
    if action_type not in ACTION_TYPES:
        return None
    if action_type == "build":
        x = _coerce_int(action.get("x"))
        y = _coerce_int(action.get("y"))
        tower_type = action.get("tower_type")
        if x is None or y is None or not isinstance(tower_type, str):
            return None
        return {"type": "build", "tower_type": tower_type, "x": x, "y": y}
    if action_type == "upgrade":
        tower_id = _coerce_int(action.get("tower_id"))
        path = action.get("path")
        if tower_id is None or path not in {"a", "b", "c"}:
            return None
        return {"type": "upgrade", "tower_id": tower_id, "path": path}
    if action_type == "sell":
        tower_id = _coerce_int(action.get("tower_id"))
        if tower_id is None:
            return None
        return {"type": "sell", "tower_id": tower_id}
    if action_type == "start_round":
        return {"type": "start_round"}
    return {"type": "noop"}


def _extract_json_object(text):
    raw = text.strip()
    if raw.startswith("{") and raw.endswith("}") and len(raw) <= MAX_ACTION_CHARS:
        try:
            return json.loads(raw)
        except Exception:
            pass
    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if not match:
        return None
    candidate = match.group(0)
    if len(candidate) > MAX_ACTION_CHARS:
        return None
    try:
        return json.loads(candidate)
    except Exception:
        return None


def parse_action(text):
    action = _extract_json_object(text)
    if action is None:
        return None
    return _normalize_action(action)

rollout_paths = list(out_dir.glob("rollouts_step_*.json"))
if rollout_paths:
    action_types = {}
    invalid = 0
    total = 0
    for path in rollout_paths:
        try:
            data = json.loads(path.read_text(), strict=False)
        except Exception:
            continue
        for sample in data.get("samples", []):
            comp = sample.get("completion", "")
            try:
                msgs = json.loads(comp, strict=False)
                content = msgs[-1].get("content", "") if isinstance(msgs, list) and msgs else comp
            except Exception:
                content = comp
            action = parse_action(content)
            total += 1
            if action is None:
                invalid += 1
            else:
                action_types[action["type"]] = action_types.get(action["type"], 0) + 1
    lines.append("")
    lines.append("## Rollout Action Mix")
    lines.append(f"- samples: {total}")
    lines.append(f"- invalid_json_rate: {invalid / total if total else None}")
    lines.append(f"- action_counts: {action_types}")

summary_path.write_text("\n".join(lines) + "\n")
print(f"wrote_summary={summary_path}")
PY
