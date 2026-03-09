#!/usr/bin/env python3
"""Blend a base Env A corpus with a tightly filtered augmentation subset."""

from __future__ import annotations

import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_SCHEMA_VERSION = "td.actual_game.command_examples.v1"
DEFAULT_OUTPUT_PATH = Path("artifacts/x577_actual_game_command_corpus_grounded_opening/actual_game_command_examples.json")
DEFAULT_REPORT_PATH = Path("artifacts/x577_actual_game_command_corpus_grounded_opening/build_report.json")


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


def _command_type(example: Dict[str, Any]) -> str:
    target = _target(example)
    if target.get("kind") == "noop":
        return "noop"
    command_type = target.get("commandType")
    if not isinstance(command_type, str) or not command_type.strip():
        return "unknown"
    return command_type


def _sort_key(example: Dict[str, Any]) -> Tuple[int, int, str]:
    summary = example.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("example summary must be an object")
    tick = int(summary.get("tick", 0))
    state_version = int(summary.get("stateVersion", 0))
    return (tick, state_version, _example_id(example))


def _canonical_target(example: Dict[str, Any]) -> str:
    return json.dumps(_target(example), sort_keys=True, separators=(",", ":"))


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


def _payload_key(target: Dict[str, Any]) -> str:
    payload = target.get("payload")
    if not isinstance(payload, dict):
        payload = {}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _load_payload_whitelist(paths: Sequence[Path], command_type: str | None) -> Dict[str, set[str]]:
    allow = {}
    for path in paths:
        _schema_version, examples = _read_examples_payload(path)
        for example in examples:
            example_command_type = _command_type(example)
            if command_type and example_command_type != command_type:
                continue
            allow.setdefault(example_command_type, set()).add(_payload_key(_target(example)))
    return allow


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


