#!/usr/bin/env python3
"""Train a minimal LoRA SFT adapter on the actual-game command dataset."""

from __future__ import annotations

import argparse
import inspect
import json
from pathlib import Path
import shutil
import sys
from typing import Any, Dict, List, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import run_actual_game_command_local_eval as local_eval


DEFAULT_TRAIN_JSONL = Path("artifacts/x532_actual_game_command_sft_inputs/train_messages.jsonl")
DEFAULT_EVAL_JSONL = Path("artifacts/x532_actual_game_command_sft_inputs/eval_messages.jsonl")
DEFAULT_OUTPUT_DIR = Path("artifacts/x533_actual_game_command_sft_run/adapter")
DEFAULT_REPORT_PATH = Path("artifacts/x533_actual_game_command_sft_run/train_report.json")
DEFAULT_EVAL_REPORT_PATH = Path("artifacts/x533_actual_game_command_sft_run/eval_report.json")
DEFAULT_EVAL_PREDICTIONS_PATH = Path("artifacts/x533_actual_game_command_sft_run/eval_predictions.jsonl")
DEFAULT_EVAL_ROWS_PATH = Path("artifacts/x533_actual_game_command_sft_run/eval_rows.jsonl")

DEFAULT_TARGET_MODULES = (
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
)


def _resolve_path(raw_path: Path | str) -> Path:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def _load_transformers_runtime() -> Dict[str, Any]:
    try:
        import torch
        from datasets import Dataset
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, Trainer, TrainingArguments
    except ImportError as exc:  # pragma: no cover - dependency surfaced at runtime
        raise SystemExit(
            "SFT training requires torch, datasets, transformers, peft, accelerate, and optionally bitsandbytes."
        ) from exc
    return {
        "torch": torch,
        "Dataset": Dataset,
        "LoraConfig": LoraConfig,
        "get_peft_model": get_peft_model,
        "prepare_model_for_kbit_training": prepare_model_for_kbit_training,
        "AutoModelForCausalLM": AutoModelForCausalLM,
        "AutoTokenizer": AutoTokenizer,
        "BitsAndBytesConfig": BitsAndBytesConfig,
        "Trainer": Trainer,
        "TrainingArguments": TrainingArguments,
    }


def _default_torch_dtype(torch: Any) -> Any:
    if not torch.cuda.is_available():
        return torch.float32
    if torch.cuda.is_bf16_supported():
        return torch.bfloat16
    return torch.float16


