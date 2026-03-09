import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "filter_actual_game_command_examples.py"


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FILTER = _load_module("filter_actual_game_command_examples", MODULE_PATH)


def _example(
    *,
    summary_sha256: str,
    tick: int,
    state_version: int,
    round_num: int,
    player_tower_count: int,
    command_type: str,
    payload: dict | None,
    source_paths: list[str],
    summary_towers: list[dict] | None = None,
    safe_anchors: list[dict] | None = None,
) -> dict:
    if command_type == "noop":
        target = {
            "kind": "noop",
            "reason": "waiting_for_resources",
        }
    else:
        target = {
            "kind": "command",
            "commandType": command_type,
            "payload": payload or {},
        }
    return {
        "bridge_input": {"version": "td.multiplayer.llm-bridge.input.v1"},
        "summary": {
            "schemaVersion": "td.actual_game.command_summary.v1",
            "tick": tick,
            "stateVersion": state_version,
            "round": round_num,
            "playerTowerCount": player_tower_count,
            "status": "spawning",
            "allowedCommands": ["place_tower", "upgrade_tower", "trigger_next_round", "sell_tower"],
            "towers": list(summary_towers or []),
            "safePlacementAnchors": list(safe_anchors or []),
        },
        "target": target,
        "metadata": {
            "summary_sha256": summary_sha256,
            "target_sha256": f"target-{summary_sha256}",
            "source_instances": [
                {
                    "source_index": index,
                    "source_path": source_path,
                    "command_type": command_type,
                    "decision_kind": "command",
                }
                for index, source_path in enumerate(source_paths)
            ],
        },
    }