def _augment_examples(
    augment_examples: Sequence[Dict[str, Any]],
    *,
    augment_command_type: str | None,
    augment_round: int | None,
    augment_player_tower_count: int | None,
    include_patterns: Sequence[str],
    exclude_patterns: Sequence[str],
    payload_allowlist: Dict[str, set[str]],
    per_source_limit: int | None,
    total_limit: int | None,
    replace_conflicting_summaries: bool,
    existing_examples: Dict[str, Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    candidates = sorted(augment_examples, key=_sort_key)
    kept: List[Dict[str, Any]] = []
    skip_reasons: Counter[str] = Counter()
    kept_by_source: Counter[str] = Counter()
    replaced_conflicts = 0

    for example in candidates:
        command_type = _command_type(example)
        if augment_command_type and command_type != augment_command_type:
            skip_reasons["command_type_mismatch"] += 1
            continue

        summary = example.get("summary")
        if not isinstance(summary, dict):
            skip_reasons["missing_summary"] += 1
            continue
        if augment_round is not None and int(summary.get("round", -1)) != augment_round:
            skip_reasons["round_mismatch"] += 1
            continue
        if augment_player_tower_count is not None and int(summary.get("playerTowerCount", -1)) != augment_player_tower_count:
            skip_reasons["player_tower_count_mismatch"] += 1
            continue

        candidate_sources = _match_source_path(
            _source_paths(example),
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
        )
        if not candidate_sources:
            skip_reasons["source_filter_mismatch"] += 1
            continue
        attributed_source = min(candidate_sources, key=lambda source_path: (kept_by_source[source_path], source_path))

        target = _target(example)
        allowlist = payload_allowlist.get(command_type)
        if allowlist is not None and _payload_key(target) not in allowlist:
            skip_reasons["payload_not_grounded"] += 1
            continue

        example_id = _example_id(example)
        if example_id in existing_examples:
            if _canonical_target(existing_examples[example_id]) != _canonical_target(example):
                if not replace_conflicting_summaries:
                    raise ValueError(f"conflicting targets for summary_sha256 {example_id}")
                replaced_conflicts += 1
            else:
                skip_reasons["duplicate_summary"] += 1
                continue

        if per_source_limit is not None and kept_by_source[attributed_source] >= per_source_limit:
            skip_reasons["per_source_cap"] += 1
            continue
        if total_limit is not None and len(kept) >= total_limit:
            skip_reasons["total_cap"] += 1
            continue

        next_example = copy.deepcopy(example)
        next_example.setdefault("metadata", {})
        if isinstance(next_example["metadata"], dict):
            next_example["metadata"]["blend_attributed_source"] = attributed_source
        kept.append(next_example)
        existing_examples[example_id] = next_example
        kept_by_source[attributed_source] += 1

    return kept, {
        "kept_count": len(kept),
        "kept_by_source": dict(sorted(kept_by_source.items())),
        "replaced_conflicting_summaries": replaced_conflicts,
        "skip_reasons": dict(sorted(skip_reasons.items())),
    }


def blend_examples(
    *,
    base_paths: Sequence[Path | str],
    augment_paths: Sequence[Path | str],
    augment_command_type: str | None = None,
    augment_round: int | None = None,
    augment_player_tower_count: int | None = None,
    augment_source_contains: Sequence[str] = (),
    augment_exclude_source_contains: Sequence[str] = (),
    payload_whitelist_paths: Sequence[Path | str] = (),
    augment_limit_per_source: int | None = None,
    augment_limit_total: int | None = None,
    replace_conflicting_summaries: bool = False,
) -> Tuple[str, List[Dict[str, Any]], Dict[str, Any]]:
    schema_version = EXAMPLES_SCHEMA_VERSION
    base_examples: List[Dict[str, Any]] = []
    augment_examples: List[Dict[str, Any]] = []
    base_path_labels: List[str] = []
    augment_path_labels: List[str] = []

    for raw_path in base_paths:
        path = _resolve_path(raw_path)
        current_schema, current_examples = _read_examples_payload(path)
        schema_version = current_schema or schema_version
        base_examples.extend(copy.deepcopy(current_examples))
        base_path_labels.append(_display_path(path))

    for raw_path in augment_paths:
        path = _resolve_path(raw_path)
        current_schema, current_examples = _read_examples_payload(path)
        schema_version = current_schema or schema_version
        augment_examples.extend(copy.deepcopy(current_examples))
        augment_path_labels.append(_display_path(path))

    existing_examples: Dict[str, Dict[str, Any]] = {}
    base_duplicates = 0
    for example in sorted(base_examples, key=_sort_key):
        example_id = _example_id(example)
        if example_id in existing_examples:
            if _canonical_target(existing_examples[example_id]) != _canonical_target(example):
                raise ValueError(f"conflicting base targets for summary_sha256 {example_id}")
            base_duplicates += 1
            continue
        existing_examples[example_id] = example

    payload_whitelist = _load_payload_whitelist(
        [_resolve_path(path) for path in payload_whitelist_paths],
        augment_command_type,
    )
    kept_augment_examples, augment_report = _augment_examples(
        augment_examples,
        augment_command_type=augment_command_type,
        augment_round=augment_round,
        augment_player_tower_count=augment_player_tower_count,
        include_patterns=tuple(augment_source_contains),
        exclude_patterns=tuple(augment_exclude_source_contains),
        payload_allowlist=payload_whitelist,
        per_source_limit=augment_limit_per_source,
        total_limit=augment_limit_total,
        replace_conflicting_summaries=replace_conflicting_summaries,
        existing_examples=existing_examples,
    )

    final_examples = sorted(existing_examples.values(), key=_sort_key)
    command_counts: Counter[str] = Counter(_command_type(example) for example in final_examples)
    report = {
        "schema_version": "td.actual_game.command_corpus_blend_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_paths": base_path_labels,
        "augment_paths": augment_path_labels,
        "base_unique_count": len(existing_examples) - len(kept_augment_examples),
        "base_duplicates_collapsed": base_duplicates,
        "augment_raw_count": len(augment_examples),
        "augment_kept_count": len(kept_augment_examples),
        "augment_filter": {
            "command_type": augment_command_type,
            "round": augment_round,
            "player_tower_count": augment_player_tower_count,
            "source_contains": list(augment_source_contains),
            "exclude_source_contains": list(augment_exclude_source_contains),
            "payload_whitelist_paths": [_display_path(_resolve_path(path)) for path in payload_whitelist_paths],
            "limit_per_source": augment_limit_per_source,
            "limit_total": augment_limit_total,
            "replace_conflicting_summaries": replace_conflicting_summaries,
        },
        "augment_kept_by_source": augment_report["kept_by_source"],
        "augment_replaced_conflicting_summaries": augment_report["replaced_conflicting_summaries"],
        "augment_skip_reasons": augment_report["skip_reasons"],
        "final_example_count": len(final_examples),
        "final_command_type_counts": dict(sorted(command_counts.items())),
    }
    return schema_version, final_examples, report


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", action="append", default=[], help="Base examples JSON/JSONL path. Repeatable.")
    parser.add_argument("--augment", action="append", default=[], help="Augment examples JSON/JSONL path. Repeatable.")
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT_PATH), help=f"Blended examples output path. Default: {DEFAULT_OUTPUT_PATH}")
    parser.add_argument("--report", default=str(DEFAULT_REPORT_PATH), help=f"Blend report output path. Default: {DEFAULT_REPORT_PATH}")
    parser.add_argument("--augment-command-type", default="", help="Optional command type filter for augment examples.")
    parser.add_argument("--augment-round", type=int, default=-1, help="Optional exact round filter for augment examples.")
    parser.add_argument(
        "--augment-player-tower-count",
        type=int,
        default=-1,
        help="Optional exact summary.playerTowerCount filter for augment examples.",
    )
    parser.add_argument(
        "--augment-source-contains",
        action="append",
        default=[],
        help="Substring that must match at least one augment source_path. Repeatable.",
    )
    parser.add_argument(
        "--augment-exclude-source-contains",
        action="append",
        default=[],
        help="Substring that excludes augment source_path matches. Repeatable.",
    )
    parser.add_argument(
        "--augment-payload-whitelist-from",
        action="append",
        default=[],
        help="Examples file whose command payloads define the allowed augment payload set. Repeatable.",
    )
    parser.add_argument("--augment-limit-per-source", type=int, default=-1, help="Optional cap per attributed augment source.")
    parser.add_argument("--augment-limit-total", type=int, default=-1, help="Optional total cap across all kept augment examples.")
    parser.add_argument(
        "--replace-conflicting-summaries",
        action="store_true",
        help="Replace base examples when an augment example has the same summary_sha256 but a different target.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.base:
        raise SystemExit("At least one --base path is required")
    if not args.augment:
        raise SystemExit("At least one --augment path is required")

    schema_version, examples, report = blend_examples(
        base_paths=args.base,
        augment_paths=args.augment,
        augment_command_type=args.augment_command_type.strip() or None,
        augment_round=args.augment_round if args.augment_round >= 0 else None,
        augment_player_tower_count=args.augment_player_tower_count if args.augment_player_tower_count >= 0 else None,
        augment_source_contains=args.augment_source_contains,
        augment_exclude_source_contains=args.augment_exclude_source_contains,
        payload_whitelist_paths=args.augment_payload_whitelist_from,
        augment_limit_per_source=args.augment_limit_per_source if args.augment_limit_per_source >= 0 else None,
        augment_limit_total=args.augment_limit_total if args.augment_limit_total >= 0 else None,
        replace_conflicting_summaries=args.replace_conflicting_summaries,
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
