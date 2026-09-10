# HEA DFT failure repair assessment — 2026-09-10

This assessment separates scheduler state from scientific acceptance. Original attempts, acceptance criteria, and cluster jobs are unchanged.

## Confirmed output-handling repair

The follow-up runner already accepts either nonempty `charge-density.dat` or `charge-density.hdf5`. Twelve valid follow-up SCF/projection results were recovered and hash-verified without rerunning DFT. Their historical Slurm FAILED labels remain intact. Two other follow-up attempts genuinely failed to converge, using 940.373 core-hours.

## Current cluster evidence

Read-only `sacct` and SFTP inspection confirms:

| Job | Scheduler outcome | Allocated seconds × CPUs | Evidence |
|---|---|---|---|
| 20543029_1 | COMPLETED | 1226 × 128 | Diagnostic says CLEAN_REPRODUCTION, new endpoint COMPLETE, complete rank capture, no invalid ranks, complete retention. Prior flagged attempt is not reclassified. |
| 20543035_1 through _5 | COMPLETED | 2077, 2010, 1773, 1755, 2063 seconds × 128 | Scheduler completion verified; full independent scientific readout remains outstanding. |
| 20543035_6 | FAILED, exit 16 | 2206 × 128 = 78.4356 core-hours | `hs__leader_pull2.10__ortho__smearing.scf_qc.json` rejects `IEEE_INVALID_FLAG`. Raw output contains the flag after JOB DONE. |

The newest failed sensitivity calculation is not another density-file mismatch or a time-limit failure. Its force audit reports a converged finite SCF, but the stricter complete QC correctly rejects the invalid-operation flag. Projection did not run through this runner's exit-16 path. Footer placement cannot identify the operation that set the flag. The successful atomic diagnostic is encouraging but does not prove that the earlier exception was harmless or establish its root cause.

Remote evidence paths are under `/anvil/projects/x-che260157/sts/runs/hea/`: `ieee_2026-09-09/hd__leader_builder__atomic__ieee_repro.{diagnostic,rank_audit,qc}.json` and `sensitivity_2026-09-09/hs__leader_pull2.10__ortho__smearing.{out,scf_qc.json}`. The bounded local access receipts are `C:/Users/frank/AppData/Local/Temp/sts-dft-repair-20260910.log` and `sts-dft-repair-detail-20260910.log`.

## Recovery sequence

1. Validate the clean atomic diagnostic against its frozen inputs, raw output/projection, checkpoint lineage and matching atomic partner; retain it as a separate attempt. Do not silently promote or overwrite the original rejected result.
2. Apply the existing per-rank diagnostic approach to the exact failed smearing endpoint, with a separate destination and preserved source checkpoint. A clean repeat is a new result, not an explanation of an intermittent flag. If reproduced, locate the offending operation with a diagnostic build before changing production numerical settings or acceptance rules.
3. Inspect the residual, energy and magnetic-state histories of the two repeatedly nonconvergent ortho states before selecting a bounded solver-control experiment. Repeating their previous four-hour settings already failed. Any numerical stabilization that changes smearing or the final electronic state requires a matched endpoint comparison and return to the target settings before scientific acceptance.
4. Keep cost accounting split into scheduler failure, recovered valid result, nonconvergence and exception rejection. A Slurm FAILED total is not a wasted-compute total.

No new scientific implementation defect was established by this assessment. No DFT retry or new allocation was submitted. A successful repair of the remaining scientific failures is not yet demonstrated.

## Verification

The existing follow-up shell, follow-up QC, and sensitivity shell regression suites passed together (`python -m pytest -q tests/test_hea_followup_shell.py tests/test_hea_followup_qc.py tests/test_hea_sensitivity_shell.py`, exit 0). The isolated worker verified `Codex_STS_Background`; completion is recorded in `C:/Users/frank/AppData/Local/Temp/sts-dft-repair-tests-20260910.status.json`. These checks exercise the existing retention fix and rejection paths; they do not establish convergence of the remaining scientific attempts.
