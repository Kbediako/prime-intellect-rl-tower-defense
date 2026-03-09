import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "blend_actual_game_command_examples.py"


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BLEND = _load_module("blend_actual_game_command_examples", MODULE_PATH)


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
    metadata = {
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
        },
        "target": target,
        "metadata": metadata,
    }


class BlendActualGameCommandExamplesTest(unittest.TestCase):
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

    def test_blend_keeps_base_and_caps_filtered_augment_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base_examples = [
                _example(
                    summary_sha256="base-1",
                    tick=15,
                    state_version=1,
                    round_num=1,
                    player_tower_count=0,
                    command_type="place_tower",
                    payload={"type": "dart", "x": 336.0, "y": 152.0},
                    source_paths=["artifacts/x563/base.json"],
                ),
                _example(
                    summary_sha256="base-2",
                    tick=30,
                    state_version=2,
                    round_num=1,
                    player_tower_count=0,
                    command_type="place_tower",
                    payload={"type": "dart", "x": 600.0, "y": 180.0},
                    source_paths=["artifacts/x563/base.json"],
                ),
                _example(
                    summary_sha256="base-3",
                    tick=45,
                    state_version=3,
                    round_num=1,
                    player_tower_count=0,
                    command_type="noop",
                    payload={},
                    source_paths=["artifacts/x563/base.json"],
                ),
            ]
            augment_examples = [
                _example(
                    summary_sha256="aug-keep-a1",
                    tick=45,
                    state_version=3,
                    round_num=1,
                    player_tower_count=0,
                    command_type="place_tower",
                    payload={"type": "dart", "x": 336.0, "y": 152.0},
                    source_paths=["artifacts/x572/x557.teacher.json"],
                ),
                _example(
                    summary_sha256="aug-cap-a2",
                    tick=60,
                    state_version=4,
                    round_num=1,
                    player_tower_count=0,
                    command_type="place_tower",
                    payload={"type": "dart", "x": 336.0, "y": 152.0},
                    source_paths=["artifacts/x572/x557.teacher.json"],
                ),
                _example(
                    summary_sha256="aug-keep-b1",
                    tick=75,
                    state_version=5,
                    round_num=1,
                    player_tower_count=0,
                    command_type="place_tower",
                    payload={"type": "dart", "x": 600.0, "y": 180.0},
                    source_paths=["artifacts/x572/x558.teacher.json"],
                ),
                _example(
                    summary_sha256="aug-reject-bad-payload",
                    tick=90,
                    state_version=6,
                    round_num=1,
                    player_tower_count=0,
                    command_type="place_tower",
                    payload={"type": "dart", "x": 900.0, "y": 300.0},
                    source_paths=["artifacts/x572/x558.teacher.json"],
                ),
                _example(
                    summary_sha256="aug-reject-x562",
                    tick=105,
                    state_version=7,
                    round_num=1,
                    player_tower_count=0,
                    command_type="place_tower",
                    payload={"type": "dart", "x": 600.0, "y": 180.0},
                    source_paths=["artifacts/x572/x562.teacher.json"],
                ),
            ]
            base_path = self._write_examples(root, "base", base_examples)
            augment_path = self._write_examples(root, "augment", augment_examples)

            schema_version, blended, report = BLEND.blend_examples(
                base_paths=[base_path],
                augment_paths=[augment_path],
                augment_command_type="place_tower",
                augment_round=1,
                augment_player_tower_count=0,
                augment_source_contains=["x557.teacher", "x558.teacher"],
                augment_exclude_source_contains=["x562.teacher"],
                payload_whitelist_paths=[base_path],
                augment_limit_per_source=1,
                augment_limit_total=3,
            )

        self.assertEqual(schema_version, "td.actual_game.command_examples.v1")
        self.assertEqual(len(blended), 5)
        kept_ids = {_example["metadata"]["summary_sha256"] for _example in blended}
        self.assertEqual(kept_ids, {"base-1", "base-2", "base-3", "aug-keep-a1", "aug-keep-b1"})
        self.assertEqual(report["augment_kept_count"], 2)
        self.assertEqual(
            report["augment_kept_by_source"],
            {
                "artifacts/x572/x557.teacher.json": 1,
                "artifacts/x572/x558.teacher.json": 1,
            },
        )
        self.assertEqual(report["augment_skip_reasons"]["payload_not_grounded"], 1)
        self.assertEqual(report["augment_skip_reasons"]["per_source_cap"], 1)
        self.assertEqual(report["augment_skip_reasons"]["source_filter_mismatch"], 1)

    def test_blend_skips_duplicate_summary_with_same_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            shared = _example(
                summary_sha256="dup-1",
                tick=15,
                state_version=1,
                round_num=1,
                player_tower_count=0,
                command_type="place_tower",
                payload={"type": "dart", "x": 336.0, "y": 152.0},
                source_paths=["artifacts/x563/base.json"],
            )
            base_path = self._write_examples(root, "base", [shared])
            augment_path = self._write_examples(
                root,
                "augment",
                [
                    _example(
                        summary_sha256="dup-1",
                        tick=15,
                        state_version=1,
                        round_num=1,
                        player_tower_count=0,
                        command_type="place_tower",
                        payload={"type": "dart", "x": 336.0, "y": 152.0},
                        source_paths=["artifacts/x572/x557.teacher.json"],
                    )
                ],
            )

            _schema_version, blended, report = BLEND.blend_examples(
                base_paths=[base_path],
                augment_paths=[augment_path],
            )

        self.assertEqual(len(blended), 1)
        self.assertEqual(report["augment_kept_count"], 0)
        self.assertEqual(report["augment_skip_reasons"]["duplicate_summary"], 1)

    def test_blend_can_replace_conflicting_summary_targets_when_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base_path = self._write_examples(
                root,
                "base",
                [
                    _example(
                        summary_sha256="shared-1",
                        tick=30,
                        state_version=2,
                        round_num=1,
                        player_tower_count=1,
                        command_type="place_tower",
                        payload={"type": "dart", "x": 336.0, "y": 152.0},
                        source_paths=["artifacts/x577/base.json"],
                    )
                ],
            )
            augment_path = self._write_examples(
                root,
                "augment",
                [
                    _example(
                        summary_sha256="shared-1",
                        tick=30,
                        state_version=2,
                        round_num=1,
                        player_tower_count=1,
                        command_type="upgrade_tower",
                        payload={"towerId": 1, "path": "top"},
                        source_paths=["artifacts/x582/x557.teacher.json"],
                    )
                ],
            )

            _schema_version, blended, report = BLEND.blend_examples(
                base_paths=[base_path],
                augment_paths=[augment_path],
                replace_conflicting_summaries=True,
            )

        self.assertEqual(len(blended), 1)
        self.assertEqual(report["augment_kept_count"], 1)
        self.assertEqual(report["augment_replaced_conflicting_summaries"], 1)
        self.assertEqual(blended[0]["target"]["commandType"], "upgrade_tower")
        self.assertEqual(
            blended[0]["metadata"]["blend_attributed_source"],
            "artifacts/x582/x557.teacher.json",
        )

    def test_blend_accepts_jsonl_and_balances_multi_source_caps(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base_path = self._write_examples_jsonl(
                root,
                "base",
                [
                    _example(
                        summary_sha256="base-1",
                        tick=15,
                        state_version=1,
                        round_num=1,
                        player_tower_count=0,
                        command_type="place_tower",
                        payload={"type": "dart", "x": 336.0, "y": 152.0},
                        source_paths=["artifacts/x563/base.json"],
                    )
                ],
            )
            augment_path = self._write_examples_jsonl(
                root,
                "augment",
                [
                    _example(
                        summary_sha256="aug-1",
                        tick=45,
                        state_version=3,
                        round_num=1,
                        player_tower_count=0,
                        command_type="place_tower",
                        payload={"type": "dart", "x": 336.0, "y": 152.0},
                        source_paths=["artifacts/x572/x557.teacher.json", "artifacts/x572/x558.teacher.json"],
                    ),
                    _example(
                        summary_sha256="aug-2",
                        tick=60,
                        state_version=4,
                        round_num=1,
                        player_tower_count=0,
                        command_type="place_tower",
                        payload={"type": "dart", "x": 336.0, "y": 152.0},
                        source_paths=["artifacts/x572/x557.teacher.json", "artifacts/x572/x558.teacher.json"],
                    ),
                ],
            )

            _schema_version, blended, report = BLEND.blend_examples(
                base_paths=[base_path],
                augment_paths=[augment_path],
                augment_command_type="place_tower",
                augment_source_contains=["x557.teacher", "x558.teacher"],
                payload_whitelist_paths=[base_path],
                augment_limit_per_source=1,
                augment_limit_total=2,
            )

        self.assertEqual(len(blended), 3)
        self.assertEqual(
            report["augment_kept_by_source"],
            {
                "artifacts/x572/x557.teacher.json": 1,
                "artifacts/x572/x558.teacher.json": 1,
            },
        )


if __name__ == "__main__":
    unittest.main()
