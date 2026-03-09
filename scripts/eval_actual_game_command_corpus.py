#!/usr/bin/env python3
"""Run a replay sanity eval over an Env A actual-game command corpus."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any, Dict


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from prime_td_env import actual_game_env as actual_env


DEFAULT_EXAMPLES_PATH = Path("artifacts/x523_actual_game_command_corpus/actual_game_command_examples.json")
DEFAULT_REPORT_PATH = Path("artifacts/x523_actual_game_command_corpus/eval_report.json")


def _resolve_path(raw_path: Path | str) -> Path:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def evaluate_examples_file(examples_path: Path) -> Dict[str, Any]:
    dataset_config = {"dataset": {"examples_path": str(examples_path)}}
    examples = actual_env._resolve_examples(dataset_config["dataset"])

    dataset_prompt_count = None
    dataset_answer_count = None
    env_class = None
    runtime_note = None
    if actual_env.Dataset is not None and actual_env.vf is not None:
        dataset = actual_env._build_actual_game_command_dataset(dataset_config, num_examples=-1, seed_start=0)
        env = actual_env.load_environment(dataset_config, num_examples=-1, seed_start=0)
        dataset_prompt_count = len(dataset["prompt"])
        dataset_answer_count = len(dataset["answer"])
        env_class = env.__class__.__name__
    else:
        runtime_note = (
            "Skipped dataset/env construction because 'datasets' and/or 'verifiers' are not installed."
        )

    replay_format_pass_count = 0
    replay_env_pass_count = 0
    schema_version_counts: Counter[str] = Counter()
    command_type_counts: Counter[str] = Counter()
    source_path_counts: Counter[str] = Counter()

    for example in examples:
        target = example["target"]
        summary = example["summary"]
        completion = [{"role": "assistant", "content": json.dumps(target, sort_keys=True)}]
        info = {"summary": summary, "target": target}
        format_score = actual_env._actual_game_command_format_reward([], completion, "", {}, info=info)
        env_score = actual_env._actual_game_command_env_reward([], completion, "", {}, info=info)
        if format_score == 1.0:
            replay_format_pass_count += 1
        if env_score == 1.0:
            replay_env_pass_count += 1
        schema_version_counts[summary["schemaVersion"]] += 1
        command_type_counts[target.get("commandType", "noop")] += 1
        metadata = example.get("metadata", {})
        source_instances = metadata.get("source_instances")
        if isinstance(source_instances, list) and source_instances:
            for source_instance in source_instances:
                source_path = source_instance.get("source_path")
                if isinstance(source_path, str) and source_path:
                    source_path_counts[source_path] += 1
        else:
            source_records = metadata.get("sourceRecords")
            if isinstance(source_records, list) and source_records:
                for source_record in source_records:
                    source_path = source_record.get("path")
                    if isinstance(source_path, str) and source_path:
                        source_path_counts[source_path] += 1
                continue
            source_path_counts["unknown"] += 1

    example_count = len(examples)
    return {
        "examples_path": str(examples_path),
        "example_count": example_count,
        "training_runtime_available": actual_env.Dataset is not None and actual_env.vf is not None,
        "dataset_prompt_count": dataset_prompt_count,
        "dataset_answer_count": dataset_answer_count,
        "env_class": env_class,
        "runtime_note": runtime_note,
        "schema_version_counts": dict(sorted(schema_version_counts.items())),
        "command_type_counts": dict(sorted(command_type_counts.items())),
        "source_path_counts": dict(sorted(source_path_counts.items())),
        "replay_format_pass_count": replay_format_pass_count,
        "replay_env_pass_count": replay_env_pass_count,
        "replay_format_pass_rate": float(replay_format_pass_count) / float(example_count) if example_count else 0.0,
        "replay_env_pass_rate": float(replay_env_pass_count) / float(example_count) if example_count else 0.0,
    }


def write_report(path: Path, report: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay-sanity eval for Env A actual-game command corpus.")
    parser.add_argument(
        "--examples",
        default=str(DEFAULT_EXAMPLES_PATH),
        help=f"JSON/JSONL examples file. Default: {DEFAULT_EXAMPLES_PATH}",
    )
    parser.add_argument(
        "--report",
        default=str(DEFAULT_REPORT_PATH),
        help=f"Where to write eval report JSON. Default: {DEFAULT_REPORT_PATH}",
    )
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    examples_path = _resolve_path(args.examples)
    report_path = _resolve_path(args.report)
    report = evaluate_examples_file(examples_path)
    report = dict(report)
    report["report_path"] = str(report_path)
    write_report(report_path, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
