# Ru pseudopotential control: reviewed readout — 2026-09-17

The twelve fixed-geometry GBRV Ru SCFs converged. Their projections also completed, but the launch validator rejected the nonmagnetic output format. Independent validation of the unchanged raw files resolves that parser defect without rerunning calculations or replacing the original twelve REJECTED receipts.

The primary quantity is **Q = 0.071583 V**, compared with the pre-stated ONCV value **0.092250 V**. Its **−20.667 meV** shift exceeds the frozen ±7.8 meV comparability band, while Q remains below 0.100 V. The pre-stated outcome is **MIDDLE**. Ru remains below the floor under both pseudopotential families, but its numerical margin depends on the pseudopotential. A7.3 remains **NOT MET at 3 of 6** and A6.3 remains **INVERTED**.

## Scientific results

The estimator, fixed U endpoints, gas references, vibrational corrections and outcome bands are the September 16 choices from docs/89 and `src/dft/ru_pp_readout.py`. No alternative seed, replacement output, equalised branch or additional U rung enters this readout.

| Quantity | GBRV result | Pre-stated comparison | Outcome |
|---|---:|---|---|
| Q = abs[c(0) − c(9)] / 2 | 0.071583 V | ONCV 0.092250 V; floor 0.100 V; shift tolerance ±0.0078 V | MIDDLE |
| η(Ru), U = 0 | 0.803848 V | ONCV 0.787 V; absolute shift 0.016848 V < 0.20 V | COMPARABLE |
| η(Ru), U = 6.73 | 0.419601 V | η(Ir, Xu anchor) − η(Ru) = +0.217399 V | Positive ordering reproduced; PROJECTOR-MISMATCHED |
| η(Ru), U = 9 | 0.336785 V | η(Ir) − η(Ru) = +0.417215 V > 0.36 V | Clears the measured error-class bound on one PP family |

The potential-limiting steps are 3, 3 and 2 at U = 0, 6.73 and 9 respectively. The U = 9 Ir–Ru ordering survives the family-matched control. It remains larger than the largest cell/coverage difference measured by this campaign. This supports the anchor-pair comparison within the stated protocol; it supplies no new material-performance claim.

The primary span needs only OH and OOH at U = 0 and 9. Gas, slab and fixed vibrational terms cancel in that endpoint difference. The three overpotentials use all four slab states and the banked H2/H2O references. The independent ONCV reconstruction gives Q = 0.09224816402274882 V, consistent with the rounded comparator fixed before the run.

## Why the original validator rejected all twelve projections

`research_batch.projection_check` required the sequence of all `Atom # N: total charge` lines to equal 1…nat. For these nonmagnetic QE 7.5 calculations, each atom appears on three adjacent rows: s, p and d. The sequences are 1,1,1,2,2,2,…; the repeated total charge is identical on each row. The banked Ru ONCV projection output already uses this format.

Every new Ru projection has one Lowdin block, ordered and complete s/p/d rows for every atom, one finite spilling parameter and one JOB DONE after the charge table. Atom counts are 18/19/20/21 for slab/O/OH/OOH, corresponding to 54/57/60/63 charge rows. Spilling parameters span 0.0017–0.0022. No severe numerical failure marker appears. Both SCF and projection process return codes were zero in all twelve original receipts, with no stop reason.

The shared validator in `src/dft/projection_qc.py` groups adjacent rows by atom, checks atom order and complete angular channels against the projection basis, checks equal repeated totals, and retains finite-value and severe-failure checks. It requires the order Lowdin → Spilling → JOB DONE. A partial single-channel atom cannot pass as a complete group; a combined spin-output row must contain every channel indicated by its basis. Unknown IEEE flags fail closed; underflow, denormal and inexact notices remain nonfatal.

## Evidence and status separation

The reviewed artifact is `results/research_readout_2026-09-17/ru_pp_reviewed_readout_2026-09-17.json`. It reports original strict scoreability **0/12** and independent reviewed scoreability **12/12**, with `REVIEWED_COMPLETE`. Original `.qc.json` and `.REJECTED` files retain their bytes and classification; original scheduler FAILED exits remain part of the record.

The additive helper `src/dft/ru_pp_projection_revalidation.py` requires:

- The exact original projection-format rejection, zero process return codes and no stop reason; any KILLED marker blocks review.
- Six raw artifact hashes per job matching `results/research_readout_2026-09-17/retrieval_initial.json`.
- The approved deck hash, exact ONCV-to-GBRV input substitution, only the allowed runtime path rewrites, the matching projection input and all pseudopotential hashes.
- Repeated SCF and force checks, complete finite projections, and every ONCV comparator row and gas reference passing its existing checks.
- Retained XML and density evidence in `retained_scratch_initial.json`, collected after the original runner stopped before its retention check. XML content hashes are recorded; density evidence establishes existence and size, not a density content hash.

The helper writes the separate dated artifact exclusively and refuses to overwrite a previous reviewed result. It never alters raw outputs, original receipts or the banked A0 readout.

The local launch runner now uses the shared projection validator for future jobs. A future specification must explicitly pin `src/dft/projection_qc.py`; preflight verifies both the staged file and the sibling source the runner executes. The historical launch specification is unchanged and cannot authorize this revision. The separately staged Anvil runner is unchanged; its exact source is retained in `results/research_readout_2026-09-17/original_research_batch.py`. The SCF parser is unchanged.

## Scope

Coordinates remain the ONCV-relaxed structures, and all calculations use the inherited nonmagnetic nspin = 1 protocol, 80/640 Ry cutoffs and 8×4×1 k-mesh. No Ru-specific cutoff ladder or GBRV-consistent relaxation has been added. Equal nominal U does not imply equal atomic projectors between the pseudopotentials. The U = 6.73 corroboration remains PROJECTOR-MISMATCHED. Lowdin populations are not compared across the two projection bases.

## Verification

**62 tests passed** in the Ru readout and projection-revalidation suites. The reviewed scorer independently accepted all twelve unchanged output sets. Tests cover both output formats, truncated and reordered atom/channel groups, inconsistent repeated totals, malformed/nonfinite values, severe flags, marker order, artifact changes, altered rejection reasons, missing retention and KILLED precedence.

```text
python -m pytest tests/test_ru_pp_projection_revalidation.py tests/test_ru_pp_readout.py -q
python src/dft/ru_pp_projection_revalidation.py --json results/research_readout_2026-09-17/ru_pp_reviewed_readout_2026-09-17.json
```

The second command records a new artifact only when that path does not exist. No DFT rerun is required to resolve this output-format defect.
