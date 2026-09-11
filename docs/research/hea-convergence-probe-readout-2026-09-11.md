# HEA capped convergence probes: readout, 2026-09-11

## Decision

The four probes tested their intended numerical controls and reached their prescribed stopping conditions, but none established a converged SCF endpoint. They are informative numerical rejections, not evidence of a new launcher or wrapper failure. Do not extend or repeat these four jobs unchanged. The next small experiment worth considering is one pull-baseline occupation-broadening probe, capped at 60 electronic iterations and one 128-core hour. Its purpose is diagnosis, not replacement of the original-width scientific result.

The precision arm did **not** hold the eigensolver threshold at `1e-10` throughout SCF. Both precision outputs show that value at iteration 1 and a looser value at iteration 2. Consequently, these probes do not rule out an eigensolver-accuracy contribution to the plateau.

This readout does not select candidates for a larger relaxation or ranking campaign. That expansion remains dependent on the ensemble/census readout. These two difficult electronic states are a bounded numerical question, separate from analysis of the eight accepted historical-winner audits.

## Evidence and controls

The completed array is `20563390`, tasks 1–4. Full outputs, histories, clone receipts, runtime inputs and QC reports are under [the probe run directory](../../runs/hea/convergence_probe_2026-09-10/). The [verified transfer inventory](../../results/hea_continuation_2026-09-11/collection_verified/transfers.json), timestamped `2026-09-11T19:40:07.883172+00:00`, records the mirrored bytes. Accounting is in [the collected accounting record](../../results/hea_continuation_2026-09-11/collection_verified/accounting.json). Initial inspection used the `2026-09-11T18:38:25.962408+00:00` status snapshot; every snapshot residual agrees with the subsequent full-output read.

An independent, file-only reparse of the raw outputs found zero discrepancies against the saved per-iteration residual, total magnetization, absolute magnetization and printed `ethr` fields. Each output SHA-256 also matches its `.history.json`. Only complete iterations enter the statistics below; an iteration that began before the CPU cap but lacks a residual is not counted. No new calculation, production-input change or checkpoint modification is part of this readout.

The [frozen launch specification](../../results/hea_convergence_probe_2026-09-10/launch_spec.json) defines these two states and two arms:

| Short name | Exact job suffix after `hp__` | Numerical arm |
|---|---|---|
| Builder precision | `leader_builder__ortho__recover_metal_alternating__precision` | `diago_thr_init=1e-10`, `diago_full_acc=.true.`; beta 0.1, default mixing history 8 |
| Pull precision | `leader_pull2.10__ortho__recover_baseline__precision` | Same precision settings |
| Builder mixing | `leader_builder__ortho__recover_metal_alternating__mixing` | `mixing_beta=0.05`, `mixing_ndim=12`; default diagonalization controls |
| Pull mixing | `leader_pull2.10__ortho__recover_baseline__mixing` | Same mixing settings |

All four use SCF at fixed geometry, `conv_thr=1e-6` Ry, local-TF mixing, MV broadening of 0.01 Ry, 80/640 Ry cutoffs, the original 4×2×1 mesh, 128 MPI ranks and eight pools. Each has `electron_maxstep=60`, `max_seconds=3300` and a one-hour Slurm limit. Each arm independently clones the same corresponding **original failed follow-up density**, as pinned by the [numerical source inventory](../../results/hea_numerical_2026-09-08/source_checkpoints.json); it does not continue the terminal density of the previous four-hour recovery. Startup is `from_scratch`, `startingpot='file'`, `startingwfc='atomic+random'`.

## Observed convergence

Residuals are the printed estimated SCF accuracy in Ry, not an independently established error bar on the final energy. None of the four traces ever falls below `1e-6` Ry.

| Probe / array task | Complete iterations | Minimum residual (iteration) | Final residual | Median first 10 → last 10 | Stop | Allocated core-h |
|---|---:|---:|---:|---:|---|---:|
| Builder precision / 1 | 56 | 3.154e-5 (4) | 1.7443e-4 | 1.3319e-4 → 1.99845e-4 | CPU cap during 57 | 118.649 |
| Pull precision / 2 | 59 | 7.6141e-4 (24) | 8.4734e-4 | 9.4280e-4 → 9.0330e-4 | CPU cap during 60 | 118.578 |
| Builder mixing / 3 | 60 | 2.019e-5 (5) | 1.9101e-4 | 2.5024e-4 → 1.8757e-4 | Iteration cap | 110.293 |
| Pull mixing / 4 | 60 | 6.109e-5 (59) | 3.127174e-2 | 1.050325e-3 → 8.22605e-4 | Iteration cap | 108.871 |

