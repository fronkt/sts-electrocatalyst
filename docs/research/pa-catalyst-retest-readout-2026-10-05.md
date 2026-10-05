# Catalyst P-A re-test — terminal investigation, 2026-10-05

## Verdict and allocation

**Job 21075231 remains scientifically INCONCLUSIVE.** Its registered three-evaluation trajectory-continuity gate failed. Production acceptance, every-step P-A validation and terminal fresh acceptance remain false. No threshold or historical result is amended by this investigation.

The parent scheduler row is FAILED / 3:0. All four QE processes themselves returned zero and have validated numerical receipts. The wrapper exit follows the continuity refusal, rather than an MPI failure or timeout. The negative/reset control was after that gate and was not executed; no reseed arm was selected. Four of the maximum six permitted calls ran, with no automatic retry/requeue.

| Item | Terminal observation |
|---|---|
| Start / end, Anvil Eastern daylight time | Oct 5, 09:40:32 / 12:26:26 |
| Parent elapsed | 9,954 s = 2 h 45 m 54 s |
| Actual allocation | 1 whole node, 128 CPU/tasks, 200 GiB, billing128 |
| Parent CPUTimeRAW / allocation CPU SU | 1,274,112 s / **353.92 SU** |
| Prior estimate / approved hard ceiling | 275–543 SU / 2,048 SU and 16 h |
| Earlier job 21034683 | Separate FAILED3:0 / INCONCLUSIVE record; 102.8622 SU |
| New solver calls / jobs during this investigation | **0 / 0** |

Accounting uses the parent job once. Batch and extern rows are retained and are not summed into the allocation charge. The value is scheduler allocation CPU SU, rather than a separately obtained billing invoice.

Sources: [terminal accounting](../../results/pa_catalyst_retest_readout_2026-10-05/terminal_accounting.json), [fresh inventory and complete controller receipt](../../results/pa_catalyst_retest_readout_2026-10-05/terminal_inventory.json).

## Exact launch and preservation

The target is the existing Cu8Cr23Mn35Co34 seed20/site2 72-atom clean slab at the retained cycle-5 geometry. The implementation is the exact launched **c5b33c28bb09324d7decf5c2bb5f6100a877a366**, spec SHA256 **4c2384c6375f1c7892d33d8f6c37478243f41af3da9dd0f9ec507bcd8423e435**. Fresh terminal checks verify the same remote commit and all controller/adapter/contract/batch, deck/review, executable, UPF and original four-file seed pins.

Preservation includes **1,623 trial files** plus eight launch/source/scheduler files: **1,631 files and 76,112,065,809 logical bytes**. The complete independent Anvil archive is:

~~~text
/anvil/projects/x-che260157/sts_pa_catalyst_retest_2026-10-04/evidence_archive_21075231_2026-10-05
~~~

It contains 492 unique content files / 60,874,634,461 bytes, with every source and copied-content SHA256 verified. Full original names, sizes and metadata map to content hashes in raw_manifest.json. Content permissions are 0400 and archive directories 0500. Original trial outputs, checkpoints and checkout source files were only read.

The local scientific mirror independently verifies **1,098 files / 35,476,741 bytes**, including complete deciding logs, inputs, XML, process/setup/parsed receipts, checkpoint inventories, BFGS and electronic restart metadata. It is also retained as raw_small_v2.tar.gz for explicit-path Git backup. The optional complete Windows binary mirror was stopped after the complete Anvil archive verified; its verified and partial content files remain locally retained and are inventoried in storage_decision.json. Full binary local preservation is not claimed.

The remote archive manifest is LF; its byte hash is 910c79bca816c42e4ed20480b499b8d00d607eb0c7fecce26ee0cf0b8db9bfa4. The Windows raw_manifest.json has CRLF and SHA c707caea13fdfb49c72fb745c7b79827879607fad93fd95b84010c3c1e7575d5. Replacing only CRLF with LF gives the remote byte hash exactly; file-content pins and integer metadata are preserved.

Read-only collection refusals and offline-parser corrections remain separate in collection_refusals.json and analysis_refusals.json. The post-retention squeue “Invalid job id” response does not override the fresh terminal sacct row. The initial streaming tar compresslevel incompatibility with remote Python3.9 was handled by a separate gzip-wrapper collector. Neither event launched QE or changed trial evidence.

Sources: [raw manifest](../../results/pa_catalyst_retest_readout_2026-10-05/raw_manifest.json), [complete archive receipt](../../results/pa_catalyst_retest_readout_2026-10-05/anvil_archive_complete.json), [local small-mirror checks](../../results/pa_catalyst_retest_readout_2026-10-05/small_mirror_verified.json), [storage disposition](../../results/pa_catalyst_retest_readout_2026-10-05/storage_decision.json), [exact launch snapshots](../../results/pa_catalyst_retest_readout_2026-10-05/launch_snapshot/source_manifest.json).

