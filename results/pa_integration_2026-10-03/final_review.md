# Independent final review — 2026-10-03

GO — scoped offline extraction and P-A contract only

## Evidence reviewed

- Rehashed the four pinned S29420/S29447 main/SI binaries and four pinned reading transcriptions; all matched `extraction_verification.json`. The original ACS DOCX OOXML matched its pinned SHA-256 `747609f8359e6087eb946eb08c8ad9aa9df2f5938a3f98bc38b70412abd9c4f2`.
- The primary passages support the model, method, reference, and pathway claims. S29420’s main text reports the AEM pair 0.59/0.75 eV at theoretical U=1.23 V; Fig. S5 separately reports 0.56/0.73 eV. Both remain verbatim reported quantities, with no recalculation or preferred pair. S29447’s main text explicitly assigns the U=0 V vs RHE maximum among ΔG1–ΔG4 to each site’s limiting potential; this is not an activation barrier or a newly derived eta.
- Original Table S3 OOXML contains 63 rows including its header, with 10 cells per row and no merge/grid-span markers. All 62 data rows match the CSV’s 10 source fields in original order; endpoint labels and blank surface numbers are preserved. No values were recalculated or ranked.
- Frozen contract SHA-256 `67412c8363877f0a6407e382a4d3c33c6c0f6dac7b1f5de3e3968bf77755ae39` and test SHA-256 `7ab803c0838c0b65bfc3a1520aa65f9bd7845ed62b2d448921574408d21cca6d` match the final `compute_tests.json` receipt. Final checks report 83 evidence tests with zero failures/errors; 330 compute tests and 7 subtests passed, with one symlink fixture skipped because Windows could not create it. The retained initial failure receipt remains separate.
- `package_verification.json` reports no errors and matching before/after pins for 9,791 tracked files and 21 unrelated untracked files. It also records zero canonical screening/checklist changes, no new paid API calls, and no new QE/Slurm jobs.

## Contract assessment and limits

The module is an offline supplied-evidence audit/oracle. It does not launch QE or mutate scratch, and every result has `production_accepted=false` and `real_catalyst_test_pending=true`. It distinguishes evaluated geometry from the next proposal; binds the fresh check to the same evaluated geometry and separate scratch; inventories recursive outdir and optional distinct WFC trees; applies the strict, one-sided >10 meV/cell reseed rule; holds failed fresh checks; reseeds stalled warm evaluations only from a clean fresh reference; enforces segment/reseed caps; and checks terminal evaluated energy/force evidence plus nonzero, exact resume counters and no startup reset/fallback. The normalized fixed flags use 1=fixed/0=free; conversion from QE `if_pos` is explicitly assigned to a future adapter.

The contract validates supplied receipts and manifest consistency; it does not itself establish that their source paths, hashes, geometry, units, constraints, UPFs, settings, or QE log observations match raw runtime files. Those checks, the full adapter, and real runtime/source review remain pending. The platform-dependent symlink guard also needs execution on a platform that supports the fixture. No real catalyst reseed branch is evidenced unless a future fresh test actually finds a >10 meV/cell lower state.

The 128-core/16-hour/2,048-SU proposal with at most six sequential invocations of at most two hours is explicitly not approved or submitted. Its numerical experiment checks fresh-SCF interposition at the first evaluated boundary only; controls are not accepted production P-A steps. Full every-step checks, terminal fresh acceptance, and actual catalyst adapter/restart behavior remain unvalidated. The historical H2 Slurm outcome `FAILED2:0` remains preserved; its scientific result supports QE restart plumbing only.
