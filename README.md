# Prime Intellect RL Tower Defense (v1)

Text-first tower-defense environment designed for Prime Intellect hosted RFT (prime-rl + verifiers).

## Goals (v1)
- Deterministic simulation with procedural maps and infinite rounds.
- Verifiers-compatible environment (`load_environment`).
- Baseline training + evaluation harness.

## Repo layout
- `src/prime_td_env/`: environment package
- `configs/`: environment schemas + default configs

## Notes
- Primary planning docs live in CO (see `docs/PRD-prime-intellect-rl-tower-defense.md`).
- Prime Intellect hosted training docs list supported model families; v1 target: `Qwen/Qwen3-4B-Instruct-2507` (fallback `Qwen/Qwen3-30B-Instruct-2507`).

## Next steps
1) Implement `load_environment` in `src/prime_td_env/environment.py`.
2) Define the state/action schema in `configs/env_schema.json` and wire config loading.
3) Add a smoke test harness to validate determinism and action validity.
