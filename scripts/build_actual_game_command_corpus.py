#!/usr/bin/env python3
"""Build a deduplicated Env A corpus from real-game bridge decision artifacts."""

from __future__ import annotations

import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from prime_td_env.actual_game_env import (
    _sync_known_tower_owners,
    create_command_summary_from_bridge_input,
    normalize_command_decision,
    validate_bridge_input,
)


EXAMPLE_SCHEMA_VERSION = "td.actual_game.command_examples.v1"
DEFAULT_SOURCE_PATHS = [
    Path("artifacts/x512_x504_real_game_probe/extended_60x15/bridge-decisions.json"),
    Path("artifacts/x513_base_qwen3_4b_real_game_probe/bridge-decisions.json"),
    Path("artifacts/x518_x486_real_game_probe/extended_60x15/bridge-decisions.json"),
]
DEFAULT_OUTPUT_PATH = Path("artifacts/x523_actual_game_command_corpus/actual_game_command_examples.json")
DEFAULT_REPORT_PATH = Path("artifacts/x523_actual_game_command_corpus/build_report.json")


def _sha256_json(value: Any) -> str:
    blob = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


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


def _strip_provenance(decision: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in decision.items() if key != "provenance"}


def _load_source_entries(path: Path) -> List[Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{path} must contain a top-level list")
    normalized_entries: List[Dict[str, Any]] = []
    for index, entry in enumerate(payload):
        if not isinstance(entry, dict):
            raise ValueError(f"{path} entry {index} must be an object")
        normalized_entries.append(entry)
    return normalized_entries


def _build_source_instance(
    source_path: Path,
    source_index: int,
    decision: Dict[str, Any],
    realized_result: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    provenance = decision.get("provenance") if isinstance(decision.get("provenance"), dict) else {}
    instance: Dict[str, Any] = {
        "source_path": _display_path(source_path),
        "source_index": source_index,
        "decision_kind": decision.get("kind"),
    }
    if isinstance(decision.get("commandType"), str) and decision["commandType"]:
        instance["command_type"] = decision["commandType"]
    if isinstance(provenance.get("modelId"), str) and provenance["modelId"]:
        instance["model_id"] = provenance["modelId"]
    if isinstance(provenance.get("requestId"), str) and provenance["requestId"]:
        instance["request_id"] = provenance["requestId"]
    if isinstance(realized_result, dict):
        instance["realized_result"] = copy.deepcopy(realized_result)
    return instance


def _sort_examples(examples: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        examples,
        key=lambda example: (
            int(example["_summary"]["tick"]),
            int(example["_summary"]["stateVersion"]),
            example["target"]["kind"],
            str(example["target"].get("commandType", "")),
        ),
    )


def _command_result_matches_target(
    target: Dict[str, Any],
    result_entry: Dict[str, Any],
    player_id: str,
) -> bool:
    command = result_entry.get("command")
    if not isinstance(command, dict) or target.get("kind") != "command":
        return False
    if str(command.get("playerId", "")).strip() != player_id:
        return False
    command_type = str(command.get("type", "")).strip().lower()
    if command_type != target.get("commandType"):
        return False
    payload = command.get("payload")
    if payload is None:
        payload = {}
    return payload == target.get("payload", {})


def extract_realized_result(entry: Dict[str, Any], target: Dict[str, Any]) -> Dict[str, Any] | None:
    poll = entry.get("poll")
    if not isinstance(poll, dict):
        return None
    entry_input = entry.get("input")
    player_id = ""
    if isinstance(entry_input, dict):
        player_id = str(entry_input.get("playerId", "")).strip()
    command_results = poll.get("commandResults")
    if not isinstance(command_results, list):
        return None
    for result_entry in reversed(command_results):
        if (
            isinstance(result_entry, dict)
            and _command_result_matches_target(target, result_entry, player_id)
        ):
            result = result_entry.get("result")
            if isinstance(result, dict):
                return copy.deepcopy(result)
            return {}
    return None


def build_examples_from_paths(
    paths: Sequence[Path | str],
    *,
    require_poll_success: bool = False,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    source_paths = [_resolve_path(path) for path in paths]
    deduped: Dict[str, Dict[str, Any]] = {}
    raw_decision_kind_counts: Counter[str] = Counter()
    raw_command_type_counts: Counter[str] = Counter()
    raw_status_counts: Counter[str] = Counter()
    source_entry_counts: Counter[str] = Counter()
    source_model_ids: Counter[str] = Counter()
    source_total_entries = 0
    filtered_poll_failures = 0
    noop_reason_conflicts_collapsed = 0

    for path in source_paths:
        entries = _load_source_entries(path)
        path_known_tower_owners: Dict[int, str] = {}
        source_entry_counts[_display_path(path)] += len(entries)
        source_total_entries += len(entries)
        for source_index, entry in enumerate(entries):
            bridge_input = validate_bridge_input(entry.get("input"))
            path_known_tower_owners = _sync_known_tower_owners(bridge_input, path_known_tower_owners)
            summary = create_command_summary_from_bridge_input(bridge_input, path_known_tower_owners)
            decision = entry.get("decision")
            if not isinstance(decision, dict):
                raise ValueError(f"{path} entry {source_index} has invalid decision")
            normalized_target = normalize_command_decision(
                _strip_provenance(decision),
                summary["allowedCommands"],
            )
            realized_result = extract_realized_result(entry, normalized_target)
            realized_success = isinstance(realized_result, dict) and realized_result.get("success") is True
            if require_poll_success and normalized_target["kind"] == "command" and not realized_success:
                filtered_poll_failures += 1
                continue
            raw_decision_kind_counts[normalized_target["kind"]] += 1
            if normalized_target["kind"] == "command":
                raw_command_type_counts[str(normalized_target["commandType"])] += 1
            raw_status_counts[str(summary["status"])] += 1

            instance = _build_source_instance(path, source_index, decision, realized_result)
            if "model_id" in instance:
                source_model_ids[str(instance["model_id"])] += 1

            if normalized_target["kind"] == "command" and realized_success:
                player_id = str(bridge_input.get("playerId", "")).strip()
                command_type = normalized_target["commandType"]
                payload = normalized_target.get("payload", {})
                if command_type == "place_tower":
                    tower_id = realized_result.get("towerId")
                    if isinstance(tower_id, (int, float)) and float(tower_id).is_integer() and tower_id >= 1 and player_id:
                        path_known_tower_owners[int(tower_id)] = player_id
                elif command_type == "sell_tower":
                    tower_id = payload.get("towerId")
                    if isinstance(tower_id, int):
                        path_known_tower_owners.pop(tower_id, None)
                elif command_type == "upgrade_tower":
                    tower_id = payload.get("towerId")
                    if isinstance(tower_id, int) and player_id and tower_id not in path_known_tower_owners:
                        path_known_tower_owners[tower_id] = player_id

            summary_key = _sha256_json(summary)
            existing = deduped.get(summary_key)
            if existing is None:
                deduped[summary_key] = {
                    "bridge_input": bridge_input,
                    "target": normalized_target,
                    "metadata": {
                        "summary_sha256": _sha256_json(summary),
                        "target_sha256": _sha256_json(normalized_target),
                        "source_instances": [instance],
                    },
                    "_summary": summary,
                }
                continue
            if _sha256_json(existing["target"]) != _sha256_json(normalized_target):
                if existing["target"].get("kind") == "noop" and normalized_target.get("kind") == "noop":
                    existing["metadata"]["source_instances"].append(instance)
                    noop_reason_conflicts_collapsed += 1
                    continue
                raise ValueError(f"Conflicting targets for summary_sha256={existing['metadata']['summary_sha256']}")
            existing["metadata"]["source_instances"].append(instance)

    sorted_examples = _sort_examples(deduped.values())
    unique_decision_kind_counts: Counter[str] = Counter()
    unique_command_type_counts: Counter[str] = Counter()
    unique_status_counts: Counter[str] = Counter()
    examples: List[Dict[str, Any]] = []

    for example in sorted_examples:
        summary = example["_summary"]
        target = example["target"]
        metadata = dict(example["metadata"])
        metadata["source_instances"] = sorted(
            metadata["source_instances"],
            key=lambda instance: (instance["source_path"], int(instance["source_index"])),
        )
        unique_decision_kind_counts[str(target["kind"])] += 1
        unique_status_counts[str(summary["status"])] += 1
        if target["kind"] == "command":
            unique_command_type_counts[str(target["commandType"])] += 1
        examples.append(
            {
                "bridge_input": example["bridge_input"],
                "summary": summary,
                "target": target,
                "metadata": metadata,
            }
        )

    report = {
        "schema_version": "td.actual_game.command_corpus_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_paths": [_display_path(path) for path in source_paths],
        "source_entry_count": source_total_entries,
        "unique_example_count": len(examples),
        "duplicates_removed": source_total_entries - filtered_poll_failures - len(examples),
        "rowsFilteredPollFailure": filtered_poll_failures,
        "conflictCount": 0,
        "noopReasonConflictsCollapsed": noop_reason_conflicts_collapsed,
        "source_entry_counts": dict(sorted(source_entry_counts.items())),
        "decision_kind_counts": dict(sorted(raw_decision_kind_counts.items())),
        "command_type_counts": dict(sorted(raw_command_type_counts.items())),
        "status_counts": dict(sorted(raw_status_counts.items())),
        "unique_decision_kind_counts": dict(sorted(unique_decision_kind_counts.items())),
        "unique_command_type_counts": dict(sorted(unique_command_type_counts.items())),
        "unique_status_counts": dict(sorted(unique_status_counts.items())),
        "source_model_ids": dict(sorted(source_model_ids.items())),
        "source_rows_total": source_total_entries,
    }
    return examples, report


def build_examples(
    paths: Sequence[Path | str],
    *,
    require_poll_success: bool = False,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    return build_examples_from_paths(paths, require_poll_success=require_poll_success)


def write_examples(path: Path, examples: Sequence[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schemaVersion": EXAMPLE_SCHEMA_VERSION,
        "examples": list(examples),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_report(path: Path, report: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        "--input",
        action="append",
        default=[],
        help="Bridge-decisions JSON path. Repeat to merge multiple sources.",
    )
    parser.add_argument(
        "--out",
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help=f"Corpus output path. Default: {DEFAULT_OUTPUT_PATH}",
    )
    parser.add_argument(
        "--report-out",
        "--report",
        default=str(DEFAULT_REPORT_PATH),
        help=f"Build report output path. Default: {DEFAULT_REPORT_PATH}",
    )
    parser.add_argument(
        "--require-poll-success",
        action="store_true",
        help="Exclude command rows without a matched successful realized result in poll.commandResults.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    source_paths = args.source or [str(path) for path in DEFAULT_SOURCE_PATHS]
    examples, report = build_examples_from_paths(
        source_paths,
        require_poll_success=args.require_poll_success,
    )
    output_path = _resolve_path(args.out)
    report_path = _resolve_path(args.report_out)
    write_examples(output_path, examples)
    write_report(report_path, report)
    print(
        f"wrote_examples={output_path} wrote_report={report_path} "
        f"unique_examples={report['unique_example_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