Total allocation use was **456.391 core-h**, against a 512 core-h ceiling, using elapsed seconds × 128 / 3600. All four scheduler states are `FAILED`, exit `16:0`; the underlying SCF processes returned zero after their orderly capped exits. The wrapper correctly rejected them, did not run projection, and retained the diagnostic history. `JOB DONE` or process exit zero is not scientific convergence.

The earlier [builder recovery](../../runs/hea/numerical_2026-09-08/hn__leader_builder__ortho__recover_metal_alternating.out) completed 261 iterations: minimum `3.059e-5` at iteration 4, final `1.3277e-4`, and median residual `1.5661e-4` over the first 30 versus `1.8122e-4` over the last 50. The earlier [pull recovery](../../runs/hea/numerical_2026-09-08/hn__leader_pull2.10__ortho__recover_baseline.out) completed 277: minimum `2.9564e-4` at iteration 210, final `8.6243e-4`, and corresponding medians `8.26255e-4` versus `9.1248e-4`. The new arms therefore reproduce approximately the same late residual scale. The lower isolated minima in the mixing arms do not constitute sustained convergence.

In particular, pull mixing goes from `6.109e-5` at iteration 59 to `3.127174e-2` at 60, a roughly 512-fold rebound. Pull precision spikes to `0.45849131` at iteration 54 before returning to its previous plateau. A long extension priced as steady exponential convergence would be unsupported.

## Eigensolver, spin and occupation evidence

The actual printed precision thresholds are:

| Precision probe | Iteration 1 `ethr` | Iteration 2 `ethr` | Late `ethr` | Earlier recovery's terminal `ethr` |
|---|---:|---:|---:|---:|
| Builder | 1e-10 | 3.81e-8 | 4.68e-9 | 4.54e-9 |
| Pull | 1e-10 | 1.60e-7 | 1.13e-7 | 4.39e-8 |

The tight initial solve costs about 35.1 and 38.8 average diagonalization iterations for builder and pull, respectively, versus 11.6 and 12.9 in the mixing arms' first solves. It does not impose a persistent threshold ceiling. QE documents `diago_thr_init` as the initial iterative-diagonalization control, with threshold adaptation during SCF; `diago_full_acc` makes empty states use the occupied-state accuracy. Neither should be interpreted here as proof of fixed `1e-10` accuracy. The raw threshold sequence is the decisive evidence for this run. [QE input reference](https://www.quantum-espresso.org/Doc/INPUT_PW.html)

Builder stays near total magnetization `0.06 μB` and absolute magnetization `58.53 μB`. Over the last 20 complete iterations, total magnetization spans `0.02–0.06` in precision and `0.04–0.06` in mixing; absolute magnetization prints as `58.53` throughout both windows. This is a stable global spin signature at the printed precision, not proof that every local moment or Hubbard occupation is unchanged.

Pull remains mostly near `38.00 μB` total and `66.18 μB` absolute magnetization, but its largest residual spikes coincide with spin changes. In precision, iteration 53 → 54 changes `(M, |M|)` from `(37.99, 66.19)` to `(38.75, 65.37)`, then iteration 55 returns to `(37.87, 66.32)`. In mixing, iteration 59 → 60 changes `(37.96, 66.20)` to `(38.15, 65.98)`. Earlier pull recovery also showed excursions: its final 50 iterations span `37.83–39.99 μB` total and `64.20–66.36 μB` absolute magnetization. These correlations indicate an electronically unstable trajectory; they do not establish a specific local spin flip or an accepted alternate branch.

**Occupation limitation:** every old recovery and new probe prints 23 Hubbard-site `Tr[ns]` blocks at startup and another 23 in iteration 1, but none in later iterations. The two arms' initial traces match exactly within each state. The largest printed per-spin trace change from startup to iteration 1 is only `0.00110` electron across the four probes. There is no late Hubbard occupation-matrix series or band/Fermi occupation series with which to identify the subsequent spikes. A retained terminal `occup.txt` is not a trajectory and cannot fill this gap.

