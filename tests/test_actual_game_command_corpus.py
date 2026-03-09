import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "actual_game_command_examples.json"
REPO_ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = REPO_ROOT / "scripts" / "build_actual_game_command_corpus.py"
EVAL_PATH = REPO_ROOT / "scripts" / "eval_actual_game_command_corpus.py"
EXPORT_PATH = REPO_ROOT / "scripts" / "export_actual_game_command_sft_dataset.py"
SCORE_PATH = REPO_ROOT / "scripts" / "score_actual_game_command_predictions.py"
RUN_EVAL_PATH = REPO_ROOT / "scripts" / "run_actual_game_command_eval.py"
LOCAL_EVAL_PATH = REPO_ROOT / "scripts" / "run_actual_game_command_local_eval.py"
TRAIN_SFT_PATH = REPO_ROOT / "scripts" / "train_actual_game_command_sft.py"


def _ensure_test_deps() -> None:
    if "verifiers" not in sys.modules:
        vf = types.SimpleNamespace()
        vf.Messages = list
        vf.State = dict
        vf.Info = dict

        class SingleTurnEnv:  # pragma: no cover - stub
            def __init__(self, *args, **kwargs) -> None:
                self.args = args
                self.kwargs = kwargs

        vf.SingleTurnEnv = SingleTurnEnv

        class MultiTurnEnv:  # pragma: no cover - stub
            def __init__(self, *args, **kwargs) -> None:
                self.args = args
                self.kwargs = kwargs

            async def setup_state(self, state):
                return state

            def add_trajectory_step(self, state, step):
                return step

        vf.MultiTurnEnv = MultiTurnEnv

        def stop(func=None, **_kwargs):  # pragma: no cover - stub
            if func is None:
                def _decorator(inner):
                    return inner
                return _decorator
            return func

        vf.stop = stop

        class Rubric:  # pragma: no cover - stub
            def __init__(self, *args, **kwargs) -> None:
                self.args = args
                self.kwargs = kwargs

        vf.Rubric = Rubric
        vf.Environment = object
        sys.modules["verifiers"] = vf

    if "datasets" not in sys.modules:
        ds = types.SimpleNamespace()

        class Dataset:  # pragma: no cover - stub
            @staticmethod
            def from_dict(payload):
                return payload

        ds.Dataset = Dataset
        sys.modules["datasets"] = ds


_ensure_test_deps()


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILDER = _load_module("build_actual_game_command_corpus", BUILDER_PATH)
EVAL = _load_module("eval_actual_game_command_corpus", EVAL_PATH)
EXPORT = _load_module("export_actual_game_command_sft_dataset", EXPORT_PATH)
SCORE = _load_module("score_actual_game_command_predictions", SCORE_PATH)
RUN_EVAL = _load_module("run_actual_game_command_eval", RUN_EVAL_PATH)
LOCAL_EVAL = _load_module("eval_actual_game_command_local_model", LOCAL_EVAL_PATH)
TRAIN_SFT = _load_module("train_actual_game_command_sft", TRAIN_SFT_PATH)


