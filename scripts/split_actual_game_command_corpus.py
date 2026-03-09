#!/usr/bin/env python3
"""Create deterministic train/eval splits for the Env A actual-game corpus."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXAMPLES_PATH = Path("artifacts/x523_actual_game_command_corpus/actual_game_command_examples.json")
DEFAULT_OUTPUT_DIR = Path("artifacts/x526_actual_game_command_splits")
DEFAULT_TRAIN_PATH = DEFAULT_OUTPUT_DIR / "train_examples.json"
DEFAULT_EVAL_PATH = DEFAULT_OUTPUT_DIR / "eval_examples.json"
DEFAULT_REPORT_PATH = DEFAULT_OUTPUT_DIR / "split_report.json"
EXAMPLES_SCHEMA_VERSION = "td.actual_game.command_examples.v1"


def _resolve_path(raw_path: Path | str) -> Path:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def _read_examples_payload(path: Path) -> Tuple[str, List[Dict[str, Any]]]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        return EXAMPLES_SCHEMA_VERSION, [json.loads(line) for line in raw.splitlines() if line.strip()]
    payload = json.loads(raw)
    if isinstance(payload, list):
        return EXAMPLES_SCHEMA_VERSION, payload
    if isinstance(payload, dict) and isinstance(payload.get("examples"), list):
        schema_version = payload.get("schemaVersion")
        if not isinstance(schema_version, str) or not schema_version.strip():
            schema_version = EXAMPLES_SCHEMA_VERSION
        return schema_version, payload["examples"]
    raise ValueError(f"Unsupported examples payload in {path}")


def _example_id(example: Dict[str, Any]) -> str:
    metadata = example.get("metadata")
    if isinstance(metadata, dict):
        summary_sha256 = metadata.get("summary_sha256")
        if isinstance(summary_sha256, str) and summary_sha256.strip():
            return summary_sha256
    raise ValueError("split examples require metadata.summary_sha256")


def _command_type(example: Dict[str, Any]) -> str:
    target = example.get("target")
    if not isinstance(target, dict):
        return "unknown"
    command_type = target.get("commandType")
    return str(command_type or "noop")


def _source_paths(example: Dict[str, Any]) -> List[str]:
    metadata = example.get("metadata")
    if not isinstance(metadata, dict):
        return []
    raw_records = metadata.get("source_instances", metadata.get("sourceRecords", []))
    if not isinstance(raw_records, list):
        return []
    paths = set()
    for record in raw_records:
        if not isinstance(record, dict):
            continue
        source_path = record.get("source_path", record.get("path"))
        if isinstance(source_path, str) and source_path:
            paths.add(source_path)
    return sorted(paths)


def _count_command_types(examples: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    counts: Counter[str] = Counter()
    for example in examples:
        counts[_command_type(example)] += 1
    return dict(sorted(counts.items()))


def _count_source_paths(examples: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    counts: Counter[str] = Counter()
    for example in examples:
        source_paths = _source_paths(example)
        if source_paths:
            for source_path in source_paths:
                counts[source_path] += 1
        else:
            counts["unknown"] += 1
    return dict(sorted(counts.items()))


def split_examples(
    examples: Sequence[Dict[str, Any]],
    *,
    eval_fraction: float = 0.2,
    min_eval_per_command_type: int = 1,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    if not 0.0 <= eval_fraction < 1.0:
        raise ValueError("eval_fraction must be in [0.0, 1.0)")
    if min_eval_per_command_type < 0:
        raise ValueError("min_eval_per_command_type must be >= 0")

    grouped: Dict[str, List[Dict[str, Any]]] = {}
    seen_example_ids: Dict[str, str] = {}
    for example in examples:
        example_id = _example_id(example)
        canonical_target = json.dumps(example.get("target", {}), sort_keys=True, separators=(",", ":"))
        if example_id in seen_example_ids:
            if seen_example_ids[example_id] != canonical_target:
                raise ValueError(f"conflicting targets for summary_sha256 {example_id}")
            raise ValueError(f"duplicate summary_sha256 {example_id}; split input must be deduplicated")
        seen_example_ids[example_id] = canonical_target
        grouped.setdefault(_command_type(example), []).append(example)

    train_examples: List[Dict[str, Any]] = []
    eval_examples: List[Dict[str, Any]] = []
    split_by_command_type: Dict[str, Dict[str, int]] = {}

    for command_type in sorted(grouped):
        command_examples = sorted(grouped[command_type], key=_example_id)
        example_count = len(command_examples)
        if example_count <= 1:
            eval_count = 0
        else:
            fractional_eval = int(round(example_count * eval_fraction))
            eval_count = max(min_eval_per_command_type, fractional_eval)
            eval_count = min(eval_count, example_count - 1)

        eval_slice = command_examples[:eval_count]
        train_slice = command_examples[eval_count:]
        train_examples.extend(train_slice)
        eval_examples.extend(eval_slice)
        split_by_command_type[command_type] = {
            "train": len(train_slice),
            "eval": len(eval_slice),
        }

    train_examples = sorted(train_examples, key=_example_id)
    eval_examples = sorted(eval_examples, key=_example_id)

    report = {
        "example_count": len(examples),
        "train_count": len(train_examples),
        "eval_count": len(eval_examples),
        "eval_fraction": eval_fraction,
        "min_eval_per_command_type": min_eval_per_command_type,
        "command_type_counts": _count_command_types(examples),
        "train_command_type_counts": _count_command_types(train_examples),
        "eval_command_type_counts": _count_command_types(eval_examples),
        "train_source_path_counts": _count_source_paths(train_examples),
        "eval_source_path_counts": _count_source_paths(eval_examples),
        "split_by_command_type": split_by_command_type,
    }
    return train_examples, eval_examples, report


def write_examples(path: Path, schema_version: str, examples: Sequence[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schemaVersion": schema_version,
        "examples": list(examples),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_report(path: Path, report: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--examples",
        default=str(DEFAULT_EXAMPLES_PATH),
        help=f"Input examples JSON/JSONL. Default: {DEFAULT_EXAMPLES_PATH}",
    )
    parser.add_argument(
        "--train-output",
        default=str(DEFAULT_TRAIN_PATH),
        help=f"Train split examples output path. Default: {DEFAULT_TRAIN_PATH}",
    )
    parser.add_argument(
        "--eval-output",
        default=str(DEFAULT_EVAL_PATH),
        help=f"Eval split examples output path. Default: {DEFAULT_EVAL_PATH}",
    )
    parser.add_argument(
        "--report",
        default=str(DEFAULT_REPORT_PATH),
        help=f"Split report path. Default: {DEFAULT_REPORT_PATH}",
    )
    parser.add_argument(
        "--eval-fraction",
        type=float,
        default=0.2,
        help="Fraction of each command type assigned to eval. Default: 0.2",
    )
    parser.add_argument(
        "--min-eval-per-command-type",
        type=int,
        default=1,
        help="Minimum eval examples per command type when possible. Default: 1",
    )
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    examples_path = _resolve_path(args.examples)
    train_output_path = _resolve_path(args.train_output)
    eval_output_path = _resolve_path(args.eval_output)
    report_path = _resolve_path(args.report)

    schema_version, examples = _read_examples_payload(examples_path)
    train_examples, eval_examples, report = split_examples(
        examples,
        eval_fraction=args.eval_fraction,
        min_eval_per_command_type=args.min_eval_per_command_type,
    )
    write_examples(train_output_path, schema_version, train_examples)
    write_examples(eval_output_path, schema_version, eval_examples)

    report = dict(report)
    report["examples_path"] = str(examples_path)
    report["train_output_path"] = str(train_output_path)
    report["eval_output_path"] = str(eval_output_path)
    report["report_path"] = str(report_path)
    write_report(report_path, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
