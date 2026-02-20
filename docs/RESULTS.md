# Results — Prime Intellect RL Tower Defense

> Status: **SingleTurn diagnostics concluded**; macro-round multi-turn is the primary training interface. Episode-length validation remains **inconclusive beyond cap** (X44/X45/X46b/X47b/X49/X53/X55/X57/X59/X61/X63/X65/X67/X69/X73/X75/X77/X79/X81/X83/X85/X87/X89/X91/X93/X96/X98/X102/X104/X106/X110/X112/X114/X116/X118/X120/X122/X124 hit observed caps at 20/22/24/26/28/30/30/30/32/34/36/36/38/38/38/40/42/44/44/46/46/48/50/50/50/52/53/54/54/53/54/54/53/54/54/54/54/54). Horizon probes still show intermittent sample-upload 500s on some runs (X51 no samples; X53 partial samples; X55 partial samples; X63 missing step-20 samples; X67 missing step 0/20/40 samples; X69 missing step 0 samples; X79 partial sample coverage at steps 10/20/50; X83 partial sample coverage at steps 0/10/20; X89 partial sample coverage at steps 20/30/40; X100 no samples with upload 500s at steps 0/10/20/30/40/50; X102 partial sample coverage at steps 20/50 with upload 500s; X104 only step-40 samples with upload 500s at 0/10/20/30/50; X108 partial sample coverage at steps 0/30/40 with upload 500s; X110 partial sample coverage at step 30 with upload 500s; X112 partial sample coverage at steps 10/40/50 with upload 500s), while the reliability-first horizon lane now includes high-cap runs with full samples at 30/32/34/36/38/40/42/44/46/48/50/52/53/54 (X57/X59/X61/X65/X73/X75/X77/X81/X85/X87/X91/X93/X96/X98/X106/X114/X116/X118/X120/X122/X124). Adaptive late-phase policy target is spend-primary (upgrade-leaning with build presence, **25-45% late upgrade lead on spend**; count lead is secondary trend only). X71 remains invalid for policy analysis due persistent truncation/format failures.
> Horizon measurement semantics: with `difficulty.max_rounds = N`, observed episode length is right-censored at `N`; cap-hit runs prove only a lower bound (`true horizon >= N`). To test beyond-cap gains, raise `max_rounds` in the horizon lane while keeping payload-safe controls fixed.
> Decision update (2026-02-11): PI-side upload reliability appears materially improved on recent runs; treat larger payload/volume experiments as allowed again, but only via one-variable canaries with two consecutive reliable confirmations before further expansion. Continue classifying reliability separately from policy quality when samples are missing.

## Run Snapshot

| Run | Status | Run ID | Base Model | Env ID | Env Version | Config | Primary Delta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | completed | `cpe5e60oplhmtdsa3byqc6ro` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.1` | `configs/lab/prime-td-run-a.toml` | baseline weights + sampling |
| B | completed | `y788w0uxqiormzp81q1poq41` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.1` | `configs/lab/prime-td-run-b.toml` | tuned weights + tighter sampling |
| C | stopped | `dw5b1xkhx8sj4ny9ljgvvqml` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.1` | `configs/lab/prime-td-run-c.toml` | rollout_steps=0 curriculum change |
| D | stopped | `ds2s6uije2q9z4t9ny1e70fb` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.1` | `configs/lab/prime-td-run-d.toml` | rollout_steps=0 + lower step penalty |
| E | completed | `xc662lm8afgdz25dc0a7dhdu` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.1` | `configs/lab/prime-td-run-e.toml` | rollout_steps=1 diagnostic |
| F | completed | `u1uxany3ub4g7gab3aofd7gh` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.1` | `configs/lab/prime-td-run-f.toml` | rollout_steps=1 + lower step penalty |
| H | stopped | `z95gkb5x662h6selsv4125rn` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.1` | `configs/lab/prime-td-run-h.toml` | lookahead_rounds=8, weight=0.5 |
| J | completed | `x1ctjo6uvbqmdbpomn76zxfw` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.1` | `configs/lab/prime-td-run-j.toml` | lookahead_rounds=2, weight=0.5 + rollout_steps=4 |
| K | completed | `eqjqeuhswcenpnt3vdvythig` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.2` | `configs/lab/prime-td-auto-advance-80-k.toml` | auto-advance + prep budget (2 → scale 0.1, max 6) |
| L | completed | `ogxpb2r9sylec7sl9c9a9xu2` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.2` | `configs/lab/prime-td-auto-advance-80-l.toml` | auto-advance + higher prep budget (3 → scale 0.15, max 8) |
| M | completed | `a6vzmamlqca13wcziu9zlero` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.2` | `configs/lab/prime-td-auto-advance-80-m.toml` | rollout_steps=9 (target round ~5, remaining=1) |
| N | completed | `bwyppq2uq9qhjw9i91kyc8k4` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.2` | `configs/lab/prime-td-auto-advance-80-n.toml` | max_build_slots=12 (compress build action space) |
| O | completed | `i1lpujti4rwhd52qp1d5cnde` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.3` | `configs/lab/prime-td-auto-advance-80-o.toml` | reward credit: auto-advance round completion in rubric |
| P | completed | `cxysr9i9p16oz5co0l6lvl9a` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.3` | `configs/lab/prime-td-auto-advance-80-p.toml` | dataset.policy=bootstrap for decision-relevant prompts |
| Q | completed | `ns3xax5y1gpvlcmuv5j6ando` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.7` | `configs/lab/prime-td-auto-advance-80-q.toml` | dataset.policy=noop_then_start (round ~5, prep remaining=1) |
| R | completed | `eonmjp6nrmq1mphz2n93779i` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.7` | `configs/lab/prime-td-auto-advance-80-r.toml` | noop_then_start + start_round_max_prep_remaining=1 (enforced) |
| S | completed | `rouzhjav619vbwxazzkx9fzs` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.10` | `configs/lab/prime-td-auto-advance-80-s.toml` | max_build_slots=3 + higher exploration |
| T | completed | `qud3jsz07g060aiumnvowsbv` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.10` | `configs/lab/prime-td-auto-advance-80-t.toml` | cash-scarce economy to force upgrades |
| U | completed | `xzmgqle5c5c68jp3d2bpukn8` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.11` | `configs/lab/prime-td-auto-advance-80-u.toml` | diverse snapshot dataset + dominance diagnostic |
| V | completed | `g5ylvtzgn2m7wa4710l4nkb2` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.11` | `configs/lab/prime-td-macro-round-30-v.toml` | macro-round multi-turn diagnostic |
| W | completed | `ljq5em3x4m8iuk84s30miz80` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.13` | `configs/lab/prime-td-auto-advance-80-w.toml` | SingleTurn snapshot run (rounds 15/20, decision filter disabled) |
| X | failed (no samples) | `jdgigcvppsiq09b7af5tqp3d` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.13` | `configs/lab/prime-td-macro-round-60-x.toml` | macro-round diagnostic; rollouts returned 0 samples |
| X2 | stopped (no samples) | `vo84e6ikhq9u9hc98y2gm2i1` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.13` | `configs/lab/prime-td-macro-round-60-x.toml` | macro-round rerun; logs showed 500s on sample uploads |
| X3 | stopped (no samples) | `aqubxfcdpwhg69efxofqjhrw` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.13` | `configs/lab/prime-td-macro-round-60-x.toml` | rerun with max_tokens=64, rollouts_per_example=1, smaller prompts |
| X4 | completed (format-invalid) | `ddr57p562fj7o4g6dryodlat` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.13` | `configs/lab/prime-td-macro-round-60-x.toml` | rerun with max_tokens=32, rounds=[10,15], max_rounds=15, smaller prompts |
| X5 | completed (format-invalid) | `c20w0kwl9lu8ldgdiphmfkra` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.13` | `configs/lab/prime-td-macro-round-60-x.toml` | rerun with max_tokens=48, rounds=[10,15], max_rounds=15, smaller prompts |
| X6 | completed (valid plans, invalid actions) | `xinrtc6zvjy28t7974st4tsj` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.13` | `configs/lab/prime-td-macro-round-60-x.toml` | parallel run with max_tokens=96, same caps |
| X7 | stopped (no samples) | `ddjewl8c12ixol8pizpri5e6` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.13` | `configs/lab/prime-td-macro-round-60-x7.toml` | choose-index plans, max_tokens=64, max_rounds=20 |
| X8 | stopped (no samples) | `ho9d66h4359hte2q41ull6an` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.13` | `configs/lab/prime-td-macro-round-60-x8.toml` | choose-index plans, max_tokens=96, max_rounds=20 |
| X9 | stopped (no samples) | `l9n63uciqylm5c8kmsqa8hsm` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.13` | `configs/lab/prime-td-macro-round-60-x9.toml` | choose-index plans, max_tokens=32, batch_size=8 |
| X10 | stopped (no samples) | `aadtrwgfor3no3iank7njtqw` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.13` | `configs/lab/prime-td-macro-round-60-x10.toml` | choose-index plans, max_tokens=48, batch_size=8 |
| X11 | completed (rounds stalled) | `p4ovp2yk1tx4cisez61ein86` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.14` | `configs/lab/prime-td-macro-round-60-x11.toml` | choose-index plans, max_rounds=16, max_tokens=64, batch_size=16 |
| X12 | completed (rounds stalled) | `tec5wov4528pqk1jfknl73gr` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.14` | `configs/lab/prime-td-macro-round-60-x12.toml` | choose-index plans, max_rounds=16, max_tokens=96, batch_size=16 |
| X13 | stopped (interleaved) | `z3ggo2k2op99xr57s2t3nzfp` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.16` | `configs/lab/prime-td-macro-round-60-x13.toml` | interleaved warning persisted; rounds stalled (delta 0) |
| X14 | stopped (interleaved) | `dva1t7dejvtxdk6mklmhfrlt` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.16` | `configs/lab/prime-td-macro-round-60-x14.toml` | interleaved warning persisted; rounds stalled (delta 0) |
| X15 | stopped (interleaved) | `hl0z9ab4a68ii54gx7pbzy4f` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.17` | `configs/lab/prime-td-macro-round-60-x15.toml` | interleaved warning persisted; rounds likely stalled |
| X16 | stopped (interleaved) | `pze7enmlf1vgvkuslpyv579x` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.17` | `configs/lab/prime-td-macro-round-60-x16.toml` | interleaved warning persisted; rounds likely stalled |
| X17 | completed | `dinkirjvsnwwzfx2wkmf3w9p` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x17.toml` | non-interleaved macro-round, filtered candidates, max_tokens=64 |
| X18 | completed | `emhsyysqgiayso0cga9mfgdj` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x18.toml` | non-interleaved macro-round, filtered candidates, max_tokens=96 |
| X19 | stopped (no samples) | `xzrhblbnx516kusdbm9nbfd9` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x19.toml` | candidate balance + soft cap; max_rounds=24 caused oversized completions (500s) |
| X20 | stopped (no samples) | `ypjb7kxzh701fd0ju1e2bzrn` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x20.toml` | stronger balance; max_rounds=24 caused oversized completions (500s) |
| X21 | completed (samples at step 0 only; 500s after step 10) | `umxk16fllh8t925x4jw5usp5` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x21.toml` | candidate balance + soft cap; max_rounds=18 |
| X22 | stopped (no samples) | `f4mjslk5ww900qs9xybd7hna` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x22.toml` | stronger balance; max_rounds=18, max_tokens=64 (500s) |
| X23 | completed | `ex7jobk9catq1nbaeic4zljt` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x23.toml` | stronger balance; max_rounds=16, max_tokens=48 |
| X24 | completed | `t0vh9pd4c1x413jxpnxtuky9` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x24.toml` | redo X21 with lower payload + soft cap; `trajectory_strategy=interleaved` (relaunch) |
| X25 | completed | `j7pttou1w8589wezwr7m63e0` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x25.toml` | higher build frac + upgrade caps + longer safe_explore build; `trajectory_strategy=branching` |
| X26 | stopped (500s; deleted) | `onpj7d9zujtas2gyezdc2ody` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x26.toml` | horizon test; max_rounds=18; hit upload 500s |
| X26b | stopped (500s; deleted) | `hkdt63q8gvm73zk0q80b8ws3` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x26b.toml` | horizon test retry; max_rounds=17 + tighter observation caps; hit 500s |
| X27 | stopped (500s; deleted) | `kbku4pzmgxrrlt6v00knj5hw` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x27.toml` | stronger early build bias; hit 500s |
| X26c | stopped (truncation; deleted) | `ahq5xayugi7ibo1ofgtpjv9q` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x26c.toml` | payload-tightened baseline; max_tokens=32 caused format truncation |
| X27b | stopped (truncation risk; deleted) | `mni7hyfs7tjxnh41v5ojyyob` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x27b.toml` | stopped after X26c truncation signal |
| X26d | completed | `yb058zzb4odhdz69ox2dunjz` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x26d.toml` | payload‑stable retry; max_tokens=40; tight caps; `trajectory_strategy=branching` |
| X27c | completed | `wjqmxxhozj9pokemdkupdz13` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x27c.toml` | stronger early build bias; max_tokens=40; tight caps; `trajectory_strategy=branching` |
| X28 | stopped (500s) | `qlgelc48t1hnz5qx0d5a6vf1` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x28.toml` | episode‑length probe; max_rounds=18; tight caps; `trajectory_strategy=branching` |
| X28b | completed (intermittent 500s) | `pt54lbjrcqkvi4z96od3ncfb` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x28b.toml` | episode‑length probe; batch_size=8; tighter caps; max_rounds=18 |
| X29 | stopped (500s) | `l8o0eoxn02hxbhpzh0k6z5gz` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x29.toml` | late‑phase mix nudge; max_rounds=18; payload‑reduced caps |
| X29b | completed | `bj8966t8ymaluccsvn2cwj3r` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x29b.toml` | late‑phase mix nudge + batch_size=4; tightest caps; max_rounds=18 |
| X30 | completed | `fg1tujh491j736mq9bg0evea` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x30.toml` | X26d behavioral baseline + X29b payload controls; max_rounds=18 |
| X31 | completed | `pu1v7q9evjrh8ij59kv7h2bx` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x31.toml` | X26d baseline + late‑phase mix nudge; batch_size=4; max_rounds=18 |
| X32 | completed | `ydiylivcgzume5wk445g6rj3` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x32.toml` | aggressive build bias under payload caps; batch_size=4; max_rounds=18 |
| X33 | completed | `z90upu7c2yx5a2zyh6qc1uk5` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x33.toml` | aggressive build bias + stronger safe_explore prior; batch_size=4; max_rounds=18 |
| X34 | completed | `fer1svk36hya7kih1x19lldf` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x34.toml` | late‑phase clamp (overall 0.6/3; early 0.7/2, mid 0.6/2, late 0.7/2); batch_size=4; max_rounds=18 |
| X35 | completed | `l4mzckq1j8cncl7u3qqaw71r` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x35.toml` | build availability boost (max_action_candidates=6, max_build_slots=3) with balance 0.6/3; batch_size=4; max_rounds=18 |
| X36 | completed | `zxqi7bskg48j5gx4o9g7vyno` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x36.toml` | late upgrade‑leaning w/ build floor (late min_build_frac=0.25, max_upgrade_candidates=4); batch_size=4; max_rounds=18 |
| X37 | completed | `dszrlojwleae536fzo3rimsn` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x37.toml` | **build‑leaning baseline** (late balanced); max_build_slots=3, snapshots [12,16]; batch_size=4; max_rounds=18 |
| X38 | completed | `watmtno5atltqppgwx7oq0s7` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x38.toml` | late upgrade‑leaning (late min_build_frac=0.30, max_upgrade_candidates=4) with snapshots [12,16] |
| X39 | completed | `hn1dm10r2s46pn0kosyizh6z` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x39.toml` | stronger late upgrade‑leaning (late min_build_frac=0.25, max_upgrade_candidates=5) with snapshots [12,16] |
| X40 | completed | `lu6ydpitdtw01w20le4ta3a4` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x40.toml` | late near‑parity (late min_build_frac=0.30, max_upgrade_candidates=3) with snapshots [12,16] |
| X41 | completed | `exwrtnd147o8u66vt5dnoi9f` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x41.toml` | late near‑parity (late min_build_frac=0.29, max_upgrade_candidates=4) with snapshots [12,16]; step 0 had no samples |
| X42 | completed | `d9j37xv9s07ian59ziyoz7x3` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x42.toml` | late target probe (late min_build_frac=0.30, max_upgrade_candidates=4) with snapshots [12,16] |
| X43 | completed | `k8bg50ecudykctj48ryedaoz` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x43.toml` | late target probe (late min_build_frac=0.29, max_upgrade_candidates=3) with snapshots [12,16] |
| X44 | completed | `p42ky7ibnnr52fm5yzxllhes` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x44.toml` | episode‑length probe (max_rounds=20) using X43 baseline |
| X45 | completed | `rqkultap39xvj8ngq0fyy0k1` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x45.toml` | episode‑length probe (max_rounds=22) using X43 baseline |
| X46 | stopped + deleted (500s) | `t3nlprqwjim2okcim6qwzp2d` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x46.toml` | episode‑length probe (max_rounds=24); failed on upload 500s |
| X47 | stopped + deleted (500s) | `yx7icez3h2ratiklyfy3oqru` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x47.toml` | episode‑length probe (max_rounds=26); failed on upload 500s |
| X46b | completed | `lozcb7xg62lovah0khh6xwp1` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x46b.toml` | episode‑length probe retry (max_rounds=24, batch_size=2) |
| X47b | completed | `s89xetmwo9kz12344g3ahegk` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x47b.toml` | episode‑length probe retry (max_rounds=26, batch_size=2) |
| X48 | completed | `tydn3z6mbziugdpf4rmn3i65` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x48.toml` | late-phase ratio calibration (late min_build_frac=0.295, max_upgrade_candidates=3) |
| X49 | completed (step 40 sample upload 500) | `kvbr2r2jo431owjoytccr4rw` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x49.toml` | episode-length probe (max_rounds=28, batch_size=2) carrying X48 late mix |
| X50 | completed | `sqfh70lt1nbp8n7bjmdls1iw` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x50.toml` | late-phase correction (late min_build_frac=0.32, max_upgrade_candidates=3) |
| X51 | completed (no samples; repeated sample upload 500s) | `kvyrkg3erl6yy72o5g2ljioc` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x51.toml` | episode-length probe (max_rounds=30, batch_size=2) carrying X50 late mix |
| X52 | completed | `dc364f3ugz42snhey1m9dd8s` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x52.toml` | adaptive late-phase calibration (late min_build_frac=0.35, max_upgrade_candidates=3) |
| X53 | completed (partial samples; sample upload 500s at steps 0/20/30) | `n7ryszjxt4mc2notva686x81` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x53.toml` | max_rounds=30 horizon probe with stricter observation payload caps |
| X54 | completed | `rx19kk1zx6nspnt1evtrgljf` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x54.toml` | behavior-lane calibration around adaptive late target center (late min_build_frac=0.34, max_upgrade_candidates=3) |
| X55 | completed (partial samples; sample upload 500s at steps 0/30/50) | `ixxzcocxw63ldm3dnvsyx2mi` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x55.toml` | max_rounds=30 horizon probe carrying X54 late mix with moderated payload caps |
| X56 | completed | `ve1jc2gbw4qbt156kjhrn07f` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x56.toml` | behavior-lane re-anchor to X52 target mix |
| X57 | completed | `za3gzloxpcbnen5569hweg61` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x57.toml` | reliability-first horizon probe (`batch_size=1`, snapshots [14,18]) carrying X52 late mix |
| X58 | completed | `h3r60z8yudqphntd9fzbopj9` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x58.toml` | behavior-lane refinement from X52 (late `max_upgrade_candidates=4`) |
| X59 | completed | `qufw80jvuzy04e5xm52fhq2l` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x59.toml` | reliability-first horizon progression (`max_rounds=32`, `batch_size=1`) |
| X60 | completed | `ihs7ugrp6m3t6x05raszs2fd` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x60.toml` | behavior-lane retune from X58 with stronger late build floor |
| X61 | completed | `xb1nvxg3o9zz2x34qciqrlcr` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x61.toml` | reliability-first horizon progression (`max_rounds=34`, `batch_size=1`) |
| X62 | completed | `kt8szeteixlxd9eg3i6qjd9c` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x62.toml` | behavior-lane retune from X60 (late `min_build_frac=0.39`, `max_upgrade_candidates=4`) |
| X63 | completed (step 20 samples missing; upload 500) | `rogycwef5ouzhbj3mbbr51ru` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x63.toml` | reliability-first horizon progression (`max_rounds=36`, `batch_size=1`) |
| X64 | completed | `tk4ffny3aag33tdlvtx6ib47` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x64.toml` | behavior-lane retune from X62 (late `min_build_frac=0.36`, `max_upgrade_candidates=5`) |
| X65 | completed | `emw80z7hb1123l3wqe6cqy3p` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.18` | `configs/lab/prime-td-macro-round-60-x65.toml` | reliability-first horizon progression (`max_rounds=36`, `batch_size=1`, reduced payload caps) |
| X66 | completed | `ktjauq2lx3xzm8xec03okj24` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.19` | `configs/lab/prime-td-macro-round-60-x66.toml` | behavior-lane refinement from X64 (late `min_build_frac=0.38`, `max_upgrade_candidates=4`) |
| X67 | completed (partial samples; upload 500 at steps 0/20/40) | `wpb6r4x9he1nzmxbqdfxwjfh` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.19` | `configs/lab/prime-td-macro-round-60-x67.toml` | reliability-first horizon progression (`max_rounds=38`, `batch_size=1`, X65 payload controls) |
| X68 | completed | `a7sre56kqbvb3xz48eyg1de6` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.19` | `configs/lab/prime-td-macro-round-60-x68.toml` | behavior-lane refinement from X66 (late `min_build_frac=0.37`, `max_upgrade_candidates=4`) |
| X69 | completed (step 0 samples missing; upload 500 at step 0 sample post) | `q9zubvghcurv9moam8ey9h70` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.19` | `configs/lab/prime-td-macro-round-60-x69.toml` | reliability-first horizon retry (`max_rounds=38`) with tighter observation payload caps |
| X70 | completed | `y1ko3j91odfs1sljd0ep7nds` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.19` | `configs/lab/prime-td-macro-round-60-x70.toml` | behavior-lane interpolation from X66/X68 (late `min_build_frac=0.377`, `max_upgrade_candidates=4`) |
| X71 | completed (policy-invalid: persistent truncation/format failures) | `ovhep1ox0xkif31gp0vsu12r` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.19` | `configs/lab/prime-td-macro-round-60-x71.toml` | stricter-payload horizon retry (`max_rounds=38`, `max_tokens=32`, lower observation caps, later snapshots [16,20]) |
| X72 | completed | `lh85h7erg0s1740t16pne7z4` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.19` | `configs/lab/prime-td-macro-round-60-x72.toml` | behavior-lane midpoint probe from X66/X70 (late `min_build_frac=0.378`, `max_upgrade_candidates=4`) |
| X73 | completed | `j5oydpr582dck13jblmdwq7m` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.19` | `configs/lab/prime-td-macro-round-60-x73.toml` | horizon-lane retry at `max_rounds=38` with safe token budget (`max_tokens=40`) and payload-tight observations |
| X74 | completed (step-20 partial samples: 2/4) | `o6obbmmtsyhfb3qaxny7nc5e` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.19` | `configs/lab/prime-td-macro-round-60-x74.toml` | behavior-lane center-of-band probe from X72 (late `min_build_frac=0.382`, `max_upgrade_candidates=4`) |
| X75 | completed | `xq1xk3mcui3nl84e2drdgoqm` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.19` | `configs/lab/prime-td-macro-round-60-x75.toml` | horizon-lane cap probe (`max_rounds=40`) with strict payload controls from X73/X69 |
| X76 | completed | `xqs8b45jqgl4b1n58duqfm19` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.19` | `configs/lab/prime-td-macro-round-60-x76.toml` | behavior-lane recenter from X74 toward X70/X72 (late `min_build_frac=0.379`, `max_upgrade_candidates=4`) |
| X77 | completed | `pzk2urzgf0nx1zkthpv8ex9g` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.19` | `configs/lab/prime-td-macro-round-60-x77.toml` | reliability-first horizon extension from X75 (`max_rounds=42`) with unchanged payload controls |
| X78 | completed | `x1td9k7eyllyqxrakglcqdp5` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.19` | `configs/lab/prime-td-macro-round-60-x78.toml` | behavior-lane re-anchor to X70 settings (late `min_build_frac=0.377`, `max_upgrade_candidates=4`) |
| X79 | completed (partial sample coverage; upload 500s) | `kwq5knmc1h818fynlwuazovr` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.19` | `configs/lab/prime-td-macro-round-60-x79.toml` | reliability-first horizon extension from X77 (`max_rounds=44`) with unchanged payload controls |
| X80 | completed | `uq51yx2vi3msd5r4psf12ty5` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x80.toml` | behavior-lane correction from X78 (late `min_build_frac=0.40`, `max_upgrade_candidates=3`) |
| X81 | completed | `z1v341emf1dgj7uc5c4s8x80` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x81.toml` | horizon reliability retry at `max_rounds=44` with tighter payload controls |
| X82 | completed | `dw053ie0lst239fekqrvkmif` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x82.toml` | behavior-lane correction from X80 to restore late upgrade lead (`late min_build_frac=0.33`, `late max_upgrade_candidates=4`) |
| X83 | completed (partial sample coverage; upload 500s) | `d237m4lj2rovlkiel5g9ey8d` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x83.toml` | reliability-first horizon progression from X81 (`max_rounds=46`) with unchanged payload controls |
| X84 | completed | `kazerh7ne61t9d2kcf70gknw` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x84.toml` | behavior-lane midpoint correction from X82 (`late min_build_frac=0.37`, `late max_upgrade_candidates=3`) |
| X85 | completed (one terminal non-cap delta=0) | `wadgkqmdn89kpfnrp702i9yh` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x85.toml` | reliability-first horizon retry at `max_rounds=46` with reduced payload pressure (smaller obs + later snapshots) |
| X86 | completed | `keseltdrc48o5y3a2aqghf5l` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x86.toml` | behavior-lane nudge from X84 (`late min_build_frac=0.36`, `late max_upgrade_candidates=4`) |
| X87 | completed | `gygske407ch6gm6lq7lvi5ea` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x87.toml` | reliability-first horizon extension from X85 (`max_rounds=48`, payload-safe controls unchanged) |
| X88 | completed | `kqpra14bmvcsk93v0soycqut` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x88.toml` | behavior-lane trim from X86 (late `min_build_frac=0.34`, `max_upgrade_candidates=4`) |
| X89 | completed (partial sample coverage; upload 500s) | `hbeams5x27syg1pt4vxmoogn` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x89.toml` | reliability-first horizon extension from X87 (`max_rounds=50`, payload-safe controls unchanged) |
| X90 | completed | `nuui12dr1mrym44qzt83tvqe` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x90.toml` | behavior-lane one-variable correction from X88 (`late min_build_frac=0.35`) |
| X91 | completed | `hcjjn3byus5f57074wbzn5zh` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x91.toml` | horizon-lane reliability follow-up at `max_rounds=50` with later snapshots (`[26,30]`) |
| X92 | completed | `pqugfuxz423856b0pi6ib9je` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x92.toml` | behavior-lane one-variable correction from X90 (`late min_build_frac=0.345`) |
| X93 | completed (restart after capacity stalls) | `zw58rlkeo94buj1viwrp9w6z` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x93.toml` | horizon-lane retry at `max_rounds=50` completed with full sample-step coverage (prior stalled attempts: `ihszxmubdikxgrzcyrhr319v`, `wid834u3horfi4ebhtqmafnl`, `tzzmwhxnyjekskmupsg2nn5m`) |
| X94 | completed | `nl0um7oqtgeedqzbnkenysx8` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x94.toml` | behavior-lane opposite correction from X92 (`late min_build_frac=0.347`) |
| X95 | completed | `p4k0ur16w5twtgtgji1ehifh` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x95.toml` | behavior-lane one-variable correction from X92 (`late max_upgrade_candidates=3`) |
| X96 | completed (one terminal non-cap delta=0) | `mar5xgx2179s82m6zvwcv574` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x96.toml` | horizon-lane one-variable extension from X93 restart (`max_rounds=52`) |
| X97 | completed | `nj8hsrsetm0ny5jm4fx41ba5` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x97.toml` | behavior-lane consensus follow-up from X95 (`late min_build_frac=0.338`, late cap kept at 3) |
| X98 | completed (two terminal non-cap delta=0 events) | `dp055tbj7a2p5po1frsca2yy` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x98.toml` | horizon-lane one-variable extension from X96 (`max_rounds=53`) |
| X99 | completed | `vve5v5td8r40dtp7h4os0xpk` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x99.toml` | behavior-lane one-variable micro-nudge from X90 (`late min_build_frac=0.349`, late cap kept at 4) |
| X100 | completed (no rollouts; upload 500 at sample steps 0/10/20/30/40/50) | `pes0dcr1z5dh3d04mn2m0gq7` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x100.toml` | horizon-lane one-variable extension from X98 (`max_rounds=54`) |
| X101 | completed | `osw0usw5yuvuqux2vncny1ti` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x101.toml` | behavior-lane damped opposite nudge from X99 (`late min_build_frac=0.3497`, late cap kept at 4) |
| X102 | completed (partial sample coverage; upload 500 at steps 20/50) | `dxt3sop7ti7gpwox0ntywnr3` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x102.toml` | horizon-lane reliability retry at `max_rounds=54` with payload trim (`sampling.max_tokens=36`) |
| X103 | completed | `y5d8pdi4xaap4km391mikwhc` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x103.toml` | behavior-lane one-variable nudge from X101 (`late min_build_frac=0.3495`, late cap kept at 4) |
| X104 | completed (only step-40 samples; upload 500 at steps 0/10/20/30/50) | `hncxuec1jquqmxny9zwcn9sd` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x104.toml` | horizon-lane reliability retry at `max_rounds=54` with payload trim (`sampling.max_tokens=34`) |
| X105 | completed | `sdoudjw7ta8cgx611jr2v87a` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x105.toml` | behavior-lane midpoint correction from X103 (`late min_build_frac=0.3496`, late cap kept at 4) |
| X106 | completed | `r5f574yh1bq1lnpeggca6fqq` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x106.toml` | horizon-lane boundary test from X102 (`max_rounds=53`, `sampling.max_tokens=36`) |
| X107 | completed | `btz2gniuqzm8y8yyqyqy2qid` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x107.toml` | behavior-lane reproducibility replicate of X105 (no knob changes) |
| X108 | completed (partial sample coverage; upload 500 at steps 0/30/40) | `ebj7orrhokr5pa2pc22enlx4` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x108.toml` | horizon-lane boundary retry from X106 (`max_rounds=54`, `sampling.max_tokens=36`) |
| X109 | completed | `ywp6hw463scdzzbfxqul8nad` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x109.toml` | behavior-lane stability replicate of X105 (no knob changes) |
| X110 | completed (partial sample coverage; upload 500 at step 30) | `zxk2ygd4m4e5aaij4devmeb1` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x110.toml` | horizon-lane boundary retry from X106 (`max_rounds=54`, `sampling.max_tokens=36`) |
| X111 | completed | `zves2p0f8iywrepjegv3e6ft` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x111.toml` | behavior-lane one-variable correction from X109 (`late min_build_frac=0.3494`, cap-4 base unchanged) |
| X112 | completed (partial sample coverage; upload 500 at steps 10/40/50) | `ob2sc03cqf8h5arkyz46bitp` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x112.toml` | horizon-lane exact replicate of X110 (`max_rounds=54`, `sampling.max_tokens=36`, snapshots unchanged) |
| X113 | completed | `d5uanp8ih986m2m0pd2bd2b0` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x113.toml` | behavior-lane one-variable correction from X111 (`late min_build_frac=0.3485`, cap-4 base unchanged) |
| X114 | completed | `i85bj5zwerqxiyvzn7pbny4i` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x114.toml` | horizon-lane one-variable rollback from X112 (`max_rounds=53`, `sampling.max_tokens=36`, snapshots unchanged) |
| X115 | completed | `ap7mm6wxbqige5cncf4i4bry` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x115.toml` | behavior-lane one-variable nudge from X113 (`late min_build_frac=0.3478`, cap-4 base unchanged) |
| X116 | completed | `tivxmi4wuyql4s978pvtxmg0` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x116.toml` | horizon-lane payload-control probe at cap 54 from X112 (snapshot rounds `[26,30] -> [30,34]`, `sampling.max_tokens=36`) |
| X117 | completed | `n0xc9w6thqky8bkx9b290ivy` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x117.toml` | behavior-lane one-variable opposite nudge from X115 (`late min_build_frac=0.3480`, cap-4 base unchanged) |
| X118 | completed | `dkcly2xivrrjxs87s6h0utm9` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x118.toml` | horizon-lane exact reliability replicate of X116 at cap 54 (`sampling.max_tokens=36`, snapshots `[30,34]`) |
| X119 | completed | `xxjx3f6i1is1wja0yhlua3ou` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x119.toml` | behavior-lane one-variable micro-nudge from X117 (`late min_build_frac=0.3479`, cap-4 base unchanged) |
| X120 | completed | `wfnfguf00es2neh69iff3efc` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x120.toml` | horizon-lane strict cap-54 sentinel replicate of X118 controls (`sampling.max_tokens=36`, snapshots `[30,34]`) |
| X121 | completed | `tznkzsc5219a6qjv2rq1zayr` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x121.toml` | behavior-lane exact replicate of X117 to de-noise X119 variance (`late min_build_frac=0.3480`) |
| X122 | completed | `teqva7wjcdavfaz5rsene07b` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x122.toml` | horizon-lane exact sentinel replicate of X120 at cap 54 (`sampling.max_tokens=36`, snapshots `[30,34]`) |
| X123 | completed | `iv8cdu0fnwig2smqxj4u6jz1` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x123.toml` | behavior-lane one-variable correction from X121 (`late min_build_frac=0.3478`) |
| X124 | completed (three terminal non-cap delta=0 events) | `ueykeiomaqy4xas1jjsu5mib` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x124.toml` | horizon-lane one-variable survivability nudge from X122 (`late min_build_frac=0.50`, cap 54 controls unchanged) |
| X125 | queued/running (fresh restart after deleting failed attempts) | `w7yqulklo2vose7007aayn6w` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x125.toml` | behavior-lane exact reproducibility replicate of X123 (deleted prior failed backoff attempts before relaunch) |
| X126 | queued/running (fresh restart after deleting failed attempts) | `ekdy40gqzg173v0dbj92oks4` | `Qwen/Qwen3-4B-Instruct-2507` | `kbediako/prime-td-env` | `0.2.22` | `configs/lab/prime-td-macro-round-60-x126.toml` | horizon-lane exact reproducibility replicate of X124 (deleted prior failed backoff attempts before relaunch) |

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
- **Run C** keeps B settings but sets `dataset.rollout_steps=0` to remove tower-seeded prompts.
- **Run D** keeps C settings but lowers `step_penalty` back to `0.1`.
- **Run E** uses `rollout_steps=1` (single-step curriculum) with B reward settings.
- **Run F** uses `rollout_steps=1` with lower `step_penalty=0.1`.

## Eval Protocol (fixed + deterministic)

- **Train seeds:** `0..63` (64 examples)
- **Held-out eval seeds:** `1000..1049` (50 examples)
- **Random suite:** `2000..2019` (20 examples)
- **Metrics:** avg_round, win_rate, lives_remaining, invalid_json_rate, invalid_action_rate, truncation_rate
- **Eval command:** see “Repro commands” in this doc once run completes

## Metrics (placeholders)

| Run | Avg Round | Win Rate | Avg Lives | Avg Reward | Invalid JSON | Invalid Action | Truncation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A (early) | TBD | TBD | TBD | 92.17 | 0.00 | TBD | 0.00 |
| A (late) | TBD | TBD | TBD | 103.58 | 0.00 | TBD | 0.00 |
| B (early) | TBD | TBD | TBD | 25.62 | 0.00 | TBD | 0.00 |
| B (late) | TBD | TBD | TBD | 0.05 | 0.00 | TBD | 0.00 |

## Rollout Snippets (placeholders)

1) **Snippet A1 (step 0, reward 0.4):** `{"type":"build","tower_type":"dart","x":8,"y":3}`
   - **Demonstrates:** format-stable build action at episode start.
2) **Snippet A2 (step 40, reward 110.4):** `{"type":"start_round"}`
   - **Demonstrates:** high reward for advance action once towers are seeded in prompt.
3) **Snippet A3 (step 70, reward 110.4):** `{"type":"start_round"}`
   - **Demonstrates:** continued reliance on advance action; action diversity to monitor.
4) **Snippet B1 (step 0, reward 0.05):** `{"type":"build","tower_type":"dart","x":3,"y":2}`
   - **Demonstrates:** format-stable build action in Run B early phase.
5) **Snippet B2 (step 70, reward 0.05):** `{"type":"build","tower_type":"dart","x":3,"y":1}`
   - **Demonstrates:** Run B remained build-heavy with low reward late in training.

## Known Observations / Open Checks

- Run A action mix (steps 0/40/70): `start_round=17`, `build=7`, `invalid_json_rate=0.0`. Likely driven by `rollout_steps=2` seeding towers in the prompt (so “advance” is locally good). We will verify whether this reduces build/upgrade diversity and adjust in later runs if needed.
- Run B action mix (steps 0/40/70): `build=23`, `start_round=1`, `invalid_json_rate=0.0`. Late-phase reward collapsed to ~0.05; needs follow-up run or config tweak if this persists.
- Runs K/L (auto-advance, prep budgets) were **build-only** in sampled rollouts (8/8 build at steps 20/40), with prompts stuck at **round=1** and prep remaining > 0. This suggests rollout_steps was too short to reach reward-informative “last prep action before wave” states. M/N addressed this by pushing rollout_steps=9 and reducing build-slot explosion.
- Runs M/N (round ~4–5, prep remaining mostly 1) started with mixed actions but **collapsed to start_round-only by step ~40**, indicating the rubric still only credits round simulation.
- Run O (credit fix + random policy) still **collapsed to start_round-only by step ~40**; reward/mean last ~132.28 and rollouts showed start_round dominance (steps 40+).
- Run P (credit fix + bootstrap) **collapsed to a single action type** (build-only early, upgrade-only mid) and ended with negative reward/mean (~-5.04), suggesting prompts were too late/hard for single-turn actions.
- Runs Q/R target decision-relevant prompts via `dataset.policy=noop_then_start` (round ~4–5, prep remaining=1); R additionally gates `start_round` to the last prep action to remove the safe-action attractor.
- Run Q (v0.2.7) collapsed to **start_round-only** by step 40 (action mix: step 0 build-only, steps 40/70 start_round-only). Reward/mean fell from ~114.47 (steps 0–3 avg) to ~21.62 (steps 70+ avg); last reward/mean ~21.74.
- Run R (v0.2.7) avoided start_round but stayed **build-only** across steps 0/40/70. Reward/mean remained high: ~112.92 (steps 0–3 avg), ~93.70 (mid), ~121.96 (steps 70+ avg); last reward/mean ~132.18.
- In sampled rollouts (steps 0/40/70), both Q/R prompts were consistently `prep_actions_remaining=1` and `round=5` (with `last_round.round=4`), indicating the rollout targeting is working but action diversity remains limited.
- Run S (v0.2.10) started with a **build/upgrade mix** (step 0: upgrade=5, build=3) but collapsed to **build-only** by step 40/70. Reward/mean stayed high (min ~103.29, max ~139.40, last ~136.40) with `_format_reward=1.0`.
- Run T (v0.2.10, cash-scarce) collapsed to **upgrade-only** across steps 0/40/70. Reward/mean was lower (min ~12.90, max/last ~56.40) with `_format_reward=1.0`.
- Run U (v0.2.11) logged **dominance diagnostic** showing upgrades were optimal in many prompts (best_by_type: upgrade=361, build=73, start_round=24, sell=182; build_vs_upgrade: build=73, upgrade=49). Despite this, rollouts still **collapsed to start_round** by step 40/70 (step 0: upgrade=5, start_round=3; step 40/70: start_round=8). Reward/mean min ~119.81, max ~351.90, last ~227.65; `_format_reward=1.0`, errors 0.
- Run V (v0.2.11, macro-round) showed **short episodes** (`metrics/num_turns` mean ~2.0). Rollouts at steps 0/40 produced **empty plans** (0 actions), while step 70 produced **2-action plans** (build+upgrade). Reward/mean min ~-422.90, max ~1367.19, last ~284.60; macro reward min ~-423.40, max ~1366.69, last ~284.10; format reward ranged -1..1 (last 1.0). One trajectory showed a **round jump to 12 after a single plan** with lives <= 0, which suggests the macro-round env in this run may still be advancing multiple rounds per plan (pre-fix env build). Treat V as **non-diagnostic** until rerun on the fixed env.
- Run W (v0.2.13, SingleTurn; decision filter disabled) produced **decision-relevant snapshots** (round 15/20, prep_remaining=1, towers present), but reward signal was **format-only** (`reward/mean ≈ 0.5`, `_reward_from_action ≈ 0.0`, `_regret_metric ≈ 0.0`), confirming SingleTurn reward-flat behavior. Treat W as the **final SingleTurn diagnostic**.
- Run X (v0.2.13, macro-round) returned **0 rollout samples** (no prompt uploads), so no action-mix or plan diagnostics were captured; rerun required.
- X note (infra): Prime CLI reported HTTP 500s on completion uploads; likely **payload too large**. Mitigation: lower `sampling.max_tokens` (and/or `dataset.rollouts_per_example`) to reduce completion size before rerun.
- Run X2 (v0.2.13, macro-round rerun) still shows **0 rollout samples**. Logs show repeated HTTP 500s on sample uploads; metrics report very large completion lengths (~25–31k tokens/sample) and `is_truncated≈1`, reinforcing the payload-size hypothesis.
- Run X3 (v0.2.13, macro-round) restarted with reduced payload settings (`max_tokens=64`, `rollouts_per_example=1`, smaller observation caps) but still hit HTTP 500s on sample uploads; no samples captured.
- Run X4 (v0.2.13, macro-round) produced samples but **all completions were truncated** (`is_truncated=1.0`) and **format reward = -1** across rollouts, so plans were invalid and round-jump checks were not possible. Payload size is under control; next retry should increase `max_tokens` modestly (e.g., 48) while keeping prompt caps tight.
- Run X5 (v0.2.13, macro-round) produced samples but **format validity remained low** (only 3/48 valid plans; format reward mostly -1). Treat X5 as **format-invalid**.
- Run X6 (v0.2.13, macro-round) produced **valid plans** (48/48) with 1–2 actions and a build+upgrade mix, but **macro-round invariant still fails**: simulated round delta was **0 in 31/48** samples (delta=1 in 17/48). Most delta=0 samples were **round=15 with max_rounds=15**, which truncates before a +1 increment; remaining failures were driven by invalid actions (`insufficient_cash`, `unknown_tower`). Episodes did not clearly lengthen over training (num_turns/mean ~3.47 early vs ~3.48 late). Reward stayed stable without absurd spikes.
- Next macro-round runs (X7/X8) will enforce **candidate-index plans** and set `max_rounds` above snapshot rounds to validate the +1 round invariant without truncation.
- Runs X7–X10 (candidate-index, max_rounds=20) **failed to upload samples** (HTTP 500) despite smaller batches; metrics show large completion lengths and higher num_turns, so payload size is still too large. Likely driver: **longer episodes from max_rounds=20**; set `max_rounds=16` and re-run after publishing the choose-index env to reduce turn count and payload size.
- Run X11 (v0.2.14, max_rounds=16, max_tokens=64) produced samples with **valid plans** and no truncation, but **rounds did not advance** in trajectories (round delta = 0 across all adjacent turns; e.g., round 15 → 15). Plans were always length 2 and **upgrade‑dominant**; `choose_out_of_range` appeared mid/late. Reward/mean was stable (min ~589.7, max ~1496.1, last ~1171.2). **Not successful** against macro-round criteria.
- Run X12 (v0.2.14, max_rounds=16, max_tokens=96) showed the same **round‑stall** pattern (delta 0 across turns), fixed plan length (2), and upgrade‑heavy actions with growing `choose_out_of_range`. Reward/mean stable (min ~595.9, max ~1564.2, last ~1306.9). **Not successful** against macro-round criteria.
- Run X17 (v0.2.18, max_rounds=16, max_tokens=64) **passed round‑delta checks** when parsing all turns (delta_round=1 after turn 1 across steps 0/10/20/30/40/50). Plan length remained 2, and action mix was **upgrade‑dominant** (e.g., step 50: upgrade=86, build=9) matching a heavily upgrade‑skewed candidate pool (step 50: upgrade=598 vs build=54). Reward/mean min ~871.91, max/last ~1524.57; format reward dipped to 0.875 early but ended 1.0.
- Run X18 (v0.2.18, max_rounds=16, max_tokens=96) **passed round‑delta checks** when parsing all turns (delta_round=1 after turn 1 across steps 0/10/20/30/40/50). Plan length was mostly 2, action mix stayed **upgrade‑dominant** (e.g., step 50: upgrade=73, build=4) with a candidate pool skew (step 50: upgrade=312 vs build=65). Reward/mean min ~805.71, max ~1591.90, last ~1007.27; format reward dipped to ~0.893 late.
- Both X17/X18: interleaved warnings were present in logs but round deltas were correct; episode length cannot improve with max_rounds=16 (rollouts already reach 16).
- Run X19/X20 (v0.2.18, max_rounds=24) hit HTTP 500s with **no samples**; completion lengths were ~19–20k tokens and `num_turns≈13`, indicating payload size/timeouts. Stopped and replaced with X21/X22 (max_rounds=18).
- Run X21 (v0.2.18, max_rounds=18, max_tokens=96) produced samples **only at step 0**; logs show HTTP 500s after step 10, so no later samples were uploaded. Step 0 passed round‑delta checks; plan length mostly 2; action mix still upgrade‑dominant but with higher build presence (build=23, upgrade=65). Candidate pool skew remained (build=127 vs upgrade=390). Reward/mean min ~1547.40, max ~2038.71, last ~1950.13; format reward dipped to ~0.882 late.
- Run X22 (v0.2.18, max_rounds=18, max_tokens=64) hit HTTP 500s with **no samples**; stopped and replaced with X23 (max_rounds=16, max_tokens=48).
- Run X23 (v0.2.18, max_rounds=16, max_tokens=48) produced samples at steps 0/10/20/30/40/50. Round‑delta checks **passed** across all turns; plan length mostly 2. Action mix improved with build presence across phases (e.g., step 40: build=32, upgrade=56; step 50: build=29, upgrade=49), and candidate balance increased build availability (step 50 candidates: build=115 vs upgrade=315). Reward/mean min ~796.02, max ~1524.70, last ~1473.81; format reward reached 1.0. Episode length still saturates at max_rounds=16, so “longer episodes” cannot be observed yet.
- Run X24 (v0.2.18, interleaved, max_rounds=16, max_tokens=48) completed with samples at steps 0/10/20/30/40/50. Round‑delta checks **passed** across all turns (0 failures). Plan length was almost always 2 (one 0‑action plan at step 30). Action mix stayed **upgrade‑dominant** with some build (aggregate: upgrade=357, build=72, noop=17), matching a candidate pool still skewed toward upgrades (aggregate: upgrade=2163 vs build=377). By round phase: early build 13 vs upgrade 63; mid build 11 vs upgrade 65; late build 48 vs upgrade 229. Reward/mean min ~1008.76, max ~1524.70, last ~1060.16. No truncation or 500s observed.
- Run X25 (v0.2.18, branching, max_rounds=16, max_tokens=48) completed with samples at steps 0/10/20/30/40/50. Round‑delta checks **passed** across all turns (0 failures). Plan length was consistently 2. Action mix showed **higher build presence** vs X24 (aggregate: upgrade=294, build=181, noop=13), aligned with a more build‑balanced candidate pool (aggregate: upgrade=1259 vs build=666). By round phase: early build 42 vs upgrade 53; mid build 46 vs upgrade 53; late build 93 vs upgrade 188. Reward/mean min ~1066.09, max ~1471.19, last ~1237.00. No truncation or 500s observed.
- Run X26d (v0.2.18, branching, max_rounds=16, max_tokens=40) completed with samples at steps 0/10/20/30/40/50. Round‑delta checks **passed** across all turns (0 failures; 0 missing). Plan length almost always 2 (231/232), invalid_plan=0. Action mix showed **build‑heavy early/mid** with late mixed: early build 51 vs upgrade 36; mid build 54 vs upgrade 32; late build 103 vs upgrade 178. Aggregate actions: build=208, upgrade=246, noop=7 (choose_out_of_range=2). Candidate pool aggregate: build=499 vs upgrade=927. Reward/mean min ~860.97, max ~1562.59, last ~1215.25; format reward remained 1.0; truncation 0. No 500s observed. Episode length improvement still **not measurable** at max_rounds=16.
- Run X27c (v0.2.18, branching, max_rounds=16, max_tokens=40) completed with samples at steps 0/10/20/30/40/50. Round‑delta checks **passed** across all turns (0 failures; 0 missing). Plan length mostly 2 (208/224), with a few 1‑action plans (15) and one 0‑action plan; invalid_plan=0. Action mix was **balanced overall** (build=217, upgrade=213, noop=1). By phase: early build 51 vs upgrade 25; mid build 53 vs upgrade 14; late mixed but upgrade‑dominant (upgrade 174 vs build 113). Candidate pool aggregate: build=394 vs upgrade=815. Reward/mean min ~809.27, max ~1572.91, last ~1391.95; format reward min ~0.893, last 1.0; truncation 0; completion_len/mean max ~7236.67, last ~6161.25. All rollouts ended at round 16 (cap), so episode‑length improvement is **not measurable** yet. No 500s observed.
- Run X28 (v0.2.18, max_rounds=18) stopped after HTTP 500 on sample upload at step 1; replaced by X28b.
- Run X28b (v0.2.18, max_rounds=18, batch_size=8) completed with samples logged at steps 0/10/20/30/40/50, but rollouts at steps 20/30 returned **0 samples** (despite logged uploads). Round‑delta checks **passed** across all parsed turns (0 failures; 0 missing). Plan length mostly 2 (213/216) with a few 1‑action plans (3); invalid_plan=0. Action mix was **upgrade‑dominant** (upgrade=341, build=81, noop=7), aligned with an upgrade‑heavy candidate pool (upgrade=813 vs build=229). By phase: early build 22 vs upgrade 31; mid build 12 vs upgrade 43; late build 47 vs upgrade 267. Reward/mean min ~1439.00, max ~2130.05, last ~1749.45; format reward 1.0; truncation 0. Episodes saturated at round 18 (cap), so length improvement is **not measurable**. 500s occurred at steps 21/31 (sample upload failures).
- Run X29 (v0.2.18, max_rounds=18) stopped after HTTP 500 on sample upload at step 1; replaced by X29b.
- Run X29b (v0.2.18, max_rounds=18, batch_size=4) completed with samples at steps 0/10/20/30/40/50. Round‑delta checks **passed** across all parsed turns (0 failures; 0 missing). Plan length mostly 2 (154/156) with a few 1‑action plans (2); invalid_plan=0. Action mix remained **upgrade‑dominant** but with improved build presence (upgrade=192, build=116, noop=2) alongside a less skewed candidate pool (upgrade=366 vs build=190). By phase: early build 17 vs upgrade 18 (near‑balanced), mid build 14 vs upgrade 22, late build 85 vs upgrade 152 (still upgrade‑leaning). Reward/mean min ~1402.25, max ~2276.70, last ~1843.60; format reward 1.0; truncation 0. Episodes saturated at round 18 (cap), so length improvement is **not measurable**. No 500s observed.
- Run X30 (v0.2.18, max_rounds=18, batch_size=4) completed with samples at steps 0/10/20/30/40/50. Round‑delta checks **passed** across all parsed turns (0 failures; 0 missing). Plan length mostly 2 (169/176) with a few 1‑action plans (7); invalid_plan=0. Action mix was **upgrade‑dominant** (upgrade=271, build=72, noop=2) with a heavily upgrade‑skewed candidate pool (upgrade=621 vs build=132). By phase: early build 21 vs upgrade 29; mid build 10 vs upgrade 46; late build 41 vs upgrade 196 — **plan quality failed** (not build‑heavy early; not mixed mid/late). Reward/mean min ~1440.75, max ~2292.70, last ~2043.90; format reward 1.0; truncation 0. Episodes saturated at round 18 (cap), so length improvement is **not measurable**. No 500s observed.
- Run X31 (v0.2.18, max_rounds=18, batch_size=4) completed with samples at steps 0/10/20/30/40/50. Round‑delta checks **passed** across all parsed turns (0 failures; 0 missing). Plan length mostly 2 (165/168) with a few 1‑action plans (3); invalid_plan=0. Action mix remained **upgrade‑dominant** but improved build presence vs X30 (upgrade=217, build=114, noop=2) alongside a less skewed candidate pool (upgrade=439 vs build=193). By phase: early build 22 vs upgrade 25 (near‑balanced), mid build 19 vs upgrade 29, late build 73 vs upgrade 163 — **plan quality still fails** (mid/late upgrade‑leaning). Reward/mean min ~1414.00, max ~2275.20, last ~1831.85; format reward 1.0; truncation 0. Episodes saturated at round 18 (cap), so length improvement is **not measurable**. No 500s observed.
- Run X32 (v0.2.18, max_rounds=18, batch_size=4, aggressive build bias) completed with samples at steps 0/10/20/30/40/50. Round‑delta checks **passed** across all parsed turns (0 failures; 0 missing). Plan length mostly 2 (136/140) with a few 1‑action plans (4); invalid_plan=0. Action mix remained **upgrade‑dominant** (upgrade=184, build=86, noop=6) with a moderately less skewed candidate pool (upgrade=289 vs build=171). By phase: early build 7 vs upgrade 12; mid build 5 vs upgrade 12; late build 74 vs upgrade 160 — **plan quality fails** (early/mid not build‑heavy; late upgrade‑dominant). Reward/mean min ~1442.75, max ~2266.45, last ~1859.35; format reward 1.0; truncation 0. Episodes saturated at round 18 (cap), so length improvement is **not measurable**. No 500s observed.
- Run X33 (v0.2.18, max_rounds=18, batch_size=4, aggressive build bias + stronger safe_explore prior) completed with samples at steps 0/10/20/30/40/50. Round‑delta checks **passed** across all parsed turns (0 failures; 0 missing). Plan length mostly 2 (156/168) with a higher share of 1‑action plans (12); invalid_plan=0. Action mix remained **upgrade‑dominant** (upgrade=218, build=106) with a skewed candidate pool (upgrade=341 vs build=144). By phase: early build 37 vs upgrade 10 (**build‑heavy early**), mid build 21 vs upgrade 16 (**build‑leaning mid**), late build 48 vs upgrade 192 (**late upgrade‑dominant**) — **partial plan quality** (early/mid pass, late fail). Reward/mean min ~1394.00, max ~2262.70, last ~1831.85; format reward 1.0; truncation 0. Episodes saturated at round 18 (cap), so length improvement is **not measurable**. No 500s observed.
- Run X34 (v0.2.18, max_rounds=18, batch_size=4, late‑phase clamp) completed with samples at steps 0/10/20/30/40/50. Round‑delta checks **passed** across all parsed turns (0 failures; 0 missing). Plan length mix: 1‑action 46, 2‑action 130; invalid_plan=0. Action mix was near‑balanced overall (upgrade=168, build=138), but **late phase remains upgrade‑dominant**. By phase: early build 44 vs upgrade 12 (**build‑heavy early**), mid build 35 vs upgrade 9 (**build‑heavy mid**), late build 59 vs upgrade 147 (**late upgrade‑dominant**) — **partial plan quality** (late fail). Candidate pool aggregate: build=137 vs upgrade=204 (noop=176). Reward/mean min ~1409.75, max ~2250.95, last ~1665.55; format reward 1.0; truncation 0. Episodes saturated at round 18 (cap), so length improvement is **not measurable**. No 500s observed.
- Run X35 (v0.2.18, max_rounds=18, batch_size=4, build‑availability boost) completed with samples at steps 0/10/20/30/40/50. Round‑delta checks **passed** across all parsed turns (0 failures; 0 missing). Plan length mostly 2 (160/176) with some 1‑action plans (16); invalid_plan=0. Action mix improved build presence (upgrade=177, build=148, noop=11), but **late phase is still upgrade‑dominant**. By phase: early build 36 vs upgrade 18 (**build‑leaning early**), mid build 31 vs upgrade 17 (**build‑leaning mid**), late build 81 vs upgrade 142 (**late upgrade‑dominant**) — **partial plan quality** (late fail). Candidate pool aggregate: build=239 vs upgrade=341 (noop=176). Reward/mean min ~1443.50, max ~2259.70, last ~1613.55; format reward 1.0; truncation 0. Episodes saturated at round 18 (cap), so length improvement is **not measurable**. No 500s observed.
- Run X36 (v0.2.18, max_rounds=18, batch_size=4, late upgrade‑leaning w/ build floor) completed with samples at steps 0/10/20/30/40/50. Round‑delta checks **passed** across all parsed turns (0 failures; 0 missing). Plan length mostly 2 (160/172) with some 1‑action plans (12); invalid_plan=0. Action mix was **upgrade‑dominant** (upgrade=267, build=64, noop=1) with a highly upgrade‑skewed candidate pool (upgrade=539 vs build=139). By phase: early build 28 vs upgrade 20 (**build‑leaning early**), mid build 14 vs upgrade 30 (**upgrade‑leaning mid**), late build 22 vs upgrade 217 (**late heavily upgrade‑dominant**) — **plan quality fails** (late build presence too low under new “upgrade‑leaning but still build” target). Reward/mean min ~1398.25, max ~2279.95, last ~2073.90; format reward 1.0; truncation 0. Episodes saturated at round 18 (cap), so length improvement is **not measurable**. No 500s observed.
- Run X37 (v0.2.18, max_rounds=18, batch_size=4, build‑leaning baseline with later snapshots [12,16]) completed with samples at steps 0/10/20/30/40/50. Round‑delta checks **passed** across all parsed turns (0 failures; 0 missing). Plan length mostly 2 (114/116) with very few 1‑action plans (2); invalid_plan=0. Action mix was **build‑leaning overall** (build=126, upgrade=96, noop=8) with a less skewed candidate pool (build=281 vs upgrade=365). By phase (note: rounds start at 12, so “early” not observed): mid build 35 vs upgrade 8 (**build‑leaning mid**), late build 91 vs upgrade 88 (**late balanced**) — **baseline for build‑leaning behavior** (retain as fallback). Reward/mean min ~899.90, max ~1912.85, last ~1373.75; format reward 1.0; truncation 0. Episodes saturated at round 18 (cap), so length improvement is **not measurable**. No 500s observed.
- Run X38 (v0.2.18, max_rounds=18, batch_size=4, late upgrade‑leaning w/ build floor, snapshots [12,16]) completed with samples at steps 0/10/20/30/40/50. Round‑delta checks **passed** across all parsed turns (0 failures; 0 missing). Plan length was always 2 (124/124); invalid_plan=0. Action mix was **slightly upgrade‑leaning overall** (upgrade=131, build=113, noop=4) with a moderately upgrade‑skewed candidate pool (upgrade=426 vs build=283). By phase (rounds start at 12): mid build 38 vs upgrade 13 (**build‑leaning mid**), late build 75 vs upgrade 118 (**late upgrade‑leaning with build presence**) — **plan quality passes** under updated late‑phase target. Reward/mean min ~900.15, max ~1874.85, last ~1613.30; format reward 1.0; truncation 0. Episodes saturated at round 18 (cap), so length improvement is **not measurable**. No 500s observed.
- Run X39 (v0.2.18, max_rounds=18, batch_size=4, stronger late upgrade‑leaning, snapshots [12,16]) completed with samples at steps 0/10/20/30/40/50. Round‑delta checks **passed** across all parsed turns (0 failures; 0 missing). Plan length was always 2 (120/120); invalid_plan=0. Action mix was **upgrade‑leaning overall** (upgrade=134, build=97, noop=9) with a more upgrade‑skewed candidate pool (upgrade=504 vs build=282). By phase: mid build 34 vs upgrade 13 (**build‑leaning mid**), late build 63 vs upgrade 121 (**late upgrade‑leaning with reduced build presence**) — **plan quality passes** (build still present late). Reward/mean min ~912.65, max ~1839.60, last ~1380.75; format reward 1.0; truncation 0. Episodes saturated at round 18 (cap), so length improvement is **not measurable**. No 500s observed.
- Run X40 (v0.2.18, max_rounds=18, batch_size=4, late near‑parity, snapshots [12,16]) completed with samples at steps 0/10/20/30/40/50. Round‑delta checks **passed** across all parsed turns (0 failures; 0 missing). Plan length was always 2 (124/124); invalid_plan=0. Action mix was **build‑leaning overall** (build=138, upgrade=104, noop=6) with a near‑balanced candidate pool (build=285 vs upgrade=322). By phase (rounds start at 12): mid build 39 vs upgrade 13 (**build‑leaning mid**), late build 99 vs upgrade 91 (**late slightly build‑leaning**) — **plan quality partial** (late not upgrade‑leaning). Reward/mean min ~904.15, max ~1881.35, last ~932.15; format reward 1.0; truncation 0. Episodes saturated at round 18 (cap), so length improvement is **not measurable**. No 500s observed.
- Run X41 (v0.2.18, max_rounds=18, batch_size=4, late near‑parity, snapshots [12,16]) completed with samples at steps 10/20/30/40/50 (**step 0 had no samples**). Round‑delta checks **passed** across all parsed turns (0 failures; 0 missing). Plan length mostly 2 (103/104) with one 1‑action plan; invalid_plan=0. Action mix was **upgrade‑leaning overall** (upgrade=124, build=83) with an upgrade‑skewed candidate pool (upgrade=350 vs build=214). By phase: mid build 29 vs upgrade 14 (**build‑leaning mid**), late build 54 vs upgrade 110 (**late upgrade‑leaning with build present**) — **plan quality passes** under updated late‑phase target. Reward/mean min ~891.15, max ~1867.10, last ~1192.70; format reward 1.0; truncation 0. Episodes saturated at round 18 (cap), so length improvement is **not measurable**. No 500s observed.
- Run X42 (v0.2.18, max_rounds=18, batch_size=4, late target probe, snapshots [12,16]) completed with samples at steps 0/10/20/30/40/50. Round‑delta checks **passed** across all parsed turns (0 failures; 0 missing). Plan length mostly 2 (122/124) with two 1‑action plans; invalid_plan=0. Action mix was **upgrade‑leaning overall** (upgrade=143, build=102, noop=1) with an upgrade‑skewed candidate pool (upgrade=413 vs build=254). By phase (rounds start at 12): mid build 32 vs upgrade 18 (**build‑leaning mid**), late build 70 vs upgrade 125 (**late upgrade‑leaning with build present**) — **plan quality passes** under the “late upgrade ~10–15% higher” target. Reward/mean min ~910.40, max ~1891.35, last ~1866.35; format reward 1.0; truncation 0. Episodes saturated at round 18 (cap), so length improvement is **not measurable**. No 500s observed.
- Run X43 (v0.2.18, max_rounds=18, batch_size=4, late target probe, snapshots [12,16]) completed with samples at steps 0/10/20/30/40/50. Round‑delta checks **passed** across all parsed turns (0 failures; 0 missing). Plan length was always 2 (132/132); invalid_plan=0. Action mix was **near‑balanced overall** (upgrade=129, build=127, noop=8) with a slightly upgrade‑skewed candidate pool (upgrade=352 vs build=292). By phase: mid build 44 vs upgrade 16 (**build‑leaning mid**), late build 83 vs upgrade 113 (**late upgrade‑leaning with build present**) — **plan quality passes** under the “late upgrade ~10–15% higher” target. Reward/mean min ~896.40, max ~1861.35, last ~1667.55; format reward 1.0; truncation 0. Episodes saturated at round 18 (cap), so length improvement is **not measurable**. No 500s observed.
- Run X44 (v0.2.18, max_rounds=20, batch_size=4, episode‑length probe) completed with samples at steps 0/10/20/30/40/50. Round‑delta checks **passed** across all parsed turns (0 failures; 0 missing). Plan length was always 2 (148/148); invalid_plan=0. Action mix was **upgrade‑leaning overall** (upgrade=166, build=126, noop=4) with an upgrade‑skewed candidate pool (upgrade=407 vs build=296). By phase (rounds start at 12): mid build 21 vs upgrade 7 (**build‑leaning mid**), late build 105 vs upgrade 159 (**late upgrade‑leaning with build present**) — **plan quality passes** under the target. Reward/mean min ~1615.50, max ~2540.70, last ~2344.90; format reward 1.0; truncation 0. Episodes ended at round **20** (cap), so episode length still **not measured beyond cap**. No 500s observed.
- Run X45 (v0.2.18, max_rounds=22, batch_size=4, episode‑length probe) completed with samples at steps 0/10/20/30/40/50. Round‑delta checks **passed** across all parsed turns (0 failures; 0 missing). Plan length was always 2 (220/220); invalid_plan=0. Action mix was **upgrade‑dominant overall** (upgrade=293, build=136, noop=11) with a heavily upgrade‑skewed candidate pool (upgrade=587 vs build=334). By phase: mid build 41 vs upgrade 11 (**build‑leaning mid**), late build 95 vs upgrade 282 (**late strongly upgrade‑dominant**) — **plan quality fails** (late upgrades exceed target; build presence too low). Reward/mean min ~2372.10, max ~3336.05, last ~2583.90; format reward 1.0; truncation 0. Episodes ended at round **22** (cap), so episode length still **not measured beyond cap**. No 500s observed.
- Run X46/X47 (v0.2.18, max_rounds=24/26, batch_size=4) were stopped and deleted after recurring HTTP 500 upload failures; rerun as X46b/X47b with `batch_size=2`.
- Run X46b (v0.2.18, max_rounds=24, batch_size=2, branching) completed with samples at steps 0/10/20/30/40/50. Parsed all rollouts and all turns: 12 samples, plan length always 2 (132/132), invalid_plan=0, choose_out_of_range=0. Action mix was **upgrade‑dominant** with build presence (upgrade=186, build=75, noop=3), and the candidate pool remained upgrade‑skewed (upgrade=353 vs build=181; noop candidates=132). By phase: mid build 17 vs upgrade 7; late build 58 vs upgrade 179 (**late upgrade‑dominant**). Round progression: all non-cap checks passed; the only `delta_round=0` observations occurred at round 24 cap (12/120 checks). Reward/mean min ~3055.2, max ~4156.9, last ~3558.8; format reward 1.0; truncation 0; completion_len/mean min ~9716.5, max ~15088.0, last ~12207.5. No upload 500s; logs showed transient server sync/model-query connection errors that self-recovered.
- Run X47b (v0.2.18, max_rounds=26, batch_size=2, branching) completed with samples at steps 0/10/20/30/40/50. Parsed all rollouts and all turns: 12 samples, plan length always 2 (148/148), invalid_plan=0, choose_out_of_range=0. Action mix stayed **more upgrade‑dominant** than X46b (upgrade=214, build=69, noop=13), with an upgrade‑skewed candidate pool (upgrade=391 vs build=198; noop candidates=148). By phase: mid build 9 vs upgrade 6; late build 60 vs upgrade 208 (**late strongly upgrade‑dominant**). Round progression: all non-cap checks passed; the only `delta_round=0` observations occurred at round 26 cap (12/136 checks). Reward/mean min ~2810.7, max ~4936.0, last ~4844.5; format reward 1.0; truncation 0; completion_len/mean min ~9596.0, max/last ~18086.0. No upload 500s; metrics recorded one transient model connection error at step 33 (`error/mean=0.5`) that self-recovered.
- Run X48 (v0.2.18, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50. Parsed all rollouts and all turns: 24 samples, plan length always 2 (124/124), invalid_plan=0, choose_out_of_range=2. Action mix was near parity overall (upgrade=126, build=119, noop=1) with a moderately upgrade‑skewed candidate pool (upgrade=333 vs build=270; noop candidates=124). By phase: mid build 61 vs upgrade 43 (**build‑leaning mid**), late build 58 vs upgrade 83 (**late upgrade‑leaning**, ~43% more upgrades than builds). Round progression: all non-cap checks passed; the only `delta_round=0` observations occurred at round 18 cap (24/100 checks). Reward/mean min ~911.9, max ~1881.35, last ~1161.2; format reward 1.0; truncation 0; completion_len/mean min ~2679.25, max ~7687.0, last ~4003.5. No upload 500s observed.
- Run X49 (v0.2.18, max_rounds=28, batch_size=2, branching) completed with samples at steps 0/10/20/30/50 (step 40 sample upload failed). Parsed all available rollouts and all turns: 10 samples, plan length always 2 (146/146), invalid_plan=0, choose_out_of_range=0. Action mix became strongly upgrade‑dominant (upgrade=238, build=54) with an upgrade‑skewed candidate pool (upgrade=380 vs build=190; noop candidates=146). By phase: mid build 18 vs upgrade 14 (**build‑leaning mid**), late build 36 vs upgrade 224 (**late heavily upgrade‑dominant**). Round progression: all non-cap checks passed; the only `delta_round=0` observations occurred at round 28 cap (10/136 checks). Reward/mean min ~4715.4, max ~5818.6, last ~4825.9; format reward 1.0; truncation 0; completion_len/mean min ~14570.5, max ~20520.5, last ~15399.0. Logs show an intermittent sample-upload failure at step 40 (`HTTP 500 Internal Server Error`), after which training continued to completion.
- Run X50 (v0.2.18, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50. Parsed all rollouts and all turns: 24 samples, plan length always 2 (124/124), invalid_plan=0, choose_out_of_range=0. Action mix was near parity overall (build=123, upgrade=118, noop=7) with a moderately upgrade-skewed candidate pool (build=260 vs upgrade=324; noop candidates=124). By phase: mid build 64 vs upgrade 39 (**build-leaning mid**), late build 59 vs upgrade 79 (**late upgrade-leaning**, ~34% more upgrades than builds). Round progression: all non-cap checks passed; the only `delta_round=0` observations occurred at round 18 cap (24/100 checks). Reward/mean min ~924.4, max ~1857.85, last ~1404.75; format reward 1.0; truncation 0; completion_len/mean min ~2773.0, max ~7541.0, last ~5169.0. No upload 500s observed.
- Run X51 (v0.2.18, max_rounds=30, batch_size=2, branching) completed **without retrievable rollout samples** (steps 0/10/20/30/40/50 all returned 0 samples). Logs show repeated sample-upload failures (`HTTP 500 Internal Server Error`) at each sample checkpoint while training continued to completion. Metrics remained well-formed (reward/mean min ~5693.5, max ~6836.7, last ~6621.7; format reward 1.0; truncation 0), but completion payloads were large (completion_len/mean min ~16864.5, max ~22802.0, last ~21446.5; num_turns/mean up to 19), so behavioral analysis for X51 is **not possible** from rollouts.
- Run X52 (v0.2.18, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50. Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (127/128) with one 1-action plan; invalid_plan=0, choose_out_of_range=0. Action mix was build-leaning overall (build=140, upgrade=109, noop=6) with candidate availability still upgrade-skewed (build=277 vs upgrade=328; noop candidates=128). By phase: mid build 74 vs upgrade 33 (**build-leaning mid**), late build 66 vs upgrade 76 (**late upgrade-leaning**, ~15% more upgrades than builds). Round progression: all non-cap checks passed; the only `delta_round=0` observations occurred at round 18 cap (24/104 checks). Reward/mean min ~901.9, max ~1895.85, last ~901.9; format reward min ~0.929, last 1.0; truncation 0; completion_len/mean min ~2594.0, max ~7562.5, last ~2719.75. No upload 500s; one transient server sync error at run end.
- Run X53 (v0.2.18, max_rounds=30, batch_size=2, stricter observation caps) completed with samples at steps 10/40/50 only (step samples: 2/2/2). Steps 0/20/30 logged sample upload attempts but then hit `HTTP 500 Internal Server Error`, so those rollouts are unavailable. Parsed all available rollouts and all turns: 6 samples, plan length mostly 2 (100/102) with two 1-action plans; invalid_plan=0, choose_out_of_range=0. Action mix was strongly upgrade-dominant (upgrade=171, build=14, noop=17). By phase: mid build 5 vs upgrade 15, late build 9 vs upgrade 156 with high noop (15). Candidate availability in parsed turns was heavily skewed late (late candidates: build=30, upgrade=234, noop=90), indicating build-opportunity starvation under the strict payload caps. Round progression: all non-cap checks passed; the only `delta_round=0` observations occurred at round 30 cap (6/96 checks). Reward/mean min ~4768.9, max ~6793.2, last ~6153.6; format reward 1.0; truncation 0; completion_len/mean min ~13314.0, max ~20188.5, last ~17114.5.
- Run X54 (v0.2.18, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50. Parsed all rollouts and all turns: 24 samples, plan length always 2 (124/124), invalid_plan=0, choose_out_of_range=0. Action mix was build-leaning overall (build=147, upgrade=100, noop=1) while candidate availability was near-balanced with slight upgrade skew (build=275 vs upgrade=310; noop candidates=124). By phase (rounds start at 12): mid build 41 vs upgrade 11 (**build-heavy mid**), late build 106 vs upgrade 89 (**late build-leaning**) - **plan quality fails** the late adaptive target (should be upgrade-leaning with build present). Round progression: all post-turn checks passed (`delta_round == 1` for 100/100, 0 missing, 0 pre-cap failures). Reward/mean min ~911.4, max ~1896.85, last ~1160.7; format reward 1.0; truncation 0; completion_len/mean min ~2700.75, max ~7765.0, last ~3989.0. No upload 500s observed. Episodes saturated at round 18 cap, so episode length remains **not measurable beyond cap** in this run.
- Run X55 (v0.2.18, max_rounds=30, batch_size=2, branching) completed with partial retrievable samples at steps 10/20/40 only (step samples: 2/2/2). Logs show sample-upload `HTTP 500 Internal Server Error` warnings around steps 0/30/50, so those rollout checkpoints are missing. Parsed all available rollouts and all turns: 6 samples, plan length always 2 (90/90), invalid_plan=0, choose_out_of_range=0. Action mix was strongly upgrade-dominant (upgrade=136, build=44), and candidate availability was similarly skewed (upgrade=246, build=79, noop=90). By phase (all sampled turns are late due snapshots at rounds 12/16): late build 44 vs upgrade 136 (~209% upgrade lead; build share ~24%) - **plan quality fails** adaptive late target (upgrade lead too large despite some build presence). Round progression: all post-turn checks passed (`delta_round == 1` for 84/84, 0 missing, 0 pre-cap failures). Reward/mean min ~5622.0, max ~6841.2, last ~6144.6; format reward 1.0; truncation 0; completion_len/mean min ~16133.0, max ~22811.0, last ~18475.5. Parsed rollouts all reached round 30 cap, so episode length remains **cap-limited/inconclusive beyond cap**, but X55 does show horizon execution can reach 30 under current settings when sample uploads succeed.
- Run X56 (v0.2.18, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50. Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (102/104) with two 1-action plans; invalid_plan=0, choose_out_of_range=0. Action mix was build-leaning overall (build=123, upgrade=83) and candidate availability was near-balanced with mild upgrade skew (build=247 vs upgrade=271; noop candidates=104). By phase (rounds start at 12): mid build 23 vs upgrade 9 (**build-heavy mid**), late build 100 vs upgrade 74 (**late build-leaning**) - **plan quality fails** the adaptive late target (late should be upgrade-leaning with build presence). Round progression: all post-turn checks passed (`delta_round == 1` for 80/80, 0 missing, 0 pre-cap failures). Reward/mean min ~895.9, max ~1881.35, last ~1418.75; format reward 1.0; truncation 0; completion_len/mean min ~2649.25, max ~7862.25, last ~5279.25. No upload 500s observed. Episodes saturated at round 18 cap, so episode length remains **not measurable beyond cap** in this run.
- Run X57 (v0.2.18, max_rounds=30, batch_size=1, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length always 2 (90/90); invalid_plan=0, choose_out_of_range=0. Action mix was upgrade-dominant (upgrade=130, build=35, noop=15), with candidate availability also skewed to upgrades (upgrade=260, build=98, noop=90). By phase (snapshots at rounds 14/18, so parsed turns are effectively late): late build 35 vs upgrade 130 (~271% upgrade lead; build share ~21%) - **plan quality fails** adaptive late target (upgrade lead too large; build share below floor). Round progression: all post-turn checks passed (`delta_round == 1` for 84/84, 0 missing, 0 pre-cap failures). Reward/mean min ~4994.9, max ~6544.1, last ~6210.1; format reward 1.0; truncation 0; completion_len/mean min ~13294.0, max ~20503.0, last ~18510.0. No sample-upload 500s and no missing sample steps. Parsed rollouts reached round 30 cap, so episode length beyond cap remains **inconclusive**, but upload reliability is improved versus prior max_rounds=30 runs.
- Run X58 (v0.2.18, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50. Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (126/128) with two 1-action plans; invalid_plan=0, choose_out_of_range=0. Action mix was slightly **upgrade-leaning overall** (upgrade=137, build=113, noop=4) with a more upgrade-skewed candidate pool than X56 (upgrade=378 vs build=256; noop candidates=128). By phase (rounds start at 12): mid build 34 vs upgrade 21 (**build-leaning mid**), late build 79 vs upgrade 116 (**late upgrade-leaning with build presence**, ~47% upgrade lead) - **plan quality pass (partial)** for late target direction but still above preferred 15-25% lead band. Round progression: all post-turn checks passed (`delta_round == 1` for 104/104, 0 missing, 0 pre-cap failures). Reward/mean min ~889.9, max ~1887.6, last ~1859.6; format reward min ~0.571 (recovered to 1.0 by end), truncation 0; completion_len/mean min ~2762.0, max ~7856.75, last ~7458.75. No upload 500s observed. Episodes saturated at round 18 cap, so episode length remains **not measurable beyond cap** in this run.
- Run X59 (v0.2.18, max_rounds=32, batch_size=1, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length always 2 (106/106); invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=175, build=37) with a heavily upgrade-skewed candidate pool (upgrade=298 vs build=70; noop candidates=106). By phase (snapshots at rounds 14/18, parsed turns effectively late): late build 37 vs upgrade 175 (~373% upgrade lead; build share ~17%) - **plan quality fails** adaptive late target (upgrade lead too large; build floor missed). Round progression: all post-turn checks passed (`delta_round == 1` for 100/100, 0 missing, 0 pre-cap failures). Reward/mean min ~5892.5, max ~7395.7, last ~6150.5; format reward 1.0; truncation 0; completion_len/mean min ~16099.0, max ~23059.0, last ~16320.0. No sample-upload 500s and no missing sample steps. Parsed rollouts reached round 32 cap, so episode length beyond cap remains **inconclusive**, but this extends stable capped-horizon execution and sample reliability versus earlier runs.
- Run X60 (v0.2.18, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50. Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (110/112) with two 1-action plans; invalid_plan=0, choose_out_of_range=0. Action mix remained **upgrade-leaning overall** (upgrade=121, build=99, noop=2) with an upgrade-skewed candidate pool (upgrade=365 vs build=231; noop candidates=112). By phase (rounds start at 12): mid build 26 vs upgrade 12 (**build-leaning mid**), late build 73 vs upgrade 109 (**late upgrade-leaning with build presence**, ~49% upgrade lead) - **plan quality pass (partial)** for late target direction but still above preferred lead band. Round progression: all post-turn checks passed (`delta_round == 1` for 88/88, 0 missing, 0 pre-cap failures). Reward/mean min ~902.65, max ~1902.6, last ~1635.05; format reward 1.0; truncation 0; completion_len/mean min ~2820.0, max ~7812.75, last ~6323.75. No sample-upload 500s observed. Episodes saturated at round 18 cap, so episode length remains **not measurable beyond cap** in this run.
- Run X61 (v0.2.18, max_rounds=34, batch_size=1, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length always 2 (114/114); invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=191, build=37) with a heavily upgrade-skewed candidate pool (upgrade=322 vs build=70; noop candidates=114). By phase (snapshots at rounds 14/18, parsed turns effectively late): late build 37 vs upgrade 191 (~416% upgrade lead; build share ~16%) - **plan quality fails** adaptive late target (upgrade lead too large; build floor missed). Round progression: all post-turn checks passed (`delta_round == 1` for 108/108, 0 missing, 0 pre-cap failures). Reward/mean min ~6811.1, max ~8370.3, last ~6886.1; format reward 1.0; truncation 0; completion_len/mean min ~17632.0, max ~25582.0, last ~18405.0. No sample-upload 500s and no missing sample steps. Parsed rollouts reached round 34 cap, so episode length beyond cap remains **inconclusive**, but reliability-first horizon execution remains stable at higher cap.
- Run X62 (v0.2.18, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50. Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (109/112) with three 1-action plans; invalid_plan=0, choose_out_of_range=0. Action mix was slightly **build-leaning overall** (build=116, upgrade=105) with an upgrade-skewed candidate pool (upgrade=356 vs build=239; noop candidates=112). By phase (rounds start at 12): mid build 28 vs upgrade 11 (**build-leaning mid**), late build 88 vs upgrade 94 (**late upgrade-leaning with build presence**, ~7% upgrade lead) - **plan quality partial** (late direction is correct but below the preferred 15-25% lead band). Round progression: all non-cap checks passed (`delta_round == 1` for 88/88, 0 missing, 0 pre-cap failures); cap-bound observations were `delta_round=0` at round 18 (24/112 checks). Reward/mean min ~881.65, max ~1882.10, last ~1352.25; format reward 1.0; truncation 0; completion_len/mean min ~2613.5, max ~7757.0, last ~5211.25. No sample-upload 500s observed. Episodes saturated at round 18 cap, so episode length remains **not measurable beyond cap** in this run.
- Run X63 (v0.2.18, max_rounds=36, batch_size=1, branching) completed with samples at steps 0/10/30/40/50 (**step 20 had 0 samples**). Parsed all available rollouts and all turns: 5 samples, plan length always 2 (107/107); invalid_plan=0, choose_out_of_range=0. Action mix was strongly **upgrade-dominant** (upgrade=181, build=29, noop=4) with a heavily upgrade-skewed candidate pool (upgrade=311 vs build=77; noop candidates=107). By phase (snapshots at rounds 14/18, parsed turns effectively late): late build 29 vs upgrade 181 (~524% upgrade lead; build share ~14%) - **plan quality fails** adaptive late target (upgrade lead too large; build floor missed). Round progression: all non-cap checks passed (`delta_round == 1` for 102/102, 0 missing, 0 pre-cap failures); cap-bound observations were `delta_round=0` at round 36 (5/107 checks). Reward/mean min ~7898.7, max ~9573.9, last ~9151.9; format reward 1.0; truncation 0; completion_len/mean min ~20616.0, max ~29027.0, last ~25513.0. Logs show one sample-upload `HTTP 500 Internal Server Error` at step 20, matching missing step-20 rollouts. Parsed rollouts reached round 36 cap, so episode length beyond cap remains **inconclusive**, but horizon lower-bound execution extends to >=36.
- Run X64 (v0.2.18, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50. Parsed all rollouts and all turns: 24 samples, plan length always 2 (100/100); invalid_plan=0, choose_out_of_range=0. Action mix was near-balanced with mild upgrade lead (upgrade=104, build=92, noop=4) and a moderately upgrade-skewed candidate pool (upgrade=370 vs build=235; noop candidates=100). By phase (snapshots at rounds 12/16): mid build 19 vs upgrade 9 (**build-leaning mid**), late build 73 vs upgrade 95 (**late upgrade-leaning with build presence**, ~30% upgrade lead) - **plan quality pass (partial)** for target direction, but still above the preferred 15-25% lead band. Round progression: all non-cap checks passed (`delta_round == 1` for 52/52, 0 missing, 0 pre-cap failures); cap-bound observations were `delta_round=0` at round 18 (24/48 checks). Reward/mean min ~915.9, max ~1861.35, last ~1387.75; format reward 1.0; truncation 0; completion_len/mean min ~2917.0, max ~7919.75, last ~5437.0. No sample-upload 500s observed.
- Run X65 (v0.2.18, max_rounds=36, batch_size=1, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length always 2 (122/122); invalid_plan=0, choose_out_of_range=0. Action mix was strongly upgrade-dominant (upgrade=207, build=37) with a heavily upgrade-skewed candidate pool (upgrade=352 vs build=67; noop candidates=122). By phase (snapshots at rounds 14/18, parsed turns effectively late): late build 37 vs upgrade 207 (~459% upgrade lead; build share ~15%) - **plan quality fails** adaptive late target (upgrade lead too large; build floor missed). Round progression: all non-cap checks passed (`delta_round == 1` for 110/110, 0 missing, 0 pre-cap failures); cap-bound observations were `delta_round=0` at round 36 (6/12 checks). Reward/mean min ~7851.7, max ~9556.9, last ~9058.9; format reward 1.0; truncation 0; completion_len/mean min ~19098.0, max ~26976.0, last ~24804.0. No sample-upload 500s observed. Parsed rollouts reached round 36 cap with full sample checkpoints, so horizon reliability improved, but beyond-cap episode length remains **inconclusive**.
- Run X66 (v0.2.19, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50. Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (114/116) with two 1-action plans; invalid_plan=0, choose_out_of_range=0. Action mix was near-balanced with mild upgrade lead (upgrade=118, build=112) and a moderately upgrade-skewed candidate pool (upgrade=370 vs build=255; noop candidates=116). By phase (snapshots at rounds 12/16): mid build 25 vs upgrade 18 (**build-leaning mid**), late build 87 vs upgrade 100 (**late upgrade-leaning with build presence**, ~15% upgrade lead) - **plan quality pass** (meets the lower bound of the preferred 15-25% late upgrade-lead band). Round progression: all non-cap checks passed (`delta_round == 1` for 68/68, 0 missing, 0 pre-cap failures); cap-bound observations were `delta_round=0` at round 18 (24/48 checks). Reward/mean min ~903.4, max ~1884.35, last ~1848.35; format reward 1.0; truncation 0; completion_len/mean min ~2740.5, max ~7823.75, last ~7531.25. No sample-upload 500s observed.
- Run X67 (v0.2.19, max_rounds=38, batch_size=1, branching) completed with samples at steps 10/30/50 only (**steps 0/20/40 sample uploads failed with HTTP 500**). Parsed all available rollouts and all turns: 3 samples, plan length always 2 (63/63); invalid_plan=0, choose_out_of_range=0. Action mix was strongly upgrade-dominant (upgrade=106, build=20) with a heavily upgrade-skewed candidate pool (upgrade=179 vs build=32; noop candidates=63). By phase (snapshots at rounds 14/18, parsed turns effectively late): late build 20 vs upgrade 106 (~430% upgrade lead; build share ~16%) - **plan quality fails** adaptive late target (upgrade lead too large; build floor missed). Round progression: all non-cap checks passed on available rollouts (`delta_round == 1` for 57/57, 0 missing, 0 pre-cap failures); cap-bound observations were `delta_round=0` at round 38 (3/6 checks). Reward/mean min ~5699.4, max ~10215.5, last ~6734.2; format reward 1.0; truncation 0; completion_len/mean min ~21820.0, max ~29407.0, last ~29371.0. Parsed rollouts reached round 38 cap, so horizon lower-bound execution extends to >=38, but beyond-cap episode length remains **inconclusive** and sample reliability regressed vs X65.
- Run X68 (v0.2.19, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (121/124) with three 1-action plans; invalid_plan=0, choose_out_of_range=0. Action mix was near-balanced (upgrade=123, build=120, noop=2) with an upgrade-skewed candidate pool (upgrade=377 vs build=256; noop candidates=124). By phase (snapshots at rounds 12/16): mid build 37 vs upgrade 14 (**build-leaning mid**), late build 83 vs upgrade 109 (**late upgrade-leaning with build presence**, ~31% upgrade lead) - **plan quality partial** (correct direction, but above the preferred 15-25% lead band). Round progression: all non-cap checks passed (`delta_round == 1` for 76/76, 0 missing, 0 pre-cap failures); cap-bound observations at round 18 were split between `delta_round=1` and `delta_round=0` with cap-zero at 24/48 checks. Reward/mean min ~910.4, max ~1890.6, last ~1407.5; format reward 1.0; truncation 0; completion_len/mean min ~2686.75, max ~7747.75, last ~5316.0. No sample-upload 500s observed.
- Run X69 (v0.2.19, max_rounds=38, batch_size=1, branching) completed with samples at steps 10/20/30/40/50 (**step 0 sample upload failed with HTTP 500 after retries**). Parsed all available rollouts and all turns: 5 samples, plan length always 2 (117/117); invalid_plan=0, choose_out_of_range=0. Action mix was strongly upgrade-dominant (upgrade=215, build=19) with a heavily upgrade-skewed candidate pool (upgrade=341 vs build=31; noop candidates=117). By phase (snapshots at rounds 14/18, parsed turns effectively late-only): late build 19 vs upgrade 215 (~1032% upgrade lead; build share ~8%) - **plan quality fails** adaptive late target (upgrade lead too large; build floor missed). Round progression: all non-cap checks passed on available rollouts (`delta_round == 1` for 107/107, 0 missing, 0 pre-cap failures); cap-bound observations were `delta_round=0` at round 38 (5/10 checks). Reward/mean min ~4166.3, max ~7956.5, last ~6618.8; format reward 1.0; truncation 0; completion_len/mean min ~20471.0, max ~26131.0, last ~20759.0. Parsed rollouts reached round 38 cap, so horizon lower-bound execution remains >=38, but beyond-cap episode length is still **inconclusive** and sample reliability is **partial**.
- Run X70 (v0.2.19, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (113/116) with three 1-action plans; invalid_plan=0, choose_out_of_range=0. Action mix was near-balanced overall (build=116, upgrade=112, noop=1) with an upgrade-skewed candidate pool (upgrade=354 vs build=242; noop candidates=116). By phase (snapshots at rounds 12/16): mid build 34 vs upgrade 10 (**build-leaning mid**), late build 82 vs upgrade 102 (**late upgrade-leaning with build presence**, ~24% upgrade lead) - **plan quality pass** (near upper bound of preferred 15-25% band). Round progression: all non-cap checks passed (`delta_round == 1` for 68/68, 0 missing, 0 pre-cap failures); cap-bound observations at round 18 were split (`delta_round=0` in 24/48 checks). Reward/mean min ~902.15, max ~1883.35, last ~1137.70; format reward 1.0; truncation 0; completion_len/mean min ~2727.25, max ~7917.75, last ~3983.25. No sample-upload 500s observed.
- Run X71 (v0.2.19, max_rounds=38, batch_size=1, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1) and no sample-upload 500s, but policy outputs were persistently invalid. Parsed all rollouts and all turns: 6 samples, assistant turns=103, **format-invalid plans=103/103**, plan-length histogram=`invalid` only, and parsed chosen action mix was empty. Metrics confirm persistent generation failure: `is_truncated/mean=1.0` throughout, `_macro_round_format_reward=-1.0` throughout, reward/mean stayed negative (min/last -25.8, max -10.4), completion_len/mean remained very large (~8.4k to ~23.1k), and num_turns rose to 23. Round progression degraded (`delta_round` non-cap pass/fail = 95/4). Parsed rollouts reached round 38 cap in 2/6 samples only. **Fail** for behavior and horizon inference; treat X71 as configuration-invalid due over-tight generation budget (`max_tokens=32`) under this prompt regime.
- Run X72 (v0.2.19, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (119/120) with one 1-action plan; invalid_plan=0, choose_out_of_range=0. Action mix was slightly build-leaning overall (build=124, upgrade=113, noop=2) with an upgrade-skewed candidate pool (upgrade=374 vs build=251; noop candidates=120). By phase (snapshots at rounds 12/16): mid build 40 vs upgrade 8 (**build-leaning mid**), late build 84 vs upgrade 105 (**late upgrade-leaning with build presence**, ~25% upgrade lead) - **plan quality pass** (upper bound of preferred 15-25% band). Round progression: all non-cap checks passed (`delta_round == 1` for 72/72, 0 missing, 0 pre-cap failures); cap-bound observations at round 18 were split (`delta_round=0` in 24/48 checks). Reward/mean min ~776.50, max ~1883.35, last ~1159.45; format reward 1.0; truncation 0; completion_len/mean min ~2102.75, max ~7659.50, last ~3877.00. No sample-upload 500s observed; one transient metric error spike (`error/mean=0.5` at step 8) self-recovered.
- Run X73 (v0.2.19, max_rounds=38, batch_size=1, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length always 2 (126/126), invalid_plan=0, choose_out_of_range=0. Action mix was strongly upgrade-dominant (upgrade=227, build=25) with upgrade-heavy candidate pool (upgrade=248 vs build=70; noop candidates=126). By phase (snapshots at rounds 16/20, effectively late-only): late build 25 vs upgrade 227 (~808% upgrade lead; build share ~10%) - **plan quality fail** adaptive late target (upgrade lead too large; build floor missed). Round progression: all non-cap checks passed (`delta_round == 1` for 114/114, 0 missing, 0 pre-cap failures); cap-bound observations at round 38 were split (`delta_round=0` in 6/12 checks). Reward/mean min ~627.10, max ~9363.90, last ~4142.00; format reward 1.0; truncation 0; completion_len/mean min ~1077.0, max ~21084.0, last ~20766.0; num_turns max/last 23. No sample-upload 500s observed; one transient server-sync/model-query connection error early in run self-recovered.
- Run X74 (v0.2.19, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/2/4/4/4). Parsed all retrieved rollouts and all turns: 22 samples, plan length always 2 (102/102), invalid_plan=0, choose_out_of_range=0. Action mix was near parity overall (build=102, upgrade=100, noop=2), while candidate availability stayed upgrade-skewed (build=232 vs upgrade=322; noop candidates=102). By phase (snapshots at rounds 12/16): mid build 30 vs upgrade 6 (**build-leaning mid**), late build 72 vs upgrade 94 (**late upgrade-leaning with build presence**, ~31% upgrade lead) - **plan quality partial** (direction is correct, but above preferred 15-25% band). Round progression: all non-cap checks passed (`delta_round == 1` for 58/58, 0 missing, 0 pre-cap failures); cap-bound observations at round 18 were split (`delta_round=0` in 22/44 checks). Reward/mean min ~896.15, max ~1916.35, last ~1626.05; format reward recovered to 1.0; truncation max 0.25 then 0.0 at end; completion_len/mean min ~2799.75, max ~7846.0, last ~6422.75. Logs show no sample-upload 500s; one transient server-sync/model-query connection error self-recovered. **Criteria verdict:** round progression PASS; plan quality PARTIAL; no exploit-spike signal PASS; episode length still cap-limited/inconclusive at 18.
- Run X75 (v0.2.19, max_rounds=40, batch_size=1, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length always 2 (138/138), invalid_plan=0, choose_out_of_range=0. Action mix was strongly upgrade-dominant (upgrade=250, build=25, noop=1), and candidate availability was similarly skewed (upgrade=272, build=38, noop=138). By phase (snapshots at rounds 16/20, effectively late-only): late build 25 vs upgrade 250 (~900% upgrade lead; build share ~9%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression: all non-cap checks passed (`delta_round == 1` for 126/126, 0 missing, 0 pre-cap failures); cap-bound observations at round 40 were split (`delta_round=0` in 6/12 checks). Reward/mean min ~277.30, max ~5222.10, last ~3878.40; format reward 1.0; truncation 0; completion_len/mean min ~35.0, max ~22489.0, last ~18675.0; num_turns max/last 25/21. No sample-upload 500s or logged runtime errors. **Criteria verdict:** round progression PASS; plan quality FAIL; horizon lower-bound PASS (`true horizon >= 40`); beyond-cap episode length still unresolved by right-censoring.
- Run X76 (v0.2.19, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length always 2 (132/132), invalid_plan=0, choose_out_of_range=0. Action mix was slightly upgrade-leaning overall (upgrade=137, build=127), with an upgrade-skewed candidate pool (upgrade=402 vs build=271; noop candidates=132). By phase (round-mapped with early<=11, mid<=13): mid build 48 vs upgrade 12 (**build-leaning mid**), late build 79 vs upgrade 125 (**late upgrade-leaning with build presence**, ~58% upgrade lead) - **plan quality partial** (direction is correct, but upgrade lead remains above preferred 15-25% band). Round progression: all non-cap checks passed (`delta_round == 1` for 84/84, 0 missing, 0 pre-cap failures); cap-bound observations at round 18 were split (`delta_round=0` in 24/48 checks). Reward/mean min ~902.15, max ~1872.35, last ~938.40; format reward 1.0; truncation 0; completion_len/mean min ~2668.0, max ~7729.5, last ~2772.25. No sample-upload 500s or logged runtime errors. **Criteria verdict:** round progression PASS; plan quality PARTIAL; no exploit-spike signal PASS; episode length still cap-limited/inconclusive at 18.
- Run X77 (v0.2.19, max_rounds=42, batch_size=1, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length always 2 (154/154), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=285, build=23), and candidate availability was similarly skewed (upgrade=302, build=34, noop=154). By phase (snapshots at rounds 16/20, effectively late-only): late build 23 vs upgrade 285 (~1139% upgrade lead; build share ~7%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression: all non-cap checks passed (`delta_round == 1` for 142/142, 0 missing, 0 pre-cap failures); cap-bound observations at round 42 were split (`delta_round=0` in 6/12 checks). Reward/mean min ~3098.40, max ~11643.10, last ~5216.90; format reward 1.0; truncation 0; completion_len/mean min ~13797.0, max ~25103.0, last ~20523.0; num_turns max/last 27/23. No sample-upload 500s or logged runtime errors. **Criteria verdict:** round progression PASS; plan quality FAIL; horizon lower-bound PASS (`true horizon >= 42`); beyond-cap episode length remains unresolved by right-censoring.
- Run X78 (v0.2.19, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length always 2 (128/128), invalid_plan=0, choose_out_of_range=0. Action mix was slightly upgrade-leaning overall (upgrade=135, build=120, noop=1) with upgrade-skewed candidate availability (upgrade=386 vs build=275; noop candidates=128). By phase (round-mapped with early<=11, mid<=13): mid build 41 vs upgrade 15 (**build-leaning mid**), late build 79 vs upgrade 120 (**late upgrade-leaning with build presence**, ~52% upgrade lead) - **plan quality partial** (direction correct, but above preferred 15-25% late upgrade-lead band). Round progression: all non-cap checks passed (`delta_round == 1` for 104/104, 0 missing, 0 pre-cap failures); cap-bound observations were `delta_round=0` at round 18 (24/128 checks). Reward/mean min ~928.15, max ~1860.10, last ~1604.30; format reward 1.0; truncation 0; completion_len/mean min ~2830.0, max ~7765.75, last ~6370.50. No sample-upload 500s or logged runtime errors. **Criteria verdict:** round progression PASS; plan quality PARTIAL; no exploit-spike signal PASS; episode length remains cap-limited/inconclusive at 18.
- Run X79 (v0.2.19, max_rounds=44, batch_size=1, branching) completed with samples at steps 0/30/40 (step samples: 1/1/1). Steps 10/20/50 logged sample-upload `HTTP 500 Internal Server Error` warnings, so rollout coverage is partial. Parsed all available rollouts and all turns: 3 samples, plan length always 2 (75/75), invalid_plan=0, choose_out_of_range=0. Action mix was strongly upgrade-dominant (upgrade=141, build=9) with similarly skewed candidate availability (upgrade=147 vs build=13; noop candidates=75). By phase (snapshots effectively late-only): late build 9 vs upgrade 141 (~1467% upgrade lead; build share ~6%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression: all non-cap checks passed on available rollouts (`delta_round == 1` for 72/72, 0 missing, 0 pre-cap failures); cap-bound observations were `delta_round=0` at round 44 (3/75 checks). Reward/mean min ~3443.10, max ~5810.60, last ~5102.70; format reward 1.0; truncation 0; completion_len/mean min ~22090.0, max ~26307.0, last ~22380.0. **Criteria verdict:** round progression PASS (on available rollouts); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 44`); sample reliability PARTIAL due intermittent upload 500s.
- Run X80 (v0.2.22, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (119/120; one 1-action plan), invalid_plan=0, choose_out_of_range=0. Action mix shifted build-leaning overall (build=140, upgrade=96, noop=3) with near-balanced candidate availability (build=262 vs upgrade=286; noop candidates=120). By phase (round-mapped with early<=11, mid<=13): mid build 34 vs upgrade 14 (**build-leaning mid**), late build 106 vs upgrade 82 (**late build-leading**) - **plan quality fail** for the upgrade-leaning late target (direction reversed). Round progression: all non-cap checks passed (`delta_round == 1` for 72/72, 0 missing, 0 pre-cap failures); cap-bound observations at round 18 were split (`delta_round=0` in 24/48 checks). Reward/mean min ~884.40, max ~1839.85, last ~1150.45; format reward 1.0; truncation 0; completion_len/mean min ~2682.25, max ~7666.5, last ~3795.75; error/mean remained 0.0. No sample-upload 500s or logged runtime errors. **Criteria verdict:** round progression PASS; plan quality FAIL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X81 (v0.2.22, max_rounds=44, batch_size=1, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length mostly 2 (126/146; one-action plans 20), invalid_plan=0, choose_out_of_range=0. Action mix was strongly upgrade-dominant (upgrade=251, build=21) with an upgrade-skewed candidate pool (upgrade=267 vs build=55; noop candidates=146). By phase (snapshots effectively late-only): late build 21 vs upgrade 251 (~1095% upgrade lead; build share ~7.7%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression: all non-cap checks passed (`delta_round == 1` for 134/134, 0 missing, 0 pre-cap failures); cap-bound observations at round 44 were split (`delta_round=0` in 6/12 checks). Reward/mean min ~1850.70, max ~11796.10, last ~2892.00; format reward 1.0; truncation 0; completion_len/mean min ~19241.0, max ~24143.0, last ~22883.0; error/mean remained 0.0. No sample-upload 500s or logged runtime errors. **Criteria verdict:** round progression PASS; plan quality FAIL; horizon lower-bound PASS (`true horizon >= 44`); reliability PASS.
- Run X82 (v0.2.22, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length always 2 (116/116), invalid_plan=0, choose_out_of_range=0. Action mix moved back to upgrade-leaning overall (upgrade=125, build=100, noop=7) with an upgrade-skewed candidate pool (upgrade=378 vs build=246; noop candidates=116). By phase (round-mapped with early<=11, mid<=13): mid build 36 vs upgrade 8 (**build-leaning mid**), late build 64 vs upgrade 117 (**late upgrade-leaning with build presence**, ~82.8% upgrade lead) - **plan quality partial** (direction corrected, but upgrade lead remains above preferred 15-25% band). Round progression: all non-cap checks passed (`delta_round == 1` for 68/68, 0 missing, 0 pre-cap failures); cap-bound observations at round 18 were split (`delta_round=0` in 24/48 checks). Reward/mean min ~921.65, max ~1873.60, last ~1405.75; format reward 1.0; truncation 0; completion_len/mean min ~2827.0, max ~7917.25, last ~5363.5; error/mean remained 0.0. No sample-upload 500s or logged runtime errors. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X83 (v0.2.22, max_rounds=46, batch_size=1, branching) completed with samples at steps 30/40/50 (step samples: 1/1/1). Steps 0/10/20 logged sample-upload `HTTP 500 Internal Server Error` warnings, so rollout coverage is partial. Parsed all available rollouts and all turns: 3 samples, plan length always 2 (75/75), invalid_plan=0, choose_out_of_range=0. Action mix was strongly upgrade-dominant (upgrade=141, build=9) with similarly skewed candidate availability (upgrade=148 vs build=14; noop candidates=75). By phase (snapshots effectively late-only): late build 9 vs upgrade 141 (~1467% upgrade lead; build share ~6.0%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression: all non-cap checks passed on available rollouts (`delta_round == 1` for 69/69, 0 missing, 0 pre-cap failures); cap-bound observations at round 46 were split (`delta_round=0` in 3/6 checks). Reward/mean min ~2307.40, max ~5306.70, last ~2805.80; format reward 1.0; truncation 0; completion_len/mean min ~20982.0, max ~25918.0, last ~24764.0; error/mean remained 0.0. **Criteria verdict:** round progression PASS (on available rollouts); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 46`); sample reliability PARTIAL due intermittent upload 500s.
- Run X84 (v0.2.22, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (123/124; one 1-action plan), invalid_plan=0, choose_out_of_range=0. Action mix was near-parity and slightly build-leaning overall (build=135, upgrade=107, noop=5) with a near-balanced candidate pool (build=277 vs upgrade=320; noop candidates=124). By phase (round-mapped with early<=11, mid<=13): mid build 40 vs upgrade 10 (**build-leaning mid**), late build 95 vs upgrade 97 (**late near parity**) - **plan quality partial** (good build presence and close to target, but late upgrade lead is below preferred 15-25% band). Round progression: all non-cap checks passed (`delta_round == 1` for 76/76, 0 missing, 0 pre-cap failures); cap-bound observations at round 18 were split (`delta_round=0` in 24/48 checks). Reward/mean min ~923.65, max ~1870.35, last ~1363.25; format reward 1.0; truncation 0; completion_len/mean min ~2675.75, max ~7721.25, last ~5111.0; error/mean remained 0.0. No sample-upload 500s or logged runtime errors. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X85 (v0.2.22, max_rounds=46, batch_size=1, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length mostly 2 (119/121; one-action plans 2), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=202, build=17, noop=21) with an upgrade-skewed candidate pool (upgrade=230 vs build=81; noop candidates=121). By phase (snapshots effectively late-only): late build 17 vs upgrade 202 (~1088% upgrade lead; build share ~7.8%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression: non-cap checks were mostly valid (`delta_round == 1` for 110/111) with **one** non-cap `delta_round=0` terminal event (step 40 sample 0 turn 4) where lives dropped from 1 to -25 at round 29; cap-bound observations at round 46 were split (`delta_round=0` in 5/10 checks). Reward/mean min ~-280.30, max ~10297.30, last ~2055.90; format reward 1.0; truncation 0; completion_len/mean min ~2758.0, max ~20178.0, last ~16554.0; error/mean remained 0.0. No sample-upload 500s or logged runtime errors. **Criteria verdict:** round progression PARTIAL (single terminal non-cap delta=0); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 46`); reliability PASS.
- Run X86 (v0.2.22, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length always 2 (112/112), invalid_plan=0, choose_out_of_range=0. Action mix was near-parity and slightly upgrade-leaning overall (upgrade=110, build=105, noop=9) with an upgrade-skewed candidate pool (upgrade=349 vs build=254; noop candidates=112). By phase (`round_phase` from observation): mid build 28 vs upgrade 12 (**build-leaning mid**), late build 77 vs upgrade 98 (**late upgrade-leaning with build presence**, ~27.3% upgrade lead; build share ~44.0%) - **plan quality partial** (direction is correct but still outside preferred adaptive late band where build share should be lower). Round progression: all non-cap checks passed (`delta_round == 1` for 64/64, 0 missing, 0 pre-cap failures); cap-bound observations at round 18 were split (`delta_round=0` in 24/48 checks). Reward/mean min ~946.65, max ~1888.35, last ~1874.35; format reward remained 1.0; truncation 0; completion_len/mean min ~2667.0, max ~7762.25, last ~7726.0; error/mean remained 0.0. No sample-upload 500s or runtime errors. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X87 (v0.2.22, max_rounds=48, batch_size=1, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length always 2 (142/142), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=262, build=22) with an upgrade-skewed candidate pool (upgrade=278 vs build=34; noop candidates=142). By phase (`round_phase` from observation; effectively late-only): late build 22 vs upgrade 262 (~1091% upgrade lead; build share ~7.7%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression: all non-cap checks passed (`delta_round == 1` for 130/130, 0 missing, 0 pre-cap failures); cap-bound observations at round 48 were split (`delta_round=0` in 6/12 checks). Reward/mean min ~570.50, max ~13024.10, last ~1177.00; format reward remained 1.0; truncation 0; completion_len/mean min ~3730.0, max ~22306.0, last ~18105.0; error/mean remained 0.0. No sample-upload 500s or runtime errors. **Criteria verdict:** round progression PASS; plan quality FAIL; horizon lower-bound PASS (`true horizon >= 48`); reliability PASS.
- Run X88 (v0.2.22, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (107/108; one 1-action plan), invalid_plan=0, choose_out_of_range=0. Action mix moved further upgrade-leaning vs X86 (upgrade=121, build=91, noop=3) with an upgrade-skewed candidate pool (upgrade=354 vs build=232; noop candidates=108). By phase (`round_phase` from observation): late build 67 vs upgrade 111 (~65.7% upgrade lead; build share ~37.6%) - **plan quality partial** (direction remains upgrade-leaning with build presence, but lead is above preferred adaptive late band). Round progression: all non-cap checks passed (`delta_round == 1` for 60/60, 0 missing, 0 pre-cap failures); cap-bound observations at round 18 were split (`delta_round=0` in 24/48 checks). Reward/mean min ~913.15, max ~1858.10, last ~1404.75; format reward remained 1.0; truncation 0; completion_len/mean min ~2600.5, max ~7806.25, last ~5045.5; error/mean remained 0.0. No sample-upload 500s or runtime errors. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X89 (v0.2.22, max_rounds=50, batch_size=1, branching) completed with samples at steps 0/10/50 (step samples: 1/1/1). Steps 20/30/40 logged sample-upload `HTTP 500 Internal Server Error` warnings, so rollout coverage is partial. Parsed all available rollouts and all turns: 3 samples, plan length mostly 2 (53/75; one-action plans 22), invalid_plan=0, choose_out_of_range=0. Action mix was strongly upgrade-dominant (upgrade=119, build=9) with skewed candidate availability (upgrade=126 vs build=38; noop candidates=75). By phase (`round_phase` from observation; effectively late-only): late build 9 vs upgrade 119 (~1222% upgrade lead; build share ~7.0%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression: all non-cap checks passed on available rollouts (`delta_round == 1` for 69/69, 0 missing, 0 pre-cap failures); cap-bound observations at round 50 were split (`delta_round=0` in 3/6 checks). Reward/mean min ~570.50, max ~15103.70, last ~1938.50; format reward remained 1.0; truncation 0; completion_len/mean min ~3730.0, max ~23984.0, last ~19995.0; error/mean remained 0.0. **Criteria verdict:** round progression PASS (on available rollouts); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 50`); sample reliability PARTIAL due upload 500s.
- Run X90 (v0.2.22, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length always 2 (104/104), invalid_plan=0, choose_out_of_range=0. Action mix shifted to slight build-lean overall (build=112, upgrade=96) against an upgrade-skewed candidate pool (upgrade=339 vs build=244; noop candidates=104). By phase (`round_phase` from observation): mid build 29 vs upgrade 3 (**build-heavy mid**), late build 83 vs upgrade 93 (**late upgrade-leaning with build presence**, ~12.0% upgrade lead; build share ~47.2%) - **plan quality partial** (direction is correct, but late upgrade lead is below preferred 15-25% band and build share remains high). Round progression: all non-cap checks passed (`delta_round == 1` for 56/56, 0 missing, 0 pre-cap failures); cap-bound observations at round 18 were split (`delta_round=0` in 24/48 checks). Reward/mean min ~890.15, max ~1861.60, last ~1341.75; format reward 1.0; truncation 0; completion_len/mean min ~2755.75, max ~7786.50, last ~5220.00; error/mean remained 0.0. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X91 (v0.2.22, max_rounds=50, batch_size=1, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length always 2 (127/127), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=235, build=19) with similarly skewed candidate availability (upgrade=247 vs build=37; noop candidates=127). By phase (`round_phase` from observation; effectively late-only): late build 19 vs upgrade 235 (~1136.8% upgrade lead; build share ~7.5%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression: non-cap checks were mostly valid (`delta_round == 1` for 117/119) with **two** non-cap `delta_round=0` terminal events where lives were already below zero (step 40 sample 0 turn 15 at round 40, and step 50 sample 0 turn 20 at round 45); cap-bound observations at round 50 were split (`delta_round=0` in 4/8 checks). Reward/mean min ~-167.10, max ~13373.50, last ~1625.00; format reward 1.0; truncation 0; completion_len/mean min ~1941.00, max ~20055.00, last ~16729.00; error/mean remained 0.0. No sample-upload 500s or runtime errors observed. **Criteria verdict:** round progression PARTIAL (terminal non-cap delta=0 events); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 50` on cap-hit samples); reliability PASS.
- Run X92 (v0.2.22, max_rounds=18, batch_size=4, branching) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length always 2 (124/124), invalid_plan=0, choose_out_of_range=0. Action mix moved to slight upgrade-leaning overall (upgrade=126, build=120, noop=2) with upgrade-skewed candidate availability (upgrade=380 vs build=284; noop candidates=124). By phase (`round_phase` from observation): mid build 43 vs upgrade 9 (**build-heavy mid**), late build 77 vs upgrade 117 (**late upgrade-leaning with build presence**, ~51.9% upgrade lead; build share ~39.7%) - **plan quality partial** (late direction is correct with build floor, but lead remains above preferred 15-25% band and mid is not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 76/76; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~927.90, max ~1875.35, last ~1356.25; format reward 1.0; truncation 0; completion_len/mean min ~2668.0, max ~7761.0, last ~4996.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X93 (v0.2.22, max_rounds=50, batch_size=1, branching) initial concurrent attempts (`ihszxmubdikxgrzcyrhr319v`, `wid834u3horfi4ebhtqmafnl`, `tzzmwhxnyjekskmupsg2nn5m`) stalled under capacity pressure and were stopped/retried; see reliability note below for the successful restart run.
- Run X93 (v0.2.22, max_rounds=50, batch_size=1, branching, restart run `zw58rlkeo94buj1viwrp9w6z`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length always 2 (142/142), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=260, build=23, noop=1) with similarly skewed candidate availability (upgrade=278 vs build=36; noop candidates=142). By phase (`round_phase` from observation; effectively late-only): late build 23 vs upgrade 260 (~1030.4% upgrade lead; build share ~8.1%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression: all non-cap checks passed (`delta_round == 1` for 130/130, 0 missing, 0 pre-cap failures); cap-bound observations at round 50 were split (`delta_round=0` in 6/12 checks, `delta_round=1` in 6/12). Reward/mean min ~1151.8, max ~3954.9, last ~1537.6; format reward 1.0; truncation 0; completion_len/mean min ~9916.0, max ~20638.0, last ~20011.0; error/mean remained 0.0. No sample-upload 500s, no missing sample steps. **Criteria verdict:** round progression PASS; plan quality FAIL; horizon lower-bound PASS (`true horizon >= 50` on cap-hit samples); reliability PASS.
- Run X94 (v0.2.22, max_rounds=18, batch_size=4, branching, run `nl0um7oqtgeedqzbnkenysx8`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length always 2 (124/124), invalid_plan=0, choose_out_of_range=0. Action mix became more upgrade-leaning than X92 (upgrade=136, build=110, noop=2) with upgrade-skewed candidate availability (upgrade=386 vs build=258; noop candidates=124). By phase (`round_phase` from observation): mid build 43 vs upgrade 9 (**build-heavy mid**), late build 67 vs upgrade 127 (**late upgrade-leaning with build presence**, ~89.6% upgrade lead; build share ~34.5%) - **plan quality partial** (late direction is correct with build floor, but lead remains far above preferred 15-25% band and mid is not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 76/76; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~914.4, max ~1871.85, last ~1408.5; format reward 1.0; truncation 0; completion_len/mean min ~2815.0, max ~7812.5, last ~5069.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X95 (v0.2.22, max_rounds=18, batch_size=4, branching, run `p4k0ur16w5twtgtgji1ehifh`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (99/100; one 1-action plan), invalid_plan=0, choose_out_of_range=0. Action mix shifted build-leaning overall (build=126, upgrade=73) with near-balanced candidate availability (build=233 vs upgrade=268; noop candidates=100). By phase (`round_phase` from observation): mid build 23 vs upgrade 5 (**build-heavy mid**), late build 103 vs upgrade 68 (**late build-leaning**) - **plan quality fail** adaptive late target (late should remain upgrade-leaning with build presence). Round progression accounting: non-cap checks passed (`delta_round == 1` for 52/52; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~902.15, max ~1859.6, last ~1187.7; format reward 1.0; truncation 0; completion_len/mean min ~2708.75, max ~7896.75, last ~3908.75; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality FAIL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X96 (v0.2.22, max_rounds=52, batch_size=1, branching, run `mar5xgx2179s82m6zvwcv574`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length always 2 (126/126), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=229, build=23) with similarly skewed candidate availability (upgrade=246 vs build=36; noop candidates=126). By phase (`round_phase` from observation; effectively late-only): late build 23 vs upgrade 229 (~895.7% upgrade lead; build share ~9.1%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression accounting: non-cap checks were mostly valid (`delta_round == 1` for 115/116) with one terminal non-cap `delta_round=0` event (step 40 sample 0 turn 7 at round 32, lives -11); cap-bound checks at round 52 were split (`delta_round=0` in 5/10 with `delta_round=1` in 5/10). Reward/mean min ~-280.3, max ~14212.1, last ~2219.7; format reward 1.0; truncation 0; completion_len/mean min ~1941.0, max ~21834.0, last ~18375.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PARTIAL (single terminal non-cap delta=0); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 52` on cap-hit samples); reliability PASS.
- Run X97 (v0.2.22, max_rounds=18, batch_size=4, branching, run `nj8hsrsetm0ny5jm4fx41ba5`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (107/108; one 1-action plan), invalid_plan=0, choose_out_of_range=0. Action mix remained build-leaning overall (build=129, upgrade=79, noop=7) with near-balanced candidate availability (build=254 vs upgrade=278; noop candidates=108). By phase (`round_phase` from observation): mid build 32 vs upgrade 4 (**build-heavy mid**), late build 97 vs upgrade 75 (**late build-leaning**) - **plan quality fail** adaptive late target (late should remain upgrade-leaning with build presence). Round progression accounting: non-cap checks passed (`delta_round == 1` for 60/60; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~886.9, max ~1899.85, last ~1629.8; format reward 1.0; truncation 0; completion_len/mean min ~2656.75, max ~7789.75, last ~6528.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality FAIL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X98 (v0.2.22, max_rounds=53, batch_size=1, branching, run `dp055tbj7a2p5po1frsca2yy`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length mostly 2 (119/135; one-action plans 16), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=233, build=21) with similarly skewed candidate availability (upgrade=249 vs build=49; noop candidates=135). By phase (`round_phase` from observation; effectively late-only): late build 21 vs upgrade 233 (~1009.5% upgrade lead; build share ~8.3%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression accounting: non-cap checks were mostly valid (`delta_round == 1` for 125/127) with two terminal non-cap `delta_round=0` events (step 40 sample 0 turn 8 at round 37 with lives -8; step 50 sample 0 turn 19 at round 48 with lives -6); cap-bound checks at round 53 were split (`delta_round=0` in 4/8 with `delta_round=1` in 4/8). Reward/mean min ~-324.1, max ~15332.9, last ~2005.2; format reward 1.0; truncation 0; completion_len/mean min ~1941.0, max ~22677.0, last ~22366.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PARTIAL (terminal-only non-cap delta=0 events); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 53` on cap-hit samples); reliability PASS.
- Run X99 (v0.2.22, max_rounds=18, batch_size=4, branching, run `vve5v5td8r40dtp7h4os0xpk`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length always 2 (120/120), invalid_plan=0, choose_out_of_range=0. Action mix was slightly upgrade-leaning overall (upgrade=121, build=113, noop=6) with upgrade-skewed candidate availability (upgrade=376 vs build=288; noop candidates=120). By phase (`round_phase` from observation): mid build 35 vs upgrade 12 (**build-heavy mid**), late build 78 vs upgrade 109 (**late upgrade-leaning with build presence**, ~39.7% upgrade lead; build share ~41.7%) - **plan quality partial** (late direction is correct with build floor, but lead remains above preferred 15-25% band and mid is not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 72/72; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~906.15, max ~1848.60, last ~926.40; format reward 1.0; truncation 0; completion_len/mean min ~2683.67, max ~7800.50, last ~2907.75; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X100 (v0.2.22, max_rounds=54, batch_size=1, branching, run `pes0dcr1z5dh3d04mn2m0gq7`) completed with rollout requests at steps 0/10/20/30/40/50, but all step files contained 0 samples (step samples: 0/0/0/0/0/0). Progress reported `steps_with_samples=[]` with distributions present at 0/10/20/30/40/50. Parsed all retrieved rollout files (no samples available), so action-mix/candidate-pool/phase/delta-turn accounting is not measurable for this run. Logs showed sample-upload `HTTP 500 Internal Server Error` at every sample checkpoint (steps 0/10/20/30/40/50). Reward/mean min ~433.70, max ~13102.50, last ~2154.50; format reward 1.0; truncation 0; completion_len/mean min ~2773.0, max ~23349.0, last ~20024.0; error/mean remained 0.0. **Criteria verdict:** round progression INCONCLUSIVE (no rollout turn data); plan quality INCONCLUSIVE; horizon lower-bound INCONCLUSIVE; reliability FAIL (upload 500s + zero sample-step coverage). Treat as infra reliability risk, not policy fail.
- Run X101 (v0.2.22, max_rounds=18, batch_size=4, branching, run `osw0usw5yuvuqux2vncny1ti`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length always 2 (108/108), invalid_plan=0, choose_out_of_range=0. Action mix was slightly build-leaning overall (build=111, upgrade=102, noop=3) with upgrade-skewed candidate availability (upgrade=344 vs build=250; noop candidates=108). By phase (`round_phase` from observation): mid build 28 vs upgrade 8 (**build-heavy mid**), late build 83 vs upgrade 94 (**late upgrade-leaning with build presence**, ~13.3% upgrade lead; build share ~46.9%) - **plan quality partial** (late direction is correct with strong build floor, but lead is below the preferred 15-25% band and mid is not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 60/60; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~916.15, max ~1882.60, last ~1410.50; format reward 1.0; truncation 0; completion_len/mean min ~2807.25, max ~7854.0, last ~5350.25; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X102 (v0.2.22, max_rounds=54, batch_size=1, branching, run `dxt3sop7ti7gpwox0ntywnr3`) completed with samples at steps 0/10/30/40 (step samples: 1/1/1/1); steps 20/50 returned 0 samples after sample-upload `HTTP 500 Internal Server Error` warnings. Parsed all available rollouts and all turns: 4 samples, plan length always 2 (79/79), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=143, build=15) with similarly skewed candidate availability (upgrade=154 vs build=26; noop candidates=79). By phase (`round_phase` from observation; effectively late-only): late build 15 vs upgrade 143 (~853% upgrade lead; build share ~9.5%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression accounting on available rollouts: non-cap checks were mostly valid (`delta_round == 1` for 72/73) with one terminal non-cap `delta_round=0` event (step 0 sample 0 turn 4 at round 33, lives -2); cap-bound checks at round 54 were split (`delta_round=0` in 3/6 with `delta_round=1` in 3/6). Reward/mean min ~-211.30, max ~13878.50, last ~1968.10; format reward 1.0; truncation 0; completion_len/mean min ~2773.0, max ~26648.0, last ~23314.0; error/mean remained 0.0. **Criteria verdict:** round progression PARTIAL (single terminal non-cap delta=0 on available rollouts); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 54` on cap-hit available rollouts); reliability PARTIAL due upload 500s and missing sample steps.
- Run X103 (v0.2.22, max_rounds=18, batch_size=4, branching, run `y5d8pdi4xaap4km391mikwhc`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (135/136; one 1-action plan), invalid_plan=0, choose_out_of_range=0. Action mix was upgrade-leaning overall (upgrade=143, build=127, noop=1) with upgrade-skewed candidate availability (upgrade=379 vs build=270; noop candidates=136). By phase (`round_phase` from observation): mid build 48 vs upgrade 15 (**build-heavy mid**), late build 79 vs upgrade 128 (**late upgrade-leaning with build presence**, ~62.0% upgrade lead; build share ~38.2%) - **plan quality partial** (late direction is correct with build floor, but lead remains above preferred 15-25% band and mid is not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 88/88; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~924.15, max ~1893.85, last ~1159.20; format reward min ~0.571 then recovered to 1.0; truncation max 0.25 then 0.0 at end; completion_len/mean min ~2749.5, max ~8030.0, last ~4177.25; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X104 (v0.2.22, max_rounds=54, batch_size=1, branching, run `hncxuec1jquqmxny9zwcn9sd`) completed with rollout requests at steps 0/10/20/30/40/50; only step 40 returned a sample (step samples: 0/0/0/0/1/0). Parsed all retrieved rollouts and all turns: 1 sample, plan length always 2 (25/25), invalid_plan=0, choose_out_of_range=0. Action mix on available rollout was strongly upgrade-dominant (upgrade=47, build=3) with similarly skewed candidate availability (upgrade=49 vs build=5; noop candidates=25). By phase (`round_phase` from observation; late-only): late build 3 vs upgrade 47 (~1466.7% upgrade lead; build share ~6.0%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression accounting on available rollouts: non-cap checks passed (`delta_round == 1` for 23/23; fail=0; missing=0); cap-bound checks at round 54 were split (`delta_round=0` in 1/2 with `delta_round=1` in 1/2). Logs showed sample-upload `HTTP 500 Internal Server Error` at steps 0/10/20/30/50; metrics also show `is_truncated/mean=1.0` for this run. Reward/mean min ~887.3, max ~15877.7, last ~1082.3; format reward 1.0; completion_len/mean min ~4535.0, max ~23984.0, last ~4535.0. **Criteria verdict:** round progression PASS (on available rollouts); plan quality FAIL (on available rollouts); horizon lower-bound PASS (`true horizon >= 54` on available cap-hit rollout); reliability PARTIAL due upload 500s and missing sample steps.
- Run X105 (v0.2.22, max_rounds=18, batch_size=4, branching, run `sdoudjw7ta8cgx611jr2v87a`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (111/112; one 1-action plan), invalid_plan=0, choose_out_of_range=0. Action mix was slightly build-leaning overall (build=115, upgrade=103, noop=5) with upgrade-skewed candidate availability (upgrade=356 vs build=274; noop candidates=112). By phase (`round_phase` from observation): mid build 36 vs upgrade 4 (**build-heavy mid**), late build 79 vs upgrade 99 (**late upgrade-leaning with build presence**, ~25.3% upgrade lead; build share ~44.4%) - **plan quality partial** (late mix is near the preferred upper edge but mid remains build-heavy rather than mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 64/64; fail=0; missing=0); cap-bound checks at round 18 showed `delta_round=1` in 24/24. Reward/mean min ~922.4, max ~1859.1, last ~940.4; format reward 1.0; truncation 0; completion_len/mean min ~2828.75, max ~8095.0, last ~2890.5; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X106 (v0.2.22, max_rounds=53, batch_size=1, branching, run `r5f574yh1bq1lnpeggca6fqq`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length always 2 (120/120), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=216, build=20, noop=4) with similarly skewed candidate availability (upgrade=231 vs build=43; noop candidates=120). By phase (`round_phase` from observation; effectively late-only): late build 20 vs upgrade 216 (~980% upgrade lead; build share ~8.5%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression accounting: non-cap checks passed (`delta_round == 1` for 110/110; fail=0; missing=0); cap-bound checks at round 53 showed `delta_round=1` in 4/4. Reward/mean min ~785.4, max ~14857.9, last ~1650.7; format reward 1.0; truncation 0; completion_len/mean min ~4537.0, max ~22664.0, last ~19213.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality FAIL; horizon lower-bound PASS (`true horizon >= 53` on cap-hit samples); reliability PASS.
- Run X107 (v0.2.22, max_rounds=18, batch_size=4, branching, run `btz2gniuqzm8y8yyqyqy2qid`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length always 2 (132/132), invalid_plan=0, choose_out_of_range=0. Action mix moved back to upgrade-leaning overall (upgrade=143, build=121) with upgrade-skewed candidate availability (upgrade=405 vs build=306; noop candidates=132). By phase (`round_phase` from observation): mid build 47 vs upgrade 13 (**build-heavy mid**), late build 74 vs upgrade 130 (**late upgrade-leaning with build presence**, ~75.7% upgrade lead; build share ~36.3%) - **plan quality partial** (late direction is correct with build floor, but lead is far above preferred 15-25% band and mid is not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 84/84; fail=0; missing=0); cap-bound checks at round 18 showed `delta_round=1` in 24/24. Reward/mean min ~903.65, max ~1896.1, last ~1399.0; format reward 1.0; truncation 0; completion_len/mean min ~2859.0, max ~7936.75, last ~5374.5; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X108 (v0.2.22, max_rounds=54, batch_size=1, branching, run `ebj7orrhokr5pa2pc22enlx4`) completed with samples at steps 10/20/50 (step samples: 1/1/1); steps 0/30/40 returned 0 samples after sample-upload `HTTP 500 Internal Server Error` warnings. Parsed all available rollouts and all turns: 3 samples, plan length always 2 (52/52), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=76, build=12, noop=16) with similarly skewed candidate availability (upgrade=100 vs build=20; noop candidates=52). By phase (`round_phase` from observation; effectively late-only): late build 12 vs upgrade 76 (~533.3% upgrade lead; build share ~13.6%) - **plan quality fail** adaptive late target (build floor low; upgrade lead far above band). Round progression accounting on available rollouts: non-cap checks passed (`delta_round == 1` for 49/49; fail=0; missing=0); no cap-bound `round=54` observations were present in available rollouts (max observed round 52). Reward/mean min ~917.5, max ~8875.7, last ~1882.0; format reward 1.0; truncation 0; completion_len/mean min ~3607.0, max ~23450.0, last ~23340.0; error/mean remained 0.0. **Criteria verdict:** round progression PASS (on available rollouts); plan quality FAIL (on available rollouts); horizon lower-bound PASS (`true horizon >= 52` on available rollouts) with `>=54` unresolved; reliability PARTIAL due upload 500s and missing sample steps.
- Run X109 (v0.2.22, max_rounds=18, batch_size=4, branching, run `ywp6hw463scdzzbfxqul8nad`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length always 2 (96/96), invalid_plan=0, choose_out_of_range=0. Action mix shifted build-leaning overall (build=102, upgrade=86, noop=4) while candidate availability remained upgrade-skewed (upgrade=326 vs build=241; noop candidates=96). By phase (`round_phase` from observation): mid build 16 vs upgrade 8 (**build-heavy mid**), late build 86 vs upgrade 78 (**late build-leaning**, ~9.3% upgrade deficit; build share ~52.4%) - **plan quality fail** adaptive late target (late should remain upgrade-leaning with build presence). Round progression accounting: non-cap checks passed (`delta_round == 1` for 24/24; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~906.15, max ~1860.35, last ~1406.75; format reward 1.0; truncation 0; completion_len/mean min ~2712.75, max ~7660.0, last ~5211.25; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality FAIL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X110 (v0.2.22, max_rounds=54, batch_size=1, branching, run `zxk2ygd4m4e5aaij4devmeb1`) completed with samples at steps 0/10/20/40/50 (step samples: 1/1/1/1/1); step 30 returned 0 samples after a sample-upload `HTTP 500 Internal Server Error`. Parsed all available rollouts and all turns: 5 samples, plan length always 2 (109/109), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=177, build=17, noop=6) with similarly skewed candidate availability (upgrade=196 vs build=52; noop candidates=109). By phase (`round_phase` from observation; effectively late-only): late build 17 vs upgrade 177 (~941.2% upgrade lead; build share ~8.8%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression accounting on available rollouts: non-cap checks were mostly valid (`delta_round == 1` for 96/98) with two terminal non-cap `delta_round=0` events (step 40 sample 0 turn 24 at round 53 with lives 0; step 50 sample 0 turn 10 at round 35 with lives -8); cap-bound checks at round 54 were split (`delta_round=0` in 3/6 with `delta_round=1` in 3/6). Reward/mean min ~-167.10, max ~15521.70, last ~1645.60; format reward 1.0; truncation 0; completion_len/mean min ~1941.0, max ~26584.0, last ~20023.0; error/mean remained 0.0. **Criteria verdict:** round progression PARTIAL (terminal non-cap delta=0 events); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 54` on available cap-hit samples); reliability PARTIAL due upload 500 at step 30 and missing sample step coverage.
- Run X111 (v0.2.22, max_rounds=18, batch_size=4, branching, run `zves2p0f8iywrepjegv3e6ft`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length always 2 (96/96), invalid_plan=0, choose_out_of_range=0. Action mix was near-parity and slightly build-leaning overall (build=99, upgrade=92, noop=1) with upgrade-skewed candidate availability (upgrade=307 vs build=211; noop candidates=96). By phase (`round_phase` from observation): mid build 18 vs upgrade 6 (**build-heavy mid**), late build 81 vs upgrade 86 (**late upgrade-leaning with build presence**, ~6.2% upgrade lead; build share ~48.5%) - **plan quality partial** (late direction corrected from X109, but lead remains below preferred 15-25% band and mid is not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 24/24; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~904.4, max ~1912.1, last ~1656.8; format reward 1.0; truncation 0; completion_len/mean min ~2779.67, max ~7954.5, last ~6499.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X112 (v0.2.22, max_rounds=54, batch_size=1, branching, run `ob2sc03cqf8h5arkyz46bitp`) completed with samples at steps 0/20/30 (step samples: 1/1/1); steps 10/40/50 returned 0 samples after sample-upload `HTTP 500 Internal Server Error` warnings. Parsed all available rollouts and all turns: 3 samples, plan length always 2 (53/53), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=90, build=10, noop=6) with similarly skewed candidate availability (upgrade=102 vs build=28; noop candidates=53). By phase (`round_phase` from observation; effectively late-only): late build 10 vs upgrade 90 (~800% upgrade lead; build share ~10.0%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression accounting on available rollouts: non-cap checks were mostly valid (`delta_round == 1` for 45/46) with one terminal non-cap `delta_round=0` event (step 0 sample 0 turn 3 at round 32 with lives -11); cap-bound checks at round 54 were split (`delta_round=0` in 2/4 with `delta_round=1` in 2/4). Reward/mean min ~-324.1, max ~15521.7, last ~2072.5; format reward 1.0; truncation 0; completion_len/mean min ~1941.0, max ~26584.0, last ~19849.0; error/mean remained 0.0. **Criteria verdict:** round progression PARTIAL (single terminal non-cap delta=0 on available rollouts); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 54` on available cap-hit rollouts); reliability PARTIAL due upload 500s and missing sample-step coverage.
- Run X113 (v0.2.22, max_rounds=18, batch_size=4, branching, run `d5uanp8ih986m2m0pd2bd2b0`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length always 2 (104/104), invalid_plan=0, choose_out_of_range=0. Action mix was slightly build-leaning overall (build=108, upgrade=100) with upgrade-skewed candidate availability (upgrade=343 vs build=245; noop candidates=104). By phase (`round_phase` from observation): mid build 24 vs upgrade 8 (**build-heavy mid**), late build 84 vs upgrade 92 (**late upgrade-leaning with build presence**, ~9.5% upgrade lead; build share ~47.7%) - **plan quality partial** (late direction improved but still below the preferred 15-25% lead band; mid remains not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 56/56; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~923.15, max ~1878.60, last ~1657.55; format reward 1.0; truncation 0; completion_len/mean min ~2772.75, max ~7932.50, last ~6488.75; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X114 (v0.2.22, max_rounds=53, batch_size=1, branching, run `i85bj5zwerqxiyvzn7pbny4i`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length always 2 (128/128), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=235, build=21) with similarly skewed candidate availability (upgrade=250 vs build=36; noop candidates=128). By phase (`round_phase` from observation; effectively late-only): late build 21 vs upgrade 235 (~1019.0% upgrade lead; build share ~8.2%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression accounting: non-cap checks were mostly valid (`delta_round == 1` for 117/118) with one terminal non-cap `delta_round=0` event (step 40 sample 0 turn 4 at round 33 with lives -5); cap-bound checks at round 53 were split (`delta_round=0` in 5/10 with `delta_round=1` in 5/10). Reward/mean min ~433.70, max ~2623.50, last ~2009.20; format reward 1.0; truncation 0; completion_len/mean min ~2773.0, max ~22520.0, last ~22487.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PARTIAL (single terminal non-cap delta=0); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 53` on cap-hit samples); reliability PASS.
- Run X115 (v0.2.22, max_rounds=18, batch_size=4, branching, run `ap7mm6wxbqige5cncf4i4bry`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length always 2 (120/120), invalid_plan=0, choose_out_of_range=0. Action mix was near parity and slightly build-leaning overall (build=120, upgrade=119, noop=1) with upgrade-skewed candidate availability (upgrade=360 vs build=265; noop candidates=120). By phase (`round_phase` from observation): mid build 36 vs upgrade 12 (**build-heavy mid**), late build 84 vs upgrade 107 (**late upgrade-leaning with build presence**, ~27.4% upgrade lead; build share ~44.0%) - **plan quality partial** (moved materially toward band from X113, but still above the preferred 15-25% lead range and mid is not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 72/72; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~887.90, max ~1898.35, last ~958.15; format reward 1.0; truncation 0; completion_len/mean min ~2704.75, max ~7822.0, last ~2816.25; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X116 (v0.2.22, max_rounds=54, batch_size=1, branching, run `tivxmi4wuyql4s978pvtxmg0`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length always 2 (104/104), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=185, build=23) with similarly skewed candidate availability (upgrade=202 vs build=40; noop candidates=104). By phase (`round_phase` from observation; effectively late-only): late build 23 vs upgrade 185 (~704.3% upgrade lead; build share ~11.1%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression accounting: non-cap checks were mostly valid (`delta_round == 1` for 95/98) with three terminal non-cap `delta_round=0` events (step 10 sample 0 turn 17 at round 50 with lives -3; step 40 sample 0 turn 14 at round 47 with lives -3; step 50 sample 0 turn 6 at round 39 with lives -2); cap-bound checks at round 54 were split (`delta_round=0` in 3/6 with `delta_round=1` in 3/6). Reward/mean min ~-757.90, max ~8875.70, last ~2302.90; format reward 1.0; truncation 0; completion_len/mean min ~986.0, max ~20054.0, last ~16752.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PARTIAL (terminal non-cap delta=0 events); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 54` on cap-hit samples); reliability PASS.
- Run X117 (v0.2.22, max_rounds=18, batch_size=4, branching, run `n0xc9w6thqky8bkx9b290ivy`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length always 2 (104/104), invalid_plan=0, choose_out_of_range=0. Action mix was exactly balanced on build/upgrade (build=103, upgrade=103, noop=2) with upgrade-skewed candidate availability (upgrade=330 vs build=246; noop candidates=104). By phase (`round_phase` from observation): mid build 22 vs upgrade 10 (**build-heavy mid**), late build 81 vs upgrade 93 (**late upgrade-leaning with build presence**, ~14.8% upgrade lead; build share ~46.6%) - **plan quality partial** (very close to lower edge of the preferred 15-25% lead band, but still slightly below and mid remains not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 56/56; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~924.65, max ~1884.60, last ~1189.20; format reward min ~0.571 then recovered to 1.0; truncation peaked at 0.25 then ended at 0.0; completion_len/mean min ~2845.25, max ~7792.0, last ~4151.25; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X118 (v0.2.22, max_rounds=54, batch_size=1, branching, run `dkcly2xivrrjxs87s6h0utm9`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length always 2 (106/106), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=191, build=21) with similarly skewed candidate availability (upgrade=208 vs build=34; noop candidates=106). By phase (`round_phase` from observation; effectively late-only): late build 21 vs upgrade 191 (~809.5% upgrade lead; build share ~9.9%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression accounting: non-cap checks were mostly valid (`delta_round == 1` for 97/100) with three terminal non-cap `delta_round=0` events (step 0 sample 0 turn 23 at round 52 with lives -4; step 10 sample 0 turn 7 at round 36 with lives -1; step 20 sample 0 turn 5 at round 38 with lives -8); cap-bound checks at round 54 were split (`delta_round=0` in 3/6 with `delta_round=1` in 3/6). Reward/mean min ~-167.10, max ~13102.50, last ~1001.50; format reward 1.0; truncation 0; completion_len/mean min ~1939.0, max ~22761.0, last ~3593.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PARTIAL (terminal non-cap delta=0 events); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 54` on cap-hit samples); reliability PASS.
- Run X119 (v0.2.22, max_rounds=18, batch_size=4, branching, run `xxjx3f6i1is1wja0yhlua3ou`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length always 2 (104/104), invalid_plan=0, choose_out_of_range=0. Action mix tilted build-leading (build=109, upgrade=97, noop=2) despite upgrade-skewed candidate availability (upgrade=341 vs build=242; noop candidates=104). By phase (`round_phase` from observation): mid build 24 vs upgrade 8 (**build-heavy mid**), late build 85 vs upgrade 89 (**late upgrade-leaning with build presence**, ~4.7% upgrade lead; build share ~48.9%) - **plan quality partial** (late lead remained below the preferred 15-25% band and mid remained not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 56/56; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~893.65, max ~1873.10, last ~1623.55; format reward 1.0; truncation 0; completion_len/mean min ~2673.0, max ~7904.25, last ~6386.75; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X120 (v0.2.22, max_rounds=54, batch_size=1, branching, run `wfnfguf00es2neh69iff3efc`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length always 2 (127/127), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=230, build=24) with skewed candidate availability (upgrade=248 vs build=42; noop candidates=127). By phase (`round_phase` from observation; effectively late-only): late build 24 vs upgrade 230 (~858.3% upgrade lead; build share ~9.4%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression accounting: non-cap checks were mostly valid (`delta_round == 1` for 116/117) with one terminal non-cap `delta_round=0` event (step 40 sample 0 turn 18 at round 51 with lives -8); cap-bound checks at round 54 were split (`delta_round=0` in 5/10 with `delta_round=1` in 5/10). Reward/mean min ~510.70, max ~13878.50, last ~2037.50; format reward 1.0; truncation 0; completion_len/mean min ~2775.0, max ~20781.0, last ~20034.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PARTIAL (one terminal non-cap delta=0 event); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 54` on cap-hit samples); reliability PASS.
- Run X121 (v0.2.22, max_rounds=18, batch_size=4, branching, run `tznkzsc5219a6qjv2rq1zayr`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length always 2 (112/112), invalid_plan=0, choose_out_of_range=0. Action mix tilted build-leading (build=119, upgrade=98, noop=7) despite upgrade-skewed candidate availability (upgrade=355 vs build=271; noop candidates=112). By phase (`round_phase` from observation): mid build 31 vs upgrade 8 (**build-heavy mid**), late build 88 vs upgrade 90 (**late upgrade-leaning with build presence**, ~2.3% upgrade lead; build share ~49.4%) - **plan quality partial** (late lead remained well below the preferred 15-25% band and mid remained not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 64/64; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~896.90, max ~1900.35, last ~1145.20; format reward dipped to ~0.5 before recovering to 1.0; truncation 0; completion_len/mean min ~2753.75, max ~7985.0, last ~4053.25; error/mean briefly rose to 0.25 then returned to 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X122 (v0.2.22, max_rounds=54, batch_size=1, branching, run `teqva7wjcdavfaz5rsene07b`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length always 2 (100/100), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=178, build=22) with skewed candidate availability (upgrade=195 vs build=37; noop candidates=100). By phase (`round_phase` from observation; effectively late-only): late build 22 vs upgrade 178 (~709.1% upgrade lead; build share ~11.0%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression accounting: non-cap checks were mostly valid (`delta_round == 1` for 90/92) with two terminal non-cap `delta_round=0` events (step 20 sample 0 turn 6 at round 39 with lives -2; step 50 sample 0 turn 6 at round 39 with lives -7); cap-bound checks at round 54 were split (`delta_round=0` in 4/8 with `delta_round=1` in 4/8). Reward/mean min ~-211.30, max ~11826.30, last ~2386.90; format reward 1.0; truncation 0; completion_len/mean min ~1941.0, max ~20059.0, last ~16749.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PARTIAL (terminal non-cap delta=0 events); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 54` on cap-hit samples); reliability PASS.
- Run X123 (v0.2.22, max_rounds=18, batch_size=4, branching, run `iv8cdu0fnwig2smqxj4u6jz1`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (119/120; one 1-action plan), invalid_plan=0, choose_out_of_range=0. Action mix was slightly upgrade-leaning overall (upgrade=125, build=113, noop=1) with upgrade-skewed candidate availability (upgrade=378 vs build=255; noop candidates=120). By phase (`round_phase` from observation): mid build 38 vs upgrade 9 (**build-heavy mid**), late build 75 vs upgrade 116 (**late upgrade-leaning with build presence**, ~54.7% upgrade lead; build share ~39.3%) - **plan quality partial** (late direction is correct with build floor, but lead remains above the preferred 15-25% band and mid is not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 72/72; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~897.15, max ~1884.35, last ~1382.75; format reward min ~0.571 then recovered to 1.0; truncation 0; completion_len/mean min ~2755.75, max ~7965.75, last ~5375.50; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X124 (v0.2.22, max_rounds=54, batch_size=1, branching, run `ueykeiomaqy4xas1jjsu5mib`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length always 2 (119/119), invalid_plan=0, choose_out_of_range=18. Action mix remained strongly upgrade-dominant (upgrade=192, build=22, noop=6) with similarly skewed candidate availability (upgrade=214 vs build=62; noop candidates=119). By phase (`round_phase` from observation; effectively late-only): late build 22 vs upgrade 192 (~772.7% upgrade lead; build share ~10.3%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression accounting: non-cap checks were mostly valid (`delta_round == 1` for 110/113) with three terminal non-cap `delta_round=0` events (step 10 sample 0 turn 17 at round 46 with lives -4; step 20 sample 0 turn 24 at round 53 with lives 0; step 30 sample 0 turn 7 at round 36 with lives -1); cap-bound checks at round 54 were split (`delta_round=0` in 3/6 with `delta_round=1` in 3/6). Reward/mean min ~-332.10, max ~13286.50, last ~1330.60; format reward 1.0; truncation 0; completion_len/mean min ~1821.0, max ~22761.0, last ~19917.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PARTIAL (terminal non-cap delta=0 events); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 54` on cap-hit samples); reliability PASS.
- Run X125 (v0.2.22, max_rounds=18, batch_size=4, branching, run `w7yqulklo2vose7007aayn6w`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (111/112; one 1-action plan), invalid_plan=0, choose_out_of_range=0. Action mix was near parity and slightly upgrade-leaning overall (upgrade=112, build=110, noop=1) with upgrade-skewed candidate availability (upgrade=339 vs build=252; noop candidates=112). By phase (`round_phase` from observation): mid build 28 vs upgrade 12 (**build-heavy mid**), late build 82 vs upgrade 100 (**late upgrade-leaning with build presence**, ~22.0% upgrade lead; build share ~45.1%) - **plan quality partial** (late mix is now in the preferred 15-25% lead band, but mid remains not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 64/64; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~895.15, max ~1856.10, last ~1633.55; format reward 1.0; truncation 0; completion_len/mean min ~2701.0, max ~7753.75, last ~6574.25; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X126 (v0.2.22, max_rounds=54, batch_size=1, branching, run `ekdy40gqzg173v0dbj92oks4`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length mostly 2 (97/115; eighteen 1-action plans), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=191, build=20, noop=1) with similarly skewed candidate availability (upgrade=207 vs build=55; noop candidates=115). By phase (`round_phase` from observation; effectively late-only): late build 20 vs upgrade 191 (~855.0% upgrade lead; build share ~9.5%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression accounting: non-cap checks were mostly valid (`delta_round == 1` for 105/107) with two terminal non-cap `delta_round=0` events (step 20 sample 0 turn 14 at round 43 with lives -5; step 50 sample 0 turn 13 at round 46 with lives -7); cap-bound checks at round 54 were split (`delta_round=0` in 4/8 with `delta_round=1` in 4/8). Reward/mean min ~258.70, max ~13102.50, last ~1941.50; format reward 1.0; truncation 0; completion_len/mean min ~2512.0, max ~22761.0, last ~19903.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PARTIAL (terminal non-cap delta=0 events); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 54` on cap-hit samples); reliability PASS.
- Decision update (2026-02-10): X125 (exact config replicate of X123) produced materially different late behavior (from ~54.7% to ~22.0% late upgrade lead), confirming high variance around this setting; treat behavior as improved but not closed until two consecutive in-band late-mix runs are observed and mid-phase mixing improves.
- Decision update (2026-02-10): X126 (exact config replicate of X124) reproduced full horizon-lane reliability at cap 54 with no upload 500s, but controllable policy criteria remain unresolved (late over-upgrade; progression partial from terminal-only non-cap delta exceptions); keep 54 as a lower-bound horizon anchor and continue behavior fixes separately.
- Decision update (2026-02-10): Launched X127 behavior-lane replicate with run `yd7xworxd16hngfpe5jkdp66` using `configs/lab/prime-td-macro-round-60-x127.toml` (exact X125 replicate) to test consecutive reproducibility against anti-circling guardrail.
- Decision update (2026-02-10): Launched X128 horizon-lane probe with run `yxeemvmosh5j7uof73p1lf3p` using `configs/lab/prime-td-macro-round-60-x128.toml` (one-variable change from X126: late `max_upgrade_candidates` 2 -> 1) to test over-upgrade mitigation while keeping reliability controls fixed.
- Run X127 (v0.2.22, max_rounds=18, batch_size=4, branching, run `yd7xworxd16hngfpe5jkdp66`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length always 2 (88/88), invalid_plan=0, choose_out_of_range=0. Action mix shifted build-leaning overall (build=93, upgrade=81, noop=2) with upgrade-skewed candidate availability (upgrade=306 vs build=229; noop candidates=88). By phase (`round_phase` from observation): mid build 11 vs upgrade 5 (**build-heavy mid**), late build 82 vs upgrade 76 (**late build-leaning**, ~7.3% upgrade deficit; build share ~51.9%) - **plan quality fail** adaptive late target (late should remain upgrade-leaning with build presence). Round progression accounting: non-cap checks passed (`delta_round == 1` for 40/40; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~902.40, max ~1880.35, last ~1165.70; format reward 1.0; truncation 0; completion_len/mean min ~2717.5, max ~7942.0, last ~4229.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality FAIL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X128 (v0.2.22, max_rounds=54, batch_size=1, branching, run `yxeemvmosh5j7uof73p1lf3p`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length mixed (2-action: 77/118; 1-action: 41/118), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=113, build=21, noop=61) with candidate availability (upgrade=118 vs build=36; noop candidates=118). By phase (`round_phase` from observation; effectively late-only): late build 21 vs upgrade 113 (~438.1% upgrade lead; build share ~15.7%) - **plan quality fail** adaptive late target (build floor low; upgrade lead far above band). Round progression accounting: non-cap checks were mostly valid (`delta_round == 1` for 107/108) with one terminal non-cap `delta_round=0` event (step 20 sample 0 turn 5 at round 38 with lives -13); cap-bound checks at round 54 were split (`delta_round=0` in 5/10 with `delta_round=1` in 5/10). Reward/mean min ~-753.90, max ~14554.50, last ~14238.50; format reward 1.0; truncation 0; completion_len/mean min ~932.0, max ~20176.0, last ~18826.0; error/mean briefly peaked at 1.0 before ending at 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PARTIAL (single terminal non-cap delta=0 event); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 54` on cap-hit samples); reliability PASS.
- Decision update (2026-02-10): X127 failed the behavior-lane reproducibility gate by flipping from X125’s in-band late upgrade lead to late build-leaning behavior, confirming high variance and keeping behavior closure open.
- Decision update (2026-02-10): X128’s one-variable late cap reduction (2 -> 1) improved horizon-lane policy shape versus X126 (late upgrade lead reduced from ~855% to ~438%) while preserving full reliability, but controllable policy criteria remain unresolved (still late over-upgrade; progression still terminal-partial).
- Decision update (2026-02-10): Launched X129 behavior-lane probe with run `wb025d4m8ybo1bil982avup8` using `configs/lab/prime-td-macro-round-60-x129.toml` (one-variable change from X127: late `min_build_frac` 0.3478 -> 0.3450) to counter late build-leaning drift.
- Decision update (2026-02-10): Launched X130 horizon-lane replicate with run `qwvdodett51pyil90oxiuzxq` using `configs/lab/prime-td-macro-round-60-x130.toml` (exact X128 replicate) to check reproducibility while holding reliability controls fixed.
- Run X129 (v0.2.22, max_rounds=18, batch_size=4, branching, run `wb025d4m8ybo1bil982avup8`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length always 2 (132/132), invalid_plan=0, choose_out_of_range=0. Action mix was near parity and slightly build-leaning overall (build=133, upgrade=129, noop=2) with upgrade-skewed candidate availability (upgrade=398 vs build=275; noop candidates=132). By phase (`round_phase` from observation): mid build 47 vs upgrade 13 (**build-heavy mid**), late build 86 vs upgrade 116 (**late upgrade-leaning with build presence**, ~34.9% upgrade lead; build share ~42.6%) - **plan quality partial** (late direction corrected from X127 and build floor is present, but lead remains above the preferred 15-25% band and mid is not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 84/84; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~923.15, max ~1892.60, last ~1659.05; format reward min ~0.571 then recovered to 1.0; truncation peaked at 0.25 then ended at 0.0; completion_len/mean min ~2810.0, max ~7842.25, last ~6533.5; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X130 (v0.2.22, max_rounds=54, batch_size=1, branching, run `qwvdodett51pyil90oxiuzxq`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length mixed (2-action: 97/126; 1-action: 29/126), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=118, build=20, noop=85) with candidate availability (upgrade=126 vs build=79; noop candidates=126). By phase (`round_phase` from observation; effectively late-only): late build 20 vs upgrade 118 (~490.0% upgrade lead; build share ~14.5%) - **plan quality fail** adaptive late target (build floor low; upgrade lead far above band). Round progression accounting: non-cap checks were mostly valid (`delta_round == 1` for 115/116) with one terminal non-cap `delta_round=0` event (step 0 sample 0 turn 13 at round 46 with lives -4); cap-bound checks at round 54 were split (`delta_round=0` in 5/10 with `delta_round=1` in 5/10). Reward/mean min ~-127.30, max ~14513.50, last ~2172.50; format reward 1.0; truncation 0; completion_len/mean min ~2667.0, max ~20173.0, last ~19912.0; error/mean briefly peaked at 1.0 before ending at 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PARTIAL (single terminal non-cap delta=0 event); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 54` on cap-hit samples); reliability PASS.
- Decision update (2026-02-10): X129 one-variable anti-build correction restored late upgrade-leaning direction relative to X127, but still overshot the preferred late lead band and kept mid build-heavy; behavior lane remains PARTIAL with high variance.
- Decision update (2026-02-10): X130 (exact X128 replicate) preserved full reliability and horizon lower-bound evidence at cap 54, but did not improve controllable policy criteria (late over-upgrade; terminal-partial progression), so horizon lane remains a reliability/lower-bound track rather than policy-quality closure.
- Decision update (2026-02-10): Collab consensus for the next pair rejected an immediate 54->56 cap raise; launched a reproducibility + fixed-cap probe pair instead (X131 exact X129 replicate, X132 one-variable late-floor adjustment at unchanged cap 54).
- Decision update (2026-02-10): Launched X131 behavior-lane replicate with run `tpxxawdx1dlj2teozd8hc7u6` using `configs/lab/prime-td-macro-round-60-x131.toml` (exact X129 replicate to test consecutive in-band reproducibility under the anti-circling guardrail).
- Decision update (2026-02-10): Launched X132 fixed-cap horizon-policy probe with run `ge6uug9btiirnmnl1xgf0d3z` using `configs/lab/prime-td-macro-round-60-x132.toml` (one-variable change from X130: late `min_build_frac` 0.50 -> 0.55 at `max_rounds=54` to reduce late over-upgrade without conflating with cap changes).
- Run X131 (v0.2.22, max_rounds=18, batch_size=4, branching, run `tpxxawdx1dlj2teozd8hc7u6`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (103/104; one 1-action plan), invalid_plan=0, choose_out_of_range=0. Action mix was slightly build-leaning overall (build=106, upgrade=98, noop=3) with upgrade-skewed candidate availability (upgrade=341 vs build=231; noop candidates=104). By phase (`round_phase` from observation): mid build 28 vs upgrade 3 (**build-heavy mid**), late build 78 vs upgrade 95 (**late upgrade-leaning with build presence**, ~21.8% upgrade lead; build share ~45.1%) - **plan quality partial** (late mix is in the preferred 15-25% lead band, but mid remains not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 56/56; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~891.45, max ~1842.85, last ~1370.25; format reward 1.0; truncation 0; completion_len/mean min ~2432.0, max ~7798.33, last ~5299.75; error/mean briefly peaked at 0.25 before ending at 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X132 (v0.2.22, max_rounds=54, batch_size=1, branching, run `ge6uug9btiirnmnl1xgf0d3z`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length mixed (2-action: 76/142; 1-action: 66/142), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=132, build=18, noop=68) with similarly skewed candidate availability (upgrade=136 vs build=30; noop candidates=142). By phase (`round_phase` from observation; effectively late-only): late build 18 vs upgrade 132 (~633.3% upgrade lead; build share ~12.0%) - **plan quality fail** adaptive late target (build floor missed; upgrade lead far above band). Round progression accounting: non-cap checks passed (`delta_round == 1` for 130/130; fail=0; missing=0); cap-bound checks at round 54 were split (`delta_round=0` in 6/12 with `delta_round=1` in 6/12). Reward/mean min ~-168.10, max ~14556.50, last ~449.70; format reward 1.0; truncation 0; completion_len/mean min ~35.0, max ~18803.0, last ~2319.0; error/mean briefly peaked at 1.0 before ending at 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality FAIL; horizon lower-bound PASS (`true horizon >= 54` on cap-hit samples); reliability PASS.
- Decision update (2026-02-10): X131 recovered late behavior into the preferred lead band with clean progression/reliability, but mid-phase remains build-heavy; behavior lane remains PARTIAL and should prioritize a replicate before further knob changes.
- Decision update (2026-02-10): X132 resolved strict progression at cap 54 while preserving full reliability and horizon lower-bound evidence (`>=54`), but controllable policy quality remains unresolved (late over-upgrade); keep cap raises blocked until a second clean 54-cap confirmation and a policy-shape improvement probe.
- Decision update (2026-02-10): Collab-deliberation consensus validated the recommended replicate pair as-is (X133 exact X131, X134 exact X132) to satisfy the anti-circling two-consecutive confirmation guardrail before introducing new variables.
- Decision update (2026-02-10): Launched X133 behavior-lane replicate with run `gd5fo2oio0ze3hpguobnbcee` using `configs/lab/prime-td-macro-round-60-x133.toml` (exact X131 replicate to test consecutive in-band late-mix reproducibility).
- Decision update (2026-02-10): Launched X134 horizon-lane replicate with run `dfqncw6jys76gtasb1jo7wz2` using `configs/lab/prime-td-macro-round-60-x134.toml` (exact X132 replicate to confirm second consecutive clean cap-54 progression/reliability signal).
- Run X133 (v0.2.22, max_rounds=18, batch_size=4, branching, run `gd5fo2oio0ze3hpguobnbcee`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (114/116; two 1-action plans), invalid_plan=0, choose_out_of_range=0. Action mix was upgrade-leaning overall (upgrade=127, build=101, noop=2) with upgrade-skewed candidate availability (upgrade=365 vs build=248; noop candidates=116). By phase (`round_phase` from observation): mid build 30 vs upgrade 13 (**build-heavy mid**), late build 71 vs upgrade 114 (**late upgrade-leaning with build presence**, ~60.6% upgrade lead; build share ~38.4%) - **plan quality partial** (late direction/build floor are preserved, but lead overshoots the preferred 15-25% band and mid is not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 68/68; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~751.64, max ~1904.10, last ~1149.70; format reward min ~0.571 then recovered to 1.0; truncation peaked at 0.25 then ended at 0.0; completion_len/mean min ~2901.0, max ~7781.0, last ~3985.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X134 (v0.2.22, max_rounds=54, batch_size=1, branching, run `dfqncw6jys76gtasb1jo7wz2`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length mixed (2-action: 78/135; 1-action: 57/135), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=124, build=21, noop=68) with similarly skewed candidate availability (upgrade=129 vs build=36; noop candidates=135). By phase (`round_phase` from observation; effectively late-only): late build 21 vs upgrade 124 (~490.5% upgrade lead; build share ~14.5%) - **plan quality fail** adaptive late target (build floor low; upgrade lead far above band). Round progression accounting: non-cap checks were mostly valid (`delta_round == 1` for 124/125) with one terminal non-cap `delta_round=0` event (step 40 sample 0 turn 14 at round 47 with lives 0); cap-bound checks at round 54 were split (`delta_round=0` in 5/10 with `delta_round=1` in 5/10). Reward/mean min ~-753.90, max ~14417.50, last ~11408.30; format reward 1.0; truncation 0; completion_len/mean min ~932.0, max ~18803.0, last ~15735.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PARTIAL (single terminal non-cap delta=0 event); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 54` on cap-hit samples); reliability PASS.
- Decision update (2026-02-10): X133 (exact X131 replicate) did not reproduce the prior in-band late mix; late upgrade lead moved from ~21.8% to ~60.6%, so behavior-lane two-consecutive reproducibility remains unmet and behavior closure stays open.
- Decision update (2026-02-10): X134 (exact X132 replicate) preserved full reliability and cap-54 lower-bound evidence, but strict progression regressed to PARTIAL due one terminal non-cap delta exception; keep cap-raise gate closed until two consecutive clean non-cap progression passes at cap 54 are observed.
- Decision update (2026-02-10): Collab-deliberation consensus selected a replicate/replicate disambiguation pair (X135 exact X133, X136 exact X134) to resolve reproducibility ambiguity before introducing any new variable.
- Decision update (2026-02-10): Launched X135 behavior-lane replicate with run `ybutarn66v7u3ha038uk8r26` using `configs/lab/prime-td-macro-round-60-x135.toml` (exact X133 replicate to test whether late overshoot is stable or stochastic).
- Decision update (2026-02-10): Launched X136 horizon-lane replicate with run `zh4bs6oo3c7z4sp3evcekfdl` using `configs/lab/prime-td-macro-round-60-x136.toml` (exact X134 replicate at cap 54 to test whether the terminal non-cap delta exception recurs).
- Run X135 (v0.2.22, max_rounds=18, batch_size=4, branching, run `ybutarn66v7u3ha038uk8r26`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (119/120; one 1-action plan), invalid_plan=0, choose_out_of_range=0. Action mix was upgrade-leaning overall (upgrade=134, build=100, noop=5) with upgrade-skewed candidate availability (upgrade=383 vs build=238; noop candidates=120). By phase (`round_phase` from observation): mid build 36 vs upgrade 11 (**build-heavy mid**), late build 64 vs upgrade 123 (**late upgrade-leaning with build presence**, ~92.2% upgrade lead; build share ~34.2%) - **plan quality partial** (late direction/build floor are preserved, but lead overshoots the preferred 15-25% band and mid is not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 72/72; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~883.65, max ~1854.10, last ~1606.05; format reward 1.0; truncation 0; completion_len/mean min ~2681.0, max ~7751.67, last ~6513.25; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X136 (v0.2.22, max_rounds=54, batch_size=1, branching, run `zh4bs6oo3c7z4sp3evcekfdl`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length mixed (2-action: 101/134; 1-action: 33/134), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=120, build=23, noop=92) with similarly skewed candidate availability (upgrade=128 vs build=40; noop candidates=134). By phase (`round_phase` from observation; effectively late-only): late build 23 vs upgrade 120 (~421.7% upgrade lead; build share ~16.1%) - **plan quality fail** adaptive late target (build floor low; upgrade lead far above band). Round progression accounting: non-cap checks were mostly valid (`delta_round == 1` for 123/124) with one terminal non-cap `delta_round=0` event (step 50 sample 0 turn 17 at round 50 with lives 0); cap-bound checks at round 54 were split (`delta_round=0` in 5/10 with `delta_round=1` in 5/10). Reward/mean min ~-753.90, max ~14417.50, last ~14354.50; format reward 1.0; truncation 0; completion_len/mean min ~932.0, max ~18803.0, last ~18643.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PARTIAL (single terminal non-cap delta=0 event); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 54` on cap-hit samples); reliability PASS.
- Decision update (2026-02-10): X135 (exact X133 replicate) reinforced the same overshoot regime (late upgrade lead increased from ~60.6% to ~92.2%), so behavior-lane variance has narrowed toward above-band upgrade pressure and behavior closure remains unmet.
- Decision update (2026-02-10): X136 (exact X134 replicate) reproduced full reliability and cap-54 lower-bound evidence but again retained a terminal-only non-cap delta exception, so strict progression remains PARTIAL and cap-raise gating stays blocked.
- Decision update (2026-02-10): Collab-deliberation rejected the initial micro-nudge proposal as underpowered and recommended larger one-variable corrections (X137 late `min_build_frac` 0.345 -> 0.350 from X135; X138 late `min_build_frac` 0.55 -> 0.57 from X136) to avoid another low-signal loop.
- Decision update (2026-02-10): Launched X137 behavior-lane probe with run `p7phvjku0s0glzx9mdax8w6w` using `configs/lab/prime-td-macro-round-60-x137.toml` (one-variable correction from X135: late `min_build_frac` 0.345 -> 0.350).
- Decision update (2026-02-10): Launched X138 horizon-lane probe with run `kc0gmig0bpr99wrh3ru6dgi9` using `configs/lab/prime-td-macro-round-60-x138.toml` (one-variable correction from X136 at fixed cap 54: late `min_build_frac` 0.55 -> 0.57).
- Run X137 (v0.2.22, max_rounds=18, batch_size=4, branching, run `p7phvjku0s0glzx9mdax8w6w`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length mixed (2-action: 102/104; 1-action: 2/104), invalid_plan=0, choose_out_of_range=0. Action mix was near parity and slightly upgrade-leaning overall (upgrade=103, build=100, noop=3) with upgrade-skewed candidate availability (upgrade=335 vs build=221; noop candidates=104). By phase (`round_phase` from observation): mid build 25 vs upgrade 6 (**build-heavy mid**), late build 75 vs upgrade 97 (**late upgrade-leaning with build presence**, ~29.3% upgrade lead; build share ~43.6%) - **plan quality partial** (late lead moved substantially toward target but remains slightly above the preferred 15-25% band; mid is still not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 56/56; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~907.65, max ~1864.85, last ~1591.80; format reward 1.0; truncation 0; completion_len/mean min ~2739.33, max ~7774.75, last ~6376.25; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X138 (v0.2.22, max_rounds=54, batch_size=1, branching, run `kc0gmig0bpr99wrh3ru6dgi9`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length mixed (2-action: 60/138; 1-action: 78/138), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=128, build=22, noop=48) with similarly skewed candidate availability (upgrade=132 vs build=38; noop candidates=138). By phase (`round_phase` from observation; effectively late-only): late build 22 vs upgrade 128 (~481.8% upgrade lead; build share ~14.7%) - **plan quality fail** adaptive late target (build floor low; upgrade lead far above band). Round progression accounting: non-cap checks passed (`delta_round == 1` for 126/126; fail=0; missing=0); cap-bound checks at round 54 were split (`delta_round=0` in 6/12 with `delta_round=1` in 6/12). Reward/mean min ~-75.10, max ~14550.50, last ~12282.30; format reward 1.0; truncation 0; completion_len/mean min ~1833.0, max ~18803.0, last ~15574.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality FAIL; horizon lower-bound PASS (`true horizon >= 54` on cap-hit samples); reliability PASS.
- Decision update (2026-02-10): X137 one-variable build-floor increase from X135 materially reduced late overshoot (~92.2% -> ~29.3%) while keeping progression/reliability clean; behavior lane remains PARTIAL and now requires a smaller follow-up correction to land in-band.
- Decision update (2026-02-10): X138 one-variable build-floor increase from X136 cleared strict progression at cap 54 (non-cap delta pass 126/126) and preserved reliability/lower-bound evidence, but controllable policy quality remains unresolved due persistent late over-upgrade.
- Guardrail (2026-02-10): strict deliberation protocol is now mandatory before new launches - the collab subagent must explicitly inspect and cite at least the last two behavior TOMLs, last two horizon TOMLs, and the latest decision-update block in `docs/RESULTS.md`; recommendations without explicit file citations are invalid.
- Decision update (2026-02-10): Launched X139 behavior-lane probe with run `efk2s3xi71g1cggjjsngkhdf` using `configs/lab/prime-td-macro-round-60-x139.toml` (one-variable change from X137: late `min_build_frac` 0.3500 -> 0.3550) after strict collab-deliberation consensus.
- Decision update (2026-02-10): Launched X140 horizon-lane replicate with run `fpupzed5h6klely60az769r9` using `configs/lab/prime-td-macro-round-60-x140.toml` (exact X138 replicate at fixed `max_rounds=54`) to satisfy anti-circling two-consecutive confirmation before any further horizon knob move.
- Decision update (2026-02-11): Verified X140 run `fpupzed5h6klely60az769r9` reached `COMPLETED` status; rollout analysis pending.
- Decision update (2026-02-11): Per operator request, stopped and deleted hung X139 run `efk2s3xi71g1cggjjsngkhdf` before analysis/reuse.
- Decision update (2026-02-11): Restarted X139 with run `b2sv7mdj19hvinquk0nu5jrd` using `configs/lab/prime-td-macro-round-60-x139.toml` (same one-variable X137->X139 late `min_build_frac` 0.3500 -> 0.3550 setting).
- Run X139 (v0.2.22, max_rounds=18, batch_size=4, branching, restart run `b2sv7mdj19hvinquk0nu5jrd`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (2-action: 123/124; 1-action: 1/124), invalid_plan=0, choose_out_of_range=0. Action mix was slightly upgrade-leaning overall (upgrade=122, build=116, noop=9) with upgrade-skewed candidate availability (upgrade=380 vs build=265; noop candidates=124). By phase (`round_phase` from observation): mid build 38 vs upgrade 13 (**build-heavy mid**), late build 78 vs upgrade 109 (**late upgrade-leaning with build presence**, ~39.7% upgrade lead; build share ~41.7%) - **plan quality partial** (late direction/build floor remain correct, but lead is above the preferred 15-25% band and mid is still not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 76/76; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~884.15, max ~1891.85, last ~1160.45; format reward 1.0; truncation 0; completion_len/mean min ~2673.0, max ~7659.0, last ~4018.75; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X140 (v0.2.22, max_rounds=54, batch_size=1, branching, run `fpupzed5h6klely60az769r9`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length mixed (2-action: 67/108; 1-action: 41/108), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=97, build=18, noop=60) with similarly skewed candidate availability (upgrade=103 vs build=27; noop candidates=108). By phase (`round_phase` from observation; effectively late-only): late build 18 vs upgrade 97 (~438.9% upgrade lead; build share ~15.7%) - **plan quality fail** adaptive late target (build floor low; upgrade lead far above band). Round progression accounting: non-cap checks were mostly valid (`delta_round == 1` for 97/98) with one terminal non-cap `delta_round=0` event (step 40 sample 0 turn 3 at round 36 with lives -3); cap-bound checks at round 54 were split (`delta_round=0` in 5/10 with `delta_round=1` in 5/10). Reward/mean min ~-168.10, max ~14608.50, last ~1938.90; format reward 1.0; truncation 0; completion_len/mean min ~1558.0, max ~18793.0, last ~15498.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PARTIAL (single terminal non-cap delta=0 event); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 54` on cap-hit samples); reliability PASS.
- Decision update (2026-02-11): X139 one-variable build-floor increase from X137 (`late min_build_frac` 0.3500 -> 0.3550) did not reduce late overshoot; late upgrade lead moved back up (~29.3% -> ~39.7%), so behavior lane remains PARTIAL and should continue with small one-variable corrective tuning on the same base while requiring replicate confirmation.
- Decision update (2026-02-11): X140 (exact X138 replicate) preserved full reliability and cap-54 lower-bound evidence but did not reproduce strict non-cap cleanliness (one terminal non-cap delta exception) and kept policy shape over-upgrade; treat horizon lane as reliability/lower-bound tracking with progression still terminal-partial.
- Decision update (2026-02-11): Strict collab-deliberation review was executed before launch; lead decision selected the operator-approved pair for execution to preserve continuity: X141 as exact X137 replicate plus X142 as one-variable fixed-cap horizon probe (`late min_build_frac` 0.57 -> 0.60 from X140).
- Decision update (2026-02-11): Launched X141 behavior-lane replicate with run `wqwdodgrop2talwj6blwtc53` using `configs/lab/prime-td-macro-round-60-x141.toml` (exact X137 replicate for reproducibility check).
- Decision update (2026-02-11): Launched X142 horizon-lane probe with run `hw9xm7lpo4p0kbqwwvppxfgm` using `configs/lab/prime-td-macro-round-60-x142.toml` (one-variable change from X140: late `min_build_frac` 0.57 -> 0.60 at fixed `max_rounds=54`).
- Run X141 (v0.2.22, max_rounds=18, batch_size=4, branching, run `wqwdodgrop2talwj6blwtc53`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length mostly 2 (2-action: 111/112; 1-action: 1/112), invalid_plan=0, choose_out_of_range=0. Action mix remained upgrade-leaning overall (upgrade=126, build=97) with upgrade-skewed candidate availability (upgrade=368 vs build=252; noop candidates=112). By phase (`round_phase` from observation): mid build 25 vs upgrade 14 (**mid still build-leaning**), late build 72 vs upgrade 112 (**late upgrade-leaning with build presence**, ~55.6% upgrade lead; build share ~39.1%) - **plan quality partial** (late direction/build floor remain correct, but lead is still above the preferred 15-25% band; mid remains build-leaning). Round progression accounting: non-cap checks passed (`delta_round == 1` for 64/64; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~899.90, max ~1884.10, last ~1142.95; format reward 1.0; truncation 0; completion_len/mean min ~2784.25, max ~7946.5, last ~4109.75; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X142 (v0.2.22, max_rounds=54, batch_size=1, branching, run `hw9xm7lpo4p0kbqwwvppxfgm`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length mixed (2-action: 55/134; 1-action: 79/134), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=124, build=21, noop=44) with similarly skewed candidate availability (upgrade=128 vs build=36; noop candidates=134). By phase (`round_phase` from observation; effectively late-only): late build 21 vs upgrade 124 (~490.5% upgrade lead; build share ~14.5%) - **plan quality fail** adaptive late target (build floor low; upgrade lead far above band). Round progression accounting: non-cap checks passed (`delta_round == 1` for 122/122; fail=0; missing=0); cap-bound checks at round 54 were split (`delta_round=0` in 6/12 with `delta_round=1` in 6/12). Reward/mean min ~-753.90, max ~14701.50, last ~14448.50; format reward 1.0; truncation 0; completion_len/mean min ~932.0, max ~18783.0, last ~18773.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality FAIL; horizon lower-bound PASS (`true horizon >= 54` on cap-hit samples); reliability PASS.
- Decision update (2026-02-11): X141 (exact X137 replicate) did not improve behavior-lane closure; late upgrade lead increased to ~55.6% and remains above-band, confirming ongoing high-variance/overshoot risk around this behavior regime.
- Decision update (2026-02-11): X142 one-variable horizon-lane build-floor increase (`late min_build_frac` 0.57 -> 0.60 from X140) produced a clean non-cap progression pass (122/122) with full reliability at cap 54, but controllable policy quality is still unresolved due persistent late over-upgrade.
- Decision update (2026-02-11): Strict collab deliberation executed before launch; behavior subagent flagged risk on the X143 nudge while horizon subagent approved X144 replicate, and lead decision proceeded with the operator-approved pair for continuity and direct empirical validation.
- Decision update (2026-02-11): Launched X143 behavior-lane probe with run `fidm7siizcuoooi8h2xjr28f` using `configs/lab/prime-td-macro-round-60-x143.toml` (one-variable change from X139: late `min_build_frac` 0.3550 -> 0.3600).
- Decision update (2026-02-11): Launched X144 horizon-lane replicate with run `eonmfzpt8qg540w3zt5akyh1` using `configs/lab/prime-td-macro-round-60-x144.toml` (exact X142 replicate at fixed `max_rounds=54`).
- Run X143 (v0.2.22, max_rounds=18, batch_size=4, branching, run `fidm7siizcuoooi8h2xjr28f`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, plan length always 2 (2-action: 100/100), invalid_plan=0, choose_out_of_range=0. Action mix was near parity and slightly build-leaning overall (build=102, upgrade=97, noop=1) with upgrade-skewed candidate availability (upgrade=334 vs build=230; noop candidates=100). By phase (`round_phase` from observation): mid build 19 vs upgrade 9 (**mid still build-leaning**), late build 83 vs upgrade 88 with noop 1 (**late upgrade-leaning with strong build presence**, ~6.0% upgrade lead; build share ~48.5%) - **plan quality partial** (late direction is correct but under target versus preferred 15-25% upgrade-lead band; mid remains not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 52/52; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48 with `delta_round=1` in 24/48). Reward/mean min ~910.15, max ~1903.35, last ~1647.05; format reward 1.0; truncation 0; completion_len/mean min ~2695.75, max ~7828.0, last ~6423.75; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X144 (v0.2.22, max_rounds=54, batch_size=1, branching, run `eonmfzpt8qg540w3zt5akyh1`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, plan length mixed (2-action: 60/94; 1-action: 34/94), invalid_plan=0, choose_out_of_range=0. Action mix remained upgrade-dominant (upgrade=80, build=23, noop=51) with similarly skewed candidate availability (upgrade=88 vs build=40; noop candidates=94). By phase (`round_phase` from observation; effectively late-only): late build 23 vs upgrade 80 with noop 51 (**late over-upgrade**, ~247.8% upgrade lead; build share ~22.3% over build+upgrade actions) - **plan quality fail** adaptive late target (upgrade lead far above band). Round progression accounting: non-cap checks were mostly valid (`delta_round == 1` for 85/88) with three terminal non-cap `delta_round=0` events (step 0 turn 14 at round 47 lives 0; step 20 turn 4 at round 37 lives -18; step 40 turn 5 at round 38 lives -7); cap-bound checks at round 54 were split (`delta_round=0` in 3/6 with `delta_round=1` in 3/6). Reward/mean min ~-753.90, max ~14556.50, last ~4132.60; format reward 1.0; truncation 0; completion_len/mean min ~932.0, max ~18795.0, last ~15331.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PARTIAL (terminal non-cap delta events); plan quality FAIL; horizon lower-bound PASS (`true horizon >= 54` on cap-hit samples); reliability PASS.
- Decision update (2026-02-11): X143 one-variable behavior nudge from X139 (`late min_build_frac` 0.3550 -> 0.3600) corrected prior overshoot but under-shot the preferred late lead band (~6% late upgrade lead), so behavior lane remains PARTIAL and should use small opposite-direction correction from this new anchor with replicate confirmation.
- Decision update (2026-02-11): X144 (exact X142 replicate) did not reproduce X142’s clean non-cap progression; terminal non-cap delta exceptions returned while policy quality remained over-upgrade, so horizon lane remains reliability PASS but progression PARTIAL and policy unresolved at cap 54.
- Decision update (2026-02-11): Launched X145 behavior-lane probe with run `qjxsqxdtsr8ltojh2y9eys6h` using `configs/lab/prime-td-macro-round-60-x145.toml` (one-variable change from X143: late `min_build_frac` 0.3600 -> 0.3580).
- Decision update (2026-02-11): Launched X146 horizon-lane probe with run `e6ri6ah8b0tz0s8acm060nfz` using `configs/lab/prime-td-macro-round-60-x146.toml` (one-variable change from X144: `max_rounds` 54 -> 56 under unchanged payload controls).
- Run X145 (v0.2.22, max_rounds=18, batch_size=4, branching, run `qjxsqxdtsr8ltojh2y9eys6h`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, 112 turns, plan length always 2 (2-action: 112/112), invalid_plan=0, choose_out_of_range=0. Action mix was near parity and slightly build-leaning overall (build=114, upgrade=110, noop=0) with upgrade-skewed candidate availability (upgrade=350 vs build=240; noop candidates=112). By phase (`round_phase` from observation): mid build 30 vs upgrade 10 (**mid remains build-heavy**), late build 84 vs upgrade 100 (**late upgrade-leaning with build presence**, ~19.0% upgrade lead; build share ~45.7%) - **plan quality partial** (late target band now met, but mid remains not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 64/64; fail=0; missing=0); cap-bound checks at round 18 were clean (`delta_round=1` in 24/24; delta0=0). Reward/mean min ~903.65, max ~1880.60, last ~1159.70; format reward 1.0; truncation 0; completion_len/mean min ~2767.75, max ~7806.75, last ~4134.25; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X146 (v0.2.22, max_rounds=56, batch_size=1, branching, run `e6ri6ah8b0tz0s8acm060nfz`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, 112 turns, plan length mixed (2-action: 89/112; 1-action: 6/112; 0-action: 17/112), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=83, build=23, noop=78) with similarly skewed candidate availability (upgrade=106 vs build=40; noop candidates=112). By phase (`round_phase` from observation; effectively late-only): late build 23 vs upgrade 83 with noop 78 (**late over-upgrade**, ~260.9% upgrade lead; build share ~21.7% over build+upgrade actions) - **plan quality fail** adaptive late target (upgrade lead far above band). Round progression accounting: non-cap checks passed (`delta_round == 1` for 102/102; fail=0; missing=0); cap-bound checks at round 56 were clean (`delta_round=1` in 4/4; delta0=0). Reward/mean min ~-127.30, max ~15888.10, last ~13519.90; format reward 1.0; truncation 0; completion_len/mean min ~2462.0, max ~20348.0, last ~17101.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality FAIL; horizon lower-bound PASS (`true horizon >= 56` on cap-hit samples); reliability PASS.
- Decision update (2026-02-11): X145 opposite micro-correction from X143 (`late min_build_frac` 0.3600 -> 0.3580) moved late behavior into the preferred 15-25% upgrade-lead band (~19.0%) while preserving clean progression/reliability; behavior lane remains PARTIAL because mid-phase is still build-heavy.
- Decision update (2026-02-11): X146 cap raise from 54 -> 56 delivered full sample coverage, no upload 500s, and clean non-cap progression with horizon lower-bound `>=56`; this is strong evidence the prior upload-500 bottleneck may be resolved under current conditions, so payload limits can be relaxed cautiously via one-variable canary runs rather than abrupt multi-knob expansion.
- Decision update (2026-02-11): Strict collab deliberation consensus validated the next pair as non-circular when scored lane-wise: X147 exact X145 replicate for behavior reproducibility plus X148 one-variable horizon canary (`max_action_candidates` 2 -> 3 from X146).
- Decision update (2026-02-11): Launched X147 behavior-lane replicate with run `zca2ko013oesiexcl6bsivs5` using `configs/lab/prime-td-macro-round-60-x147.toml` (exact X145 replicate).
- Decision update (2026-02-11): Launched X148 horizon-lane canary with run `aewnwzxha7me4jtb8egswahe` using `configs/lab/prime-td-macro-round-60-x148.toml` (one-variable change from X146: `observation.max_action_candidates` 2 -> 3 at fixed `max_rounds=56`).
- Run X147 (v0.2.22, max_rounds=18, batch_size=4, branching, run `zca2ko013oesiexcl6bsivs5`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, 120 turns, plan length always 2 (2-action: 120/120), invalid_plan=0, choose_out_of_range=0. Action mix remained near parity but slightly upgrade-leaning overall (upgrade=124, build=116, noop=0) with upgrade-skewed candidate availability (upgrade=371 vs build=277; noop candidates=120). By phase (`round_phase` from observation): mid build 37 vs upgrade 11 (**mid remains build-heavy**), late build 79 vs upgrade 113 (**late upgrade-leaning with build presence**, ~43.0% upgrade lead; build share ~41.1%) - **plan quality partial** (late direction/build presence are correct, but lead is above the preferred 15-25% band and mid remains not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 72/72; fail=0; missing=0); cap-bound checks at round 18 were clean (`delta_round=1` in 24/24; delta0=0). Reward/mean min ~906.15, max ~1887.35, last ~1178.70; format reward 1.0; truncation 0; completion_len/mean min ~2740.75, max ~8012.0, last ~4037.25; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X148 (v0.2.22, max_rounds=56, batch_size=1, branching, run `aewnwzxha7me4jtb8egswahe`) completed with samples at steps 0/10/20/30/40/50 (step samples: 1/1/1/1/1/1). Parsed all rollouts and all turns: 6 samples, 132 turns, plan length mixed (2-action: 111/132; 1-action: 21/132), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=116, build=23, noop=104) with similarly skewed candidate availability (upgrade=126 vs build=40; noop candidates=132). By phase (`round_phase` from observation; effectively late-only): late build 23 vs upgrade 116 with noop 104 (**late over-upgrade**, ~404.3% upgrade lead; build share ~16.5% over build+upgrade actions) - **plan quality fail** adaptive late target (upgrade lead far above band). Round progression accounting: non-cap checks passed (`delta_round == 1` for 121/121; fail=0; missing=0); cap-bound checks at round 56 were clean (`delta_round=1` in 5/5; delta0=0). Reward/mean min ~-199.10, max ~16095.10, last ~12805.90; format reward 1.0; truncation 0; completion_len/mean min ~1556.0, max ~20324.0, last ~17278.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality FAIL; horizon lower-bound PASS (`true horizon >= 56` on cap-hit samples); reliability PASS.
- Decision update (2026-02-11): X147 (exact X145 replicate) did not reproduce X145’s in-band late mix; late upgrade lead moved from ~19.0% back up to ~43.0%, so behavior closure guardrail remains unmet and the lane stays PARTIAL.
- Decision update (2026-02-11): X148 one-variable payload-relax canary (`max_action_candidates` 2 -> 3 from X146) preserved full sample-step coverage, no upload 500s, and clean progression at cap 56 despite high completion payload (completion_len/mean max ~20.3k), supporting cautious continued payload relaxation via single-knob canaries.
- Decision update (2026-02-11): Strict collab deliberation consensus validated expanding horizon for more rollout volume via one-variable `batch_size` increase on the X148 base, while keeping behavior lane as a one-variable micro-correction to avoid circling.
- Decision update (2026-02-11): Launched X149 behavior-lane probe with run `s5lcowlkjp9xxbqcea0dtpbo` using `configs/lab/prime-td-macro-round-60-x149.toml` (one-variable change from X147: late `min_build_frac` 0.3580 -> 0.3590).
- Decision update (2026-02-11): Launched X150 horizon-lane rollout-volume canary with run `oai6pqzwjjok3wtnksh255ng` using `configs/lab/prime-td-macro-round-60-x150.toml` (one-variable change from X148: `batch_size` 1 -> 2 at fixed `max_rounds=56`).
- Run X149 (v0.2.22, max_rounds=18, batch_size=4, branching, run `s5lcowlkjp9xxbqcea0dtpbo`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, 112 turns, plan length always 2 (2-action: 112/112), invalid_plan=0, choose_out_of_range=0. Action mix was near parity and slightly build-leaning overall (build=113, upgrade=107, noop=4) with upgrade-skewed candidate availability (upgrade=351 vs build=262; noop candidates=112). By phase (`round_phase` from observation): mid build 30 vs upgrade 10 (**mid remains build-heavy**), late build 83 vs upgrade 97 with noop 4 (**late upgrade-leaning with build presence**, ~16.9% upgrade lead; build share ~46.1%) - **plan quality partial** (late target band met, but mid remains not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 64/64; fail=0; missing=0); cap-bound checks at round 18 were clean (`delta_round=1` in 24/24; delta0=0). Reward/mean min ~885.90, max ~1888.60, last ~1383.00; format reward 1.0; truncation 0; completion_len/mean min ~2780.0, max ~7862.25, last ~5221.75; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X150 (v0.2.22, max_rounds=56, batch_size=2, branching, run `oai6pqzwjjok3wtnksh255ng`) completed with samples at steps 0/10/20/30/40/50 (step samples: 2/2/2/2/2/2). Parsed all rollouts and all turns: 12 samples, 277 turns, plan length mixed (2-action: 229/277; 1-action: 32/277; 0-action: 16/277), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=231, build=45, noop=214) with similarly skewed candidate availability (upgrade=266 vs build=75; noop candidates=277). By phase (`round_phase` from observation; effectively late-only): late build 45 vs upgrade 231 with noop 214 (**late over-upgrade**, ~413.3% upgrade lead; build share ~16.3% over build+upgrade actions) - **plan quality fail** adaptive late target (upgrade lead far above band). Round progression accounting: non-cap checks passed (`delta_round == 1` for 255/255; fail=0; missing=0); cap-bound checks at round 56 were clean (`delta_round=1` in 10/10; delta0=0). Reward/mean min ~1066.65, max ~15882.60, last ~9179.90; format reward 1.0; truncation 0; completion_len/mean min ~6551.5, max ~20327.0, last ~18572.0; error/mean showed a transient spike (max 0.5, last 0.0) aligned with a single recovered server sync failure in logs (no upload failures). No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality FAIL; horizon lower-bound PASS (`true horizon >= 56` on cap-hit samples); reliability PASS (transient infra warning recovered).
- Decision update (2026-02-11): X149 one-variable behavior micro-correction from X147 (`late min_build_frac` 0.3580 -> 0.3590) moved late behavior back into the preferred 15-25% band (~16.9%) while preserving clean progression/reliability, but behavior closure remains PARTIAL because mid-phase is still build-heavy and prior replicate variance remains unresolved.
- Decision update (2026-02-11): X150 one-variable horizon rollout-volume canary (`batch_size` 1 -> 2 from X148) doubled sampled rollout volume (6 -> 12 total samples across checkpoints) with full step coverage and no upload 500s at cap 56, supporting cautious further horizon expansion for rollout depth/volume under single-knob controls.
- Decision update (2026-02-11): Strict collab deliberation tie-break consensus selected a reproducibility guardrail pair as the best non-circular next step: X151 exact X149 replicate (behavior lane) + X152 exact X150 replicate (horizon lane), deferring `batch_size` expansion until X150 reliability signal is reproduced.
- Decision update (2026-02-11): Launched X151 behavior-lane reproducibility replicate with run `l5pntxgckrs709679ko20fla` using `configs/lab/prime-td-macro-round-60-x151.toml` (exact X149 replicate).
- Decision update (2026-02-11): Launched X152 horizon-lane reproducibility replicate with run `xu9lgpqi2qr3m1vq8oyw3nmd` using `configs/lab/prime-td-macro-round-60-x152.toml` (exact X150 replicate).
- Run X151 (v0.2.22, max_rounds=18, batch_size=4, branching, run `l5pntxgckrs709679ko20fla`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, 128 turns, plan length always 2 (2-action: 128/128), invalid_plan=0, choose_out_of_range=0. Action mix was upgrade-leaning overall (upgrade=143, build=108, noop=5) with upgrade-skewed candidate availability (upgrade=392 vs build=266; noop candidates=128). By phase (`round_phase` from observation): mid build 39 vs upgrade 17 (**mid remains build-heavy**), late build 69 vs upgrade 126 with noop 5 (**late upgrade-leaning with build presence**, ~82.6% upgrade lead; build share ~35.4%) - **plan quality partial** (late direction/build presence are correct, but lead is above the preferred 15-25% band and mid remains not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 80/80; fail=0; missing=0); cap-bound checks at round 18 were clean (`delta_round=1` in 24/24; delta0=0). Reward/mean min ~897.90, max ~1877.10, last ~1372.00; format reward 1.0; truncation 0; completion_len/mean min ~2721.75, max ~7890.0, last ~5100.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X152 (v0.2.22, max_rounds=56, batch_size=2, branching, run `xu9lgpqi2qr3m1vq8oyw3nmd`) completed with samples at steps 0/10/20/30/40/50 (step samples: 2/2/2/2/2/2). Parsed all rollouts and all turns: 12 samples, 237 turns, plan length mixed (2-action: 114/237; 1-action: 123/237), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=218, build=37, noop=96) with similarly skewed candidate availability (upgrade=226 vs build=63; noop candidates=237). By phase (`round_phase` from observation; effectively late-only): late build 37 vs upgrade 218 with noop 96 (**late over-upgrade**, ~489.2% upgrade lead; build share ~14.5% over build+upgrade actions) - **plan quality fail** adaptive late target (upgrade lead far above band). Round progression accounting: non-cap checks passed (`delta_round == 1` for 216/216; fail=0; missing=0); cap-bound checks at round 56 were clean (`delta_round=1` in 9/9; delta0=0). Reward/mean min ~437.20, max ~15831.10, last ~14566.50; format reward 1.0; truncation 0; completion_len/mean min ~2616.0, max ~20324.0, last ~18778.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage; logs showed only transient environment-server readiness warnings during startup and then recovered. **Criteria verdict:** round progression PASS; plan quality FAIL; horizon lower-bound PASS (`true horizon >= 56` on 9 cap-hit samples); reliability PASS.
- Decision update (2026-02-11): X151 (exact X149 replicate) did not reproduce X149’s in-band late mix; late upgrade lead moved from ~16.9% (X149) to ~82.6% with mid still build-heavy, so behavior closure guardrail remains unmet and the lane stays PARTIAL.
- Decision update (2026-02-11): X152 (exact X150 replicate) reproduced horizon-lane reliability at cap 56 with full sample-step coverage, no upload 500s, and clean non-cap progression while preserving 12 sampled rollouts; this confirms X150’s rollout-volume reliability signal and supports a cautious one-variable horizon-volume expansion next.
- Decision update (2026-02-11): Approved next pair launched under lane-separation guardrails: X153 exact X149 replicate (behavior reproducibility check) + X154 one-variable horizon rollout-volume expansion from X152 (`batch_size` 2 -> 3) at fixed cap/payload controls.
- Decision update (2026-02-11): Launched X153 behavior-lane reproducibility replicate with run `sq6662jz8jhcblqhqh2yxdnh` using `configs/lab/prime-td-macro-round-60-x153.toml` (exact X149 replicate).
- Decision update (2026-02-11): Launched X154 horizon-lane rollout-volume expansion with run `nl6uhyk08o5p4x9w86p1inld` using `configs/lab/prime-td-macro-round-60-x154.toml` (one-variable change from X152: `batch_size` 2 -> 3 at fixed `max_rounds=56` and payload controls).
- Run X153 (v0.2.22, max_rounds=18, batch_size=4, branching, run `sq6662jz8jhcblqhqh2yxdnh`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, 120 turns, plan length always 2 (2-action: 120/120), invalid_plan=0, choose_out_of_range=0. Action mix was near parity and slightly build-leaning overall (build=120, upgrade=117, noop=3) with upgrade-skewed candidate availability (upgrade=362 vs build=260; noop candidates=120). By phase (`round_phase` from observation): mid build 34 vs upgrade 14 (**mid remains build-heavy**), late build 86 vs upgrade 103 with noop 3 (**late upgrade-leaning with build presence**, ~19.8% upgrade lead; build share ~45.5%) - **plan quality partial** (late target band met, but mid remains not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 72/72; fail=0; missing=0); cap-bound checks at round 18 were clean (`delta_round=1` in 24/24; delta0=0). Reward/mean min ~915.65, max ~1912.35, last ~1392.00; format reward 1.0; truncation 0; completion_len/mean min ~2815.25, max ~7801.25, last ~5339.25; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage; logs contained only transient startup/event-loop warnings that self-recovered. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X154 (v0.2.22, max_rounds=56, batch_size=3, branching, run `nl6uhyk08o5p4x9w86p1inld`) completed with samples at steps 0/10/20/30/40/50 (step samples: 3/3/3/3/3/3). Parsed all rollouts and all turns: 18 samples, 361 turns, plan length mixed (2-action: 243/361; 1-action: 118/361), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=328, build=60, noop=216) with similarly skewed candidate availability (upgrade=343 vs build=102; noop candidates=361). By phase (`round_phase` from observation; effectively late-only): late build 60 vs upgrade 328 with noop 216 (**late over-upgrade**, ~446.7% upgrade lead; build share ~15.5% over build+upgrade actions) - **plan quality fail** adaptive late target (upgrade lead far above band). Round progression accounting: non-cap checks passed (`delta_round == 1` for 333/333; fail=0; missing=0); cap-bound checks at round 56 were clean (`delta_round=1` in 10/10; delta0=0). Reward/mean min ~1573.53, max ~15455.43, last ~10285.63; format reward 1.0; truncation 0; completion_len/mean min ~7647.0, max ~20317.0, last ~17826.0; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage; logs contained only transient startup/event-loop warnings that self-recovered. **Criteria verdict:** round progression PASS; plan quality FAIL; horizon lower-bound PASS (`true horizon >= 56` on 10 cap-hit samples); reliability PASS.
- Decision update (2026-02-11): X153 (exact X149 replicate) re-entered the preferred late band (~19.8%) with clean progression/reliability, but behavior closure remains PARTIAL because mid-phase is still build-heavy and the in-band late mix has not yet been reproduced in two consecutive behavior runs.
- Decision update (2026-02-11): X154 one-variable horizon rollout-volume expansion (`batch_size` 2 -> 3 from X152) increased sampled rollout volume from 12 -> 18 with full sample-step coverage, no upload 500s, and clean non-cap progression at cap 56; this is positive but should be replicated once before further volume expansion to satisfy the anti-circling two-consecutive guardrail.
- Decision update (2026-02-11): Collab deliberation consensus validated the next pair as guardrail-consistent and non-circular: X155 exact X153 replicate (behavior reproducibility confirmation) + X156 exact X154 replicate (horizon `batch_size=3` reproducibility confirmation) before any additional knob changes.
- Decision update (2026-02-11): Launched X155 behavior-lane reproducibility replicate with run `z9ez3pbo5vynfnbfp0bam78y` using `configs/lab/prime-td-macro-round-60-x155.toml` (exact X153 replicate).
- Decision update (2026-02-11): Launched X156 horizon-lane reproducibility replicate with run `nm9p0xh7byfym6xmwj0y6u4f` using `configs/lab/prime-td-macro-round-60-x156.toml` (exact X154 replicate at `batch_size=3`).
- Run X155 (v0.2.22, max_rounds=18, batch_size=4, branching, run `z9ez3pbo5vynfnbfp0bam78y`) completed with sample rollouts retrieved at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all retrieved rollouts and all turns: 24 samples, 112 turns, plan length mostly 2 (2-action: 110/112; 1-action: 2/112), invalid_plan=0, choose_out_of_range=0. Action mix was upgrade-leaning overall (upgrade=130, build=90, noop=2) with upgrade-skewed candidate availability (upgrade=365 vs build=220; noop candidates=112). By phase (`round_phase` from observation): mid build 23 vs upgrade 15 (**mid remains build-heavy**), late build 67 vs upgrade 115 with noop 2 (**late upgrade-leaning with build presence**, ~71.6% upgrade lead; build share ~36.8%) - **plan quality partial** (late direction/build presence are correct, but lead is above the preferred 15-25% band and mid remains not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 64/64; fail=0; missing=0); cap-bound checks at round 18 were clean (`delta_round=1` in 24/24; delta0=0). Reward/mean min ~888.40, max ~1886.35, last ~1153.70; format reward dipped transiently (min ~0.571, last 1.0); truncation showed a transient spike (max ~0.25, last 0.0); completion_len/mean min ~2806.5, max ~7743.25, last ~4155.0; error/mean remained 0.0. No sample-upload 500s; logs contained only transient startup/event-loop warnings that self-recovered. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS.
- Run X156 (v0.2.22, max_rounds=56, batch_size=3, branching, run `nm9p0xh7byfym6xmwj0y6u4f`) completed with samples at steps 0/10/20/30/40/50 (step samples: 3/3/3/3/3/3). Parsed all rollouts and all turns: 18 samples, 416 turns, plan length mixed (2-action: 221/416; 1-action: 195/416), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=382, build=61, noop=194) with similarly skewed candidate availability (upgrade=399 vs build=101; noop candidates=416). By phase (`round_phase` from observation; effectively late-only): late build 61 vs upgrade 382 with noop 194 (**late over-upgrade**, ~526.2% upgrade lead; build share ~13.8% over build+upgrade actions) - **plan quality fail** adaptive late target (upgrade lead far above band). Round progression accounting: non-cap checks passed (`delta_round == 1` for 384/384; fail=0; missing=0); cap-bound checks at round 56 were clean (`delta_round=1` in 14/14; delta0=0). Reward/mean min ~1545.57, max ~15449.10, last ~10334.50; format reward 1.0; truncation 0; completion_len/mean min ~10556.67, max ~20318.0, last ~15883.33; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage; logs contained only transient startup/event-loop warnings that self-recovered. **Criteria verdict:** round progression PASS; plan quality FAIL; horizon lower-bound PASS (`true horizon >= 56` on 14 cap-hit samples); reliability PASS.
- Decision update (2026-02-11): X155 (exact X153 replicate) did not reproduce X153’s in-band late mix; late upgrade lead moved from ~19.8% (X153) to ~71.6%, so behavior closure guardrail remains unmet and behavior lane stays PARTIAL.
- Decision update (2026-02-11): X156 (exact X154 replicate) reproduced `batch_size=3` horizon reliability/volume at cap 56 (18 samples, no upload 500s, clean progression), satisfying two consecutive reliable runs for this volume setting and enabling cautious next-step horizon expansion under one-variable controls.
- Decision update (2026-02-11): Strict collab deliberation consensus validated the next pair as guardrail-consistent: X157 exact X153 replicate (behavior reproducibility) + X158 one-variable horizon rollout-volume expansion from X156 (`batch_size` 3 -> 4), with mandatory pre-launch diff checks to prevent multi-knob drift.
- Decision update (2026-02-11): Launched X157 behavior-lane reproducibility replicate with run `p7dphhqilb3opjdhp4d6umzk` using `configs/lab/prime-td-macro-round-60-x157.toml` (exact X153 replicate).
- Decision update (2026-02-11): Launched X158 horizon-lane rollout-volume expansion with run `ja6pdbymyhguoqe39ohk8bks` using `configs/lab/prime-td-macro-round-60-x158.toml` (one-variable change from X156: `batch_size` 3 -> 4 at fixed `max_rounds=56` and payload controls).
- Run X157 (v0.2.22, max_rounds=18, batch_size=4, branching, run `p7dphhqilb3opjdhp4d6umzk`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, 132 turns, plan length always 2 (2-action: 132/132), invalid_plan=0, choose_out_of_range=0. Action mix was near parity and slightly build-leaning overall (build=132, upgrade=131, noop=1) with upgrade-skewed candidate availability (upgrade=390 vs build=265; noop candidates=132). By phase (`round_phase` from observation): mid build 52 vs upgrade 8 (**mid remains build-heavy**), late build 80 vs upgrade 123 with noop 1 (**late upgrade-leaning with build presence**, ~53.8% upgrade lead; build share ~39.4%) - **plan quality partial** (late direction/build presence are correct but lead is above the preferred 15-25% band, and mid is not mixed). Round progression accounting: non-cap checks passed (`delta_round == 1` for 84/84; fail=0; missing=0); cap-bound checks at round 18 were clean (`delta_round=1` in 24/24; delta0=0). Reward/mean min ~913.65, max ~1879.60, last ~1361.00; format reward 1.0; truncation 0; completion_len/mean min ~2755.75, max ~7963.25, last ~5336.50; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage; logs showed only transient startup/checkpoint warnings that self-recovered. **Criteria verdict:** round progression PASS; plan quality PARTIAL; reliability PASS; episode length remains cap-limited/inconclusive at 18.
- Run X158 (v0.2.22, max_rounds=56, batch_size=4, branching, run `ja6pdbymyhguoqe39ohk8bks`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4). Parsed all rollouts and all turns: 24 samples, 430 turns, plan length mixed (2-action: 356/430; 1-action: 74/430), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=375, build=87, noop=324) with similarly skewed candidate availability (upgrade=406 vs build=150; noop candidates=430). By phase (`round_phase` from observation; effectively late-only): late build 87 vs upgrade 375 with noop 324 (**late over-upgrade**, ~331.0% upgrade lead; build share ~18.8% over build+upgrade actions) - **plan quality fail** adaptive late target (upgrade lead far above band). Round progression accounting: non-cap checks passed (`delta_round == 1` for 393/393; fail=0; missing=0); cap-bound checks at round 56 were clean (`delta_round=1` in 13/13; delta0=0). Reward/mean min ~1845.52, max ~14540.75, last ~11608.20; format reward 1.0; truncation 0; completion_len/mean min ~7613.50, max ~20181.67, last ~18679.25; error/mean remained 0.0. No sample-upload 500s and full sample-step coverage; logs showed two transient scheduler warnings (`Cancelled 1 old rollout requests`) that self-recovered. **Criteria verdict:** round progression PASS; plan quality FAIL; horizon lower-bound PASS (`true horizon >= 56` on 13 cap-hit samples); reliability PASS.
- Decision update (2026-02-11): X157 (exact X153 replicate) did not reproduce X153’s in-band late behavior (late upgrade lead moved from ~19.8% to ~53.8%) and mid phase remained build-heavy, so behavior closure guardrail is still unmet and behavior lane remains PARTIAL.
- Decision update (2026-02-11): X158 one-variable horizon rollout-volume expansion (`batch_size` 3 -> 4 from X156) increased sampled rollout volume from 18 -> 24 with full sample-step coverage, no upload 500s, and clean non-cap progression at cap 56; this is positive but still needs one exact replicate at `batch_size=4` before any further horizon-volume expansion under the two-consecutive guardrail.
- Decision update (2026-02-11): Standardized transfer cadence gate (Option 4) to use canonical cross-repo command `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --out output/transfer/<run_id>.json --json` with canonical metrics: `core_completion_rate` (primary), `waves_survived_mean`, `waves_survived_p10`, `base_hp_loss_mean`, `leftover_cash_mean`, `invalid_action_rate`, `stall_timeout_rate`, `determinism_replay_match_rate`.
- Decision update (2026-02-11): Transfer gate status is **PENDING (platform task required)** because `/Users/kbediako/Code/tower-defence` currently has no `benchmark:transfer` script (`npm run benchmark:transfer` returns “Missing script”); this is now tracked as required implementation work in that repo before transfer-pass/fail claims.
- Decision update (2026-02-11): Pre-launch pair framing approved under anti-circling + one-variable rules. `goal_link`: stabilize behavior reproducibility while confirming horizon `batch_size=4` reliability for transfer-ready training confidence. `hypothesis`: lowering behavior `sampling.temperature` from 0.60 to 0.55 reduces late-mix variance without collapsing direction, while an exact horizon replicate reproduces no-500/full-coverage reliability. `success_metric`: PASS = both runs diagnostic, behavior late 15-25% upgrade lead with build floor, clean progression/reliability; PARTIAL = diagnostic but behavior out-of-band; FAIL = any non-diagnostic run or behavior direction collapse. `stop_condition`: if behavior remains out-of-band for two additional runs after this lever switch, pivot to a different behavior lever; if horizon reliability regresses, rollback to the last reliable payload setting.
- Decision update (2026-02-11): Launched X159 behavior-lane one-variable lever switch with run `vz4416kc15kygnzmcdtqd8a6` using `configs/lab/prime-td-macro-round-60-x159.toml` (one-variable change from X157: `sampling.temperature` 0.60 -> 0.55).
- Decision update (2026-02-11): Launched X160 horizon-lane reliability replicate with run `tltide8qyzrlveqvrkadwfun` using `configs/lab/prime-td-macro-round-60-x160.toml` (exact functional replicate of X158 at `batch_size=4`, cap/payload unchanged).
- Decision update (2026-02-11): Benchmark-hardening is now a required **platform track** before any benchmark-closure claims. Non-blocking carveout remains: config-only replicate runs (including X160) may proceed while this track is in progress; any env/harness code change requires transfer eval before further non-replicate launches.
- Decision update (2026-02-11): Required benchmark-hardening scope for transfer-gate closure: (1) add provenance fields in outputs/observations (`benchmark_pack`, `benchmark_scenario`, `benchmark_version`, `run_config_id`/config filename); (2) emit deterministic state hashes per step/turn plus final state; (3) explicitly version action/observation schemas; (4) normalize replay artifacts for cross-repo transfer ingestion; (5) wire canonical transfer-eval status into run notes/results so gating decisions are explicit.
- Run X159 (v0.2.22, max_rounds=18, batch_size=4, branching, run `vz4416kc15kygnzmcdtqd8a6`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4; coverage 100% each). Pulled rollouts at every sampled step with `limit=32`, parsed all rollouts and all turns: 24 samples, 104 assistant turns, plan length always 2 (2-action: 104/104), invalid_plan=0, choose_out_of_range=0. Action mix was near parity and slightly build-leaning overall (build=104, upgrade=100, noop=4) with upgrade-skewed candidate availability (upgrade=337 vs build=246; noop candidates=104). By phase (`round_phase` from observation): mid build 27 vs upgrade 5, late build 77 vs upgrade 95 with noop 4 (**late upgrade-leaning with build presence**, ~23.4% upgrade lead; build share ~44.8%) - **plan quality PASS** for the current late-band gate. Full delta accounting: non-cap checks passed (`delta_round == 1` for 56/56; fail=0; missing=0); cap-bound checks at round 18 were split (`delta_round=0` in 24/48, `delta_round=1` in 24/48). Metrics: reward/mean min ~732.89, max ~1876.85, last ~1171.45; format reward min 0.5 max 1.0 last 1.0; truncation mean min 0.0 max 0.25 last 0.0; completion_len/mean min ~2769.33 max ~7785.25 last ~4123.75; error/mean min 0.0 max 0.25 last 0.0. Reliability notes: no sample-upload 500s, no backoff-limit/stall warnings; one informational interleaving warning in logs. **Criteria verdict:** progression PASS; plan quality PASS; reliability `diagnostic`; horizon lower-bound N/A (behavior lane).
- Run X160 (v0.2.22, max_rounds=56, batch_size=4, branching, run `tltide8qyzrlveqvrkadwfun`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4; coverage 100% each). Pulled rollouts at every sampled step with `limit=32`, parsed all rollouts and all turns: 24 samples, 537 assistant turns, plan lengths mixed (2-action: 334/537; 1-action: 203/537), invalid_plan=0, choose_out_of_range=0. Action mix remained strongly upgrade-dominant (upgrade=483, build=90, noop=298) with similarly skewed candidate availability (upgrade=516 vs build=147; noop candidates=537). Phase breakdown (late-only): late build 90 vs upgrade 483 with noop 298 (**late over-upgrade**, ~436.7% upgrade lead; build share ~15.7%) - **plan quality FAIL** adaptive late target. Full delta accounting: non-cap checks were 493/497 pass with **4 non-cap `delta_round=0` failures** (all terminal events with lives <= 0 at rounds 39, 55, 33, 38); non-cap missing=0. Cap-bound checks at round 56 were split (`delta_round=0` in 20/40, `delta_round=1` in 20/40). Metrics: reward/mean min ~1368.07, max ~15283.60, last ~6043.75; format reward 1.0 throughout; truncation 0; completion_len/mean min ~6470.50 max ~20332.50 last ~19266.75; error/mean 0.0 throughout. Reliability notes: no sample-upload 500s, no backoff-limit/stall/interleaving warnings. **Criteria verdict:** progression PARTIAL (terminal non-cap delta failures); plan quality FAIL; reliability `non_diagnostic` (delta failures violate diagnostic policy despite full coverage/no 500s); horizon lower-bound PASS (`true horizon >= 56` on cap-hit samples).
- Decision update (2026-02-11): X159 delivered a first in-band, diagnostic behavior run under the temperature lever switch (`0.60 -> 0.55`), but behavior-lane closure remains open because closure requires two consecutive in-band diagnostic runs.
- Decision update (2026-02-11): X160 did not satisfy diagnostic reliability due non-cap delta failures; by policy this run is non-diagnostic, so no directional policy claims should be taken from it despite clean coverage and no upload 500s.
- Decision update (2026-02-11): Canonical transfer-eval status against latest `/Users/kbediako/Code/tower-defence` remains **PENDING**; `npm run benchmark:transfer -- --help` still fails (`Missing script: benchmark:transfer`), so canonical transfer metrics are unavailable (all set N/A pending implementation).
- Direction scorecard (2026-02-11, after X159/X160): `training_quality=PARTIAL` (behavior improved but not closed; horizon still over-upgrade), `reliability=PARTIAL` (one diagnostic + one non_diagnostic), `horizon_confidence=PARTIAL` (lower-bound evidence present but latest run non-diagnostic), `transfer_readiness=PENDING` (canonical transfer harness not yet implemented).
- Decision update (2026-02-11): **Hold launches** pending `$collab-deliberation` because latest pair includes a `non_diagnostic` run (X160), which triggers mandatory deliberation before proposing the next run pair. Keep reliability classification separate from policy quality and avoid advancing strategy from X160 signals.
- Decision update (2026-02-11): `$collab-deliberation` completed. Options considered: (1) keep holding and only do platform hardening, (2) run a new-lever pair, (3) run exact reproducibility replicates of X159/X160. Recommendation selected option (3) to maximize causal clarity under guardrails.
- Decision update (2026-02-11): Open-question resolutions formalized: Q1 keep strict non-cap progression rule (`delta_round == 1` required after turn 1; terminal non-cap failures still count), Q2 keep mid-phase 45-55 as secondary until late-band reproducibility closure is stable, Q3 yes - "queue platform task" means explicitly queue benchmark-hardening as a required platform track (non-blocking for config-only replicates, blocking for env/harness code changes without transfer eval).
- Decision update (2026-02-11): Pre-launch pair framing approved under anti-circling + one-variable rules. `goal_link`: improve reliability confidence and transfer readiness by testing reproducibility instead of introducing new knobs after a non-diagnostic horizon run. `hypothesis`: X161 replicates X159 in-band behavior with diagnostic reliability, and X162 clarifies whether X160 terminal non-cap delta failures persist under exact replay. `success_metric`: PASS = both runs diagnostic with clean non-cap deltas and X161 late in-band (15-25% upgrade lead with build presence); PARTIAL = exactly one diagnostic_with_caution and no regressions; FAIL = any non-diagnostic run, upload 500 regression, or repeated non-cap delta failures. `stop_condition`: if behavior reproducibility fails for three behavior runs total, pivot levers; if X162 repeats non-cap delta failures, halt horizon expansion and pivot to reliability root-cause work.
- Decision update (2026-02-11): Launched X161 behavior-lane reproducibility replicate with run `sitfcmyb6bm63m6q12itbo1v` using `configs/lab/prime-td-macro-round-60-x161.toml` (exact replicate of X159).
- Decision update (2026-02-11): Launched X162 horizon-lane reproducibility replicate with run `dbgueiezjchg9hiqwr55xst0` using `configs/lab/prime-td-macro-round-60-x162.toml` (exact replicate of X160 at `batch_size=4`, `max_rounds=56`).
- Decision update (2026-02-12): Canonical transfer command is now implemented on `/Users/kbediako/Code/tower-defence` `main` at commit `64fc010`. Verified locally: `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --json` returns canonical metrics + provenance/schema fields and explicit gate fields.
- Decision update (2026-02-12): Transfer gate remains **PENDING** (not blocked) because baseline deltas are not yet established; tool reports `gate_status=pending`, `gate_reason=\"Baseline metrics unavailable for transfer delta thresholds\"`. Latest canonical metrics: `core_completion_rate=1.0`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1.0`.
- Run X161 (v0.2.22, max_rounds=18, batch_size=4, branching, run `sitfcmyb6bm63m6q12itbo1v`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4; coverage 100% each). Pulled rollouts for every sampled step at max page coverage (`--limit 100`), parsed all rollouts and all turns: 24 samples, 126 turns, plan lengths 2-action=125 and 1-action=1, invalid_plan=0, choose_out_of_range=0. Action mix build/upgrade/noop=104/143/4; candidate pool build/upgrade/noop=278/392/126. Phase breakdown: mid build/upgrade/noop=35/21/1 and late build/upgrade/noop=69/122/3 (late upgrade lead ~76.8%, build share ~36.1%) - **plan quality FAIL** (late outside preferred 15-25% band). Full delta accounting (post-turn observations): non-cap pass/fail/missing=56/0/0; cap delta1/delta0/other=23/23/0. Metrics: reward/mean min ~898.90, max ~1857.10, last ~1603.80; format reward min ~0.571 max 1.0 last 1.0; truncation min 0.0 max 0.25 last 0.0; completion_len/mean min ~2741.50 max ~7823.0 last ~6541.25; error/mean min 0.0 max 0.25 last 0.0. Reliability notes: no sample-upload 500s, no interleaving warnings, full-turn parsing complete. **Criteria verdict:** progression PASS; plan quality FAIL; reliability `diagnostic`; horizon lower-bound N/A (behavior lane).
- Run X162 (v0.2.22, max_rounds=56, batch_size=4, branching, run `dbgueiezjchg9hiqwr55xst0`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4; coverage 100% each). Pulled rollouts for every sampled step at max page coverage (`--limit 100`), parsed all rollouts and all turns: 24 samples, 515 turns, plan lengths 2-action=273 and 1-action=242, invalid_plan=0, choose_out_of_range=0. Action mix build/upgrade/noop=84/467/237; candidate pool build/upgrade/noop=133/494/515. Phase breakdown (late-only): build/upgrade/noop=84/467/237 (late upgrade lead ~456.0%, build share ~15.2%) - **plan quality FAIL** adaptive late target. Full delta accounting (post-turn observations): non-cap pass/fail/missing=448/5/0, with 5 non-cap `delta_round=0` failures (all terminal, lives <= 0; rounds 37, 52, 42, 37, 39); cap delta1/delta0/other=19/19/0. Metrics: reward/mean min ~1589.50, max ~15211.80, last ~11142.63; format reward 1.0 throughout; truncation 0 throughout; completion_len/mean min ~8359.50 max ~20166.0 last ~17962.50; error/mean min 0.0 max 0.5 last 0.0. Reliability notes: no sample-upload 500s, no interleaving warnings, full-turn parsing complete. **Criteria verdict:** progression PARTIAL (terminal-only non-cap delta failures); plan quality FAIL; reliability `non_diagnostic` (delta failures violate diagnostic policy); horizon lower-bound PASS (`true horizon >= 56` on cap-hit samples).
- Direction scorecard (2026-02-12, after X161/X162): `training_quality=PARTIAL` (both runs late out-of-band), `reliability=PARTIAL` (one diagnostic + one non_diagnostic), `horizon_confidence=PARTIAL` (cap-hit lower bound present but latest horizon run non-diagnostic), `transfer_readiness=PENDING` (canonical command implemented; baseline gate thresholds pending).
- Decision update (2026-02-12): **Hold launches** pending `$collab-deliberation` because latest pair still includes a `non_diagnostic` run (X162) and behavior reproducibility regressed from X159 to X161; per guardrails, do not advance direction from this pair without deliberation/pivot framing.
- Decision update (2026-02-12): `$collab-deliberation` completed for next-step choice; selected Option 4 (concurrent one-variable pivots in behavior + horizon lanes) instead of full hold.
- Decision update (2026-02-12): Open-question resolutions finalized for this cycle: Q1 keep strict non-cap progression rule (terminal non-cap `delta_round != 1` still counts as failure); Q2 transfer-baseline calibration window is 3 canonical transfer runs on identical code state before activating delta-threshold blocks; Q3 choose horizon lever `max_towers` (2 -> 3) rather than cap pivot to preserve horizon comparability.
- Decision update (2026-02-12): Pre-launch pair framing approved under anti-circling + one-variable rules. `goal_link`: recover behavior reproducibility while reducing horizon terminal-collapse pressure without cap/payload expansion. `hypothesis`: X163 temperature reduction (0.55 -> 0.45) narrows late-mix variance; X164 `max_towers` increase (2 -> 3) reduces terminal non-cap delta failures at cap 56. `success_metric`: PASS = X163 diagnostic + late in-band (15-25% upgrade lead) and X164 diagnostic + clean non-cap deltas; PARTIAL = one diagnostic and no reliability regression; FAIL = any non-diagnostic run or no targeted-signal improvement. `stop_condition`: if behavior stays out-of-band across 3 post-switch runs, pivot lever family; if X164 repeats non-cap delta failures, halt horizon expansion and pivot reliability lever.
- Decision update (2026-02-12): Launched X163 behavior-lane variance-control pivot with run `j5f7b535x4vdjx5e1uk23wjo` using `configs/lab/prime-td-macro-round-60-x163.toml` (one-variable change from X161: `sampling.temperature` 0.55 -> 0.45).
- Decision update (2026-02-12): Launched X164 horizon-lane terminal-pressure pivot with run `ted0hohwpwtrfeldvpbquz1t` using `configs/lab/prime-td-macro-round-60-x164.toml` (one-variable change from X162: `observation.max_towers` 2 -> 3).
- Run X163 (v0.2.22, max_rounds=18, batch_size=4, branching, run `j5f7b535x4vdjx5e1uk23wjo`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4; coverage 100% each). Pulled rollouts for every sampled step at max page coverage (`--limit 100`), parsed all rollouts and all turns: 24 samples, 124 turns, plan lengths 2-action=123 and 1-action=1, invalid_plan=0, choose_out_of_range=0. Action mix build/upgrade/noop=103/135/9; candidate pool build/upgrade/noop=255/380/124. Phase breakdown: mid build/upgrade/noop=34/17/0 and late build/upgrade/noop=69/118/9 (late upgrade lead ~71.0%, build share ~36.9%) - **plan quality FAIL** (late outside preferred 15-25% band). Full delta accounting (post-turn observations): non-cap pass/fail/missing=52/0/0; cap delta1/delta0/other=24/24/0. Metrics: reward/mean min ~911.90, max ~1910.10, last ~1148.45; format reward 1.0 throughout; truncation 0 throughout; completion_len/mean min ~2868.33 max ~7782.0 last ~4075.25; error/mean 0.0 throughout. Reliability notes: no sample-upload 500s, no interleaving warnings, full-turn parsing complete. **Criteria verdict:** progression PASS; plan quality FAIL; reliability `diagnostic`; horizon lower-bound N/A (behavior lane).
- Run X164 (v0.2.22, max_rounds=56, batch_size=4, branching, run `ted0hohwpwtrfeldvpbquz1t`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4; coverage 100% each). Pulled rollouts for every sampled step at max page coverage (`--limit 100`), parsed all rollouts and all turns: 24 samples, 593 turns, plan lengths 2-action=193, 1-action=377, 0-action=23, invalid_plan=0, choose_out_of_range=0. Action mix build/upgrade/noop=86/528/149; candidate pool build/upgrade/noop=137/570/593. Phase breakdown (late-only): build/upgrade/noop=86/528/149 (late upgrade lead ~514.0%, build share ~14.0%) - **plan quality FAIL** adaptive late target. Full delta accounting (post-turn observations): non-cap pass/fail/missing=522/1/0 with one non-cap `delta_round=0` failure (terminal at round 37, lives=-1); cap delta1/delta0/other=23/23/0. Metrics: reward/mean min ~3425.47, max ~12349.90, last ~9978.53; format reward 1.0 throughout; truncation 0 throughout; completion_len/mean min ~14002.25 max ~21514.25 last ~21514.25; error/mean 0.0 throughout. Reliability notes: no sample-upload 500s, no interleaving warnings, full-turn parsing complete. **Criteria verdict:** progression PARTIAL (terminal-only non-cap delta failure); plan quality FAIL; reliability `non_diagnostic` (delta failure violates diagnostic policy); horizon lower-bound PASS (`true horizon >= 56` on cap-hit samples).
- Direction scorecard (2026-02-12, after X163/X164): `training_quality=PARTIAL` (both runs late out-of-band), `reliability=PARTIAL` (one diagnostic + one non_diagnostic), `horizon_confidence=PARTIAL` (cap-hit lower bound present but latest horizon run non-diagnostic), `transfer_readiness=PENDING` (canonical command implemented; baseline calibration window pending completion).
- Decision update (2026-02-12): **Hold launches** pending `$collab-deliberation` because latest pair still includes a `non_diagnostic` run (X164). Keep reliability separate from policy quality and do not advance strategy from this pair without deliberation/pivot framing.
- Decision update (2026-02-12): `$collab-deliberation` completed with operator-approved consensus to proceed on the recommended pair: behavior structural pivot + horizon replicate (one-variable diffs preserved per lane).
- Decision update (2026-02-12): Open-question decisions applied for this cycle: terminal non-cap delta policy remains strict; transfer baseline window remains 3 canonical runs on identical code state before threshold-based blocking; behavior lever family pivots from temperature nudges to structural candidate-cap control.
- Decision update (2026-02-12): Pre-launch pair framing approved under anti-circling + one-variable rules. `goal_link`: reduce behavior late over-upgrade while testing horizon non-cap terminal-failure persistence. `hypothesis`: X165 late `max_upgrade_candidates` 4 -> 3 reduces late upgrade lead; X166 exact replicate of X164 clarifies whether terminal non-cap delta failure is stochastic. `success_metric`: PASS = X165 diagnostic in-band late mix + X166 diagnostic with non-cap fail=0; PARTIAL = one diagnostic with targeted improvement and no infra regression; FAIL = any non-diagnostic regression or no targeted-signal improvement. `stop_condition`: if X165 becomes build-leading or remains >60% late upgrade lead, pivot behavior lever family; if X166 repeats non-cap delta failure, halt horizon expansion and pivot reliability lever.
- Decision update (2026-02-12): Launched X165 behavior-lane structural pivot with run `gb07kbtwfwtttafadalssh28` using `configs/lab/prime-td-macro-round-60-x165.toml` (one-variable change from X163: late `max_upgrade_candidates` 4 -> 3).
- Decision update (2026-02-12): Launched X166 horizon-lane reproducibility replicate with run `vf4mgqrm3sd8kycdsiwek5do` using `configs/lab/prime-td-macro-round-60-x166.toml` (exact replicate of X164 at fixed cap/payload/volume).
- Run X165 (v0.2.22, max_rounds=18, batch_size=4, branching, run `gb07kbtwfwtttafadalssh28`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4; coverage 100% each). Pulled rollouts for every sampled step at max page coverage (`--limit 100`), parsed all rollouts and all turns: 24 samples, 120 turns, plan lengths 2-action=119 and 1-action=1, invalid_plan=0, choose_out_of_range=0. Action mix build/upgrade/noop=119/114/6; candidate pool build/upgrade/noop=263/302/120. Phase breakdown: mid build/upgrade/noop=35/13/0 and late build/upgrade/noop=84/101/6 (late upgrade lead ~20.2%, build share ~45.4%) - **plan quality PASS** (in-band late target with build presence). Full delta accounting (post-turn observations): non-cap pass/fail/missing=48/0/0; cap delta1/delta0/other=24/24/0. Metrics: reward/mean min ~895.90, max ~1877.35, last ~1877.35; format reward 1.0 throughout; truncation 0 throughout; completion_len/mean min ~2640.25 max ~7618.0 last ~7134.25; error/mean 0.0 throughout. Reliability notes: no sample-upload 500s, no interleaving warnings, full-turn parsing complete. **Criteria verdict:** progression PASS; plan quality PASS; reliability `diagnostic`; horizon lower-bound N/A (behavior lane).
- Run X166 (v0.2.22, max_rounds=56, batch_size=4, branching, run `vf4mgqrm3sd8kycdsiwek5do`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4; coverage 100% each). Pulled rollouts for every sampled step at max page coverage (`--limit 100`), parsed all rollouts and all turns: 24 samples, 608 turns, plan lengths 2-action=210, 1-action=375, 0-action=23, invalid_plan=0, choose_out_of_range=0. Action mix build/upgrade/noop=82/547/166; candidate pool build/upgrade/noop=140/584/608. Phase breakdown (late-only): build/upgrade/noop=82/547/166 (late upgrade lead ~567.1%, build share ~13.0%) - **plan quality FAIL** adaptive late target. Full delta accounting (post-turn observations): non-cap pass/fail/missing=536/0/0; cap delta1/delta0/other=24/24/0. Metrics: reward/mean min ~3774.15, max ~13300.12, last ~9553.33; format reward 1.0 throughout; truncation 0 throughout; completion_len/mean min ~14188.25 max ~21511.0 last ~19801.75; error/mean 0.0 throughout. Reliability notes: no sample-upload 500s, no interleaving warnings, full-turn parsing complete. **Criteria verdict:** progression PASS; plan quality FAIL; reliability `diagnostic`; horizon lower-bound PASS (`true horizon >= 56` on cap-hit samples).
- Direction scorecard (2026-02-12, after X165/X166): `training_quality=PARTIAL` (behavior in-band pass; horizon policy still over-upgrade), `reliability=PASS` (both runs diagnostic), `horizon_confidence=PASS` (cap-hit lower-bound + clean progression), `transfer_readiness=PENDING` (transfer baseline calibration window still in progress).
- Decision update (2026-02-12): CLI drift check before X165/X166 analysis showed no command-surface changes but reported available upgrade (`prime` 0.5.34 available; installed 0.5.27); treated as informational/non-blocking for run operations.
- Decision update (2026-02-12): Recommended next pair (not yet launched): X167 exact replicate of X165 to test second consecutive in-band diagnostic behavior closure, plus X168 exact replicate of X166 to establish second consecutive reliable cap56 horizon baseline before any further horizon lever/cap expansion.
- Decision update (2026-02-12): Upgraded CLI with `prime upgrade`; resolved active binary to `prime` 0.5.34. Startup check after upgrade shows minor CLI drift: `prime rl` now includes `restart` command; required `run`/`progress`/`rollouts` surfaces are unchanged and non-blocking for current ops.
- Decision update (2026-02-12): Collab subagent deliberation consensus returned `YES` that X167/X168 is valid under guardrails (no safer alternative): exact behavior replicate for second in-band diagnostic confirmation + exact horizon replicate for second reliable cap56 confirmation.
- Decision update (2026-02-12): Pre-launch pair framing approved under consensus. `goal_link`: validate reproducibility before new lever changes; `hypothesis`: exact X165/X166 replicates reproduce behavior in-band and horizon reliability; `success_metric`: PASS = both runs diagnostic with behavior in-band and horizon non-cap fail=0; `stop_condition`: pivot behavior if out-of-band drift recurs or halt horizon expansion if non-cap delta failures recur.
- Decision update (2026-02-12): Launched X167 behavior-lane reproducibility replicate with run `zjk6i0xtr8vn9u606776k5a5` using `configs/lab/prime-td-macro-round-60-x167.toml` (exact replicate of X165).
- Decision update (2026-02-12): Launched X168 horizon-lane reproducibility replicate with run `rx2y33anr5n30b1ob2a8s88d` using `configs/lab/prime-td-macro-round-60-x168.toml` (exact replicate of X166 at fixed cap/payload/volume).
- Run X167 (v0.2.22, max_rounds=18, batch_size=4, branching, run `zjk6i0xtr8vn9u606776k5a5`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4; coverage 100% each). Pulled rollouts for every sampled step at max page coverage (`--limit 100`), parsed all rollouts and all turns: 24 samples, 128 turns, plan length 2-action=128, invalid_plan=0, choose_out_of_range=1. Action mix build/upgrade/noop=130/115/10; candidate pool build/upgrade/noop=278/326/128. Phase breakdown: mid build/upgrade/noop=40/15/1; late build/upgrade/noop=90/100/9 (late upgrade lead ~11.1%, late build share ~47.4%) - **plan quality PARTIAL** (late upgrade lead below 15-25% target despite build presence). Full delta accounting (post-turn observations): non-cap pass/fail/missing=56/0/0; cap delta1/delta0/other=24/24/0. Metrics: reward/mean min ~911.65, max ~1888.35, last ~1626.30; format reward 1.0 throughout; truncation 0 throughout; completion_len/mean min ~2637.25, max ~7655.25, last ~6451.25; error/mean 0.0 throughout. Reliability notes: no sample-upload 500s, no interleaving warnings, full-turn parsing complete. **Criteria verdict:** progression PASS; plan quality PARTIAL; reliability `diagnostic`; horizon lower-bound PASS (`>=18` cap-hit lower bound, behavior lane).
- Run X168 (v0.2.22, max_rounds=56, batch_size=4, branching, run `rx2y33anr5n30b1ob2a8s88d`) completed with samples at steps 0/10/20/30/40/50 (step samples: 4/4/4/4/4/4; coverage 100% each). Pulled rollouts for every sampled step at max page coverage (`--limit 100`), parsed all rollouts and all turns: 24 samples, 584 turns, plan lengths 2-action=239, 1-action=328, 0-action=17, invalid_plan=0, choose_out_of_range=0. Action mix build/upgrade/noop=87/528/191; candidate pool build/upgrade/noop=144/562/584. Phase breakdown (late-only): build/upgrade/noop=87/528/191 (late upgrade lead ~506.9%, build share ~14.1%) - **plan quality FAIL** adaptive late target. Full delta accounting (post-turn observations): non-cap pass/fail/missing=514/2/0 with 2 non-cap `delta_round=0` failures (both terminal: step 0 round 54 lives=-10, step 50 round 50 lives=0); cap delta1/delta0/other=22/22/0. Metrics: reward/mean min ~3657.27, max ~15290.05, last ~6285.45; format reward 1.0 throughout; truncation 0 throughout; completion_len/mean min ~11881.5, max ~21432.75, last ~18996.0; error/mean 0.0 throughout. Reliability notes: no sample-upload 500s, no interleaving warnings, full-turn parsing complete. **Criteria verdict:** progression PARTIAL (strict terminal non-cap delta failures); plan quality FAIL; reliability `non_diagnostic` (delta failures violate diagnostic policy); horizon lower-bound PASS (`true horizon >= 56` on cap-hit samples).
- Decision update (2026-02-12): Canonical transfer benchmark re-run on `/Users/kbediako/Code/tower-defence` `main` remains `gate_status=pending` with reason `Baseline metrics unavailable for transfer delta thresholds`. Latest canonical metrics remain unchanged: `core_completion_rate=1.0`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1.0`.
- Direction scorecard (2026-02-12, after X167/X168): `training_quality=PARTIAL` (behavior under-target + horizon over-upgrade), `reliability=PARTIAL` (one diagnostic + one non_diagnostic), `horizon_confidence=PARTIAL` (cap-hit lower bound present but latest run non-diagnostic), `transfer_readiness=PENDING` (canonical transfer baseline thresholds still pending).
- Decision update (2026-02-12): Latest pair includes `non_diagnostic` X168, so `$collab-deliberation` was mandatory before any new launch recommendation; reliability is kept separate from policy quality and no policy-closure claim is taken from X168.
- Decision update (2026-02-12): `$collab-deliberation` consensus recommends a one-variable pivot pair (not launched yet) instead of full hold or another exact replicate cycle. Proposed behavior run `X169`: one-variable from X167 with `env.args.config.observation.candidate_balance.by_phase.late.min_build_frac` `0.3590 -> 0.3550` to recenter late upgrade lead toward 15-25%. Proposed horizon run `X170`: one-variable from X168 with `env.args.config.observation.max_towers` `3 -> 4` to test whether terminal non-cap delta failures clear at fixed cap56/payload.
- Decision update (2026-02-12): Next-pair framing (X169/X170) under guardrails. `goal_link`: improve policy quality and reliability confidence without losing horizon comparability. `hypothesis`: slight late build-floor relaxation increases behavior late upgrade lead into band, and raising horizon `max_towers` reduces terminal non-cap delta failures. `success_metric`: PASS = both runs diagnostic, behavior late 15-25% with build presence, horizon non-cap fail=0; PARTIAL = at most one run `diagnostic_with_caution` and no delta failures; FAIL = any `non_diagnostic`, any non-cap delta failure, or coverage/upload regression. `stop_condition`: if behavior remains out-of-band after this pivot, switch behavior lever family; if horizon repeats any non-cap delta failure, halt horizon launches and pivot to reliability root-cause work.
- Decision update (2026-02-12): Launched X169 behavior-lane one-variable pivot with run `fl6la5xxwrxs7s7wk365t6lm` using `configs/lab/prime-td-macro-round-60-x169.toml` (one-variable from X167: late `min_build_frac` 0.3590 -> 0.3550).
- Decision update (2026-02-12): Launched X170 horizon-lane one-variable reliability pivot with run `xd4zzdau4etvl5dht1afwk5y` using `configs/lab/prime-td-macro-round-60-x170.toml` (one-variable from X168: `observation.max_towers` 3 -> 4).
- Decision update (2026-02-12): Immediate post-launch status check: X169 and X170 are both `PENDING`; monitor with `prime rl logs fl6la5xxwrxs7s7wk365t6lm -f` and `prime rl logs xd4zzdau4etvl5dht1afwk5y -f`.
- Run X169 (v0.2.22, max_rounds=18, batch_size=4, branching, run `fl6la5xxwrxs7s7wk365t6lm`) completed with samples at steps 10/20/30/40/50 (step samples: 4/4/4/4/4; coverage 100% each sampled step). `prime rl progress` shows `steps_with_samples=[10,20,30,40,50]` and `steps_with_distributions=[0,10,20,30,40,50]`. Pulled rollouts for every sampled step at max page coverage (`--limit 100`), parsed all rollouts and all turns: 20 samples, 104 turns, plan lengths 2-action=103 and 1-action=1, invalid_plan=0, choose_out_of_range=0. Action mix build/upgrade/noop=109/93/5; candidate pool build/upgrade/noop=212/258/104. Phase breakdown: mid build/upgrade=37/7 and late build/upgrade/noop=72/86/5 (late upgrade lead ~19.4%, build share ~45.6%) - **plan quality PASS** late-band gate (mid remains build-heavy secondary signal). Full delta accounting (post-turn observations): non-cap pass/fail/missing=44/0/0; cap delta1/delta0/other=20/20/0. Metrics: reward/mean min ~766.39, max ~1878.85, last ~766.39; format reward min ~0.571 max 1.0 last ~0.571; truncation 0 throughout; completion_len/mean min ~2673.75 max ~7776.0 last ~3771.0; error/mean 0.0 throughout. Reliability notes: no sample-upload 500s, no interleaving warnings, full-turn parsing complete. **Criteria verdict:** progression PASS; plan quality PASS; reliability `diagnostic`; horizon lower-bound PASS (`>=18` cap-hit lower bound, behavior lane).
- Run X170 (v0.2.22, max_rounds=56, batch_size=4, branching, run `xd4zzdau4etvl5dht1afwk5y`) completed with samples at steps 20/30/40/50 (step samples: 4/4/4/4; coverage 100% each sampled step). `prime rl progress` shows `steps_with_samples=[20,30,40,50]` and `steps_with_distributions=[0,10,20,30,40,50]`. Pulled rollouts for every sampled step at max page coverage (`--limit 100`), parsed all rollouts and all turns: 16 samples, 369 turns, plan lengths 2-action=55 and 1-action=314, invalid_plan=0, choose_out_of_range=0. Action mix build/upgrade/noop=53/349/22; candidate pool build/upgrade/noop=84/355/369. Phase breakdown (late-only): build/upgrade/noop=53/349/22 (late upgrade lead ~558.5%, build share ~13.2%) - **plan quality FAIL** adaptive late target. Full delta accounting (post-turn observations): non-cap pass/fail/missing=322/1/0 with one non-cap `delta_round=0` failure (terminal: step 50 round 41 lives=0); cap delta1/delta0/other=15/15/0. Metrics: reward/mean min ~6587.40, max ~13941.15, last ~7308.27; format reward 1.0 throughout; truncation 0 throughout; completion_len/mean min ~16936.0 max ~22881.5 last ~21808.25; error/mean 0.0 throughout. Reliability notes: no sample-upload 500s, no interleaving warnings, full-turn parsing complete. **Criteria verdict:** progression PARTIAL (strict terminal non-cap delta failure); plan quality FAIL; reliability `non_diagnostic` (delta failure violates diagnostic policy); horizon lower-bound PASS (`true horizon >= 56` on cap-hit samples).
- Decision update (2026-02-12): Canonical transfer benchmark re-run after X169/X170 remains `gate_status=pending` with reason `Baseline metrics unavailable for transfer delta thresholds`; canonical metrics remain unchanged (`core_completion_rate=1.0`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1.0`).
- Direction scorecard (2026-02-12, after X169/X170): `training_quality=PARTIAL` (behavior lane pass, horizon lane fail), `reliability=PARTIAL` (one diagnostic + one non_diagnostic), `horizon_confidence=PARTIAL` (cap-hit lower bound present but latest horizon run non-diagnostic), `transfer_readiness=PENDING` (baseline threshold window still pending).
- Decision update (2026-02-12): Latest pair includes `non_diagnostic` X170, so `$collab-deliberation` was triggered before any new launch recommendation.
- Decision update (2026-02-12): `$collab-deliberation` consensus for this cycle is **hold launches** (do not propose/run next pair yet). Rationale: prior stop condition on X169/X170 framing required halting horizon launches if any non-cap delta failure recurred; X170 repeated a terminal non-cap delta failure, so next action is reliability root-cause analysis rather than another speculative run.
- Decision update (2026-02-12): Hold-cycle framing. `goal_link`: protect reliability confidence and avoid non-diagnostic policy drift. `hypothesis`: terminal non-cap failures at cap56 are not resolved by `max_towers` alone and need targeted root-cause before next lever test. `success_metric`: complete failure-pattern packet across X166/X168/X170 and define one explicit next horizon canary with a falsifiable expected effect. `stop_condition`: if root-cause remains unresolved, keep horizon paused and escalate instrumentation instead of launching.
- Decision update (2026-02-12): Open-question resolutions for this cycle: (Q1) terminal non-cap `delta_round=0` remains a strict progression/reliability failure after turn 1; (Q2) no policy claims from X170 because it is `non_diagnostic`; (Q3) behavior closure is not claimed from single in-band X169 (still requires reproducibility); (Q4) transfer gate remains `pending` until baseline-threshold window is established.
- Decision update (2026-02-12): Root-cause packet completed (`artifacts/root_cause_x166_x168_x170_v3.json`) across X166/X168/X170 failure and clean-cap trajectories. Terminal non-cap failures are concentrated in three sampled trajectories: X168 step0 ordinal3 (turn21 round54 lives -10), X168 step50 ordinal0 (turn17 round50 lives 0), X170 step50 ordinal2 (turn8 round41 lives 0).
- Decision update (2026-02-12): Root-cause evidence indicates late-state action-set starvation during failing windows: `pre_action_counts` repeatedly show `build=0`, `sell=0`, `upgrade=1` with `action_truncated.upgrade=true` and large omitted-upgrade counts (5-20). Failing trajectories entered these windows with low lives and then stalled (`delta_round=0`), while clean cap-hit references at the same sampled steps maintained healthy lives under the same strict progression checks.
- Decision update (2026-02-12): Proposed next horizon canary (not launched): `configs/lab/prime-td-macro-round-60-x171.toml`, one-variable from X170 with late `max_upgrade_candidates` `1 -> 2` (cap/payload unchanged). `goal_link`: reduce terminal non-cap failures by exposing a second late upgrade option when build actions are unavailable. `hypothesis`: broader late upgrade choice reduces collapse frequency under low-life pressure. `success_metric`: PASS = diagnostic reliability with non-cap fail=0 and no coverage/upload regressions; PARTIAL = diagnostic_with_caution only (single 90-95% step) and non-cap fail=0; FAIL = any non-cap failure, any sampled-step coverage <90%, or any upload 500 with incomplete coverage. `stop_condition`: if X171 still has any terminal non-cap delta failure, keep launches on hold and escalate instrumentation/root-cause depth rather than continuing lever sweeps.
- Decision update (2026-02-12): Concurrency deliberation approved to keep compute utilized without breaking guardrails: run X171 horizon canary in parallel with a behavior reproducibility replicate (X172) rather than idling the behavior lane.
- Decision update (2026-02-12): Concurrency launch framing. `goal_link`: validate horizon root-cause canary while progressing behavior closure evidence. `hypothesis`: X171 clears terminal non-cap failures via broader late upgrade choice, and X172 reproduces X169 in-band behavior for second consecutive diagnostic confirmation. `success_metric`: PASS = both runs diagnostic, X171 non-cap fail=0, X172 late 15-25% with build presence; PARTIAL = at most one diagnostic_with_caution with no non-cap failures; FAIL = any non-diagnostic run, any non-cap failure, or coverage/upload regression. `stop_condition`: if X171 has any non-cap failure, re-freeze horizon launches; if X172 is out-of-band/non-diagnostic, keep behavior closure open and re-deliberate before new behavior lever changes.
- Decision update (2026-02-12): Launched X171 horizon-lane reliability canary with run `bncl4zf0qs5www7xpvm6rqur` using `configs/lab/prime-td-macro-round-60-x171.toml` (one-variable from X170: late `max_upgrade_candidates` 1 -> 2).
- Decision update (2026-02-12): Launched X172 behavior-lane reproducibility replicate with run `jh1jqd3ruqbvxcr7s1mks3ll` using `configs/lab/prime-td-macro-round-60-x172.toml` (exact replicate of X169).
- Decision update (2026-02-12): Immediate post-launch status check: X171 and X172 are both `PENDING`; monitor with `prime rl logs bncl4zf0qs5www7xpvm6rqur -f` and `prime rl logs jh1jqd3ruqbvxcr7s1mks3ll -f`.
- Run X171 results (post-completion): `configs/lab/prime-td-macro-round-60-x171.toml` (`bncl4zf0qs5www7xpvm6rqur`), steps `0/10/20/30/40`, `4/4/4/4/4` samples each (max `--limit`, 100% coverage), all turns parsed, `action mix build/upgrade/noop=66/847/34`, `candidate pool=109/941/532`, phase breakdown late-only `66/847/34`, non-cap `delta_round` `pass=472/fail=0/missing=0`, cap `delta1=20/delta0=0/other=0`, `choose_out_of_range=0`, no 500s, one interleaving warning only, progression **PASS**, plan quality **FAIL**, reliability **diagnostic**, horizon-lower-bound **PASS** (`>=56`).
- Run X172 results (post-completion): `configs/lab/prime-td-macro-round-60-x172.toml` (`jh1jqd3ruqbvxcr7s1mks3ll`), steps `0/10/20/30/40/50`, `4/4/4/4/4/4` samples each (max `--limit`, 100% coverage), all turns parsed, `action mix build/upgrade/noop=117/120/8`, `candidate pool=248/321/124`, phase breakdown late-only `37/56/3` (~20.4% late upgrade lead), non-cap `delta_round` `pass=76/fail=0/missing=0`, cap `delta1=24/delta0=0/other=0`, `choose_out_of_range=0`, no 500s, progression **PASS**, plan quality **PASS**, reliability **diagnostic**, behavior-lower-bound **PASS** (`>=18`).
- Transfer check after both runs (canonical benchmark): command `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --out output/transfer/x171_x172.json --json` returns `gate_status=pending`, blocker `Baseline metrics unavailable for transfer delta thresholds`; latest canonical metrics unchanged (`core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`).
- Decision update (2026-02-12): Post `x171/x172` direction scorecard: `training_quality=PARTIAL` (behavior lane pass, horizon lane fail policy), `reliability=PASS` (both runs diagnostic), `horizon_confidence=PASS` (cap-hit lower-bound reached at >=56 with clean progression), `transfer_readiness=PENDING` (canonical transfer threshold baseline still missing).
- Decision update (2026-02-12): Next-pair recommendation (one-variable diffs, concurrent): `X173` exact behavior replicate of `X172` + `X174` horizon canary one-variable from `X171` (`observation.max_towers 4 -> 5`), with goal_link: stabilize behavior reproducibility while testing conservative horizon lever.
- Decision update (2026-02-13): `x173/x174` launch valid per guardrails and collab consensus. `X173` (behavior replicate) and `X174` (horizon one-variable canary) were launched concurrently.
- Decision update (2026-02-13): Launched X173 with config `configs/lab/prime-td-macro-round-60-x173.toml` using run `zf3jcdj1xg2g1rtbtfyx78or` (exact replicate of X172, one-variable diff=none).
- Decision update (2026-02-13): Launched X174 with config `configs/lab/prime-td-macro-round-60-x174.toml` using run `q096f96lnw407y58lvb4xm1z` (one-variable from X171: `observation.max_towers 4 -> 5`; same cap/payload).
- Decision update (2026-02-13): Immediate post-launch status check: both runs are `PENDING` and should be monitored with `prime rl logs zf3jcdj1xg2g1rtbtfyx78or -f` and `prime rl logs q096f96lnw407y58lvb4xm1z -f`.
- Decision update (2026-02-13): Session startup CLI checks for this maintainer handoff captured local source-of-truth surfaces first: `prime --version`=`0.5.34`, `prime rl -h`, `prime rl run -h`, and monitoring/help commands (`get/list/progress/logs/metrics/rollouts`). Drift note: no command-surface changes vs the existing `0.5.34` baseline used in recent runs.
- Run X173 results (post-completion): `configs/lab/prime-td-macro-round-60-x173.toml` (`zf3jcdj1xg2g1rtbtfyx78or`), sampled steps `0/10/20/30/40/50`, `4/4/4/4/4/4` samples each (`--limit 100`, 100% coverage), all pages fetched and all turns parsed (`24` samples, `120` turns). Action mix `build/upgrade/noop=106/120/13`; candidate pool `266/326/120`; phase breakdown `mid=29/18`, `late=77/102/13` (late upgrade lead `~32.5%`, late build share `~43.0%`). Full delta accounting: non-cap `pass/fail/missing=72/0/0`; cap `delta1/delta0/other=24/24/0`. Reliability notes: upload 500s `0`, interleaving warnings `0`, parse failures `0`, `choose_out_of_range=0`. **Criteria verdict:** progression **PASS**, plan quality **PARTIAL** (late overshoot above 15-25% band), reliability **diagnostic**, behavior lower-bound **PASS** (`>=18` cap-hit evidence).
- Run X174 results (post-completion): `configs/lab/prime-td-macro-round-60-x174.toml` (`q096f96lnw407y58lvb4xm1z`), sampled steps `0/10/20/30/40/50`, `4/4/4/4/4/4` samples each (`--limit 100`, 100% coverage), all pages fetched and all turns parsed (`24` samples, `608` turns). Action mix `build/upgrade/noop=73/1022/15`; candidate pool `122/1119/608`; phase breakdown late-only `73/1022/15` (late upgrade lead `~1300%`, late build share `~6.7%`). Full delta accounting: non-cap `pass/fail/missing=560/0/0`; cap `delta1/delta0/other=24/24/0`. Reliability notes: upload 500s `0`, interleaving warnings `0`, parse failures `0`, `choose_out_of_range=0`. **Criteria verdict:** progression **PASS**, plan quality **FAIL**, reliability **diagnostic**, horizon lower-bound **PASS** (`true horizon >=56` on cap-hit samples).
- Transfer check after both runs (canonical benchmark): command `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --out output/transfer/x173_x174.json --json` (run in `/Users/kbediako/Code/tower-defence`) returns `gate_status=pending`, blocker `Baseline metrics unavailable for transfer delta thresholds`; canonical metrics unchanged (`core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`).
- Direction scorecard (2026-02-13, after X173/X174): `training_quality=PARTIAL` (behavior lane partial + horizon lane fail policy quality), `reliability=PASS` (both runs diagnostic), `horizon_confidence=PASS` (cap-hit lower-bound `>=56` with clean non-cap progression), `transfer_readiness=PENDING` (baseline transfer threshold still unavailable).
- Decision update (2026-02-13): Next-pair recommendation (not launched; one-variable guardrails): `X175` exact behavior replicate of `X173` (no knob changes) to test variance around late-band overshoot, plus `X176` horizon one-variable from `X174` with `env.args.config.observation.candidate_balance.by_phase.late.min_build_frac` `0.60 -> 0.65` (cap/payload unchanged). `goal_link`: recover behavior reproducibility and reduce horizon late over-upgrade without relaxing reliability controls. `hypothesis`: stronger late build-floor pressure increases late build share and reduces extreme upgrade dominance while preserving clean delta progression. `success_metric`: PASS = both runs diagnostic, X175 late lead back in 15-25% with build presence, X176 non-cap fail=0 and late build share >=10% with late upgrade lead below X174; PARTIAL = both diagnostic with only trend improvement on X176; FAIL = any non-diagnostic, any non-cap delta failure, or no X176 late-mix improvement. `stop_condition`: if any non-cap terminal delta failure recurs, stop horizon expansion immediately and pivot back to reliability/root-cause workflow.
- Decision update (2026-02-13): Recommendation approved; launched X175 with config `configs/lab/prime-td-macro-round-60-x175.toml` using run `ptdi9h74qjc30d14y97uuf5r` (behavior-lane exact replicate control of X173, no policy-knob changes).
- Decision update (2026-02-13): Recommendation approved; launched X176 with config `configs/lab/prime-td-macro-round-60-x176.toml` using run `p9cb0qg7l5axso2btkxjty2c` (horizon-lane one-variable from X174: late `min_build_frac` `0.60 -> 0.65`, cap/payload unchanged).
- Decision update (2026-02-13): Immediate post-launch status check: X175 and X176 are `QUEUED`; monitor with `prime rl logs ptdi9h74qjc30d14y97uuf5r -f` and `prime rl logs p9cb0qg7l5axso2btkxjty2c -f`.
- Decision update (2026-02-13): Current status snapshot after startup logs: X175 (`ptdi9h74qjc30d14y97uuf5r`) and X176 (`p9cb0qg7l5axso2btkxjty2c`) are now both `RUNNING`; `progress` has not yet reported sampled steps.
- Decision update (2026-02-13): Session startup checks were re-run before completion analysis (`prime --version`, `prime rl -h`, `prime rl rollouts/progress/logs -h`); local CLI remained `0.5.34` with no command-surface drift.
- Run X175 results (post-completion): `configs/lab/prime-td-macro-round-60-x175.toml` (`ptdi9h74qjc30d14y97uuf5r`), sampled steps `0/10/20/30/40/50`, `4/4/4/4/4/4` samples each (max `--limit 100`, 100% coverage), all rollout pages fetched and all turns parsed (`24` samples, `132` turns). Action mix `build/upgrade/noop=140/117/7`; candidate pool `281/332/132`; phase breakdown `mid=49/11`, `late=91/106/7` (late upgrade lead `~16.5%`, late build share `~46.2%`). Full delta accounting: non-cap `pass/fail/missing=84/0/0`; cap `delta1/delta0/other=24/24/0`. Reliability notes: upload 500s `0`, interleaving warnings `0`, parse failures `0`, `choose_out_of_range=0`. **Criteria verdict:** progression **PASS**, plan quality **PASS**, reliability **diagnostic**, behavior lower-bound **PASS** (`>=18` cap-hit evidence).
- Run X176 results (post-completion): `configs/lab/prime-td-macro-round-60-x176.toml` (`p9cb0qg7l5axso2btkxjty2c`), `progress.steps_with_samples` reported `10/20/30/40/50`, but direct rollout pull at expected step `0` also returned samples (`4`), so final sampled set is `0/10/20/30/40/50` with `4/4/4/4/4/4` samples (max `--limit 100`, 100% coverage). All rollout pages fetched and all turns parsed (`24` samples, `592` turns). Action mix `build/upgrade/noop=86/939/109`; candidate pool `146/1075/592`; phase breakdown late-only `86/939/109` (late upgrade lead `~991.9%`, late build share `~8.4%`). Full delta accounting: non-cap `pass/fail/missing=544/0/0`; cap `delta1/delta0/other=24/24/0`. Reliability notes: upload 500s `0`, interleaving warnings `0`, parse failures `0`, `choose_out_of_range=0`. **Criteria verdict:** progression **PASS**, plan quality **FAIL**, reliability **diagnostic**, horizon lower-bound **PASS** (`true horizon >=56` on cap-hit samples).
- Transfer check after both runs (canonical benchmark): command `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --out output/transfer/x175_x176.json --json` (run in `/Users/kbediako/Code/tower-defence`) returns `gate_status=pending` (`pending`, not blocked), blocker `Baseline metrics unavailable for transfer delta thresholds`; canonical metrics unchanged (`core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`).
- Direction scorecard (2026-02-13, after X175/X176): `training_quality=PARTIAL` (behavior lane pass, horizon lane fail policy quality), `reliability=PASS` (both runs diagnostic), `horizon_confidence=PASS` (cap-hit lower-bound `>=56` with clean non-cap progression), `transfer_readiness=PENDING` (baseline transfer threshold still unavailable).
- Decision update (2026-02-13): Next action recommendation (not launched; one-variable diffs): `X177` behavior-lane one-variable from X175 with `env.args.config.observation.candidate_balance.by_phase.mid.min_build_frac` `0.60 -> 0.58` (goal: reduce mid build-heavy skew while preserving in-band late behavior), and `X178` horizon-lane one-variable from X176 with `env.args.config.observation.candidate_balance.by_phase.late.min_build_frac` `0.65 -> 0.70` (goal: continue reducing late over-upgrade while keeping cap/payload/reliability controls unchanged). `stop_condition`: if any non-cap terminal `delta_round` failure recurs, stop horizon expansion immediately and pivot to reliability/root-cause workflow.
- Decision update (2026-02-13): Recommendation approved; launched X177 with config `configs/lab/prime-td-macro-round-60-x177.toml` using run `x90u5gfxtfaccibv7cnbyio1` (behavior-lane one-variable from X175: `by_phase.mid.min_build_frac` `0.60 -> 0.58`).
- Decision update (2026-02-13): Recommendation approved; launched X178 with config `configs/lab/prime-td-macro-round-60-x178.toml` using run `o9x0ugl1svbhr2uz86suxyqq` (horizon-lane one-variable from X176: `by_phase.late.min_build_frac` `0.65 -> 0.70`).
- Decision update (2026-02-13): Immediate post-launch status snapshot: X177 and X178 are `RUNNING`; monitor with `prime rl logs x90u5gfxtfaccibv7cnbyio1 -f` and `prime rl logs o9x0ugl1svbhr2uz86suxyqq -f`.
- Decision update (2026-02-13): Session startup checks were re-run before `x177/x178` completion analysis (`prime --version`, `prime rl -h`, `prime rl run/get/progress/rollouts/logs -h`); local CLI remained `0.5.34` with no command-surface drift versus the active baseline.
- Decision update (2026-02-13): Monitoring observed a temporary platform-side metadata stall around steps `43-44` for both runs (progress timestamps flat while status remained `RUNNING`), then both resumed without intervention; treated as informational because final coverage, upload health, and delta checks are clean.
- Run X177 results (post-completion): `configs/lab/prime-td-macro-round-60-x177.toml` (`x90u5gfxtfaccibv7cnbyio1`), sampled steps `0/10/20/30/40/50`, `4/4/4/4/4/4` samples each (max `--limit 32`, 100% coverage), all rollout pages fetched and all turns parsed (`24` samples, `108` turns). Action mix `build/upgrade/noop=112/92/10`; candidate pool `234/279/108`; phase breakdown `mid=27/9`, `late=85/83/10` (late upgrade lead `~-2.35%`, late build share `~50.6%`). Full delta accounting: non-cap `pass/fail/missing=60/0/0`; cap `delta1/delta0/other=24/24/0`. Reliability notes: upload 500s `0`, interleaving warnings `0`, parse failures `0`, `choose_out_of_range=0`. **Criteria verdict:** progression **PASS**, plan quality **PARTIAL** (late behavior is near parity/build-leaning, below the target upgrade-leaning 15-25% band), reliability **diagnostic**, behavior lower-bound **PASS** (`>=18` cap-hit evidence).
- Run X178 results (post-completion): `configs/lab/prime-td-macro-round-60-x178.toml` (`o9x0ugl1svbhr2uz86suxyqq`), sampled steps `0/10/20/30/40/50`, `4/4/4/4/4/4` samples each (max `--limit 32`, 100% coverage), all rollout pages fetched and all turns parsed (`24` samples, `604` turns). Action mix `build/upgrade=83/1097`; candidate pool `build/noop/upgrade=83/604/1122`; phase breakdown late-only `83/1097` (late upgrade lead `~1221.7%`, late build share `~7.0%`). Full delta accounting: non-cap `pass/fail/missing=556/0/0`; cap `delta1/delta0/other=24/24/0`. Reliability notes: upload 500s `0`, interleaving warnings `0`, parse failures `0`, `choose_out_of_range=0`. **Criteria verdict:** progression **PASS**, plan quality **FAIL**, reliability **diagnostic**, horizon lower-bound **PASS** (`true horizon >=56` on cap-hit samples).
- Transfer check after both runs (canonical benchmark): command `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --out output/transfer/x177_x178.json --json` (run in `/Users/kbediako/Code/tower-defence`) returns `gate_status=pending`, `gate_reason=Baseline metrics unavailable for transfer delta thresholds`; canonical metrics remain `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`.
- Direction scorecard (2026-02-13, after X177/X178): `training_quality=PARTIAL` (behavior lane partial + horizon lane fail policy quality), `reliability=PASS` (both runs diagnostic), `horizon_confidence=PASS` (cap-hit lower-bound `>=56` with clean non-cap progression), `transfer_readiness=PENDING` (baseline transfer threshold still unavailable).
- Decision update (2026-02-13): `$collab-deliberation` consensus validated next-pair launch as **valid** under active guardrails (both latest runs diagnostic, no non-cap delta failures, no upload 500s).
- Decision update (2026-02-13): Next action recommendation (not launched; one-variable diffs): `X179` behavior-lane one-variable from X177 with `env.args.config.observation.candidate_balance.by_phase.mid.min_build_frac` `0.58 -> 0.60` (re-anchor to the last in-band behavior profile), and `X180` horizon-lane one-variable from X178 with `env.args.config.observation.max_build_slots` `2 -> 3` (increase build-option availability while keeping cap and other reliability controls fixed). `goal_link`: recover late upgrade-leaning behavior in the behavior lane and reduce extreme horizon over-upgrade without conflating with reliability regressions. `hypothesis`: restoring mid build-floor to `0.60` pulls behavior lane back toward the 15-25% late upgrade lead band, and expanding build slots raises late build share above X178's floor while keeping non-cap delta clean. `success_metric`: PASS = both runs `diagnostic`, behavior late upgrade lead in `15-25%` with build presence, horizon late build share `>7.03%` and late upgrade lead `<1221.7%` with non-cap fail `0`; PARTIAL = both runs diagnostic but only one lane shows directional improvement; FAIL = any non-diagnostic run, any non-cap delta failure, or coverage/upload regression. `stop_condition`: if any non-cap terminal delta failure recurs, stop horizon expansion immediately and pivot to reliability/root-cause workflow.
- Decision update (2026-02-13): Session startup CLI checks were rerun before launching X179/X180 (`prime --version`, `prime rl -h`, `prime rl run/get/progress/rollouts/logs -h`); local source-of-truth remained `prime` `0.5.34` with no command-surface drift versus current baseline.
- Decision update (2026-02-13): Recommendation approved; launched X179 with config `configs/lab/prime-td-macro-round-60-x179.toml` using run `fh7w7inugol08g69k52k62j5` (behavior-lane one-variable from X177: `by_phase.mid.min_build_frac` `0.58 -> 0.60`).
- Decision update (2026-02-13): Recommendation approved; launched X180 with config `configs/lab/prime-td-macro-round-60-x180.toml` using run `tjzrje4qz6j038ffsvkz0qor` (horizon-lane one-variable from X178: `observation.max_build_slots` `2 -> 3`).
- Decision update (2026-02-13): Immediate post-launch status snapshot: X179 and X180 transitioned from `PENDING` to `RUNNING`; `progress` currently shows no sampled steps yet (expected pre-sample state).
- Decision update (2026-02-13): Session startup checks were rerun before `x179/x180` completion analysis (`prime --version`, `prime rl -h`, `prime rl get/progress/rollouts/logs -h`); local CLI remained `0.5.34` with no command-surface drift versus baseline.
- Run X179 results (post-completion): `configs/lab/prime-td-macro-round-60-x179.toml` (`fh7w7inugol08g69k52k62j5`), sampled steps `0/10/20/30/40/50`, `4/4/4/4/4/4` samples each (max `--limit 100`, 100% coverage), all rollout pages fetched and all turns parsed (`24` samples, `112` turns). Action mix `build/upgrade/noop=123/98/2`; candidate pool `224/297/112`; phase breakdown `mid=27/12`, `late=96/86/2` (late upgrade lead `~-10.42%`, late build share `~52.75%`). Full delta accounting: non-cap `pass/fail/missing=64/0/0`; cap `delta1/delta0/other=24/24/0`. Reliability notes: upload 500s `0`, interleaving warnings `0`, parse failures `0`, `choose_out_of_range=0`. **Criteria verdict:** progression **PASS**, plan quality **FAIL** (late behavior is build-leading, outside target upgrade-lean band), reliability **diagnostic**, behavior lower-bound **PASS** (`>=18` cap-hit evidence).
- Run X180 results (post-completion): `configs/lab/prime-td-macro-round-60-x180.toml` (`tjzrje4qz6j038ffsvkz0qor`), sampled steps `0/10/20/30/40/50`, `4/4/4/4/4/4` samples each (max `--limit 100`, 100% coverage), all rollout pages fetched and all turns parsed (`24` samples, `600` turns). Action mix `build/upgrade=122/987`; candidate pool `build/noop/upgrade=167/600/1110`; phase breakdown late-only `122/987` (late upgrade lead `~709.0%`, late build share `~11.0%`). Full delta accounting: non-cap `pass/fail/missing=552/0/0`; cap `delta1/delta0/other=24/24/0`. Reliability notes: upload 500s `0`, interleaving warnings `0`, parse failures `0`, `choose_out_of_range=0`. **Criteria verdict:** progression **PASS**, plan quality **FAIL** (late over-upgrade persists), reliability **diagnostic**, horizon lower-bound **PASS** (`>=56` cap-hit evidence).
- Transfer check after both runs (canonical benchmark): command `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --out output/transfer/x179_x180.json --json` (run in `/Users/kbediako/Code/tower-defence`) returns `gate_status=pending`, `gate_reason=Baseline metrics unavailable for transfer delta thresholds`; canonical metrics remain `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`.
- Direction scorecard (2026-02-13, after X179/X180): `training_quality=PARTIAL` (both lanes fail policy-quality targets), `reliability=PASS` (both runs diagnostic), `horizon_confidence=PASS` (cap-hit lower-bound `>=56` with clean non-cap progression), `transfer_readiness=PENDING` (baseline transfer threshold still unavailable).
- Decision update (2026-02-13): `$collab-deliberation` consensus validated the next pair as **valid** under guardrails (one-variable diffs, both latest runs diagnostic, no non-cap delta failures); reliability-first expansion gate satisfied by consecutive diagnostic horizon-lane runs (`X178`, `X180`).
- Decision update (2026-02-13): Next action recommendation (not launched; one-variable diffs): `X181` behavior-lane one-variable from X179 with `env.args.config.observation.candidate_balance.by_phase.late.min_build_frac` `0.3550 -> 0.3500`, and `X182` horizon-lane one-variable from X180 with `env.args.config.observation.max_build_slots` `3 -> 4` (keep cap/payload controls fixed). `goal_link`: recover behavior lane from build-leading drift while reducing horizon late upgrade dominance without conflating reliability. `hypothesis`: lowering late build floor slightly in behavior lane restores late upgrade-leaning direction, and adding one build slot in horizon lane raises build-share while preserving progression cleanliness. `success_metric`: PASS = both runs diagnostic with non-cap fail `0`, X181 improves late upgrade lead above `-10.42%` with lower late build share than `52.75%`, and X182 lowers late upgrade lead below `709.0%` with late build share above `11.0%`; PARTIAL = both runs diagnostic but only one lane improves directionally; FAIL = any non-diagnostic run, any non-cap delta failure, or any coverage/upload regression. `stop_condition`: if any non-cap terminal delta failure recurs, stop horizon expansion immediately and pivot to reliability/root-cause workflow.
- Decision update (2026-02-13): AGENTS-required targeted test ran clean for this session: `PYTHONPATH=src python3 -m unittest tests/test_reward_shaping_choose.py` -> `Ran 11 tests ... OK`.
- Decision update (2026-02-13): Session startup checks were rerun before launching `x181/x182` (`prime --version`, `prime rl -h`, `prime rl run/get/progress/rollouts/logs -h`); local CLI remained `0.5.34` with no command-surface drift versus baseline.
- Decision update (2026-02-13): Recommendation approved; launched X181 with config `configs/lab/prime-td-macro-round-60-x181.toml` using run `qe9hdo1nkw8lbbi6hqg1tn93` (behavior-lane one-variable from X179: `by_phase.late.min_build_frac` `0.3550 -> 0.3500`).
- Decision update (2026-02-13): Recommendation approved; launched X182 with config `configs/lab/prime-td-macro-round-60-x182.toml` using run `w19w8vl7wbc37sn93e9s3gql` (horizon-lane one-variable from X180: `observation.max_build_slots` `3 -> 4`).
- Decision update (2026-02-13): One-variable diff check passed for both child configs (name + exactly one policy knob per lane).
- Decision update (2026-02-13): Immediate post-launch status snapshot: X181 is `RUNNING`, X182 is `PENDING`; `progress` for both currently shows no sampled steps yet (expected pre-sample state).
- Decision update (2026-02-13): Follow-up status snapshot: X182 transitioned to `RUNNING`; both runs are now active with `progress.steps_with_samples=[]` (still pre-sample).
- Decision update (2026-02-13): Early monitoring snapshot: both runs remain `RUNNING`; sampled-step coverage has started (`X181 latest_step=1, steps_with_samples=[0]`; `X182 latest_step=0, steps_with_samples=[0]`).
- Decision update (2026-02-13): Session startup checks were rerun before `x181/x182` completion analysis (`prime --version`, `prime rl -h`, `prime rl get/progress/rollouts/logs -h`); local CLI remained `0.5.34` with no command-surface drift versus baseline.
- Run X181 results (post-completion): `configs/lab/prime-td-macro-round-60-x181.toml` (`qe9hdo1nkw8lbbi6hqg1tn93`), sampled steps `0/10/20/30/40`, `4/4/4/4/4` samples each (max `--limit 100`, 100% coverage at sampled steps), all rollout pages fetched and all turns parsed (`20` samples, `108` turns). Action mix `build/upgrade/noop=105/106/4`; candidate pool `build/upgrade/noop=192/275/108`; phase breakdown `mid=38/9`, `late=67/97/4` (late upgrade lead `~44.8%`, late build share `~40.9%`). Full delta accounting: non-cap `pass/fail/missing=68/0/0`; cap `delta1/delta0/other=20/20/0`. Reliability notes: upload 500s `0`, interleaving warnings `0`, parse failures `0`, `choose_out_of_range=0`. **Criteria verdict:** progression **PASS**, plan quality **PARTIAL** (upgrade-leaning with build presence but above 15-25% late lead band), reliability **diagnostic**, behavior lower-bound **PASS** (`>=18` cap-hit evidence).
- Run X182 results (post-completion): `configs/lab/prime-td-macro-round-60-x182.toml` (`w19w8vl7wbc37sn93e9s3gql`), sampled steps `0/10/20/30/40/50`, `4/4/4/4/4/4` samples each (max `--limit 100`, 100% coverage at sampled steps), all rollout pages fetched and all turns parsed (`24` samples, `604` turns). Action mix `build/upgrade/noop=141/891/9`; candidate pool `build/upgrade/noop=229/1096/604`; phase breakdown late-only `141/891/9` (late upgrade lead `~531.9%`, late build share `~13.7%`). Full delta accounting: non-cap `pass/fail/missing=556/0/0`; cap `delta1/delta0/other=24/24/0`. Reliability notes: upload 500s `0`, interleaving warnings `0`, parse failures `0`, `choose_out_of_range=0`. **Criteria verdict:** progression **PASS**, plan quality **FAIL** (extreme late over-upgrade persists), reliability **diagnostic**, horizon lower-bound **PASS** (`>=56` cap-hit evidence).
- Transfer check after both runs (canonical benchmark): command `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --out output/transfer/x181_x182.json --json` (run in `/Users/kbediako/Code/tower-defence`) returns `gate_status=pending`, `gate_reason=Baseline metrics unavailable for transfer delta thresholds`; canonical metrics remain `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`.
- Direction scorecard (2026-02-13, after X181/X182): `training_quality=PARTIAL` (behavior lane partial + horizon lane fail policy quality), `reliability=PASS` (both runs diagnostic), `horizon_confidence=PASS` (cap-hit lower-bound `>=56` with clean non-cap progression), `transfer_readiness=PENDING` (baseline transfer threshold still unavailable).
- Decision update (2026-02-13): `$collab-deliberation` consensus validated next-pair launch as **VALID (with caution)** under guardrails (one-variable diffs, both latest runs diagnostic, no non-cap delta failures, no upload 500s).
- Decision update (2026-02-13): Next action recommendation (not launched; one-variable diffs): `X183` behavior-lane one-variable from X181 with `env.args.config.observation.candidate_balance.by_phase.late.min_build_frac` `0.3500 -> 0.3520`, and `X184` horizon-lane one-variable from X182 with `env.args.config.observation.max_build_slots` `4 -> 5` (explicit canary; cap/payload controls otherwise fixed). `goal_link`: damp behavior-lane late overshoot toward the 15-25% band while continuing horizon de-overupgrade trend without conflating reliability. `hypothesis`: a small late floor increase (`+0.002`) moves behavior lead down from `44.8%` toward target, and one additional build slot reduces horizon lead below `531.9%` while increasing late build share above `13.7%` with non-cap delta clean. `success_metric`: PASS = both runs diagnostic with non-cap fail `0`, X183 late upgrade lead in `15-25%` with build presence, and X184 lead `<531.9%` with build share `>13.7%`; PARTIAL = both runs diagnostic but only one lane improves directionally; FAIL = any non-diagnostic run, any non-cap delta failure, or any coverage/upload regression. `stop_condition`: if any non-cap terminal delta failure recurs, stop horizon expansion immediately and pivot to reliability/root-cause workflow.
- Decision update (2026-02-13): Session startup checks were rerun before launching `x183/x184` (`prime --version`, `prime rl -h`, `prime rl run/get/progress/rollouts/logs -h`); local CLI remained `0.5.34` with no command-surface drift versus baseline.
- Decision update (2026-02-13): Recommendation approved; launched X183 with config `configs/lab/prime-td-macro-round-60-x183.toml` using run `pfpkrcyivmkcrc04ayr0x82z` (behavior-lane one-variable from X181: `by_phase.late.min_build_frac` `0.3500 -> 0.3520`).
- Decision update (2026-02-13): Recommendation approved; launched X184 with config `configs/lab/prime-td-macro-round-60-x184.toml` using run `hy4aa5o9fqgetw5j19qxv9h3` (horizon-lane one-variable from X182: `observation.max_build_slots` `4 -> 5`).
- Decision update (2026-02-13): One-variable diff check passed for both child configs (name + exactly one policy knob per lane).
- Decision update (2026-02-13): Immediate post-launch status snapshot: both runs are `RUNNING`; `progress` currently shows no sampled steps yet (expected pre-sample state).
- Decision update (2026-02-13): Session startup checks were rerun before `x183/x184` completion analysis (`prime --version`, `prime rl -h`, `prime rl get/progress/rollouts/logs -h`); local CLI remained `0.5.34` with no command-surface drift versus baseline.
- Decision update (2026-02-13): Initial completion-check snapshot showed `X183=COMPLETED` while `X184` was still `RUNNING`; monitoring continued until `X184` reached `COMPLETED` at recorded `completed_at=2026-02-13 10:50:11.137000` (from `prime rl get` run metadata).
- Run X183 results (post-completion): `configs/lab/prime-td-macro-round-60-x183.toml` (`pfpkrcyivmkcrc04ayr0x82z`), sampled steps `0/10/20/30/40/50`, `4/4/4/4/4/4` samples each (max `--limit 100`, 100% coverage at sampled steps), all rollout pages fetched and all turns parsed (`24` samples, `112` turns). Action mix `build/upgrade/noop=129/93/1`; candidate pool `build/upgrade/noop=240/298/112`; phase breakdown `mid=32/8`, `late=97/85/1` (late upgrade lead `~-12.4%`, late build share `~53.3%`). Full delta accounting: non-cap `pass/fail/missing=64/0/0`; cap `delta1/delta0/other=24/24/0`. Reliability notes: upload 500s `0`, interleaving warnings `0`, parse failures `0`, `choose_out_of_range=0`. **Criteria verdict:** progression **PASS**, plan quality **FAIL** (late behavior is build-leading, outside target upgrade-lean band), reliability **diagnostic**, behavior lower-bound **PASS** (`>=18` cap-hit evidence).
- Run X184 results (post-completion): `configs/lab/prime-td-macro-round-60-x184.toml` (`hy4aa5o9fqgetw5j19qxv9h3`), sampled steps `0/10/20/30/40`, `4/4/4/4/4` samples each (max `--limit 100`, 100% coverage at sampled steps; no step-50 samples in `progress.steps_with_samples`), all rollout pages fetched and all turns parsed (`20` samples, `516` turns). Action mix `build/upgrade/noop=131/820/8`; candidate pool `build/upgrade/noop=201/936/516`; phase breakdown late-only `131/820/8` (late upgrade lead `~526.0%`, late build share `~13.8%`). Full delta accounting: non-cap `pass/fail/missing=476/0/0`; cap `delta1/delta0/other=20/20/0`. Reliability notes: upload 500s `0`, interleaving warnings `0`, parse failures `0`, `choose_out_of_range=0`. **Criteria verdict:** progression **PASS**, plan quality **FAIL** (extreme late over-upgrade persists), reliability **diagnostic**, horizon lower-bound **PASS** (`>=56` cap-hit evidence).
- Transfer check after both runs (canonical benchmark): command `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --out output/transfer/x183_x184.json --json` (run in `/Users/kbediako/Code/tower-defence`) returns `gate_status=pending`, `gate_reason=Baseline metrics unavailable for transfer delta thresholds`; canonical metrics remain `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`.
- Direction scorecard (2026-02-13, after X183/X184): `training_quality=FAIL` (both lanes fail policy-quality targets), `reliability=PASS` (both runs diagnostic), `horizon_confidence=PASS` (cap-hit lower-bound `>=56` with clean non-cap progression), `transfer_readiness=PENDING` (baseline transfer threshold still unavailable).
- Decision update (2026-02-13): `$collab-deliberation` consensus validated next-pair launch as **VALID** under guardrails (one-variable diffs, both latest runs diagnostic, no non-cap delta failures, no upload 500s).
- Decision update (2026-02-13): Next action recommendation (not launched; one-variable diffs): `X185` behavior-lane one-variable from X183 with `env.args.config.observation.candidate_balance.by_phase.late.min_build_frac` `0.3520 -> 0.3510`, and `X186` horizon-lane one-variable from X184 with `env.args.config.observation.max_towers` `5 -> 6` (keep cap/payload controls otherwise fixed). `goal_link`: recover behavior lane from build-leading regression while testing a stronger horizon context lever after low-signal `max_build_slots` expansion. `hypothesis`: behavior midpoint correction (`0.3510`) restores upgrade-leaning late direction, and increasing observed tower context (`max_towers=6`) reduces horizon upgrade dominance vs X184 without delta regressions. `success_metric`: PASS = both runs diagnostic with non-cap fail `0`, X185 late upgrade lead in `15-25%` with build presence, and X186 lead `<525.95%` with build share `>13.77%`; PARTIAL = both runs diagnostic but only one lane improves directionally; FAIL = any non-diagnostic run, any non-cap delta failure, or any coverage/upload regression. `stop_condition`: if any non-cap terminal delta failure recurs, stop horizon expansion immediately and pivot to reliability/root-cause workflow.
- Decision update (2026-02-08): X92 shows the X90->X92 one-variable `late min_build_frac` nudge did not land in-band; late behavior remains upgrade-leaning with build presence but overshoots the preferred 15-25% upgrade lead, so the next behavior probe should be another small one-variable correction in the opposite direction.
- Decision update (2026-02-08): X93 restart (`zw58rlkeo94buj1viwrp9w6z`) completed with full sample-step coverage and no upload 500s, so prior infra-blocked status is now resolved as transient capacity delay rather than persistent upload instability.
- Decision update (2026-02-08): X94 opposite correction from X92 did not reduce late overshoot; late upgrade lead increased to ~89.6%, so next behavior-lane change should re-anchor with stronger late build pressure and/or tighter late upgrade-candidate caps.
- Decision update (2026-02-08): X95 confirms lowering late `max_upgrade_candidates` from 4 to 3 over-corrected into late build-leaning behavior; keep this setting as an upper bound on build pressure rather than the new behavior baseline.
- Decision update (2026-02-08): X96 extends the reliability-first horizon lower bound to `>=52` with full sample-step coverage and no upload 500s, but progression remains partial due one terminal non-cap `delta_round=0` event and policy quality remains late over-upgrade.
- Decision update (2026-02-08): X97 re-confirms that the `late max_upgrade_candidates=3` regime is still over-corrected toward late build-leaning behavior even after lowering late `min_build_frac` to 0.338, so behavior-lane tuning should return to a `late max_upgrade_candidates=4` base with tighter late build-floor control to avoid oscillation.
- Decision update (2026-02-08): X98 extends the reliability-first horizon lower bound to `>=53` with full sample-step coverage and no upload 500s; progression remains partial due two terminal-only non-cap `delta_round=0` events, so horizon tuning should treat this as non-actionable terminal noise unless non-terminal delta failures appear.
- Decision update (2026-02-08): X99 keeps the behavior lane in the correct late-direction regime (upgrade-leaning with build presence) but still overshoots the preferred late lead band (~39.7%) and remains mid build-heavy; next behavior-lane change should stay on the `late max_upgrade_candidates=4` base and apply only a tiny opposite late-floor nudge with replicate confirmation to avoid oscillation.
- Decision update (2026-02-08): X100 (`max_rounds=54`) regressed reliability with sample-upload 500s at every sample checkpoint and zero retrievable rollouts; treat horizon and policy signals as inconclusive for this run, and recover by restoring the last reliable horizon settings (X98 at `max_rounds=53`) or reducing payload before retrying 54.
- Decision update (2026-02-08): X101 confirms the damped opposite nudge from X99 removed late overshoot but under-shot the preferred 15-25% late lead band (~13.3%), with mid still build-heavy; next behavior-lane tweak should be a tiny upgrade-pressure increase on the same cap-4 base and validated with replicate consistency checks.
- Decision update (2026-02-08): X102 (`max_rounds=54`, `max_tokens=36`) partially recovered horizon signal versus X100 (samples restored at 0/10/30/40 and cap-hit evidence `>=54`), but upload 500s still removed steps 20/50; keep cap at 54 and prioritize one more payload-reliability reduction before considering any further horizon raise.
- Decision update (2026-02-08): X103 confirms the one-variable behavior nudge from X101 (`late min_build_frac=0.3495`) moved late policy back above-band (~62% upgrade lead) while preserving build floor and clean reliability; keep the cap-4 behavior base, but tighten with smaller corrective steps and require 2-run reproducibility before declaring convergence.
- Decision update (2026-02-08): X104 (`max_rounds=54`, `max_tokens=34`) regressed reliability versus X102 (only step-40 sample, upload 500s at 0/10/20/30/50); do not lower token budget further at cap 54, and re-run horizon reliability at `max_tokens=36` with unchanged controls to satisfy the two-consecutive reliable-run guardrail.
- Decision update (2026-02-08): X105 midpoint correction (`late min_build_frac=0.3496`) moved late behavior from overshoot to near the preferred upper edge (~25.3% upgrade lead) with full reliability and clean progression, but mid-phase remains build-heavy; treat behavior lane as PARTIAL and require replicate confirmation before claiming closure.
- Decision update (2026-02-08): X106 boundary rollback (`max_rounds=53`, `max_tokens=36`) restored full horizon reliability (all sample steps present, no upload 500s) with clean non-cap progression and cap-hit evidence (`>=53`), supporting 53 as the current reliable lower-bound operating point while 54 remains unresolved.
- Decision update (2026-02-08): X107 did not reproduce X105’s near-band late mix; behavior remained upgrade-leaning but overshot to ~75.7% late upgrade lead with mid still build-heavy, so behavior closure guardrail is not met and further behavior nudge should remain minimal/one-variable.
- Decision update (2026-02-08): X108 re-opened the 54-cap reliability issue (upload 500s with missing sample steps 0/30/40) and provided no available cap-hit at round 54; keep X106 (`max_rounds=53`, `max_tokens=36`) as the reliable horizon baseline and treat 54 as unresolved.
- Decision update (2026-02-09): X109 (exact X105 replicate) failed behavior-lane reproducibility by flipping into late build-leading policy; keep behavior lane open and avoid declaring convergence from single-run in-band hits.
- Decision update (2026-02-09): X110 reached cap 54 again (horizon lower bound `>=54` on available cap-hit rollouts) but still showed sample-upload 500 at step 30 and terminal non-cap delta exceptions; treat 54 as still unresolved for reliability closure, and prioritize payload control before another 54 confirmation attempt.
- Decision update (2026-02-09): X111 corrected X109’s direction back to late upgrade-leaning while preserving full reliability and clean progression, but the late lead (~6.2%) remains below the preferred 15-25% band and mid is still build-heavy; behavior lane remains PARTIAL and requires another small one-variable push.
- Decision update (2026-02-09): X112 (exact X110 replicate) did not confirm transient reliability recovery at cap 54; upload 500s reappeared (missing steps 10/40/50) and progression stayed PARTIAL on available rollouts, so keep X106 (`max_rounds=53`, `max_tokens=36`) as the reliability baseline and treat 54 as unresolved pending a stronger payload-control change.
- Decision update (2026-02-09): X113 moved the behavior lane in the intended direction (late upgrade lead increased from ~6.2% in X111 to ~9.5%) while preserving full reliability and clean progression, but the run remains below the preferred 15-25% late lead band and mid is still build-heavy; behavior lane stays PARTIAL and should keep one-variable, low-amplitude tuning.
- Decision update (2026-02-09): X114 re-established the horizon reliability baseline at `max_rounds=53` with full sample-step coverage and no upload 500s under the payload-safe controls (`sampling.max_tokens=36`), but policy quality remains late over-upgrade and progression is still PARTIAL due one terminal non-cap delta event; keep 53 as the reliable lower-bound anchor and do not advance cap until 54 is reproduced reliably.
- Decision update (2026-02-09): X115 maintained full reliability/progression cleanliness and moved late behavior closer to target (upgrade lead ~27.4%), but remains slightly above the preferred 15-25% band with mid still build-heavy; keep behavior lane PARTIAL and use tiny opposite-direction one-variable corrections to avoid oscillation.
- Decision update (2026-02-09): X116 achieved full sample-step coverage and no upload 500s at cap 54 under the snapshot-shift payload control, providing a clean reliability signal at 54, but progression remains PARTIAL due terminal non-cap delta events and policy quality remains late over-upgrade; treat this as first reliable 54 evidence and require one more consecutive reliable 54 run before claiming horizon closure.
- Decision update (2026-02-09): X117’s opposite nudge corrected X115 overshoot and landed near the lower edge of the target late band (~14.8% upgrade lead), but still slightly under the preferred 15-25% range with mid remaining build-heavy; keep behavior lane PARTIAL and continue micro-step one-variable tuning.
- Decision update (2026-02-09): X118 reproduced X116 reliability at cap 54 (full sample-step coverage, no upload 500s, full-turn parsing), satisfying the two-consecutive reliability guardrail for horizon closure at 54; maintain 54 as the confirmed reliable lower-bound operating point and avoid cap increases until policy/progression objectives are intentionally separated from horizon confirmation.
- Decision update (2026-02-09): X119’s one-variable micro-nudge (`late min_build_frac=0.3479`) did not improve late-band alignment; late lead dropped to ~4.7% with mid still build-heavy, so behavior remains PARTIAL and this probe should be treated as low-signal/noise-prone rather than convergence evidence.
- Decision update (2026-02-09): X120 preserved full reliability at cap 54 (full sample-step coverage, no upload 500s) and improved non-cap progression errors versus X118 (1 terminal non-cap `delta_round=0` vs 3), but strict progression is still not fully clean; hold cap advancement until a clean non-cap `delta_round==1` pass is observed under the same controls.
- Decision update (2026-02-09): X121 (exact X117 replicate) did not reproduce near-band late behavior; late lead narrowed further to ~2.3% with mid still build-heavy, reinforcing that the current 0.3480 behavior setting is under-target and high-variance for the 15-25% objective.
- Decision update (2026-02-09): X122 (exact X120 replicate) maintained full reliability at cap 54 (full sample-step coverage, no upload 500s) but did not clear strict progression (2 terminal non-cap `delta_round=0` events), so keep cap advancement blocked until a clean non-cap pass is observed on the same controls.
- Decision update (2026-02-09): X123 (one-variable 0.3478 correction from X121) moved behavior back to the intended late direction with full reliability/progression cleanliness, but overshot the preferred late lead band (~54.7%) and kept mid build-heavy; treat as PARTIAL and prioritize reproducibility checks over additional large knob movement.
- Decision update (2026-02-09): X124 (`max_rounds=54`, `late min_build_frac=0.50`) retained full reliability and cap-hit horizon lower bound (`>=54`) but did not improve strict progression (3 terminal non-cap `delta_round=0` events) and remained strongly over-upgrade; treat as PARTIAL/FAIL for controllable quality criteria and keep horizon lane on payload-safe controls without cap increase.
- Guardrail (2026-02-08): to avoid circling, count a lane change as real progress only if it reproduces in **2 consecutive runs** with (a) full sample-step coverage at configured checkpoints, (b) no sample-upload 500s, (c) all retrieved rollouts parsed across all turns, and (d) non-cap post-turn observations satisfying `macro_round_meta.delta_round == 1` except terminal-only events. If any condition fails, mark exploratory/inconclusive and do not advance horizon cap or claim behavior closure.
- Guardrail (2026-02-08): behavior closure requires two consecutive runs in-band for late mix (upgrade lead ~15-25% with build presence) before switching focus to mid-phase tuning; horizon closure at `max_rounds=54` requires two consecutive reliable runs before any cap increase.
- Decision update (2026-02-08): X90 confirms the one-variable correction from X88 pulled late behavior back from over-upgrade but overshot toward near-parity/under-target late lead (~12%); the next behavior probe should apply a small late-pressure increase from X90 (not another large shift).
- Decision update (2026-02-08): X91 restored full reliability at `max_rounds=50` (all sample steps present, no upload 500s), but policy quality remains late upgrade-dominant and round-progression is only partial due two terminal non-cap `delta_round=0` events; keep horizon cap fixed at 50 until progression reliability is fully clean again.
- Decision update (2026-02-07): X86 confirms the behavior lane can keep clean progression/reliability while moving from late parity to late upgrade-leaning; next behavior probe should reduce late build share without collapsing into upgrade-only behavior.
- Decision update (2026-02-07): X87 extends the reliability-first horizon lower bound to `>=48` with full sample checkpoints and no upload 500s; continue horizon probing with incremental cap increases while keeping payload controls fixed.
- Decision update (2026-02-07): X88 confirms the behavior lane is sensitive to small late-floor changes; dropping late `min_build_frac` from 0.36 to 0.34 overshot the late upgrade lead, so the next behavior probe should move by smaller increments and/or re-balance with upgrade-candidate cap control.
- Decision update (2026-02-07): X89 extends the reliability-first horizon lower bound to `>=50` on available rollouts, but intermittent sample-upload 500s reappeared (missing steps 20/30/40); keep payload controls and raise cap incrementally only after reliability recovers.
- Decision update (2026-02-03): SingleTurn diagnostics concluded after W; macro-round multi-turn is now the primary training path.
- Decision update (2026-02-04): all future Prime TD runs should use `trajectory_strategy="branching"` unless explicitly overridden for experiments.
- Decision update (2026-02-05): X28/X29 will run in parallel to probe **episode length** with minimal payload risk. X28 raises `max_rounds=18` while keeping X26d payload controls; X29 keeps the same caps but nudges late-phase candidate balance (late `min_build_frac=0.45`, late `max_upgrade_candidates=7`) to improve late mix without increasing payload size.
- Decision update (2026-02-05): proceed to the **next stage** despite episode-length remaining **inconclusive** due to intermittent 500s at higher payloads; defer length testing until PI fixes the upload issue.
- Decision update (2026-02-05): next-stage runs will use **X26d behavioral baseline** (best plan quality so far) under **X29b payload controls** to keep uploads stable; run X30/X31 in parallel with a minimal late-phase mix nudge in X31.
- Decision update (2026-02-05): late-game upgrades are **expected** as rounds harden; refine plan-quality target to **early build-heavy**, **mid mixed**, **late upgrade-leaning but with some build actions** (to allow specialized towers).
- Decision update (2026-02-05): `batch_size=2` mitigated upload 500s for max_round probes (X46b/X47b), but both runs saturated at cap (24/26), so episode-length improvement beyond cap remains **inconclusive**.
- Decision update (2026-02-06): X49 extended the stable horizon to round-cap 28 (all parsed rollouts ended at 28), but the step-40 sample-upload 500 and cap saturation still leave true episode-length gains beyond cap **unresolved**.
- Decision update (2026-02-06): for next configs, treat late `10-15%` upgrade lead as a **minimum** signal rather than a fixed optimum; prefer an adaptive late target around **15-25%** upgrade lead with enforced build presence (late build share roughly **25-35%**) to balance survivability and avoid upgrade-only policy collapse.
- Decision update (2026-02-06): X51 (`max_rounds=30`) confirms that horizon extension can re-trigger sample-upload 500 failures even at `batch_size=2`; keep two-track evaluation (behavior at stable horizon + separate horizon probe) and treat missing-rollout runs as infra-limited/non-diagnostic for policy quality.
- Decision update (2026-02-06): X52 is the new behavior-lane reference for adaptive late mix (~15% late upgrade lead with build present), while X53 shows that stricter payload caps can recover some horizon samples but may over-constrain late build opportunities and still intermittently 500 at sample upload.
- Decision update (2026-02-06): X54 confirms the current center-point calibration can over-correct into late build-leaning behavior; retain X52 as behavior-lane reference for now.
- Decision update (2026-02-06): X55 reaches round-cap 30 on all parsed rollouts, but intermittent sample-upload 500s (missing steps 0/30/50) and cap saturation keep episode-length gains beyond cap **inconclusive**.
- Decision update (2026-02-06): for episode-length testing, use a reliability-first horizon lane (smaller upload payload per sample, e.g., `batch_size=1` and later snapshots) in parallel with behavior-lane calibration anchored on X52; avoid large YOLO runs until sample-upload stability improves.
- Decision update (2026-02-06): X56 re-confirmed that naive re-anchoring can drift into late build-leaning behavior; keep X52 as behavior-lane baseline for late-phase targeting.
- Decision update (2026-02-06): X57 validated the reliability-first horizon approach (`batch_size=1`, later snapshots) with full sample-step coverage and no upload 500s at `max_rounds=30`, but policy quality remained late over-upgrade, so horizon and behavior lanes should stay decoupled.
- Decision update (2026-02-06): X58 shows that increasing late `max_upgrade_candidates` can correct build-lean drift (late direction fixed) but may overshoot into too-strong upgrade lead; next behavior-lane tweak should tighten toward the 15-25% lead band.
- Decision update (2026-02-06): X59 extends reliability-first horizon execution to `max_rounds=32` with full sample-step coverage and no upload 500s; true episode-length gain beyond cap is still unobservable, so future horizon claims should require raising cap again under the same reliability controls.
- Decision update (2026-02-06): X60 kept late-phase direction upgrade-leaning with build presence but did not tighten the lead band enough; keep behavior lane anchored around X52 and continue small late-floor/candidate adjustments.
- Decision update (2026-02-06): X61 extends reliability-first horizon execution to `max_rounds=34` with full sample-step coverage and no upload 500s; horizon infra is stable, but true beyond-cap episode-length gains remain unobserved until a higher cap run stops saturating.
- Decision update (2026-02-06): X62 improved late-phase balance toward parity and preserved build presence with zero 500s, but the late upgrade lead (~7%) is below the preferred 15-25% band; next behavior-lane tweak should slightly reduce late build floor or modestly increase late upgrade candidate pressure.
- Decision update (2026-02-06): X63 extends horizon-lane cap saturation to `max_rounds=36` on all parsed samples, but one step-20 sample-upload 500 confirms horizon runs remain infra-sensitive at high completion payloads; treat horizon signal as lower-bound progress, not beyond-cap proof.
- Decision update (2026-02-06): X65 confirms the reliability-first horizon lane can run `max_rounds=36` with full sample checkpoints and no upload 500s under reduced payload caps; keep those controls fixed and raise cap gradually for horizon probing, while X66 should tighten behavior-lane late-phase pressure slightly from X64 to target a 15-25% upgrade lead.
- Decision update (2026-02-07): X66 achieved the target late-phase behavior at the lower bound (~15% upgrade lead with build presence), so use X66 as the behavior-lane baseline for the next pair. X67 reached cap 38 but had sample-upload 500s at steps 0/20/40; keep the horizon lane on X65 payload controls and either retry cap 38 or reduce completion payload further before raising cap again.
- Decision update (2026-02-07): X68 confirms the X66-anchored behavior lane remains stable but a small late-floor nudge (`min_build_frac=0.37`) can overshoot the preferred band (~31% late upgrade lead); keep X66 as behavior baseline and use smaller late-pressure deltas.
- Decision update (2026-02-07): X69 shows that even tighter observation payload caps still hit intermittent sample-upload 500 at high-horizon cap 38 when completion payload remains large (~20k-26k tokens/sample); treat horizon evidence as lower-bound only and keep infra-risk explicitly tracked in pass/fail calls.
- Decision update (2026-02-07): X70 meets behavior-lane criteria at the upper bound of the preferred late-phase band (~24% upgrade lead with strong build presence), so keep X66 and X70 as stable lower/upper anchors for late-mix tuning.
- Decision update (2026-02-07): X71 indicates `sampling.max_tokens=32` is below safe macro-plan output budget for the current prompt/observation regime; keep horizon lane at `max_tokens>=40` and treat sub-40 settings as high risk for truncation-driven policy collapse.
- Decision update (2026-02-07): X72 reproduces upper-band behavior-lane success (~25% late upgrade lead with build presence) under stable payload controls, confirming X66 (lower bound) and X70/X72 (upper bound) as robust calibration anchors.
- Decision update (2026-02-07): X73 restores horizon-lane reliability at `max_rounds=38` with full sample coverage and no upload 500s when `max_tokens` is returned to 40; keep this as the new horizon baseline, while treating episode-length gain beyond cap as still unresolved.
- Decision update (2026-02-07): X74 is a viable behavior-lane fallback with cleaner mid/late structure and stable infra, but late upgrade lead (~31%) is still above target; keep X66/X70/X72 as primary behavior anchors and treat X74 as an upper-pressure reference.
- Decision update (2026-02-07): X75 extends the reliability-first horizon lower bound to `>=40` with full sample checkpoints and no upload 500s; continue horizon probing by raising cap incrementally under the same payload controls, while keeping beyond-cap episode length claims explicitly unresolved until a non-cap-stop run is observed.
- Decision update (2026-02-07): X76 re-confirms stable behavior-lane infrastructure with full sample coverage and clean round progression, but its late upgrade lead (~58%) still overshoots target; keep X66/X70/X72 as calibration anchors and use smaller late-pressure changes.
- Decision update (2026-02-07): X77 extends the reliability-first horizon lower bound to `>=42` with full sample checkpoints and no upload 500s; continue cap-raising horizon probes under unchanged payload controls, while keeping true beyond-cap episode-length claims unresolved until a non-cap-stop run is observed.

## Q/R Rollout Snippets (diagnostic detail)

Notes:
- Step indices below are **training steps**, not environment steps.
- Reward breakdown + counterfactuals are replayed from logged observations with the run config (auto-advance on), to make action tradeoffs explicit.
- No samples in Q/R rollouts had `prep_actions_remaining > 1` (all were `1`).

### Run Q (v0.2.7) metadata
- **Config:** `configs/lab/prime-td-auto-advance-80-q.toml`
- **Dataset policy:** `noop_then_start`, `rollout_steps=9`
- **Rules:** `auto_advance_round=true`, `prep_actions_per_round=2`, `prep_actions_round_scale=0.0`, `prep_actions_max=6`
- **start_round_max_prep_remaining:** unset (no gating)

**Q step 0 (training step)** — action `{"type":"build","tower_type":"dart","x":1,"y":3}`
- **State:** round=5, `prep_actions_remaining=1`, cash=902, lives=100
- **Towers:** id 1 dart upgrades:none @(0,4)
- **valid_actions.start_round:** true
- **Reward breakdown:** pop_reward=38.0, end_round_income=100.0, life_loss_penalty=0.0, invalid_action_penalty=0.0, step_penalty=-0.1
- **Simulated round:** yes; **auto-advance credit fix:** no (round already simulated)
- **Counterfactual:** `start_round` would yield ~9.9 reward with ~10 lives lost; best build yields ~137.9 reward with 0 lives lost.

**Q step 40 (training step)** — action `{"type":"start_round"}`
- **State:** round=5, `prep_actions_remaining=1`, cash=902, lives=100
- **Towers:** id 1 dart upgrades:none @(0,5)
- **valid_actions.start_round:** true
- **Reward breakdown:** pop_reward=10.0, end_round_income=100.0, life_loss_penalty=-100.0, invalid_action_penalty=0.0, step_penalty=-0.1
- **Simulated round:** yes; **auto-advance credit fix:** no
- **Counterfactual:** best build yields ~137.9 reward with 0 lives lost vs `start_round` ~9.9 reward with ~10 lives lost.

**Q step 70 (training step)** — action `{"type":"start_round"}`
- **State:** round=5, `prep_actions_remaining=1`, cash=902, lives=100
- **Towers:** id 1 dart upgrades:none @(0,4)
- **valid_actions.start_round:** true
- **Reward breakdown:** pop_reward=12.0, end_round_income=100.0, life_loss_penalty=-80.0, invalid_action_penalty=0.0, step_penalty=-0.1
- **Simulated round:** yes; **auto-advance credit fix:** no
- **Counterfactual:** best build yields ~133.9 reward with 0 lives lost vs `start_round` ~31.9 reward with ~8 lives lost.

### Run R (v0.2.7) metadata
- **Config:** `configs/lab/prime-td-auto-advance-80-r.toml`
- **Dataset policy:** `noop_then_start`, `rollout_steps=9`
- **Rules:** `auto_advance_round=true`, `prep_actions_per_round=2`, `prep_actions_round_scale=0.0`, `prep_actions_max=6`
- **start_round_max_prep_remaining:** 1

**R step 0 (training step)** — action `{"type":"build","tower_type":"dart","x":1,"y":5}` (invalid_position)
- **State:** round=5, `prep_actions_remaining=1`, cash=902, lives=100
- **Towers:** id 1 dart upgrades:none @(0,5)
- **valid_actions.start_round:** true
- **Reward breakdown:** pop_reward=10.0, end_round_income=100.0, life_loss_penalty=-100.0, invalid_action_penalty=-1.0, step_penalty=-0.1
- **Simulated round:** yes; **auto-advance credit fix:** no
- **Counterfactual:** best build yields ~137.9 reward with 0 lives lost; `start_round` ~9.9 reward with ~10 lives lost.

**R step 40 (training step)** — action `{"type":"build","tower_type":"dart","x":1,"y":7}` (invalid_position)
- **State:** round=5, `prep_actions_remaining=1`, cash=902, lives=100
- **Towers:** id 1 dart upgrades:none @(0,5)
- **valid_actions.start_round:** true
- **Reward breakdown:** pop_reward=9.0, end_round_income=100.0, life_loss_penalty=-110.0, invalid_action_penalty=-1.0, step_penalty=-0.1
- **Simulated round:** yes; **auto-advance credit fix:** no
- **Counterfactual:** best build yields ~139.9 reward with 0 lives lost vs `start_round` ~-1.1 reward with ~11 lives lost.

**R step 70 (training step)** — action `{"type":"build","tower_type":"dart","x":1,"y":4}`
- **State:** round=5, `prep_actions_remaining=1`, cash=902, lives=100
- **Towers:** id 1 dart upgrades:none @(0,5)
- **valid_actions.start_round:** true
- **Reward breakdown:** pop_reward=32.0, end_round_income=100.0, life_loss_penalty=0.0, invalid_action_penalty=0.0, step_penalty=-0.1
- **Simulated round:** yes; **auto-advance credit fix:** no
- **Counterfactual:** best build yields ~131.9 reward with 0 lives lost vs `start_round` ~42.9 reward with ~7 lives lost.

## S/T Rollout Snippets (diagnostic detail)

Notes:
- Step indices below are **training steps**, not environment steps.
- Reward breakdown + counterfactuals are replayed from logged observations with the run config (auto-advance on), to make action tradeoffs explicit.
- No samples in S/T rollouts had `prep_actions_remaining > 1` (all were `1`).

### Run S (v0.2.10) metadata
- **Config:** `configs/lab/prime-td-auto-advance-80-s.toml`
- **Dataset policy:** `noop_then_start`, `rollout_steps=9`
- **Rules:** `auto_advance_round=true`, `prep_actions_per_round=2`, `prep_actions_round_scale=0.0`, `prep_actions_max=6`
- **start_round_max_prep_remaining:** 1

**S step 0 (training step)** — action `{"type":"build","tower_type":"dart","x":1,"y":4}`
- **State:** round=5, `prep_actions_remaining=1`, cash=902, lives=100
- **Towers:** id 1 dart upgrades:none @(0,4)
- **valid_actions.start_round:** true
- **Reward breakdown:** pop_reward=40.0, end_round_income=100.0, life_loss_penalty=0.0, invalid_action_penalty=0.0, step_penalty=-0.1
- **Simulated round:** yes; **auto-advance credit fix:** no
- **Counterfactual:** `start_round` would yield ~-1.1 reward with ~11 lives lost; best build yields ~139.9 reward with 0 lives lost.

**S step 40 (training step)** — action `{"type":"build","tower_type":"dart","x":1,"y":0}`
- **State:** round=5, `prep_actions_remaining=1`, cash=902, lives=100
- **Towers:** id 1 dart upgrades:none @(0,0)
- **valid_actions.start_round:** true
- **Reward breakdown:** pop_reward=34.0, end_round_income=100.0, life_loss_penalty=0.0, invalid_action_penalty=0.0, step_penalty=-0.1
- **Simulated round:** yes; **auto-advance credit fix:** no
- **Counterfactual:** `start_round` would yield ~31.9 reward with ~8 lives lost; best build yields ~133.9 reward with 0 lives lost.

**S step 70 (training step)** — action `{"type":"build","tower_type":"dart","x":1,"y":3}`
- **State:** round=5, `prep_actions_remaining=1`, cash=902, lives=100
- **Towers:** id 1 dart upgrades:none @(0,3)
- **valid_actions.start_round:** true
- **Reward breakdown:** pop_reward=28.0, end_round_income=100.0, life_loss_penalty=0.0, invalid_action_penalty=0.0, step_penalty=-0.1
- **Simulated round:** yes; **auto-advance credit fix:** no
- **Counterfactual:** `start_round` would yield ~64.9 reward with ~5 lives lost; best build yields ~127.9 reward with 0 lives lost.

### Run T (v0.2.10) metadata
- **Config:** `configs/lab/prime-td-auto-advance-80-t.toml`
- **Dataset policy:** `noop_then_start`, `rollout_steps=9`
- **Rules:** `auto_advance_round=true`, `prep_actions_per_round=2`, `prep_actions_round_scale=0.0`, `prep_actions_max=6`
- **start_round_max_prep_remaining:** 1
- **Economy:** `starting_cash=200`, `end_round_income=30`

**T step 0 (training step)** — action `{"type":"upgrade","tower_id":1,"path":"a"}`
- **State:** round=5, `prep_actions_remaining=1`, cash=172, lives=100
- **Towers:** id 1 dart upgrades:none @(0,1)
- **valid_actions.start_round:** true
- **Reward breakdown:** pop_reward=28.0, end_round_income=30.0, life_loss_penalty=-20.0, invalid_action_penalty=0.0, step_penalty=-0.1
- **Simulated round:** yes; **auto-advance credit fix:** no
- **Counterfactual:** `start_round` would yield ~-38.1 reward with ~8 lives lost; best upgrade yields ~37.9 reward with ~2 lives lost.

**T step 40 (training step)** — action `{"type":"upgrade","tower_id":1,"path":"a"}`
- **State:** round=5, `prep_actions_remaining=1`, cash=172, lives=100
- **Towers:** id 1 dart upgrades:none @(0,1)
- **valid_actions.start_round:** true
- **Reward breakdown:** pop_reward=35.0, end_round_income=30.0, life_loss_penalty=-50.0, invalid_action_penalty=0.0, step_penalty=-0.1
- **Simulated round:** yes; **auto-advance credit fix:** no
- **Counterfactual:** `start_round` would yield ~-71.1 reward with ~11 lives lost; best upgrade yields ~14.9 reward with ~5 lives lost.

**T step 70 (training step)** — action `{"type":"upgrade","tower_id":1,"path":"a"}`
- **State:** round=5, `prep_actions_remaining=1`, cash=172, lives=100
- **Towers:** id 1 dart upgrades:none @(0,0)
- **valid_actions.start_round:** true
- **Reward breakdown:** pop_reward=31.0, end_round_income=30.0, life_loss_penalty=-30.0, invalid_action_penalty=0.0, step_penalty=-0.1
- **Simulated round:** yes; **auto-advance credit fix:** no
- **Counterfactual:** `start_round` would yield ~-38.1 reward with ~8 lives lost; best upgrade yields ~30.9 reward with ~3 lives lost.

## Repro Commands (to fill once run completes)

- Collect artifacts: `scripts/collect_prime_run_artifacts.sh <RUN_ID>`
- Held-out eval: `python3 scripts/eval.py --eval-seed-start 1000 --eval-seed-count 50 --random-seed-start 2000 --random-seed-count 20 --max-rounds 20 --max-steps 200 --output-dir out/eval`

## Launch Status (x185/x186)

- **Session startup check before launch:** `prime --version`=`0.5.34`, `prime rl -h`, `prime rl run/get/progress/rollouts/logs -h`; no CLI surface drift vs baseline.
- **Coordinator decision executed:** launch `X185` and `X186` now; hold full-run/scale-up while transfer gate remains pending.
- **X185 behavior run launched:** `prime-td-macro-round-60-x185.toml`
  - **Run ID:** `zjqs16svaoitp5c9p9163df4`
  - **Config path:** `configs/lab/prime-td-macro-round-60-x185.toml`
  - **Type:** one-variable from `X183` (`by_phase.late.min_build_frac` `0.3520 -> 0.3510`)
- **X186 policy-quality corrective canary launched:** `prime-td-macro-round-60-x186.toml`
  - **Run ID:** `d362lycrl2p6v52uv1m407ng`
  - **Config path:** `configs/lab/prime-td-macro-round-60-x186.toml`
  - **Type:** one-variable from `X184` (`observation.max_towers` `5 -> 6`), policy-signal canary (not horizon-expansion proof).
- **One-variable diff check:** passed for both lanes (config `name` update + exactly one lane knob changed per child).
- **Conditional next step gate:** launch `X187` only if `X186` is `diagnostic` and non-cap `delta_round` failures are `0`; if `X186` is non-diagnostic or any non-cap delta failure appears, do **not** launch `X187`.

## Completed Runs (x185/x186)

### Run X185
- **Run ID:** `zjqs16svaoitp5c9p9163df4`
- **Config:** `configs/lab/prime-td-macro-round-60-x185.toml`
- **Coverage:** sampled steps `0,10,20,30,40,50`; `4/4/4/4/4/4` samples (`100%`) at sampled steps.
- **Rollouts parsed:** all pages at `--limit 100`, all turns, all samples (`24` samples, `136` turns).
- **Action mix:** `build=142`, `upgrade=127`, `noop=3`
- **Candidate pool:** `build=285`, `upgrade=341`, `noop=136`
- **Plan:** `2-action=136`
- **Phase breakdown:** `mid build/upgrade=46/18`; `late build/upgrade/noop=96/109/3` (late upgrade lead `~13.54%`, late build share `~46.15%`).
- **Full delta-round accounting:** non-cap `pass=88/fail=0/missing=0`; cap `delta1=24/delta0=24/other=0`
- **Candidate reliability:** parse failures `0`, `choose_out_of_range=0`, upload 500s `0`, interleaving warnings `0`

### Run X186
- **Run ID:** `d362lycrl2p6v52uv1m407ng`
- **Config:** `configs/lab/prime-td-macro-round-60-x186.toml`
- **Coverage:** sampled steps `0,10,20,30,40,50`; `4/4/4/4/4/4` samples (`100%`) at sampled steps.
- **Rollouts parsed:** all pages at `--limit 100`, all turns, all samples (`24` samples, `592` turns).
- **Action mix:** `build=151`, `upgrade=991`, `noop=35`
- **Candidate pool:** `build=271`, `upgrade=1056`, `noop=592`
- **Plan:** `2-action=585`, `1-action=7`
- **Phase breakdown (late-only):** `build=151`, `upgrade=991`, `noop=35` (late upgrade lead `~556.29%`, late build share `~12.83%`).
- **Full delta-round accounting:** non-cap `pass=544/fail=0/missing=0`; cap `delta1=24/delta0=24/other=0`
- **Candidate reliability:** parse failures `0`, `choose_out_of_range=0`, upload 500s `0`, interleaving warnings `0`

## Run Verdicts (x185/x186)

- **x185 progression:** PASS
- **x185 plan quality:** PARTIAL (upgrade-leaning recovered, but below 15-25% late lead band and build share remains high)
- **x185 reliability:** diagnostic
- **x185 behavior lower-bound:** PASS (`>=18`)

- **x186 progression:** PASS
- **x186 plan quality:** FAIL (policy-quality corrective canary regressed vs X184: higher late upgrade lead, lower late build share)
- **x186 reliability:** diagnostic
- **x186 horizon lower-bound:** PASS (`>=56`)

## Conditional Launch (x187)

- **Gate check:** `X186` satisfied launch condition (`reliability=diagnostic` and non-cap delta failures `=0`).
- **X187 horizon expansion launched:** `prime-td-macro-round-60-x187.toml`
  - **Run ID:** `z81q96j6d8f5a713rik0g4xk`
  - **Config path:** `configs/lab/prime-td-macro-round-60-x187.toml`
  - **Type:** one-variable from `X186` (`difficulty.max_rounds` `56 -> 60`) with payload fixed.
  - **Launch-time status:** `PENDING`, `progress.steps_with_samples=[]` (pre-sample).

## Transfer (x185/x186)

- **Transfer command:** `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --out output/transfer/x185_x186.json --json`
- **Transfer outcome:** `gate_status=pending`
- **Reason:** `Baseline metrics unavailable for transfer delta thresholds`
- **Latest metrics:** `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`

## Direction Scorecard (post x185/x186)

- **training_quality:** `PARTIAL` (behavior lane partial + horizon lane fail)
- **reliability:** `PASS` (both runs diagnostic)
- **horizon_confidence:** `PASS` (reliable lower-bound still `>=56`; `X187` launched as pure horizon probe)
- **transfer_readiness:** `PENDING` (baseline threshold still unavailable; full-run/scale-up remains blocked)

## Completed Run (x187)

- **Session startup check before analysis:** `prime --version`=`0.5.34`, `prime rl -h`, `prime rl get/progress/rollouts/logs -h`; no CLI surface drift vs baseline.
- **Run ID:** `z81q96j6d8f5a713rik0g4xk`
- **Config:** `configs/lab/prime-td-macro-round-60-x187.toml`
- **Completion:** `completed_at=2026-02-13 12:08:10.391000`
- **Coverage:** sampled steps `0,10,20,30,40,50`; `4/4/4/4/4/4` samples (`100%`) at sampled steps.
- **Rollouts parsed:** all pages at `--limit 100`, all turns, all samples (`24` samples, `692` turns).
- **Action mix:** `build=157`, `upgrade=1151`, `noop=17`
- **Candidate pool:** `build=272`, `upgrade=1258`, `noop=692`
- **Plan:** `2-action=633`, `1-action=59`
- **Phase breakdown (late-only):** `build=157`, `upgrade=1151`, `noop=17` (late upgrade lead `~633.12%`, late build share `~11.85%`).
- **Full delta-round accounting:** non-cap `pass=644/fail=0/missing=0`; cap `delta1=24/delta0=24/other=0`
- **Candidate reliability:** parse failures `0`, `choose_out_of_range=0`, upload 500s `0`, interleaving warnings `0`

## Run Verdict (x187)

- **x187 progression:** PASS
- **x187 plan quality:** FAIL (extreme late over-upgrade persists and worsens vs X186 policy canary)
- **x187 reliability:** diagnostic
- **x187 horizon lower-bound:** PASS (`>=60`)

## Transfer (x187)

- **Transfer command:** `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --out output/transfer/x187.json --json`
- **Transfer outcome:** `gate_status=pending`
- **Reason:** `Baseline metrics unavailable for transfer delta thresholds`
- **Latest metrics:** `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`

## Transfer Gate Transition (x187 baseline canonical)

- **Transition:** `pending -> pass`
- **Validation command (exact):** `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --baseline-canonical --out output/transfer/x187-check.json --json`
- **Evidence path:** `output/transfer/x187-check.json`
- **Result:** `gate_status=pass`, `gate_reason=\"Transfer gate thresholds satisfied\"`
- **Canonical metrics (unchanged):** `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`

## Direction Scorecard (post x187)

- **training_quality:** `PARTIAL` (behavior lane still partial from X185; horizon lane fails policy quality on X187)
- **reliability:** `PASS` (X185/X186/X187 diagnostic)
- **horizon_confidence:** `PASS` (reliable cap-hit lower bound now `>=60`)
- **transfer_readiness:** `PENDING` (full-run/scale-up remains blocked by baseline-threshold gate)

## Decision / Next Step (proposed, not launched)

- **Collab deliberation:** launch is valid now for a diagnostic canary pair (latest runs diagnostic, non-cap delta failures remain `0`).
- **Next pair strategy (one-variable diffs):**
  - **X188 behavior lane:** one-variable from `X185` with `env.args.config.observation.candidate_balance.by_phase.late.min_build_frac` `0.3510 -> 0.3508`.
  - **X189 horizon lane:** one-variable policy-quality corrective from `X187` with `env.args.config.observation.max_build_slots` `5 -> 6` (keep `max_rounds=60`, `max_towers=6`, and payload controls otherwise fixed).
- **Goal link:** raise behavior late upgrade lead into band while testing whether added build-option availability reduces horizon over-upgrade at the now-reliable `>=60` cap.
- **Hypothesis:** tiny behavior nudge restores `15-25%` late upgrade lead with build presence; horizon build-slot increase decreases late upgrade lead below `633.12%` and increases build share above `11.85%` without reliability regression.
- **Success metric:** PASS if both runs are diagnostic with non-cap fail `0`, X188 late upgrade lead enters `15-25%`, and X189 improves both horizon policy metrics (`lead < 633.12%` and `build share > 11.85%`); PARTIAL if both runs are diagnostic but only one lane meets target while the other is directionally improved; FAIL on any non-diagnostic run, any non-cap delta failure, or no directional improvement.
- **Stop condition:** if any non-cap delta failure appears, or if X189 is diagnostic but fails to improve both late policy metrics vs X187, hold horizon changes and pivot to policy-quality root-cause at fixed horizon.

## Launch Status (x188/x189)

- **Session startup check before launch:** `prime --version`=`0.5.34`, `prime rl -h`, `prime rl run/get/progress/rollouts/logs -h`; no CLI surface drift.
- **Collab deliberation (strict x183-x187 history):** launch is valid as diagnostic canary only; no full-run/scale-up claim without reproducible behavior criteria (`2` consecutive runs).
- **X188 behavior run launched:** `prime-td-macro-round-60-x188.toml`
  - **Run ID:** `twkr0lrw67xewzovcisnmojv`
  - **Config path:** `configs/lab/prime-td-macro-round-60-x188.toml`
  - **Type:** one-variable from `X185` (`by_phase.late.min_build_frac` `0.3510 -> 0.3508`)
- **X189 horizon-policy corrective run launched:** `prime-td-macro-round-60-x189.toml`
  - **Run ID:** `i5k4wb8em65vods8bvu49xpg`
  - **Config path:** `configs/lab/prime-td-macro-round-60-x189.toml`
  - **Type:** one-variable from `X187` (`observation.max_build_slots` `5 -> 6`, keep `max_rounds=60`, `max_towers=6`, payload fixed)
- **One-variable diff check:** passed for both lanes.
- **Post-launch status:** both `PENDING` with `progress.steps_with_samples=[]` (pre-start state).

## Completed Runs (x188/x189)

### Run X188
- **Run ID:** `twkr0lrw67xewzovcisnmojv`
- **Config:** `configs/lab/prime-td-macro-round-60-x188.toml`
- **Completion:** `completed_at=2026-02-13 12:47:26.183000`
- **Coverage:** sampled steps `0,10,20,30,40,50`; `4/4/4/4/4/4` samples (`100%`) at sampled steps.
- **Rollouts parsed:** all pages at `--limit 100`, all turns, all samples (`24` samples, `104` turns).
- **Action mix:** `build=122`, `upgrade=78`, `noop=7`
- **Candidate pool:** `build=254`, `upgrade=274`, `noop=104`
- **Plan:** `2-action=103`, `1-action=1`
- **Phase breakdown:** `mid build/upgrade=27/5`; `late build/upgrade/noop=95/73/7` (late upgrade lead `~-23.16%`, late build share `~54.29%`).
- **Full delta-round accounting:** non-cap `pass=56/fail=0/missing=0`; cap `delta1=24/delta0=24/other=0`
- **Candidate reliability:** parse failures `0`, `choose_out_of_range=0`, upload 500s `0`, interleaving warnings `0`

### Run X189
- **Run ID:** `i5k4wb8em65vods8bvu49xpg`
- **Config:** `configs/lab/prime-td-macro-round-60-x189.toml`
- **Completion:** `completed_at=2026-02-13 13:18:40.234000`
- **Coverage:** sampled steps `0,10,20,30,40,50`; `4/4/4/4/4/4` samples (`100%`) at sampled steps.
- **Rollouts parsed:** all pages at `--limit 100`, all turns, all samples (`24` samples, `684` turns).
- **Action mix:** `build=168`, `upgrade=1046`, `noop=14`
- **Candidate pool:** `build=248`, `upgrade=1250`, `noop=684`
- **Plan:** `2-action=544`, `1-action=140`
- **Phase breakdown (late-only):** `build=168`, `upgrade=1046`, `noop=14` (late upgrade lead `~522.62%`, late build share `~13.68%`).
- **Full delta-round accounting:** non-cap `pass=636/fail=0/missing=0`; cap `delta1=24/delta0=24/other=0`
- **Candidate reliability:** parse failures `0`, `choose_out_of_range=0`, upload 500s `0`, interleaving warnings `0`

## Run Verdicts (x188/x189)

- **x188 progression:** PASS
- **x188 plan quality:** FAIL (behavior lane regressed into stronger late build-leading policy vs X185)
- **x188 reliability:** diagnostic
- **x188 behavior lower-bound:** PASS (`>=18`)

- **x189 progression:** PASS
- **x189 plan quality:** FAIL (still extreme late over-upgrade despite directional improvement vs X187)
- **x189 reliability:** diagnostic
- **x189 horizon lower-bound:** PASS (`>=60`)

## Transfer (x188/x189 baseline canonical)

- **Transfer command:** `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --baseline-canonical --out output/transfer/x188_x189.json --json`
- **Transfer outcome:** `gate_status=pass`
- **Reason:** `Transfer gate thresholds satisfied`
- **Latest metrics:** `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`

## Direction Scorecard (post x188/x189)

- **training_quality:** `FAIL` (both lanes fail plan-quality criteria)
- **reliability:** `PASS` (both runs diagnostic)
- **horizon_confidence:** `PASS` (reliable cap-hit lower bound remains `>=60`)
- **transfer_readiness:** `PASS` (canonical baseline gate now passing)

## Decision / Next Step (proposed, not launched)

- **Full-run/scale-up:** **HOLD**. Transfer gate is now PASS, but behavior criteria are not reproducibly met (`X185` partial followed by `X188` fail), so the 2-consecutive-run behavior requirement is unsatisfied.
- **Next behavior-lane probe (one-variable):** from `X185`, `env.args.config.observation.candidate_balance.by_phase.late.min_build_frac` `0.3510 -> 0.3509` (smaller corrective than X188) for signal confirmation.
- **Next horizon-policy probe (one-variable):** from `X189`, `env.args.config.observation.candidate_balance.by_phase.late.min_build_frac` `0.70 -> 0.72` (keep `max_rounds=60`, `max_towers=6`, `max_build_slots=6`, payload fixed).
- **Stop condition:** any non-cap delta failure, any non-diagnostic reliability verdict, or no directional behavior recovery toward late `15-25%` upgrade lead with build presence.

## Decision / Next Step (x190/x191 launched)

- **Session startup checks before deliberation+launch (2026-02-13):** reran `prime --version`, `prime rl -h`, `prime rl run -h`, `prime rl get -h`, `prime rl progress -h`, `prime rl rollouts -h`, `prime rl logs -h`; local CLI remained `0.5.34` with no help-surface drift.
- **Strict collab deliberation (x183-x189 context):** ran two-sided subagent review (advocate + challenger). Consensus: no clearly better one-variable pair is proven against current evidence and guardrails, so execute default pair.
- **Challenger alternative considered/rejected:** behavior/horizon `late.max_upgrade_candidates` pivots were not selected because they introduce a new lever-family before taking the required behavior stability anchor replicate at the closest in-band setting.
- **Decision policy applied:** keep full-run/scale-up **HOLD** until behavior criteria are reproducibly in-band for `2` consecutive runs.

## Launch Status (x190/x191)

- **X190 behavior stability anchor launched:** `prime-td-macro-round-60-x190.toml`
  - **Run ID:** `zmmzp14vju5baqjixegnhio5`
  - **Config path:** `configs/lab/prime-td-macro-round-60-x190.toml`
  - **Type:** exact replicate of `X185` (no knob changes).
- **X191 horizon policy corrective launched:** `prime-td-macro-round-60-x191.toml`
  - **Run ID:** `oimes3mg8wobsp4e6e546pl8`
  - **Config path:** `configs/lab/prime-td-macro-round-60-x191.toml`
  - **Type:** one-variable from `X189` with `env.args.config.observation.candidate_balance.by_phase.late.min_build_frac` `0.70 -> 0.72` (keep `max_rounds=60`, `max_towers=6`, `max_build_slots=6`, payload fixed).
- **One-variable diff check:** passed (`X190` exact replicate, `X191` single policy knob change).
- **Post-launch status:** both runs `RUNNING`; `progress.steps_with_samples=[]` for both at capture time (pre-sample).

## Completed Runs (x190/x191)

### Run X190
- **Run ID:** `zmmzp14vju5baqjixegnhio5`
- **Config:** `configs/lab/prime-td-macro-round-60-x190.toml`
- **Completion:** `completed_at=2026-02-13 14:15:51.125000`
- **Coverage:** sampled steps `0,10,20,30,40,50`; `4/4/4/4/4/4` samples (`100%`) at sampled steps.
- **Rollouts parsed:** all sampled-step rollouts at `--limit 100`, all turns, all samples (`24` samples, `120` turns).
- **Action mix:** `build=130`, `upgrade=103`, `noop=5`
- **Candidate pool:** `build=248`, `upgrade=312`, `noop=120`
- **Plan:** `2-action=118`, `1-action=2`
- **Phase breakdown:** `mid build/upgrade=40/7`; `late build/upgrade/noop=90/96/5` (late upgrade lead `~6.67%`, late build share `~47.12%`).
- **Full delta-round accounting:** non-cap `pass=72/fail=0/missing=0`; cap `delta1=24/delta0=24/other=0`
- **Candidate reliability:** parse failures `0`, `choose_out_of_range=0`, upload 500s `0`, interleaving warnings `0`

### Run X191
- **Run ID:** `oimes3mg8wobsp4e6e546pl8`
- **Config:** `configs/lab/prime-td-macro-round-60-x191.toml`
- **Completion:** `completed_at=2026-02-13 14:24:45.258000`
- **Coverage:** sampled steps `0,10,20,30,40,50`; `4/4/4/4/4/4` samples (`100%`) at sampled steps.
- **Rollouts parsed:** all sampled-step rollouts at `--limit 100`, all turns, all samples (`24` samples, `712` turns).
- **Action mix:** `build=170`, `upgrade=1125`, `noop=43`
- **Candidate pool:** `build=318`, `upgrade=1283`, `noop=712`
- **Plan:** `2-action=626`, `1-action=86`
- **Phase breakdown (late-only):** `build=170`, `upgrade=1125`, `noop=43` (late upgrade lead `~561.76%`, late build share `~12.71%`).
- **Full delta-round accounting:** non-cap `pass=664/fail=0/missing=0`; cap `delta1=24/delta0=24/other=0`
- **Candidate reliability:** parse failures `0`, `choose_out_of_range=0`, upload 500s `0`, interleaving warnings `0`

## Run Verdicts (x190/x191)

- **x190 progression:** PASS
- **x190 plan quality:** PARTIAL (upgrade-leaning but still below the 15-25% late lead target band; build share remains high)
- **x190 reliability:** diagnostic
- **x190 behavior lower-bound:** PASS (`>=18`)

- **x191 progression:** PASS
- **x191 plan quality:** FAIL (horizon policy regressed vs X189: higher late upgrade lead, lower late build share)
- **x191 reliability:** diagnostic
- **x191 horizon lower-bound:** PASS (`>=60`)

## Transfer (x190/x191 baseline canonical)

- **Required command:** `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --baseline-canonical --out output/transfer/x190_x191.json --json`
- **Initial run note:** command first failed because canonical baseline file was missing (`output/transfer/baselines/core-v1__core-v1-default.json`).
- **Baseline republish command:** `npm run benchmark:transfer:baseline -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400`
- **Final transfer outcome:** `gate_status=pass`, `gate_reason=Transfer gate thresholds satisfied`
- **Output path:** `output/transfer/x190_x191.json`
- **Metrics:** `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`

## Direction Scorecard (post x190/x191)

- **training_quality:** `PARTIAL` (behavior lane partial + horizon lane fail)
- **reliability:** `PASS` (both runs diagnostic)
- **horizon_confidence:** `PASS` (reliable cap-hit lower-bound remains `>=60`)
- **transfer_readiness:** `PASS` (canonical baseline gate passing)

## Decision / Next Step (proposed, not launched)

- **Full-run/scale-up:** **HOLD**. Behavior reproducibility criteria remain unsatisfied (still no two consecutive in-band behavior runs).
- **Behavior-lane next probe (one-variable from X190):** `env.args.config.observation.candidate_balance.by_phase.late.max_upgrade_candidates` `3 -> 4` (pivot lever-family; avoid another tiny late floor tweak).
- **Horizon-lane next probe (one-variable from X191):** `env.args.config.observation.candidate_balance.by_phase.late.max_upgrade_candidates` `2 -> 1` (keep `max_rounds=60`, `max_towers=6`, `max_build_slots=6`, payload fixed).
- **Goal link:** recover behavior lane into the 15-25% late upgrade-lead band while reducing horizon over-upgrade with a stronger structural lever.
- **Success metric:** PASS if both runs are diagnostic with non-cap fail `0`, behavior late upgrade lead enters `15-25%`, and horizon late metrics improve beyond the best recent anchor (`lead < 522.62%`, `build share > 13.68%`); PARTIAL if only one lane improves under diagnostic reliability; FAIL on any non-diagnostic run, any non-cap delta failure, or no directional horizon improvement.
- **Stop condition:** if any non-cap delta failure appears, halt policy claims and pivot to reliability/root-cause workflow.

## Decision / Next Step (x192/x193 launched)

- **Session startup checks before deliberation+launch (2026-02-13):** reran `prime --version`, `prime rl -h`, `prime rl run -h`, `prime rl get -h`, `prime rl progress -h`, `prime rl rollouts -h`, `prime rl logs -h`; local CLI remained `0.5.34` with no help-surface drift.
- **Strict collab deliberation (x183-x191 context):** two-sided subagent review executed; no clearly better one-variable pair was proven over the coordinator default under current policy/constraints.
- **Coordinator default accepted:** launch structural-pivot pair on `by_phase.late.max_upgrade_candidates`.

## Launch Status (x192/x193)

- **X192 behavior structural-pivot launched:** `prime-td-macro-round-60-x192.toml`
  - **Run ID:** `hylx9lzhprfi65twlcwwohh6`
  - **Config path:** `configs/lab/prime-td-macro-round-60-x192.toml`
  - **Type:** one-variable from `X190` with `env.args.config.observation.candidate_balance.by_phase.late.max_upgrade_candidates` `3 -> 4`.
- **X193 horizon structural-pivot launched:** `prime-td-macro-round-60-x193.toml`
  - **Run ID:** `dkhf66z2gm89k98ubhew2ezz`
  - **Config path:** `configs/lab/prime-td-macro-round-60-x193.toml`
  - **Type:** one-variable from `X191` with `env.args.config.observation.candidate_balance.by_phase.late.max_upgrade_candidates` `2 -> 1` (keep `max_rounds=60`, `max_towers=6`, `max_build_slots=6`, payload fixed).
- **One-variable diff check:** passed for both lanes.
- **Post-launch status:** both runs `PENDING`; `progress.steps_with_samples=[]` for both at capture time (pre-sample).

## Completed Runs (x192/x193)

### Run X192
- **Run ID:** `hylx9lzhprfi65twlcwwohh6`
- **Config:** `configs/lab/prime-td-macro-round-60-x192.toml`
- **Completion:** `completed_at=2026-02-13 15:23:07.029000`
- **Coverage:** sampled steps `0,10,20,30,40,50`; `4/4/4/4/4/4` samples (`100%`) at sampled steps.
- **Rollouts parsed:** all sampled-step rollouts at `--limit 100`, all turns, all samples (`24` samples, `120` turns).
- **Action mix:** `build=100`, `upgrade=129`, `noop=10`
- **Candidate pool:** `build=248`, `upgrade=374`, `noop=120`
- **Plan:** `2-action=119`, `1-action=1`
- **Phase breakdown:** `mid build/upgrade/noop=33/13/1`; `late build/upgrade/noop=67/116/9` (late upgrade lead `~73.13%`, late build share `~34.90%`).
- **Full delta-round accounting:** non-cap `pass=72/fail=0/missing=0`; cap `delta1=24/delta0=24/other=0`
- **Candidate reliability:** parse failures `0`, `choose_out_of_range=0`, upload 500s `0`, interleaving warnings `0`

### Run X193
- **Run ID:** `dkhf66z2gm89k98ubhew2ezz`
- **Config:** `configs/lab/prime-td-macro-round-60-x193.toml`
- **Completion:** `completed_at=2026-02-13 15:46:06.057000`
- **Coverage:** sampled steps `0,10,20,30,40,50`; `4/4/4/4/4/4` samples (`100%`) at sampled steps.
- **Rollouts parsed:** all sampled-step rollouts at `--limit 100`, all turns, all samples (`24` samples, `666` turns).
- **Action mix:** `build=158`, `upgrade=580`, `noop=108`
- **Candidate pool:** `build=265`, `upgrade=642`, `noop=666`
- **Plan:** `2-action=201`, `1-action=465`, `choose_out_of_range=21`
- **Phase breakdown (late-only):** `build=158`, `upgrade=580`, `noop=108` (late upgrade lead `~267.09%`, late build share `~18.68%`).
- **Full delta-round accounting:** non-cap `pass=619/fail=0/missing=1`; cap `delta1=23/delta0=23/other=0`
- **Reliability note:** one sampled rollout ended on an assistant turn without a post-turn user observation (counted as non-cap missing for strict delta accounting).
- **Candidate reliability:** parse failures `0`, upload 500s `0`, interleaving warnings `0`

## Run Verdicts (x192/x193)

- **x192 progression:** PASS
- **x192 plan quality:** PARTIAL (upgrade-leaning with build presence, but well above the `15-25%` target band)
- **x192 reliability:** diagnostic
- **x192 behavior lower-bound:** PASS (`>=18`)

- **x193 progression:** PARTIAL (non-cap missing `1`; no non-cap delta failures)
- **x193 plan quality:** **NO_POLICY_CLAIM** (run non-diagnostic)
- **x193 reliability:** non_diagnostic
- **x193 horizon lower-bound:** **NO_POLICY_CLAIM** (non-diagnostic run)

## Pair Outcome (x192/x193)

- **Pair verdict:** **FAIL** (policy rule: any non-diagnostic run -> FAIL for pair claims).
- **PASS criteria check:** not met (`x192` behavior outside `15-25%`; `x193` non-diagnostic).
- **PARTIAL criteria check:** not met (reliability gate failed on `x193`, and behavior lane did not improve directionally vs parent).

## Transfer (x192/x193 baseline canonical)

- **Preflight:** canonical baseline republished before transfer check: `npm run benchmark:transfer:baseline -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400`
- **Required command:** `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --baseline-canonical --out output/transfer/x192_x193.json --json`
- **Transfer outcome:** `gate_status=pass`, `gate_reason=Transfer gate thresholds satisfied`
- **Post-completion recheck:** reran required command after `X193` terminal completion; result unchanged (`gate_status=pass`).
- **Output path:** `output/transfer/x192_x193.json`
- **Metrics:** `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`

## Direction Scorecard (post x192/x193)

- **training_quality:** `FAIL` (no claimable pair-level policy pass; behavior still out-of-band and horizon run non-diagnostic)
- **reliability:** `PARTIAL` (`x192` diagnostic, `x193` non_diagnostic)
- **horizon_confidence:** `PARTIAL` (directional signal present, but non-diagnostic)
- **transfer_readiness:** `PASS` (canonical baseline gate passing)

## Decision / Next Step (proposed, not launched)

- **Launch posture:** **HOLD policy-quality launches** until `x193` reliability is recovered (strict non-cap missing must be 0).
- **Immediate reliability action:** run an exact reliability replicate of `x193` config (no knob changes) to recover diagnostic evidence before making any horizon-policy claim.
- **Behavior lever-family counter:** `1/3` completed on this lever family (`x192` miss); do not pivot lever family yet, but do not claim policy closure.
- **If reliability replicate is diagnostic:** continue behavior lever-family experiment `2/3` with one-variable adjustment; if behavior still misses band after `3/3`, pivot to new lever family per stop condition.

## Decision / Next Step (x194/x195 launched)

- **Session startup checks before launch (2026-02-14 AEDT):** reran `prime --version`, `prime rl -h`, `prime rl run -h`, `prime rl get -h`, `prime rl progress -h`, `prime rl rollouts -h`, `prime rl logs -h`.
- **Local CLI source-of-truth:** `Prime CLI version: 0.5.34`.
- **CLI drift record:** no monitoring-surface drift vs prior session for required subcommands (`run/get/progress/rollouts/logs`).
- **Coordinator decision applied:** keep full-run/scale-up `HOLD`; prioritize horizon reliability recovery while continuing one-variable behavior correction in parallel.

## Launch Status (x194/x195)

- **X194 horizon reliability replicate launched:** `prime-td-macro-round-60-x194.toml`
  - **Run ID:** `dr64eju2ygqogh1yud5prlka`
  - **Config path:** `configs/lab/prime-td-macro-round-60-x194.toml`
  - **Type:** exact replicate of `X193` (no knob changes), goal `non-cap missing=0`.
- **X195 behavior corrective launched:** `prime-td-macro-round-60-x195.toml`
  - **Run ID:** `ljdqkny63f5e1b5jcqkowsue`
  - **Config path:** `configs/lab/prime-td-macro-round-60-x195.toml`
  - **Type:** one-variable from `X192` with `env.args.config.observation.candidate_balance.by_phase.late.min_build_frac` `0.3510 -> 0.3520` (keep `late.max_upgrade_candidates=4`).
- **One-variable diff check:** passed for both lanes (`X194` exact replicate metadata-only, `X195` single knob change).
- **Post-launch status at capture:** both runs `QUEUED`; rollout sampling not started yet.

## Completed Runs (x194/x195)

### Run X194
- **Run ID:** `dr64eju2ygqogh1yud5prlka`
- **Config:** `configs/lab/prime-td-macro-round-60-x194.toml`
- **Completion:** `completed_at=2026-02-13 17:26:25.764000`
- **Coverage:** sampled steps `0,10,20,30,40,50`; `4/4/4/4/4/4` samples (`100%`) at sampled steps.
- **Rollouts parsed:** all sampled-step rollouts at `--limit 100`, all turns, all samples (`24` samples, `696` turns).
- **Action mix:** `build=165`, `upgrade=601`, `noop=138`
- **Candidate pool:** `build=277`, `upgrade=671`, `noop=696`
- **Plan:** `2-action=208`, `1-action=488`
- **Phase breakdown (late-only):** `build=165`, `upgrade=601`, `noop=138` (late upgrade lead `~264.24%`, late build share `~18.25%`).
- **Full delta-round accounting:** non-cap `pass=648/fail=0/missing=0`; cap `delta1=24/delta0=24/other=0`
- **Candidate reliability:** parse failures `0`, `choose_out_of_range=0`, upload 500s `0`, interleaving warnings `0`
- **Runtime notes:** occasional `Cancelled 1 old rollout requests` warnings observed; treated as informational because coverage/delta checks remained clean.

### Run X195
- **Run ID:** `ljdqkny63f5e1b5jcqkowsue`
- **Config:** `configs/lab/prime-td-macro-round-60-x195.toml`
- **Completion:** `completed_at=2026-02-13 16:34:20.997000`
- **Coverage:** sampled steps `0,10,20,30,40,50`; `4/4/4/4/4/4` samples (`100%`) at sampled steps.
- **Rollouts parsed:** all sampled-step rollouts at `--limit 100`, all turns, all samples (`24` samples, `116` turns).
- **Action mix:** `build=118`, `upgrade=105`, `noop=2`
- **Candidate pool:** `build=250`, `upgrade=344`, `noop=116`
- **Plan:** `2-action=109`, `1-action=7`
- **Phase breakdown:** `mid build/upgrade/noop=36/7/0`; `late build/upgrade/noop=82/98/2` (late upgrade lead `~19.51%`, late build share `~45.05%`).
- **Full delta-round accounting:** non-cap `pass=68/fail=0/missing=0`; cap `delta1=24/delta0=24/other=0`
- **Candidate reliability:** parse failures `0`, `choose_out_of_range=0`, upload 500s `0`, interleaving warnings `0`

## Run Verdicts (x194/x195)

- **x194 progression:** PASS
- **x194 plan quality:** PARTIAL (late over-upgrade persists despite clean reliability)
- **x194 reliability:** diagnostic
- **x194 horizon lower-bound:** PASS (`>=60`)

- **x195 progression:** PASS
- **x195 plan quality:** PASS (late upgrade lead `~19.51%` in target `15-25%` band)
- **x195 reliability:** diagnostic
- **x195 behavior lower-bound:** PASS (`>=18`)

## Pair Outcome (x194/x195)

- **Pair verdict:** **PASS**.
- **PASS criteria check:** met (`x194` diagnostic with non-cap missing `0`; `x195` diagnostic with late upgrade lead in `15-25%` band).
- **PARTIAL criteria check:** not applicable (PASS achieved).

## Transfer (x194/x195 baseline canonical)

- **Preflight baseline republish:** `npm run benchmark:transfer:baseline -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400`
- **Required command:** `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --baseline-canonical --out output/transfer/x194_x195.json --json`
- **Transfer outcome:** `gate_status=pass`, `gate_reason=Transfer gate thresholds satisfied`
- **Output path:** `output/transfer/x194_x195.json`
- **Metrics:** `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`

## Direction Scorecard (post x194/x195)

- **training_quality:** `PARTIAL` (behavior lane hit target; horizon lane still over-upgrade on plan-quality axis)
- **reliability:** `PASS` (both runs diagnostic; x194 non-cap missing recovered to `0`)
- **horizon_confidence:** `PASS` (`>=60` with clean strict non-cap delta accounting)
- **transfer_readiness:** `PASS` (baseline-canonical gate passing)

## Decision / Next Step (proposed, not launched)

- **Full-run/scale-up:** **HOLD** (coordinator policy unchanged).
- **Operational outcome:** horizon reliability recovery objective met on `X194`; behavior corrective objective met on `X195`.

## Decision / Next Step (x196/x197 launched)

- **Session startup checks before launch (2026-02-14 AEDT):** reran `prime --version`, `prime rl -h`, `prime rl run -h`, `prime rl get -h`, `prime rl progress -h`, `prime rl rollouts -h`, `prime rl logs -h`.
- **Local CLI source-of-truth:** `Prime CLI version: 0.5.34`.
- **CLI drift record:** no drift vs prior startup captures for required monitoring subcommands (`run/get/progress/rollouts/logs`).
- **Coordinator decision applied:** full-run/scale-up remains `HOLD`; launch controlled pair with one-variable-per-lane.

## Launch Status (x196/x197)

- **X196 behavior reproducibility replicate launched:** `prime-td-macro-round-60-x196.toml`
  - **Run ID:** `whoa9thifpmbyelgp6h76te8`
  - **Config path:** `configs/lab/prime-td-macro-round-60-x196.toml`
  - **Type:** exact replicate of `X195` (no knob changes).
- **X197 horizon policy corrective launched:** `prime-td-macro-round-60-x197.toml`
  - **Run ID:** `t08qc46srsd5guvehodm9iqg`
  - **Config path:** `configs/lab/prime-td-macro-round-60-x197.toml`
  - **Type:** one-variable from `X194` with `env.args.config.observation.candidate_balance.by_phase.late.min_build_frac` `0.72 -> 0.75` (payload fixed).
- **One-variable diff check:** passed for both lanes (`X196` metadata-only replicate, `X197` single knob change).
- **Post-launch status at capture:** both runs `QUEUED`.

## Completed Runs (x196/x197)

### Run X196
- **Run ID:** `whoa9thifpmbyelgp6h76te8`
- **Config:** `configs/lab/prime-td-macro-round-60-x196.toml`
- **Completion:** `completed_at=2026-02-13 18:01:05.432000`
- **Coverage:** sampled steps from `progress.steps_with_samples` were `0/10/20/30/50`; `4/4/4/4/4` samples (`100%`) at sampled steps.
- **Rollouts parsed:** all sampled-step rollouts at `--limit 100`, all turns, all samples (`20` samples, `176` completion-turn messages).
- **Action mix:** `build=68`, `upgrade=101`, `noop=7`
- **Candidate pool:** `build=206`, `upgrade=285`, `noop=88`
- **Phase breakdown:** `mid build/upgrade/noop=16/12/0`; `late build/upgrade/noop=52/89/7` (late upgrade lead `~71.15%`, late build share `~35.14%`).
- **Full delta-round accounting:** non-cap `pass=48/fail=0/missing=0`; cap `delta1=20/delta0=20/other=0`
- **Candidate reliability:** parse failures `0`, `choose_out_of_range=0`, upload 500s `0`, interleaving warnings `0`

### Run X197
- **Run ID:** `t08qc46srsd5guvehodm9iqg`
- **Config:** `configs/lab/prime-td-macro-round-60-x197.toml`
- **Completion:** `completed_at=2026-02-13 18:35:39.547000`
- **Coverage:** sampled steps from `progress.steps_with_samples` were `10/20/30/40/50`; `4/4/4/4/4` samples (`100%`) at sampled steps.
- **Rollouts parsed:** all sampled-step rollouts at `--limit 100`, all turns, all samples (`20` samples, `1152` completion-turn messages).
- **Action mix:** `build=135`, `upgrade=527`, `noop=155`
- **Candidate pool:** `build=243`, `upgrade=555`, `noop=576`
- **Phase breakdown (late-only):** `build=135`, `upgrade=527`, `noop=155` (late upgrade lead `~290.37%`, late build share `~16.52%`).
- **Full delta-round accounting:** non-cap `pass=536/fail=0/missing=0`; cap `delta1=20/delta0=20/other=0`
- **Candidate reliability:** parse failures `0`, `choose_out_of_range=0`, upload 500s `0`, interleaving warnings `1`
- **Runtime note:** one `No trajectory steps ... Skipping rollout` warning appeared in orchestrator logs; sampled-step coverage remained 100% at all reported sampled steps.

## Run Verdicts (x196/x197)

- **x196 progression:** PASS
- **x196 plan quality:** FAIL (late upgrade lead `~71.15%` is outside behavior target `15-25%`)
- **x196 reliability:** diagnostic
- **x196 behavior lower-bound:** PASS (`>=18`)

- **x197 progression:** PASS
- **x197 plan quality:** FAIL (directional horizon objective not met vs `x194`: lead `290.37%` is not `<264.24%`, build share `16.52%` is not `>18.25%`)
- **x197 reliability:** diagnostic
- **x197 horizon lower-bound:** PASS (`>=60`)

## Pair Outcome (x196/x197)

- **Pair verdict:** **FAIL**.
- **FAIL criteria trigger:** no reliability failure, but policy targets missed in both lanes (`x196` out-of-band; `x197` not directionally improved vs `x194`).
- **Behavior reproducibility gate:** **NOT satisfied** (`x195` in-band followed by `x196` out-of-band).

## Transfer (x196/x197 baseline canonical)

- **Required command:** `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --baseline-canonical --out output/transfer/x196_x197.json --json`
- **Transfer outcome:** `gate_status=pass`, `gate_reason=Transfer gate thresholds satisfied`
- **Output path:** `output/transfer/x196_x197.json`
- **Metrics:** `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`

## Direction Scorecard (post x196/x197)

- **training_quality:** `FAIL` (both lane policy targets missed)
- **reliability:** `PASS` (both runs diagnostic with clean strict non-cap delta accounting)
- **horizon_confidence:** `PASS` (`>=60` lower-bound remains clean/reproducible)
- **transfer_readiness:** `PASS` (baseline-canonical gate passing)

## Decision / Next Step (proposed, not launched)

- **Full-run/scale-up:** **HOLD** (policy unchanged).
- **Behavior lane recommendation (one-variable, structural pivot):** from `x196`, change `env.args.config.observation.candidate_balance.by_phase.late.max_upgrade_candidates` `4 -> 3` (stop relying on min-build-frac micro behavior as primary correction lever).
- **Horizon lane recommendation (one-variable corrective rollback):** from `x197`, change `env.args.config.observation.candidate_balance.by_phase.late.min_build_frac` `0.75 -> 0.72` to revert the regressive horizon change while keeping payload fixed.

## Decision / Next Step (x198/x199 launched)

- **Session startup checks before launch (2026-02-14 AEDT):** reran `prime --version`, `prime rl -h`, `prime rl run -h`, `prime rl get -h`, `prime rl progress -h`, `prime rl rollouts -h`, `prime rl logs -h`.
- **Local CLI source-of-truth:** `Prime CLI version: 0.5.34`.
- **CLI drift record:** no drift vs prior startup captures for required monitoring subcommands (`run/get/progress/rollouts/logs`).
- **Coordinator decision applied:** keep full-run/scale-up `HOLD`; launch one-variable corrective pair to recover behavior direction and restore horizon anchor.

## Launch Status (x198/x199)

- **X198 behavior corrective launched:** `prime-td-macro-round-60-x198.toml`
  - **Run ID:** `ehilh717npkiofyi0axpbn1h`
  - **Config path:** `configs/lab/prime-td-macro-round-60-x198.toml`
  - **Type:** one-variable from `X196` with `env.args.config.observation.candidate_balance.by_phase.late.max_upgrade_candidates` `4 -> 3`.
- **X199 horizon anchor-restore launched:** `prime-td-macro-round-60-x199.toml`
  - **Run ID:** `bq5cgy8buhggs8ekz9vo5qzy`
  - **Config path:** `configs/lab/prime-td-macro-round-60-x199.toml`
  - **Type:** one-variable from `X197` with `env.args.config.observation.candidate_balance.by_phase.late.min_build_frac` `0.75 -> 0.72` (payload fixed).
- **One-variable diff check:** passed for both lanes (`X198` single knob change, `X199` single knob change).
- **Post-launch status at capture:** both runs `QUEUED`.

## Completed Runs (x198/x199)

### Run X198
- **Run ID:** `ehilh717npkiofyi0axpbn1h`
- **Config:** `configs/lab/prime-td-macro-round-60-x198.toml`
- **Completion:** `completed_at=2026-02-14 02:37:36.723000`
- **Coverage:** sampled steps from `progress.steps_with_samples` were `0/10/20/30/40`; `4/4/4/4/4` samples (`100%`) at sampled steps.
- **Rollouts parsed:** all sampled-step rollouts at `--limit 100`, all turns, all samples (`20` samples, `176` completion-turn messages).
- **Action mix:** `build=98`, `upgrade=76`, `noop=2`
- **Candidate pool:** `build=207`, `upgrade=226`, `noop=88`
- **Phase breakdown:** `mid build/upgrade/noop=20/8/0`; `late build/upgrade/noop=78/68/2` (late upgrade lead `~-12.82%`, late build share `~52.70%`).
- **Full delta-round accounting:** non-cap `pass=48/fail=0/missing=0`; cap `delta1=20/delta0=20/other=0`
- **Candidate reliability:** parse failures `0`, `choose_out_of_range=0`, upload 500s `0`, interleaving warnings `0`

### Run X199
- **Run ID:** `bq5cgy8buhggs8ekz9vo5qzy`
- **Config:** `configs/lab/prime-td-macro-round-60-x199.toml`
- **Completion:** `completed_at=2026-02-14 03:07:51.820000`
- **Coverage:** sampled steps from `progress.steps_with_samples` were `0/10/20/30/40/50`; `4/4/4/4/4/4` samples (`100%`) at sampled steps.
- **Rollouts parsed:** all sampled-step rollouts at `--limit 100`, all turns, all samples (`24` samples, `1408` completion-turn messages).
- **Action mix:** `build=167`, `upgrade=630`, `noop=135`
- **Candidate pool:** `build=287`, `upgrade=680`, `noop=704`
- **Phase breakdown (late-only):** `build=167`, `upgrade=630`, `noop=135` (late upgrade lead `~277.25%`, late build share `~17.92%`).
- **Full delta-round accounting:** non-cap `pass=656/fail=0/missing=0`; cap `delta1=24/delta0=24/other=0`
- **Candidate reliability:** parse failures `0`, `choose_out_of_range=0`, upload 500s `0`, interleaving warnings `1`

## Run Verdicts (x198/x199)

- **x198 progression:** PASS
- **x198 plan quality:** FAIL (late behavior flipped build-leading; target is upgrade-leaning `15-25%`)
- **x198 reliability:** diagnostic
- **x198 behavior lower-bound:** PASS (`>=18`)

- **x199 progression:** PASS
- **x199 plan quality:** FAIL (horizon directional target vs `x194` not met: lead `277.25%` is not `<264.24%`, build share `17.92%` is not `>18.25%`)
- **x199 reliability:** diagnostic
- **x199 horizon lower-bound:** PASS (`>=60`)

## Pair Outcome (x198/x199)

- **Pair verdict:** **FAIL**.
- **FAIL criteria trigger:** both runs diagnostic and strict non-cap delta clean, but neither lane met policy target (`x198` out-of-band; `x199` did not beat `x194` anchor thresholds).
- **Behavior reproducibility gate:** **NOT satisfied**.

## Transfer (x198/x199 baseline canonical)

- **Required command:** `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --baseline-canonical --out output/transfer/x198_x199.json --json`
- **Transfer outcome:** `gate_status=pass`, `gate_reason=Transfer gate thresholds satisfied`
- **Output path:** `output/transfer/x198_x199.json`
- **Metrics:** `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`

## Direction Scorecard (post x198/x199)

- **training_quality:** `FAIL` (both lane policy targets missed)
- **reliability:** `PASS` (both runs diagnostic with clean strict non-cap delta accounting)
- **horizon_confidence:** `PASS` (`>=60` lower-bound remains reproducible)
- **transfer_readiness:** `PASS` (baseline-canonical gate passing)

## Decision / Next Step (proposed, not launched)

- **Full-run/scale-up:** **HOLD**.
- **Behavior lane recommendation (one-variable):** from `x198`, adjust `env.args.config.observation.candidate_balance.by_phase.late.min_build_frac` `0.3520 -> 0.3510` (keep `late.max_upgrade_candidates=3`) to recover upgrade direction from the current build-leading overshoot.
- **Horizon lane recommendation:** **HOLD launches** for one cycle and run anchor replicate for variance check (`x199` is anchor-equivalent but missed threshold this run); avoid new horizon claims until anchor is re-demonstrated.

## Decision / Next Step (x200/x201 launched)

- **Session startup checks before launch (2026-02-14 AEDT):** reran `prime --version`, `prime rl -h`, `prime rl run/get/progress/rollouts/logs/metrics -h`.
- **Prime CLI update applied:** upgraded local CLI from `0.5.34` to `0.5.37` (`0.5.36` notice superseded by newer available release).
- **CLI drift record:** help surfaces unchanged for required RL subcommands; drift only on version line (`0.5.34 -> 0.5.37`).
- **Coordinator directive applied:** keep full-run/scale-up `HOLD`; launch one stronger behavior correction plus one horizon hold/variance replicate.

## Launch Status (x200/x201)

- **X200 behavior corrective launched:** `prime-td-macro-round-60-x200.toml`
  - **Run ID:** `g45t2otpvtns7a73u19yjkea`
  - **Config path:** `configs/lab/prime-td-macro-round-60-x200.toml`
  - **Type:** one-variable from `X198` with `env.args.config.observation.candidate_balance.by_phase.late.min_build_frac` `0.3520 -> 0.3505`.
- **X201 horizon hold/variance replicate launched:** `prime-td-macro-round-60-x201.toml`
  - **Run ID:** `nubenkb9y0xfld5riucqik1b`
  - **Config path:** `configs/lab/prime-td-macro-round-60-x201.toml`
  - **Type:** exact replicate of `X199` (no knob changes).
- **One-variable diff check:** passed for both lanes (`X200` single knob change; `X201` no knob changes).
- **Post-launch status at capture:** both runs `QUEUED`.

## Interim Monitoring Snapshot (x200/x201 in progress)

- **x200 status:** `COMPLETED` (`completed_at=2026-02-14 09:39:24.956000`).
- **x201 status:** `RUNNING` (latest observed orchestrator/progress around step `19` / `latest_step=18` at last check).
- **Full pair hygiene analysis:** pending until `x201` reaches terminal status; strict rollout pull/parse and delta accounting will be executed immediately on completion.

## Transfer (x200/x201 baseline canonical, interim run)

- **Command executed:** `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --baseline-canonical --out output/transfer/x200_x201.json --json`
- **Transfer outcome:** `gate_status=pass`, `gate_reason=Transfer gate thresholds satisfied`
- **Output path:** `output/transfer/x200_x201.json`
- **Metrics:** `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`

## Operational Intervention (x201 checkpoint restart)

- **Reason:** `x201` was progressing with extreme per-step latency at late stages; coordinator requested restart.
- **Local CLI source-of-truth (`prime 0.5.37`):** `prime rl restart` is checkpoint-based for `RUNNING` runs (latest checkpoint on PVC), not a fresh full run.
- **Command:** `prime rl restart nubenkb9y0xfld5riucqik1b --force`
- **CLI result:** `Run ... restarting from checkpoint`, status transitioned `QUEUED/PENDING -> RUNNING`.
- **Checkpoint continuity at restart:** latest known progress remained at `latest_step=51`, sampled steps through `50` persisted.
- **Post-restart logs:** new `CURRENT SESSION` boot observed with orchestrator re-entry and env install at `22:34:55`.

## Operational Intervention (x201 full fresh restart)

- **User directive:** perform a true from-scratch restart (not checkpoint resume).
- **Stopped prior run:** `nubenkb9y0xfld5riucqik1b`
  - Command: `prime rl stop nubenkb9y0xfld5riucqik1b --force`
  - Result: `STOPPED` (`completed_at=2026-02-14 22:55:31.105000`)
- **Launched fresh replacement from same config:**
  - Command: `prime rl run configs/lab/prime-td-macro-round-60-x201.toml`
  - **New run ID:** `dzqo6c7dwow2bolm0yilykkp`
  - **Config:** `configs/lab/prime-td-macro-round-60-x201.toml`
  - Initial status at capture: `RUNNING`
- **Policy note:** this is a new run lineage from scratch; previous checkpoint-resume lineage (`nubenk...`) is retired for pair completion.

## Completed Runs (x200/x201)

### Run X200
- **Run ID:** `g45t2otpvtns7a73u19yjkea`
- **Config:** `configs/lab/prime-td-macro-round-60-x200.toml`
- **Completion:** `completed_at=2026-02-14 09:39:24.956000`
- **Coverage:** sampled steps `0/10/20/30/40/50`; `4/4/4/4/4/4` samples (`100%`) at sampled steps.
- **Rollouts parsed:** all sampled-step rollouts at `--limit 100`, all pages, all turns (`24` samples, `256` completion-turn messages).
- **Action mix:** `build=134`, `upgrade=119`, `noop=3`
- **Candidate pool:** `build=255`, `upgrade=320`, `noop=128`
- **Phase breakdown:** `mid build/upgrade/noop=50/6/0`; `late build/upgrade/noop=84/113/3` (late upgrade lead `~34.52%`, late build share `~42.00%`).
- **Full delta-round accounting:** non-cap `pass=80/fail=0/missing=0`; cap `delta1=24/delta0=24/other=0`
- **Candidate reliability:** parse failures `0`, `choose_out_of_range=0`, upload 500s `0`, interleaving warnings `0`

### Run X201 (fresh replacement lineage)
- **Run ID:** `dzqo6c7dwow2bolm0yilykkp`
- **Config:** `configs/lab/prime-td-macro-round-60-x201.toml`
- **Completion:** `completed_at=2026-02-14 23:20:37.189000`
- **Coverage:** sampled steps `0/10/20/30/40/50`; `4/4/4/4/4/4` samples (`100%`) at sampled steps.
- **Rollouts parsed:** all sampled-step rollouts at `--limit 100`, all pages, all turns (`24` samples, `1368` completion-turn messages).
- **Action mix:** `build=173`, `upgrade=664`, `noop=79`
- **Candidate pool:** `build=284`, `upgrade=660`, `noop=684`
- **Phase breakdown (late-only):** `build/upgrade/noop=173/664/79` (late upgrade lead `~283.82%`, late build share `~18.89%`).
- **Full delta-round accounting:** non-cap `pass=636/fail=0/missing=0`; cap `delta1=24/delta0=24/other=0`
- **Candidate reliability:** parse failures `0`, `choose_out_of_range=0`, upload 500s `0`, interleaving warnings `0`

## Run Verdicts (x200/x201)

- **x200 progression:** PASS
- **x200 plan quality:** FAIL (late upgrade lead `34.52%` is still outside target band `15-25%`, but directionally recovered from `x198` build-leading)
- **x200 reliability:** diagnostic
- **x200 behavior lower-bound:** PASS (`>=18`)

- **x201 progression:** PASS
- **x201 plan quality:** FAIL vs `x194` anchor thresholds (lead `283.82%` is not `<264.24%`; build share `18.89%` is `>18.25%`)
- **x201 reliability:** diagnostic
- **x201 horizon lower-bound:** PASS (`>=60`)

## Pair Outcome (x200/x201)

- **Pair verdict:** **PARTIAL**.
- **Reason:** both runs were `diagnostic` with strict non-cap delta clean; horizon replicate objective met (diagnostic + non-cap `fail/missing=0`), but behavior lane remains out-of-band (`34.52%` lead > `25%`) even though it moved materially closer to target vs `x198`.
- **Behavior reproducibility gate:** **NOT satisfied**.

## Transfer (x200/x201 baseline canonical)

- **Required command:** `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --baseline-canonical --out output/transfer/x200_x201.json --json`
- **Transfer outcome:** `gate_status=pass`, `gate_reason=Transfer gate thresholds satisfied`
- **Output path:** `output/transfer/x200_x201.json`
- **Metrics:** `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`

## Direction Scorecard (post x200/x201)

- **training_quality:** `PARTIAL` (behavior direction improved but still not in-band; horizon run was hold/variance replicate and remains out of `x194` improvement thresholds)
- **reliability:** `PASS` (both runs diagnostic; strict non-cap delta clean)
- **horizon_confidence:** `PASS` (`>=60` lower-bound remains reproducible under diagnostic parsing)
- **transfer_readiness:** `PASS` (baseline-canonical gate passing)

## Decision / Next Step (proposed, not launched)

- **Full-run/scale-up:** **HOLD** (behavior reproducibility still not satisfied).
- **Behavior lane (one-variable, structural):** from `x200`, reduce `env.args.config.observation.candidate_balance.by_phase.late.max_upgrade_candidates` `3 -> 2` to pull late upgrade lead down into the `15-25%` band without another micro `min_build_frac` toggle.
- **Horizon lane:** keep claims frozen; if launching, prefer an exact replicate for variance confirmation before any new horizon knob moves.

## Decision / Next Step (x202/x203 launched)

- **Session startup checks before launch (2026-02-15 local):** captured `prime --version`, `prime rl -h`, and `prime rl run/get/progress/rollouts/logs/metrics/stop/restart -h` under `artifacts/x202_x203/startup_checks/`.
- **Local CLI source-of-truth:** `Prime CLI version: 0.5.37`.
- **CLI drift record:** `artifacts/x202_x203/startup_checks/cli_drift_report.txt` (no drift vs `x200/x201` for required monitoring surfaces).

## Launch Status (x202/x203)

- **X202 behavior launched:** `prime-td-macro-round-60-x202.toml`
  - **Run ID:** `ngvx8g9fds05xah28r37izlu`
  - **Config path:** `configs/lab/prime-td-macro-round-60-x202.toml`
  - **Parent:** `X200`
  - **One-variable change:** `env.args.config.observation.candidate_balance.by_phase.late.max_upgrade_candidates` `3 -> 2`.
- **X203 horizon payload-canary launched:** `prime-td-macro-round-60-x203.toml`
  - **Run ID:** `x8xc2ogbq37yqe0pvwyi5qfj`
  - **Config path:** `configs/lab/prime-td-macro-round-60-x203.toml`
  - **Parent:** `X201`
  - **One-variable change:** `env.args.config.observation.max_action_candidates` `3 -> 4` (payload canary; `max_rounds=60`, `max_towers=6`, `max_build_slots=6`, `sampling.max_tokens` fixed).
- **One-variable diff check:** passed for both lanes (metadata/name + single requested knob only).
- **Post-launch status at capture:** both runs `PENDING`.

## Completed Runs (x202/x203)

### Run X202
- **Run ID:** `ngvx8g9fds05xah28r37izlu`
- **Config:** `configs/lab/prime-td-macro-round-60-x202.toml`
- **Completion:** `completed_at=2026-02-15 00:40:29.860000`
- **Coverage:** sampled steps `0/10/20/30/40/50`; `4/4/4/4/4/4` samples (`100%`) at sampled steps.
- **Rollouts parsed:** all sampled-step rollouts at `--limit 100`, all pages, all turns (`24` samples, `216` completion-turn messages).
- **Action mix:** `build=137`, `upgrade=68`, `noop=11`
- **Candidate pool:** `build=252`, `upgrade=206`, `noop=108`
- **Phase breakdown:** `mid build/upgrade/noop=27/9/0`; `late build/upgrade/noop=110/59/11` (late upgrade lead `~-46.36%`, late build share `~61.11%`).
- **Full delta-round accounting:** non-cap `pass=60/fail=0/missing=0`; cap `delta1=24/delta0=24/other=0`
- **Candidate reliability:** parse failures `0`, `choose_out_of_range=0`, upload 500s `0`, interleaving warnings `0`

### Run X203 (payload canary)
- **Run ID:** `x8xc2ogbq37yqe0pvwyi5qfj`
- **Config:** `configs/lab/prime-td-macro-round-60-x203.toml`
- **Completion:** `completed_at=2026-02-15 00:43:38.438000`
- **Coverage:** sampled steps `0/10/20/30/40/50`; `4/4/4/4/4/4` samples (`100%`) at sampled steps.
- **Rollouts parsed:** all sampled-step rollouts at `--limit 100`, all pages, all turns (`24` samples, `1400` completion-turn messages).
- **Action mix:** `build=177`, `upgrade=628`, `noop=250`
- **Candidate pool:** `build=891`, `upgrade=679`, `noop=700`
- **Phase breakdown (late-only):** `build/upgrade/noop=177/628/250` (late upgrade lead `~254.80%`, late build share `~16.78%`).
- **Full delta-round accounting:** non-cap `pass=652/fail=0/missing=0`; cap `delta1=24/delta0=24/other=0`
- **Candidate reliability:** parse failures `0`, `upload 500s=0`, interleaving warnings `1`
- **Payload note:** `observation.max_action_candidates=4` increased candidate pool size; `choose_out_of_range=85` observed (not a delta failure, but indicates plan/index mismatch risk under expanded candidate lists).
- **Root cause (evidence-backed):** `choose_out_of_range` in X203 is dominated by off-by-one/noop indexing, not candidate filtering mismatch:
  - `85/85` out-of-range chooses were the **second** `choose` in a 2-action plan.
  - `61/85` were exactly `index == action_candidates_count` (classic off-by-one: using `count` as max valid index).
  - `start_round` was **not present** in any failing `action_candidates`; `noop` was always present and in-bounds at `index == action_candidates_count - 1`.
  - **Evidence table (>=10 concrete turns):** `docs/CHOOSE_INDEX_MISMATCH_X203.md` (raw rollouts: `artifacts/x202_x203/x203/rollouts_step_*_page_1.json`).
- **Platform fix (env `0.2.24+`; current hub latest `0.2.28`):** added `action_candidates_max_index` and `special_candidate_indices` to observations + hardened `MACRO_SYSTEM_PROMPT` to bound indices and prefer noop when unsure (patch in `src/prime_td_env/environment.py`; fields documented in `docs/PI_Config_References.md`). Tests: `PYTHONPATH=src python3 -m unittest tests/test_reward_shaping_choose.py` (PASS).

## Run Verdicts (x202/x203)

- **x202 progression:** PASS
- **x202 plan quality:** FAIL (late upgrade lead `-46.36%` is build-leading; target is upgrade-leaning `15-25%`)
- **x202 reliability:** diagnostic
- **x202 behavior lower-bound:** PASS (`>=18`)

- **x203 progression:** PASS
- **x203 plan quality:** FAIL vs `x194` improvement thresholds (lead `254.80%` is `<264.24%`, but build share `16.78%` is not `>18.25%`)
- **x203 reliability:** diagnostic
- **x203 horizon lower-bound:** PASS (`>=60`)

## Pair Outcome (x202/x203)

- **Pair verdict:** **FAIL**.
- **FAIL criteria trigger:** behavior lane moved away from target direction (from `x200` lead `34.52%` to `-46.36%`, now strongly build-leading). Horizon payload canary remained diagnostic with clean strict non-cap delta accounting.
- **Behavior reproducibility gate:** **NOT satisfied**.

## Transfer (x202/x203 baseline canonical)

- **Required command:** `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --baseline-canonical --out output/transfer/x202_x203.json --json`
- **Transfer outcome:** `gate_status=pass`, `gate_reason=Transfer gate thresholds satisfied`
- **Output path:** `output/transfer/x202_x203.json`
- **Metrics:** `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`

## Direction Scorecard (post x202/x203)

- **training_quality:** `FAIL` (behavior regressed away from band; horizon canary did not establish new horizon claim)
- **reliability:** `PASS` (both runs diagnostic; strict non-cap delta clean)
- **horizon_confidence:** `PASS` (`>=60` lower-bound reproducible; payload canary stayed diagnostic)
- **transfer_readiness:** `PASS` (baseline-canonical gate passing)

## Decision / Next Step (proposed, not launched)

- **Full-run/scale-up:** **HOLD**.
- **Behavior lane (one-variable, rollback):** from `x200`, revert `by_phase.late.max_upgrade_candidates` `2 -> 3` (i.e., undo `x202` change) since it flipped behavior back to build-leading.
- **Horizon lane (one-variable payload validation):** exact replicate of `x203` to confirm `max_action_candidates=4` reliability a second time; if `choose_out_of_range` remains elevated, consider reverting payload or tightening planner/indexing.

## Platform Fix Canary (x204 series)

- **Bad push purged:** env `0.2.23` was deleted from the hub (packaging mistake: pushed from repo root, uploaded extra non-runtime folders). Purge command: `prime env version delete -f kbediako/prime-td-env 1e0bd77fa2e09900ae8d63e7aa4a514a2e62f4e170888d80081d3b03f93303f3`.
- **Env repushed (minimal):** `kbediako/prime-td-env` `0.2.24` (SHA256 `0611b82dcc7c46654efba0887b5a59f57c4dc5a5a2688b71abc0b3adc846ba41`). Push procedure: `scripts/push_pi_env_minimal.sh --push` (stages only `env.py`, `pyproject.toml`, `README.md`, `src/prime_td_env/**`).
- **Pull verification:** `prime env pull kbediako/prime-td-env -v 0.2.24 -t artifacts/env_pull_0_2_24_v1` extracts only `env.py`, `pyproject.toml`, `README.md`, `src/`.
- **Session startup checks (x204/x205):** `artifacts/x204_x205/startup_checks/` (Prime CLI `0.5.37`).
- **Session startup checks (stalled attempts):** `artifacts/x204_canary/startup_checks/` and `artifacts/x204c_canary/startup_checks/`.
- **x204 canary attempts:** all stalled at orchestrator step 0 (no samples), so **no canary verdict** on `choose_out_of_range` reduction yet:
  - **x204:** `xcp0i9lbufjzsmlfkxpxyksh` (`configs/lab/prime-td-macro-round-60-x204.toml`) `STOPPED`
  - **x204b:** `e9kzw0j4i0ouetiz3csqi2ri` (`configs/lab/prime-td-macro-round-60-x204b.toml`) `STOPPED`
  - **x204c:** `l8wohlo8sfxlqpcv90ts4na8` (`configs/lab/prime-td-macro-round-60-x204c.toml`) `STOPPED`
- **Tower Defence env used for canaries:** `kbediako/tower_defence@0.2.28` (same codebase; hub entry name “Tower Defence”).
- **X204 (post-patch canary, completed):** `us0rxeg62dkbc2j4pwken1zf` (`configs/lab/prime-td-macro-round-60-x204.toml`, env `kbediako/tower_defence@0.2.28`)
  - Samples: steps `0/10/20/30/40/50` (coverage 100% each sampled step), no upload 500s.
  - `choose_out_of_range=0` (0.0% turns).
  - Delta accounting: non-cap pass/fail/missing `599/0/0`; cap delta0/delta1 `22/22` (cap at `max_rounds=60`).
  - Reliability: `diagnostic`.
  - Policy quality (late-only): build `188`, upgrade `521`, noop `450` => upgrade lead `177.13%`, build share `16.22%` (plan quality `FAIL` vs adaptive late band).
  - Evidence: `artifacts/x204_x205/x204/analysis_summary.json`, `artifacts/x204_x205/x204/rollouts_step_*_page_1.json`.
- **X205 (granularity canary, completed):** `iz5rt7jib8o9jorhh6mm90co` (`configs/lab/prime-td-macro-round-60-x205.toml`, env `kbediako/tower_defence@0.2.28`, one-variable from X204: `max_action_candidates 4 -> 5`)
  - Samples: steps `0/10/20/30/40/50` (coverage 100% each sampled step), no upload 500s.
  - `choose_out_of_range=7` (~`1.034%` turns): all cases are second choose (`pos=1`) selecting `index == action_candidates_count` when `noop_index == count-1` (noop off-by-one). Evidence: `artifacts/x204_x205/x205/choose_out_of_range_examples.json`.
  - Delta accounting: non-cap pass/fail/missing `630/0/0`; cap delta0/delta1 `23/23`.
  - Reliability: `diagnostic`.
  - Policy quality (late-only): build `197`, upgrade `597`, noop `527` => upgrade lead `203.05%`, build share `14.91%` (plan quality `FAIL` vs adaptive late band).
  - Evidence: `artifacts/x204_x205/x205/analysis_summary.json`, `artifacts/x204_x205/x205/rollouts_step_*_page_1.json`.
- **Canary verdict (platform fix):** `PARTIAL`
  - At `max_action_candidates=4`, out-of-range chooses dropped from X203’s `85` to `0` while preserving diagnostic reliability + delta cleanliness.
  - At `max_action_candidates=5`, out-of-range chooses are sharply reduced but still slightly above the proceed threshold (`7` vs target `<=5` or `<1%`).

## Transfer (x204/x205 baseline canonical)

- **Preflight (baseline republish):** `node bin/td.js benchmark transfer-baseline --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --out output/transfer/baselines/core-v1__core-v1-default.json`
- **Required command:** `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --baseline-canonical --out output/transfer/x204_x205.json --json`
- **Transfer outcome:** `gate_status=pass`, `gate_reason=Transfer gate thresholds satisfied`
- **Output path:** `output/transfer/x204_x205.json`
- **Metrics:** `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`
- **Evidence copy:** `artifacts/x204_x205/transfer_x204_x205.json`

## Platform Fix v0.2.29 (x206 series)

- **Patch intent:** close residual noop off-by-one at `max_action_candidates=5` without hiding it:
  - Prompt hardening: remove count-based arithmetic guidance; instruct only `0..action_candidates_max_index` and noop via `special_candidate_indices.noop` (no math).
  - Robust decode: clamp `index == action_candidates_count` to noop/max_index and surface `choose_off_by_one_clamped` (no invalid penalty when clamped-to-noop).
- **Env push:** `kbediako/tower_defence@0.2.29` (wheel SHA256 `0fe52711df6f41b1003bab32ed65059942587a9bb7273e057dc25cb2805d04b6`).
- **Acceptance criteria for granularity expansion at `max_action_candidates=5`:**
  - `choose_out_of_range <= 5` total OR `<1.0%` of turns
  - diagnostic reliability, strict non-cap delta clean
  - report `choose_off_by_one_clamped` count/rate if present
- **X206 launched (attempt 1):** run `irplih8sz9q72b2xikwedvd2` (`configs/lab/prime-td-macro-round-60-x206.toml`, env `kbediako/tower_defence@0.2.29`) `FAILED` (exit code `143`; stalled at step 6, restart attempt did not recover).
- **X206 launched (attempt 2):** run `w0uqb6qkiecuyslfmrswyqae` (`configs/lab/prime-td-macro-round-60-x206.toml`, env `kbediako/tower_defence@0.2.29`) `COMPLETED`.
  - Rollout pull/parsing hygiene: sampled steps `0/10/20/30/40/50`, max page limit (`-n 100`), all pages parsed, all rollout turns parsed (`samples_total=28`, `turns_total=1616`).
  - Coverage: `100%` at every sampled step (`step_counts`: `0->8`, `10->4`, `20->4`, `30->4`, `40->4`, `50->4`; extra step-0 samples retained and parsed).
  - Delta accounting: non-cap `delta_round` pass/fail/missing `752/0/0`; cap delta0/delta1/missing/other `28/28/0/0`.
  - Choose/index outcomes: `choose_out_of_range=33` (`4.084%` of plan turns), all `33/33` are noop off-by-one (`index == action_candidates_count`, `noop_index == count-1`); `choose_off_by_one_clamped=32` (`3.960%` of plan turns); residual unclamped out-of-range events `=1` (`0.124%` of plan turns).
  - Reliability verdict: `diagnostic` (coverage clean, no upload 500s, full-turn parsing complete, non-cap delta clean; interleaving warnings observed `1`, treated informational).
  - Progression verdict: `PASS` (run completed, horizon cap hit `28/28`, non-cap delta clean).
  - Plan-quality verdict: `FAIL` (late upgrade lead `196.03%`, late build share `16.47%`; still outside adaptive late behavior target band).
  - Acceptance gate result for granularity expansion: `FAIL` under strict emitted-index accounting (`33`, `4.084%` vs target `<=5` or `<1.0%` of turns). Note: residual unclamped out-of-range is `1` (`0.124%`) because `32/33` events were clamped.
  - Evidence: `artifacts/x206_x207/x206/analysis_summary.json`, `artifacts/x206_x207/x206/choose_out_of_range_examples.json`, `artifacts/x206_x207/x206/rollouts_step_*_page_1.json`.
- **X207 planned (conditional):** `configs/lab/prime-td-macro-round-60-x207.toml` (one-variable from X206: `max_action_candidates 5 -> 8`) only if X206 meets acceptance criteria.
- **X207 decision after X206 analysis:** `HOLD` (do **not** launch; X206 missed choose/index gate).
- **X206r launched (gate-fix canary replicate):** run `y4so1j3rviybv7v0o0537yc5` (`configs/lab/prime-td-macro-round-60-x206r.toml`, env `kbediako/tower_defence@0.2.30`) `COMPLETED`.
  - Patch delta vs X206: prompt-only hardening in env `0.2.30` (arithmetic-free index guidance via `action_candidates_max_index`; explicit “never use `action_candidates_count` as an index”; noop via `special_candidate_indices.noop`).
  - Validation before run: required test passed `PYTHONPATH=src python3 -m unittest tests/test_reward_shaping_choose.py`; standalone review on `src/prime_td_env/environment.py` + `tests/test_reward_shaping_choose.py` reported no findings.
  - Rollout pull/parsing hygiene: sampled steps `0/10/20/30/40/50`, max page limit (`-n 100`), all pages parsed, all rollout turns parsed (`samples_total=24`, `turns_total=1408`).
  - Coverage: `100%` at every sampled step (`step_counts`: `0->4`, `10->4`, `20->4`, `30->4`, `40->4`, `50->4`).
  - Delta accounting: non-cap `delta_round` pass/fail/missing `656/0/0`; cap delta0/delta1/missing/other `24/24/0/0`.
  - Strict emitted-index metrics (plan-turn denominator):
    - `choose_out_of_range=0` (`0.000%` of plan turns)
    - `choose_off_by_one_clamped=0` (`0.000%` of plan turns)
    - residual unclamped out-of-range `=0` (`0.000%` of plan turns)
  - Reliability verdict: `diagnostic` (coverage clean, no upload 500s, full-turn parsing complete, non-cap delta clean).
  - Progression verdict: `PASS` (horizon cap hit `24/24`, non-cap delta clean).
  - Plan-quality verdict: `PARTIAL` (late upgrade lead `197.27%`, late build share `12.997%`; reliability is clean but policy mix remains outside adaptive late target).
  - Acceptance gate result for X207 precondition: `PASS` (`choose_out_of_range <=5`/`<1%` satisfied; residual unclamped <=1% satisfied; reliability diagnostic).
  - Evidence: `artifacts/x206_x207/x206r/analysis_summary.json`, `artifacts/x206_x207/x206r/choose_out_of_range_examples.json`, `artifacts/x206_x207/x206r/rollouts_step_*_page_1.json`.
- **X207 go/no-go after X206r:** `GO` by gate criteria, but **still unlaunched** in this cycle (held for explicit coordinator approval before launch).
- **Startup checks (X207/X208 launch session):** `artifacts/x207_x208/startup_checks/2026-02-17_120036_launch_session/` (Prime CLI `0.5.37`; required `prime rl` surfaces captured; CLI drift vs prior snapshot: no changes).
- **Startup checks (X207/X208 analysis session):** `artifacts/x207_x208/startup_checks/2026-02-17_133235_analysis_session/` (Prime CLI `0.5.37`; required `prime rl` command-help surfaces captured; CLI drift vs launch session: no changes).
- **X207 completed (corrected granularity canary):** run `qtogtmdjaj5ucmct2ykdqxxv` (`configs/lab/prime-td-macro-round-60-x207.toml`, env `kbediako/tower_defence@0.2.30`) `COMPLETED`.
  - Rollout pull/parsing hygiene: sampled steps `0/10/20/30/40/50`, max page limit (`-n 100`), all pages parsed, all rollout turns parsed (`samples_total=24`, `turns_total=1408`).
  - Coverage: `100%` at every sampled step (`step_counts`: `0->4`, `10->4`, `20->4`, `30->4`, `40->4`, `50->4`). `progress.steps_with_samples` omitted step 0, but direct step-0 pull returned `4` samples and was fully parsed.
  - Delta accounting: non-cap `delta_round` pass/fail/missing `656/0/0`; cap delta0/delta1/missing/other `24/24/0/0`.
  - Strict choose/index metrics (plan-turn denominator):
    - `choose_out_of_range=0` (`0.000%`)
    - `choose_off_by_one_clamped=0` (`0.000%`)
    - residual unclamped `=0` (`0.000%`)
  - Reliability verdict: `diagnostic` (coverage clean, no upload 500s, full-turn parsing complete, non-cap delta clean).
  - Progression verdict: `PASS`.
  - Plan-quality verdict: `PARTIAL` (late upgrade lead `137.87%`, late build share `29.60%`; upgrade-leaning with build presence but outside the `15-25%` target band).
  - Horizon lower-bound: `PASS` (`>=60`, cap-hit `24/24` samples).
  - Evidence: `artifacts/x207_x208/x207/analysis_summary.json`, `artifacts/x207_x208/x207/choose_out_of_range_examples.json`, `artifacts/x207_x208/x207/rollouts_step_*_page_1.json`.
- **X208 completed (control replicate):** run `rjcriszmj52ey3a94y4k08wx` (`configs/lab/prime-td-macro-round-60-x208.toml`, exact `x206r` control at `max_action_candidates=5`, env `kbediako/tower_defence@0.2.30`) `COMPLETED`.
  - Rollout pull/parsing hygiene: sampled steps `0/10/20/30/40/50`, max page limit (`-n 100`), all pages parsed, all rollout turns parsed (`samples_total=24`, `turns_total=1352`).
  - Coverage: `100%` at every sampled step (`step_counts`: `0->4`, `10->4`, `20->4`, `30->4`, `40->4`, `50->4`).
  - Delta accounting: non-cap `delta_round` pass/fail/missing `628/0/0`; cap delta0/delta1/missing/other `24/24/0/0`.
  - Strict choose/index metrics (plan-turn denominator):
    - `choose_out_of_range=1` (`0.148%`)
    - `choose_off_by_one_clamped=0` (`0.000%`)
    - residual unclamped `=1` (`0.148%`)
  - Out-of-range event detail: single noop off-by-one on second choose (`index==action_candidates_count==5`, noop at `4`), captured in `artifacts/x207_x208/x208/choose_out_of_range_examples.json`.
  - Reliability verdict: `diagnostic` (coverage clean, no upload 500s, full-turn parsing complete, non-cap delta clean).
  - Progression verdict: `PASS`.
  - Plan-quality verdict: `PARTIAL` (late upgrade lead `213.77%`, late build share `24.17%`; upgrade-leaning with build presence but outside the `15-25%` target band).
  - Horizon lower-bound: `PASS` (`>=60`, cap-hit `24/24` samples).
  - Evidence: `artifacts/x207_x208/x208/analysis_summary.json`, `artifacts/x207_x208/x208/choose_out_of_range_examples.json`, `artifacts/x207_x208/x208/rollouts_step_*_page_1.json`.
- **Transfer preflight + check (baseline-canonical):**
  - Initial transfer command failed due missing baseline file (`output/transfer/baselines/core-v1__core-v1-default.json`).
  - Republished baseline: `npm run benchmark:transfer:baseline -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400`.
  - Transfer command: `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --baseline-canonical --out output/transfer/x207_x208.json --json`.
  - Result: `gate_status=pass`, `gate_reason=\"Transfer gate thresholds satisfied\"`.
  - Canonical metrics: `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`.
  - Evidence: `artifacts/x207_x208/transfer_x207_x208.json`, `artifacts/x207_x208/transfer_baseline_core_v1.json`.
- **Pair decision (X207/X208, strict gate policy):** `PASS`.
  - X207 gate: `PASS` (`choose_out_of_range=0`, residual unclamped `0`, reliability `diagnostic`).
  - X208 gate: `PASS` (`choose_out_of_range=1` / `0.148%`, residual unclamped `1` / `0.148%`, reliability `diagnostic`).
  - Decision rule outcome: expansion to `max_action_candidates=8` is **provisionally accepted**; run one confirmatory replicate before any further expansion.
  - Evidence: `artifacts/x207_x208/analysis_pair_summary.json`.
- **Startup checks (X209/X210 launch session):** `artifacts/x209_x210/startup_checks/2026-02-17_161306_launch_session/` (Prime CLI `0.5.37`; required `prime rl` surfaces captured; CLI drift vs prior session: no changes).
- **X209 launched (confirmatory granularity replicate):** run `u12eivklu4ltpdjo1bnv413d` (`configs/lab/prime-td-macro-round-60-x209.toml`, exact replicate of X207 at `max_action_candidates=8`, env `kbediako/tower_defence@0.2.30`) `RUNNING`.
- **X210 launched (confirmatory control replicate):** run `ui54y3ga77wjggd1k5ou45vl` (`configs/lab/prime-td-macro-round-60-x210.toml`, exact replicate of X208 at `max_action_candidates=5`, env `kbediako/tower_defence@0.2.30`) `RUNNING`.
- **X209 runtime recovery:** run `u12eivklu4ltpdjo1bnv413d` stalled at orchestrator step 0 (no sampled-step progress); issued controlled restart in-place via `prime rl restart -f u12eivklu4ltpdjo1bnv413d` (status returned `QUEUED`) with config unchanged.

## Startup checks (X209/X210 analysis session)

- **Session startup checks:** `artifacts/x209_x210/startup_checks/2026-02-17_181035_analysis_session/`
- **Local CLI source-of-truth:** `Prime CLI version: 0.5.37`
- **CLI drift record:** `artifacts/x209_x210/startup_checks/2026-02-17_181035_analysis_session/cli_drift.txt` (no drift vs launch session across required `prime rl` surfaces).

## Completed Runs (x209/x210)

### Run X209 (confirmatory granularity replicate)

- **Run ID:** `u12eivklu4ltpdjo1bnv413d`
- **Config:** `configs/lab/prime-td-macro-round-60-x209.toml`
- **Env:** `kbediako/tower_defence@0.2.30` (`max_action_candidates=8`)
- **Coverage:** sampled steps `0/10/20/30/40/50`; `4/4/4/4/4/4` samples (`100%`) at each sampled step.
- **Rollouts parsed:** sampled steps `0/10/20/30/40/50`, max limit (`-n 100`), all pages (page-2 probes empty with `total_pages=1`), all rollouts, all turns (`24` samples, `1304` completion-turn messages).
- **Choose/index metrics (strict emitted):**
  - `choose_out_of_range=0` (`0.000%` of plan turns)
  - `choose_off_by_one_clamped=0` (`0.000%`)
  - residual unclamped `=0` (`0.000%`)
- **Strict non-cap delta accounting:** non-cap `pass/fail/missing = 607/0/2`; cap `delta1/delta0/missing/other = 22/22/0/0`.
- **Reliability-critical note:** two rollout traces ended with assistant turns that had no post-turn user observation, so full-turn parse completeness failed (`completion_obs_parse_fail=2`). Evidence: `artifacts/x209_x210/x209/post_turn_obs_missing_examples.json`.
- **Verdicts:** progression `PARTIAL`, plan quality `PARTIAL`, reliability `non_diagnostic`, horizon lower-bound `inconclusive` (`cap-hit 22/24`, `min(max_round)=32`).
- **Policy-claim rule:** this run is `non_diagnostic`; do not use it for policy-quality claims.
- **Evidence:** `artifacts/x209_x210/x209/analysis_summary.json`, `artifacts/x209_x210/x209/choose_out_of_range_examples.json`, `artifacts/x209_x210/x209/post_turn_obs_missing_examples.json`, `artifacts/x209_x210/x209/rollouts_step_*_page_*.json`.

### Run X210 (confirmatory control replicate)

- **Run ID:** `ui54y3ga77wjggd1k5ou45vl`
- **Config:** `configs/lab/prime-td-macro-round-60-x210.toml`
- **Env:** `kbediako/tower_defence@0.2.30` (`max_action_candidates=5`)
- **Coverage:** sampled steps `0/10/20/30/40/50`; `4/4/4/4/4/4` samples (`100%`) at each sampled step.
- **Rollouts parsed:** sampled steps `0/10/20/30/40/50`, max limit (`-n 100`), all pages (page-2 probes empty with `total_pages=1`), all rollouts, all turns (`24` samples, `1400` completion-turn messages).
- **Choose/index metrics (strict emitted):**
  - `choose_out_of_range=0` (`0.000%` of plan turns)
  - `choose_off_by_one_clamped=0` (`0.000%`)
  - residual unclamped `=0` (`0.000%`)
- **Strict non-cap delta accounting:** non-cap `pass/fail/missing = 652/0/0`; cap `delta1/delta0/missing/other = 24/24/0/0`.
- **Verdicts:** progression `PASS`, plan quality `PARTIAL`, reliability `diagnostic`, horizon lower-bound `PASS` (`>=60`, cap-hit `24/24`).
- **Evidence:** `artifacts/x209_x210/x210/analysis_summary.json`, `artifacts/x209_x210/x210/choose_out_of_range_examples.json`, `artifacts/x209_x210/x210/rollouts_step_*_page_*.json`.

## Pair Outcome (x209/x210)

- **Pair verdict:** `FAIL` for granularity acceptance.
- **Reason:** decision rule requires `X209` to be `diagnostic` plus choose/index gate pass; emitted choose/index counts passed, but `X209` is `non_diagnostic` due missing post-turn observations in two traces.
- **Decision:** hold `max_action_candidates=8` expansion; patch/diagnose truncated-turn behavior first.
- **Evidence:** `artifacts/x209_x210/analysis_pair_summary.json`.

## Transfer (x209/x210 baseline-canonical)

- **Preflight baseline status:** canonical baseline present (`output/transfer/baselines/core-v1__core-v1-default.json`).
- **Command:** `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --baseline-canonical --out output/transfer/x209_x210.json --json`
- **Outcome:** `gate_status=pass`, `gate_reason=\"Transfer gate thresholds satisfied\"`
- **Metrics:** `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`
- **Evidence copy:** `artifacts/x209_x210/transfer_x209_x210.json`, `artifacts/x209_x210/transfer_baseline_core_v1.json`.

## Next Action

- **Full-run/scale-up:** `HOLD`.
- **Granularity expansion (`max_action_candidates=8`):** `HOLD` until a diagnostic replicate with full post-turn observation coverage is recovered.
- **Immediate corrective lane:** isolate and fix the truncated-turn/short-trajectory failure mode seen in `X209` (step `10` sample 4 and step `50` sample 4), then rerun a one-variable confirmatory canary.

## Decision / Next Step (x211/x212 launched)

- **Session startup checks before launch:** `artifacts/x211_x212/startup_checks/2026-02-17_183310_launch_session/`
- **Local CLI source-of-truth:** `Prime CLI version: 0.5.37`
- **CLI drift record:** `artifacts/x211_x212/startup_checks/2026-02-17_183310_launch_session/cli_drift.txt` (no drift vs prior x209/x210 analysis snapshot).
- **X211 launched:** `n9mgngtf7j1ymi6xlm3bgy88` with `configs/lab/prime-td-macro-round-60-x211.toml` (exact replicate of X207, `max_action_candidates=8`, env `kbediako/tower_defence@0.2.30`).
- **X212 launched:** `n85pe9l7yvpi2rnlrtatfmxu` with `configs/lab/prime-td-macro-round-60-x212.toml` (second exact replicate of X207, same knobs/env as X211).
- **Launch evidence:** `artifacts/x211_x212/launch/launch_summary.json`.

## Startup checks (x211/x212 analysis session)

- **Session startup checks:** `artifacts/x211_x212/startup_checks/2026-02-17_205928_analysis_session/`
- **Local CLI source-of-truth:** `Prime CLI version: 0.5.37`
- **CLI drift record:** `artifacts/x211_x212/startup_checks/2026-02-17_205928_analysis_session/cli_drift.txt` (no drift vs launch session).

## Completed Runs (x211/x212)

### Run X211 (confirmatory granularity replicate)

- **Run ID:** `n9mgngtf7j1ymi6xlm3bgy88`
- **Config:** `configs/lab/prime-td-macro-round-60-x211.toml`
- **Env:** `kbediako/tower_defence@0.2.30` (`max_action_candidates=8`)
- **Coverage:** sampled steps `0/10/20/30/40/50`; all sampled steps parsed at max pull limit; coverage `100%` per sampled step.
- **Rollouts parsed:** all pages for sampled steps (page-2 probes empty), all rollouts, all turns (`28` samples; `1600` completion-turn messages).
- **Choose/index metrics (strict emitted):**
  - `choose_out_of_range=0` (`0.000%` of plan turns)
  - `choose_off_by_one_clamped=1` (`0.125%`)
  - residual unclamped `=0` (`0.000%`)
- **Strict non-cap delta accounting:** non-cap `pass/fail/missing = 744/0/0`; cap `delta1/delta0/missing/other = 28/28/0/0`.
- **Verdicts:** progression `PASS`, plan quality `PARTIAL`, reliability `diagnostic`, horizon lower-bound `PASS` (`>=60`, cap-hit `28/28`).
- **Policy note:** late mix remained upgrade-heavy (`late upgrade lead ~124.35%`, late build share `~30.83%`), so plan-quality remains outside adaptive late in-band target.
- **Evidence:** `artifacts/x211_x212/x211/analysis_summary.json`, `artifacts/x211_x212/x211/rollouts_step_*_page_1.json`.

### Run X212 (second confirmatory granularity replicate)

- **Run ID:** `n85pe9l7yvpi2rnlrtatfmxu`
- **Config:** `configs/lab/prime-td-macro-round-60-x212.toml`
- **Env:** `kbediako/tower_defence@0.2.30` (`max_action_candidates=8`)
- **Coverage:** sampled steps `0/10/20/30/40/50`; all sampled steps parsed at max pull limit; coverage `100%` per sampled step.
- **Rollouts parsed:** all pages for sampled steps (page-2 probes empty), all rollouts, all turns (`24` samples; `1376` completion-turn messages).
- **Choose/index metrics (strict emitted):**
  - `choose_out_of_range=0` (`0.000%` of plan turns)
  - `choose_off_by_one_clamped=0` (`0.000%`)
  - residual unclamped `=0` (`0.000%`)
- **Strict non-cap delta accounting:** non-cap `pass/fail/missing = 640/0/0`; cap `delta1/delta0/missing/other = 24/24/0/0`.
- **Verdicts:** progression `PASS`, plan quality `PARTIAL`, reliability `diagnostic`, horizon lower-bound `PASS` (`>=60`, cap-hit `24/24`).
- **Policy note:** late mix remained upgrade-heavy (`late upgrade lead ~114.11%`, late build share `~31.84%`), outside adaptive late in-band target.
- **Evidence:** `artifacts/x211_x212/x212/analysis_summary.json`, `artifacts/x211_x212/x212/rollouts_step_*_page_1.json`.

## Pair Outcome (x211/x212)

- **Pair verdict:** `PASS` for granularity-8 confirm rule.
- **Decision rule outcome:** both `X211` and `X212` are `diagnostic` and both meet choose/index gate (`choose_out_of_range <= 5` or `<1%`, residual unclamped `<=1%`), so `max_action_candidates=8` is accepted as stable.
- **Evidence:** `artifacts/x211_x212/analysis_pair_summary.json`.

## Transfer (x211/x212 baseline-canonical)

- **Preflight baseline status:** canonical baseline present; baseline republish also run as safety preflight.
- **Command:** `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --baseline-canonical --out output/transfer/x211_x212.json --json`
- **Outcome:** `gate_status=pass`, `gate_reason=\"Transfer gate thresholds satisfied\"`
- **Metrics:** `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`
- **Evidence copy:** `artifacts/x211_x212/transfer_x211_x212.json`, `artifacts/x211_x212/transfer_baseline_core_v1.json`.

## Next Action

- **Full-run/scale-up:** `HOLD` (behavior reproducibility-in-band gate still not met; reliability and transfer are clean but policy-quality target remains unmet).
- **Granularity policy:** `max_action_candidates=8` is now accepted and can be used as the new default candidate-granularity setting for next controlled one-variable experiments.

## Decision / Next Step (x213/x214 launched)

- **Session startup checks before launch:** `artifacts/x213_x214/startup_checks/2026-02-17_220232_launch_session/`
- **Local CLI source-of-truth:** `Prime CLI version: 0.5.37`
- **CLI drift record:** `artifacts/x213_x214/startup_checks/2026-02-17_220232_launch_session/cli_drift.txt` (no drift vs prior `x211/x212` analysis session).
- **X213 launched:** `mumbrye2uit5exsv8wsu51py` with `configs/lab/prime-td-macro-round-60-x213.toml` (one-variable from X207: `dataset.safe_explore_upgrade_prob=0.35`; `max_action_candidates=8`, env `kbediako/tower_defence@0.2.30` unchanged).
- **X214 launched:** `mrg5geug5dm1xzx34m49lfcf` with `configs/lab/prime-td-macro-round-60-x214.toml` (exact replicate of X207 at `max_action_candidates=8`, env `kbediako/tower_defence@0.2.30`).
- **Launch evidence:** `artifacts/x213_x214/launch/launch_summary.json`.

## Startup checks (x213/x214 analysis session)

- **Session startup checks:** `artifacts/x213_x214/startup_checks/2026-02-17_232827_analysis_session/`
- **Local CLI source-of-truth:** `Prime CLI version: 0.5.37`
- **CLI drift record:** `artifacts/x213_x214/startup_checks/2026-02-17_232827_analysis_session/cli_drift.txt` (no drift vs launch session).

## Completed Runs (x213/x214)

### Run X213 (behavior lane; restarted for stall recovery)

- **Run ID:** `mumbrye2uit5exsv8wsu51py`
- **Config:** `configs/lab/prime-td-macro-round-60-x213.toml`
- **Env:** `kbediako/tower_defence@0.2.30`
- **Status:** `COMPLETED` (after two in-place restarts from checkpoint due sustained orchestrator stalls).
- **Recovery evidence:** `artifacts/x213_x214/restarts/x213_restart_1.txt`, `artifacts/x213_x214/restarts/x213_restart_2.txt`, `artifacts/x213_x214/monitor_status_after_restart.log`.
- **Coverage:** sampled steps `0/10/20/30/40/50` parsed at max limit and all pages; step counts `4/4/8/4/8/3` with step-50 coverage `75%` (below diagnostic threshold).
- **Rollouts parsed:** all fetched rollouts, all turns (`31` samples; `1818` completion-turn messages).
- **Strict choose/index metrics:**
  - `choose_out_of_range=0` (`0.000%` of plan turns)
  - `choose_off_by_one_clamped=0` (`0.000%`)
  - residual unclamped `=0` (`0.000%`)
- **Strict non-cap delta accounting:** non-cap `pass/fail/missing = 816/0/0`; cap `delta1/delta0/missing/other = 31/31/0/0`.
- **Late behavior metrics:** late upgrade lead `118.30%`; late build share `16.83%`.
- **Verdicts:** progression `PASS`, plan quality `PARTIAL`, reliability `non_diagnostic`, horizon lower-bound `PASS` (`>=60`, cap-hit `31/31`).
- **Policy-claim constraint:** no behavior-policy claim from `X213` because run is `non_diagnostic` (sample-step coverage failure at step 50).
- **Evidence:** `artifacts/x213_x214/x213/analysis_summary.json`, `artifacts/x213_x214/x213/rollouts_step_*_page_1.json`.

### Run X214 (control lane; exact X207 replicate)

- **Run ID:** `mrg5geug5dm1xzx34m49lfcf`
- **Config:** `configs/lab/prime-td-macro-round-60-x214.toml`
- **Env:** `kbediako/tower_defence@0.2.30`
- **Status:** `COMPLETED`.
- **Coverage:** sampled steps `0/10/20/30/40/50`; step counts `4/4/4/4/4/4` (`100%` each sampled step).
- **Rollouts parsed:** all fetched rollouts, all turns (`24` samples; `1424` completion-turn messages).
- **Strict choose/index metrics:**
  - `choose_out_of_range=24` (`3.371%` of plan turns)
  - `choose_off_by_one_clamped=23` (`3.230%`)
  - residual unclamped `=1` (`0.140%`)
  - out-of-range pattern: `24/24` emitted as noop off-by-one (`index == action_candidates_count`; noop index `count-1`).
- **Strict non-cap delta accounting:** non-cap `pass/fail/missing = 640/0/0`; cap `delta1/delta0/missing/other = 24/24/0/0`.
- **Late behavior metrics:** late upgrade lead `157.42%`; late build share `15.21%`.
- **Verdicts:** progression `PASS`, plan quality `PARTIAL`, reliability `diagnostic`, horizon lower-bound `PASS` (`>=60`, cap-hit `24/24`).
- **Evidence:** `artifacts/x213_x214/x214/analysis_summary.json`, `artifacts/x213_x214/x214/choose_out_of_range_examples.json`, `artifacts/x213_x214/x214/rollouts_step_*_page_1.json`.

## Pair Outcome (x213/x214)

- **Pair verdict:** `FAIL`.
- **Reliability gate:** **failed** (`X213` is `non_diagnostic` due coverage `75%` at sampled step 50).
- **Platform choose/index gate:** **failed** (`X214` emitted `choose_out_of_range=24`, `3.371%` > accepted gate).
- **Behavior objective gate (`X213` target lead <=89 and >0):** **failed** (observed `118.30%`), and policy interpretation is blocked by non-diagnostic reliability.
- **Decision note:** this cycle did not isolate policy-lever effect because control lane regressed on emitted-index stability while behavior lane failed reliability.
- **Evidence:** `artifacts/x213_x214/analysis_pair_summary.json`.

## Transfer (x213/x214 baseline-canonical)

- **Preflight baseline republish:** `npm run benchmark:transfer:baseline -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400`
- **Command:** `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --baseline-canonical --out output/transfer/x213_x214.json --json`
- **Outcome:** `gate_status=pass`, `gate_reason=\"Transfer gate thresholds satisfied\"`
- **Metrics:** `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`
- **Evidence copy:** `artifacts/x213_x214/transfer_x213_x214.json`, `artifacts/x213_x214/transfer_baseline_core_v1.json`.

## Next Action

- **Full-run/scale-up:** `HOLD`.
- **Immediate recommendation:** hold new policy-lever experiments until platform reliability is re-confirmed at `max_action_candidates=8`:
  - run a control-only reliability reconfirm (`x214` exact replicate) with strict emitted-index accounting;
  - if emitted off-by-one persists, patch prompt/decode guardrail before any further behavior-lane lever testing.
- **Anti-circling control:** do **not** repeat `safe_explore_upgrade_prob` tuning until control lane is gate-clean; next policy lane should pivot to a different lever family only after control stability is restored.

## Decision / Next Step (x215/x216 launched)

- **Session startup checks before launch:** `artifacts/x215_x216/startup_checks/2026-02-17_233951_launch_session/`
- **Local CLI source-of-truth:** `Prime CLI version: 0.5.37`
- **CLI drift record:** `artifacts/x215_x216/startup_checks/2026-02-17_233951_launch_session/cli_drift.txt` (no drift vs prior `x213/x214` analysis session).
- **X215 launched:** `b81ryt43nwav38f2y1vkb8ep` with `configs/lab/prime-td-macro-round-60-x215.toml` (exact replicate of X214; env `kbediako/tower_defence@0.2.30`, `max_action_candidates=8`, `max_tokens=36`).
- **X216 launched:** `f8umop4tqws1u2ji06id39sm` with `configs/lab/prime-td-macro-round-60-x216.toml` (one-variable from X214: `sampling.max_tokens 36 -> 32`; all other knobs unchanged).
- **Launch evidence:** `artifacts/x215_x216/launch/launch_summary.json`.

## Startup checks (x215/x216 analysis session)

- **Session startup checks:** `artifacts/x215_x216/startup_checks/2026-02-18_080910_analysis_session/`
- **Local CLI source-of-truth:** `Prime CLI version: 0.5.37`
- **CLI drift record:** `artifacts/x215_x216/startup_checks/2026-02-18_080910_analysis_session/cli_drift.txt` (no drift vs x215/x216 launch session).

## Completed Runs (x215/x216)

### Run X215 (control reconfirm; exact x214 replicate)

- **Run ID:** `b81ryt43nwav38f2y1vkb8ep`
- **Config:** `configs/lab/prime-td-macro-round-60-x215.toml`
- **Coverage:** sampled steps `0/10/20/30/40/50` all `4/4` (`100%`) at max pull limit (`-n 100`), all pages parsed.
- **Parse volume:** `samples_total=24`, `turns_total=692`, `plan_turn_total=692`.
- **Strict choose/index metrics (plan-turn denominator):**
  - `choose_out_of_range=0` (`0.000%`)
  - `choose_off_by_one_clamped=0` (`0.000%`)
  - residual unclamped `=0` (`0.000%`)
- **Strict non-cap delta accounting:** non-cap `pass/fail/missing = 644/0/0`; cap `delta1/delta0/missing/other = 24/0/0/0`.
- **Verdicts:** progression `PASS`, plan quality `PARTIAL`, reliability `diagnostic`, horizon lower-bound `PASS` (`>=60`, cap-hit `24/24`).
- **Plan-quality context:** late build share `16.76%`, late upgrade lead `122.41%` (upgrade-leaning; outside in-band `15-25%`).
- **Evidence:** `artifacts/x215_x216/x215/analysis_summary.json`.

### Run X216 (one-variable token canary: max_tokens `36 -> 32`)

- **Run ID:** `f8umop4tqws1u2ji06id39sm`
- **Config:** `configs/lab/prime-td-macro-round-60-x216.toml`
- **Coverage:** sampled steps `0/10/20/30/40/50` all `4/4` (`100%`) at max pull limit (`-n 100`), all pages parsed.
- **Parse volume:** `samples_total=24`, `turns_total=672`, `plan_turn_total=672`, `invalid_plan=672` (all turns required regex fallback extraction due truncated/invalid JSON plan output).
- **Strict choose/index metrics (plan-turn denominator):**
  - `choose_out_of_range=0` (`0.000%`)
  - `choose_off_by_one_clamped=0` (`0.000%`)
  - residual unclamped `=0` (`0.000%`)
- **Strict non-cap delta accounting:** non-cap `pass/fail/missing = 624/0/0`; cap `delta1/delta0/missing/other = 24/0/0/0`.
- **Verdicts:** progression `PASS`, plan quality `FAIL`, reliability `diagnostic`, horizon lower-bound `PASS` (`>=60`, cap-hit `24/24`).
- **Policy-quality degradation note (separate from reliability):** format/truncation regressed (`metrics/_macro_round_format_reward = -1.0` across run; `is_truncated/mean` up to `1.0`), late mix build-leading (`late upgrade lead = -100.0%`, build share `79.02%`).
- **Evidence:** `artifacts/x215_x216/x216/analysis_summary.json`.

## Pair Outcome (x215/x216)

- **Decision rule result:** `PASS`.
- **Reason:** `X215` is `diagnostic` and choose/index gate-clean, so treat `x214` as variance outlier per rule.
- **Operational decision:** keep platform baseline at `max_tokens=36`; do **not** adopt `max_tokens=32` because X216 produced all-invalid/truncated plan outputs despite clean reliability counters.
- **Evidence:** `artifacts/x215_x216/analysis_pair_summary.json`.

## Transfer (x215/x216 baseline-canonical)

- **Initial transfer attempt:** failed due missing canonical baseline file `output/transfer/baselines/core-v1__core-v1-default.json`.
- **Baseline republish:**
  - `npm run benchmark:transfer:baseline -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400`
- **Transfer command:**
  - `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --baseline-canonical --out output/transfer/x215_x216.json --json`
- **Outcome:** `gate_status=pass`, `gate_reason="Transfer gate thresholds satisfied"`.
- **Canonical metrics:** `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`.
- **Evidence copy:** `artifacts/x215_x216/transfer_x215_x216.json`, `artifacts/x215_x216/transfer_baseline_core_v1.json`.

## Next Action

- **Full-run/scale-up:** `HOLD` (policy-quality target band still not met reproducibly).
- **Platform baseline:** continue from `x215` settings (`max_tokens=36`, `max_action_candidates=8`) for next policy-lever experiments.

## Calibration Note (x211/x212/x215 economics)

- **Source artifact:** `artifacts/x217_x218/calibration_x211_x212_x215.json` (computed from full rollout turn parsing for `x211`, `x212`, `x215`).
- **Cost-weighted late action mix (chosen actions, build+upgrade spend only):**
  - `x211`: upgrade spend share `58.57%`, build spend share `41.43%` (upgrade-to-build spend ratio `1.414`)
  - `x212`: upgrade spend share `59.05%`, build spend share `40.95%` (ratio `1.442`)
  - `x215`: upgrade spend share `59.66%`, build spend share `40.34%` (ratio `1.479`)
  - combined: upgrade spend share `59.07%`, build spend share `40.93%` (ratio `1.443`, spend lead ≈ `+44.3%` vs build)
- **Late-phase best-action prevalence proxy (candidate + reward evidence):**
  - candidate opportunity in late phase remains build-heavy by spend capacity (`build 68.49%`, `upgrade 31.51%`), but realized policy still runs upgrade-heavy spend.
  - next-turn pop-reward proxy is consistently higher after `upgrade_only` late turns than `build_only` late turns (e.g. `x211`: `559.91` vs `418.45`; `x212`: `559.00` vs `428.96`; `x215`: `554.50` vs `419.63`).
- **Band support decision:** current count-based late upgrade-lead in-band target `15-25%` is **not economically supported** by these diagnostics.
- **Recommended in-band target update:** use an economics-calibrated late target of **`25-45%` upgrade lead on spend** (primary), and treat count-based lead as secondary trend signal only.

## Decision / Next Step (x217/x218 launched)

- **Session startup checks before launch/calibration:** `artifacts/x217_x218/startup_checks/2026-02-18_083603_calibration_session/`
- **Local CLI source-of-truth:** `Prime CLI version: 0.5.37`
- **CLI drift record:** `artifacts/x217_x218/startup_checks/2026-02-18_083603_calibration_session/cli_drift.txt` (no drift vs prior snapshot).
- **X217 launched:** `rkgqiusntw6xkvyv60zokmpy` with `configs/lab/prime-td-macro-round-60-x217.toml` (exact replicate of X215 baseline).
- **X218 launched:** `ow2slx2bsq8zx29w2fm11lt3` with `configs/lab/prime-td-macro-round-60-x218.toml` (one-variable from X215: `dataset.safe_explore_upgrade_prob 0.50 -> 0.20`; all else unchanged).
- **Launch evidence:** `artifacts/x217_x218/launch/launch_summary.json`.

## Completed Runs (x217/x218)

## Method Update (2026-02-18; restart-aggregated coverage fix)

- Recomputed `x217/x218` from existing artifacts only (no relaunch) using updated analyzer logic in `artifacts/x217_x218/analyze_pair.py`.
- Expected sampled-step baseline now uses nominal config count: `expected_nominal = batch_size * rollouts_per_example` (`4 * 1 = 4`), replacing prior `max(step_counts)` logic.
- Coverage reporting now records both `raw_count_by_step` (audit; includes restart aggregation) and `effective_count_by_step` (latest `created_at` cluster per step).
- Reliability coverage gates now use `min(effective_count, expected_nominal) / expected_nominal`.
- Method-change evidence: `artifacts/x217_x218/x217/analysis_summary.json`, `artifacts/x217_x218/x218/analysis_summary.json`, `artifacts/x217_x218/analysis_pair_summary.json`.

### Run X217 (control; exact x215 replicate)

- **Run ID:** `rkgqiusntw6xkvyv60zokmpy`
- **Config:** `configs/lab/prime-td-macro-round-60-x217.toml`
- **Status:** `COMPLETED` (required in-place restarts from checkpoint due long-step stalls).
- **Restart evidence:** `artifacts/x217_x218/restarts/x217_restart_1.txt`, `artifacts/x217_x218/restarts/x217_restart_2.txt`.
- **Coverage (method-corrected):** sampled steps `0/10/20/30/40/50` parsed at max pull limit (`-n 100`) and all pages; expected nominal `4`; raw counts `4/3/4/4/4/8`; effective counts `4/3/4/4/4/4`; gate coverage `100/75/100/100/100/100%`.
- **Parse volume:** `samples_total=27`, `turns_total=743`, `plan_turn_total=743`, `invalid_plan=0`.
- **Strict choose/index metrics:**
  - `choose_out_of_range=0` (`0.000%`)
  - `choose_off_by_one_clamped=0` (`0.000%`)
  - residual unclamped `=0` (`0.000%`)
- **Strict non-cap delta accounting:** non-cap `pass/fail/missing = 690/0/0`; cap `delta1/delta0/missing/other = 26/0/0/0`.
- **Late policy mix (spend-primary):** late build spend `49800.0`, late upgrade spend `85580.0`, late upgrade spend lead `71.85%` (out of target `25-45%`); count trend secondary: late upgrade count lead `136.14%`.
- **Verdicts:** progression `FAIL`, plan quality `PARTIAL`, reliability `non_diagnostic`, horizon lower-bound `PASS` (`>=30`, cap-hit `26/27`).
- **Evidence:** `artifacts/x217_x218/x217/analysis_summary.json`.

### Run X218 (one-variable from x215: `safe_explore_upgrade_prob 0.50 -> 0.20`)

- **Run ID:** `ow2slx2bsq8zx29w2fm11lt3`
- **Config:** `configs/lab/prime-td-macro-round-60-x218.toml`
- **Status:** `COMPLETED` (required multiple in-place restarts from checkpoint due long-step stalls).
- **Restart evidence:** `artifacts/x217_x218/restarts/x218_restart_4.txt`, `artifacts/x217_x218/restarts/x218_restart_5.txt`, `artifacts/x217_x218/restarts/x218_restart_6.txt`.
- **Coverage (method-corrected):** sampled steps `0/10/20/30/40/50` parsed at max pull limit (`-n 100`) and all pages; expected nominal `4`; raw counts `4/12/4/4/3/4`; effective counts `4/4/4/4/3/4`; gate coverage `100/100/100/100/75/100%`.
- **Parse volume:** `samples_total=31`, `turns_total=894`, `plan_turn_total=894`, `invalid_plan=0`.
- **Strict choose/index metrics:**
  - `choose_out_of_range=0` (`0.000%`)
  - `choose_off_by_one_clamped=0` (`0.000%`)
  - residual unclamped `=0` (`0.000%`)
- **Strict non-cap delta accounting:** non-cap `pass/fail/missing = 833/0/0`; cap `delta1/delta0/missing/other = 30/0/0/0`.
- **Late policy mix (spend-primary):** late build spend `61400.0`, late upgrade spend `116580.0`, late upgrade spend lead `89.87%` (out of target `25-45%`); count trend secondary: late upgrade count lead `110.75%`.
- **Verdicts:** progression `FAIL`, plan quality `PARTIAL`, reliability `non_diagnostic`, horizon lower-bound `PASS` (`>=37`, cap-hit `30/31`).
- **Evidence:** `artifacts/x217_x218/x218/analysis_summary.json`.

## Pair Outcome (x217/x218)

- **Pair verdict:** `FAIL`.
- **Reliability gate:** **failed** (both runs remain `non_diagnostic` under corrected effective-count coverage: `x217` step `10` = `75%`, `x218` step `40` = `75%`).
- **Platform choose/index gate:** **pass** (`choose_out_of_range=0`, residual unclamped `0` on both runs).
- **Behavior objective gate (spend-primary, X218 vs X217):** treatment worsened spend lead (`71.85% -> 89.87%`, reduction `-18.02pp`), and both runs are `non_diagnostic`; **no policy claim allowed**.
- **Decision:** hold policy-lever conclusion for this cycle; treat result as non-diagnostic trend-only.
- **Evidence:** `artifacts/x217_x218/analysis_pair_summary.json`.

## Transfer (x217/x218 baseline-canonical)

- **Command:** `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --baseline-canonical --out output/transfer/x217_x218.json --json`
- **Outcome:** `gate_status=pass`, `gate_reason="Transfer gate thresholds satisfied"`.
- **Canonical metrics:** `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`.
- **Evidence copy:** `artifacts/x217_x218/transfer_x217_x218.json`.

## Next Action

- **Full-run/scale-up:** `HOLD`.
- **Immediate lane policy:** do not make policy-quality claims from x217/x218; re-establish clean diagnostic reliability first, then continue one-variable policy lever work.
- **Anti-circling:** if `safe_explore_upgrade_prob` is re-tested, keep control replicate diagnostic in the same cycle; otherwise pivot lever family after reliability is stable.

## Decision / Next Step (x219/x220 launched)

- **Session startup checks before launch/analysis:** `artifacts/x219_x220/startup_checks/2026-02-18_113547_x219_x220_session/`
- **Local CLI source-of-truth:** `Prime CLI version: 0.5.37`
- **CLI drift record:** `artifacts/x219_x220/startup_checks/2026-02-18_113547_x219_x220_session/cli_drift.txt` (no material command-surface drift; rollout retrieval command confirmed as `prime rl rollouts`).
- **X219 launched:** `vj5og3mglx2udpw5lgrhjcrs` with `configs/lab/prime-td-macro-round-60-x219.toml` (exact replicate of x215/x217 baseline profile).
- **X220 launched:** `nvmw8omr11nqq7n9691ooqe4` with `configs/lab/prime-td-macro-round-60-x220.toml` (exact copy of X219 with one change only: `env.args.config.dataset.safe_explore_upgrade_prob = 0.20`).
- **One-variable diff check:** x219 vs x215 = name only; x220 vs x219 = name + `safe_explore_upgrade_prob` only.
- **Launch evidence:** `artifacts/x219_x220/launch/launch_summary.json`.

## Completed Runs (x219/x220)

### Run X219 (control; exact baseline replicate)

- **Run ID:** `vj5og3mglx2udpw5lgrhjcrs`
- **Config:** `configs/lab/prime-td-macro-round-60-x219.toml`
- **Status:** `COMPLETED` (`2026-02-18 04:19`).
- **Runtime note:** rollout-queue warning appeared four times (`Cancelled 1 old rollout requests...`); treated as informational because delta accounting and coverage gates remained clean.
- **Coverage (method-corrected):** sampled steps `0/10/20/30/40/50` pulled at max limit (`-n 100`) and all pages; expected nominal `4`; raw counts `4/4/4/4/4/4`; effective counts `4/4/4/4/4/4`; gate coverage `100/100/100/100/100/100%`.
- **Pagination evidence:** `artifacts/x219_x220/x219/rollouts_step_*_page_1.json` + terminal probes `artifacts/x219_x220/x219/rollouts_step_*_page_2_probe.json`.
- **Parse volume:** `samples_total=24`, `turns_total=696`, `plan_turn_total=696`, `invalid_plan=0`.
- **Strict choose/index metrics:**
  - `choose_out_of_range=0` (`0.000%`)
  - `choose_off_by_one_clamped=0` (`0.000%`)
  - residual unclamped `=0` (`0.000%`)
- **Strict non-cap delta accounting:** non-cap `pass/fail/missing = 648/0/0`; cap `delta1/delta0/missing/other = 24/0/0/0`.
- **Late policy mix (spend-primary):** late build spend `47000.0`, late upgrade spend `67800.0`, late upgrade spend lead `44.26%` (in target `25-45%`); count trend secondary: late upgrade count lead `116.60%`.
- **Verdicts:** progression `PASS`, plan quality `PARTIAL`, reliability `diagnostic`, horizon lower-bound `PASS` (`>=60`, cap-hit `24/24`).
- **Evidence:** `artifacts/x219_x220/x219/analysis_summary.json`.

### Run X220 (treatment; one-variable `safe_explore_upgrade_prob=0.20`)

- **Run ID:** `nvmw8omr11nqq7n9691ooqe4`
- **Config:** `configs/lab/prime-td-macro-round-60-x220.toml`
- **Status:** `COMPLETED` (`2026-02-18 04:47`).
- **Stall handling:** sustained no-progress windows required controlled restarts from checkpoint (`artifacts/x219_x220/restarts/x220_restart_1.txt` ... `artifacts/x219_x220/restarts/x220_restart_4.txt`, post-restart status in `artifacts/x219_x220/restarts/x220_post_restart_get_*.txt`).
- **Runtime note:** one rollout-queue warning observed (`Cancelled 2 old rollout requests...`); treated as informational because coverage and delta gates remained clean.
- **Coverage (method-corrected):** sampled steps `0/10/20/30/40/50` pulled at max limit (`-n 100`) and all pages; expected nominal `4`; raw counts `4/4/4/4/4/4`; effective counts `4/4/4/4/4/4`; gate coverage `100/100/100/100/100/100%`.
- **Pagination evidence:** `artifacts/x219_x220/x220/rollouts_step_*_page_1.json` + terminal probes `artifacts/x219_x220/x220/rollouts_step_*_page_2_probe.json`.
- **Parse volume:** `samples_total=24`, `turns_total=680`, `plan_turn_total=680`, `invalid_plan=0`.
- **Strict choose/index metrics:**
  - `choose_out_of_range=0` (`0.000%`)
  - `choose_off_by_one_clamped=0` (`0.000%`)
  - residual unclamped `=0` (`0.000%`)
- **Strict non-cap delta accounting:** non-cap `pass/fail/missing = 632/0/0`; cap `delta1/delta0/missing/other = 24/0/0/0`.
- **Late policy mix (spend-primary):** late build spend `45600.0`, late upgrade spend `90320.0`, late upgrade spend lead `98.07%` (out of target `25-45%`); count trend secondary: late upgrade count lead `118.86%`.
- **Verdicts:** progression `PASS`, plan quality `PARTIAL`, reliability `diagnostic`, horizon lower-bound `PASS` (`>=60`, cap-hit `24/24`).
- **Evidence:** `artifacts/x219_x220/x220/analysis_summary.json`.

## Pair Outcome (x219/x220)

- **Pair verdict:** `FAIL`.
- **Reliability gate:** **pass** (both runs `diagnostic`, full-turn parsing complete, no upload 500, sampled-step coverage gate `100%` at all sampled steps).
- **Platform choose/index gate:** **pass** on both runs (`choose_out_of_range=0`, residual unclamped `0`).
- **Behavior objective (spend-primary, treatment vs control):** **failed**.
  - `x219` late upgrade spend lead: `44.26%` (in target band)
  - `x220` late upgrade spend lead: `98.07%` (out of target band)
  - spend reduction: `-53.81pp` (worse); spend-band distance moved from `0.0pp` to `53.07pp`
- **Count trend (secondary only):** `116.60% -> 118.86%` (`+2.26pp`).
- **Decision rule outcome:** both runs are diagnostic, so comparison is valid; treatment failed spend-primary criteria and should not be repeated as a positive lever claim.
- **Evidence:** `artifacts/x219_x220/analysis_pair_summary.json`, `artifacts/x219_x220/spend_backfill_x219_x220.json`.

## Transfer (x219/x220 baseline-canonical)

- **Execution context:** transfer command run from `/Users/kbediako/Code/tower-defence` (benchmark package root).
- **Preflight note:** first transfer attempt failed because canonical baseline file was missing; baseline was republished and transfer re-run.
- **Commands:**
  - `npm run benchmark:transfer:baseline -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400`
  - `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --baseline-canonical --out output/transfer/x219_x220.json --json`
- **Outcome:** `gate_status=pass`, `gate_reason="Transfer gate thresholds satisfied"`.
- **Canonical metrics:** `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`.
- **Evidence copy:** `artifacts/x219_x220/transfer_x219_x220.json`, `artifacts/x219_x220/transfer_baseline_core_v1.json`, `artifacts/x219_x220/transfer_command.log`.

## Criteria Status (Session A-E)

- **A. Analyzer/process correction:** `PASS`  
  Updated analyzer now uses `expected_nominal = batch_size * rollouts_per_example`, reports both raw/effective per-step counts, and gates on `min(effective_count, expected_nominal)/expected_nominal` while retaining raw audit counts. Evidence: `artifacts/x217_x218/analyze_pair.py`.
- **B. Recompute x217/x218 with corrected method:** `PASS`  
  Recomputed without relaunch; both runs remain `non_diagnostic` under corrected effective coverage; policy claim for this lane remains blocked. Evidence: `artifacts/x217_x218/analysis_pair_summary.json`.
- **C. Launch next concurrent one-variable pair (x219/x220):** `PASS`  
  x219 exact baseline replicate; x220 one-variable treatment (`safe_explore_upgrade_prob=0.20`); run IDs + config paths recorded at launch. Evidence: `artifacts/x219_x220/launch/launch_summary.json`.
- **D. Full hygiene + canonical transfer:** `PASS`  
  Sampled steps `0/10/20/30/40/50` pulled at max limit with all pages, all rollouts/turns parsed, strict non-cap delta accounting and choose/index residual metrics reported, `--baseline-canonical` transfer executed and passing. Evidence: `artifacts/x219_x220/x219/analysis_summary.json`, `artifacts/x219_x220/x220/analysis_summary.json`, `artifacts/x219_x220/transfer_x219_x220.json`.
- **E. Decision rule application:** `PASS` (rule applied; treatment result `FAIL`)  
  Both runs diagnostic, comparison valid; x220 failed spend-primary criteria (late upgrade spend lead `98.07%` vs control `44.26%`, reduction `-53.81pp`), so no positive policy claim; full-run/scale-up remains `HOLD` until both reliability and behavior criteria are satisfied.

## Decision / Next Step (x221/x222 launched)

- **Session startup checks before launch/analysis:** `artifacts/startup_checks/prime_cli_surface_2026-02-18.txt`
- **Local CLI source-of-truth:** `Prime CLI version: 0.5.37`
- **CLI drift record:** `artifacts/startup_checks/cli_drift_2026-02-18.md` (no material command-surface drift for this session).
- **X221 launched:** `poujha9095dr06pep4vbpjhi` with `configs/lab/prime-td-macro-round-60-x221.toml` (exact replicate of x219 baseline profile).
- **X222 launched:** `a4ynpac00ltxu8qjuggqpijb` with `configs/lab/prime-td-macro-round-60-x222.toml` (one-variable from X221: `late.min_build_frac 0.72 -> 0.73`).
- **One-variable diff check:** x222 vs x221 differs only in `env.args.config.observation.candidate_balance.by_phase.late.min_build_frac`.
- **Launch evidence:** `artifacts/x221_x222/launch/launch_summary.json`, `artifacts/x221_x222/plan.md`, `artifacts/x221_x222/config_diff.txt`.

## Completed Runs (x221/x222)

### Run X221 (control; exact x219 replicate)

- **Run ID:** `poujha9095dr06pep4vbpjhi`
- **Config:** `configs/lab/prime-td-macro-round-60-x221.toml`
- **Status:** `COMPLETED`.
- **Coverage (method-corrected):** sampled steps `0/10/20/30/40/50` pulled at max limit (`-n 100`) and all pages; expected nominal `4`; raw/effective counts `4/4/4/4/4/4`; gate coverage `100%` at all sampled steps.
- **Parse volume:** `samples_total=24`, `turns_total=696`, `plan_turn_total=696`, `invalid_plan=0`.
- **Strict choose/index metrics:** `choose_out_of_range=0` (`0.000%`), `choose_off_by_one_clamped=0` (`0.000%`), residual unclamped `0` (`0.000%`).
- **Strict non-cap delta accounting:** non-cap `pass/fail/missing = 648/0/0`; cap `delta1/delta0/missing/other = 24/0/0/0`.
- **Late policy mix (spend-primary):** late build spend `39600.0`, late upgrade spend `67200.0`, late upgrade spend lead `69.70%` (out of target `25-45%`); count trend secondary: late upgrade count lead `150.00%`.
- **Verdicts:** progression `PASS`, plan quality `PARTIAL`, reliability `diagnostic`, horizon lower-bound `PASS` (`>=60`, cap-hit `24/24`).
- **Evidence:** `artifacts/x221_x222/x221/analysis_summary.json`.

### Run X222 (treatment; one-variable `late.min_build_frac=0.73`)

- **Run ID:** `a4ynpac00ltxu8qjuggqpijb`
- **Config:** `configs/lab/prime-td-macro-round-60-x222.toml`
- **Status:** `COMPLETED`.
- **Coverage (method-corrected):** sampled steps `0/10/20/30/40/50` pulled at max limit (`-n 100`) and all pages; expected nominal `4`; raw/effective counts `4/4/4/4/4/4`; gate coverage `100%` at all sampled steps.
- **Parse volume:** `samples_total=24`, `turns_total=696`, `plan_turn_total=696`, `invalid_plan=0`.
- **Strict choose/index metrics:** `choose_out_of_range=0` (`0.000%`), `choose_off_by_one_clamped=0` (`0.000%`), residual unclamped `0` (`0.000%`).
- **Strict non-cap delta accounting:** non-cap `pass/fail/missing = 648/0/0`; cap `delta1/delta0/missing/other = 24/0/0/0`.
- **Late policy mix (spend-primary):** late build spend `45200.0`, late upgrade spend `71280.0`, late upgrade spend lead `57.70%` (out of target `25-45%`); count trend secondary: late upgrade count lead `138.50%`.
- **Verdicts:** progression `PASS`, plan quality `PARTIAL`, reliability `diagnostic`, horizon lower-bound `PASS` (`>=60`, cap-hit `24/24`).
- **Evidence:** `artifacts/x221_x222/x222/analysis_summary.json`.

## Pair Outcome (x221/x222)

- **Pair verdict:** `FAIL`.
- **Reliability gate:** **pass** (both runs `diagnostic`, no upload 500s, full-turn parsing complete, sampled-step gate coverage `100%` at all sampled steps).
- **Platform choose/index gate:** **pass** on both runs (`choose_out_of_range=0`, residual unclamped `0`).
- **Behavior objective (spend-primary, treatment vs control):** **failed**.
  - `x221` late upgrade spend lead: `69.70%` (out of target `25-45%`)
  - `x222` late upgrade spend lead: `57.70%` (out of target `25-45%`)
  - spend reduction: `+12.00pp` (improved), spend-band distance `24.70pp -> 12.70pp` (improved), but treatment remains out-of-band
- **Count trend (secondary only):** `150.00% -> 138.50%` (`-11.50pp`).
- **Decision rule outcome:** both runs are diagnostic and treatment improved directionally, but spend-primary in-band target is still unmet; no positive policy claim.
- **Evidence:** `artifacts/x221_x222/analysis_pair_summary.json`, `artifacts/x221_x222/spend_backfill_x221_x222.json`.

## Transfer (x221/x222 baseline-canonical)

- **Execution context:** transfer command run from `/Users/kbediako/Code/tower-defence` (benchmark package root).
- **Commands:**
  - `npm run benchmark:transfer:baseline -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400`
  - `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --baseline-canonical --out output/transfer/x221_x222.json --json`
- **Outcome:** `gate_status=pass`, `gate_reason="Transfer gate thresholds satisfied"`.
- **Canonical metrics:** `core_completion_rate=1`, `waves_survived_mean=2`, `waves_survived_p10=2`, `base_hp_loss_mean=0`, `leftover_cash_mean=312`, `invalid_action_rate=0`, `stall_timeout_rate=0`, `determinism_replay_match_rate=1`.
- **Evidence copy:** `artifacts/x221_x222/transfer_x221_x222.json`, `artifacts/x221_x222/transfer_baseline_core_v1.json`, `artifacts/x221_x222/transfer_command.log`.

## FULL-RUN Decision (x221/x222)

- **FULL-RUN:** `NO-GO`.
- **Why:** reliability/progression/horizon/transfer gates are all clean, but the spend-primary plan-quality gate remains unmet (`x221` and `x222` both outside `25-45%` late upgrade spend lead band).
- **Blockers:** spend-primary policy quality remains out-of-band; no run in this pair demonstrates in-band late spend mix under diagnostic reliability.

## X223/X224 Launch Record

- Startup checks: `artifacts/x223_x224/startup_checks/2026-02-18_102944Z_x223_x224_session/prime_cli_surface.txt`
- CLI drift note: `artifacts/x223_x224/startup_checks/2026-02-18_102944Z_x223_x224_session/cli_drift.md` (no material drift).
- `X223` launched:
  - run_id: `cwwxhitoeputg4e9hycy6e7i`
  - config: `configs/lab/prime-td-macro-round-60-x223.toml`
  - type: one-variable from `x222` (`late.min_build_frac 0.73 -> 0.74`)
- `X224` launched:
  - run_id: `u2zia71nvxzb1krk4vh3nzni`
  - config: `configs/lab/prime-td-macro-round-60-x224.toml`
  - type: one-variable from `x222` (`late.min_build_frac 0.73 -> 0.75`)
- Launch evidence: `artifacts/x223_x224/launch/launch_summary.json`, `artifacts/x223_x224/config_diff.txt`.

## X223/X224 Analysis Session (completed)

### X223 (`cwwxhitoeputg4e9hycy6e7i`, `configs/lab/prime-td-macro-round-60-x223.toml`)

- **Status:** `COMPLETED`.
- **Coverage:** sampled steps `0/10/20/30/40/50` at max pull limit (`-n 100`) and all pages; raw/effective counts `4/4/4/4/4/4`; gate coverage `100%` for each sampled step.
- **Parse volume:** `samples_total=24`, `turns_total=688`, `plan_turn_total=688`, `invalid_plan=0`.
- **Action mix + candidates + phase breakdown:**
  - `action_mix`: `build=238`, `upgrade=518`, `noop=619`
  - `candidate_pool`: `build=1888`, `upgrade=1316`, `noop=1376`
  - `phase_action.late`: `build=238`, `upgrade=518`, `noop=619`
- **Strict choose/index accounting:**
  - `choose_out_of_range=1` (`0.145%`)
  - `choose_off_by_one_clamped=1` (`0.145%`)
  - residual unclamped `0` (`0.000%`)
- **Full delta accounting:** non-cap `pass/fail/missing = 640/0/0`; cap `delta1/delta0/missing/other = 24/0/0/0`.
- **Reliability notes:** `upload_500_count=0`, `interleaving_warning_count=0`, parse failures `0`, full-turn parsing complete.
- **Spend-primary metrics:**
  - `late_build_spend=47600.0`
  - `late_upgrade_spend=69020.0`
  - `late_upgrade_spend_lead_pct=45.00%` (in-band edge)
  - spend-band distance from `25-45`: `0.00pp`
  - secondary count trend: `late_upgrade_count_lead_pct=117.65%`
- **Verdicts:** progression `PASS`, plan quality `PASS`, reliability `diagnostic`, horizon lower-bound `PASS` (`>=60`, cap-hit `24/24`).
- **Evidence:** `artifacts/x223_x224/x223/analysis_summary.json`.

### X224 (`u2zia71nvxzb1krk4vh3nzni`, `configs/lab/prime-td-macro-round-60-x224.toml`)

- **Status:** `COMPLETED`.
- **Coverage:** sampled steps `0/10/20/30/40/50` at max pull limit (`-n 100`) and all pages; raw/effective counts `4/4/4/4/4/4`; gate coverage `100%` for each sampled step.
- **Parse volume:** `samples_total=24`, `turns_total=707`, `plan_turn_total=707`, `invalid_plan=0`.
- **Action mix + candidates + phase breakdown:**
  - `action_mix`: `build=237`, `upgrade=536`, `noop=641`
  - `candidate_pool`: `build=1710`, `upgrade=1350`, `noop=1414`
  - `phase_action.late`: `build=237`, `upgrade=536`, `noop=641`
- **Strict choose/index accounting:**
  - `choose_out_of_range=0` (`0.000%`)
  - `choose_off_by_one_clamped=0` (`0.000%`)
  - residual unclamped `0` (`0.000%`)
- **Full delta accounting:** non-cap `pass/fail/missing = 660/0/0`; cap `delta1/delta0/missing/other = 23/0/0/0`.
- **Reliability notes:** `upload_500_count=0`, `interleaving_warning_count=0`, parse failures `0`, full-turn parsing complete.
- **Spend-primary metrics:**
  - `late_build_spend=47400.0`
  - `late_upgrade_spend=70620.0`
  - `late_upgrade_spend_lead_pct=48.99%` (out-of-band high)
  - spend-band distance from `25-45`: `3.99pp`
  - secondary count trend: `late_upgrade_count_lead_pct=126.16%`
- **Verdicts:** progression `FAIL`, plan quality `PARTIAL`, reliability `diagnostic`, horizon lower-bound `PASS` (`>=47`, cap-hit `23/24`).
- **Evidence:** `artifacts/x223_x224/x224/analysis_summary.json`.

## Pair Outcome (x223/x224)

- **Strict pair PASS rule (required) check:**
  - both diagnostic: `PASS`
  - choose/index gate clean: `PASS`
  - non-cap fail=0 and missing=0: `PASS`
  - at least one run in `25-45%` spend band: `PASS` (`x223=45.00%`)
- **Pair verdict under rule:** `PASS`.
- **Spend-primary comparison:**
  - `x223` spend lead `45.00%` (in-band)
  - `x224` spend lead `48.99%` (out-of-band)
  - spend delta (`x224 - x223`) `+3.99pp`
  - spend reduction (`x223 - x224`) `-3.99pp` (x224 worse)
- **Count trend (secondary only):** `117.65% -> 126.16%` (`+8.51pp`).
- **Lever-family exhaustion rule:** `NOT exhausted` (`both >45` false; `any <25` false).
- **Evidence:** `artifacts/x223_x224/analysis_pair_summary.json`, `artifacts/x223_x224/spend_backfill_x223_x224.json`.

## Transfer (x223/x224 baseline-canonical)

- **Commands (from `/Users/kbediako/Code/tower-defence`):**
  - `npm run benchmark:transfer:baseline -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400`
  - `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --baseline-canonical --out output/transfer/x223_x224.json --json`
- **Transfer verdict:** `PASS`.
  - `gate_status=pass`
  - `gate_reason="Transfer gate thresholds satisfied"`
- **Evidence:** `artifacts/x223_x224/transfer_x223_x224.json`, `artifacts/x223_x224/transfer_baseline_core_v1.json`, `artifacts/x223_x224/transfer_command.log`.

## FULL-RUN Decision (x223/x224)

- **FULL-RUN:** `GO`.
- **Rule application:** spend-primary gate criteria are satisfied with diagnostic reliability (strict pair PASS rule met) and transfer gate passes.
- **Evidence:** `artifacts/x223_x224/final_decision.md`.

## X225 Full-Run Launch Record

- **Launched at (UTC):** 2026-02-18T12:56:42Z
- **Run ID:** `t7c3gjpoui57fs11ctzr7wzn`
- **Config:** `configs/lab/prime-td-macro-round-60-x225.toml`
- **Baseline source:** `configs/lab/prime-td-macro-round-60-x223.toml`
- **Startup checks:** `artifacts/x225_fullrun/startup_checks/2026-02-18_124747Z_x225_fullrun_session/prime_cli_surface.txt`
- **CLI drift note:** `artifacts/x225_fullrun/startup_checks/2026-02-18_124747Z_x225_fullrun_session/cli_drift.md`
- **Config parity proof:** `artifacts/x225_fullrun/config_diff.txt`
- **Launch artifact:** `artifacts/x225_fullrun/launch/launch_summary.json`

## X225 Full-Run Session (from approved x223 baseline)

- **Session timestamp (UTC):** 2026-02-18T14:43:02Z
- **Run ID:** `t7c3gjpoui57fs11ctzr7wzn`
- **Config:** `configs/lab/prime-td-macro-round-60-x225.toml`
- **Baseline source:** `configs/lab/prime-td-macro-round-60-x223.toml`
- **Startup checks:** `artifacts/x225_fullrun/startup_checks/2026-02-18_124747Z_x225_fullrun_session/prime_cli_surface.txt`
- **CLI drift:** no material drift (`prime 0.5.37`) relative to latest snapshot.
- **Config parity proof:** `artifacts/x225_fullrun/config_diff.txt` (behavior knobs frozen; only run `name` changed).

### Monitoring + Restarts

- Monitor log: `artifacts/x225_fullrun/monitor_status.log`.
- Sustained no-progress detected around step `6/7`; controlled restart protocol applied.
- Restart attempt 1 (`artifacts/x225_fullrun/restarts/restart_1_2026-02-18T132039Z.log`) was aborted by interactive confirmation prompt.
- Restart attempt 2 used non-interactive force (`prime rl restart -f`), resumed from checkpoint step `5`, and progression recovered.
- Final run status: `COMPLETED` (`Created 2026-02-18 12:56`, `Started 2026-02-18 13:23`, `Completed 2026-02-18 14:39`).

### Post-Completion Hygiene (strict)

- **Coverage:** sampled steps `0/10/20/30/40/50`, max pull limit (`-n 100`), all pages; coverage `100%` at each sampled step.
- **Parse volume:** `samples_total=24`, `turns_total=680`, `plan_turn_total=680`, `invalid_plan=0`.
- **Action mix + candidate pool + phase breakdown:**
  - `action_mix`: `build=228`, `upgrade=517`, `noop=615`
  - `candidate_pool`: `build=1758`, `upgrade=1296`, `noop=1360`
  - `phase_action.late`: `build=228`, `upgrade=517`, `noop=615`
- **Choose/index gate:** `choose_out_of_range=0`, `choose_off_by_one_clamped=0`, residual unclamped `0`.
- **Delta accounting:** non-cap `pass/fail/missing = 632/0/0`; cap `delta1/delta0/missing/other = 24/0/0/0`.
- **Reliability notes:** full-turn parsing complete, parse failures `0`, upload 500 count `0`, interleaving warnings `0`.
- **Verdicts:** reliability `diagnostic`, progression `PASS`, horizon lower-bound `>=60` (cap-hit `24/24`).
- **Evidence:** `artifacts/x225_fullrun/x225/analysis_summary.json`.

### Spend-Primary Metrics (active policy gate)

- `late_build_spend=45600.0`
- `late_upgrade_spend=66480.0`
- `late_upgrade_spend_lead_pct=45.7895%`
- Spend band distance from `25-45`: `0.7895pp` (high)
- `upgrade_to_build_spend_ratio=1.4579`
- Secondary trend only: `late_upgrade_count_lead_pct=126.7544%`
- Spend summary artifact: `artifacts/x225_fullrun/spend_backfill_x225_fullrun.json`.

### Transfer Gate (baseline-canonical)

- **Commands:**
  - `npm run benchmark:transfer:baseline -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400`
  - `npm run benchmark:transfer -- --pack core-v1 --seeds 1000:1049 --episodes 50 --max-steps 400 --baseline-canonical --out output/transfer/x225_fullrun.json --json`
- **Outcome:** `gate_status=pass`, `gate_reason="Transfer gate thresholds satisfied"`.
- **Evidence:** `artifacts/x225_fullrun/transfer_x225_fullrun.json`, `artifacts/x225_fullrun/transfer_baseline_core_v1.json`, `artifacts/x225_fullrun/transfer_command.log`.

### Decisions

- **FULL-RUN:** `GO` (run completed; hygiene quality gates passed).
- **DEPLOYMENT-READINESS:** `NO-GO`.
- **Deployment blocker:** spend-primary gate miss at end-of-run evidence (`45.7895%` > `45.0%`).
- **Minimum next corrective pair:**
  - `x226` control replicate of `x225`/`x223` behavior profile.
  - `x227` one-variable treatment from `x226`: `env.args.config.observation.candidate_balance.by_phase.late.min_build_frac = 0.745`.
- Decision artifact: `artifacts/x225_fullrun/final_decision.md`.

## X226 MAIN High-Batch Launch Record

- **Launched at (UTC):** 2026-02-18T15:04:59Z
- **Run ID:** `wy4fakzxk82dyh12htegffzq`
- **Config:** `configs/lab/prime-td-macro-round-60-x226.toml`
- **Effective total batch:** `4096` (`batch_size=4096`, `rollouts_per_example=1`)
- **Behavior baseline source:** `configs/lab/prime-td-macro-round-60-x225.toml` (x223/x225 policy profile frozen)
- **Startup checks:** `artifacts/x226_mainrun/startup_checks/2026-02-18_150356Z_x226_mainrun_session/prime_cli_surface.txt`
- **CLI drift note:** `artifacts/x226_mainrun/startup_checks/2026-02-18_150356Z_x226_mainrun_session/cli_drift.md`
- **Config parity/diff artifact:** `artifacts/x226_mainrun/config_diff.txt`
- **Launch artifact:** `artifacts/x226_mainrun/launch/launch_summary.json`

### X226 Hard Reset Record

- **Timestamp (UTC):** 2026-02-18T15:54:07Z
- Initial x226 run `wzf0usupuxfhxvlcm38wudew` remained stuck at step 0 (no sampled-step progress, stale progress timestamp) after controlled restart.
- Applied hard reset (`prime rl stop -f` + fresh relaunch of same config).
- **Superseded run:** `wzf0usupuxfhxvlcm38wudew`
- **Replacement run:** `wy4fakzxk82dyh12htegffzq`
- **Config (unchanged):** `configs/lab/prime-td-macro-round-60-x226.toml`
- **Effective total batch:** `4096`
- **Reset evidence:** artifacts/x226_mainrun/restarts/hard_reset_2026-02-18T155349Z.log

### X226 Fourth Fallback Scale Relaunch (active main run)

- **Timestamp (UTC):** 2026-02-20T00:18:52Z
- **Superseded fallback run:** `oxo75zj1idp1wu5wtckll8qc` (`512`) stalled for >5h at step 40 (`last_updated_at=2026-02-19T19:20:34.659094Z`), was restarted from checkpoint, then immediately failed (`Pod not found - run may have crashed or been deleted`) and was deleted.
- **Active run ID:** `ourjokrvb410zp5zknvyyz3j`
- **Config:** `configs/lab/prime-td-macro-round-60-x226u.toml`
- **Effective total batch:** `512` (`batch_size=512`, `rollouts_per_example=1`)
- **Scale/continuation reason:** `4096`, `2048`, and `1024` variants failed/stalled; `512` progressed to step 40 but restart terminated with pod-level failure, so run was relaunched as an exact `512` replicate with behavior knobs still frozen.
- **Observed warning note:** recurring `Cancelled X old rollout requests (will refill naturally)` was present before the stall; treated as queue/backpressure diagnostic, not by itself a hard failure.
- **Behavior parity proofs:** `artifacts/x226_mainrun/config_diff_fallback_x226r.txt`, `artifacts/x226_mainrun/config_diff_fallback_x226s.txt`, `artifacts/x226_mainrun/config_diff_fallback_x226t.txt`, `artifacts/x226_mainrun/config_diff_fallback_x226u.txt`.
- **Restart/delete evidence:** `artifacts/x226_mainrun/restarts/stall_probe_x226t_2026-02-20T0000Z.log`, `artifacts/x226_mainrun/restarts/restart_x226t_stall_2026-02-20T001605Z.log`, `artifacts/x226_mainrun/restarts/delete_superseded_512_oxo75zj1idp1wu5wtckll8qc_2026-02-20T0019Z.log`.
- **Launch artifact:** `artifacts/x226_mainrun/launch/launch_summary.json`.
- **Progress update (UTC 2026-02-20T12:35:46Z):** run `ourjokrvb410zp5zknvyyz3j` is still `RUNNING`; `latest_step=38`; sampled/distribution checkpoints currently at `0/10/20/30`; `last_updated_at=2026-02-20T12:33:08.975228+00:00`.
