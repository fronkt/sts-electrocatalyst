# Technical review of the current STS electrocatalyst campaign — 2026-09-05

This is a technical assessment and refinement of the existing project, not an STS research
report, a new registration, an elected threshold, or a replacement claim sentence. The starting
snapshot is branch `r0-catalysis-revival`, commit `0ea1363`. Read the current dated additions in
`tasks/todo.md`, docs/43, and docs/45 before the historical README. The thermal branch and early
rutile rankings are historical context.

The strongest path toward the original goal is to connect the existing DFT failure analysis to a
prospective materials decision. At present the project demonstrates consequential specification
and convergence problems. It has not established a more accurate functional, nor a melt that
outperforms an iridium electrode. A useful improvement would make a previously unreliable
decision demonstrably more reliable on new surfaces or new melts.

## 1. What the current evidence supports

| Component | Evidence in this repository | Scientific limit |
|---|---|---|
| DFT reference repair | docs/30–41: SCF failures, chemically wrong adsorbates, magnetic traps, constraint and symmetry problems were found and repaired | Numerical convergence alone is insufficient; model disagreement cannot automatically be blamed on the ML model |
| Symmetry and stationarity | docs/49, docs/56, docs/45: displaced-mode and escape calculations, fresh-density checks, and larger-cell comparisons | An adsorbate-block Hessian tests that block, not every possible full-slab instability |
| Projector sensitivity | docs/83: metal-dependent paired changes at U=7.50 eV in 1×1; docs/84: Cr at U=7.15 eV in 2×1v | Changing projector at fixed U changes the method; the larger or smaller answer is not automatically more accurate |
| Adopted-cell Cr comparison | `docs/figs/pproj_cell_readout.json`: nominal paired difference +0.1725164 V; 1×1 companion +0.4868562 V | Fixed-geometry, one-material comparison; model-phase values are not candidate activity predictions |
| Alloy screen | `results/r4_gated.json`: 12 compositions, six without a desorption flag on the selected chain, three decorations and 12 sampled sites per composition | Minimum site overpotential is a motif-search statistic, not electrode current; oxide structure is a model of a possible surface |
| Stability annotation | `src/dft/pourbaix_multi.py`, `results/r4_gated.json` | Equilibrium soluble-cation fraction at specified concentration/potential/pH is not dissolution rate, retained mass, or measured lifetime |
| Deliverable | QC and analysis tooling is substantial; current task record identifies the remaining silentgate core and control runs | Review tooling and a registered specification do not demonstrate that an absent core works |

The ordinary DFT hypothesis is also narrower than some wording in the record: CHE selects the
**potential-limiting step**, the largest reaction free-energy increment. It does not identify a
kinetic rate-determining step or prove a reaction mechanism without kinetic evidence. Use the
former term in future technical descriptions; preserve historical registered text with dated
clarifications where necessary.

## 2. A concrete correction from this review

The continuous robustness claim in docs/84 was inferred from a 3×3×3 grid. Such a grid contains
27 sample points; a three-dimensional cube has eight vertices. Paired agreement at sampled points does not in general prove agreement throughout the box
when the limiting steps change across those points. In contrast, vertex checks can prove that
one fixed step dominates throughout a box, because its differences from competitors are affine.

For the banked Cr 2×1v comparison at U=7.15 eV, apply the **same** additive changes to both sets
of adsorption free energies, in OH/O/OOH order:

`(-0.0525, +0.0525, 0.0000) eV`.

The atomic calculation then has potential-limiting step 1 and the orthogonalized calculation
step 2. Their difference is +0.1756950 V. This point is inside the ±0.10, ±0.15 and ±0.30 eV
boxes for which the grid had found zero disagreements. The two switching surfaces are close,
but distinct: disagreement occurs when

`0.154321333835 < delta_O - 2*delta_OH < 0.160820093150 eV`

within the tested domain. Along `delta=(-t,+t,0)`, that interval is
`0.051440444612 < t < 0.053606697717 eV`.

