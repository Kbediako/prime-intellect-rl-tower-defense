import json
from pathlib import Path
import sys
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

        class Environment:  # pragma: no cover - stub
            pass

        vf.Environment = Environment
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

try:
    from prime_td_env import actual_game_env as actual_env
except ImportError:  # pragma: no cover - fallback for src-layout imports
    from src.prime_td_env import actual_game_env as actual_env


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "actual_game_command_examples.json"


class ActualGameEnvTest(unittest.TestCase):
    def _load_fixture_example(self) -> dict:
        payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        return payload["examples"][0]

    def test_create_command_summary_from_bridge_input_matches_fixture_expectations(self) -> None:
        example = self._load_fixture_example()
        summary = actual_env.create_command_summary_from_bridge_input(example["bridge_input"])
        economy = example["bridge_input"].get("economy", {})
        team_cash = ((economy.get("team_totals") or {}).get("current_cash"))
        if team_cash is None:
            team_cash = example["bridge_input"].get("state", {}).get("cash")
        if team_cash is None:
            team_cash = summary["playerCash"]

        self.assertEqual(summary["schemaVersion"], actual_env.COMMAND_SUMMARY_SCHEMA_VERSION)
        self.assertEqual(summary["playerId"], "bot-bridge")
        self.assertEqual(summary["allowedCommands"], ["place_tower", "upgrade_tower", "trigger_next_round"])
        self.assertEqual(summary["playerTowerIds"], [7])
        self.assertEqual(summary["playerTowerCount"], 1)
        self.assertEqual(summary["enemyCount"], 0)
        self.assertTrue(summary["safePlacementAnchors"])
        self.assertEqual(summary["commandResultsTail"][0]["type"], "place_tower")
        self.assertEqual(summary["teamCash"], float(team_cash))

    def test_create_command_summary_exposes_team_cash_when_wallet_cash_is_low(self) -> None:
        example = self._load_fixture_example()
        bridge_input = json.loads(json.dumps(example["bridge_input"]))
        bridge_input["economy"]["players"]["bot-bridge"]["cash"] = 26
        bridge_input["economy"]["team_totals"] = {"current_cash": 351}
        bridge_input["state"]["cash"] = 351

        summary = actual_env.create_command_summary_from_bridge_input(bridge_input)

        self.assertEqual(summary["playerCash"], 26.0)
        self.assertEqual(summary["teamCash"], 351.0)

    def test_create_command_summary_falls_back_to_visible_towers_when_ownership_history_is_truncated(self) -> None:
        example = self._load_fixture_example()
        bridge_input = json.loads(json.dumps(example["bridge_input"]))
        bridge_input["lastCommandResults"] = []

        summary = actual_env.create_command_summary_from_bridge_input(bridge_input)

        self.assertEqual(summary["playerTowerIds"], [7])
        self.assertEqual(summary["playerTowerCount"], 1)

    def test_create_command_summary_excludes_occupied_safe_anchor(self) -> None:
        example = self._load_fixture_example()
        summary = actual_env.create_command_summary_from_bridge_input(example["bridge_input"])

        anchors = {(anchor["x"], anchor["y"]) for anchor in summary["safePlacementAnchors"]}
        self.assertNotIn((336, 64), anchors)
        self.assertIn((432, 64), anchors)
        self.assertIn((900, 500), anchors)

    def test_validate_command_decision_enforces_payload_rules(self) -> None:
        allowed = ["upgrade_tower", "trigger_next_round"]
        valid = actual_env.normalize_command_decision(
            {
                "kind": "command",
                "commandType": "upgrade_tower",
                "payload": {"towerId": 7, "path": "top"},
            },
            allowed,
        )
        self.assertEqual(valid["payload"]["path"], "top")

        with self.assertRaises(ValueError):
            actual_env.normalize_command_decision(
                {
                    "kind": "command",
                    "commandType": "upgrade_tower",
                    "payload": {"towerId": 7, "path": "left"},
                },
                allowed,
            )

        with self.assertRaises(ValueError):
            actual_env.normalize_command_decision(
                {
                    "kind": "command",
                    "commandType": "sell_tower",
                    "payload": {"towerId": 7},
                },
                allowed,
            )

        with self.assertRaises(ValueError):
            actual_env.normalize_command_decision(
                {
                    "kind": "noop",
                    "reason": "waiting_for_resources",
                    "commandType": "sell_tower",
                },
                allowed,
            )

        with self.assertRaises(ValueError):
            actual_env.normalize_command_decision(
                {
                    "kind": "command",
                    "commandType": "place_tower",
                    "payload": {"type": "dart", "x": float("nan"), "y": 64},
                },
                ["place_tower"],
            )

        with self.assertRaises(ValueError):
            actual_env.normalize_command_decision(
                {
                    "kind": "command",
                    "commandType": "upgrade_tower",
                    "payload": {"towerId": 7, "path": "top", "unexpected": True},
                },
                ["upgrade_tower"],
            )

    def test_build_dataset_supports_examples_path_with_bridge_input(self) -> None:
        dataset = actual_env._build_actual_game_command_dataset(
            {
                "wrapper": "actual_game_command",
                "dataset": {
                    "examples_path": str(FIXTURE_PATH),
                },
            },
            num_examples=1,
            seed_start=0,
        )

        self.assertEqual(len(dataset["prompt"]), 1)
        self.assertEqual(dataset["task"], ["train"])
        prompt = dataset["prompt"][0]
        self.assertEqual(prompt[0]["content"], actual_env.ACTUAL_GAME_COMMAND_SYSTEM_PROMPT)
        self.assertIn("State:\n", prompt[1]["content"])
        self.assertIn(actual_env.COMMAND_SUMMARY_SCHEMA_VERSION, prompt[1]["content"])
        self.assertEqual(
            json.loads(dataset["answer"][0]),
            {
                "kind": "command",
                "commandType": "upgrade_tower",
                "payload": {"towerId": 7, "path": "top"},
            },
        )

    def test_format_and_env_rewards_score_exact_replay_match(self) -> None:
        example = self._load_fixture_example()
        summary = actual_env.create_command_summary_from_bridge_input(example["bridge_input"])
        target = actual_env.normalize_command_decision(example["target"], summary["allowedCommands"])
        completion = [{"role": "assistant", "content": json.dumps(target)}]
        info = {"summary": summary, "target": target}

        self.assertEqual(
            actual_env._actual_game_command_format_reward([], completion, "", {}, info=info),
            1.0,
        )
        self.assertEqual(
            actual_env._actual_game_command_env_reward([], completion, "", {}, info=info),
            1.0,
        )

        non_exact = [{"role": "assistant", "content": json.dumps({"kind": "noop", "reason": "waiting_for_resources"})}]
        self.assertEqual(
            actual_env._actual_game_command_env_reward([], non_exact, "", {}, info=info),
            0.0,
        )

        non_strict = [
            {
                "role": "assistant",
                "content": f"prefix {json.dumps(target)}",
            }
        ]
        self.assertEqual(
            actual_env._actual_game_command_format_reward([], non_strict, "", {}, info=info),
            -1.0,
        )
        self.assertEqual(
            actual_env._actual_game_command_env_reward([], non_strict, "", {}, info=info),
            -1.0,
        )

        extra_key = [
            {
                "role": "assistant",
                "content": json.dumps(
                    {
                        "kind": "command",
                        "commandType": "upgrade_tower",
                        "payload": {"towerId": 7, "path": "top", "unexpected": True},
                    }
                ),
            }
        ]
        self.assertEqual(
            actual_env._actual_game_command_format_reward([], extra_key, "", {}, info=info),
            -1.0,
        )
        self.assertEqual(
            actual_env._actual_game_command_env_reward([], extra_key, "", {}, info=info),
            -1.0,
        )

    def test_noop_env_reward_accepts_reason_variation(self) -> None:
        summary = {
            "schemaVersion": actual_env.COMMAND_SUMMARY_SCHEMA_VERSION,
            "tick": 255,
            "stateVersion": 17,
            "playerId": "bot-bridge",
            "allowedCommands": ["place_tower", "sell_tower", "upgrade_tower", "trigger_next_round"],
            "round": 1,
            "status": "spawning",
            "lives": 100,
            "playerCash": 325,
            "teamCash": 325,
            "map": {"width": 960, "height": 540},
            "safePlacementAnchors": [{"x": 336, "y": 64}],
            "playerTowerIds": [],
            "playerTowerCount": 0,
            "towers": [],
            "enemyCount": 15,
            "commandResultsTail": [],
        }
        target = {
            "kind": "noop",
            "reason": "Waiting for spawning to complete before placing towers",
        }
        info = {"summary": summary, "target": target}
        completion = [{"role": "assistant", "content": json.dumps({"kind": "noop", "reason": "wait for spawn"})}]

        self.assertEqual(
            actual_env._actual_game_command_format_reward([], completion, "", {}, info=info),
            1.0,
        )
        self.assertEqual(
            actual_env._actual_game_command_env_reward([], completion, "", {}, info=info),
            1.0,
        )

    def test_known_tower_owners_json_keys_are_preserved(self) -> None:
        example = self._load_fixture_example()
        bridge_input = json.loads(json.dumps(example["bridge_input"]))
        bridge_input["lastCommandResults"] = []
        normalized = actual_env._normalize_example(
            {
                "bridge_input": bridge_input,
                "known_tower_owners": {"7": "bot-bridge"},
                "target": {
                    "kind": "command",
                    "commandType": "upgrade_tower",
                    "payload": {"towerId": 7, "path": "top"},
                },
            }
        )
        self.assertEqual(normalized["summary"]["playerTowerIds"], [7])
        self.assertEqual(normalized["summary"]["playerTowerCount"], 1)

    def test_tower_defence_alias_dispatches_actual_game_wrapper(self) -> None:
        import tower_defence

        env = tower_defence.load_environment(
            config={
                "wrapper": "actual_game_command",
                "dataset": {
                    "examples_path": str(FIXTURE_PATH),
                },
            },
            num_examples=1,
            seed_start=0,
        )

        prompt = env.kwargs["dataset"]["prompt"][0]
        self.assertEqual(prompt[0]["content"], actual_env.ACTUAL_GAME_COMMAND_SYSTEM_PROMPT)

    def test_num_examples_minus_one_expands_to_all_examples(self) -> None:
        example = self._load_fixture_example()
        dataset = actual_env._build_actual_game_command_dataset(
            {
                "wrapper": "actual_game_command",
                "dataset": {
                    "examples_inline": [
                        example,
                        {
                            "summary": {
                                "schemaVersion": actual_env.COMMAND_SUMMARY_SCHEMA_VERSION,
                                "tick": 2,
                                "stateVersion": 2,
                                "playerId": "bot-bridge",
                                "allowedCommands": ["trigger_next_round"],
                                "round": 2,
                                "status": "intermission",
                                "lives": 100,
                                "playerCash": 50,
                                "teamCash": 50,
                                "map": {"width": 960, "height": 540},
                                "safePlacementAnchors": [{"x": 336, "y": 64}],
                                "playerTowerIds": [],
                                "playerTowerCount": 0,
                                "towers": [],
                                "enemyCount": 0,
                                "commandResultsTail": [],
                            },
                            "target": {
                                "kind": "command",
                                "commandType": "trigger_next_round",
                                "payload": {},
                            },
                        },
                    ],
                },
            },
            num_examples=-1,
            seed_start=0,
        )
        self.assertEqual(len(dataset["prompt"]), 2)
        self.assertEqual(len(dataset["answer"]), 2)

    def test_resolve_examples_supports_module_relative_examples_path(self) -> None:
        resolved = actual_env._resolve_examples(
            {
                "examples_path": "data/actual_game_command/test_examples.json",
            }
        )

        self.assertEqual(len(resolved), 1)
        self.assertEqual(resolved[0]["metadata"]["summary_sha256"], "fixture-test-summary")
        self.assertEqual(resolved[0]["summary"]["teamCash"], 50)

    def test_validate_command_summary_rejects_incomplete_nested_entries(self) -> None:
        summary = {
            "schemaVersion": actual_env.COMMAND_SUMMARY_SCHEMA_VERSION,
            "tick": 1,
            "stateVersion": 1,
            "playerId": "bot-bridge",
            "allowedCommands": ["place_tower"],
            "round": 1,
            "status": "intermission",
            "lives": 100,
            "playerCash": 250,
            "teamCash": 250,
            "map": {"width": 960, "height": 540},
            "safePlacementAnchors": [{"x": 336, "y": 64}],
            "playerTowerIds": [],
            "playerTowerCount": 0,
            "towers": [
                {
                    "id": None,
                    "type": "",
                    "x": 10,
                    "y": 20,
                    "invested": 100,
                    "upgrades": {"top": 0},
                }
            ],
            "enemyCount": 0,
            "commandResultsTail": [
                {
                    "id": None,
                    "type": "",
                    "playerId": "",
                    "success": True,
                    "reason": "",
                }
            ],
        }
        with self.assertRaises(ValueError):
            actual_env.validate_command_summary(summary)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
