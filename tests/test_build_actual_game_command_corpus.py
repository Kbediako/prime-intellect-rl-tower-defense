import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest


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


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from prime_td_env import actual_game_env as actual_env


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build_actual_game_command_corpus.py"
spec = importlib.util.spec_from_file_location("build_actual_game_command_corpus", MODULE_PATH)
builder = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(builder)


def _row(
    *,
    index: int,
    tick: int,
    state_version: int,
    digest: str,
    decision: dict,
    last_command_results: list | None = None,
    state_towers: list | None = None,
    poll_result: dict | None = None,
    poll_command_results: list | None = None,
    enqueue_result: dict | None = None,
) -> dict:
    command_results = list(poll_command_results or [])
    if poll_command_results is None and poll_result is not None and decision.get("kind") == "command":
        payload = decision.get("payload") or {}
        command_results.append(
            {
                "command": {
                    "type": decision["commandType"],
                    "playerId": "bot-bridge",
                    "payload": payload,
                },
                "result": poll_result,
            }
        )
    return {
        "index": index,
        "input": {
            "version": actual_env.BRIDGE_INPUT_VERSION,
            "tick": tick,
            "stateVersion": state_version,
            "stateDigest": digest,
            "economy": {
                "players": {
                    "bot-bridge": {"cash": 250},
                }
            },
            "lobby": {"lobbyId": "fixture"},
            "playerId": "bot-bridge",
            "allowedCommands": ["place_tower", "upgrade_tower", "sell_tower", "trigger_next_round"],
            "lastCommandResults": last_command_results or [],
            "deadlineAt": 1738800000000 + tick,
            "budgetMs": 1200,
            "state": {
                "round": 2,
                "status": "intermission",
                "lives": 100,
                "width": 960,
                "height": 540,
                "towers": state_towers or [],
                "enemies": [],
            },
        },
        "decision": decision,
        "enqueueResult": enqueue_result if enqueue_result is not None else {"accepted": True},
        "stepResult": {"success": True, "tick": tick + 1, "stateVersion": state_version + 1},
        "poll": {"commandResults": command_results},
    }


