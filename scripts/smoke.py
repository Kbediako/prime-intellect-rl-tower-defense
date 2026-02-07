"""Determinism + action validity smoke checks."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from prime_td_env.environment import load_environment


def run_with_actions(actions: List[Dict[str, Any]], seed: int) -> List[Tuple[Dict[str, Any], float, bool, Dict[str, Any]]]:
    env = load_environment({})
    env.reset(seed=seed)
    trajectory = []
    for action in actions:
        obs, reward, done, info = env.step(action)
        trajectory.append((obs, reward, done, info))
        if done:
            break
    return trajectory


def assert_determinism() -> None:
    env = load_environment({})
    obs = env.reset(seed=123)
    build_slot = obs["map"]["build_slots"][0]
    actions = [
        {"type": "build", "tower_type": "dart", "x": build_slot[0], "y": build_slot[1]},
        {"type": "upgrade", "tower_id": 1, "path": "a"},
        {"type": "noop"},
    ]

    first = run_with_actions(actions, seed=123)
    second = run_with_actions(actions, seed=123)
    assert first == second, "Determinism check failed: trajectories differ"


def assert_invalid_actions() -> None:
    env = load_environment({})
    obs = env.reset(seed=456)
    path_x, path_y = obs["map"]["path"][0]
    valid_actions = obs["valid_actions"]
    assert "build" in valid_actions and isinstance(valid_actions["build"], list)
    assert "upgrade" in valid_actions and isinstance(valid_actions["upgrade"], list)
    assert "sell" in valid_actions and isinstance(valid_actions["sell"], list)
    assert "start_round" in valid_actions
    for action in valid_actions["build"]:
        assert action["cost"] <= obs["cash"]

    noop_obs, noop_reward, noop_done, noop_info = env.step({"type": "noop"})
    assert noop_info.get("invalid_action") is False

    env.reset(seed=456)
    invalid_obs, invalid_reward, invalid_done, invalid_info = env.step(
        {"type": "build", "tower_type": "dart", "x": path_x, "y": path_y}
    )
    assert invalid_info.get("invalid_action") is True
    penalty = env.config["rewards"]["invalid_action_penalty"]
    expected = noop_reward - penalty
    assert abs(invalid_reward - expected) < 1e-6, "Invalid action penalty mismatch"

    obs = env.reset(seed=789)
    slot = obs["map"]["build_slots"][0]
    env.step({"type": "build", "tower_type": "dart", "x": slot[0], "y": slot[1]})
    obs, reward, done, info = env.step({"type": "upgrade", "tower_id": 999, "path": "a"})
    assert info.get("invalid_action") is True


def assert_round_cap() -> None:
    env = load_environment({"difficulty": {"max_rounds": 1}})
    env.reset(seed=321)
    obs, reward, done, info = env.step({"type": "start_round"})
    assert done is True
    assert obs["round"] == 1


def main() -> None:
    assert_determinism()
    assert_invalid_actions()
    assert_round_cap()
    print("smoke checks passed")


if __name__ == "__main__":
    main()
