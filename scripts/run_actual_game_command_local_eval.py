#!/usr/bin/env python3
"""Run actual-game command eval against a local Transformers model or adapter."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Dict, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import run_actual_game_command_eval as base_eval


DEFAULT_EXAMPLES_PATH = Path("src/prime_td_env/data/actual_game_command/eval_examples.json")
DEFAULT_PREDICTIONS_PATH = Path("artifacts/x533_actual_game_command_local_eval/predictions.jsonl")
DEFAULT_ROWS_OUT_PATH = Path("artifacts/x533_actual_game_command_local_eval/rows.jsonl")
DEFAULT_REPORT_PATH = Path("artifacts/x533_actual_game_command_local_eval/report.json")


def _resolve_path(raw_path: Path | str) -> Path:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def _load_transformers_runtime() -> Tuple[Any, Any, Any, Any, Any]:
    try:
        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    except ImportError as exc:  # pragma: no cover - dependency surfaced at runtime
        raise SystemExit(
            "Transformers local eval requires torch, transformers, peft, accelerate, and optionally bitsandbytes."
        ) from exc
    return torch, AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, PeftModel


def _default_torch_dtype(torch: Any) -> Any:
    if not torch.cuda.is_available():
        return torch.float32
    if torch.cuda.is_bf16_supported():
        return torch.bfloat16
    return torch.float16


def _model_device(model: Any) -> Any:
    try:
        return next(model.parameters()).device
    except StopIteration:  # pragma: no cover - defensive for empty parameter iterators
        return None


def _load_model_bundle(
    *,
    model_name: str,
    adapter_path: Path | None,
    load_in_4bit: bool,
) -> Dict[str, Any]:
    torch, AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, PeftModel = _load_transformers_runtime()
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model_kwargs: Dict[str, Any] = {
        "trust_remote_code": True,
    }
    if torch.cuda.is_available():
        model_kwargs["device_map"] = "auto"
    if load_in_4bit:
        model_kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=_default_torch_dtype(torch),
        )
    else:
        model_kwargs["torch_dtype"] = _default_torch_dtype(torch)

    model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
    if adapter_path is not None:
        model = PeftModel.from_pretrained(model, str(adapter_path))
    model.eval()
    return {
        "torch": torch,
        "tokenizer": tokenizer,
        "model": model,
        "adapter_path": str(adapter_path) if adapter_path is not None else None,
    }


def _build_prediction_fn(
    *,
    bundle: Dict[str, Any],
    temperature: float,
    max_new_tokens: int,
):
    torch = bundle["torch"]
    tokenizer = bundle["tokenizer"]
    model = bundle["model"]

    def _predict(_example: Dict[str, Any], messages: Sequence[Dict[str, str]]) -> Dict[str, Any]:
        prompt_text = tokenizer.apply_chat_template(
            list(messages),
            tokenize=False,
            add_generation_prompt=True,
        )
        encoded = tokenizer(prompt_text, return_tensors="pt", add_special_tokens=False)
        device = _model_device(model)
        if device is not None:
            encoded = {key: value.to(device) for key, value in encoded.items()}

        generation_kwargs: Dict[str, Any] = {
            "max_new_tokens": max_new_tokens,
            "pad_token_id": tokenizer.pad_token_id,
            "eos_token_id": tokenizer.eos_token_id,
        }
        if temperature > 0:
            generation_kwargs["do_sample"] = True
            generation_kwargs["temperature"] = temperature
        else:
            generation_kwargs["do_sample"] = False

        with torch.no_grad():
            output = model.generate(**encoded, **generation_kwargs)

        prompt_len = encoded["input_ids"].shape[1]
        completion_ids = output[0][prompt_len:]
        completion_text = tokenizer.decode(completion_ids, skip_special_tokens=True).strip()
        return {"choices": [{"message": {"content": completion_text}}]}

    return _predict


def evaluate_examples(
    examples: Sequence[Dict[str, Any]],
    *,
    model_label: str,
    predictor,
    adapter_path: str = "",
):
    def _prediction_fn(example: Dict[str, Any], messages: Sequence[Dict[str, str]]) -> Dict[str, Any]:
        completion_text = predictor(example, messages)
        return {"choices": [{"message": {"content": completion_text}}]}

    report, prediction_rows, score_rows = base_eval.evaluate_examples(
        examples,
        mode="inference",
        model=model_label,
        prediction_fn=_prediction_fn,
    )
    report = dict(report)
    report["mode"] = "local_transformers"
    report["adapter_path"] = adapter_path or None
    return report, prediction_rows, score_rows


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--examples",
        default=str(DEFAULT_EXAMPLES_PATH),
        help=f"Eval examples file. Default: {DEFAULT_EXAMPLES_PATH}",
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Base Hugging Face model id or local model path.",
    )
    parser.add_argument(
        "--adapter-path",
        default="",
        help="Optional PEFT adapter directory to apply on top of --model.",
    )
    parser.add_argument(
        "--predictions-out",
        default=str(DEFAULT_PREDICTIONS_PATH),
        help=f"Prediction rows JSONL path. Default: {DEFAULT_PREDICTIONS_PATH}",
    )
    parser.add_argument(
        "--rows-out",
        default=str(DEFAULT_ROWS_OUT_PATH),
        help=f"Scored rows JSONL path. Default: {DEFAULT_ROWS_OUT_PATH}",
    )
    parser.add_argument(
        "--report",
        default=str(DEFAULT_REPORT_PATH),
        help=f"Report JSON path. Default: {DEFAULT_REPORT_PATH}",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature. Default: 0.0 (greedy).",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=128,
        help="Maximum generated completion tokens. Default: 128",
    )
    parser.add_argument(
        "--load-in-4bit",
        action="store_true",
        help="Load the base model in 4-bit quantized mode.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    examples_path = _resolve_path(args.examples)
    predictions_out_path = _resolve_path(args.predictions_out)
    rows_out_path = _resolve_path(args.rows_out)
    report_path = _resolve_path(args.report)
    adapter_path = _resolve_path(args.adapter_path) if args.adapter_path else None

    dataset_config = {"dataset": {"examples_path": str(examples_path)}}
    examples = base_eval.actual_env._resolve_examples(dataset_config["dataset"])
    bundle = _load_model_bundle(
        model_name=args.model,
        adapter_path=adapter_path,
        load_in_4bit=args.load_in_4bit,
    )
    prediction_fn = _build_prediction_fn(
        bundle=bundle,
        temperature=args.temperature,
        max_new_tokens=args.max_new_tokens,
    )
    report, prediction_rows, score_rows = evaluate_examples(
        examples,
        model_label=args.model,
        predictor=lambda example, messages: prediction_fn(example, messages)["choices"][0]["message"]["content"],
        adapter_path=str(adapter_path) if adapter_path is not None else "",
    )
    report["examples_path"] = str(examples_path)
    report["predictions_out_path"] = str(predictions_out_path)
    report["rows_out_path"] = str(rows_out_path)
    report["report_path"] = str(report_path)
    report["load_in_4bit"] = bool(args.load_in_4bit)

    base_eval.write_jsonl(predictions_out_path, prediction_rows)
    base_eval.write_jsonl(rows_out_path, score_rows)
    base_eval.write_json(report_path, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
