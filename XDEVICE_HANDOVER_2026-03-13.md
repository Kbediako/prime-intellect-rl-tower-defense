## Cross-Device Handover Mirror

This file is the tracked remote mirror of the local handover bundle created on March 13, 2026.

- Local bundle path: `/Users/kbediako/Code/prime-intellect-rl-tower-defense-xdevice-handover-2026-03-13.zip`
- SHA-256: `c152d9aa0ef71ed88d06526fb375855e116e03515bbbac1599341852cfa2ec31`
- Bundle size: `251676075` bytes

## What This Push Mirrors

This push mirrors the tracked code and test changes that were included in the zip:

- actual-game relabel repairs for invalid placement and insufficient-cash historical failures
- local SFT and local eval runtime support for non-CUDA paths, including MPS
- actual-game summary alignment updates (`teamCash`, visible occupied anchor filtering)
- new bridge failure filtering, strict bridge scoring, and custom replay builder utilities
- matching unit tests for the new replay/filter/score paths and the relabel repairs

## What Is Still Local-Only

The zip contains additional local-only state that cannot be mirrored by a normal GitHub push:

- the `artifacts/` tree, which is gitignored in this repo
- the cross-device handover packet under `artifacts/x1267_cross_device_handover/`
- the authoritative local frontier/decision artifacts under `artifacts/x1265...` and `artifacts/x1266...`
- large recovered x1264 training bundles that are not suitable for normal GitHub storage

This tracked file therefore inlines the critical handover state instead of trying to push the ignored artifact tree.

## Current Truthful State

- No active paid Prime pods.
- Latest paid row43-only rerun `x1264` is closed and rejected.
- `x1264` result:
  - `50/73` env-pass
  - `73/73` format-pass
- Decision:
  - reject `x1264` for live promotion
  - keep paid launch closed after `x1264`

## Active Frontier

- `x1180` remains the key row43-only paid control at `51/73`.
- `x1239` is a co-frontier tie rather than a replacement frontier.
- `x1245` is a non-promotable co-frontier advance rather than a live-canary clearance.
- The paid row43-only family rooted at `x1261` is exhausted.
- `x1256` broad row43-plus-guardset remains hold-only.
- The active frontier references are back to `x1245` and `x1239`.

## Local Control Reality

- A generic no-spend local SFT/eval path now exists in code.
- On the 16 GB Apple Silicon MacBook Air used for the handover, that path remained device-blocked for this 4B control family.

## Resume Guidance

If resuming from the repository alone, start from the frontier state above.

If resuming with the local handover zip as well, the first files to read are:

1. `artifacts/x1265_x1264_row43_only_rejection_decision/report.json`
2. `artifacts/x1266_offline_post_x1264_replan/report.json`
3. `artifacts/x1246_x1245_r27_r59_frontier_advance_no_live_promotion/report.json`
4. `artifacts/x1240_x1239_r53_only_frontier_advance/report.json`
5. `artifacts/x1181_x1180_frontier_advance_no_live_promotion/report.json`
6. `artifacts/x1257_offline_x1256_launch_clearance/report.json`
7. `artifacts/x1263_offline_x1261_local_control_clearance/report.json`
