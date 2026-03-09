import json
import importlib.util
from pathlib import Path
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SPLIT_PATH = REPO_ROOT / "scripts" / "split_actual_game_command_corpus.py"


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SPLIT = _load_module("split_actual_game_command_corpus", SPLIT_PATH)


class SplitActualGameCommandCorpusTest(unittest.TestCase):
    def _example(self, command_type: str, summary_id: str, source_path: str) -> dict:
        return {
            "summary": {"allowedCommands": [command_type], "summaryId": summary_id},
            "target": {"kind": "command", "commandType": command_type, "payload": {}},
            "metadata": {
                "summary_sha256": summary_id,
                "source_instances": [{"source_path": source_path}],
            },
        }

    def test_split_examples_is_deterministic_and_stratified(self) -> None:
        examples = [
            self._example("noop", "b-noop", "b.json"),
            self._example("noop", "a-noop", "a.json"),
            self._example("place_tower", "d-place", "d.json"),
            self._example("place_tower", "c-place", "c.json"),
            self._example("place_tower", "e-place", "e.json"),
        ]

        train_examples, eval_examples, report = SPLIT.split_examples(
            examples,
            eval_fraction=0.4,
            min_eval_per_command_type=1,
        )

        self.assertEqual([example["metadata"]["summary_sha256"] for example in eval_examples], ["a-noop", "c-place"])
        self.assertEqual(
            [example["metadata"]["summary_sha256"] for example in train_examples],
            ["b-noop", "d-place", "e-place"],
        )
        self.assertEqual(report["train_command_type_counts"], {"noop": 1, "place_tower": 2})
        self.assertEqual(report["eval_command_type_counts"], {"noop": 1, "place_tower": 1})
        self.assertEqual(report["split_by_command_type"]["noop"], {"train": 1, "eval": 1})

    def test_split_examples_keeps_singletons_in_train(self) -> None:
        examples = [
            self._example("noop", "only-noop", "noop.json"),
            self._example("place_tower", "only-place", "place.json"),
        ]

        train_examples, eval_examples, report = SPLIT.split_examples(examples)

        self.assertEqual(len(train_examples), 2)
        self.assertEqual(len(eval_examples), 0)
        self.assertEqual(report["eval_command_type_counts"], {})

    def test_write_examples_preserves_schema_version(self) -> None:
        examples = [self._example("noop", "only-noop", "noop.json")]
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "examples.json"
            SPLIT.write_examples(output_path, "td.actual_game.command_examples.v1", examples)
            payload = output_path.read_text(encoding="utf-8")

        self.assertIn("\"schemaVersion\": \"td.actual_game.command_examples.v1\"", payload)
        self.assertIn("\"summary_sha256\": \"only-noop\"", payload)

    def test_split_examples_rejects_conflicting_targets_for_same_summary_id(self) -> None:
        examples = [
            self._example("place_tower", "shared-id", "a.json"),
            {
                **self._example("place_tower", "shared-id", "b.json"),
                "target": {
                    "kind": "command",
                    "commandType": "place_tower",
                    "payload": {"towerType": "cannon"},
                },
            },
        ]

        with self.assertRaisesRegex(ValueError, "conflicting targets"):
            SPLIT.split_examples(examples)

    def test_read_examples_payload_accepts_jsonl(self) -> None:
        examples = [
            self._example("noop", "only-noop", "noop.json"),
            self._example("place_tower", "only-place", "place.json"),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            jsonl_path = Path(tmpdir) / "examples.jsonl"
            jsonl_path.write_text(
                "\n".join(json.dumps(example, sort_keys=True) for example in examples) + "\n",
                encoding="utf-8",
            )

            schema_version, loaded_examples = SPLIT._read_examples_payload(jsonl_path)

        self.assertEqual(schema_version, "td.actual_game.command_examples.v1")
        self.assertEqual(len(loaded_examples), 2)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
