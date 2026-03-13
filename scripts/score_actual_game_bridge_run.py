#!/usr/bin/env python3
"""Score actual-game bridge runs using realized command outcomes, not optimistic enqueue coverage."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_COMMAND_TYPES = ("place_tower", "sell_tower", "upgrade_tower", "trigger_next_round")
DEFAULT_DECISIONS_PATH = Path(
    "artifacts/x799_prime_actual_game_bridge_eval_x796_vs_base_seed3_fuller_a6000/"
    "adapter_extended_60x15_seed_11/bridge-decisions.json"
)
DEFAULT_REPORT_PATH = Path("artifacts/x800_actual_game_bridge_strict_reassessment/report.json")


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
    rows: List[Dict[str, Any]] = []
    for index, entry in enumerate(payload):
        if not isinstance(entry, dict):
            raise ValueError(f"{path} row {index} must be an object")
        rows.append(entry)
    return rows


def _decision_identity(row: Dict[str, Any]) -> Tuple[str, str, str, Dict[str, Any], int | None]:
    decision = row.get("decision") if isinstance(row.get("decision"), dict) else {}
    provenance = decision.get("provenance") if isinstance(decision.get("provenance"), dict) else {}
    bridge_input = row.get("input") if isinstance(row.get("input"), dict) else {}
    return (
        str(provenance.get("requestId", "")).strip(),
        str(bridge_input.get("playerId", "")).strip(),
        str(decision.get("commandType", "")).strip(),
        decision.get("payload") if isinstance(decision.get("payload"), dict) else {},
        bridge_input.get("stateVersion") if isinstance(bridge_input.get("stateVersion"), int) else None,
    )


def match_command_result(row: Dict[str, Any]) -> Dict[str, Any] | None:
    decision = row.get("decision") if isinstance(row.get("decision"), dict) else {}
    if decision.get("kind") != "command":
        return None

    request_id, player_id, command_type, payload, state_version = _decision_identity(row)
    poll = row.get("poll") if isinstance(row.get("poll"), dict) else {}
    command_results = poll.get("commandResults")
    if not isinstance(command_results, list):
        return None

    if request_id:
        for candidate in reversed(command_results):
            if not isinstance(candidate, dict):
                continue
            command = candidate.get("command") if isinstance(candidate.get("command"), dict) else {}
            provenance = command.get("provenance") if isinstance(command.get("provenance"), dict) else {}
            if str(provenance.get("requestId", "")).strip() == request_id:
                return candidate

    for candidate in reversed(command_results):
        if not isinstance(candidate, dict):
            continue
        command = candidate.get("command") if isinstance(candidate.get("command"), dict) else {}
        provenance = command.get("provenance") if isinstance(command.get("provenance"), dict) else {}
        if str(command.get("playerId", "")).strip() != player_id:
            continue
        if str(command.get("type", "")).strip() != command_type:
            continue
        candidate_payload = command.get("payload") if isinstance(command.get("payload"), dict) else {}
        if candidate_payload != payload:
            continue
        candidate_state_version = provenance.get("stateVersion")
        if state_version is not None and candidate_state_version != state_version:
            continue
        return candidate

    return None


def analyze_rows(rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    decision_kind_counts: Counter[str] = Counter()
    enqueued_command_counts: Counter[str] = Counter()
    strict_success_counts: Counter[str] = Counter()
    failed_command_counts: Counter[str] = Counter()
    failure_reason_counts: Counter[str] = Counter()
    unmatched_command_counts: Counter[str] = Counter()

    for row in rows:
        decision = row.get("decision") if isinstance(row.get("decision"), dict) else {}
        kind = str(decision.get("kind", "unknown"))
        decision_kind_counts[kind] += 1
        if kind != "command":
            continue

        command_type = str(decision.get("commandType", "")).strip()
        enqueue_result = row.get("enqueueResult") if isinstance(row.get("enqueueResult"), dict) else {}
        if enqueue_result.get("success") is True:
            enqueued_command_counts[command_type] += 1

        matched = match_command_result(row)
        if matched is None:
            unmatched_command_counts[command_type] += 1
            continue

        result = matched.get("result") if isinstance(matched.get("result"), dict) else {}
        if result.get("success") is True:
            strict_success_counts[command_type] += 1
            continue

        failed_command_counts[command_type] += 1
        reason = str(result.get("reasonCode") or result.get("reason") or "UNKNOWN").strip() or "UNKNOWN"
        failure_reason_counts[f"{command_type}:{reason}"] += 1

    strict_success_by_type = {command_type: strict_success_counts.get(command_type, 0) > 0 for command_type in REQUIRED_COMMAND_TYPES}
    optimistic_enqueued_by_type = {command_type: enqueued_command_counts.get(command_type, 0) > 0 for command_type in REQUIRED_COMMAND_TYPES}
    strict_success_observed = [command_type for command_type in REQUIRED_COMMAND_TYPES if strict_success_by_type[command_type]]
    optimistic_observed = [command_type for command_type in REQUIRED_COMMAND_TYPES if optimistic_enqueued_by_type[command_type]]
    command_decision_count = sum(1 for row in rows if isinstance(row.get("decision"), dict) and row["decision"].get("kind") == "command")

    return {
        "decision_count": len(rows),
        "command_decision_count": command_decision_count,
        "decision_kind_counts": dict(sorted(decision_kind_counts.items())),
        "optimistic_enqueued_counts": dict(sorted(enqueued_command_counts.items())),
        "strict_success_counts": dict(sorted(strict_success_counts.items())),
        "failed_command_counts": dict(sorted(failed_command_counts.items())),
        "unmatched_command_counts": dict(sorted(unmatched_command_counts.items())),
        "failure_reason_counts": dict(sorted(failure_reason_counts.items())),
        "optimistic_enqueued_coverage": {
            "required": list(REQUIRED_COMMAND_TYPES),
            "observed": optimistic_observed,
            "by_type": optimistic_enqueued_by_type,
        },
        "strict_success_coverage": {
            "required": list(REQUIRED_COMMAND_TYPES),
            "observed": strict_success_observed,
            "by_type": strict_success_by_type,
        },
        "strict_status": "pass" if all(strict_success_by_type.values()) else "fail",
    }


def analyze_paths(paths: Sequence[Path | str]) -> Dict[str, Any]:
    resolved_paths = [_resolve_path(path) for path in paths]
    per_source: Dict[str, Any] = {}
    aggregate_success = Counter()
    aggregate_enqueued = Counter()
    aggregate_failure_reasons = Counter()
    aggregate_failed = Counter()
    aggregate_unmatched = Counter()
    total_rows = 0
    total_command_rows = 0

    for path in resolved_paths:
        rows = _load_rows(path)
        source_report = analyze_rows(rows)
        per_source[_display_path(path)] = source_report
        total_rows += source_report["decision_count"]
        total_command_rows += source_report["command_decision_count"]
        aggregate_success.update(source_report["strict_success_counts"])
        aggregate_enqueued.update(source_report["optimistic_enqueued_counts"])
        aggregate_failure_reasons.update(source_report["failure_reason_counts"])
        aggregate_failed.update(source_report["failed_command_counts"])
        aggregate_unmatched.update(source_report["unmatched_command_counts"])

    aggregate_success_by_type = {command_type: aggregate_success.get(command_type, 0) > 0 for command_type in REQUIRED_COMMAND_TYPES}
    aggregate_enqueued_by_type = {command_type: aggregate_enqueued.get(command_type, 0) > 0 for command_type in REQUIRED_COMMAND_TYPES}

    return {
        "schema_version": "td.actual_game.bridge_strict_score.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_paths": [_display_path(path) for path in resolved_paths],
        "decision_count": total_rows,
        "command_decision_count": total_command_rows,
        "strict_success_counts": dict(sorted(aggregate_success.items())),
        "optimistic_enqueued_counts": dict(sorted(aggregate_enqueued.items())),
        "failed_command_counts": dict(sorted(aggregate_failed.items())),
        "unmatched_command_counts": dict(sorted(aggregate_unmatched.items())),
        "failure_reason_counts": dict(sorted(aggregate_failure_reasons.items())),
        "strict_success_coverage": {
            "required": list(REQUIRED_COMMAND_TYPES),
            "observed": [command_type for command_type in REQUIRED_COMMAND_TYPES if aggregate_success_by_type[command_type]],
            "by_type": aggregate_success_by_type,
        },
        "optimistic_enqueued_coverage": {
            "required": list(REQUIRED_COMMAND_TYPES),
            "observed": [command_type for command_type in REQUIRED_COMMAND_TYPES if aggregate_enqueued_by_type[command_type]],
            "by_type": aggregate_enqueued_by_type,
        },
        "strict_status": "pass" if all(aggregate_success_by_type.values()) else "fail",
        "per_source": per_source,
    }


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--decisions",
        action="append",
        default=[],
        help="Bridge decision JSON path. Repeat to aggregate multiple runs.",
    )
    parser.add_argument(
        "--report",
        default=str(DEFAULT_REPORT_PATH),
        help=f"Aggregate report path. Default: {DEFAULT_REPORT_PATH}",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    decision_paths = args.decisions or [str(DEFAULT_DECISIONS_PATH)]
    report = analyze_paths(decision_paths)
    report_path = _resolve_path(args.report)
    report["report_path"] = _display_path(report_path)
    write_json(report_path, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
