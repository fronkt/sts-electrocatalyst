# Eligible comparison and catalyst P-A readiness — 2026-10-03

This phase is an extraction and offline contract, not another screening round.
S29420 and S29447 remain eligible under the approved case rulings. Their
computational models support distinct mechanistic hypotheses; neither paper
selects a melt composition for the present campaign. The other three recovered
packages retain their scientific holds. Screening state, checklist and original
reads are unchanged.

## Comparative evidence

| Feature | S29420: GDY armor | S29447: Ru–Ir solid solutions |
|---|---|---|
| Computed material | Rutile RuO2(110),144 atoms; five O–Ru–O layers plus GDY(002),333 atoms, fixed strained lattice | Twenty composition-disordered Ru1−xIrxO2(110) slabs plus pure RuO2/IrO2 controls;62 cus sites,24 metal positions per mixed slab |
| Method | VASP/PBE/PAW,450eV,DFT-D3; SI distinguishes3×3×1 optimization sampling and1×1×1 surface sampling | GPAW/ASE/RPBE,500eV,spin-paired,3×1 slab/2×2 k-points; four layers,bottom two fixed |
| Author thermodynamic quantity | Direct AEM eta: main0.59/0.75eV; SI0.56/0.73eV, retained as conflicting pairs | TableS3 reported maxΔG1–4 at0V vs RHE in eV; main explicitly assigns it to each site's limiting potential |
| Reference clarity | Main gives theoretical U=1.23V; inspected calculation text does not explicitly establish theoretical RHE scale/CHE half-reaction equation | SI paragraph110 explicitly gives H2/RHE CHE relation; TableS2 defines four one-electron steps |
| Mechanistic distinction | Authors propose interfacial charge transfer and suppression of lattice-oxygen participation, favoring AEM | Authors compare bridge-proton-enabled intermediates with cus-only paths; local Ru/Ir arrangement and neighboring bridge O matter |
| Transfer limit | Coated strained interface, not a bulk alloy melt; theoretical and experimental RuO2−x labels remain distinct | Local cus sites are not62 melt compositions; ideal spin-paired rutile models are not the project's spin-polarized DFT+U slabs |