This corrects the broad robustness prose, **not the nominal A13 result**. The entire ±0.05 eV
shared-correction box still has pair (1,1) and constant difference +0.1725164 V. In each of the
±0.10, ±0.15 and ±0.30 eV boxes, the continuous difference spans approximately
[+0.1725164, +0.1790151] V. Thus the magnitude is stable under this particular stress test even
though the paired step identity is not.

The supporting implementation in `src/dft/che_box_robustness.py` enumerates the 16 possible
active-step pairs and solves their linear constraints over the continuous box. It reports
extremal differences and explicit witness corrections, distinguishes ties from strict
step assignments, and states solver tolerances. This is an exhaustive piecewise-linear
formulation evaluated numerically, not a claim of symbolic or arbitrary-precision proof.

The reproduction script, `src/dft/che_robustness_case_study.py`, ties the analysis to hashes of
the banked input and implementation, retains the original nominal values, and exports a JSON
audit and a figure. It does not change the registered scorer or its stored result. The supporting
ZPE decomposition script now also uses continuous bounds, so rerunning the older analysis
cannot silently repeat the grid-as-proof mistake.

This is useful supporting software, not a claim that linear programming is a new algorithm.
It is a sensitivity calculation, not a confidence interval. Shared correction errors are
appropriate for a shared constants table. Surface-specific vibrational or solvation errors
need additional independent/correlated degrees of freedom; this three-variable calculation
does not certify those errors, U uncertainty, electronic branch uncertainty, or phase identity.

## 3. What “better DFT” should mean in this project

The existing work establishes failures of specification and validation. The next step should
measure whether a repair changes **predictive validity** on independent data. A new functional
would require a substantially different validation case. A reproducible, better-tested DFT
workflow is already a meaningful deliverable.

**Preserve the existing paired controls.** Fixed-geometry, fixed-U projector comparisons answer
whether an often omitted specification changes the answer. They should remain paired controls.
Add a separate accuracy study if the aim is to recommend a production protocol; do not alter the
old comparison until it answers a different question.

**Evaluate complete protocols on a small, physically relevant benchmark.** Compare an explicit
baseline with the proposed repaired protocol using the same validation targets and failures
included. The repaired workflow should carry pseudopotential checksum, projector definition,
U provenance, spin initialization/search, coverage, cell, constraints, solvent/reference
convention, convergence checks, and unresolved alternatives. Test independent structures or
composition families. Adjacent frames from one relaxation belong in one data split.

