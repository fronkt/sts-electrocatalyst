# Stall-robust protocol arms — readout, 2026-09-25

Both arms of `lowtail-stall-robust-protocol-plan-2026-09-22.md` §3 have stopped. **Neither meets its pre-stated success reading.** No leg is licensed, the S8 hold is unchanged, and nothing here is a census result, an adsorption reference or a claim.

Sources:
- Arm B: `results/lowtail_low_state_restart_2026-09-22/fixedns/` (`readout.json`, `traces.json`).
- Arm A: `results/lowtail_low_state_restart_2026-09-22/checked2/`:
  - `readout.json`;
  - the mirrored `slab_c5low__checked.qc.json`;
  - the 85 segment and fresh-check files under `outputs/…/segments/`, with `mirror_manifest.json`. The stage collector expects the single-`.out` layout and marks those files absent, so they were mirrored separately by read-only SFTP.

All energies below are relative to step 1, E₁ = −7551.86633 Ry. The same geometry and seed gave the same value in both arms.

## Arm B — `slab_c5low__fixedns15`, array 20862631

- **Scheduler:** FAILED 10:0 after 17,817 s. Its six cycles converged in 3, 12, 44, 50, 51 and 50 SCF iterations.
- **Stop:** cycle 7 stopped at 126 iterations with a residual floor of 1.2e-7 Ry. Magnetization drifted from 50.24 to 49.88 during that cycle.
- **Energy and force by step:** energy 0, −25.1, −42.7, −61.3, −80.1, −94.0 meV; force 0.0477, 0.0323, 0.0267, 0.0234, 0.0257, 0.0286 Ry/bohr.
- **BFGS:** the step counter advanced 0→5 and the trust radius grew from 0.020 to 0.050 bohr.
- **Reading:** the stall is at the seventh step, the same step as array 20851756 without `mixing_fixed_ns`, so this **fails** the pre-stated reading. `mixing_fixed_ns = 15` does not move the stall.

## Arm A — `slab_c5low__checked`, array 20862968

- **Scheduler:** FAILED 10:0 after 115,537 s (32.1 h of the 72 h wall).
- **QC status:** `REJECTED`, with reason "segment 21 stopped: wall-time ceiling; fresh check: stopped: SCF iteration ceiling".
- **Counts:** 21 segments, 0 re-seeds.

| Step | Segment SCF iterations | ΔE (meV) | Total force (Ry/bohr) | Fresh check at 8.08e-8 | Fresh − segment (meV) |
|---:|---:|---:|---:|---|---:|
| 1 | 3 | 0.0 | 0.0477 | converged, 67 it | −0.01 |
| 2 | 12 | −25.4 | 0.0331 | converged | +0.01 |
| 3 | 12 | −39.1 | 0.0278 | converged | −0.04 |
| 4 | 12 | −49.1 | 0.0248 | converged | −0.06 |
| 5 | 12 | −57.2 | 0.0227 | converged | −0.10 |
| 6 | 12 | −64.0 | 0.0211 | converged | −0.12 |
| 7 | 12 | −70.0 | 0.0198 | converged | −0.13 |
| 8 | 12 | −75.3 | 0.0187 | converged | −0.14 |
| 9 | 11 | −80.0 | 0.0179 | converged, **higher state** | **+11.88** |
| 10 | 12 | −84.4 | 0.0170 | SCF ceiling (127) | — |
| 11 | 11 | −88.3 | 0.0163 | converged | −0.15 |
| 12 | 12 | −92.0 | 0.0157 | SCF ceiling | — |
| 13 | 11 | −95.4 | 0.0152 | converged | −0.14 |
| 14 | 11 | −98.6 | 0.0147 | converged (92 it) | −0.14 |
| 15 | 17 | −101.6 | 0.0143 | converged | −0.12 |
| 16 | 11 | −104.5 | 0.0140 | SCF ceiling | — |
| 17 | 11 | −107.2 | 0.0137 | converged, **higher state** | **+25.53** |
| 18 | 12 | −109.9 | 0.0136 | converged | −0.14 |
| 19 | 13 | −112.5 | 0.0137 | SCF ceiling | — |
| 20 | 13 | −115.3 | 0.0139 | SCF ceiling | — |
| 21 | 120, stopped at the 2 h segment wall, accuracy 8.3e-5 | — | — | SCF ceiling | — |

- **Pre-stated reading: fails.**
  - BFGS did not converge: the force at step 20 is 0.0139 against 0.002, with no downward trend over the last six steps.
  - Five of the 20 accepted steps have no fresh reference: steps 10, 12, 16, 19 and 20 stopped at the fresh check's SCF iteration ceiling.
  - Step 21's segment SCF stalled.
  - By the plan's §3 last paragraph, P-C is the next arm.
- **What the checks did show:**
  - Where a fresh check converged, it matched the segment within 0.15 meV in 13 of 15 cases.
  - In the other two cases the fresh start landed *above* the segment (+11.9 and +25.5 meV). A fresh start above the trajectory does not trigger a re-seed, so both steps were correctly accepted.
  - No fresh start ever found a state below the trajectory, so there was no drop larger than δ and no re-seed.
- **Atom 20:**
  - The spin-down diagonal moved smoothly from (0.321, 0.974, 0.139, 0.903, 0.408) at step 1 to (0.326, 0.973, 0.149, 0.914, 0.389) at step 21. It stayed in the low-state orientation throughout.
  - Segment and fresh diagonals agree to within 0.01 at every step, including the two higher-state fresh checks. The higher states found by those checks therefore do not differ in atom 20's orientation.

### Arm A's optimizer did not behave as BFGS

Every segment's output reports "number of bfgs steps = 0". The trust radius fell monotonically, from 0.0201 bohr (step 1) to 0.0170 (2), 0.0145 (3), 0.0056 (10) and 0.0044 (20). The `.bfgs` history file was carried into every segment (the QC `continuation.bfgs_history` field is set for segments 1–20).

In the same leg under Arm B, the counter advanced and the trust radius grew to 0.050 bohr. Per step, Arm A made about half of Arm B's energy progress: after six steps it was at −64.0 meV, against Arm B's −94.0.

The implementation note (plan §7) says QE's BFGS module continues its history from a carried `<prefix>.bfgs` file. These outputs do not show that. The history is at best partly used: each segment behaves as a first step with a shrinking trust radius.

So Arm A's failure to converge within 40 segments reflects this optimizer behaviour. It is not evidence against the P-A checking scheme. Any rerun of P-A first needs a verified way to carry BFGS state across processes, such as the `restart_mode = 'restart'` route the note set aside, tested offline on a small cell until the step counter advances.

## Cost

Arm A used 32.1 h at 128 ranks, about 4,100 SU. The balance on 2026-09-25 is 36,878.4 SU of 100,000.

## Open for the entrant

The plan names P-C (fresh-start SCF at every step, double cost) as the next arm if Arm A does not converge. The optimizer finding above offers a second option: repair P-A's BFGS carry-over and rerun it. Choosing between them, and any launch, needs a new dated line. Neither is started.
