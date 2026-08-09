# Blocking findings — 1A-cellsym

Verbatim from the 2026-08-09 adversarial review (6 verifiers, 31 blocking,
all six verdicts FIX_FIRST). Numbering is global across all three lanes.

## [1] src/dft/build_cellsym_pilot.py:49
**lens:** computational-catalysis referee: does the deck measure what it claims to measure

**Problem.** The `*O` state is excluded from the factorial (docstring lines 49-52: "*O has no orientational degree of freedom ... so it cannot populate the symmetry arm"; enforced at lines 535 and 560, which loop over `s0_OH` and `s0_OOH` only). docs/43-prereg-week1-factorial.md, the Zenodo-deposited pre-registration written the same day and explicitly closed to edits, overrides exactly this omission by name: "**States: `*O`, `*OH`, `*OOH` — not `*OH` and `*OOH` alone.** The plan as drafted omitted `*O`, and that omission would have made the block unable to answer its own question ... **Ru `*O` is the open question** — it has never been tested, and it is the only state that can move Ru's descriptor." The stated physical reason is also false by the builder's own construction: a single O cannot be yawed, but it can be translated off the mirror plane, and `kick_y()` (line 289) plus `SPECTATOR_KICK_A = 0.35` (line 237) is exactly that operation, already applied to the 2x1o spectator and already accepted by the `dy >= 0.30` guard at line 401.

**Why it ruins the result.** Without dG_O in the 2x1 cells, no overpotential can be computed in the candidate production cell for ANY of the three metals: dG2 = dG_O - dG_OH and dG3 = dG_OOH - dG_O both require it. Cr is pls=2 (dG2) and Ir/Ru are pls=3 (dG3). So docs/43 P12's primary bin boundary, |Deta| >= 0.10 V, is uncomputable, the NEGLIGIBLE bin (which requires BOTH |Deta| < 0.03 V AND |Dc_M| < 0.05 eV) can never be assigned, and tier_v3 cannot be built from this block. Only Dc_M = D(dG_OOH - dG_OH) survives. The pilot would spend 34 relaxations and ~1200-3000 job-hours answering a question docs/43 already declared insufficient, and the one quantity Ru's entire six-closed-negatives descriptor deficit lives in (dG_O - dG_OH = 1.163 eV vs a 1.60 apex) would go untested in the new cell. It is also a documented departure from a deposited pre-registration, which a hostile referee will read as the ranking being tuned after the fact.

**Proposed fix.** Add `s0_O` to both loops. Off-plane treatment for `*O` is a y-translation, not a yaw: reuse `kick_y(ads, SPECTATOR_KICK_A)` (>= 0.30 A clears the existing guard) plus nosym/noinv. Needed cells: 1x1/off x 3 metals, 2x1v/mir x 3, 2x1v/off x 3 (the 2x1o arm degenerates for *O to a replicated 1 ML *O cell and can be dropped or kept as a second GATE-C-style control), plus one `s0_O__1x1_k8` SCF for Cr. That is ~10 relaxations + 1 SCF. They are the cheapest jobs in the block: Cr `s0_O` converged in 12 ionic steps at 1x1 (runs/Cr_slab/s0_O.out) against 44 for *OH and 82 for *OOH. If *O is deliberately kept out, that decision must be written into a dated docs/43 addendum with the reason, before launch.

---

## [2] src/dft/build_cellsym_pilot.py:560
**lens:** computational-catalysis referee: does the deck measure what it claims to measure

