#!/usr/bin/env python3
"""Filter bridge-decision rows down to exact realized command failures."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence

import score_actual_game_bridge_run as bridge_score


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = Path("artifacts/x845_actual_game_bridge_failures/bridge-decisions.json")
DEFAULT_REPORT_PATH = Path("artifacts/x845_actual_game_bridge_failures/filter_report.json")


def _resolve_path(raw_path: Path | str) -> Path:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _load_rows(path: Path) -> List[Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{path} must contain a top-level list")
    return [row for row in payload if isinstance(row, dict)]


def _decision(row: Dict[str, Any]) -> Dict[str, Any]:
    decision = row.get("decision")
    return decision if isinstance(decision, dict) else {}


def _result_reason(matched: Dict[str, Any]) -> str:
    result = matched.get("result")
    if not isinstance(result, dict):
        return "UNKNOWN"
    reason = str(result.get("reasonCode") or result.get("reason") or "UNKNOWN").strip()
    return reason or "UNKNOWN"


def filter_rows(
    *,
    source_paths: Sequence[Path | str],
    command_types: Sequence[str] = (),
    failure_reasons: Sequence[str] = (),
) -> Dict[str, Any]:
    allowed_command_types = {value.strip() for value in command_types if value.strip()}
    allowed_failure_reasons = {value.strip() for value in failure_reasons if value.strip()}

    selected_rows: List[Dict[str, Any]] = []
    command_type_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    selected_by_source: Counter[str] = Counter()

    resolved_paths = [_resolve_path(path) for path in source_paths]
    for path in resolved_paths:
        source_label = _display_path(path)
        for row in _load_rows(path):
            decision = _decision(row)
            if decision.get("kind") != "command":
                continue

            command_type = str(decision.get("commandType", "")).strip()
            if allowed_command_types and command_type not in allowed_command_types:
                continue

            matched = bridge_score.match_command_result(row)
            if matched is None:
                continue

            result = matched.get("result")
            if not isinstance(result, dict) or result.get("success") is True:
                continue

            reason = _result_reason(matched)
            reason_key = f"{command_type}:{reason}"
            if allowed_failure_reasons and reason_key not in allowed_failure_reasons:
                continue

            selected_rows.append(row)
            command_type_counts[command_type] += 1
            reason_counts[reason_key] += 1
            selected_by_source[source_label] += 1

    return {
        "rows": selected_rows,
        "report": {
            "schema_version": "td.actual_game.bridge_failure_filter_report.v2",
            "source_paths": [_display_path(path) for path in resolved_paths],
            "selected_row_count": len(selected_rows),
            "selected_by_source": dict(sorted(selected_by_source.items())),
            "command_type_counts": dict(sorted(command_type_counts.items())),
            "reason_counts": dict(sorted(reason_counts.items())),
            "filters": {
                "command_types": sorted(allowed_command_types),
                "failure_reasons": sorted(allowed_failure_reasons),
            },
        },
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Bridge decision JSON path. Repeat to merge multiple sources.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_OUTPUT_PATH),
        help=f"Filtered bridge decision JSON path. Default: {DEFAULT_OUTPUT_PATH}",
    )
    parser.add_argument(
        "--report",
        default=str(DEFAULT_REPORT_PATH),
        help=f"Filter report JSON path. Default: {DEFAULT_REPORT_PATH}",
    )
    parser.add_argument(
        "--command-type",
        action="append",
        default=[],
        help="Optional command type filter. Repeatable.",
    )
    parser.add_argument(
        "--failure-reason",
        action="append",
        default=[],
        help="Optional failure reason filter in commandType:REASON form. Repeatable.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    source_paths = args.source or []
    if not source_paths:
        raise SystemExit("--source is required")

    filtered = filter_rows(
        source_paths=source_paths,
        command_types=args.command_type,
        failure_reasons=args.failure_reason,
    )
    out_path = _resolve_path(args.out)
    report_path = _resolve_path(args.report)
    report = filtered["report"]
    report["output_path"] = _display_path(out_path)
    report["report_path"] = _display_path(report_path)
    write_json(out_path, filtered["rows"])
    write_json(report_path, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
