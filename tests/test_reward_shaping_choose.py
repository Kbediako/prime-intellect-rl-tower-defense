import asyncio
import json
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
            pass

        vf.SingleTurnEnv = SingleTurnEnv

        class MultiTurnEnv:  # pragma: no cover - stub
            def __init__(self, *args, **_kwargs):
                pass

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
                pass

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
    from prime_td_env import environment as env
except ImportError:  # pragma: no cover - fallback for src-layout imports
    from src.prime_td_env import environment as env


def _lookahead_delta(config: dict, obs: dict, rounds: int) -> float:
    baseline = env.TowerDefenseEnv(config)
    baseline.load_from_observation(obs)
    after = env.TowerDefenseEnv(config)
    after.load_from_observation(obs)

    def _simulate_rounds(simulator: env.TowerDefenseEnv, count: int) -> float:
        total = 0.0
        for _ in range(count):
            _o, reward, done, _info = simulator.step({"type": "start_round"})
            total += float(reward)
            if done:
                break
        return total

    _o, _reward, done, _info = after.step({"type": "start_round"})
    baseline_future = _simulate_rounds(baseline, rounds)
    after_future = 0.0 if done else _simulate_rounds(after, rounds)
    return after_future - baseline_future


class RewardShapingChooseTest(unittest.TestCase):
    def test_choose_start_round_matches_direct_reward(self) -> None:
        config = env.deep_merge(
            env.DEFAULT_CONFIG,
            {
                "reward_shaping": {
                    "enable_lookahead": True,
                    "lookahead_rounds": 1,
                    "lookahead_weight": 1.0,
                },
                "rules": {
                    "auto_advance_round": False,
                    "require_tower_before_start": False,
                },
            },
        )
        env._ACTIVE_CONFIG = config

        simulator = env.TowerDefenseEnv(config)
        obs = simulator.reset(seed=123)
        candidates = obs.get("action_candidates", [])
        index = next(
            (
                i
                for i, candidate in enumerate(candidates)
                if isinstance(candidate, dict) and candidate.get("type") == "start_round"
            ),
            None,
        )
        self.assertIsNotNone(index, "start_round should be present in action_candidates")

        choose_action = {"type": "choose", "index": index}
        direct_action = {"type": "start_round"}

        choose_completion = [{"role": "assistant", "content": json.dumps(choose_action)}]
        direct_completion = [{"role": "assistant", "content": json.dumps(direct_action)}]

        reward_choose = env._reward_from_action([], choose_completion, "", None, info={"obs": obs})
        reward_direct = env._reward_from_action([], direct_completion, "", None, info={"obs": obs})

        self.assertAlmostEqual(reward_choose, reward_direct, places=9)

        delta = _lookahead_delta(config, obs, rounds=1)
        self.assertGreater(abs(delta), 1e-6)

    def test_choose_missing_candidates_is_invalid(self) -> None:
        config = env.deep_merge(
            env.DEFAULT_CONFIG,
            {
                "rules": {
                    "auto_advance_round": False,
                    "require_tower_before_start": False,
                },
            },
        )

        simulator = env.TowerDefenseEnv(config)
        obs = simulator.reset(seed=321)

        variants = {
            "missing": {k: v for k, v in obs.items() if k != "action_candidates"},
            "empty": {**obs, "action_candidates": []},
        }

        for name, variant in variants.items():
            with self.subTest(name=name):
                replay = env.TowerDefenseEnv(config)
                replay.load_from_observation(variant)
                _obs, _reward, _done, info = replay.step({"type": "choose", "index": 0})
                self.assertTrue(info.get("invalid_action"))
                self.assertEqual(info.get("invalid_reason"), "missing_action_candidates")

    def test_build_uses_map_slots_when_candidates_filtered(self) -> None:
        config = env.deep_merge(
            env.DEFAULT_CONFIG,
            {
                "rules": {
                    "auto_advance_round": False,
                    "require_tower_before_start": False,
                },
                "observation": {
                    "max_build_slots": 5,
                },
            },
        )

        simulator = env.TowerDefenseEnv(config)
        obs = simulator.reset(seed=456)
        map_slots = obs.get("map", {}).get("build_slots", [])
        self.assertTrue(map_slots, "expected build_slots in observation")

        target_slot = map_slots[0]
        action_candidates = obs.get("action_candidates", [])
        filtered_candidates = []
        for cand in action_candidates:
            if not isinstance(cand, dict):
                continue
            if cand.get("type") == "build" and [cand.get("x"), cand.get("y")] == target_slot:
                continue
            filtered_candidates.append(cand)

        obs_variant = dict(obs)
        obs_variant["action_candidates"] = filtered_candidates

        tower_type = min(
            env.DEFAULT_CONFIG["towers"].items(),
            key=lambda item: item[1].get("cost", 0),
        )[0]
        build_action = {"type": "build", "tower_type": tower_type, "x": target_slot[0], "y": target_slot[1]}

        replay = env.TowerDefenseEnv(config)
        replay.load_from_observation(obs_variant)
        _obs, _reward, _done, info = replay.step(build_action)
        self.assertFalse(info.get("invalid_action"))

    def test_candidate_rewards_parity_with_require_choose(self) -> None:
        base_config = env.deep_merge(
            env.DEFAULT_CONFIG,
            {
                "rules": {
                    "auto_advance_round": False,
                    "require_tower_before_start": False,
                    "require_choose": False,
                },
            },
        )

        simulator = env.TowerDefenseEnv(base_config)
        obs = simulator.reset(seed=111)
        rewards_no_choose = env._candidate_rewards(obs, base_config)

        choose_config = env.deep_merge(
            base_config,
            {
                "rules": {
                    "require_choose": True,
                },
            },
        )
        rewards_choose = env._candidate_rewards(obs, choose_config)

        self.assertTrue(rewards_no_choose, "expected action_candidates to score")
        self.assertEqual(len(rewards_no_choose), len(rewards_choose))
        for (candidate_a, reward_a), (candidate_b, reward_b) in zip(rewards_no_choose, rewards_choose):
            self.assertEqual(candidate_a, candidate_b)
            self.assertAlmostEqual(reward_a, reward_b, places=9)

    def test_build_dataset_rollout_advances_with_require_choose(self) -> None:
        config = env.deep_merge(
            env.DEFAULT_CONFIG,
            {
                "rules": {
                    "auto_advance_round": False,
                    "require_tower_before_start": False,
                    "require_choose": True,
                },
                "dataset": {
                    "rollout_steps": 1,
                    "policy": "advance",
                    "num_seeds": 1,
                    "snapshots": {
                        "mode": "rounds",
                        "rounds": [2],
                    },
                    "require_best_types": ["build", "upgrade"],
                },
            },
        )

        original_step = env.TowerDefenseEnv.step
        seen_internal = {"value": False}

        def wrapped_step(self, action, internal=False):
            if self.config.get("rules", {}).get("require_choose"):
                seen_internal["value"] = seen_internal["value"] or internal
            return original_step(self, action, internal=internal)

        env.TowerDefenseEnv.step = wrapped_step
        try:
            dataset = env._build_dataset(config, num_examples=1, seed_start=0)
        finally:
            env.TowerDefenseEnv.step = original_step

        self.assertTrue(seen_internal["value"])
        infos = dataset["info"]
        self.assertTrue(any(info.get("snapshot", {}).get("round") == 2 for info in infos))

    def test_macro_round_plan_budget_respects_soft_cap(self) -> None:
        config = env.deep_merge(
            env.DEFAULT_CONFIG,
            {
                "wrapper": "macro_round",
                "economy": {
                    "starting_cash": 300,
                    "starting_lives": 100,
                    "end_round_income": 100,
                },
                "rules": {
                    "auto_advance_round": True,
                    "prep_actions_per_round": 2,
                    "prep_actions_round_scale": 0.0,
                    "prep_actions_max": 2,
                    "start_round_max_prep_remaining": 1,
                    "require_tower_before_start": True,
                    "mask_sell": True,
                    "soft_tower_cap": {
                        "per_type": {"threshold": 1, "multiplier": 1.0},
                    },
                },
                "observation": {
                    "max_build_slots": 2,
                    "max_action_candidates": 10,
                },
                "dataset": {
                    "policy": "random",
                    "rollout_steps": 0,
                    "num_seeds": 1,
                },
            },
        )

        macro_env = env.TowerDefenseMacroRoundEnv(config, num_examples=1, seed_start=0)
        state = {"info": {"seed": 7}}
        asyncio.run(macro_env.setup_state(state))
        simulator = state["simulator"]
        obs = simulator._observation()
        candidates = env._filter_macro_round_candidates(obs)
        build_indices = [
            i
            for i, candidate in enumerate(candidates)
            if isinstance(candidate, dict) and candidate.get("type") == "build"
        ]
        self.assertGreaterEqual(len(build_indices), 2)

        plan = {
            "type": "plan",
            "actions": [
                {"type": "choose", "index": build_indices[0]},
                {"type": "choose", "index": build_indices[1]},
            ],
        }
        messages = [{"role": "assistant", "content": json.dumps(plan)}]
        asyncio.run(macro_env.env_response(messages, state))

        invalids = state.get("invalid_actions", [])
        self.assertIn("plan_insufficient_cash", invalids)

    def test_macro_round_invalid_choose_advances_single_round_without_jump(self) -> None:
        config = env.deep_merge(
            env.DEFAULT_CONFIG,
            {
                "wrapper": "macro_round",
                "economy": {
                    "starting_cash": 1000,
                    "starting_lives": 100,
                    "end_round_income": 100,
                },
                "rules": {
                    "auto_advance_round": True,
                    "prep_actions_per_round": 2,
                    "prep_actions_round_scale": 0.0,
                    "prep_actions_max": 2,
                    "start_round_max_prep_remaining": 1,
                    "require_tower_before_start": True,
                    "mask_sell": True,
                },
                "observation": {
                    "max_build_slots": 3,
                    "max_action_candidates": 10,
                },
                "dataset": {
                    "policy": "random",
                    "rollout_steps": 0,
                    "num_seeds": 1,
                },
            },
        )

        macro_env = env.TowerDefenseMacroRoundEnv(config, num_examples=1, seed_start=0)
        state = {"info": {"seed": 0}}
        asyncio.run(macro_env.setup_state(state))

        simulator = state["simulator"]
        obs = simulator._observation()
        candidates = env._filter_macro_round_candidates(obs)
        build_index = next(
            i
            for i, candidate in enumerate(candidates)
            if isinstance(candidate, dict) and candidate.get("type") == "build"
        )

        valid_plan = {"type": "plan", "actions": [{"type": "choose", "index": build_index}]}
        valid_messages = [{"role": "assistant", "content": json.dumps(valid_plan)}]
        asyncio.run(macro_env.env_response(valid_messages, state))
        round_before_invalid = state["simulator"].state.round

        invalid_plan = {"type": "plan", "actions": [{"type": "choose", "index": 999}]}
        invalid_messages = [{"role": "assistant", "content": json.dumps(invalid_plan)}]
        asyncio.run(macro_env.env_response(invalid_messages, state))

        meta = state.get("macro_round_last_meta", {})
        self.assertLess(state["turn_rewards"][-1], 0.0)
        self.assertEqual(state["simulator"].state.round, round_before_invalid + 1)
        self.assertEqual(meta.get("delta_round"), 1)
        self.assertNotIn("macro_round_round_jump", state.get("invalid_actions", []))
        self.assertIn("choose_out_of_range", state.get("invalid_actions", []))
        self.assertFalse(state.get("episode_done"))

    def test_macro_round_partial_invalid_plan_keeps_single_round_progress(self) -> None:
        config = env.deep_merge(
            env.DEFAULT_CONFIG,
            {
                "wrapper": "macro_round",
                "economy": {
                    "starting_cash": 1000,
                    "starting_lives": 100,
                    "end_round_income": 100,
                },
                "rules": {
                    "auto_advance_round": True,
                    "prep_actions_per_round": 2,
                    "prep_actions_round_scale": 0.0,
                    "prep_actions_max": 2,
                    "start_round_max_prep_remaining": 1,
                    "require_tower_before_start": True,
                    "mask_sell": True,
                },
                "observation": {
                    "max_build_slots": 3,
                    "max_action_candidates": 10,
                },
                "dataset": {
                    "policy": "random",
                    "rollout_steps": 0,
                    "num_seeds": 1,
                },
            },
        )

        macro_env = env.TowerDefenseMacroRoundEnv(config, num_examples=1, seed_start=0)
        state = {"info": {"seed": 3}}
        asyncio.run(macro_env.setup_state(state))
        simulator = state["simulator"]
        obs = simulator._observation()
        candidates = env._filter_macro_round_candidates(obs)
        build_index = next(
            i
            for i, candidate in enumerate(candidates)
            if isinstance(candidate, dict) and candidate.get("type") == "build"
        )

        start_round = simulator.state.round
        plan = {
            "type": "plan",
            "actions": [
                {"type": "choose", "index": build_index},
                {"type": "choose", "index": 999},
            ],
        }
        messages = [{"role": "assistant", "content": json.dumps(plan)}]
        asyncio.run(macro_env.env_response(messages, state))

        meta = state.get("macro_round_last_meta", {})
        self.assertEqual(state["simulator"].state.round - start_round, 1)
        self.assertEqual(meta.get("delta_round"), 1)
        self.assertIn("choose_out_of_range", state.get("invalid_actions", []))
        self.assertNotIn("macro_round_round_jump", state.get("invalid_actions", []))
        self.assertFalse(state.get("episode_done"))

    def test_macro_round_over_budget_keeps_single_round_delta(self) -> None:
        config = env.deep_merge(
            env.DEFAULT_CONFIG,
            {
                "wrapper": "macro_round",
                "economy": {
                    "starting_cash": 1000,
                    "starting_lives": 100,
                    "end_round_income": 100,
                },
                "rules": {
                    "auto_advance_round": True,
                    "prep_actions_per_round": 2,
                    "prep_actions_round_scale": 0.0,
                    "prep_actions_max": 2,
                    "require_tower_before_start": True,
                    "mask_sell": True,
                },
                "observation": {
                    "max_build_slots": 3,
                    "max_action_candidates": 10,
                },
                "dataset": {
                    "policy": "random",
                    "rollout_steps": 0,
                    "num_seeds": 1,
                },
            },
        )

        macro_env = env.TowerDefenseMacroRoundEnv(config, num_examples=1, seed_start=0)
        state = {"info": {"seed": 1}}
        asyncio.run(macro_env.setup_state(state))
        simulator = state["simulator"]
        obs = simulator._observation()
        candidates = env._filter_macro_round_candidates(obs)
        build_indices = [
            i
            for i, candidate in enumerate(candidates)
            if isinstance(candidate, dict) and candidate.get("type") == "build"
        ]
        self.assertGreaterEqual(len(build_indices), 2)

        start_round = simulator.state.round
        over_budget_plan = {
            "type": "plan",
            "actions": [
                {"type": "choose", "index": build_indices[0]},
                {"type": "choose", "index": build_indices[1]},
                {"type": "choose", "index": build_indices[0]},
            ],
        }
        messages = [{"role": "assistant", "content": json.dumps(over_budget_plan)}]
        asyncio.run(macro_env.env_response(messages, state))

        end_round = state["simulator"].state.round
        self.assertEqual(end_round - start_round, 1)
        self.assertIn("plan_exceeds_budget", state.get("invalid_actions", []))
        self.assertFalse(state.get("episode_done"))

    def test_load_from_observation_clamps_upgrade_tiers(self) -> None:
        config = env.deep_merge(env.DEFAULT_CONFIG, {})
        simulator = env.TowerDefenseEnv(config)
        obs = simulator.reset(seed=11)

        build_slots = obs.get("map", {}).get("build_slots", [])
        self.assertTrue(build_slots)
        x, y = build_slots[0]
        cash_before = int(obs.get("cash", 0))

        obs_variant = dict(obs)
        obs_variant["towers"] = [
            {
                "id": 1,
                "type": "dart",
                "x": x,
                "y": y,
                "upgrades": {"a": 999},
                "targeting": "first",
            }
        ]

        simulator.load_from_observation(obs_variant)
        _obs, _reward, _done, info = simulator.step({"type": "sell", "tower_id": 1}, internal=True)
        self.assertFalse(info.get("invalid_action"))

        dart_cfg = config["towers"]["dart"]
        expected_total_cost = int(dart_cfg["cost"]) + sum(int(tier["cost"]) for tier in dart_cfg["upgrade_paths"]["a"])
        expected_refund = int(expected_total_cost * float(config["economy"]["sell_refund_ratio"]))
        self.assertEqual(simulator.state.cash, cash_before + expected_refund)

    def test_observation_exposes_round_phase_bucket(self) -> None:
        config = env.deep_merge(
            env.DEFAULT_CONFIG,
            {
                "observation": {
                    "candidate_balance": {
                        "early_max_round": 5,
                        "mid_max_round": 8,
                    }
                }
            },
        )

        simulator = env.TowerDefenseEnv(config)
        obs = simulator.reset(seed=19)
        self.assertEqual(obs.get("phase"), "build")
        self.assertEqual(obs.get("round_phase"), "early")

        simulator.state.round = 6
        obs_mid = simulator._observation(cache_action_candidates=False)
        self.assertEqual(obs_mid.get("round_phase"), "mid")

        simulator.state.round = 9
        obs_late = simulator._observation(cache_action_candidates=False)
        self.assertEqual(obs_late.get("round_phase"), "late")
