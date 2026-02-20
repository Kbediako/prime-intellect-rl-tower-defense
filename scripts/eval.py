"""Deterministic evaluation harness for random/heuristic/trained baselines."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

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
        obs.get("round", 1) / 50.0,
        obs.get("cash", 0) / 1000.0,
        obs.get("lives", 0) / 100.0,
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


def select_random(obs: Dict[str, Any], rng: np.random.Generator) -> Dict[str, Any]:
    actions = flatten_actions(obs.get("valid_actions", {}))
    if not actions:
        return {"type": "noop"}
    return actions[int(rng.integers(len(actions)))]


def select_heuristic(obs: Dict[str, Any]) -> Dict[str, Any]:
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


def select_trained(
    obs: Dict[str, Any],
    tower_types: List[str],
    weights: np.ndarray,
    rng: np.random.Generator,
    epsilon: float,
) -> Dict[str, Any]:
    actions = flatten_actions(obs.get("valid_actions", {}))
    if not actions:
        return {"type": "noop"}

    features = np.stack([featurize(obs, action, tower_types) for action in actions])
    q_values = features @ weights

    if rng.random() < epsilon:
        index = int(rng.integers(len(actions)))
    else:
        max_q = float(np.max(q_values))
        best = np.flatnonzero(q_values == max_q)
        index = int(rng.choice(best))
    return actions[index]


def run_episode(env, seed: int, agent: str, rng: np.random.Generator, max_steps: int | None, weights: np.ndarray | None) -> Dict[str, Any]:
    obs = env.reset(seed=seed)
    tower_types = sorted(env.tower_types.keys())
    total_reward = 0.0
    steps = 0
    invalid_actions = 0
    termination = ""

    while True:
        if agent == "random":
            action = select_random(obs, rng)
        elif agent == "heuristic":
            action = select_heuristic(obs)
        else:
            action = select_trained(obs, tower_types, weights, rng, epsilon=0.0)

        obs, reward, done, info = env.step(action)
        total_reward += reward
        steps += 1
        if info.get("invalid_action"):
            invalid_actions += 1

        if done or (max_steps is not None and steps >= max_steps):
            termination = info.get("termination", "")
            return {
                "seed": seed,
                "reward": total_reward,
                "round": obs.get("round", 0),
                "steps": steps,
                "lives_remaining": obs.get("lives", 0),
                "invalid_actions": invalid_actions,
                "invalid_action_rate": float(invalid_actions) / float(steps) if steps else 0.0,
                "invalid_json_rate": 0.0,
                "termination": termination,
            }


def summarize(agent: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not records:
        return {}
    avg_round = float(np.mean([r["round"] for r in records]))
    avg_lives = float(np.mean([r["lives_remaining"] for r in records]))
    avg_reward = float(np.mean([r["reward"] for r in records]))
    avg_steps = float(np.mean([r["steps"] for r in records]))
    invalid_action_rate = float(np.mean([r["invalid_action_rate"] for r in records]))
    invalid_json_rate = float(np.mean([r["invalid_json_rate"] for r in records]))
    wins = sum(1 for r in records if r.get("termination") != "loss")
    return {
        "agent": agent,
        "episodes": len(records),
        "avg_round": avg_round,
        "avg_lives_remaining": avg_lives,
        "avg_reward": avg_reward,
        "avg_steps": avg_steps,
        "win_rate": wins / float(len(records)) if records else 0.0,
        "invalid_action_rate": invalid_action_rate,
        "invalid_json_rate": invalid_json_rate,
    }


def render_markdown(summary: List[Dict[str, Any]]) -> str:
    headers = [
        "agent",
        "episodes",
        "avg_round",
        "win_rate",
        "avg_lives_remaining",
        "avg_reward",
        "invalid_action_rate",
        "invalid_json_rate",
    ]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in summary:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row.get("agent", "")),
                    str(row.get("episodes", 0)),
                    f"{row.get('avg_round', 0.0):.2f}",
                    f"{row.get('win_rate', 0.0):.2f}",
                    f"{row.get('avg_lives_remaining', 0.0):.2f}",
                    f"{row.get('avg_reward', 0.0):.2f}",
                    f"{row.get('invalid_action_rate', 0.0):.4f}",
                    f"{row.get('invalid_json_rate', 0.0):.4f}",
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic eval suites for baseline agents.")
    parser.add_argument("--eval-seed-start", type=int, default=1000)
    parser.add_argument("--eval-seed-count", type=int, default=50)
    parser.add_argument("--random-seed-start", type=int, default=2000)
    parser.add_argument("--random-seed-count", type=int, default=20)
    parser.add_argument("--max-rounds", type=int, default=20)
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--max-action-candidates", type=int, default=200)
    parser.add_argument("--weights", type=str, default="")
    parser.add_argument("--output-dir", type=str, default="out/eval")
    args = parser.parse_args()

    config: Dict[str, Any] = {
        "difficulty": {"max_rounds": args.max_rounds},
        "observation": {"max_action_candidates": args.max_action_candidates},
        "episode": {"max_steps": args.max_steps},
    }
    env = TowerDefenseEnv(config)
    rng = np.random.default_rng(42)

    agents = ["random", "heuristic"]
    weights = None
    if args.weights:
        weights = np.load(args.weights)
        agents.append("trained")

    eval_seeds = [args.eval_seed_start + i for i in range(args.eval_seed_count)]
    random_seeds = [args.random_seed_start + i for i in range(args.random_seed_count)]

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "episodes.jsonl"

    all_records: List[Dict[str, Any]] = []
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for suite_name, seeds in (("heldout", eval_seeds), ("random", random_seeds)):
            for agent in agents:
                agent_weights = weights if agent == "trained" else None
                records = []
                for seed in seeds:
                    record = run_episode(env, seed, agent, rng, args.max_steps, agent_weights)
                    record["agent"] = agent
                    record["suite"] = suite_name
                    records.append(record)
                    handle.write(json.dumps(record) + "\n")
                all_records.extend(records)

    summary = []
    for agent in agents:
        agent_records = [r for r in all_records if r["agent"] == agent and r["suite"] == "heldout"]
        summary.append(summarize(agent, agent_records))

    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))

    table = render_markdown(summary)
    table_path = output_dir / "summary.md"
    table_path.write_text(table)

    print(table)
    print(f"wrote_jsonl={jsonl_path}")
    print(f"wrote_summary={summary_path}")
    print(f"wrote_table={table_path}")


if __name__ == "__main__":
    main()
