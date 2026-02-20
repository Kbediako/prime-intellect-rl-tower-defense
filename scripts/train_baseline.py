"""Baseline linear Q-learning loop for quick environment validation."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

from prime_td_env.environment import TowerDefenseEnv

ACTION_TYPES = ["build", "upgrade", "sell", "start_round", "noop"]
UPGRADE_PATHS = ["a", "b", "c"]


def flatten_actions(valid_actions: Dict[str, Any]) -> List[Dict[str, Any]]:
    actions: List[Dict[str, Any]] = []
    for key in ("build", "upgrade", "sell"):
        actions.extend(valid_actions.get(key, []))
    if valid_actions.get("start_round"):
        actions.append({"type": "start_round"})
    if valid_actions.get("noop"):
        actions.append({"type": "noop"})
    return actions


def featurize(obs: Dict[str, Any], action: Dict[str, Any], tower_types: List[str]) -> np.ndarray:
    towers = obs.get("towers", [])
    tower_map = {tower["id"]: tower for tower in towers}
    total_upgrades = 0
    for tower in towers:
        total_upgrades += sum(tower.get("upgrades", {}).values())

    features: List[float] = [
        1.0,
        obs["round"] / 50.0,
        obs["cash"] / 1000.0,
        obs["lives"] / 100.0,
        len(towers) / 10.0,
        total_upgrades / 10.0,
    ]

    action_type = action.get("type", "noop")
    features.extend([1.0 if action_type == kind else 0.0 for kind in ACTION_TYPES])

    cost = float(action.get("cost", 0.0))
    refund = float(action.get("refund", 0.0))
    features.append(cost / 500.0)
    features.append(refund / 500.0)

    action_tower_type = action.get("tower_type")
    if action_tower_type is None and action_type == "upgrade":
        tower = tower_map.get(action.get("tower_id"))
        if tower:
            action_tower_type = tower.get("type")
    features.extend([1.0 if action_tower_type == name else 0.0 for name in tower_types])

    path = action.get("path")
    features.extend([1.0 if path == p else 0.0 for p in UPGRADE_PATHS])

    tier = float(action.get("tier", 0.0))
    features.append(tier / 3.0)

    return np.asarray(features, dtype=np.float32)


def select_action(
    obs: Dict[str, Any],
    tower_types: List[str],
    weights: np.ndarray,
    rng: np.random.Generator,
    epsilon: float,
) -> Tuple[Dict[str, Any], np.ndarray, float]:
    actions = flatten_actions(obs["valid_actions"])
    if not actions:
        noop = {"type": "noop"}
        features = featurize(obs, noop, tower_types)
        return noop, features, float(np.dot(features, weights))

    features = np.stack([featurize(obs, action, tower_types) for action in actions])
    q_values = features @ weights

    if rng.random() < epsilon:
        index = int(rng.integers(len(actions)))
    else:
        max_q = float(np.max(q_values))
        best = np.flatnonzero(q_values == max_q)
        index = int(rng.choice(best))

    return actions[index], features[index], float(q_values[index])


def run_episode(
    env,
    weights: np.ndarray,
    rng: np.random.Generator,
    epsilon: float,
    lr: float,
    gamma: float,
    max_steps: int | None,
) -> Tuple[float, int]:
    obs = env.reset(seed=int(rng.integers(1_000_000)))
    tower_types = sorted(env.tower_types.keys())
    total_reward = 0.0
    steps = 0

    while True:
        action, features, q_value = select_action(obs, tower_types, weights, rng, epsilon)
        next_obs, reward, done, info = env.step(action)
        total_reward += reward

        if done:
            target = reward
        else:
            next_actions = flatten_actions(next_obs["valid_actions"])
            if next_actions:
                next_features = np.stack([featurize(next_obs, act, tower_types) for act in next_actions])
                next_q = float(np.max(next_features @ weights))
            else:
                next_q = 0.0
            target = reward + gamma * next_q

        td_error = target - q_value
        weights += lr * td_error * features

        obs = next_obs
        steps += 1
        if done or (max_steps is not None and steps >= max_steps):
            break

    return total_reward, obs["round"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a quick baseline training loop.")
    parser.add_argument("--episodes", type=int, default=5)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--epsilon", type=float, default=0.2)
    parser.add_argument("--lr", type=float, default=0.05)
    parser.add_argument("--gamma", type=float, default=0.95)
    parser.add_argument("--max-rounds", type=int, default=20)
    parser.add_argument("--no-round-cap", action="store_true")
    parser.add_argument("--max-action-candidates", type=int, default=200)
    parser.add_argument("--max-steps", type=int, default=200)
    parser.add_argument("--save-path", type=str, default="")
    args = parser.parse_args()

    config: Dict[str, Any] = {
        "observation": {"max_action_candidates": args.max_action_candidates},
        "difficulty": {},
        "episode": {"max_steps": args.max_steps},
    }
    if args.no_round_cap:
        config["difficulty"]["max_rounds"] = None
    else:
        config["difficulty"]["max_rounds"] = args.max_rounds

    env = TowerDefenseEnv(config)
    rng = np.random.default_rng(args.seed)

    weights = np.zeros(6 + len(ACTION_TYPES) + 2 + len(sorted(env.tower_types.keys())) + len(UPGRADE_PATHS) + 1, dtype=np.float32)

    rewards: List[float] = []
    rounds: List[int] = []

    for episode in range(args.episodes):
        episode_reward, episode_round = run_episode(
            env,
            weights,
            rng,
            args.epsilon,
            args.lr,
            args.gamma,
            args.max_steps,
        )
        rewards.append(episode_reward)
        rounds.append(episode_round)
        print(
            f"episode {episode + 1}/{args.episodes} reward={episode_reward:.2f} "
            f"round={episode_round}"
        )

    avg_reward = float(np.mean(rewards)) if rewards else 0.0
    avg_round = float(np.mean(rounds)) if rounds else 0.0
    print(f"avg_reward={avg_reward:.2f} avg_round={avg_round:.2f}")

    if args.save_path:
        save_path = Path(args.save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(save_path, weights)
        print(f"saved_weights={save_path}")


if __name__ == "__main__":
    main()
