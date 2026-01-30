# Results — Prime Intellect RL Tower Defense

> Status: **Run A in progress**, Run B queued (starts after A completes).

## Run Snapshot

| Run | Status | Run ID | Base Model | Env ID | Env Version | Config | Primary Delta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | running | `cpe5e60oplhmtdsa3byqc6ro` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.1` | `configs/lab/prime-td-run-a.toml` | baseline weights + sampling |
| B | queued | `<TBD>` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.1` | `configs/lab/prime-td-run-b.toml` | tuned weights + tighter sampling |

## Run A Snapshot (exact config)

- **Run ID:** `cpe5e60oplhmtdsa3byqc6ro`
- **Base model:** `Qwen/Qwen3-4B-Instruct-2507`
- **Env ID:** `kbediako/prime-td-env`
- **Env version:** `0.2.1` (see `pyproject.toml`, wheel SHA in `.prime/.env-metadata.json`)
- **Config:** `configs/lab/prime-td-run-a.toml`
- **Sampling:** `temperature=0.2`, `max_tokens=64`
- **Reward weights:** `reward_weights.env=1.0`, `reward_weights.format=0.5`
- **Step penalty:** `0.1`
- **Dataset rollout:** `rollout_steps=2`, `policy=random`
- **Eval cadence:** every 20 steps, held-out seeds start at `1000`

## A vs B — Controlled Change

Primary delta (intended):
- **Lower format weight + higher step penalty** in B (`format=0.25`, `step_penalty=0.2`).

Secondary deltas (explicit):
- **Tighter sampling** in B (`temperature=0.15`, `max_tokens=48`).

## Eval Protocol (fixed + deterministic)

- **Train seeds:** `0..63` (64 examples)
- **Held-out eval seeds:** `1000..1049` (50 examples)
- **Random suite:** `2000..2019` (20 examples)
- **Metrics:** avg_round, win_rate, lives_remaining, invalid_json_rate, invalid_action_rate, truncation_rate
- **Eval command:** see “Repro commands” in this doc once run completes

## Metrics (placeholders)

| Run | Avg Round | Win Rate | Avg Lives | Avg Reward | Invalid JSON | Invalid Action | Truncation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A (early) | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| A (late) | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| B (early) | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| B (late) | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

## Rollout Snippets (placeholders)

1) **Snippet A1:** _TBD_
   - **Demonstrates:** _TBD_
2) **Snippet A2:** _TBD_
   - **Demonstrates:** _TBD_
3) **Snippet B1:** _TBD_
   - **Demonstrates:** _TBD_

## Known Observations / Open Checks

- Run A early samples show repeated `start_round` actions with high reward. Likely driven by `rollout_steps=2` seeding towers in the prompt (so “advance” is locally good). We will verify whether this reduces build/upgrade diversity and adjust in later runs if needed.

## Repro Commands (to fill once run completes)

- Collect artifacts: `scripts/collect_prime_run_artifacts.sh <RUN_ID>`
- Held-out eval: `python3 scripts/eval.py --eval-seed-start 1000 --eval-seed-count 50 --random-seed-start 2000 --random-seed-count 20 --max-rounds 20 --max-steps 200 --output-dir out/eval`