**Treat self-consistency precisely.** The current Cr bulk response values discussed in docs/80
were one-shot linear-response results near U=0, not a converged U-in/U-out cycle. Iterating U,
electronic density and structure is an established method, not a new invention; projector
self-consistency also has prior art. If tested here, compare the full protocol and convergence
history, rather than selecting whichever U puts a candidate near a volcano optimum.
([Timrov et al., 2021](https://arxiv.org/abs/2011.03271);
[O'Regan et al., 2010](https://arxiv.org/abs/1004.4813).)

**Validate the actual active phase before expanding the screen.** For alkaline Ni–Fe–Co
precursors, test representative oxyhydroxide motifs with plausible Fe sites, hydration and
coverage alongside the rutile proxy. Where phase identity is uncertain, retain multiple
structural hypotheses. A low energy from a model-phase endmember does not choose the structure
of the real activated electrode. Separate site-specific U values within a documented functional
from casually mixing total energies obtained under incompatible functionals.

**Spend new calculations on decisions that could change.** High-value examples are a held-out
oxyhydroxide adsorption chain, relaxation under both candidate protocols, a competing magnetic
basin, or an explicit hydration configuration that reverses the candidate ordering. More digits
on a well-converged reference are lower priority when surface identity is still unknown.
Use BEEF ensembles for the uncertainty they actually sample; they cannot stand in for missing
structures, kinetics, solvent states or magnetic basins.

**Proposed falsification test:** freeze a baseline and a repair policy using the current
calibration data, then compare error and candidate ordering on held-out physically relevant
cases. Keep a simple baseline, a repaired-DFT-only baseline, and the ML-assisted workflow.
If the repair improves internal repeatability but not external agreement or held-out decisions,
report that limit. The number of passing QC checks is not itself evidence of higher accuracy.

## 4. The most promising extension of the existing discovery work

The question worth testing is whether an uncertainty-aware description of the **activated
surface** predicts sustained performance across new precursor compositions better than bulk
composition and best-site rutile screening do. This is a refinement of the original
make–measure loop, with a measurable bridge between the two halves.

The general concepts already have close precedents. Luan et al. tracked Cantor-alloy surface
and subsurface evolution and connected Cr loss and Mn redistribution to deterioration.
([ACS Catalysis, 2024](https://pubs.acs.org/doi/10.1021/acscatal.4c02792).)
That observation concerns the studied Cantor alloy and cycling conditions; it does not
establish a universal rule that Cr or Mn must be excluded.
Zhao et al. used batch-alloy targeting for HEA electrocatalyst discovery.
([Science Advances, 2025](https://doi.org/10.1126/sciadv.adx6121).)
Therefore neither “an alloy reconstructs” nor “screen an alloy and melt it” is enough to
establish novelty here. The proposed contribution is a prospectively tested improvement in
the predictive connection, with explicit ablations and a failure criterion. This is a novelty
direction, not a completed novelty proof.

Three refinements have especially good scientific value:

| Refinement | New comparison | What would defeat the proposed explanation? |
|---|---|---|
| Surface identity and precursor memory | Predict post-activation surface chemistry and sustained OER behavior from precursor composition; compare with composition-only and rutile-only baselines on held-out melts | Different precursors converge to similar active surfaces and the surface-aware prediction has no added out-of-sample value |
| Useful reconstruction versus transient corrosion | Relate activation, oxygen production, dissolved metals, and later activity using matched preparation | An apparent gain vanishes after activation, mostly reflects area change, or accompanies continuing loss without improved sustained oxygen production |
| Reliable discovery under model disagreement | Compare choices from a single favorable DFT setup with choices that remain competitive across justified protocols and surface hypotheses | The robust choice performs no better than the simple baseline or abstains so often that it has little practical value |

Best-site screening needs particular care. The pure endmember may legitimately have one
symmetry-equivalent site type, while the alloy has many different environments. Repeating the
pure site 12 times would not create 12 independent observations. Instead, retain every site's
chemistry and occurrence weight, retain rejected sites, and distinguish a rare favorable motif
from its contribution to an electrode. Activity models using probabilities of local
configurations have precedent in HEA **ORR**, which is methodological context rather than
validation for this OER system.
([Batchelor et al., 2019, accepted manuscript](https://backend.orbit.dtu.dk/ws/files/171279899/Joule_accepted_manuscript.pdf).)

A site free-energy minimum cannot simply be averaged or Boltzmann-weighted into an OER current.
That requires a justified kinetic and coverage model. Initially compare empirical summaries
and a calibrated surface model against measured behavior, without representing a thermodynamic
descriptor as a predicted current density.

## 5. Candidate experiments: diagnostic mixtures, not claimed winners

The current data cannot honestly certify a melt as better than iridium. Even the legacy
minimum-energy sites often center on Cr, while the real surface and Cr retention remain
questions. The high equilibrium soluble fraction for the old Ni31Cr29Cu5Mn35 lead is a reason
to test its fate, not evidence that exactly that percentage will disappear experimentally.

For planning with the existing FWM route, the following nominal atomic-percent panel would
test interpretable substitutions. These fractions are **proposed design points**; they are
neither optimized recipes nor validated candidate rankings. No melt order is issued here.

| Nominal at.% | Experimental role |
|---|---|
| Ni75Fe25 | Binary precursor baseline; distinct from the separately prepared NiFe oxyhydroxide/LDH electrode benchmark |
| Ni60Fe25Co15 | Replace Ni by Co at fixed Fe; tests whether Co adds value under the chosen preparation |
| Ni50Fe25Co15Mn10 | Replace 10 at.% Ni by Mn at fixed Fe and Co |
| Ni40Fe25Co15Mn20 | Extend the same Mn substitution, exposing an activation–retention trade-off if one exists |
| Fe25Co25Ni25Cr25 | Historical screen link; a deliberately different composition, **not** an isolated Cr ablation |

This panel tests substitutions, not an abstract “entropy effect.” It changes composition and
possibly microstructure; it cannot assign a benefit uniquely to configurational entropy. If a
Cr-specific effect becomes the focus, use a matched replacement series rather than attributing
the entire legacy-composition difference to Cr.

Confirm achieved bulk composition and phase/microstructure after melting, especially for
volatile-loss-prone ingredients. The Ω/δ/VEC filters in the code are empirical heuristics, not
confirmation of a single phase. The current screen even permits `single_phase=true` alongside
`phase='FCC+BCC'`; preserve those historical values but interpret them as heuristic labels.
Phase separation need not be a failure if the experiment explicitly tests its effect.

Decide a prospective ranking only after the active-phase models and initial characterization
support it. Keep confirmation melts distinct from exploratory melts. An initial small panel
can estimate variability; it is not automatically a powered efficacy experiment.

## 6. What a defensible “better than iridium” result requires

The electrolyte and endpoint define the claim. Beating IrO₂ in alkaline electrolyte does not
establish a replacement for iridium in acidic PEM electrolysis. The original project already
calls for a NiFe-LDH control (docs/15); retain it and add an explicit matched IrO₂ electrode
comparison if iridium is the target. Nonprecious alkaline activity exceeding IrO₂ has precedent,
so the new value must be more specific than that comparison alone.
([Liu et al., 2018](https://www.nature.com/articles/s41467-018-05019-5).)

For the existing testing plan, the most useful refinements are:

- Compare under the same electrolyte batch, temperature, reference-electrode calibration,
  geometric area and declared iR correction. Retain uncompensated data. Control or measure
  electrolyte Fe; include the support blank and both benchmark catalyst electrodes in each testing block.
- Choose a primary steady-state endpoint before confirmation. A candidate example is potential
  at an agreed current density after a fixed activation and durability interval; select the
  actual current, interval and minimum useful improvement from the intended application and
  pilot precision. A fast LSV point is not sustained activity.
- Measure oxygen/Faradaic efficiency where available, to distinguish oxygen production from
  parasitic oxidation. Couple retained performance to dissolved-metal analysis if claiming a
  dissolution mechanism or stability advantage. The stability number is an established option
  when oxygen production and metal dissolution are both measured; zero/below-detection loss
  gives a detection-limit bound, not infinite stability.
  ([Geiger et al., 2018](https://www.nature.com/articles/s41929-018-0085-6).)
- Use independent melts/preparations as replication units, with electrodes nested within them.
  Repeated scans of one electrode are technical repeats. Block and randomize test order, report
  all failures, and estimate paired improvements with uncertainty at the batch level.
- Report geometric performance for the electrode claim, plus mass/area information and
  suitable surface-normalized comparisons for the mechanism claim. Treat capacitance-based
  ECSA as a proxy whose calibration may differ between materials. Do not divide by an assumed
  site count and call the result a measured turnover frequency.
- Characterize before activation and after defined activation/durability points. Ex-situ XPS,
  Raman or diffraction can support a phase hypothesis; they are not by themselves direct
  observations of the operando active state. Fe surface concentration alone does not count
  catalytically accessible Fe sites.

Current confirmed lab access and completed measurements were requested during this review;
they were not re-established by inspecting the computational repository. That uncertainty
affects the execution order and which mechanistic claims can be supported, not the validity
of the completed local analysis.

## 7. Deliverable and execution priorities

The practical deliverable should be a reproducible **decision package** accompanying the
existing detector: an input manifest, QC record, admissible alternative calculations,
continuous sensitivity bounds, ranked/indistinguishable/unsupported comparisons, and an
experimental validation table. A user should be able to see why a composition was selected
and which assumption would reverse the decision. Uncalibrated ensemble spread is not a
probability of beating iridium. Disagreement should permit “insufficient evidence.”

| Priority | Refinement of the current work | Completion evidence |
|---|---|---|
| Immediate | Correct the continuous-robustness inference; add the reusable solver and case study | Reproduced counterexample, independent arithmetic, tests, source hashes and inspected figure |
| Next methods milestone | Finish the already chosen detector/control work and existing licensed readouts; distinguish pending from historical task notes | Runnable deliverable and executed controls; no substituted or invented student decisions |
| Next scientific milestone | Compare a small number of realistic activated-surface models and complete DFT protocols on independent targets | Held-out error/ordering comparison and documented phase/solvation/spin limitations |
| Parallel materials milestone | Confirm access and execute an interpretable exploratory substitution panel with benchmark catalyst electrodes | Independent preparations, achieved compositions, steady-state oxygen-producing activity and initial retention |
| Confirmation | Freeze predictions and endpoints, then test held-out compositions and new preparations | Prospective comparisons, batch-level uncertainty and preserved negative outcomes |

The STS 2027 application is due November 5, 2026 at 8 PM ET. The Society describes holistic
review; a credible placement probability or a hard “computational-only ceiling” cannot be
derived from a few past projects. The appropriate target here is original scientific insight,
independent understanding and a demonstrable result. This review does not promise a placement
or supply submission prose.
([Official application requirements](https://www.societyforscience.org/regeneron-sts/application-requirements/).)

The immediate scientific improvement is concrete: a robustness claim now has a continuous
test and a counterexample, while the valid nominal result survives. The larger improvement
depends on showing that this discipline changes the outcome of a real discovery decision.

---

## Dated corrections — 2026-09-05 (session 3), after a verification pass against the repository

Nothing above this line is edited. Every number in §2 was re-derived independently from
`docs/figs/pproj_cell_readout.json` with separate code, and the test suite's 424 passed / 8 skipped was
reproduced; §2 stands. The following lines are corrected or bounded.

1. **:23, alloy screen.** `results/r4_gated.json` has 6 rows; the 12 screened compositions are in
   `results/r4_screen_box.json` (`n_screened`). The counts are right; the attribution belongs to two files.
2. **:170, "often center on Cr".** Cr is the minimum-η site metal on 3 of the 6 gated candidates and
   3 of the 12 screened.
3. **:205, "add an explicit matched IrO₂ electrode comparison".** An IrO₂ reference on the same bench is
   already registered in S8 (docs/45:93; docs/44:172-173) — as a reference, not as a target. What S8 lacks
   is its go/no-go dated line: "No S8 ruling exists in the tree" (tasks/todo.md:1437-1439), "S8 dated line,
   either way" (tasks/todo.md:1572-1573), owed the week of Sep 8 (docs/76:296-297).
4. **:180, the substitution panel.** Adoptable only after that S8 line, a dated S8 amendment restating the
   registered melt-set rule (top 2–4 by the re-rank gate + a predicted-poor anchor + IrO₂ same-bench,
   docs/45:93) and a new freeze deposit before any ingot (docs/45:56). Until then it is ideation and enters
   no report.
5. **:221-222, the stability number.** Geiger et al. 2018 define the S-number as oxygen computed from the
   passed charge at an assumed 100 % Faradaic efficiency, divided by dissolved iridium measured online;
   only the dissolution is measured. "Both measured" over-states the source; measured oxygen would be an
   addition to it.
6. **:238, lab access.** The repository does record it: furnace, XRD and OER-bench access confirmed
   2026-08-16 (docs/44:174) and the potentiostat booked (tasks/todo.md:235). What is not on record is the
   S8 decision (item 3).
7. **:259, the deadline.** Consistent with docs/43:2249-2251 (report lock, backstop Nov 5 2026 8:00 pm ET).
   tasks/todo.md:1279's "Oct 15 hard freeze" (dated 2026-09-03) is the superseded date.

Of the seven paper citations, six resolve and support their sentences (Timrov 2021 and O'Regan 2010
together carry the projector clause); item 5 is the one that does not. The Society for Science page
confirms the date and time at :259. §3's protocol-validation discipline and §7's "Immediate" row are
unaffected. The six-metal arm's own shared-constants box, which §2's method invites, is now at docs/83,
dated addendum 2026-09-05 (session 3): the class verdict is constants-robust, the Mn and Fe rows are not.
