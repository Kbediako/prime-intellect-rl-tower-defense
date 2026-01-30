# Prime Intellect RL Tower Defense (v1)

Text-first tower-defense environment designed for Prime Intellect hosted RFT (prime-rl + verifiers).

## Goals (v1)
- Deterministic simulation with procedural maps and infinite rounds.
- Verifiers-compatible environment (`load_environment`).
- Baseline training + evaluation harness.
- Infinite rounds default (set `difficulty.max_rounds` to cap episodes).

## Action phases
- Agent acts between rounds (build/upgrade/sell/noop).
- Use `start_round` to advance the wave to completion.

## Repo layout
- `src/prime_td_env/`: environment package
- `configs/`: environment schemas + default configs

## Notes
- Primary planning docs live in CO (see `docs/PRD-prime-intellect-rl-tower-defense.md`).
- Prime Intellect hosted training docs list supported model families; v1 target: `Qwen/Qwen3-4B-Instruct-2507` (fallback `Qwen/Qwen3-30B-A3B-Instruct-2507` or `PrimeIntellect/INTELLECT-3`).

## Baseline training
Run a minimal linear Q-learning loop to validate the environment:

```bash
PYTHONPATH=src python3 scripts/train_baseline.py --episodes 5 --max-rounds 20
```

## Evaluation harness
Run seeded evaluation and emit aggregate metrics:

```bash
PYTHONPATH=src python3 scripts/eval_baseline.py --episodes 10 --max-rounds 20 --output out/metrics.json
```

For deterministic suites + JSONL summaries:

```bash
PYTHONPATH=src python3 scripts/eval.py --eval-seed-count 50 --random-seed-count 20 --output-dir out/eval
```

## Prime RL hosted training
Hosted training runs use TOML configs with `prime rl run` and require a verifiers-compatible environment
published to the Prime Environments Hub. This repo includes a starter template at
`configs/lab/prime-td.toml` (update the `env.id` after publishing).

Suggested setup steps (per Prime docs):
1) Install Prime CLI and authenticate.
2) Initialize a config with `prime rl init` (defaults to `rl.toml`).
3) Publish the environment: `prime env push` (once the verifiers wrapper is ready).
4) Launch a run: `prime rl run configs/lab/prime-td.toml`.

Notes:
- Pass secrets via `env_file` or `prime rl run -e KEY=VALUE`; avoid hardcoding credentials in `args`.
- Use env args for variable names (e.g., `api_key_var`) and read them via `os.getenv`.
- Copy `configs/lab/secrets.env.example` to `configs/lab/secrets.env` for local runs (not committed).

## Prime Inference auth check
Verify credentials and list available models:

```bash
export PRIME_API_KEY="..."
export PRIME_TEAM_ID="..." # optional
PYTHONPATH=src python3 scripts/prime_inference_check.py --limit 5
```

## Next steps
1) Expand tower/bloon mechanics (crosspathing, camo/regrow/fortified, MOAB layers) and freeplay scaling curves.
2) Add a Prime Lab RFT config + Prime Inference eval runner.

## Smoke checks
Run deterministic + invalid-action checks:

```bash
PYTHONPATH=src python3 scripts/smoke.py
```