Primary references are Wang et al., *Nano Research*19,94908680(2026),
[DOI](https://doi.org/10.26599/nr.2026.94908680), main PDF p.4 and SI pp.2–4;
and Sharma et al., *ACS Catalysis*16,8008–8021(2026),
[DOI](https://doi.org/10.1021/acscatal.5c08494), main PDF pp.4–5/7 and SI
paragraphs108–110,161–163/TableS3. ACS PDF page numbers include the repository
cover. DOCX locators are original paragraph numbers, not guessed page numbers.
The original XML/media remain local; Word page layout and editable Origin
internals are not new inspection claims. Exact source pins and deciding fragments
are retained in `results/pa_integration_2026-10-03/evidence_spec.json` and the
checked extraction receipt.

The S29420 discrepancy has no source-supported preferred pair in this phase.
No averaging, unit relabeling,1.23 subtraction or new eta calculation occurs.
The S29447 limiting-potential assignment comes from the authors' main-text
definition, not highlighted cells or the separate1.5V activity discussion.
Its TableS3 descriptors remain reported thermodynamic quantities; they are not
activation barriers. Differences in functional, spin treatment, strain,
coverage and pathway preclude an unqualified cross-study ranking.

For the campaign, the two competing hypotheses are interface-driven electronic
modulation/oxygen stabilization and local multi-site proton accommodation.
Testing either requires an explicit match to the campaign's oxide surface,
adsorbate configuration and electrochemical conditions. They inform descriptor
and mechanism choices, not immediate alloy percentages. The present catalyst
P-A validation uses an existing stalled slab precisely to isolate numerical
behavior before a new composition or mechanism is introduced.

## Offline P-A-v2 scope

The real H2 test establishes QE7.5 restart plumbing only; its scientific pass
and original Slurm FAILED2:0 coexist in the retained
[tiny readout](pa-tiny-restart-readout-2026-10-03.md). The historical
`research_batch_checked.py` and A/B failures stay unchanged. Its old from-scratch
segments reset the optimizer, its four-file copy is not a full checkpoint, and
its nonterminal fresh-check failures could be accepted unchecked.

The additive `pa_checked_contract.py` is an offline decision/receipt contract,
not a runnable QE relaxation driver. It distinguishes the geometry at which
energy/force were evaluated from the optimizer's next proposal. A fresh SCF
must use the evaluated geometry and isolated scratch; it may not touch the
immutable restart snapshot. Safe continuation uses a complete recursively
inventoried checkpoint, including any distinct WFC directory. Actual restart
consumption needs observed optimizer/SCF counters and no startup reset/fallback;
copying a BFGS file is insufficient. Normal cleanup after convergence is not a
startup reset. QE's documented restart requires a clean stop and unchanged
processor/parallelization shape.
[Official restart input contract](https://www.quantum-espresso.org/Doc/INPUT_PW.html)

```text
evaluated segment + isolated fresh SCF at the SAME geometry
  fresh fails                 -> HOLD, no accepted step
  fresh lower by >10meV/cell   -> RESEED at evaluated geometry; intentional reset
  otherwise                   -> ACCEPT; continue at proposal with inherited state
```

The10meV criterion remains one-sided: a higher fresh state does not trigger a
reseed, even when more than10meV higher. Exactly10meV lower does not trigger it.
A stalled warm SCF has no usable energy; a clean fresh reference permits an
intentional reseed, not an accepted warm evaluation. A stopped/failed fresh SCF
supplies neither a reference nor seed. Segment/reseed caps count repeated work
and refuse an extra transition at the limit. A terminal convergence claim also
requires a clean fresh comparison.

Holding all unreferenced steps and resetting the optimizer for a new electronic
surface are prospective P-A-v2 differences from the historical runner. They
are explicit review items, not retroactive policy changes or a production
licence. Resetting is not restart continuity. Supplied structured evidence and
offline fixtures cannot establish that a real catalyst adapter consumed a
checkpoint, selected a lower metastable state or preserved its raw provenance.
Every contract outcome retains `production_accepted=false` and a pending real
catalyst test.

The contract is a post-hoc structured-receipt audit, not the pre-launch
controller. Its ACCEPT path requires the continuation's observed first-call
evidence; the future adapter must first decide the fresh-check branch without
launching a resume on HOLD, and then audit actual consumption separately.
Its normalized `fixed_flags` use1=fixed/0=free, the inverse of QE's `if_pos`
force-multiplication flags; source-aware conversion belongs in that adapter.
[QE atomic-position constraints](https://www.quantum-espresso.org/Doc/INPUT_PW.html)
This audit neither parses raw outputs nor establishes full electronic-ground-
state or geometry validity from supplied metadata.

## Separate catalyst validation proposal — NOT APPROVED OR SUBMITTED

Recommend one bounded numerical validation on the existing Cu8Cr23Mn35Co34,
seed20/site2 clean slab at the retained cycle5 low-state geometry. This is not
a full relaxation, adsorption reference or new composition. First complete
and independently review the catalyst adapter: source-pinned deck/seed/UPFs,
strict fresh-versus-restart scratch ownership, source/XML geometry and unit
validation, clean-stop observer at a registered evaluated boundary, full
checkpoint copier, inherited/reset startup gates, and per-invocation/aggregate
supervision. No wrapper or sbatch command is authorized by this document.

Proposed hard ceiling: one regular-CPU `wholenode` job,128 allocated/billing cores,16h,
total2048CPU SU, memory at most200GiB, at most six sequential pw.x invocations,
each at most2h, plus bounded validation/cleanup within the16h total. Keep the
same MPI/pool/thread shape for all continuity arms. No highmem/GPU partition,
array, chained job, automatic retry or projection sweep. Stop before a call
whose full registered time allowance exceeds remaining job/campaign budget.
The maximum cost is a cap, not a runtime prediction. The
[September catalyst plan](lowtail-stall-robust-protocol-plan-2026-09-22.md) records that a
single fresh SCF measured3485s at128 ranks, about124core-h; up to six2h calls
bound the nominal solver usage at1536core-h, leaving512core-h of job headroom.
Actual invocation work may time out and remain inconclusive.

Anvil SU is allocation-based; shared billing uses the larger CPU/memory share,
and node-exclusive billing charges the entire128-core node. Verify live
allocation/balance, partition, memory and `AllocTRES` before release; this
proposal assumes a regular128-core billing shape and refuses a larger one.
[Official Anvil accounting](https://docs.rcac.purdue.edu/userguides/anvil/jobs/)
The$50 literature cap and unused portion of the earlier8SU H2 allowance do
not authorize this2048SU proposal.

The six-call ceiling reserves continuous control, clean-stopped candidate,
resumed candidate, copied-history/from-scratch reset control, one isolated fresh
SCF at the first evaluated geometry, and at most one evidence-triggered reseed
evaluation. Require at least three corresponding evaluated geometries in the
continuous/split comparison, identical atom order/cell/settings, complete
ordered energy/position/force agreement and explicit retained units. Proposed
continuity tolerances remain1e−6Ry,1e−5bohr and1e−5Ry/bohr, subject to scientific
review for this128-rank catalyst build. An already-converged input, missed stop
boundary, failed fresh reference or unverified checkpoint makes the run
inconclusive; there is no silent rerun. If the fresh reference is more than10meV
lower, the reseed path is read separately and must not be forced into the
continuous-history trajectory comparison. If no genuine lower-state trigger
occurs, the real energy-drop/reseed branch remains unvalidated despite offline
fixtures or a negative-control reset.

Both continuity arms stop cleanly at the same registered third evaluated
geometry; they need not reach ionic convergence. The interrupted candidate
stops after the first evaluated geometry/first saved nonzero proposal; its
resume supplies the next two evaluations under the same numerical controls.
Stop triggers and saved-step counts must be source-reviewed for both boundaries
before launch. A natural BFGS convergence before three evaluations cannot pass
this trial. A detected SCF stall terminates the affected continuity comparison;
any licensed fresh/reseed diagnostic is reported separately, never spliced into
an equal-length continuity sequence.

This six-call experiment validates fresh-SCF interposition at one boundary,
not fresh comparisons at every step of a production trajectory. The continuous,
resumed and reset-control evaluations are numerical controls, not accepted
P-A production steps. Full every-step checking/reseeding and terminal fresh
acceptance remain a later protocol-validation gate even if this boundary test
passes. A known retained lower density is not a substitute for a genuinely
converged fresh-start result in the registered energy-drop rule.

## From this package to a melt

Next is catalyst-adapter implementation/source review, then explicit approval
of the dated resource/protocol proposal and the bounded numerical trial.
Acceptance can license a subsequent separately costed production relaxation;
it cannot create a converged reference or electronic ground-state guarantee.
Production references, matched adsorption energies/free-energy conventions and
uncertainty-aware S8 ranking/selection still precede melt composition choice.
The literature selection/extraction population freeze is also distinct from
these two-paper extractions. Melt stock/composition and sample-form constraints
must then be matched to the selected candidates. Laboratory availability is
confirmed and is not repeatedly queried here. None of the present extraction,
offline implementation or scientific planning needs Purdue/Elsevier API access.

## Verification and phase review

Fresh offline checks pass83 evidence tests and330 compute tests plus7 subtests;
one real filesystem-symlink fixture skips because Windows cannot create it.
That guard still needs platform-specific exercise before a real catalyst release.
Both scientific verifiers pass,42 registered recovery pair-reads and the seven
approved policies remain unchanged, and9791 prior tracked files plus21 unrelated
DFT files match their starting byte pins before and after testing. Extraction
repeats identically: four literal conflicting eta rows and62 original TableS3
site rows, with all eleven primary-location claims and source pins checked.
The independent extraction reviewer also matches all62 rows/10 fields directly
to original Word XML. Canonical screening/checklist changes are zero; checklist
144 and178eligible/89missing-SI/121scientific holds remain unchanged.
Initial configuration/table-selection/fixture failures remain in separate
receipts; they do not replace the final checks. Final independent package
review and publication receipt are retained alongside the verification files.
No new paid literature API or QE/Slurm run in this phase. Tracked literature
estimate remains$1.1105254 of the$50 lifetime ceiling, not an account bill.
