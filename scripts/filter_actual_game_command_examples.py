#!/usr/bin/env python3
"""Filter Env A command examples into a smaller reusable corpus slice."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_SCHEMA_VERSION = "td.actual_game.command_examples.v1"
DEFAULT_OUTPUT_PATH = Path("artifacts/x584_actual_game_command_examples_filtered/actual_game_command_examples.json")
DEFAULT_REPORT_PATH = Path("artifacts/x584_actual_game_command_examples_filtered/filter_report.json")


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


def _read_examples_payload(path: Path) -> Tuple[str, List[Dict[str, Any]]]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
        return EXAMPLES_SCHEMA_VERSION, rows
    payload = json.loads(raw)
    if isinstance(payload, list):
        return EXAMPLES_SCHEMA_VERSION, payload
    if isinstance(payload, dict) and isinstance(payload.get("examples"), list):
        schema_version = payload.get("schemaVersion")
        if not isinstance(schema_version, str) or not schema_version.strip():
            schema_version = EXAMPLES_SCHEMA_VERSION
        return schema_version, payload["examples"]
    raise ValueError(f"Unsupported examples payload in {path}")


def _write_examples(path: Path, schema_version: str, examples: Sequence[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schemaVersion": schema_version,
        "examples": list(examples),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_report(path: Path, report: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _example_id(example: Dict[str, Any]) -> str:
    metadata = example.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError("example metadata must be an object")
    summary_sha256 = metadata.get("summary_sha256")
    if not isinstance(summary_sha256, str) or not summary_sha256.strip():
        raise ValueError("example metadata.summary_sha256 is required")
    return summary_sha256


def _target(example: Dict[str, Any]) -> Dict[str, Any]:
    target = example.get("target")
    if not isinstance(target, dict):
        raise ValueError("example target must be an object")
    return target


def _canonical_target(example: Dict[str, Any]) -> str:
    return json.dumps(_target(example), sort_keys=True, separators=(",", ":"))


def _summary(example: Dict[str, Any]) -> Dict[str, Any]:
    summary = example.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("example summary must be an object")
    return summary


def _sort_key(example: Dict[str, Any]) -> Tuple[int, int, str]:
    summary = _summary(example)
    return (
        int(summary.get("tick", 0)),
        int(summary.get("stateVersion", 0)),
        _example_id(example),
    )


def _source_instances(example: Dict[str, Any]) -> List[Dict[str, Any]]:
    metadata = example.get("metadata")
    if not isinstance(metadata, dict):
        return []
    raw_records = metadata.get("source_instances", metadata.get("sourceRecords", []))
    if not isinstance(raw_records, list):
        return []
    return [record for record in raw_records if isinstance(record, dict)]


def _source_paths(example: Dict[str, Any]) -> List[str]:
    paths = []
    for record in _source_instances(example):
        source_path = record.get("source_path", record.get("path"))
        if isinstance(source_path, str) and source_path.strip():
            paths.append(source_path)
    return sorted(set(paths))


def _command_type(example: Dict[str, Any]) -> str:
    target = _target(example)
    if target.get("kind") == "noop":
        return "noop"
    command_type = target.get("commandType")
    if not isinstance(command_type, str) or not command_type.strip():
        return "unknown"
    return command_type


def _target_payload(example: Dict[str, Any]) -> Dict[str, Any]:
    target = _target(example)
    payload = target.get("payload")
    if not isinstance(payload, dict):
        return {}
    return payload


def _coerce_coord_pair(payload: Dict[str, Any]) -> Tuple[float, float] | None:
    x = payload.get("x")
    y = payload.get("y")
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        return None
    if isinstance(x, bool) or isinstance(y, bool):
        return None
    return float(x), float(y)


def _safe_anchor_pairs(example: Dict[str, Any]) -> set[Tuple[float, float]]:
    summary = _summary(example)
    anchors = summary.get("safePlacementAnchors")
    if not isinstance(anchors, list):
        return set()
    pairs: set[Tuple[float, float]] = set()
    for anchor in anchors:
        if not isinstance(anchor, dict):
            continue
        pair = _coerce_coord_pair(anchor)
        if pair is not None:
            pairs.add(pair)
    return pairs


def _occupied_tower_pairs(example: Dict[str, Any]) -> set[Tuple[float, float]]:
    summary = _summary(example)
    towers = summary.get("towers")
    if not isinstance(towers, list):
        return set()
    pairs: set[Tuple[float, float]] = set()
    for tower in towers:
        if not isinstance(tower, dict):
            continue
        pair = _coerce_coord_pair(tower)
        if pair is not None:
            pairs.add(pair)
    return pairs


def _place_target_pair(example: Dict[str, Any]) -> Tuple[float, float] | None:
    if _command_type(example) != "place_tower":
        return None
    return _coerce_coord_pair(_target_payload(example))


def _matches_path_filters(
    source_paths: Sequence[str],
    *,
    include_patterns: Sequence[str],
    exclude_patterns: Sequence[str],
) -> bool:
    matched = False if include_patterns else True
    for source_path in source_paths:
        if exclude_patterns and any(pattern in source_path for pattern in exclude_patterns):
            continue
        if include_patterns:
            if any(pattern in source_path for pattern in include_patterns):
                matched = True
        else:
            matched = True
    return matched


def filter_examples(
    *,
    input_paths: Sequence[Path | str],
    allowed_command_types: Sequence[str] = (),
    min_player_tower_count: int | None = None,
    max_player_tower_count: int | None = None,
    exact_player_tower_count: int | None = None,
    min_round: int | None = None,
    max_round: int | None = None,
    exact_round: int | None = None,
    source_contains: Sequence[str] = (),
    exclude_source_contains: Sequence[str] = (),
    require_place_target_in_safe_anchors: bool = False,
    reject_occupied_place_target: bool = False,
    limit: int | None = None,
) -> Tuple[str, List[Dict[str, Any]], Dict[str, Any]]:
    schema_version = EXAMPLES_SCHEMA_VERSION
    loaded_examples: List[Dict[str, Any]] = []
    input_labels: List[str] = []

    for raw_path in input_paths:
        path = _resolve_path(raw_path)
        current_schema, current_examples = _read_examples_payload(path)
        schema_version = current_schema or schema_version
        loaded_examples.extend(current_examples)
        input_labels.append(_display_path(path))

    filtered: Dict[str, Dict[str, Any]] = {}
    duplicates_collapsed = 0
    skip_reasons: Counter[str] = Counter()

    allowed_types = {item.strip() for item in allowed_command_types if item.strip()}

    for example in sorted(loaded_examples, key=_sort_key):
        command_type = _command_type(example)
        if allowed_types and command_type not in allowed_types:
            skip_reasons["command_type_mismatch"] += 1
            continue

        summary = _summary(example)
        round_num = int(summary.get("round", -1))
        player_tower_count = int(summary.get("playerTowerCount", -1))
        if exact_round is not None and round_num != exact_round:
            skip_reasons["round_mismatch"] += 1
            continue
        if min_round is not None and round_num < min_round:
            skip_reasons["round_mismatch"] += 1
            continue
        if max_round is not None and round_num > max_round:
            skip_reasons["round_mismatch"] += 1
            continue
        if exact_player_tower_count is not None and player_tower_count != exact_player_tower_count:
            skip_reasons["player_tower_count_mismatch"] += 1
            continue
        if min_player_tower_count is not None and player_tower_count < min_player_tower_count:
            skip_reasons["player_tower_count_mismatch"] += 1
            continue
        if max_player_tower_count is not None and player_tower_count > max_player_tower_count:
            skip_reasons["player_tower_count_mismatch"] += 1
            continue

        source_paths = _source_paths(example)
        if not _matches_path_filters(
            source_paths,
            include_patterns=tuple(source_contains),
            exclude_patterns=tuple(exclude_source_contains),
        ):
            skip_reasons["source_filter_mismatch"] += 1
            continue

        place_target_pair = _place_target_pair(example)
        if command_type == "place_tower" and (require_place_target_in_safe_anchors or reject_occupied_place_target):
            if place_target_pair is None:
                skip_reasons["place_target_invalid"] += 1
                continue
        if require_place_target_in_safe_anchors and place_target_pair is not None:
            safe_anchor_pairs = _safe_anchor_pairs(example)
            if place_target_pair not in safe_anchor_pairs:
                skip_reasons["place_target_not_in_safe_anchors"] += 1
                continue
        if reject_occupied_place_target and place_target_pair is not None:
            occupied_pairs = _occupied_tower_pairs(example)
            if place_target_pair in occupied_pairs:
                skip_reasons["place_target_occupied"] += 1
                continue

        example_id = _example_id(example)
        existing = filtered.get(example_id)
        if existing is not None:
            if _canonical_target(existing) != _canonical_target(example):
                raise ValueError(f"conflicting targets for summary_sha256 {example_id}")
            duplicates_collapsed += 1
            continue

        if limit is not None and len(filtered) >= limit:
            skip_reasons["limit_reached"] += 1
            continue

        filtered[example_id] = example

    examples = sorted(filtered.values(), key=_sort_key)
    command_counts: Counter[str] = Counter(_command_type(example) for example in examples)
    report = {
        "schema_version": "td.actual_game.command_examples_filter_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_paths": input_labels,
        "input_example_count": len(loaded_examples),
        "output_example_count": len(examples),
        "duplicates_collapsed": duplicates_collapsed,
        "filter": {
            "allowed_command_types": sorted(allowed_types),
            "min_player_tower_count": min_player_tower_count,
            "max_player_tower_count": max_player_tower_count,
            "exact_player_tower_count": exact_player_tower_count,
            "min_round": min_round,
            "max_round": max_round,
            "exact_round": exact_round,
            "source_contains": list(source_contains),
            "exclude_source_contains": list(exclude_source_contains),
            "require_place_target_in_safe_anchors": require_place_target_in_safe_anchors,
            "reject_occupied_place_target": reject_occupied_place_target,
            "limit": limit,
        },
        "skip_reasons": dict(sorted(skip_reasons.items())),
        "command_type_counts": dict(sorted(command_counts.items())),
    }
    return schema_version, examples, report


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[], help="Examples JSON/JSONL path. Repeatable.")
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT_PATH), help=f"Filtered examples output path. Default: {DEFAULT_OUTPUT_PATH}")
    parser.add_argument("--report", default=str(DEFAULT_REPORT_PATH), help=f"Filter report output path. Default: {DEFAULT_REPORT_PATH}")
    parser.add_argument("--command-type", action="append", default=[], help="Allowed command type. Repeatable.")
    parser.add_argument("--min-player-tower-count", type=int, default=-1, help="Optional inclusive minimum summary.playerTowerCount filter.")
    parser.add_argument("--max-player-tower-count", type=int, default=-1, help="Optional inclusive maximum summary.playerTowerCount filter.")
    parser.add_argument("--exact-player-tower-count", type=int, default=-1, help="Optional exact summary.playerTowerCount filter.")
    parser.add_argument("--min-round", type=int, default=-1, help="Optional inclusive minimum round filter.")
    parser.add_argument("--max-round", type=int, default=-1, help="Optional inclusive maximum round filter.")
    parser.add_argument("--exact-round", type=int, default=-1, help="Optional exact round filter.")
    parser.add_argument("--source-contains", action="append", default=[], help="Substring that must match at least one source_path. Repeatable.")
    parser.add_argument("--exclude-source-contains", action="append", default=[], help="Substring that excludes source_path matches. Repeatable.")
    parser.add_argument(
        "--require-place-target-in-safe-anchors",
        action="store_true",
        help="Keep place_tower examples only when target x/y matches summary.safePlacementAnchors.",
    )
    parser.add_argument(
        "--reject-occupied-place-target",
        action="store_true",
        help="Drop place_tower examples whose target x/y matches an existing summary.towers position.",
    )
    parser.add_argument("--limit", type=int, default=-1, help="Optional max output examples.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.input:
        raise SystemExit("At least one --input path is required")
    schema_version, examples, report = filter_examples(
        input_paths=args.input,
        allowed_command_types=args.command_type,
        min_player_tower_count=args.min_player_tower_count if args.min_player_tower_count >= 0 else None,
        max_player_tower_count=args.max_player_tower_count if args.max_player_tower_count >= 0 else None,
        exact_player_tower_count=args.exact_player_tower_count if args.exact_player_tower_count >= 0 else None,
        min_round=args.min_round if args.min_round >= 0 else None,
        max_round=args.max_round if args.max_round >= 0 else None,
        exact_round=args.exact_round if args.exact_round >= 0 else None,
        source_contains=args.source_contains,
        exclude_source_contains=args.exclude_source_contains,
        require_place_target_in_safe_anchors=args.require_place_target_in_safe_anchors,
        reject_occupied_place_target=args.reject_occupied_place_target,
        limit=args.limit if args.limit >= 0 else None,
    )
    output_path = _resolve_path(args.out)
    report_path = _resolve_path(args.report)
    _write_examples(output_path, schema_version, examples)
    report = dict(report)
    report["output_path"] = str(output_path)
    report["report_path"] = str(report_path)
    _write_report(report_path, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