There are no unconverged-eigenvector warnings or `IEEE_INVALID_FLAG` messages in these four raw outputs. Small negative-density reports remain: approximately `(0.0142, 0.0153)` for builder and `(0.0078, 0.0223)` for pull. These observations neither prove a discretization problem nor eliminate one. QE discusses finite-cutoff/augmentation effects as a possible convergence issue; the printed magnitudes alone are insufficient to diagnose it. [QE troubleshooting, §§5.0.0.20 and 5.0.0.24](https://www.quantum-espresso.org/Doc/pw_user_guide/node21.html)

## Checkpoint and scientific acceptance limits

Every `.probe.json` reports `scientific_status=REJECTED`, `diagnostic_status=CAPPED_NONCONVERGENCE`, valid diagnostic history and an empty `evidence_errors` list. Their retention check lists exactly 16 absent portable collected wavefunction files: `wfcup1..8.hdf5` and `wfcdw1..8.hdf5`. The four required density/XML/occupation/PAW files are not on that missing list.

This establishes that none is a complete portable final-wavefunction checkpoint suitable for accepted projection/postprocessing. It does **not** establish deleted files, an I/O failure, or whether every distributed restart artifact is present. The first scientific failure is SCF nonconvergence, already sufficient to reject the run; the missing portable wavefunctions are a separate limit on reuse. Do not attempt projection, assume `startingwfc='file'` is possible, or describe these endpoints as accepted energies. No old failed attempt changes status because its diagnostic offspring were useful.

## Proposed next diagnostic and stopping rules

The leading *testable hypothesis* for pull is instability associated with occupation rearrangement near the Fermi level, potentially coupled to spin/Hubbard-density mixing. QE describes abrupt residual rebounds as a reason to inspect metallic occupations and broadening. That qualitative resemblance, plus the measured spin excursions, motivates a test; it is not a causal identification. [QE troubleshooting, §5.0.0.20](https://www.quantum-espresso.org/Doc/pw_user_guide/node21.html)

The first new experiment should be **one** pull-baseline probe from a fresh independent copy of the original pinned failed-follow-up density, matching the completed pull-mixing arm except for MV `degauss=0.02` Ry instead of `0.01` Ry and an independently verified diagnostic-output setting if needed to expose late occupations. Keep `mixing_beta=0.05`, `mixing_ndim=12`, the same geometry, cutoffs, Hubbard model, k mesh, binaries and 128-rank/eight-pool layout. Do not combine this first test with added bands, new mixing parameters, a new eigensolver or altered spin constraints: that would obscure which change mattered. The existing calculation has 404 bands; empty-state sufficiency at the broader width must be checked rather than assumed.

The hard limit is **60 electronic iterations, `max_seconds=3300`, one Slurm hour and 128 core-h maximum**, with no automatic retries or extension. Preserve raw stdout/stderr and per-iteration residuals, `ethr`, total/absolute magnetization and available occupation evidence. Broader smearing changes the occupation/free-energy problem: success is not a same-width reproduction or an accepted original scientific endpoint. This baseline-density test is also distinct from the separate fragment-derived smearing endpoint with reproduced `IEEE_INVALID_FLAG`; it does not resolve or bypass that rejection.

Use the following prospective decision rules, fixed before any new launch:

- Stop at the first hard cap or any invalid numerical/startup/evidence condition. Do not loosen `conv_thr` to turn a plateau into success. Skip projection after failed SCF.
- At the cap, an isolated low residual followed by a rebound is a negative diagnostic, not a reason to continue. Consider any additional recovery allocation only if the final three complete, nonoverlapping ten-iteration windows have medians `m1`, `m2`, `m3` satisfying `m2 ≤ 0.8 m1`, `m3 ≤ 0.8 m2` and `m3 < 1e-4` Ry, with no residual in the final ten exceeding ten times the preceding ten-window median. A shorter trace cannot meet this continuation rule. These are compute-triage criteria, not scientific acceptance thresholds.
- If broader smearing yields finite clean SCF convergence and complete projection/checkpoint evidence, label it a broader-width diagnostic endpoint. A subsequent separately bounded return to `0.01` Ry, with global and site-resolved state checks, is required before accepting recovery of the original problem. A different magnetic branch remains a distinct result, not a repaired copy of the target state.
- If the broader-width probe also plateaus or spikes, stop that recovery line pending a more discriminating observation. A true sustained-eigensolver-accuracy test requires first verifying how the actual QE 7.5 build updates `ethr`; another initial-threshold-only run would not answer it. Builder's globally stable-spin plateau is not automatically the same mechanism as pull's and should not receive the pull remedy by default.

Confidence is high in the observed nonconvergence, cap behavior and precision-arm limitation. Confidence is moderate that the proposed broadening probe is informative, and low that the current evidence uniquely identifies the root numerical mechanism. The bounded probe must not displace the completed-result analysis or become an open-ended substitute for census-informed scientific prioritization.