## Where the registered comparison fails

The complete, ordered pairing is control evaluations1/2/3 against candidate evaluation1 and resumed evaluations2/3. Atoms are neither reordered nor aligned; no frame is discarded. Limits apply inclusively to absolute total-cell energy and maximum Cartesian position/force components across the matched ordered atoms.

| Global evaluation | Absolute ΔE, Ry; limit1e−6 | Max Δposition, bohr; limit1e−5 | Max Δforce, Ry/bohr; limit1e−5 | Registered result |
|---|---:|---:|---:|---|
| 1: control versus candidate | 2.00088834e−11 | 0 | 1.45027323e−10 | All pass |
| 2: control versus first resumed | 1.05242179e−7 | 1.45026657e−10 | **1.14642054e−4** | **Force fails** |
| 3: control versus second resumed | **5.04498985e−6** | **6.76788898e−5** | **6.99196884e−5** | **All three metrics fail** |

The error “all three ordered evaluations did not agree” means that the three evaluations did not all pass. It does not say all three individual frames failed.

The first failed comparison is **evaluation2, Co atom20, z force**:

- Control: −0.016696717618337235 Ry/bohr.
- Resumed: −0.016811359671995173 Ry/bohr.
- Difference: −1.1464205365793734e−4 Ry/bohr, **11.464 times** the force limit, approximately 0.002948 eV/angstrom.
- At this evaluation the largest position discrepancy is only1.45e−10 bohr and the energy difference passes. This localizes the failure to the electronic/force result at effectively the same geometry, before subsequent optimizer propagation.

At evaluation3, the largest position discrepancy is **O atom53 y**, 6.767888984e−5 bohr (3.5814e−5 angstrom); the largest force discrepancy is **Co atom21 z**, 6.99196884e−5 Ry/bohr. The total energy difference is about0.06864 meV/cell. These physically small absolute differences still fail the unchanged, strict numerical-continuity gate.

[Independent raw reconstruction](../../results/pa_catalyst_retest_readout_2026-10-05/independent_analysis.json) reproduces the deciding receipt differences exactly, without invoking the registered adapter parser. It parses all seven evaluated XML records, binds each to its own structure/energy/forces, checks atom indices and species, and verifies all complete stdout energy and72-atom force groups. Masked stdout/XML force differences and rounded energy differences are within5.1e−9 in their Ry units. Proposal/evaluation roles and fixed-coordinate flags are separately checked in independent review. There are132 movable and84 fixed Cartesian coordinates,44/28 atoms respectively.

## What the checkpoint evidence establishes

The operational consumption audit passed before the trajectory comparison. It records explicit file WFC/potential restart, same parallel/common XML identity, no startup optimizer reset or restart fallback, saved SCF/BFGS/GDIIS counters1/1/0 and resumed global SCF counters2/3 with BFGS counters1/2. First resumed geometry agrees with the candidate proposal.

The original controller's success-only final inventory scan was bypassed by the continuity exception. This investigation independently fills that verification gap: **all390 files**, their byte sizes/content hashes and directory inventory in both the candidate and immutable-candidate terminal trees exactly match the saved pre-fresh snapshot. Reconstructed tree SHA is dc3637bce66f8c9d85bd7d29f77af40810302650b8eed1f02bdf9de83c98a32c. Fresh scratch and resumed work therefore left the frozen candidate content intact.

Persistent checkpoint availability, exact copy and observed optimizer consumption are supported. The evidence does not establish equality of every continuous in-memory electronic state with restart initialization. That distinction is precisely why the separate numerical trajectory gate matters.

The checkpoint's128 .mix files are zero-length; their absence of substantive history is not missing-file evidence. The retained QE source deletes converged mixer history. Saved BFGS state is source-bound to the evaluated candidate geometry/gradient and nonzero next proposal.

## Fresh-reference branch

At the exact evaluated candidate geometry, the fresh calculation is approximately **0.14862 meV/cell higher** in energy than warm. The registered strict rule requires fresh to be more than10 meV/cell lower before an intentional reseed. RESUME_CANDIDATE was therefore the correct energy branch; this is separate from later continuity acceptance.

The fresh/warm maximum force spread at the same geometry is8.82133277420e−4 Ry/bohr at **Co atom23 z**, about0.02268 eV/angstrom. Near equality of total energies alone is insufficient to establish force equivalence or a common electronic basin. This observation supports explicitly validating force precision in any longer protocol, rather than assuming the energy branch rule supplies it.