**Problem.** The ionic-step counts driving every cost number are assumed BELOW the measured 1x1 values, in a cell with twice as many free atoms and a spliced half-and-half start. Line 560 assumes 40 steps for 2x1 *OH and 55 for 2x1 *OOH; line 535 assumes 25 and 45 for the new 1x1 off rows. Measured from the production outputs (count of `Total force` blocks): Cr s0_OOH = 82, Cr s0_OH = 44, Ru s0_OOH = 68, Ir s0_OOH = 60, Ir s0_OOH__yaw90 (1x1, off-plane) = 54. The 2x1 cells have 22 free atoms against 11, so BFGS runs in twice the dimension from a geometry whose two halves come from different relaxations. CELL_MULT_36 = 4.0 (line 447) is explicitly the floor of a 4-8 bracket, and the headline table quotes the floor. Compounding: there is no wall cap anywhere. `nstep = 200` is hardcoded in probe_decks.py:297, no `max_seconds` is emitted, and queue_r1.sh:47 runs bare `mpirun` with no `timeout`.

**Why it ruins the result.** Re-costing Cr `s0_OOH__2x1v_off` with the measured 82 steps instead of 55, at the same CELL_MULT = 4.0: 16 kpt x 82 x 48.6 s x 1.93 x 4.0 = 137 h, not the 91.7 h in the manifest; at the CELL_MULT = 6 that the measured basis-size ratios actually imply (I confirmed 2.000x bands and 2.000x G-vectors on the sibling lane's live Cr headers, so the O(N_b^2*N_pw) subspace rotation is 8x while the FFT term is 4x), it is 205 h, and at 100-130 steps (the realistic 2x1 count) 250-330 h. That is 10-14 days on one job. Four such jobs exist. With nstep = 200 and no cap, the worst case is not a bad estimate, it is an unbounded job: 200 steps x 16 kpt x 48.6 x 1.93 x 6 = 500 h, ~3 weeks, holding a box the whole time and returning nothing scoreable. tasks/plan-maximal-rigor.md:119 budgets this block at "~2 box-days on 8 boxes"; the critical path is one job, so no amount of concurrency reaches that, and the block silently slips out of Week 1. Hard rule 6 and tasks/lessons.md ("Compute estimates keep coming in low, and always for the same reason", three consecutive 2.4-3.5x misses) name this exact failure.

**Proposed fix.** Three things. (1) Re-quote the table with steps taken from the measured 1x1 counts (Cr *OOH 82, Cr *OH 44, Ru *OOH 68, Ir *OOH 60/54) and with CELL_MULT = 6 as the headline and 8 as the ceiling; state the measured basis for each. (2) Emit `max_seconds` in the four Cr 2x1 off decks and the two Cr 2x1 mir *OOH decks, sized to a real budget (e.g. 160000 s). pw.x then writes `Begin final coordinates` and exits cleanly and the run is restartable from a real geometry. (3) Because pw.x prints `JOB DONE` on a max_seconds exit and queue_r1.sh:33 SKIPs any job whose .out contains `JOB DONE`, a capped job must be gated on `bfgs converged`, not on JOB DONE, before it is scored or re-queued. Also give the Cr 2x1 jobs NP=8 or NP=12 (both exact multiples of nk in {2,4}) on a dedicated box; at NP=8 with -nk 4 the FFT grid splits across 2 ranks per pool, which halves wall-clock and per-rank memory at once.

---

## [3] src/dft/build_cellsym_pilot.py:122
**lens:** computational-catalysis referee: does the deck measure what it claims to measure

**Problem.** The Cr arm has no magnetic-basin control. The docstring's magnetic section (lines 122-130) correctly forbids startingpot/startingwfc and uses fresh atomic superposition, but nothing in the design, the manifest (runs/probe/m_cellsym.txt) or the report provides the GATE-1 check that docs/43 P12 makes a precondition of the readout: "let dE_sym = E(off-plane, **GATE-1-passed**) - E(mirror, **GATE-1-passed**)". GATE 1 is the fixed-geometry fresh SCF at the converged geometry that catches multistable SCF solutions. There are 8 new Cr adslab relaxations plus 2 Cr references, all nspin=2 + U(Cr-3d)=3.7, all in a cell with 12 Cr instead of 6, and not one of them has a companion SCF or a declared magnetisation check.

**Why it ruins the result.** The measured drifts from this exact failure mode are the same size as the effect being measured. docs/41 s6d/s6f: Cr *OOH -175 meV, Ni *OH -176 meV, Co *OH -405 meV, Co clean slab +59 meV, against an Ir symmetry escape of -291 meV. docs/41 s6e's own table: "Every magnetic 3d endmember except Mn carries at least one multistable state." A basin flip between the Cr mirror run and the Cr off-plane run is numerically indistinguishable from dE_sym in the output, produces no SCF_FAIL, no force anomaly and no QC refusal, and would be read straight into P12's TRAPPED bin. Doubling the cell makes it worse, not better: the 2x1 admits antiferromagnetic orderings along [001] that the 1x1 could not represent, and the FM start (starting_magnetization = 0.6 on all Cr) gives the SCF a new way to land somewhere the 1x1 reference never could. GATE C as designed (|E(2x1 clean) - 2*E(1x1 clean)| <= 5 meV) is an energy-only test and can be passed by a different magnetic state at near-degeneracy.

**Proposed fix.** Two parts, both cheap. (a) Free: make total and absolute magnetisation a recorded, compared quantity for every Cr job. pw.x prints it every SCF iteration; require that the mir and off members of each Cr pair agree to within 0.1 mu_B (the same tolerance docs/43 s3 already uses for the Hessian magnetic guard) and that E(ref__2x1v) matches 2*E(slab__1x1_k8) in magnetisation as well as energy before GATE C is called passed. (b) ~10 fixed-geometry SCFs, queued as a second wave once the Cr relaxations converge: one per Cr 2x1 relaxation at its own final coordinates, fresh density, identical settings, and require agreement to <= 5 meV. At 16 kpt x 3 steps x 48.6 x 1.93 x 4-6 that is 1.7-2.5 h each, ~25 h total against a >600 h Cr arm. Pre-register the exclusion rule now, not after the numbers exist.

---

## [4] src/dft/build_cellsym_pilot.py:441
**lens:** Adversarial pre-launch verification of block 1A-cellsym: will pw.x accept these 

**Problem.** MAG_MULT = 1.93 is derived from a mismatched comparator pair. The comment cites "Ru slab 2902 s at 32 kpt (90.7 s/kpt)" -- that number is `probe/Ru/slab__dipole` (a dipole-perturbed SCF, the slowest Ru slab in the archive), not a base SCF. `probe/Ru/slab__base` from the SAME queue wave (NP=4, NCONC=3, runs/probe/queue_scf.log) is 1742 s = 54.4 s/kpt. Same-wave, same-variant, Cr-vs-Ru pairs from that log give: slab 187.1/54.4 = 3.44, s0_OH 258.5/63.9 = 4.05, s0_OOH 245.9/64.1 = 3.84, s0_O 200.2/67.3 = 2.97 (mean 3.58). Even the builder's own Mn numerator against the correct denominator gives 175.0/54.4 = 3.22. The value used, 1.93, is below every like-for-like measurement available.

**Why it ruins the result.** Cr carries 15 of the 37 jobs and 595 of the 1161 quoted wall-hours -- 51% of the pilot. Understating the magnetic penalty by 1.85x understates the whole block: total goes 1161 -> 1690 job-hours at the builder's own CELL_MULT, box-hours 232 -> 338, and the longest single job 91.7 -> 163.5 h. This is precisely the failure lessons.md logs three times ("compute estimates keep coming in low"), and here it is a selected minimum, not an honest bracket.

**Proposed fix.** Set MAG_MULT = 3.5 from `probe/Cr/*__base` / `probe/Ru/*__base` in runs/probe/queue_scf.log (Cr-specific, four independent state pairs, same wave, same NP/NCONC), fix the comment to name the base runs, and re-emit the manifest table and the cost paragraph.

---

## [5] src/dft/build_cellsym_pilot.py:447
**lens:** Adversarial pre-launch verification of block 1A-cellsym: will pw.x accept these 

**Problem.** CELL_MULT_36 = 4.0 is published as "my model uses 4.0 -- the floor" and every headline number ($25, 232 box-h, 91.7 h longest job) is quoted at that floor. I measured the basis sizes first-hand by running the actual decks on the box: Cr 1x1 s0_OH = 98 bands / 297,421 smooth G / 841,263 dense; Cr 2x1o s0_OH = 196 bands / 594,817 / 1,682,519 (exactly 2.000x and 2.000x, FFT dims (32,72,270)->(64,72,270)). Davidson's FFT/H|psi> term scales as nbnd*Npw*log(Npw) = 4.1x, but the subspace-rotation ZGEMM (nbnd^2*Npw) and the subspace diagonalisation (nbnd^3) both scale 8x, and at nbnd ~ 100-200 with 300-670k plane waves those terms are comparable to the FFT term, not negligible. The honest mid-point is 5-6, not 4. Combined with the MAG_MULT error the plan number is off by 2-3x.

**Why it ruins the result.** Every downstream scheduling decision -- how many boxes to rent, whether 1A lands inside Week 1, whether block 2A can "Read 1A" -- is taken against the floor. Corrected: total 1690-3315 job-hours, 338-663 box-hours, $36-72 (vs $25). The 4 h I had for a smoke test could not close this (my 55 s probes never reached SCF iteration 1 on a 36-40 atom cell), so it stays an estimate -- but a floor must not be presented as the model.

**Proposed fix.** Quote CELL_MULT = 5.5 as the planning number and 8.0 as the ceiling, with 4.0 labelled as the floor it is. Better and cheap: measure it -- run Cr `s0_OH__1x1_k8` and Cr `s0_OH__2x1o_mir` at identical NP/nk for ~15 min each and take the ratio of the "total cpu time spent up to now" increments per SCF iteration per k-point. 15 min is the minimum useful window; 55 s is not enough to reach iteration 1.

---

## [6] runs/probe/m_cellsym.txt:2
**lens:** Adversarial pre-launch verification of block 1A-cellsym: will pw.x accept these 

**Problem.** The manifest is a single file at one NP, and the header pins NP=4. At NP=4 the critical path is ONE job: Cr `s0_OOH__2x1v_off` / `s0_OOH__2x1o_off` at 91.7 h on the builder's floor, 163.5 h with MAG_MULT corrected, 234-340 h at CELL_MULT 5.5-8.0 -- i.e. 4 to 14 days for a single job. Ten of the fifteen Cr jobs exceed 60 h under the corrected model. tasks/plan-maximal-rigor.md gives block 1A "~2 box-days on 8 boxes" and marks it critical path, with Week 2's block 2A defined as "Read 1A". Renting more boxes cannot shorten a single job.

**Why it ruins the result.** The block's whole purpose is to freeze the production cell before Week 2 commits to it. If the answer lands in week 3, either 2A commits the cell without 1A, or the campaign slips. The total throughput is fine (338-663 box-hours packs into 42-83 h wall on 8 boxes); it is entirely the Cr tail that breaks it, and the manifest as written cannot express a different NP for those lines.

**Proposed fix.** Split into two manifests: the 22 Ir/Ru jobs plus the 3 Cr SCFs at NP=4/NCONC=5, and the ~12 Cr 2x1 jobs at NP=16 or NP=20 with NCONC=1, one job per box (both 16 and 20 are exact multiples of nk in {2,4}, so hard rule 4 still holds). Order the Cr off-plane jobs first, not last. Re-quote the wall clock against the corrected per-job hours before renting.

---

## [7] src/dft/build_cellsym_pilot.py:162
**lens:** Adversarial pre-launch verification of block 1A-cellsym: will pw.x accept these 

**Problem.** The pre-registration says of the 2x1o spectator "the interaction term is unaffected either way". That is false as built. The reference does cancel from the symmetry effect S(c) = E(c,off) - E(c,mir) -- that part of the argument is correct. But line 577 (`spec = spec_mir if sym == "mir" else spec_off`) gives the 2x1o *off* deck a spectator *O kicked 0.35 A off the mirror plane plus nosym, while the 2x1o *mir* deck pins the spectator on the plane and lets pw.x symmetrise it; the 2x1v arm has no spectator at all. So S(2x1o) contains the spectator's own off-plane relaxation energy and S(2x1v) does not, and the pilot's headline number -- the cell x symmetry interaction, S(2x1o) - S(2x1v) -- inherits it. There is no `ref__2x1o_mir` anywhere in the 37-line manifest, so that contamination cannot be measured after the fact.

**Why it ruins the result.** The interaction term is the entire reason this is a crossed design rather than two experiments (module docstring lines 13-23). If ref__2x1o's spectator settles off-plane, the headline number is a sum of the effect being measured and an unquantified nuisance term, and the only honest options left are to re-run or to report it as uninterpretable. The pilot's own physics argument (docstring line 49: *O has no orientational degree of freedom) predicts the term is ~0 -- but that prediction is exactly what the pilot exists to stop assuming.

**Proposed fix.** Either (a) drop the kick from the two 2x1o *adslab* off decks and keep it only in `ref__2x1o` -- with the working adsorbate yawed and nosym set, the cell has no mirror and the spectator already feels a non-zero F_y, so it is free without being pushed differently between arms; or (b) pre-register NOW, before launch, that if ref__2x1o's spectator relaxes to |dy| > 0.02 A a `ref__2x1o_mir` job (~13 h Ir/Ru, ~45 h Cr corrected) is added before the interaction is scored. Adding it after reading the result is post-hoc and breaks the pre-registration discipline docs/39 was built on.

---

## [8] src/dft/queue_r1.sh:33
**lens:** Adversarial pre-launch verification of block 1A-cellsym: will pw.x accept these 

**Problem.** Two compounding operational holes, both already burned this project. (1) No deck carries `max_seconds`, and write_probe hardcodes `nstep = 200` (probe_decks.py:297). The 2x1 relaxations are assumed at 40/55 ionic steps but have 22 free atoms instead of 11 plus a deliberately perturbed spectator; the 1x1 archive already spans 23-82 steps. A Cr 2x1 job that walks to nstep=200 burns 200/55 x 234 h ~ 850 h -- more than the entire pilot's quoted budget -- and pw.x prints `JOB DONE` on nstep exhaustion (hard rule 3). (2) queue_r1.sh line 33 then SKIPs that job forever on any re-queue, because its `.out` contains `JOB DONE`. Verified on the box: /workspace/sts/runs/probe/{Cr,Ir,Ru}_cellsym do not exist (checked 2026-08-09 18:14 UTC), and line 32's `cd "$dir" || { echo NODIR; return 2; }` does not abort the driver -- launching today writes 37 NODIR lines and QUEUE_ALL_DONE inside one second, which reads exactly like a completed wave.

**Why it ruins the result.** Failure mode (1) silently consumes weeks of box time and produces a non-stationary geometry that the log records as rc=0 JOB_DONE=1 SCF_FAIL=0. Failure mode (2) makes that state permanent. Failure mode (3), the missing directories, means the launch can appear to succeed while doing nothing at all.

**Proposed fix.** Before launch: rsync the three dirs to /workspace/sts/runs/probe/ and md5-verify; add a pre-flight loop over the manifest that aborts if any `$RUNS/$d/$job$suf` is missing. In the decks: add `max_seconds` to &CONTROL at ~2x the corrected per-job estimate (pw.x stops cleanly and restartably; it is not in _CHECK_KEYS or _FORBIDDEN so the guard will accept it). At scoring time: gate on `bfgs converged`, never on `JOB DONE`, and delete the `.out` before any re-run.

---

