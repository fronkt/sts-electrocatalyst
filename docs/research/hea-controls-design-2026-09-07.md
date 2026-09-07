# HEA companion spin and numerical controls — 2026-09-07

The retained branch panel has four endpoints suitable for comparing electronic-state and numerical sensitivity while the MACE census continues. This companion arm has 48 fixed-geometry SCFs, with no submitted jobs. Its manifest retains the existing submitter's NOT LICENSED notice. The original 22-deck arm and its scientific record remain separate.

| Control | Geometries | Projectors | SCFs |
|---|---|---|---:|
| Exact baseline with explicit forces | Four branch endpoints | atomic, ortho-atomic | 8 |
| Alternating metal starts | Four endpoints | both | 8 |
| Polarized fragment O | Three detached-fragment endpoints | both | 6 |
| Alternating metal + polarized fragment O | Three detached-fragment endpoints | both | 6 |
| Five one-setting numerical perturbations | Both leader endpoints | both | 20 |

Baseline forces were already enabled: the existing template has tprnfor = .true. This flag requests forces in an SCF. The description of that flag as inert alongside ionic-relaxation settings in docs/92 section 3 is incorrect. The companion baseline changes only its prefix and resides in its own directory.

For alternating metal starts, selected elements' atoms receive positive/negative starts in retained atom-index order. The banked Anvil PWSCF v7.5 binary reports ntypx=10 (runs/a0/cell/ref__2x1v__u715.out:23). One species slot is reserved for fragment O in both metal modes, so the metal texture matches across paired modes. At most three eligible metals split, in alphabetical order: Co/Cr/Fe on equiatomic (Ni remains positive), and Cr/Mn/Ni on leader (its single Cu remains positive). Where needed, labels such as Cr1/Cr2 refer to the same mass and pseudopotential, and each split label receives its own identical U value. This is a deterministic AFM-like or ferrimagnetic trial texture, not an established magnetic order or a guarantee of zero total moment.

Fragment starts separate slab O1 from appended adsorbate O2, indices 72 and 73. For the O UPF's six valence electrons, starting polarization 1/12 on each fragment O corresponds nominally to 1 muB across the two O atoms in HO2, and 1/6 corresponds to 2 muB in O2. H is initially unpolarized. These are unconstrained starting guesses; their final local moments must be measured. In transferred-H states, H74 belongs to the slab chemically and must be reported separately from the O2 fragment. Same-element species splitting and fractional spin initialization follow the [QE input documentation](https://www.quantum-espresso.org/Doc/INPUT_PW.html).

Each numerical variant changes one setting from baseline: conv_thr 1e-6 to 1e-8 Ry, ecutwfc 80 to 100 Ry, ecutrho 640 to 800 Ry, k mesh 4x2x1 to 6x3x1, or degauss 0.01 to 0.005 Ry. The two cutoff changes are separate. A joint tighter-setting calculation is still required before claiming a combined numerical error bound. Both leader endpoints receive every variant, allowing comparisons of E(B)-E(A), rather than inferring cancellation from one absolute total energy. Cell, vacuum, slab thickness, adsorbate coverage, charge, U and projector remain fixed within each pair.

All outcomes should retain energies, SCF residuals and iteration counts, forces, total/absolute magnetization, per-atom Lowdin moments, and Hubbard occupation matrices. Compare branch gaps only between matching variants/projectors with converged endpoints. If a numerical perturbation changes the electronic basin, report mixed numerical and electronic-state sensitivity. Do not classify that difference as a clean numerical error estimate. There is no new pass/fail threshold and no ranking, eta, kinetic, or magnetic-ground-state conclusion from unrun decks.

Commands from the repository root:

~~~text
python src/dft/build_hea_controls.py
python src/dft/build_hea_controls.py --check
python -m pytest tests/test_hea_controls.py tests/test_hea_panel.py -q
~~~

Artifacts: runs/hea/controls_2026-09-07/*.in, requests.json in that directory, and runs/hea/m_controls_2026-09-07.txt. Each request includes exact species/spin mapping, source JSON path and geometry pointer, geometry-export and source hashes, deck MD5/SHA256, and required readouts. The builder validates every source through the original panel collector, requires LF bytes, preflights all destinations before writing, refuses different existing content, and requires the complete artifact set for --check.

Each request carries a per-deck estimate from hea_cost_model.py, using original element counts and the actual k mesh/pool count. Wavefunction and dense-grid point counts are scaled as cutoff^(3/2); the larger factor scales the wall estimate. These are explicit extrapolations: extra split-species overhead and tighter-SCF iteration counts remain uncalibrated. Requests include planning/model-B core-hours and memory estimates, plus a 3x memory scenario against the 237 GB node. The 3x wall and core-hour figures are monitoring triggers, not enforced caps or confidence bounds. The proposed inherited stop rule is wall beyond 3x that deck’s planning wall, or more than 126 SCF iterations without convergence, with a KILLED sidecar and no restart ladder. No watchdog is implemented here; the deck settings max_seconds=165000 and electron_maxstep=300 and scheduler 48-hour wall limit are separate backstops. The 48-hour allocation cap would total 294,912 core-hours if all 48 jobs exhausted it; that cap is not a forecast or a spending authorization. Additional spin textures, opposite fragment orientation, combined numerical settings, slab/vacuum/dipole tests, and paired size/coverage controls remain subsequent experiments.

A separate runs/hea/m_controls_2026-09-07_smoke.txt names exactly two jobs: hc__leader_builder__atomic__baseline and hc__leader_pull2.10__atomic__baseline. If the arm is later launched, measure those with concurrency one before expanding. Confirm observed per-process and total memory, SCF time, force output, local moments and occupations; the 3x memory scenario may exceed the node even when the planning estimate fits. The full list is a prepared experiment menu, not a request to queue every job at once.

For force diagnostics use src/dft/hea_force_audit.py after outputs are available; it is a separate readout and does not alter existing panel scoring.

The 6x3 k-point jobs explicitly use nk=4 (32 ranks/pool) instead of the baseline nk=8. At nk=16, the banked model predicts 247.216 GB, beyond the 237 GB node; at nk=4 it predicts 185.412 GB using the same model. The physical 6x3 mesh is retained. This decomposition choice is part of the request metadata and manifest, and the current comparison measures mesh plus decomposition sensitivity. Match the baseline at nk=4 before tight numerical certification, or if evidence shows decomposition sensitivity.

The eight companion baselines are exact equivalents of the original branch-panel decks except prefix. Each request links the original deck, output and Lowdin path, with original MD5/SHA256 and a shared prefix-normalized hash. Run each baseline once across both arms. Prefer an existing converged original with matching input hash, JOB DONE, forces and required local-moment/occupation records; otherwise choose one location before submission. If the companion ran first, omit the original equivalent and retain the companion output path in the readout. A failed attempt is retained as failed rather than silently retried under the other name. Omit reused baselines from any submitted subset and subtract their costs when estimating incremental spend. The 48-deck full manifest is the reviewable experiment menu; the duplicate resolution occurs before any later licensed subset is submitted.

Example force readout after a companion output lands (substitute the original input/output paths together when reusing that baseline):

~~~text
python src/dft/hea_force_audit.py --input runs/hea/controls_2026-09-07/hc__leader_builder__atomic__baseline.in --output runs/hea/controls_2026-09-07/hc__leader_builder__atomic__baseline.out --json results/hea_controls_readout/leader_builder_atomic_baseline_forces.json
~~~

The force-audit default 0.05 eV/angstrom is a diagnostic stationarity threshold, not a calibrated model-accuracy criterion. Missing outputs remain PENDING.