class ActualGameCommandCorpusEvalTest(unittest.TestCase):
    def _load_fixture_example(self) -> dict:
        payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        return payload["examples"][0]

    def _make_bridge_entry(self, index: int = 0) -> dict:
        example = self._load_fixture_example()
        bridge_input = copy.deepcopy(example["bridge_input"])
        bridge_input["deadlineAt"] = bridge_input["deadlineAt"] + (index * 100)
        return {
            "index": index,
            "input": bridge_input,
            "decision": {
                **example["target"],
                "provenance": {
                    "modelId": f"fixture-model-{index}",
                    "providerId": "fixture-provider",
                    "requestId": f"req-{index}",
                },
            },
            "enqueueResult": {"success": True, "skipped": False},
            "stepResult": {
                "success": True,
                "tick": bridge_input["tick"] + 1,
                "stateVersion": bridge_input["stateVersion"] + 1,
            },
            "poll": {},
        }

    def test_eval_examples_file_replays_targets_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            source_a = tmpdir_path / "bridge-decisions-a.json"
            source_b = tmpdir_path / "bridge-decisions-b.json"
            examples_path = tmpdir_path / "actual_game_examples.json"
            source_a.write_text(json.dumps([self._make_bridge_entry(index=0)]), encoding="utf-8")
            source_b.write_text(json.dumps([self._make_bridge_entry(index=1)]), encoding="utf-8")

            examples, build_report = BUILDER.build_examples([source_a, source_b])
            BUILDER.write_examples(examples_path, examples)
            eval_report = EVAL.evaluate_examples_file(examples_path)

        self.assertEqual(build_report["unique_example_count"], 1)
        self.assertEqual(eval_report["example_count"], 1)
        self.assertEqual(eval_report["dataset_prompt_count"], 1)
        self.assertEqual(eval_report["replay_format_pass_count"], 1)
        self.assertEqual(eval_report["replay_env_pass_count"], 1)
        self.assertEqual(eval_report["command_type_counts"]["upgrade_tower"], 1)
        self.assertEqual(
            sorted(eval_report["source_path_counts"].keys()),
            [str(source_a), str(source_b)],
        )

    def test_eval_examples_file_accepts_legacy_source_records_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            source_a = tmpdir_path / "bridge-decisions-a.json"
            source_a.write_text(json.dumps([self._make_bridge_entry(index=0)]), encoding="utf-8")

            examples, _build_report = BUILDER.build_examples([source_a])
            legacy_examples = copy.deepcopy(examples)
            metadata = legacy_examples[0]["metadata"]
            metadata["sourceRecords"] = [
                {
                    "index": record["source_index"],
                    "modelId": record.get("model_id"),
                    "path": record["source_path"],
                    "requestId": record.get("request_id"),
                }
                for record in metadata.pop("source_instances")
            ]
            examples_path = tmpdir_path / "legacy_examples.json"
            examples_path.write_text(
                json.dumps({"schemaVersion": "td.actual_game.command_examples.v1", "examples": legacy_examples}),
                encoding="utf-8",
            )

            eval_report = EVAL.evaluate_examples_file(examples_path)

        self.assertEqual(eval_report["example_count"], 1)
        self.assertEqual(eval_report["source_path_counts"], {str(source_a): 1})

    def test_export_examples_file_emits_minimal_sft_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            source_a = tmpdir_path / "bridge-decisions-a.json"
            source_b = tmpdir_path / "bridge-decisions-b.json"
            examples_path = tmpdir_path / "actual_game_examples.json"
            source_a.write_text(json.dumps([self._make_bridge_entry(index=0)]), encoding="utf-8")
            source_b.write_text(json.dumps([self._make_bridge_entry(index=1)]), encoding="utf-8")

            examples, _build_report = BUILDER.build_examples([source_a, source_b])
            BUILDER.write_examples(examples_path, examples)
            rows, export_report = EXPORT.export_examples_file(examples_path)

        self.assertEqual(export_report["row_count"], 1)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["schemaVersion"], "td.actual_game.sft_example.v1")
        self.assertEqual(len(row["messages"]), 3)
        self.assertEqual(row["messages"][0]["role"], "system")
        self.assertEqual(row["messages"][1]["role"], "user")
        self.assertEqual(row["messages"][2]["role"], "assistant")
        self.assertEqual(sorted(row["metadata"]["source_paths"]), [str(source_a), str(source_b)])
        self.assertIn("example_id", row["metadata"])
        self.assertIn("target_sha256", row["metadata"])
        self.assertNotIn("example_index", row["metadata"])
        self.assertNotIn("source_instances", row["metadata"])

    def test_export_defaults_to_packaged_train_split(self) -> None:
        self.assertEqual(
            EXPORT.DEFAULT_EXAMPLES_PATH,
            Path("src/prime_td_env/data/actual_game_command/train_examples.json"),
        )

    def test_score_examples_file_scores_exact_match_predictions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            source_a = tmpdir_path / "bridge-decisions-a.json"
            examples_path = tmpdir_path / "actual_game_examples.json"
            source_a.write_text(json.dumps([self._make_bridge_entry(index=0)]), encoding="utf-8")

            examples, _build_report = BUILDER.build_examples([source_a])
            BUILDER.write_examples(examples_path, examples)
            prediction_texts = [json.dumps(examples[0]["target"], sort_keys=True)]
            score_report, rows = SCORE.score_examples_file(examples_path, prediction_texts=prediction_texts)

        self.assertEqual(score_report["example_count"], 1)
        self.assertEqual(score_report["format_pass_count"], 1)
        self.assertEqual(score_report["env_pass_count"], 1)
        self.assertEqual(score_report["exact_match_by_type"]["upgrade_tower"], 1)
        self.assertEqual(score_report["examples_path"], str(examples_path))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["env_score"], 1.0)

    def test_run_eval_gold_mode_replays_targets_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            source_a = tmpdir_path / "bridge-decisions-a.json"
            examples_path = tmpdir_path / "actual_game_examples.json"
            source_a.write_text(json.dumps([self._make_bridge_entry(index=0)]), encoding="utf-8")

            examples, _build_report = BUILDER.build_examples([source_a])
            BUILDER.write_examples(examples_path, examples)
            report, prediction_rows, score_rows = RUN_EVAL.evaluate_examples(examples, mode="gold", model="")

        self.assertEqual(report["mode"], "gold")
        self.assertEqual(report["example_count"], 1)
        self.assertEqual(report["env_pass_rate"], 1.0)
        self.assertEqual(len(prediction_rows), 1)
        self.assertEqual(len(score_rows), 1)
        self.assertEqual(prediction_rows[0]["completion"], json.dumps(examples[0]["target"], sort_keys=True))

    def test_run_eval_inference_mode_uses_request_fn_output(self) -> None:
        examples = [self._load_fixture_example()]

        def _fake_request(_example: dict, _messages: list[dict[str, str]]) -> dict:
            return {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(examples[0]["target"], sort_keys=True),
                        }
                    }
                ]
            }

        report, prediction_rows, score_rows = RUN_EVAL.evaluate_examples(
            examples,
            mode="inference",
            model="fixture-model",
            prediction_fn=_fake_request,
        )

        self.assertEqual(report["mode"], "inference")
        self.assertEqual(report["model"], "fixture-model")
        self.assertEqual(report["env_pass_count"], 1)
        self.assertEqual(prediction_rows[0]["raw_response"]["choices"][0]["message"]["content"], prediction_rows[0]["completion"])
        self.assertEqual(score_rows[0]["format_score"], 1.0)

    def test_run_eval_resolve_prime_auth_reads_matching_cli_config(self) -> None:
        original_api = os.environ.pop("TEST_PRIME_API_KEY", None)
        original_team = os.environ.pop("TEST_PRIME_TEAM_ID", None)
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = Path(tmpdir) / "config.json"
                config_path.write_text(
                    json.dumps(
                        {
                            "api_key": "cli-token",
                            "team_id": "team-123",
                            "inference_url": RUN_EVAL.DEFAULT_BASE_URL,
                        }
                    ),
                    encoding="utf-8",
                )

                api_key, team_id = RUN_EVAL._resolve_prime_auth(
                    api_key_env="TEST_PRIME_API_KEY",
                    team_id_env="TEST_PRIME_TEAM_ID",
                    base_url=RUN_EVAL.DEFAULT_BASE_URL,
                    path=config_path,
                )
        finally:
            if original_api is not None:
                os.environ["TEST_PRIME_API_KEY"] = original_api
            if original_team is not None:
                os.environ["TEST_PRIME_TEAM_ID"] = original_team

        self.assertEqual((api_key, team_id), ("cli-token", "team-123"))

    def test_run_eval_resolve_prime_auth_prefers_explicit_env(self) -> None:
        original_api = os.environ.get("TEST_PRIME_API_KEY")
        original_team = os.environ.get("TEST_PRIME_TEAM_ID")
        os.environ["TEST_PRIME_API_KEY"] = "env-token"
        os.environ["TEST_PRIME_TEAM_ID"] = "env-team"
        try:
            api_key, team_id = RUN_EVAL._resolve_prime_auth(
                api_key_env="TEST_PRIME_API_KEY",
                team_id_env="TEST_PRIME_TEAM_ID",
                base_url=RUN_EVAL.DEFAULT_BASE_URL,
            )
        finally:
            if original_api is None:
                os.environ.pop("TEST_PRIME_API_KEY", None)
            else:
                os.environ["TEST_PRIME_API_KEY"] = original_api
            if original_team is None:
                os.environ.pop("TEST_PRIME_TEAM_ID", None)
            else:
                os.environ["TEST_PRIME_TEAM_ID"] = original_team

        self.assertEqual((api_key, team_id), ("env-token", "env-team"))

    def test_local_eval_supports_fake_predictor(self) -> None:
        examples = [self._load_fixture_example()]

        def _fake_predictor(_example: dict, _messages: list[dict[str, str]]) -> str:
            return json.dumps(examples[0]["target"], sort_keys=True)

        report, prediction_rows, score_rows = LOCAL_EVAL.evaluate_examples(
            examples,
            model_label="fixture-model",
            predictor=_fake_predictor,
            adapter_path="",
        )

        self.assertEqual(report["mode"], "local_transformers")
        self.assertEqual(report["model"], "fixture-model")
        self.assertEqual(report["env_pass_rate"], 1.0)
        self.assertEqual(len(prediction_rows), 1)
        self.assertEqual(len(score_rows), 1)

    def test_train_build_run_report_records_expected_paths(self) -> None:
        report = TRAIN_SFT.build_run_report(
            base_model="Qwen/Qwen3-4B-Instruct-2507",
            train_examples_path=Path("/tmp/train_examples.json"),
            train_dataset_path=Path("/tmp/train_messages.jsonl"),
            export_report_path=Path("/tmp/export_report.json"),
            output_dir=Path("/tmp/adapter"),
            training_config={"num_train_epochs": 4.0},
            train_metrics={"train_runtime": 12.5},
            eval_report_path=Path("/tmp/eval_report.json"),
        )

        self.assertEqual(report["base_model"], "Qwen/Qwen3-4B-Instruct-2507")
        self.assertEqual(report["train_examples_path"], "/tmp/train_examples.json")
        self.assertEqual(report["train_dataset_path"], "/tmp/train_messages.jsonl")
        self.assertEqual(report["output_dir"], "/tmp/adapter")
        self.assertEqual(report["training_config"]["num_train_epochs"], 4.0)
        self.assertEqual(report["train_metrics"]["train_runtime"], 12.5)
        self.assertEqual(report["eval_report_path"], "/tmp/eval_report.json")

    def test_load_prediction_texts_rejects_duplicate_example_indices(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            predictions_path = tmpdir_path / "predictions.json"
            predictions_path.write_text(
                json.dumps(
                    [
                        {"example_index": 0, "completion": "{\"kind\":\"noop\",\"reason\":\"a\"}"},
                        {"example_index": 0, "completion": "{\"kind\":\"noop\",\"reason\":\"b\"}"},
                    ]
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "duplicate prediction row for example_index 0"):
                SCORE._load_prediction_texts(predictions_path, 1)

    def test_load_prediction_texts_rejects_mixed_indexed_and_ordered_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            predictions_path = tmpdir_path / "predictions.json"
            predictions_path.write_text(
                json.dumps(
                    [
                        {"example_index": 0, "completion": "{\"kind\":\"noop\",\"reason\":\"a\"}"},
                        "{\"kind\":\"noop\",\"reason\":\"b\"}",
                    ]
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError,
                "predictions payload cannot mix ordered rows with example_index rows",
            ):
                SCORE._load_prediction_texts(predictions_path, 1)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