class FilterActualGameCommandExamplesTest(unittest.TestCase):
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

    def _write_examples_jsonl(self, root: Path, name: str, examples: list[dict]) -> Path:
        path = root / f"{name}.jsonl"
        path.write_text(
            "\n".join(json.dumps(example, sort_keys=True) for example in examples) + "\n",
            encoding="utf-8",
        )
        return path

    def test_filters_post_placement_examples_by_source_and_command_type(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_path = self._write_examples(
                root,
                "examples",
                [
                    _example(
                        summary_sha256="keep-upgrade",
                        tick=30,
                        state_version=2,
                        round_num=1,
                        player_tower_count=1,
                        command_type="upgrade_tower",
                        payload={"towerId": 1, "path": "top"},
                        source_paths=["artifacts/x582/x558.teacher.json"],
                    ),
                    _example(
                        summary_sha256="skip-place",
                        tick=45,
                        state_version=3,
                        round_num=1,
                        player_tower_count=1,
                        command_type="place_tower",
                        payload={"type": "dart", "x": 336.0, "y": 152.0},
                        source_paths=["artifacts/x582/x558.teacher.json"],
                    ),
                    _example(
                        summary_sha256="skip-base",
                        tick=60,
                        state_version=4,
                        round_num=1,
                        player_tower_count=1,
                        command_type="upgrade_tower",
                        payload={"towerId": 1, "path": "top"},
                        source_paths=["artifacts/x523/base.json"],
                    ),
                    _example(
                        summary_sha256="skip-opening",
                        tick=0,
                        state_version=0,
                        round_num=1,
                        player_tower_count=0,
                        command_type="place_tower",
                        payload={"type": "dart", "x": 336.0, "y": 152.0},
                        source_paths=["artifacts/x582/x558.teacher.json"],
                    ),
                ],
            )

            schema_version, examples, report = FILTER.filter_examples(
                input_paths=[input_path],
                allowed_command_types=["upgrade_tower", "trigger_next_round"],
                min_player_tower_count=1,
                source_contains=["x582/"],
            )

        self.assertEqual(schema_version, "td.actual_game.command_examples.v1")
        self.assertEqual(len(examples), 1)
        self.assertEqual(examples[0]["metadata"]["summary_sha256"], "keep-upgrade")
        self.assertEqual(report["output_example_count"], 1)
        self.assertEqual(report["skip_reasons"]["command_type_mismatch"], 2)
        self.assertEqual(report["skip_reasons"]["source_filter_mismatch"], 1)

    def test_accepts_jsonl_and_collapses_duplicate_summaries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            shared = _example(
                summary_sha256="dup-1",
                tick=15,
                state_version=1,
                round_num=1,
                player_tower_count=1,
                command_type="upgrade_tower",
                payload={"towerId": 1, "path": "top"},
                source_paths=["artifacts/x582/x557.teacher.json"],
            )
            input_path = self._write_examples_jsonl(root, "examples", [shared, shared])

            _schema_version, examples, report = FILTER.filter_examples(
                input_paths=[input_path],
                allowed_command_types=["upgrade_tower"],
                min_player_tower_count=1,
            )

        self.assertEqual(len(examples), 1)
        self.assertEqual(report["duplicates_collapsed"], 1)

    def test_rejects_conflicting_targets_for_same_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            conflict_a = _example(
                summary_sha256="dup-1",
                tick=15,
                state_version=1,
                round_num=1,
                player_tower_count=1,
                command_type="upgrade_tower",
                payload={"towerId": 1, "path": "top"},
                source_paths=["artifacts/x582/x557.teacher.json"],
            )
            conflict_b = _example(
                summary_sha256="dup-1",
                tick=15,
                state_version=1,
                round_num=1,
                player_tower_count=1,
                command_type="trigger_next_round",
                payload={},
                source_paths=["artifacts/x582/x558.teacher.json"],
            )
            input_path = self._write_examples(root, "examples", [conflict_a, conflict_b])

            with self.assertRaisesRegex(ValueError, "conflicting targets"):
                FILTER.filter_examples(input_paths=[input_path])

    def test_filters_place_targets_by_safe_anchor_and_occupancy(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_path = self._write_examples(
                root,
                "examples",
                [
                    _example(
                        summary_sha256="keep-safe-open",
                        tick=30,
                        state_version=2,
                        round_num=1,
                        player_tower_count=1,
                        command_type="place_tower",
                        payload={"type": "dart", "x": 432.0, "y": 152.0},
                        source_paths=["artifacts/x614/x613.teacher.json"],
                        summary_towers=[{"id": 1, "x": 336.0, "y": 152.0}],
                        safe_anchors=[{"x": 336.0, "y": 152.0}, {"x": 432.0, "y": 152.0}],
                    ),
                    _example(
                        summary_sha256="skip-occupied",
                        tick=45,
                        state_version=3,
                        round_num=1,
                        player_tower_count=1,
                        command_type="place_tower",
                        payload={"type": "dart", "x": 336.0, "y": 152.0},
                        source_paths=["artifacts/x614/x613.teacher.json"],
                        summary_towers=[{"id": 1, "x": 336.0, "y": 152.0}],
                        safe_anchors=[{"x": 336.0, "y": 152.0}, {"x": 432.0, "y": 152.0}],
                    ),
                    _example(
                        summary_sha256="skip-off-anchor",
                        tick=60,
                        state_version=4,
                        round_num=1,
                        player_tower_count=1,
                        command_type="place_tower",
                        payload={"type": "dart", "x": 120.0, "y": 120.0},
                        source_paths=["artifacts/x614/x613.teacher.json"],
                        summary_towers=[{"id": 1, "x": 336.0, "y": 152.0}],
                        safe_anchors=[{"x": 336.0, "y": 152.0}, {"x": 432.0, "y": 152.0}],
                    ),
                    _example(
                        summary_sha256="keep-upgrade",
                        tick=75,
                        state_version=5,
                        round_num=1,
                        player_tower_count=1,
                        command_type="upgrade_tower",
                        payload={"towerId": 1, "path": "top"},
                        source_paths=["artifacts/x614/x613.teacher.json"],
                        summary_towers=[{"id": 1, "x": 336.0, "y": 152.0}],
                        safe_anchors=[{"x": 336.0, "y": 152.0}, {"x": 432.0, "y": 152.0}],
                    ),
                ],
            )

            _schema_version, examples, report = FILTER.filter_examples(
                input_paths=[input_path],
                require_place_target_in_safe_anchors=True,
                reject_occupied_place_target=True,
            )

        self.assertEqual(
            [example["metadata"]["summary_sha256"] for example in examples],
            ["keep-safe-open", "keep-upgrade"],
        )
        self.assertEqual(report["skip_reasons"]["place_target_not_in_safe_anchors"], 1)
        self.assertEqual(report["skip_reasons"]["place_target_occupied"], 1)

    def test_rejects_place_targets_without_numeric_coordinates_when_geometry_filters_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_path = self._write_examples(
                root,
                "examples",
                [
                    _example(
                        summary_sha256="skip-missing-xy",
                        tick=30,
                        state_version=2,
                        round_num=1,
                        player_tower_count=1,
                        command_type="place_tower",
                        payload={"type": "dart"},
                        source_paths=["artifacts/x614/x613.teacher.json"],
                        summary_towers=[{"id": 1, "x": 336.0, "y": 152.0}],
                        safe_anchors=[{"x": 336.0, "y": 152.0}, {"x": 432.0, "y": 152.0}],
                    ),
                ],
            )

            _schema_version, examples, report = FILTER.filter_examples(
                input_paths=[input_path],
                require_place_target_in_safe_anchors=True,
                reject_occupied_place_target=True,
            )

        self.assertEqual(examples, [])
        self.assertEqual(report["skip_reasons"]["place_target_invalid"], 1)


if __name__ == "__main__":
    unittest.main()
