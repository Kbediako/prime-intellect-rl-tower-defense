#!/usr/bin/env python3
"""Run end-to-end actual-game command evaluation for gold or live model predictions."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any, Callable, Dict, List, Sequence, Tuple
import urllib.request
from urllib.error import HTTPError, URLError


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from prime_td_env import actual_game_env as actual_env

import score_actual_game_command_predictions as scorer


DEFAULT_EXAMPLES_PATH = Path("src/prime_td_env/data/actual_game_command/eval_examples.json")
DEFAULT_PREDICTIONS_PATH = Path("artifacts/x526_actual_game_command_model_eval/predictions.jsonl")
DEFAULT_ROWS_OUT_PATH = Path("artifacts/x526_actual_game_command_model_eval/rows.jsonl")
DEFAULT_REPORT_PATH = Path("artifacts/x526_actual_game_command_model_eval/report.json")
DEFAULT_BASE_URL = "https://api.pinference.ai/api/v1"
DEFAULT_TIMEOUT_SECONDS = 60.0
PRIME_CONFIG_PATH = Path.home() / ".prime" / "config.json"


def _resolve_path(raw_path: Path | str) -> Path:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def _load_prime_cli_config(path: Path = PRIME_CONFIG_PATH) -> Dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _resolve_prime_auth(
    *,
    api_key_env: str,
    team_id_env: str,
    base_url: str,
    path: Path = PRIME_CONFIG_PATH,
) -> Tuple[str, str | None]:
    api_key = os.getenv(api_key_env, "").strip()
    team_id = os.getenv(team_id_env, "").strip() or None
    if api_key:
        return api_key, team_id

    config = _load_prime_cli_config(path)
    inferred_base_url = str(config.get("inference_url", "") or "").strip().rstrip("/")
    if base_url.rstrip("/") != inferred_base_url and inferred_base_url:
        return api_key, team_id

    config_api_key = str(config.get("api_key", "") or "").strip()
    if not team_id:
        config_team_id = str(config.get("team_id", "") or "").strip()
        team_id = config_team_id or None
    return config_api_key, team_id


def _extract_completion_text(payload: Dict[str, Any]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("chat completion response is missing choices")
    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise ValueError("chat completion choice must be an object")
    message = first_choice.get("message")
    if isinstance(message, dict):
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text" and isinstance(item.get("text"), str):
                    text_parts.append(item["text"])
            if text_parts:
                return "".join(text_parts)
    text = first_choice.get("text")
    if isinstance(text, str):
        return text
    raise ValueError("chat completion response is missing assistant text")


def _prime_chat_completion(
    *,
    model: str,
    messages: Sequence[Dict[str, str]],
    base_url: str,
    api_key: str,
    team_id: str | None,
    temperature: float,
    max_tokens: int,
    timeout_seconds: float,
) -> Dict[str, Any]:
    payload = {
        "model": model,
        "messages": list(messages),
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "prime-intellect-rl-tower-defense/actual-game-eval",
            **({"X-Prime-Team-ID": team_id} if team_id else {}),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
        raise RuntimeError(f"chat completion failed with status {exc.code}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"network error: {exc.reason}") from exc


PredictionFn = Callable[[Dict[str, Any], Sequence[Dict[str, str]]], Dict[str, Any]]


def evaluate_examples(
    examples: Sequence[Dict[str, Any]],
    *,
    mode: str,
    model: str,
    prediction_fn: PredictionFn | None = None,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    normalized_examples = [actual_env._normalize_example(example) for example in examples]
    prediction_rows: List[Dict[str, Any]] = []
    prediction_texts: List[str] = []

    if mode == "inference" and prediction_fn is None:
        raise ValueError("prediction_fn is required for inference mode")

    for index, example in enumerate(normalized_examples):
        messages = actual_env.build_actual_game_command_messages(example["summary"])
        metadata = example.get("metadata", {})
        if mode == "gold":
            completion_text = json.dumps(example["target"], sort_keys=True)
            raw_response = {"mode": "gold"}
        else:
            raw_response = prediction_fn(example, messages)  # type: ignore[misc]
            completion_text = _extract_completion_text(raw_response)
        prediction_texts.append(completion_text)
        prediction_rows.append(
            {
                "example_index": index,
                "example_id": metadata.get("summary_sha256"),
                "messages": messages,
                "completion": completion_text,
                "target": example["target"],
                "metadata": metadata,
                "raw_response": raw_response,
            }
        )

    score_report, score_rows = scorer.score_examples(normalized_examples, prediction_texts=prediction_texts)
    score_report = dict(score_report)
    score_report["mode"] = mode
    if model:
        score_report["model"] = model
    return score_report, prediction_rows, score_rows


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
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
        "--mode",
        choices=("gold", "inference"),
        default="gold",
        help="Evaluation mode. 'gold' replays the stored target; 'inference' calls a live model.",
    )
    parser.add_argument("--model", default="", help="Model ID for inference mode.")
    parser.add_argument(
        "--base-url",
        default=os.getenv("PRIME_INFERENCE_BASE_URL", DEFAULT_BASE_URL),
        help=f"OpenAI-compatible inference base URL. Default: env PRIME_INFERENCE_BASE_URL or {DEFAULT_BASE_URL}",
    )
    parser.add_argument(
        "--api-key-env",
        default="PRIME_API_KEY",
        help="Environment variable containing the inference API key. Default: PRIME_API_KEY",
    )
    parser.add_argument(
        "--team-id-env",
        default="PRIME_TEAM_ID",
        help="Optional environment variable containing the Prime team id. Default: PRIME_TEAM_ID",
    )
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature for inference mode.")
    parser.add_argument("--max-tokens", type=int, default=256, help="Max tokens for inference mode.")
    parser.add_argument(
        "--example-limit",
        type=int,
        default=0,
        help="Optional positive cap on the number of examples to evaluate. Default: 0 (all examples).",
    )
    parser.add_argument(
        "--predictions-out",
        default=str(DEFAULT_PREDICTIONS_PATH),
        help=f"Predictions JSONL output path. Default: {DEFAULT_PREDICTIONS_PATH}",
    )
    parser.add_argument(
        "--rows-out",
        default=str(DEFAULT_ROWS_OUT_PATH),
        help=f"Per-example score rows path. Default: {DEFAULT_ROWS_OUT_PATH}",
    )
    parser.add_argument(
        "--report",
        default=str(DEFAULT_REPORT_PATH),
        help=f"Aggregate report path. Default: {DEFAULT_REPORT_PATH}",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Network timeout for inference mode. Default: {DEFAULT_TIMEOUT_SECONDS}",
    )
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    examples_path = _resolve_path(args.examples)
    predictions_out_path = _resolve_path(args.predictions_out)
    rows_out_path = _resolve_path(args.rows_out)
    report_path = _resolve_path(args.report)

    dataset_config = {"dataset": {"examples_path": str(examples_path)}}
    examples = actual_env._resolve_examples(dataset_config["dataset"])
    if args.example_limit < 0:
        raise SystemExit("--example-limit must be >= 0")
    if args.example_limit:
        examples = examples[: args.example_limit]
    if not examples:
        raise SystemExit("no examples selected for evaluation")

    prediction_fn: PredictionFn | None = None
    model = args.model.strip()
    if args.mode == "inference":
        if not model:
            raise SystemExit("--model is required in inference mode")
        api_key, team_id = _resolve_prime_auth(
            api_key_env=args.api_key_env,
            team_id_env=args.team_id_env,
            base_url=args.base_url,
        )
        if not api_key:
            raise SystemExit(
                f"missing inference api key in env var {args.api_key_env} and no matching Prime CLI login config"
            )

        def _request(example: Dict[str, Any], messages: Sequence[Dict[str, str]]) -> Dict[str, Any]:
            del example
            return _prime_chat_completion(
                model=model,
                messages=messages,
                base_url=args.base_url,
                api_key=api_key,
                team_id=team_id,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                timeout_seconds=args.timeout_seconds,
            )

        prediction_fn = _request

    report, prediction_rows, score_rows = evaluate_examples(
        examples,
        mode=args.mode,
        model=model,
        prediction_fn=prediction_fn,
    )
    report["examples_path"] = str(examples_path)
    report["prediction_count"] = len(prediction_rows)
    report["predictions_out_path"] = str(predictions_out_path)
    report["rows_out_path"] = str(rows_out_path)
    report["report_path"] = str(report_path)
    write_jsonl(predictions_out_path, prediction_rows)
    write_jsonl(rows_out_path, score_rows)
    write_json(report_path, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
