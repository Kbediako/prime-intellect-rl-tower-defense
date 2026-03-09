#!/usr/bin/env python3
"""Select a filtered subset of Env A actual-game command examples."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_SCHEMA_VERSION = "td.actual_game.command_examples.v1"
DEFAULT_EXAMPLES_PATH = Path("artifacts/x523_actual_game_command_corpus/actual_game_command_examples.json")
DEFAULT_OUTPUT_PATH = Path("artifacts/x583_actual_game_command_examples_selection/examples.json")
DEFAULT_REPORT_PATH = Path("artifacts/x583_actual_game_command_examples_selection/report.json")


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
    payload = {"schemaVersion": schema_version, "examples": list(examples)}
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


def _sort_key(example: Dict[str, Any]) -> Tuple[int, int, str]:
    summary = example.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("example summary must be an object")
    return (
        int(summary.get("tick", 0)),
        int(summary.get("stateVersion", 0)),
        _example_id(example),
    )


def _target(example: Dict[str, Any]) -> Dict[str, Any]:
    target = example.get("target")
    if not isinstance(target, dict):
        raise ValueError("example target must be an object")
    return target


def _command_type(example: Dict[str, Any]) -> str:
    target = _target(example)
    if target.get("kind") == "noop":
        return "noop"
    command_type = target.get("commandType")
    if not isinstance(command_type, str) or not command_type.strip():
        return "unknown"
    return command_type


def _source_instances(example: Dict[str, Any]) -> List[Dict[str, Any]]:
    metadata = example.get("metadata")
    if not isinstance(metadata, dict):
        return []
    raw_records = metadata.get("source_instances", metadata.get("sourceRecords", []))
    if not isinstance(raw_records, list):
        return []
    return [record for record in raw_records if isinstance(record, dict)]


def _source_paths(example: Dict[str, Any]) -> List[str]:
    paths = set()
    for record in _source_instances(example):
        source_path = record.get("source_path", record.get("path"))
        if isinstance(source_path, str) and source_path.strip():
            paths.add(source_path)
    return sorted(paths)


def _select_evenly_spaced(entries: Sequence[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
    if limit <= 0:
        return []
    if limit >= len(entries):
        return list(entries)
    return [entries[math.floor(index * len(entries) / limit)] for index in range(limit)]


def _apply_limit(
    entries: Sequence[Dict[str, Any]],
    *,
    limit: int | None,
    mode: str,
) -> List[Dict[str, Any]]:
    if limit is None:
        return list(entries)
    if mode == "first":
        return list(entries[:limit])
    if mode == "evenly_spaced":
        return _select_evenly_spaced(entries, limit)
    raise ValueError(f"Unsupported sampling mode {mode}")


def _match_source_path(
    source_paths: Sequence[str],
    *,
    include_patterns: Sequence[str],
    exclude_patterns: Sequence[str],
) -> List[str]:
    filtered = []
    for source_path in source_paths:
        if exclude_patterns and any(pattern in source_path for pattern in exclude_patterns):
            continue
        if include_patterns and not any(pattern in source_path for pattern in include_patterns):
            continue
        filtered.append(source_path)
    return sorted(filtered)


def select_examples(
    examples: Sequence[Dict[str, Any]],
    *,
    include_summary_sha256: Sequence[str] = (),
    include_command_types: Sequence[str] = (),
    exclude_command_types: Sequence[str] = (),
    include_statuses: Sequence[str] = (),
    include_rounds: Sequence[int] = (),
    min_player_tower_count: int | None = None,
    max_player_tower_count: int | None = None,
    include_source_contains: Sequence[str] = (),
    exclude_source_contains: Sequence[str] = (),
    reject_source_contains: Sequence[str] = (),
    limit_per_source: int | None = None,
    limit_total: int | None = None,
    sampling_mode: str = "first",
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    include_summary_sha256_set = {value for value in include_summary_sha256 if value}
    include_command_types_set = {value for value in include_command_types if value}
    exclude_command_types_set = {value for value in exclude_command_types if value}
    include_statuses_set = {value for value in include_statuses if value}
    include_rounds_set = {int(value) for value in include_rounds}

    skip_reasons: Counter[str] = Counter()
    filtered: List[Tuple[str, Dict[str, Any]]] = []

    for example in sorted(examples, key=_sort_key):
        example_id = _example_id(example)
        if include_summary_sha256_set and example_id not in include_summary_sha256_set:
            skip_reasons["summary_sha256_excluded"] += 1
            continue

        command_type = _command_type(example)
        if include_command_types_set and command_type not in include_command_types_set:
            skip_reasons["command_type_excluded"] += 1
            continue
        if exclude_command_types_set and command_type in exclude_command_types_set:
            skip_reasons["command_type_excluded"] += 1
            continue

        summary = example.get("summary")
        if not isinstance(summary, dict):
            skip_reasons["missing_summary"] += 1
            continue
        status = summary.get("status")
        if include_statuses_set and status not in include_statuses_set:
            skip_reasons["status_excluded"] += 1
            continue
        round_num = int(summary.get("round", -1))
        if include_rounds_set and round_num not in include_rounds_set:
            skip_reasons["round_excluded"] += 1
            continue

        player_tower_count = int(summary.get("playerTowerCount", -1))
        if min_player_tower_count is not None and player_tower_count < min_player_tower_count:
            skip_reasons["player_tower_count_too_small"] += 1
            continue
        if max_player_tower_count is not None and player_tower_count > max_player_tower_count:
            skip_reasons["player_tower_count_too_large"] += 1
            continue

        raw_source_paths = _source_paths(example)
        if reject_source_contains and any(
            pattern in source_path
            for pattern in reject_source_contains
            for source_path in raw_source_paths
        ):
            skip_reasons["source_rejected"] += 1
            continue

        source_paths = _match_source_path(
            raw_source_paths,
            include_patterns=include_source_contains,
            exclude_patterns=exclude_source_contains,
        )
        if include_source_contains or exclude_source_contains:
            if not source_paths:
                skip_reasons["source_filter_mismatch"] += 1
                continue
        else:
            source_paths = _source_paths(example)

        attributed_source = source_paths[0] if source_paths else "unknown"
        filtered.append((attributed_source, example))

    filtered_by_source: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for attributed_source, example in filtered:
        filtered_by_source[attributed_source].append(example)

    kept_by_source: Dict[str, List[Dict[str, Any]]] = {}
    for attributed_source, source_examples in sorted(filtered_by_source.items()):
        kept_by_source[attributed_source] = _apply_limit(
            source_examples,
            limit=limit_per_source,
            mode=sampling_mode,
        )

    selected_examples: List[Dict[str, Any]] = []
    source_counts: Counter[str] = Counter()
    for attributed_source in sorted(kept_by_source):
        for example in kept_by_source[attributed_source]:
            selected_examples.append(example)
            source_counts[attributed_source] += 1

    selected_examples = sorted(selected_examples, key=_sort_key)
    if limit_total is not None:
        selected_examples = _apply_limit(selected_examples, limit=limit_total, mode=sampling_mode)
        recomputed_counts: Counter[str] = Counter()
        for example in selected_examples:
            source_paths = _match_source_path(
                _source_paths(example),
                include_patterns=include_source_contains,
                exclude_patterns=exclude_source_contains,
            )
            attributed_source = source_paths[0] if source_paths else (_source_paths(example)[0] if _source_paths(example) else "unknown")
            recomputed_counts[attributed_source] += 1
        source_counts = recomputed_counts

    command_type_counts: Counter[str] = Counter(_command_type(example) for example in selected_examples)
    report = {
        "schema_version": "td.actual_game.command_examples_selection_report.v1",
        "input_example_count": len(examples),
        "filtered_count": len(filtered),
        "selected_count": len(selected_examples),
        "selected_command_type_counts": dict(sorted(command_type_counts.items())),
        "selected_by_source": dict(sorted(source_counts.items())),
        "skip_reasons": dict(sorted(skip_reasons.items())),
        "filters": {
            "include_summary_sha256": sorted(include_summary_sha256_set),
            "include_command_types": sorted(include_command_types_set),
            "exclude_command_types": sorted(exclude_command_types_set),
            "include_statuses": sorted(include_statuses_set),
            "include_rounds": sorted(include_rounds_set),
            "min_player_tower_count": min_player_tower_count,
            "max_player_tower_count": max_player_tower_count,
            "include_source_contains": list(include_source_contains),
            "exclude_source_contains": list(exclude_source_contains),
            "reject_source_contains": list(reject_source_contains),
            "limit_per_source": limit_per_source,
            "limit_total": limit_total,
            "sampling_mode": sampling_mode,
        },
    }
    return selected_examples, report


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--examples", default=str(DEFAULT_EXAMPLES_PATH), help=f"Input examples JSON/JSONL. Default: {DEFAULT_EXAMPLES_PATH}")
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT_PATH), help=f"Selected examples output path. Default: {DEFAULT_OUTPUT_PATH}")
    parser.add_argument("--report", default=str(DEFAULT_REPORT_PATH), help=f"Selection report path. Default: {DEFAULT_REPORT_PATH}")
    parser.add_argument("--include-summary-sha256", action="append", default=[], help="Exact metadata.summary_sha256 to keep. Repeatable.")
    parser.add_argument("--include-command-type", action="append", default=[], help="Command type to keep. Repeatable.")
    parser.add_argument("--exclude-command-type", action="append", default=[], help="Command type to drop. Repeatable.")
    parser.add_argument("--include-status", action="append", default=[], help="Summary status to keep. Repeatable.")
    parser.add_argument("--include-round", action="append", type=int, default=[], help="Exact summary.round to keep. Repeatable.")
    parser.add_argument("--min-player-tower-count", type=int, default=-1, help="Minimum summary.playerTowerCount to keep.")
    parser.add_argument("--max-player-tower-count", type=int, default=-1, help="Maximum summary.playerTowerCount to keep.")
    parser.add_argument("--include-source-contains", action="append", default=[], help="Substring that must match at least one source_path. Repeatable.")
    parser.add_argument("--exclude-source-contains", action="append", default=[], help="Substring that excludes matching source_path rows. Repeatable.")
    parser.add_argument(
        "--reject-source-contains",
        action="append",
        default=[],
        help="Substring that rejects the whole row if it appears in any source_path. Repeatable.",
    )
    parser.add_argument("--limit-per-source", type=int, default=-1, help="Optional cap per attributed source.")
    parser.add_argument("--limit-total", type=int, default=-1, help="Optional total cap after filtering.")
    parser.add_argument(
        "--sampling-mode",
        choices=("first", "evenly_spaced"),
        default="first",
        help="Selection mode when caps apply. Default: first",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    examples_path = _resolve_path(args.examples)
    output_path = _resolve_path(args.out)
    report_path = _resolve_path(args.report)

    schema_version, examples = _read_examples_payload(examples_path)
    selected_examples, report = select_examples(
        examples,
        include_summary_sha256=args.include_summary_sha256,
        include_command_types=args.include_command_type,
        exclude_command_types=args.exclude_command_type,
        include_statuses=args.include_status,
        include_rounds=args.include_round,
        min_player_tower_count=args.min_player_tower_count if args.min_player_tower_count >= 0 else None,
        max_player_tower_count=args.max_player_tower_count if args.max_player_tower_count >= 0 else None,
        include_source_contains=args.include_source_contains,
        exclude_source_contains=args.exclude_source_contains,
        reject_source_contains=args.reject_source_contains,
        limit_per_source=args.limit_per_source if args.limit_per_source >= 0 else None,
        limit_total=args.limit_total if args.limit_total >= 0 else None,
        sampling_mode=args.sampling_mode,
    )
    _write_examples(output_path, schema_version, selected_examples)
    report = dict(report)
    report["examples_path"] = _display_path(examples_path)
    report["output_path"] = _display_path(output_path)
    report["report_path"] = _display_path(report_path)
    _write_report(report_path, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
