#!/usr/bin/env python3
"""Score model predictions against the Env A actual-game command contract."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from prime_td_env import actual_game_env as actual_env


DEFAULT_EXAMPLES_PATH = Path("artifacts/x523_actual_game_command_corpus/actual_game_command_examples.json")
DEFAULT_REPORT_PATH = Path("artifacts/x525_actual_game_command_prediction_scoring/report.json")
DEFAULT_ROWS_OUT_PATH = Path("artifacts/x525_actual_game_command_prediction_scoring/rows.jsonl")


def _resolve_path(raw_path: Path | str) -> Path:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def _load_examples(examples_path: Path) -> List[Dict[str, Any]]:
    dataset_config = {"dataset": {"examples_path": str(examples_path)}}
    return actual_env._resolve_examples(dataset_config["dataset"])


def _read_json_payload(path: Path) -> Any:
    raw = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in raw.splitlines() if line.strip()]
    return json.loads(raw)


def _extract_completion_text(raw_prediction: Any) -> str:
    if isinstance(raw_prediction, str):
        return raw_prediction
    if not isinstance(raw_prediction, dict):
        raise ValueError("prediction rows must be strings or objects")
    for key in ("completion", "content", "assistant", "text"):
        value = raw_prediction.get(key)
        if isinstance(value, str):
            return value
        if isinstance(value, dict) and isinstance(value.get("content"), str):
            return value["content"]
    messages = raw_prediction.get("messages")
    if isinstance(messages, list):
        for message in reversed(messages):
            if isinstance(message, dict) and message.get("role") == "assistant" and isinstance(message.get("content"), str):
                return message["content"]
    raise ValueError("prediction row is missing completion/content text")


def _load_prediction_texts(path: Path, example_count: int) -> List[str]:
    payload = _read_json_payload(path)
    if isinstance(payload, dict) and isinstance(payload.get("predictions"), list):
        payload = payload["predictions"]
    if not isinstance(payload, list):
        raise ValueError("predictions payload must be a list or {\"predictions\": [...]}")

    indexed: Dict[int, str] = {}
    ordered: List[str] = []
    for offset, raw_prediction in enumerate(payload):
        completion_text = _extract_completion_text(raw_prediction)
        if isinstance(raw_prediction, dict) and isinstance(raw_prediction.get("example_index"), int):
            if ordered:
                raise ValueError("predictions payload cannot mix ordered rows with example_index rows")
            example_index = int(raw_prediction["example_index"])
            if example_index < 0 or example_index >= example_count:
                raise ValueError(
                    f"prediction row example_index {example_index} is out of range for {example_count} examples"
                )
            if example_index in indexed:
                raise ValueError(f"duplicate prediction row for example_index {example_index}")
            indexed[example_index] = completion_text
            continue
        if indexed:
            raise ValueError("predictions payload cannot mix ordered rows with example_index rows")
        ordered.append(completion_text)

    if indexed:
        missing_indices = [index for index in range(example_count) if index not in indexed]
        if missing_indices:
            raise ValueError(
                "indexed predictions are missing rows for example_index values: "
                + ",".join(str(index) for index in missing_indices)
            )
        return [indexed[index] for index in range(example_count)]

    if len(ordered) != example_count:
        raise ValueError(f"prediction count {len(ordered)} does not match example count {example_count}")
    return ordered


def _gold_prediction_texts(examples: Sequence[Dict[str, Any]]) -> List[str]:
    return [json.dumps(example["target"], sort_keys=True) for example in examples]


def score_examples(
    examples: Sequence[Dict[str, Any]],
    *,
    prediction_texts: Sequence[str],
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    if len(prediction_texts) != len(examples):
        raise ValueError("prediction_texts length must match example count")

    format_pass_count = 0
    env_pass_count = 0
    command_type_counts: Counter[str] = Counter()
    strict_format_by_type: Counter[str] = Counter()
    exact_match_by_type: Counter[str] = Counter()
    rows: List[Dict[str, Any]] = []

    for index, (example, completion_text) in enumerate(zip(examples, prediction_texts, strict=True)):
        target = example["target"]
        summary = example["summary"]
        command_type = str(target.get("commandType", "noop"))
        command_type_counts[command_type] += 1

        completion = [{"role": "assistant", "content": completion_text}]
        info = {"summary": summary, "target": target}
        format_score = actual_env._actual_game_command_format_reward([], completion, "", {}, info=info)
        env_score = actual_env._actual_game_command_env_reward([], completion, "", {}, info=info)
        if format_score == 1.0:
            format_pass_count += 1
            strict_format_by_type[command_type] += 1
        if env_score == 1.0:
            env_pass_count += 1
            exact_match_by_type[command_type] += 1

        rows.append(
            {
                "example_index": index,
                "command_type": command_type,
                "format_score": format_score,
                "env_score": env_score,
                "completion": completion_text,
                "target": target,
                "metadata": example.get("metadata", {}),
            }
        )

    example_count = len(examples)
    report = {
        "example_count": example_count,
        "format_pass_count": format_pass_count,
        "env_pass_count": env_pass_count,
        "format_pass_rate": float(format_pass_count) / float(example_count) if example_count else 0.0,
        "env_pass_rate": float(env_pass_count) / float(example_count) if example_count else 0.0,
        "command_type_counts": dict(sorted(command_type_counts.items())),
        "strict_format_by_type": dict(sorted(strict_format_by_type.items())),
        "exact_match_by_type": dict(sorted(exact_match_by_type.items())),
    }
    return report, rows


def score_examples_file(
    examples_path: Path,
    *,
    prediction_texts: Sequence[str],
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    report, rows = score_examples(_load_examples(examples_path), prediction_texts=prediction_texts)
    report = dict(report)
    report["examples_path"] = str(examples_path)
    return report, rows


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "\n".join(json.dumps(row, sort_keys=True) for row in rows)
    path.write_text(payload + ("\n" if payload else ""), encoding="utf-8")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--examples",
        default=str(DEFAULT_EXAMPLES_PATH),
        help=f"Env A corpus examples file. Default: {DEFAULT_EXAMPLES_PATH}",
    )
    parser.add_argument(
        "--predictions",
        default="",
        help="Predictions JSON/JSONL file. Rows may be strings or objects with completion/content/example_index.",
    )
    parser.add_argument(
        "--mode",
        choices=("gold",),
        default="",
        help="Use synthesized predictions instead of a predictions file. 'gold' replays the stored target.",
    )
    parser.add_argument(
        "--report",
        default=str(DEFAULT_REPORT_PATH),
        help=f"Aggregate score report path. Default: {DEFAULT_REPORT_PATH}",
    )
    parser.add_argument(
        "--rows-out",
        default=str(DEFAULT_ROWS_OUT_PATH),
        help=f"Per-example score rows path. Default: {DEFAULT_ROWS_OUT_PATH}",
    )
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    examples_path = _resolve_path(args.examples)
    report_path = _resolve_path(args.report)
    rows_out_path = _resolve_path(args.rows_out)
    examples = _load_examples(examples_path)
    if args.mode == "gold":
        prediction_texts = _gold_prediction_texts(examples)
    elif args.predictions:
        prediction_texts = _load_prediction_texts(_resolve_path(args.predictions), len(examples))
    else:
        raise SystemExit("provide either --predictions or --mode gold")

    report, rows = score_examples(examples, prediction_texts=prediction_texts)
    report["examples_path"] = str(examples_path)
    report["report_path"] = str(report_path)
    report["rows_out_path"] = str(rows_out_path)
    write_json(report_path, report)
    write_jsonl(rows_out_path, rows)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