class BuildActualGameCommandCorpusTest(unittest.TestCase):
    def _write_rows(self, root: Path, name: str, rows: list[dict]) -> Path:
        path = root / name / "bridge-decisions.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
        return path

    def test_build_examples_strips_provenance_and_deduplicates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            decision = {
                "kind": "command",
                "commandType": "upgrade_tower",
                "payload": {"towerId": 7, "path": "top"},
                "provenance": {"modelId": "m1", "requestId": "r1"},
            }
            base_bridge_history = [
                {
                    "id": 1,
                    "command": {
                        "type": "place_tower",
                        "playerId": "bot-bridge",
                        "payload": {"type": "dart", "x": 336, "y": 64},
                    },
                    "result": {"success": True, "towerId": 7},
                }
            ]
            path_a = self._write_rows(
                root,
                "a",
                [
                    _row(
                        index=0,
                        tick=12,
                        state_version=18,
                        digest="abc123",
                        decision=decision,
                        last_command_results=base_bridge_history,
                        poll_result={"success": True, "towerId": 7, "path": "top"},
                    )
                ],
            )
            path_b = self._write_rows(
                root,
                "b",
                [
                    _row(
                        index=0,
                        tick=12,
                        state_version=18,
                        digest="abc123",
                        decision={
                            "kind": "command",
                            "commandType": "upgrade_tower",
                            "payload": {"towerId": 7, "path": "top"},
                            "provenance": {"modelId": "m2", "requestId": "r2"},
                        },
                        last_command_results=base_bridge_history,
                        poll_result={"success": True, "towerId": 7, "path": "top"},
                    )
                ],
            )

            examples, report = builder.build_examples([path_a, path_b])

        self.assertEqual(len(examples), 1)
        self.assertEqual(report["duplicates_removed"], 1)
        self.assertEqual(report["unique_example_count"], 1)
        self.assertEqual(
            examples[0]["target"],
            {
                "kind": "command",
                "commandType": "upgrade_tower",
                "payload": {"towerId": 7, "path": "top"},
            },
        )
        self.assertEqual(len(examples[0]["metadata"]["source_instances"]), 2)

    def test_build_examples_detects_conflicting_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            rows = [
                _row(
                    index=0,
                    tick=12,
                    state_version=18,
                    digest="abc123",
                    decision={
                        "kind": "command",
                        "commandType": "place_tower",
                        "payload": {"type": "dart", "x": 336, "y": 64},
                    },
                    poll_result={"success": True, "towerId": 7},
                )
            ]
            path_a = self._write_rows(root, "a", rows)
            path_b = self._write_rows(
                root,
                "b",
                [
                    _row(
                        index=0,
                        tick=12,
                        state_version=18,
                        digest="abc123",
                        decision={
                            "kind": "command",
                            "commandType": "place_tower",
                            "payload": {"type": "sniper", "x": 336, "y": 64},
                        },
                        poll_result={"success": True, "towerId": 8},
                    )
                ],
            )
            with self.assertRaises(ValueError):
                builder.build_examples([path_a, path_b])

    def test_require_poll_success_filters_failed_realized_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            path = self._write_rows(
                root,
                "a",
                [
                    _row(
                        index=0,
                        tick=12,
                        state_version=18,
                        digest="abc123",
                        decision={
                            "kind": "command",
                            "commandType": "trigger_next_round",
                            "payload": {},
                        },
                        poll_result={"success": False, "reason": "Not in intermission"},
                    ),
                    _row(
                        index=1,
                        tick=15,
                        state_version=19,
                        digest="abc124",
                        decision={
                            "kind": "noop",
                            "reason": "waiting_for_resources",
                        },
                    ),
                ],
            )

            examples, report = builder.build_examples([path], require_poll_success=True)

        self.assertEqual(len(examples), 1)
        self.assertEqual(report["rowsFilteredPollFailure"], 1)
        self.assertEqual(examples[0]["target"]["kind"], "noop")

    def test_require_poll_success_filters_unrealized_commands_without_matched_poll_success(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            path = self._write_rows(
                root,
                "a",
                [
                    _row(
                        index=0,
                        tick=12,
                        state_version=18,
                        digest="abc123",
                        decision={
                            "kind": "command",
                            "commandType": "place_tower",
                            "payload": {"type": "dart", "x": 336, "y": 64},
                        },
                        enqueue_result={
                            "success": True,
                            "skipped": True,
                            "reason": "duplicate_invalid_place_tower_payload",
                        },
                        poll_command_results=[],
                    ),
                    _row(
                        index=1,
                        tick=13,
                        state_version=19,
                        digest="abc124",
                        decision={
                            "kind": "command",
                            "commandType": "trigger_next_round",
                            "payload": {},
                        },
                        enqueue_result={"success": True},
                        poll_command_results=[
                            {
                                "command": {
                                    "type": "place_tower",
                                    "playerId": "bot-bridge",
                                    "payload": {"type": "dart", "x": 480, "y": 96},
                                },
                                "result": {"success": True, "towerId": 9},
                            }
                        ],
                    ),
                    _row(
                        index=2,
                        tick=14,
                        state_version=20,
                        digest="abc125",
                        decision={
                            "kind": "command",
                            "commandType": "trigger_next_round",
                            "payload": {},
                        },
                        poll_result={"success": True},
                    ),
                ],
            )

            examples, report = builder.build_examples([path], require_poll_success=True)

        self.assertEqual(len(examples), 1)
        self.assertEqual(report["rowsFilteredPollFailure"], 2)
        self.assertEqual(examples[0]["target"]["kind"], "command")
        self.assertEqual(examples[0]["target"]["commandType"], "trigger_next_round")

    def test_same_summary_with_different_budget_is_collapsed_when_target_matches(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = _row(
                index=0,
                tick=12,
                state_version=18,
                digest="abc123",
                decision={
                    "kind": "command",
                    "commandType": "place_tower",
                    "payload": {"type": "dart", "x": 336, "y": 64},
                },
                poll_result={"success": True, "towerId": 7},
            )
            second = _row(
                index=1,
                tick=12,
                state_version=18,
                digest="abc123",
                decision={
                    "kind": "command",
                    "commandType": "place_tower",
                    "payload": {"type": "dart", "x": 336, "y": 64},
                },
                poll_result={"success": True, "towerId": 7},
            )
            second["input"]["budgetMs"] = 15000
            path = self._write_rows(root, "a", [first, second])

            examples, report = builder.build_examples([path])

        self.assertEqual(len(examples), 1)
        self.assertEqual(report["duplicates_removed"], 1)
        self.assertEqual(report["conflictCount"], 0)

    def test_noop_reason_conflicts_are_collapsed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            path_a = self._write_rows(
                root,
                "a",
                [
                    _row(
                        index=0,
                        tick=12,
                        state_version=18,
                        digest="abc123",
                        decision={
                            "kind": "noop",
                            "reason": "waiting_for_spawning",
                        },
                    )
                ],
            )
            path_b = self._write_rows(
                root,
                "b",
                [
                    _row(
                        index=0,
                        tick=12,
                        state_version=18,
                        digest="abc123",
                        decision={
                            "kind": "noop",
                            "reason": "waiting_for_resources",
                        },
                    )
                ],
            )

            examples, report = builder.build_examples([path_a, path_b])

        self.assertEqual(len(examples), 1)
        self.assertEqual(report["duplicates_removed"], 1)
        self.assertEqual(report["noopReasonConflictsCollapsed"], 1)
        self.assertEqual(examples[0]["target"]["kind"], "noop")

    def test_examples_persist_summary_for_multi_step_tower_ownership(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            path = self._write_rows(
                root,
                "a",
                [
                    _row(
                        index=0,
                        tick=12,
                        state_version=18,
                        digest="abc123",
                        decision={
                            "kind": "command",
                            "commandType": "place_tower",
                            "payload": {"type": "dart", "x": 336, "y": 64},
                        },
                        poll_result={"success": True, "towerId": 7},
                    ),
                    _row(
                        index=1,
                        tick=13,
                        state_version=19,
                        digest="abc124",
                        decision={
                            "kind": "command",
                            "commandType": "upgrade_tower",
                            "payload": {"towerId": 7, "path": "top"},
                        },
                        state_towers=[
                            {
                                "id": 7,
                                "type": "dart",
                                "position": {"x": 336, "y": 64},
                                "invested": 100,
                                "upgrades": {"top": 0, "middle": 0, "bottom": 0},
                            }
                        ],
                        poll_result={"success": True, "towerId": 7, "path": "top"},
                    ),
                ],
            )

            examples, _report = builder.build_examples([path])

        self.assertEqual(len(examples), 2)
        self.assertEqual(examples[1]["summary"]["playerTowerIds"], [7])
        normalized = actual_env._normalize_example(examples[1])
        self.assertEqual(normalized["summary"]["playerTowerIds"], [7])
        self.assertEqual(normalized["summary"]["playerTowerCount"], 1)

    def test_examples_persist_tower_ownership_across_relabel_rows_without_poll_matches(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            rows = [
                {
                    "index": 0,
                    "input": {
                        "version": actual_env.BRIDGE_INPUT_VERSION,
                        "tick": 30,
                        "stateVersion": 2,
                        "stateDigest": "abc-relabeled-0",
                        "economy": {"players": {"bot-bridge": {"cash": 225}}},
                        "lobby": {"lobbyId": "fixture"},
                        "playerId": "bot-bridge",
                        "allowedCommands": ["place_tower", "upgrade_tower", "sell_tower", "trigger_next_round"],
                        "lastCommandResults": [
                            {
                                "id": 1,
                                "command": {
                                    "type": "place_tower",
                                    "playerId": "bot-bridge",
                                    "payload": {"type": "dart", "x": 336, "y": 152},
                                },
                                "result": {"success": True, "towerId": 7},
                            }
                        ],
                        "deadlineAt": 1738800000030,
                        "budgetMs": 1200,
                        "state": {
                            "round": 1,
                            "status": "active",
                            "lives": 100,
                            "width": 960,
                            "height": 540,
                            "towers": [
                                {
                                    "id": 7,
                                    "type": "dart",
                                    "position": {"x": 336, "y": 152},
                                    "invested": 100,
                                    "upgrades": {"top": 0, "middle": 0, "bottom": 0},
                                }
                            ],
                            "enemies": [],
                        },
                    },
                    "decision": {
                        "kind": "command",
                        "commandType": "upgrade_tower",
                        "payload": {"towerId": 7, "path": "top"},
                    },
                },
                {
                    "index": 1,
                    "input": {
                        "version": actual_env.BRIDGE_INPUT_VERSION,
                        "tick": 45,
                        "stateVersion": 3,
                        "stateDigest": "abc-relabeled-1",
                        "economy": {"players": {"bot-bridge": {"cash": 225}}},
                        "lobby": {"lobbyId": "fixture"},
                        "playerId": "bot-bridge",
                        "allowedCommands": ["place_tower", "upgrade_tower", "sell_tower", "trigger_next_round"],
                        "lastCommandResults": [],
                        "deadlineAt": 1738800000045,
                        "budgetMs": 1200,
                        "state": {
                            "round": 1,
                            "status": "active",
                            "lives": 100,
                            "width": 960,
                            "height": 540,
                            "towers": [
                                {
                                    "id": 7,
                                    "type": "dart",
                                    "position": {"x": 336, "y": 152},
                                    "invested": 100,
                                    "upgrades": {"top": 0, "middle": 0, "bottom": 0},
                                }
                            ],
                            "enemies": [],
                        },
                    },
                    "decision": {
                        "kind": "command",
                        "commandType": "upgrade_tower",
                        "payload": {"towerId": 7, "path": "top"},
                    },
                },
            ]
            path = self._write_rows(root, "a", rows)

            examples, _report = builder.build_examples([path])

        self.assertEqual(len(examples), 2)
        self.assertEqual(examples[0]["summary"]["playerTowerIds"], [7])
        self.assertEqual(examples[1]["summary"]["playerTowerIds"], [7])
        self.assertEqual(examples[1]["summary"]["playerTowerCount"], 1)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
