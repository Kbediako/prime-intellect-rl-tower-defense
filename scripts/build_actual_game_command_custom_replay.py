#!/usr/bin/env python3
"""Build a train corpus by replaying selected Env A examples onto a base set."""

from __future__ import annotations

import argparse
from collections import Counter
import copy
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_SCHEMA_VERSION = "td.actual_game.command_examples.v1"


def _resolve_path(raw_path: Path | str) -> Path:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def _read_examples_payload(path: Path) -> Tuple[str, List[Dict[str, Any]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return EXAMPLES_SCHEMA_VERSION, payload
    if isinstance(payload, dict) and isinstance(payload.get("examples"), list):
        schema_version = payload.get("schemaVersion")
        if not isinstance(schema_version, str) or not schema_version.strip():
            schema_version = EXAMPLES_SCHEMA_VERSION
        return schema_version, payload["examples"]
    raise ValueError(f"Unsupported examples payload in {path}")


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


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


def _command_type(example: Dict[str, Any]) -> str:
    target = _target(example)
    if target.get("kind") == "noop":
        return "noop"
    command_type = target.get("commandType")
    if not isinstance(command_type, str) or not command_type.strip():
        return "unknown"
    return command_type


def _selected_row_summary(example: Dict[str, Any]) -> Dict[str, Any]:
    metadata = example.get("metadata", {})
    source_instances = metadata.get("source_instances", metadata.get("sourceRecords", []))
    primary_source = source_instances[0] if isinstance(source_instances, list) and source_instances else {}
    return {
        "summary_sha256": metadata.get("summary_sha256"),
        "request_id": primary_source.get("request_id"),
        "source_index": primary_source.get("source_index"),
        "source_path": primary_source.get("source_path", primary_source.get("path")),
        "target": _target(example),
    }


def build_custom_replay(
    *,
    base_examples_path: Path | str,
    augment_examples_paths: Sequence[Path | str],
    extra_repeats_per_selected_example: int = 1,
) -> Tuple[str, List[Dict[str, Any]], Dict[str, Any]]:
    if extra_repeats_per_selected_example < 1:
        raise ValueError("extra_repeats_per_selected_example must be >= 1")

    base_path = _resolve_path(base_examples_path)
    schema_version, base_examples = _read_examples_payload(base_path)

    selected_examples: Dict[str, Dict[str, Any]] = {}
    selected_sources: Counter[str] = Counter()
    for raw_augment_path in augment_examples_paths:
        augment_path = _resolve_path(raw_augment_path)
        augment_schema_version, augment_examples = _read_examples_payload(augment_path)
        if augment_schema_version != schema_version:
            raise ValueError(
                f"schema version mismatch: base={schema_version!r} augment={augment_schema_version!r} path={augment_path}"
            )
        for example in augment_examples:
            example_id = _example_id(example)
            existing = selected_examples.get(example_id)
            if existing is not None and _canonical_target(existing) != _canonical_target(example):
                raise ValueError(f"conflicting targets for summary_sha256 {example_id}")
            selected_examples.setdefault(example_id, copy.deepcopy(example))
            selected_sources[_display_path(augment_path)] += 1

    final_examples = [copy.deepcopy(example) for example in base_examples]
    ordered_selected = sorted(selected_examples.values(), key=_example_id)
    for example in ordered_selected:
        for _ in range(extra_repeats_per_selected_example):
            final_examples.append(copy.deepcopy(example))

    command_type_counts: Counter[str] = Counter()
    replayed_summary_counts: Dict[str, int] = {}
    for example in final_examples:
        command_type_counts[_command_type(example)] += 1
        summary_sha256 = _example_id(example)
        replayed_summary_counts[summary_sha256] = replayed_summary_counts.get(summary_sha256, 0) + 1

    report = {
        "schema_version": "td.actual_game.command_examples_blend_report.v1",
        "base_examples_path": _display_path(base_path),
        "augment_examples_paths": [_display_path(_resolve_path(path)) for path in augment_examples_paths],
        "selected_replay_count": len(ordered_selected),
        "extra_repeats_per_selected_example": extra_repeats_per_selected_example,
        "base_example_count": len(base_examples),
        "final_example_count": len(final_examples),
        "final_command_type_counts": dict(sorted(command_type_counts.items())),
        "selected_rows": [_selected_row_summary(example) for example in ordered_selected],
        "selected_by_augment_path": dict(sorted(selected_sources.items())),
        "replayed_summary_counts": {
            summary_sha256: count
            for summary_sha256, count in sorted(replayed_summary_counts.items())
            if count > 1
        },
    }
    return schema_version, final_examples, report


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="Base examples JSON/JSONL path.")
    parser.add_argument(
        "--augment",
        dest="augment_paths",
        action="append",
        required=True,
        help="Selected examples JSON/JSONL path. Repeat to include multiple subsets.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output examples JSON path.",
    )
    parser.add_argument(
        "--report",
        required=True,
        help="Output report JSON path.",
    )
    parser.add_argument(
        "--extra-repeats-per-selected-example",
        type=int,
        default=1,
        help="How many extra copies of each selected example to append to the base corpus.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    output_path = _resolve_path(args.output)
    report_path = _resolve_path(args.report)
    schema_version, final_examples, report = build_custom_replay(
        base_examples_path=args.base,
        augment_examples_paths=args.augment_paths,
        extra_repeats_per_selected_example=args.extra_repeats_per_selected_example,
    )
    report["output_path"] = _display_path(output_path)
    report["report_path"] = _display_path(report_path)
    _write_examples(output_path, schema_version, final_examples)
    _write_report(report_path, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
