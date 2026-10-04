# Tiny H2 replay of the readout layers (job 21024848)

Plumbing replay only: no catalyst result, no verdict, no new QE run.

| arm | XML exit | SCF converged | SCF cycles | first BFGS count | startup .bfgs deleted | user stop | PWSCF WALL s | process s | energies Ry (first 3) |
|---|---|---|---|---|---|---|---|---|---|
| continuous | 0 | 8/8 | [1, 2, 3, 4, 5, 6, 7] | [0] | False | False | 43.29 | 46.525 | -2.26460807, -2.31752826, -2.32232940 ... |
| candidate-stop | 255 | 1/1 | [1] | [0] | False | True | 9.88 | 11.189 | -2.26460807 ... |
| negative-fresh | 0 | 5/5 | [1, 2, 3, 4] | [0] | True | False | 25.09 | 26.403 | -2.31752826, -2.33231501, -2.33231890 ... |
| resumed | 0 | 7/7 | [2, 3, 4, 5, 6, 7] | [1] | False | False | 36.06 | 37.369 | -2.31752826, -2.32232940, -2.33111846 ... |

Scheduler: {"billing": "4", "charged_cpu_su_exact": 0.13777777777777778, "cputimeraw_su": 0.13777777777777778, "elapsed_s": 124, "exit": "2:0", "jobsu_minus_exact": -0.0001777777777777767, "jobsu_reported": 0.1376, "note": "scheduler FAILED 2:0 and scientific pass coexist in this historical job (OQ7)", "state": "FAILED"}

Mirror vs retained remote pins: {"remote_rows": 66, "matched": 66, "size_only_matched": 0, "mismatched": [], "not_mirrored": []}

Adapter re-derivation of candidate-stop: {"energy_Ry": -2.264608073934768, "error": null, "ok": true, "optimizer_counts": [0], "scf_counts": [1], "xml_exit_status": 255}

Energy trajectory: {"energy_only_within_tolerance": true, "max_abs_energy_difference_Ry": 1.3175088131589519e-08, "note": "positions and forces are compared by the frozen adapter (pa_tiny_raw_readout.py record), not re-derived here", "ordered_evaluations": [8, 8], "registered_tiny_energy_tolerance_Ry": 1e-06, "retained_pa_tiny_raw_readout_max_energy_Ry": 1.3175088131589519e-08, "tolerance_cite": "docs/research/pa-offline-restart-probe-2026-10-03.md:137 \"Proposed tiny-test tolerances, not production threshold changes\""}
