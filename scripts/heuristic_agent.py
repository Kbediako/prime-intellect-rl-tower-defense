"""Simple heuristic agent for sanity checks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from prime_td_env.environment import TowerDefenseEnv


def select_action(obs: Dict[str, Any]) -> Dict[str, Any]:
    valid_actions = obs.get("valid_actions", {})
    builds = valid_actions.get("build", [])
    upgrades = valid_actions.get("upgrade", [])

    if upgrades:
        upgrade_a = [action for action in upgrades if action.get("path") == "a"]
        if upgrade_a:
            return upgrade_a[0]
        return upgrades[0]

    if builds and len(obs.get("towers", [])) < 2:
        return builds[0]

    if valid_actions.get("start_round"):
        return {"type": "start_round"}

    if builds:
        return builds[0]

    return {"type": "noop"}


def run_episode(env, seed: int, max_steps: int | None) -> Dict[str, Any]:
    obs = env.reset(seed=seed)
    total_reward = 0.0
    steps = 0
    invalid_actions = 0
    while True:
        action = select_action(obs)
        obs, reward, done, info = env.step(action)
        total_reward += reward
        steps += 1
        if info.get("invalid_action"):
            invalid_actions += 1
        if done or (max_steps is not None and steps >= max_steps):
            return {
                "seed": seed,
                "reward": total_reward,
                "round": obs.get("round", 0),
                "steps": steps,
                "lives_remaining": obs.get("lives", 0),
                "invalid_actions": invalid_actions,
                "termination": info.get("termination", ""),
            }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the heuristic agent for a few episodes.")
    parser.add_argument("--episodes", type=int, default=5)
    parser.add_argument("--seed-start", type=int, default=1000)
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--max-rounds", type=int, default=20)
    parser.add_argument("--output", type=str, default="")
    args = parser.parse_args()

    config: Dict[str, Any] = {"difficulty": {"max_rounds": args.max_rounds}}
    env = TowerDefenseEnv(config)

    results: List[Dict[str, Any]] = []
    for i in range(args.episodes):
        seed = args.seed_start + i
        results.append(run_episode(env, seed, args.max_steps))

    payload = {
        "episodes": args.episodes,
        "results": results,
    }
    print(json.dumps(payload, indent=2))

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2))
        print(f"wrote_metrics={output_path}")


if __name__ == "__main__":
    main()
