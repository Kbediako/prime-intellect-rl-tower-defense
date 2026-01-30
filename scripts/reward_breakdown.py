"""Print reward component breakdown statistics over an episode."""

from __future__ import annotations

import argparse
import json
from typing import Any, Dict

from prime_td_env.environment import load_environment


def select_random(obs: Dict[str, Any], rng_seed: int) -> Dict[str, Any]:
    valid_actions = obs.get("valid_actions", {})
    actions = []
    for key in ("build", "upgrade", "sell"):
        actions.extend(valid_actions.get(key, []))
    if valid_actions.get("start_round"):
        actions.append({"type": "start_round"})
    if valid_actions.get("noop"):
        actions.append({"type": "noop"})
    if not actions:
        return {"type": "noop"}
    return actions[rng_seed % len(actions)]


def run_episode(env, seed: int, max_steps: int | None) -> Dict[str, Any]:
    obs = env.reset(seed=seed)
    totals: Dict[str, float] = {
        "pop_reward": 0.0,
        "end_round_income": 0.0,
        "life_loss_penalty": 0.0,
        "invalid_action_penalty": 0.0,
        "step_penalty": 0.0,
    }
    steps = 0
    while True:
        action = select_random(obs, seed + steps)
        obs, reward, done, info = env.step(action)
        breakdown = info.get("reward_breakdown", {})
        for key in totals.keys():
            totals[key] += float(breakdown.get(key, 0.0))
        steps += 1
        if done or (max_steps is not None and steps >= max_steps):
            return {
                "seed": seed,
                "steps": steps,
                "round": obs.get("round", 0),
                "lives_remaining": obs.get("lives", 0),
                "reward_breakdown": totals,
            }


def main() -> None:
    parser = argparse.ArgumentParser(description="Print reward breakdown for a single episode.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-rounds", type=int, default=20)
    parser.add_argument("--max-steps", type=int, default=None)
    args = parser.parse_args()

    config: Dict[str, Any] = {"difficulty": {"max_rounds": args.max_rounds}}
    env = load_environment(config)
    result = run_episode(env, args.seed, args.max_steps)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
