"""Evaluate a baseline policy and emit aggregate metrics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

from prime_td_env.environment import load_environment

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
    weights: np.ndarray | None,
    rng: np.random.Generator,
    epsilon: float,
) -> Dict[str, Any]:
    actions = flatten_actions(obs["valid_actions"])
    if not actions:
        return {"type": "noop"}

    if weights is None:
        return actions[int(rng.integers(len(actions)))]

    features = np.stack([featurize(obs, action, tower_types) for action in actions])
    q_values = features @ weights

    if rng.random() < epsilon:
        index = int(rng.integers(len(actions)))
    else:
        max_q = float(np.max(q_values))
        best = np.flatnonzero(q_values == max_q)
        index = int(rng.choice(best))
    return actions[index]


def run_episode(
    env,
    seed: int,
    weights: np.ndarray | None,
    rng: np.random.Generator,
    epsilon: float,
    max_steps: int | None,
) -> Tuple[float, int, int, int, Dict[str, int], str, int]:
    obs = env.reset(seed=seed)
    tower_types = sorted(env.tower_types.keys())
    total_reward = 0.0
    steps = 0
    invalid_actions = 0
    action_counts: Dict[str, int] = {}
    termination = ""

    while True:
        action = select_action(obs, tower_types, weights, rng, epsilon)
        action_type = action.get("type", "noop")
        action_counts[action_type] = action_counts.get(action_type, 0) + 1
        next_obs, reward, done, info = env.step(action)
        total_reward += reward
        steps += 1

        if info.get("invalid_action"):
            invalid_actions += 1

        obs = next_obs
        if done or (max_steps is not None and steps >= max_steps):
            termination = info.get("termination", "")
            return total_reward, obs["round"], steps, invalid_actions, action_counts, termination, obs["lives"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a baseline policy and emit metrics.")
    parser.add_argument("--episodes", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--seed-base", type=int, default=1000)
    parser.add_argument("--seeds", type=str, default="")
    parser.add_argument("--epsilon", type=float, default=0.0)
    parser.add_argument("--max-rounds", type=int, default=20)
    parser.add_argument("--no-round-cap", action="store_true")
    parser.add_argument("--max-action-candidates", type=int, default=200)
    parser.add_argument("--max-steps", type=int, default=200)
    parser.add_argument("--weights", type=str, default="")
    parser.add_argument("--output", type=str, default="")
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

    env = load_environment(config)
    rng = np.random.default_rng(args.seed)

    weights = None
    if args.weights:
        weights = np.load(args.weights)

    if args.seeds:
        seeds = [int(val.strip()) for val in args.seeds.split(",") if val.strip()]
    else:
        seeds = [args.seed_base + i for i in range(args.episodes)]

    rewards: List[float] = []
    rounds: List[int] = []
    lives_remaining: List[int] = []
    steps_list: List[int] = []
    invalid_total = 0
    action_counts = {name: 0 for name in ACTION_TYPES}
    termination_counts: Dict[str, int] = {}

    for seed in seeds:
        reward, round_reached, steps, invalid_actions, episode_action_counts, termination, lives_left = run_episode(
            env,
            seed,
            weights,
            rng,
            args.epsilon,
            args.max_steps,
        )
        rewards.append(reward)
        rounds.append(round_reached)
        lives_remaining.append(lives_left)
        steps_list.append(steps)
        invalid_total += invalid_actions
        for action_type, count in episode_action_counts.items():
            action_counts[action_type] = action_counts.get(action_type, 0) + count

        if termination:
            termination_counts[termination] = termination_counts.get(termination, 0) + 1

    avg_reward = float(np.mean(rewards)) if rewards else 0.0
    avg_round = float(np.mean(rounds)) if rounds else 0.0
    avg_steps = float(np.mean(steps_list)) if steps_list else 0.0
    invalid_rate = float(invalid_total) / float(sum(steps_list)) if steps_list else 0.0

    metrics = {
        "episodes": len(seeds),
        "avg_reward": avg_reward,
        "avg_round": avg_round,
        "avg_steps": avg_steps,
        "avg_lives_remaining": float(np.mean(lives_remaining)) if lives_remaining else 0.0,
        "invalid_action_rate": invalid_rate,
        "invalid_json_rate": 0.0,
        "reward_std": float(np.std(rewards)) if rewards else 0.0,
        "round_std": float(np.std(rounds)) if rounds else 0.0,
        "termination_counts": termination_counts,
        "action_type_counts": action_counts,
    }

    print(json.dumps(metrics, indent=2))

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(metrics, indent=2))
        print(f"wrote_metrics={output_path}")


if __name__ == "__main__":
    main()