def _load_jsonl_rows(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError(f"{path} contains a non-object row")
            rows.append(payload)
    if not rows:
        raise ValueError(f"{path} did not contain any rows")
    return rows


def build_run_report(
    *,
    base_model: str,
    train_examples_path: Path,
    train_dataset_path: Path,
    export_report_path: Path,
    output_dir: Path,
    training_config: Dict[str, Any],
    train_metrics: Dict[str, Any],
    eval_report_path: Path,
) -> Dict[str, Any]:
    return {
        "base_model": base_model,
        "train_examples_path": str(train_examples_path),
        "train_dataset_path": str(train_dataset_path),
        "export_report_path": str(export_report_path),
        "output_dir": str(output_dir),
        "training_config": training_config,
        "train_metrics": train_metrics,
        "eval_report_path": str(eval_report_path),
    }


def _tokenize_chat_rows(
    rows: Sequence[Dict[str, Any]],
    *,
    tokenizer: Any,
    max_seq_len: int,
) -> List[Dict[str, Any]]:
    tokenized_rows: List[Dict[str, Any]] = []
    for row in rows:
        messages = row.get("messages")
        if not isinstance(messages, list) or len(messages) < 2:
            raise ValueError("SFT rows must contain a non-empty messages list with a final assistant turn")
        prompt_messages = messages[:-1]
        full_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
        prompt_text = tokenizer.apply_chat_template(prompt_messages, tokenize=False, add_generation_prompt=True)
        full_ids = tokenizer(full_text, add_special_tokens=False)["input_ids"]
        prompt_ids = tokenizer(prompt_text, add_special_tokens=False)["input_ids"]
        if full_ids[: len(prompt_ids)] != prompt_ids:
            raise ValueError("Prompt token prefix mismatch while building assistant-only labels")
        labels = list(full_ids)
        for index in range(len(prompt_ids)):
            labels[index] = -100
        full_ids = full_ids[:max_seq_len]
        labels = labels[:max_seq_len]
        attention_mask = [1] * len(full_ids)
        tokenized_rows.append(
            {
                "input_ids": full_ids,
                "labels": labels,
                "attention_mask": attention_mask,
            }
        )
    return tokenized_rows


class _SupervisedDataCollator:
    def __init__(self, *, tokenizer: Any, torch: Any) -> None:
        self.tokenizer = tokenizer
        self.torch = torch

    def __call__(self, features: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        max_len = max(len(feature["input_ids"]) for feature in features)
        pad_id = self.tokenizer.pad_token_id
        input_ids: List[List[int]] = []
        attention_mask: List[List[int]] = []
        labels: List[List[int]] = []
        for feature in features:
            pad_width = max_len - len(feature["input_ids"])
            input_ids.append(feature["input_ids"] + [pad_id] * pad_width)
            attention_mask.append(feature["attention_mask"] + [0] * pad_width)
            labels.append(feature["labels"] + [-100] * pad_width)
        return {
            "input_ids": self.torch.tensor(input_ids, dtype=self.torch.long),
            "attention_mask": self.torch.tensor(attention_mask, dtype=self.torch.long),
            "labels": self.torch.tensor(labels, dtype=self.torch.long),
        }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Base Hugging Face model id.")
    parser.add_argument(
        "--train-jsonl",
        default=str(DEFAULT_TRAIN_JSONL),
        help=f"Training chat dataset JSONL. Default: {DEFAULT_TRAIN_JSONL}",
    )
    parser.add_argument(
        "--eval-jsonl",
        default=str(DEFAULT_EVAL_JSONL),
        help=f"Evaluation chat dataset JSONL. Default: {DEFAULT_EVAL_JSONL}",
    )
    parser.add_argument(
        "--train-examples-path",
        default="src/prime_td_env/data/actual_game_command/train_examples.json",
        help="Train examples JSON used for provenance reporting.",
    )
    parser.add_argument(
        "--train-export-report",
        default="artifacts/x532_actual_game_command_sft_inputs/train_export_report.json",
        help="Train export report JSON used for provenance reporting.",
    )
    parser.add_argument(
        "--examples",
        default="src/prime_td_env/data/actual_game_command/eval_examples.json",
        help="Eval examples JSON used for post-train scoring.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Adapter output directory. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--report",
        default=str(DEFAULT_REPORT_PATH),
        help=f"Training report path. Default: {DEFAULT_REPORT_PATH}",
    )
    parser.add_argument(
        "--eval-report",
        default=str(DEFAULT_EVAL_REPORT_PATH),
        help=f"Post-train eval report path. Default: {DEFAULT_EVAL_REPORT_PATH}",
    )
    parser.add_argument(
        "--eval-predictions-out",
        default=str(DEFAULT_EVAL_PREDICTIONS_PATH),
        help=f"Post-train prediction rows JSONL path. Default: {DEFAULT_EVAL_PREDICTIONS_PATH}",
    )
    parser.add_argument(
        "--eval-rows-out",
        default=str(DEFAULT_EVAL_ROWS_PATH),
        help=f"Post-train scored rows JSONL path. Default: {DEFAULT_EVAL_ROWS_PATH}",
    )
    parser.add_argument("--epochs", type=float, default=6.0, help="Training epochs. Default: 6")
    parser.add_argument("--learning-rate", type=float, default=2e-4, help="Learning rate. Default: 2e-4")
    parser.add_argument("--batch-size", type=int, default=4, help="Per-device train batch size. Default: 4")
    parser.add_argument("--eval-batch-size", type=int, default=4, help="Per-device eval batch size. Default: 4")
    parser.add_argument("--grad-accum", type=int, default=4, help="Gradient accumulation steps. Default: 4")
    parser.add_argument("--max-seq-len", type=int, default=2048, help="Maximum training sequence length. Default: 2048")
    parser.add_argument("--warmup-ratio", type=float, default=0.05, help="Warmup ratio. Default: 0.05")
    parser.add_argument("--weight-decay", type=float, default=0.0, help="Weight decay. Default: 0.0")
    parser.add_argument("--lora-r", type=int, default=16, help="LoRA rank. Default: 16")
    parser.add_argument("--lora-alpha", type=int, default=32, help="LoRA alpha. Default: 32")
    parser.add_argument("--lora-dropout", type=float, default=0.05, help="LoRA dropout. Default: 0.05")
    parser.add_argument(
        "--target-modules",
        nargs="+",
        default=list(DEFAULT_TARGET_MODULES),
        help="LoRA target modules. Default: q_proj k_proj v_proj o_proj gate_proj up_proj down_proj",
    )
    parser.add_argument("--seed", type=int, default=17, help="Random seed. Default: 17")
    parser.add_argument("--load-in-4bit", action="store_true", help="Load the base model in 4-bit quantized mode.")
    parser.add_argument(
        "--save-tokenizer",
        action="store_true",
        help="Also save tokenizer files into --output-dir. Disabled by default to keep adapter bundles small.",
    )
    parser.add_argument("--skip-post-train-eval", action="store_true", help="Skip local eval after training.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    runtime = _load_transformers_runtime()
    torch = runtime["torch"]
    Dataset = runtime["Dataset"]
    LoraConfig = runtime["LoraConfig"]
    get_peft_model = runtime["get_peft_model"]
    prepare_model_for_kbit_training = runtime["prepare_model_for_kbit_training"]
    AutoModelForCausalLM = runtime["AutoModelForCausalLM"]
    AutoTokenizer = runtime["AutoTokenizer"]
    BitsAndBytesConfig = runtime["BitsAndBytesConfig"]
    Trainer = runtime["Trainer"]
    TrainingArguments = runtime["TrainingArguments"]

    train_jsonl = _resolve_path(args.train_jsonl)
    eval_jsonl = _resolve_path(args.eval_jsonl)
    train_examples_path = _resolve_path(args.train_examples_path)
    train_export_report_path = _resolve_path(args.train_export_report)
    examples_path = _resolve_path(args.examples)
    output_dir = _resolve_path(args.output_dir)
    report_path = _resolve_path(args.report)
    eval_report_path = _resolve_path(args.eval_report)
    eval_predictions_path = _resolve_path(args.eval_predictions_out)
    eval_rows_path = _resolve_path(args.eval_rows_out)

    train_rows = _load_jsonl_rows(train_jsonl)
    eval_rows = _load_jsonl_rows(eval_jsonl)

    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    train_features = _tokenize_chat_rows(train_rows, tokenizer=tokenizer, max_seq_len=args.max_seq_len)
    eval_features = _tokenize_chat_rows(eval_rows, tokenizer=tokenizer, max_seq_len=args.max_seq_len)
    train_dataset = Dataset.from_list(train_features)
    eval_dataset = Dataset.from_list(eval_features)

    model_kwargs: Dict[str, Any] = {
        "trust_remote_code": True,
    }
    if torch.cuda.is_available():
        model_kwargs["device_map"] = "auto"
    if args.load_in_4bit:
        model_kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=_default_torch_dtype(torch),
        )
    else:
        model_kwargs["torch_dtype"] = _default_torch_dtype(torch)

    model = AutoModelForCausalLM.from_pretrained(args.model, **model_kwargs)
    if args.load_in_4bit:
        model = prepare_model_for_kbit_training(model)
    peft_config = LoraConfig(
        task_type="CAUSAL_LM",
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=list(args.target_modules),
    )
    model = get_peft_model(model, peft_config)
    model.config.use_cache = False

    training_kwargs: Dict[str, Any] = {
        "output_dir": str(output_dir),
        "num_train_epochs": args.epochs,
        "learning_rate": args.learning_rate,
        "per_device_train_batch_size": args.batch_size,
        "per_device_eval_batch_size": args.eval_batch_size,
        "gradient_accumulation_steps": args.grad_accum,
        "warmup_ratio": args.warmup_ratio,
        "weight_decay": args.weight_decay,
        "logging_strategy": "steps",
        "logging_steps": 1,
        "save_strategy": "epoch",
        "report_to": [],
        "bf16": bool(torch.cuda.is_available() and torch.cuda.is_bf16_supported()),
        "fp16": bool(torch.cuda.is_available() and not torch.cuda.is_bf16_supported()),
        "remove_unused_columns": False,
        "save_only_model": True,
        "save_total_limit": 1,
        "seed": args.seed,
    }
    training_signature = inspect.signature(TrainingArguments.__init__)
    strategy_key = "eval_strategy" if "eval_strategy" in training_signature.parameters else "evaluation_strategy"
    training_kwargs[strategy_key] = "epoch"
    training_args = TrainingArguments(**training_kwargs)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=_SupervisedDataCollator(tokenizer=tokenizer, torch=torch),
    )
    train_result = trainer.train()
    trainer.save_model(str(output_dir))
    if args.save_tokenizer:
        tokenizer.save_pretrained(str(output_dir))
    for checkpoint_dir in output_dir.glob("checkpoint-*"):
        if checkpoint_dir.is_dir():
            shutil.rmtree(checkpoint_dir)

    train_metrics = dict(train_result.metrics)
    report = build_run_report(
        base_model=args.model,
        train_examples_path=train_examples_path,
        train_dataset_path=train_jsonl,
        export_report_path=train_export_report_path,
        output_dir=output_dir,
        training_config={
            "epochs": args.epochs,
            "learning_rate": args.learning_rate,
            "batch_size": args.batch_size,
            "eval_batch_size": args.eval_batch_size,
            "grad_accum": args.grad_accum,
            "max_seq_len": args.max_seq_len,
            "warmup_ratio": args.warmup_ratio,
            "weight_decay": args.weight_decay,
            "seed": args.seed,
            "load_in_4bit": bool(args.load_in_4bit),
            "save_tokenizer": bool(args.save_tokenizer),
            "target_modules": list(args.target_modules),
        },
        train_metrics=train_metrics,
        eval_report_path=eval_report_path,
    )
    report.update(
        {
            "report_path": str(report_path),
            "eval_jsonl": str(eval_jsonl),
            "eval_predictions_out_path": str(eval_predictions_path),
            "eval_rows_out_path": str(eval_rows_path),
            "train_row_count": len(train_rows),
            "eval_row_count": len(eval_rows),
        }
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if not args.skip_post_train_eval:
        local_eval.main(
            [
                "--model",
                args.model,
                "--adapter-path",
                str(output_dir),
                "--examples",
                str(examples_path),
                "--predictions-out",
                str(eval_predictions_path),
                "--rows-out",
                str(eval_rows_path),
                "--report",
                str(eval_report_path),
                "--max-new-tokens",
                "128",
                *(["--load-in-4bit"] if args.load_in_4bit else []),
            ]
        )

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
