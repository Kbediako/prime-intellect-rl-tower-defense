import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "build_actual_game_command_custom_replay.py"


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CUSTOM_REPLAY = _load_module("build_actual_game_command_custom_replay", MODULE_PATH)


def _example(*, summary_sha256: str, command_type: str, payload: dict, request_id: str, source_index: int) -> dict:
    return {
        "bridge_input": {"version": "td.multiplayer.llm-bridge.input.v1"},
        "summary": {
            "schemaVersion": "td.actual_game.command_summary.v1",
            "tick": 100,
            "stateVersion": 20,
            "round": 1,
            "status": "intermission",
            "playerTowerCount": 3,
            "playerCash": 31.0,
            "teamCash": 356.0,
            "allowedCommands": ["place_tower", "upgrade_tower", "sell_tower", "trigger_next_round"],
        },
        "target": {
            "kind": "command",
            "commandType": command_type,
            "payload": payload,
        },
        "metadata": {
            "summary_sha256": summary_sha256,
            "target_sha256": f"target-{summary_sha256}",
            "source_instances": [
                {
                    "request_id": request_id,
                    "source_index": source_index,
                    "source_path": f"artifacts/source/{request_id}.json",
                }
            ],
        },
    }


class BuildActualGameCommandCustomReplayTest(unittest.TestCase):
    def _write_examples(self, root: Path, name: str, examples: list[dict]) -> Path:
        path = root / f"{name}.json"
        path.write_text(
            json.dumps(
                {
                    "schemaVersion": "td.actual_game.command_examples.v1",
                    "examples": examples,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return path

    def test_build_custom_replay_appends_explicit_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base_path = self._write_examples(
                root,
                "base",
                [
                    _example(
                        summary_sha256="a",
                        command_type="trigger_next_round",
                        payload={},
                        request_id="req-a",
                        source_index=1,
                    ),
                    _example(
                        summary_sha256="b",
                        command_type="upgrade_tower",
                        payload={"towerId": 1, "path": "top"},
                        request_id="req-b",
                        source_index=2,
                    ),
                ],
            )
            augment_one = self._write_examples(
                root,
                "augment_one",
                [
                    _example(
                        summary_sha256="b",
                        command_type="upgrade_tower",
                        payload={"towerId": 1, "path": "top"},
                        request_id="req-b",
                        source_index=2,
                    ),
                ],
            )
            augment_two = self._write_examples(
                root,
                "augment_two",
                [
                    _example(
                        summary_sha256="c",
                        command_type="upgrade_tower",
                        payload={"towerId": 3, "path": "top"},
                        request_id="req-c",
                        source_index=3,
                    ),
                ],
            )

            schema_version, final_examples, report = CUSTOM_REPLAY.build_custom_replay(
                base_examples_path=base_path,
                augment_examples_paths=[augment_one, augment_two],
                extra_repeats_per_selected_example=2,
            )

        self.assertEqual(schema_version, "td.actual_game.command_examples.v1")
        self.assertEqual(len(final_examples), 6)
        summary_counts = {}
        for example in final_examples:
            summary_sha256 = example["metadata"]["summary_sha256"]
            summary_counts[summary_sha256] = summary_counts.get(summary_sha256, 0) + 1
        self.assertEqual(summary_counts, {"a": 1, "b": 3, "c": 2})
        self.assertEqual(report["selected_replay_count"], 2)
        self.assertEqual(report["extra_repeats_per_selected_example"], 2)
        self.assertEqual(report["replayed_summary_counts"]["b"], 3)
        self.assertEqual(report["replayed_summary_counts"]["c"], 2)

    def test_build_custom_replay_rejects_conflicting_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base_path = self._write_examples(root, "base", [])
            augment_one = self._write_examples(
                root,
                "augment_one",
                [
                    _example(
                        summary_sha256="same",
                        command_type="upgrade_tower",
                        payload={"towerId": 1, "path": "top"},
                        request_id="req-one",
                        source_index=1,
                    ),
                ],
            )
            augment_two = self._write_examples(
                root,
                "augment_two",
                [
                    _example(
                        summary_sha256="same",
                        command_type="trigger_next_round",
                        payload={},
                        request_id="req-two",
                        source_index=2,
                    ),
                ],
            )

            with self.assertRaisesRegex(ValueError, "conflicting targets"):
                CUSTOM_REPLAY.build_custom_replay(
                    base_examples_path=base_path,
                    augment_examples_paths=[augment_one, augment_two],
                    extra_repeats_per_selected_example=1,
                )


if __name__ == "__main__":
    unittest.main()
