# runs/probe_d02 — the amendment-2 delta = 0.02 A rerun of the Cr *OOH 2x1v Hessian

Built 2026-08-23 by `src/dft/build_hessian_pilot.py --delta 0.02 --out runs/probe_d02`
as the REGISTERED response to the delta = 0.01 A pilot's UNDERPOWERED verdict
(docs/43 amendment 2: "On an UNDERPOWERED verdict the state is re-run at delta = 0.02 A,
and the two delta values are reported together — agreement between them is itself
evidence that the harmonic regime holds, and disagreement is reported rather than
averaged").

Why a separate root: the builder writes `<--out>/Cr_hess/<same 19 filenames>`, so a
0.02 build under the default `--out runs/probe` would have overwritten the banked 0.01
decks and outputs. The builder's manifest writer hardcoded a `probe/` directory prefix
(only right for the default root); fixed the same day to follow `--out`, so the
manifest here reads `probe_d02/Cr_hess ...` and the driver runs THESE decks.

Everything else is identical to runs/probe/Cr_hess: same source relaxation
(runs/probe/Cr_cellsym/s0_OOH__2x1v_mir, final geometry, M = 23.0), same verbatim 1A
verdict string, same conv_thr 1.0d-10 / electron_maxstep 120 / nosym+noinv / 16 k /
nspin 2 / U. The reference deck is byte-identical to the 0.01 reference (verified by
`cmp`); only the 18 displaced decks differ, by +/-0.02 A instead of +/-0.01 A.

Launched 2026-08-23 on Anvil as job 20089685 (array 1-19%19, 20 ranks / -nk 4).
Score with `PYTHONPATH=src python src/dft/hessian_analyze.py runs/probe_d02/Cr_hess`;
the analyser reads delta from hess_manifest.json. Report next to the 0.01 result in
runs/probe/Cr_hess/hessian_analysis_2026-08-23.txt, per amendment 2.