## Confirmed solver-path difference and interpretation

The raw records establish a specific restart startup difference:

| Fact | Continuous evaluation2 | First resumed evaluation2 |
|---|---:|---:|
| Active SCF convergence target | 1e−6 Ry | 1e−6 Ry |
| First diagonalization ethr | **1e−6 Ry** | **1e−5 Ry** |
| SCF iterations | 12 | 12 |
| Final SCF error, Ry | 8.060441605e−7 | 8.991391391e−7 |
| Printed total/absolute magnetization | 50.24 /68.16 | 50.24 /68.16 |
| Next printed adaptive conv_thr | 8.35e−8 Ry | 8.41e−8 Ry |

Relevant raw locations: control/stdout.log:3663 and resumed/stdout.log:1041 for ethr; candidate/stdout.log:3662 for the clean stop at next SCF iteration0; immutable-candidate .restart_scf:1 for saved iter0/dr2=0/ethr1e−6. Resumed XML records diago_thr_init0 and the input explicitly requests file WFC and potential.

The exact retained official QE7.5 sources account for this startup behavior:

- restart_in_electrons.f90:33–40 takes the non-DMFT iter<1 branch without restoring saved dr2, ethr or eigenvalues; restoration is in the successful saved-iteration branch at54–56.
- setup.f90:423–437 initializes default file-potential SCF ethr to1e−5.
- run_pwscf.f90:320–334 performs post-move updates and sets continuous ethr to1e−6.
- init_run.f90:141–148 initializes eigenvalues/occupations to zero. The clean iteration0 restart does not restore saved eigenvalues through restart_in_electrons.
- move_ions.f90:243–248 changes the adaptive SCF threshold. input.f90 resets it from the deck; restart_in_electrons does not restore tr2.

These sources explain the observed startup-threshold difference. They do **not** prove that threshold alone caused the force failure. Other restart initialization, potential/density reconstruction, eigenvalue state and finite SCF convergence effects remain competing contributors. Initial candidate/control evaluation agreement makes independent first-run randomness a weak explanation for this particular failure. Parser conversion/masking/order explanations are weakened by independent complete raw reconstruction. A metastable-state jump, missing checkpoint or optimizer reset is not established.

All22 printed starting Hubbard trace records match the candidate's final records at displayed precision. Later printed traces differ slightly. This supports preserved initialization at that limited precision and an altered electronic path; rounded traces and magnetization cannot identify a basin or prove complete binary state equivalence.

**XML SCF-error units are role-specific.** Relaxation step scf_error is unscaled Ry in add_qexsd_step.f90:100–104, while fresh output convergence_info error is divided by2 in pw_restart_new.f90:311–319 and must be multiplied by2 to recover Ry. The fresh residual is9.80071310431723e−7 Ry. All corrected residuals match rounded stdout. Total energy/force Hartree-to-Ry conversion is separate and is verified independently.

Sources are retained under [qe_source](../../results/pa_catalyst_retest_readout_2026-10-05/qe_source/cached_source_pins.json), with official QEF/q-e qe-7.5 URLs, SHA256 and new-helper Git blob pins in retrieval*.json. Exact tagged-source URLs are [restart helper](https://raw.githubusercontent.com/QEF/q-e/qe-7.5/PW/src/restart_in_electrons.f90), [setup](https://raw.githubusercontent.com/QEF/q-e/qe-7.5/PW/src/setup.f90), [continuous driver](https://raw.githubusercontent.com/QEF/q-e/qe-7.5/PW/src/run_pwscf.f90).

## Scoped next work

1. Retain this registered failed continuity result and its exact evidence. Longer every-step/production acceptance stays unresolved.
2. Prepare a dated numerical diagnostic at the **first resumed evaluation and its fixed matched geometry**. Freeze the varied initialization controls and readouts before launch. Compare residual, all force components, electronic/Hubbard state and first diagonalization path. Explicitly matching startup ethr is one discriminating variable; isolate it before assuming a fix.
3. Define the complete policy for adaptive conv_thr and persistent versus reconstructed electronic state before every-step P-A. Counter continuity and nominal deck equality alone did not meet the current gate.
4. Independently price and review the exact diagnostic. Any new solver allocation needs its own estimate, hard ceiling and approval; this investigation licenses no further job. Preserve the original tolerance and report prospective protocol changes as new experiments.
5. Expand to a longer catalyst relaxation only after the intended numerical/electronic acceptance is demonstrated. Selection-relevant chains, adsorption references and melt ranking retain their own scientific gates.

The complete raw archive, independent comparisons and exact-source investigation are available for review. Causal attribution of the force discrepancy remains open. This outcome does not establish a catalyst ranking or support melt selection.
