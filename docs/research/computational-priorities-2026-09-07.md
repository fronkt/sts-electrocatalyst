# Additional computational rigor assessment — 2026-09-07

Assessment only; no compute launched, live processes not rechecked, frozen protocols unchanged.

Protocol correction: docs/91 defines 103 manifests across 12 baseline, 36 alternate-model, 54 extended-decoration and one seven-endmember manifests. Baseline census is 144 sites and up to 1296 adsorbate relaxations. Its 1b is an O2-fragment diagnostic, not a complete bridge pathway. The handoff's 103 MPA baseline jobs and full two-pathway completion should not be treated as verified descriptions.

Priority recommendations:
1. Add a prospectively selected HEA DFT evaluation panel spanning actual winner, competitors, poor controls, intact and transferred states, multiple decorations and active metals. Keep audit cases separate from a representative held-out set. Split by composition/decoration, not adjacent trajectory frames. Report reaction-energy and force errors plus ranking flips; seven endmembers do not establish HEA transfer accuracy.
2. Add spin-basin controls to the decisive existing paired SCFs: alternative ferrimagnetic/AFM initializations and independently initialized fragment moments. Retain moments and occupations. Request forces on fixed geometries and use them to prioritize DFT relaxation. Equal-U projector pairs isolate specification sensitivity; they do not identify the physically correct projector/U combination.
3. Establish numerical convergence of reaction/branch differences on representative HEAs: SCF tolerance, cutoffs, k mesh, smearing, slab thickness, vacuum and dipole treatment. Separate coverage from lateral size. conv_thr is an SCF error estimate, not a guaranteed adsorption-energy error. Check units and actual force masks.
4. Complete atom/charge-balanced bridge pathways and surface regeneration before computing pathway limiting potentials. Use targeted DFT path/NEB checks only after stable endpoint validation. Geometric H transfer alone cannot distinguish real chemistry from surrogate failure.
5. Add active-phase tests: coverage and surface Pourbaix screening, competing oxide/oxyhydroxide structures, segregation and dissolution. Random decorations on imposed rutile do not establish its presence under operation. Bulk thermodynamic screens are triage, not proof of an operating surface.
6. Methods opportunity: test whether geometry integrity, DFT/ML force mismatch and model disagreement identify consequential errors on held-out cases better than convergence-only, geometry-only and disagreement-only baselines. Report precision/recall, selective risk versus retained coverage, ranking error and DFT cost saved. Generic ensembles/fine-tuning are already prior art.
7. Keep current frozen census intact. For future acceleration, benchmark identical-weight float64 GPU inference against CPU energies, forces and endpoint basin identity before migration; measure complete-chain throughput. Future candidate selection should retain unresolved ties, site-integrity prevalence and stability, not force a winner from a noisy minimum.

Primary sources checked:
- https://arxiv.org/abs/2601.21056 (preprint, selective-U training pathology; does not establish its cause in these specific rutile cases)
- https://arxiv.org/abs/2605.09394 (preprint, catalysis fine-tuning prior art)
- https://www.nature.com/articles/s41524-025-01905-x (heterogeneous ensemble uncertainty prior art)
- https://onlinelibrary.wiley.com/doi/10.1002/anie.202201146 (HEO bridge-pathway prior art)
- https://www.quantum-espresso.org/Doc/INPUT_PW.html (spin, forces, convergence controls)
- https://www.nature.com/articles/s41467-025-65626-x (Co-Cr spinel reconstruction/dissolution; motivates tests, not direct evidence for these rutile candidates)
- https://www.societyforscience.org/regeneron-sts/judging-and-awards/ (holistic selection; no defensible placement probabilities from project anecdotes)

Review: checked against docs/91 and docs/92 and project lessons; recommendations distinguish established protocol risks from proposed extensions. No numerical results or placement estimates generated. This note does not replace the registered protocols or historical records.
