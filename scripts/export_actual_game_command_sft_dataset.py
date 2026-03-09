#!/usr/bin/env python3
"""Export the Env A corpus to a chat-style SFT dataset."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import sys
from typing import Any, Dict, List, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from prime_td_env import actual_game_env as actual_env


DEFAULT_EXAMPLES_PATH = Path("src/prime_td_env/data/actual_game_command/train_examples.json")
DEFAULT_OUTPUT_PATH = Path("artifacts/x524_actual_game_command_sft_dataset/messages.jsonl")
DEFAULT_REPORT_PATH = Path("artifacts/x524_actual_game_command_sft_dataset/export_report.json")


def _resolve_path(raw_path: Path | str) -> Path:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def _select_evenly_spaced(entries: Sequence[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
    if limit <= 0:
        return []
    if limit >= len(entries):
        return list(entries)
    return [entries[math.floor(index * len(entries) / limit)] for index in range(limit)]


def _apply_noop_balance(
    examples: Sequence[Dict[str, Any]],
    *,
    max_noop_multiple: float | None,
) -> List[Dict[str, Any]]:
    if max_noop_multiple is None:
        return list(examples)
    if max_noop_multiple < 0:
        raise ValueError("max_noop_multiple must be >= 0 when provided")

    command_examples = [example for example in examples if example["target"].get("kind") == "command"]
    noop_examples = [example for example in examples if example["target"].get("kind") != "command"]
    noop_limit = int(math.floor(len(command_examples) * max_noop_multiple))
    selected_noops = _select_evenly_spaced(noop_examples, noop_limit)
    selected_noop_ids = {id(example) for example in selected_noops}
    return [
        example
        for example in examples
        if example["target"].get("kind") == "command" or id(example) in selected_noop_ids
    ]


def export_examples_file(
    examples_path: Path,
    *,
    max_noop_multiple: float | None = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    dataset_config = {"dataset": {"examples_path": str(examples_path)}}
    examples = actual_env._resolve_examples(dataset_config["dataset"])
    selected_examples = _apply_noop_balance(examples, max_noop_multiple=max_noop_multiple)
    rows: List[Dict[str, Any]] = []
    command_type_counts: Counter[str] = Counter()
    source_path_counts: Counter[str] = Counter()

    for example in selected_examples:
        target = example["target"]
        metadata = example.get("metadata", {})
        assistant_content = json.dumps(target, sort_keys=True)
        rows.append(
            {
                "schemaVersion": "td.actual_game.sft_example.v1",
                "messages": [*actual_env.build_actual_game_command_messages(example["summary"]), {"role": "assistant", "content": assistant_content}],
                "metadata": {
                    "example_id": metadata.get("summary_sha256"),
                    "target_sha256": metadata.get("target_sha256"),
                    "source_paths": sorted(
                        {
                            source_instance.get("source_path")
                            for source_instance in metadata.get("source_instances", [])
                            if isinstance(source_instance, dict) and isinstance(source_instance.get("source_path"), str)
                        }
                    ),
                },
            }
        )
        command_type_counts[target.get("commandType", "noop")] += 1
        source_instances = metadata.get("source_instances")
        if isinstance(source_instances, list) and source_instances:
            for source_instance in source_instances:
                source_path = source_instance.get("source_path")
                if isinstance(source_path, str) and source_path:
                    source_path_counts[source_path] += 1
        else:
            source_path_counts["unknown"] += 1

    report = {
        "examples_path": str(examples_path),
        "input_row_count": len(examples),
        "row_count": len(rows),
        "command_type_counts": dict(sorted(command_type_counts.items())),
        "source_path_counts": dict(sorted(source_path_counts.items())),
        "max_noop_multiple": max_noop_multiple,
    }
    return rows, report


def write_jsonl(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "\n".join(json.dumps(row, sort_keys=True) for row in rows)
    path.write_text(payload + ("\n" if payload else ""), encoding="utf-8")


def write_report(path: Path, report: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--examples",
        default=str(DEFAULT_EXAMPLES_PATH),
        help=f"Env A corpus examples file. Default: {DEFAULT_EXAMPLES_PATH}",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help=f"SFT JSONL output path. Default: {DEFAULT_OUTPUT_PATH}",
    )
    parser.add_argument(
        "--report",
        default=str(DEFAULT_REPORT_PATH),
        help=f"Export report path. Default: {DEFAULT_REPORT_PATH}",
    )
    parser.add_argument(
        "--max-noop-multiple",
        type=float,
        default=None,
        help="Optional cap on exported noop rows as a multiple of command rows.",
    )
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    examples_path = _resolve_path(args.examples)
    output_path = _resolve_path(args.output)
    report_path = _resolve_path(args.report)
    rows, report = export_examples_file(
        examples_path,
        max_noop_multiple=args.max_noop_multiple,
    )
    write_jsonl(output_path, rows)
    report = dict(report)
    report["output_path"] = str(output_path)
    report["report_path"] = str(report_path)
    write_report(report_path, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
