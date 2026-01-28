# Prime Intellect RL Tower Defense (v1)

Text-first tower-defense environment designed for Prime Intellect hosted RFT (prime-rl + verifiers).

## Goals (v1)
- Deterministic simulation with procedural maps and infinite rounds.
- Verifiers-compatible environment (`load_environment`).
- Baseline training + evaluation harness.
- Infinite rounds default (set `difficulty.max_rounds` to cap episodes).

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

## Next steps
1) Expand tower/bloon mechanics (crosspathing, camo/regrow/fortified, MOAB layers) and freeplay scaling curves.
2) Add a Prime Lab RFT config + Prime Inference eval runner.

## Smoke checks
Run deterministic + invalid-action checks:

```bash
PYTHONPATH=src python3 scripts/smoke.py
```
