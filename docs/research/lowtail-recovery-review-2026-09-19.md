# Independent Cr clean-slab recovery review — 2026-09-19

This reviews the existing [stall diagnosis](lowtail-clean-slab-scf-stall-2026-09-19.md) and six unrun recipe decks. It does not authorize or submit a calculation. Original task 1 remains KILLED. The raw slab SHA-256 is `f1900fbe3c0e7359de9259860540a5faa2ab46a56c25008cb488e5edb4ebd24c`; the terminal mirror and remote scratch inventory are in `results/lowtail_dft_2026-09-18/interim_20260919/terminal_mirror.json`.

## Verified numerical diagnosis

The fifth SCF cycle has 126 completed residual records, followed by the header beginning iteration 127 and a shutdown message referring back to iteration 126. The old trace counted both the unfinished header and that shutdown message, producing 128. The corrected trace reports completed and started counts separately and binds each residual to its actual iteration.

The active target is 8.08e-8 Ry, announced at raw-output line 13479, versus the input value of 1e-6. The fifth-cycle minimum is 3.6e-7 at iteration 93. Of 126 residuals, 101 are below 1e-6, first at iteration 25; none reaches the active target. Iterations 41–126 span 3.6e-7 to 1.5e-6 Ry, with nine values above 4.5e-7, not merely one excursion outside that narrower band. The registered supervisor stopped correctly. Four converged SCFs and three BFGS steps do not complete the relaxation.

The preceding gradient error is 0.016 Ry/bohr, versus the 0.002 force criterion. This establishes remaining force error, not a fraction of the optimization completed or a forecast of remaining runtime. No stopped-cycle energy enters an accepted result.

## What the existing six recipes would measure

The prepared SCFs retain the original clean-slab coordinates and `conv_thr=1e-6`. For Cu8 this repeats a geometry that already converged in the first cycle; the observed failure occurred after ionic motion. These jobs therefore test initial-geometry recipe behavior, not the failing geometry. Because an SCF exits at its first threshold crossing, its minimum reported residual is not a measured accuracy floor. A job targeting 1e-6 cannot systematically establish the proposed go/no-go requirement of reaching 1e-8.

Do not use those six outcomes to choose a relaxed-state accuracy rule, and do not infer an acceptable `upscale` from a finite trajectory's observed minimum. Lowering `upscale` would loosen the effective electronic convergence rule and needs explicit numerical force-accuracy validation as a separate scientific change.

A focused prospective alternative is one fixed-geometry diagnostic at the exact coordinates entering Cu8 cycle 5, targeting 8.08e-8 Ry with local-TF beta 0.10, unchanged physical parameters, a 126-iteration stop and a two-hour wall cap at 128 ranks. It would test a proposed numerical remedy; it would not constitute a recovered slab minimum. Its electronic start must be explicit. No such job is launched by this review.

## Checkpoint viability

The new remote inventory provides substantially stronger evidence than the printed XML/density message:

- All 128 nonempty distributed wavefunction files are present, numbered 1–128, totaling 15,070,248,960 bytes.
- Restart-SCF and restart-k each have an unnumbered file plus numbered files 2–128, all 20,346 bytes. This is consistent with a master-file plus worker-file layout.
- A 1,351,591-byte BFGS file and 16,862-byte update file are present.
- Density, schema XML, PAW and occupation files exist. Of 128 mixing files, 16 are nonempty and 112 are empty; emptiness alone does not establish corruption in distributed storage.

This is a plausible restart checkpoint, not a verified portable start. The inventory supplies names and sizes, not binary checksums or successful restore evidence. A clean-exit restart must use the same parallelization; a future recovery would need an independent scratch copy, preserved original bytes, exact binary/deck identity and a startup read check. Resetting iteration accounting must never conceal that the original cycle exhausted its registered budget. [QE restart documentation](https://www.quantum-espresso.org/Doc/INPUT_PW.html).

## Hubbard evidence is insufficient to diagnose a limit cycle

The output contains ten occupation snapshots, each covering 22 Hubbard atoms: initial occupations; iterations 1 and final-converged for cycles 1–4; and iteration 1 of cycle 5. The final snapshot begins at raw line 13580. There are **no printed occupation matrices during the failed cycle's late plateau**. Comparing cycle 4's final snapshot with cycle 5's first snapshot mixes an ionic geometry change with an electronic update; it cannot demonstrate late-cycle occupation flipping. Rounded net magnetization also cannot discriminate among charge mixing, local occupation or near-Fermi-state mechanisms.

The seven pending primary legs retain their frozen inputs. The existing launch policy requires a separate dated decision for recovery; preparation and review do not silently extend the original nine-leg launch. A failed clean-slab reference keeps the corresponding lift MACE-referenced and provisional.

## Verification

`src/dft/qe_relax_trace.py` now distinguishes completed residual records from begun iterations. Three focused regressions in `tests/test_qe_relax_trace.py` cover exit-message double counting, an unfinished iteration, residual-to-iteration alignment and separate cycles. Those regressions passed within the 44-test focused suite. All four byte-matched raw outputs were reprocessed into `results/lowtail_dft_2026-09-18/slab_stall_review_2026-09-19/`; the original traces remain unchanged. Completed residual trajectories match the previous extraction. No DFT job was launched.
