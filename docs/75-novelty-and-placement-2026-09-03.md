# docs/75 — Novelty landscape and STS placement: two verified sweeps, and the finding that reorders the plan (2026-09-03)

## 0. Status of this document

**Not a registration.** Nothing here licenses a deck, moves a threshold, scores a prediction, or
amends a deposited section. Every registration-shaped sentence is a *proposal for a dated line the
entrant writes*. Per docs/43 A7.7 the entrant paraphrases; no sentence of this file is report
prose, and per the STS 2027 Research Report Guidelines item 1 the report is written without
generative AI.

**Evidence marking.** `[OPENED]` = the source was retrieved and quoted directly. `[CARRIED]` = the
finding is reported but the source was not independently re-opened. `[CORRECTED]` = the claim was
raised and then overturned by a later check. Anything unmarked is inference.

**Scope of the two sweeps behind this file.** A novelty screen across eight literature lenses, each
followed by an adversarial refutation pass over its own findings — 113 findings survived
refutation, 57 did not, and **118 searches came back empty with their queries enumerated**. And a
verification of six STS precedent cohorts against the public record, followed by a completeness
critic that raised 22 corrections against it.

**Read §7 before quoting anything.** Both sweeps produced errors that their own checks caught,
including a **fabricated quotation inside the pass built to prevent fabricated quotations**. Those
are recorded, not hidden.

---

## 1. THE FINDING THAT REORDERS THE PLAN

**The Xu census is not blocked on silentgate. It is a four-keyword grep, and the answer is
already partly known.** `[OPENED — GitHub API + raw file fetches]`

docs/72 §9, docs/70 H-14 and docs/45:77 all treat the external census (A9 / P-XU) as gated behind
an entrant-written detector. The deposit was checked directly instead. The deposit is mirrored public
and complete at `github.com/zhongnanxu/rutile-OER`, commit `c4cb892605`, 2014-11-10, README
identical to the Zenodo record including its "fully analysis" typo. Recursive tree, not truncated:
**6,989 blobs — 815 `pwscf.in`, 815 `pwscf.out`, 815 `pwscf.run`**, plus a 2,698-blob
`linear-response/` subtree. Ten rutile dioxides x 4 CHE states x 17 U values = 680 at two layers.

**It is Quantum ESPRESSO — this project's own code.** Twenty raw input files across 5 oxides
x 4 CHE states at U = 3.5 eV parse as follows:

| oxide | nspin | tot_magnetization (bare/O/OH/OOH) | U_projection_type | &ELECTRONS | nosym |
|---|---|---|---|---|---|
| CrO2 | 2 | **16 / 14 / 15 / 15** | `'atomic'` | EMPTY | absent |
| MnO2 | 2 | **24 / 22 / 23 / 23** | `'atomic'` | EMPTY | absent |
| RuO2 | 1 | — | `'atomic'` | EMPTY | absent |
| IrO2 | 1 | — | `'atomic'` | EMPTY | absent |
| TiO2 | 1 | — | `'atomic'` | EMPTY | absent |

Error class by error class, on somebody else's decade-old field-canonical data:

- **Projector.** `U_projection_type = 'atomic'` in 20/20 — the projector QE's own manual now
  recommends against. Declared in the input files, **absent from the paper.**
- **`upscale`.** `&ELECTRONS` empty in 20/20 with `calculation = 'relax'` in 20/20: `conv_thr` and
  `upscale` both at code default in a relax, which is precisely the condition under which
  `upscale` silently tightens the threshold. The precondition is live in every file.
- **Symmetry.** No `nosym` in 20/20 -> QE default, symmetry on, forces symmetrised. **And** the
  adsorbate oxygen is explicitly frozen in x by selective dynamics (`0 1 1`). Two independent
  constraints, neither reported.
- **Magnetic, and this is the best of the four.** `tot_magnetization` is not converged to — it is
  **hard-constrained to a hand-picked integer that changes per CHE leg on an electron-counting
  rule** (CrO2 16 -> 14 -> 15 -> 15). A fixed-moment calculation is *forbidden* from finding a
  lower solution at a different total moment. And the deposit runs `nspin=2` for Cr/Mn against
  `nspin=1` for Ti/Ru/Ir — **the same partition perfectly confounded with A7.3's 3-over/3-under
  split**, appearing independently in a decade-old external dataset.

**Stated limits:** 20 of 815 files sampled at one U value (script-generated
and uniform, but the entrant runs all 815 and reports counts); the GitHub mirror matches the
Zenodo record by description, date and README text but the zip was not hashed here — note A9.7 act
1 already md5-matched the zip and compared 815/815 blob SHA-1s, so that leg is closed on the
record; and **Fe is absent from the deposit.**

**Consequence.** The single highest novelty-per-hour action in the project is ~6-10 hours of
grepping plain text, not 30-55 hours of writing a detector. It converts the report's central claim
from *"my calculations wobble"* to *"the field's reference dataset was built on every setting I
show moves the answer, and the paper reporting it states none of them."*

---

## 2. THE CLAIM SENTENCE

docs/43:1932 records that "what does not exist is the entrant's own claim sentence." These are
**drafts for the entrant to re-author**, not report prose.

> Changing a single keyword in a Quantum ESPRESSO input deck — which of the two Hubbard projectors
> shipped with the code defines the correlated orbitals — moves the computed oxygen-evolution
> overpotential on rutile(110) from 1.155 V to 1.642 V and reverses which elementary step the model
> reports as rate-limiting, with the material, the Hubbard U, the functional, the pseudopotential,
> the relaxed geometry and the convergence criteria all held fixed and the methods paragraph
> unchanged word for word; the candidates this screen was built to rank are separated by 0.03-0.08 V.

Why this construction survives both judge lenses: it leads with the **step flip** (a
mechanism-level change no error bar absorbs) rather than the magnitude; it says "shipped with the
code," never "default," so QE >= 7.1's no-default rule cannot break it; it names every held
variable, which is the operational definition of *undeclared*; it makes no negative-existence
claim; and a non-chemist gets it in one pass.

The second abstract sentence — the one that makes this an audit of a field rather than of a laptop
— is **contingent on Action A** and must carry the entrant's own count:

> Every one of the [N of 815] archived input files in the most-cited public rutile-oxide OER DFT+U
> dataset specifies one of those two projectors, hand-fixes the total magnetic moment of every
> adsorbate state, leaves the convergence block empty, and runs with symmetry on; the paper that
> reports that dataset states none of the four.

---

## 3. WHAT IS NOVEL, RANKED — with the hedge and the mandatory citation

Judge-panel means across three lenses (specialist / generalist / priority), 3 votes each:

| claim | mean | survives |
|---|---|---|
| C2 projector step-flip | **3.67** | 3/3 |
| C3 pre-registration | 3.33 | 3/3 |
| C8 magnetic metastability | 3.33 | 3/3 |
| C1 silent/declarable taxonomy | 3.00 | 2/3 |
| C6 budget exceeds signal | 3.00 | 3/3 |
| C4 internal reproducibility | 2.67 | 3/3 |
| C5 external census | 2.33 | 2/3 → **promoted to #2 by §1** |
| C7 closed loop (melt) | **1.67** | **0/3** |

**(1) The projector step-flip.** Reframe as a *crossing*, not a discovery.
**Mandatory citation, and the most dangerous omission in the current draft:** Bajaj & Kulik,
*JCTC* **18**(2), 1142-1155 (2022), DOI 10.1021/acs.jctc.1c01178 `[OPENED]` — projector
choice on rutile TiO2(110) and PtO2(110) O-adsorption. **It is not in the ledger anywhere.** What
survives: they compare a stock projector against a *bespoke* multi-atom projector they construct;
no overpotential, no *OH/*OOH, no CHE ladder, no limiting step. Claim the electrocatalytic
crossing only. Also cite Mahajan PRM 5, 104402 (2021); Macke JCTC 20, 4824 (2024); Kirchner-Hall
Appl. Sci. 11, 2395 (2021); Wang JCP 144, 144106 (2016).

**(2) The census (§1).** Hedge: report **exposure** — the fraction of independently published
archived inputs in which the preconditions are present — never a corrected overpotential. Say
plainly that this is the field's *best-practice linear-response exemplar*, not its weakest paper,
and that a zero-exposure result would have been reportable. **Do not write "the errors are the
field"** — Divanis (Chem. Sci. 11, 2943, 2020) and Chatterjee (arXiv:2512.05938) made the
field-scale statement first at larger N.

**(3) Pre-registration.** The residue that survives after §4 kills the "first" claim: Vepa
registered a threshold on model-versus-**experiment** error; A7.1 registers a threshold on a
method's disagreement **with itself** — no experiment, no material property, nothing on the other
side but the same binary twice. That is unoccupied and it is one sentence.
**Report four verdict states, not two:** CONFIRMED (A7.2, at exactly the registered minimum, zero
margin — say so), FALSIFIED (the Cr headline, withdrawn), NOT MET (A7.3), and
**UNDEFINED-BAND / VOID-CONFOUNDED** for A7.3, because the registration defined >=4 and never
defined 3, and because the 3/6 split coincides exactly with the nspin partition.

**(4) Magnetic metastability.** **New mandatory concession:** WhereWulff — Sanspeur, Heras-Domingo,
Kitchin & Ulissi, *JCIM* **63**(8), 2427-2437 (2023), DOI 10.1021/acs.jcim.3c00142
`[OPENED]` — an OER workflow that **does** search magnetic orderings, at the *bulk* stage.
Any unqualified "no standard check looks at this" is one citation from dead. The defensible
sentence: *the magnetic search stops at the bulk and is inherited downward.* Free thread: Kitchin
is an author of both the 2015 deposit that hard-fixes `tot_magnetization` per adsorbate leg and the
2023 workflow that searches orderings for bulk.
**Two arithmetic fixes:** "5 of 7 magnetic **3d endmembers**" is impossible against a six-metal
screen with three 3d metals — write "5 of 7 (metal, adsorbate-state) relaxations," name the seven,
state the selection rule, call it a hit rate on a screened subset. And Meredig is meV **per atom**;
this project's is meV **per cell** — on a 33-atom slab those differ by one to two orders of
magnitude.

**(5) The error budget — rebuild as NON-CANCELLATION.** As written, "the budget exceeds the signal
by an order of magnitude" is **a non sequitur, and three independent lenses said so.** An absolute
budget does not defeat a ranking if it cancels, and there is a sentence waiting to be quoted at
you: Moore et al., *Fluid Phase Equilibria* 476 (2018), *"predictions of the relative trends tended
to be reliable even if the absolute values were not."* Rewrite as: *these perturbations are
correlated with the axis being ranked — large for the magnetic 3d earth-abundant candidates, small
or absent for the closed-shell 4d/5d benchmarks they are ranked against; a material-correlated
error does not cancel the way a common-mode reference error does.* **This requires Action B to be
true at all.**
Mechanical: delete "order of magnitude" (the stated ranges span 1.25x-37x); stop summing eV and V
in one range (0.487 V is a delta-eta, 0.175-0.405 eV is a total-energy gap); drop the 1.122 V U leg
from the headline — Tripkovic owns it and the Xu deposit already swept U 0-7.5 eV on this system.

**(6) The taxonomy — an acknowledged import, which is stronger than an invention.** It is
multiverse analysis: Steegen/Tuerlinckx/Gelman/Vanpaemel, *Perspect. Psychol. Sci.* 11, 702 (2016);
Simmons/Nelson/Simonsohn, *Psychol. Sci.* 22, 1359 (2011) — the word in that title is
*Undisclosed*; Simonsohn 2020. Also Tambon et al., *Empir. Softw. Eng.* 29 (2023), defining "silent
bugs" as those that *"lead to wrong behavior but do not cause system crashes or hangs, nor show an
error message"* — this project's definition, five years early, in software engineering.
**The line that converts concession into contribution:** *a psychologist can only argue about what
the other analyses would have shown; a deterministic calculation lets me run all of them and print
the spread.*
**Grade yourself on a three-tier ladder:** Tier A declared-and-already-varied (U — Tripkovic owns
it); Tier B declarable but absent from published methods (projector, symmetry); Tier C not an input
at all, the log itself is wrong (the converged magnetic solution, `upscale`). **Only two of five
reach Tier C.** Rename: use **"undeclared,"** not "silent" (collides with HPC silent data
corruption); **"specification sensitivity,"** not "internal reproducibility" (collides with ISO
5725 and the NASEM definition).

---

## 4. WHAT IS NOT NOVEL — DROP OR DEMOTE

| Claim | Killed by | Verdict |
|---|---|---|
| "First pre-registered DFT / computational-catalysis study" | Wu & Chen Zenodo 21880229 (**2026-08-11, five days before the first deposit**); Vepa arXiv:2606.23725; Oberländer Zenodo 21625495; Liu *JACS Au* 10.1021/jacsau.6c00160 | **DELETE.** Breakable by one Zenodo query. |
| **C7 — screen → melt → measure** | Lun et al., *Adv. Energy Mater.* 2025, DOI 10.1002/aenm.202405657 `[OPENED]`: high-throughput DFT screen → Mg0.23Ir0.13Ru0.64O2 → **191 mV at 10 mA/cm2** → PEMWE at 1.0 A/cm2. Plus Greeley *Nat. Mater.* 2006; Seh *Science* 2017 | **DEAD.** Zero novelty even if executed perfectly. 1.67 mean, **0/3 survivors.** |
| U-sensitivity as a headline class | Tripkovic *JPCC* 122, 1135 (2018); and the Xu deposit swept U itself | **DEMOTE to Tier A.** Remove 1.1 V from the headline budget. |
| "The overpotential is uncertain" | Chatterjee arXiv:2512.05938; Krishnamurthy *JPCL* 9, 588 (2018) | **CONCEDE in the introducing sentence.** |
| "No work connects projector choice to adsorption on any surface" | Bajaj & Kulik 2022 | **FALSE. DELETE.** |
| "Invisible to every standard check" / "no detector exists" | WhereWulff 2023; pymatgen-io-validation | **DELETE the universal**; replace with an enumerated toolchain table. |
| "A Δ-gauge for surfaces" | De Waele PRB 94, 235418 (2016) reached surface energies and work functions; Δ is an integral over E(V) with no adsorbate analogue | **RENAME AND RESCOPE** — say "never for an adsorbed intermediate." |
| Any "nobody has" resting on arXiv counts | arXiv `all:` is **metadata only, not full text**; Meredig, Kirchner-Hall, Wang 2016 and others have no arXiv record — the founding literature is invisible to the searches used to prove the gap | **REWRITE EVERY ONE** as "I am aware of no…" + a printed query table. |
| Title near "Rigor and Reproducibility in Electrocatalysis" | Tackett 10.1021/acscatal.6c01946 and Bates 10.1021/acscatal.6c01834, both July 2026 | **AVOID THE PHRASE**; cite the series. |

**The 118 enumerated empty searches are the asset.** What the sweep could *not* find, across
Bing/Claude index, Semantic Scholar, OpenAlex, Crossref and the arXiv API: any study varying **only
the Hubbard projector** at fixed U/geometry/functional/code and reporting the effect on an
adsorption energy, an overpotential, or the identity of the limiting step (all projector literature
found is band gaps, computed U, polarons, or bulk energies); any adsorbate-slab **frequency audit**
of magnetic metastability; any peer-reviewed audit or published magnitude for the
symmetry-constrained relaxation trap (it is "documented community folklore"); `occupation matrix
control` AND `adsorption` → **0 results**; any retrospective audit re-running published OER DFT.
These license the claims in §3 **only in the form "I am aware of no…, and here is the query
table."**

---

## 5. STS PRECEDENT — WHAT THE VERIFIED RECORD SAYS

**The archetype places, and at the very top.** `[OPENED]`
- **Thomas Cong, 2024 — 2nd place, $175,000.** A confounder critique over other people's published
  multi-cancer data; the field's premise found *"questionable"* (verbatim, re-confirmed by the
  critic). No experiment.
- **Carolyn Beaumont, 2019 — 5th place.** Title begins *"New Analysis Reevaluates."* Overturned the
  incumbent FTIR model using independent NMR. `[CORRECTED: title confirmed via an indirect index key —
  page-number cross-reference plus her p.5 body profile; the 2019 pages are off the live site]`
- Plus Liang (2026), Tyagi (2024), Kumar (2019) at Finalist. ~5 of ~360 finalists over nine years.

**Modality buys nothing.** Zero-experiment projects took **1st in 2024, 2025 and 2026**, plus 2nd,
4th, 5th, 9th, 10th. Three real experimental materials projects — Sanxhaku's flow cells, Ramesh's
gels, Corey's specimens — all stopped at Top 40. Small n does not cap either: Corey made Finalist on
30 specimens with no error bar; Chu took the Seaborg Award on 22 cells.

**What separates the tiers is deliverable state.** The four capped Scholars — Hirshorn, Lin, Bao,
Gu — are 4-for-4 across three years and four subfields, and every one ships a *contingent
shortlist*. This project ships neither a shortlist nor a closed object, and **open is worse than
contingent**, because contingent at least names a candidate.

**Closest analogue: Frances Liang, 2026 — Finalist, NOT Top 10.** "PLI-Analyzer," a validation
platform aimed at the silent failure modes of third-party software she did not write, negative
headline (AlphaFold3 and Boltz-2 get ~half of complexes right), framed on *"the mistakes AI makes
are hard to detect."* Three differences, all against this project: her targets were **external and
named**, she **shipped a runnable artifact**, and she had **one compressible number**.

**Ceiling template: Cong.** The one sentence that should reorganise October —
**the only structural difference between Cong-tier and Liang-tier in the verified set is whose data
the defect is demonstrated in.** That is Action A.

**Placement read (inference from precedent).** As of 2026-09-03: **Scholar likely; Finalist
genuinely contingent, near-even; Top 10 low.** With the census run and the framing flipped from
"my hypothesis failed" to "the field's assumption fails," **Finalist becomes the base case.**

**Pattern observed on exactly two data points, never to be quoted as a criterion:** both top-ten
methods projects frame the result as **"the field's assumption fails,"** never **"my own hypothesis
failed."** This project is currently framed the second way. Separately: pre-registration has
**zero mentions in nine years** of the public record — an *unpriced* novelty, neither demerit nor
proven credit.

---

## 6. THE TARGETING TABLE

Ranked by novelty per entrant-hour. **SU is not the constraint.** "Fits" = completable before the
~Oct 6 writing start.

| # | Action | Novelty gained | Hrs | Fits |
|---|---|---|---|---|
| **I** | **Open the three Zenodo deposits** (or publish an OPEN companion carrying hypotheses, thresholds, freeze dates and SHA-256 hashes) | All three are **RESTRICTED**. A judge who clicks the DOI in November hits a permission wall. Converts a sealed timestamp into a readable pre-registration | **1** | ✓ |
| **C** | **Twin methods-paragraph figure** — the two projector arms' methods paragraphs side by side, byte-identical, with 1.155 V / 1.642 V and the two limiting steps beneath | The most legible artifact available; a biologist gets the thesis in three seconds. Nobody has proposed it | **1-2** | ✓ |
| **D** | **Magnetic-moment control on the projector pair** — total and per-site moments for both arms, all four states | Closes the first question a referee asks: *did the projector just move the spin state?* Silence here is fatal | **2-3** | ✓ |
| **A** | **XU-DEPOSIT SETTINGS CENSUS** — grep all 815 `pwscf.in` for `U_projection_type`, `nosym`, empty `&ELECTRONS`, `calculation`, `nspin`, `tot_magnetization`; tabulate `tot_magnetization` across the four CHE legs per oxide per U | **The single biggest novelty gain in the project** (§1). Also supplies *external* corroboration for the A7.3 nspin confound | **6-10** | ✓ |
| **B** | **Non-cancellation / rank-inversion table** — Δη per metal per perturbation, Kendall τ between baseline and perturbed orderings, inverted pairs out of 15 | **The thesis sentence is logically invalid without this.** Pre-register that it can kill C6 | **6-10** | ✓ |
| **F** | **Metascience import paragraph** (Steegen / Simmons / Simonsohn) | Removes the largest generalist-panel credibility risk and upgrades "I invented a taxonomy" to "I transferred a named instrument into a field that lacked it" | **2-3** | ✓ |
| **G** | **Toolchain audit table with pinned commits** + the WhereWulff concession | Converts an unenumerable negative into a countable one | **3-4** | ✓ |
| **K** | **Read, via Purdue library: Bajaj & Kulik (JCTC 18, 1142), Chaudhari (Digital Discovery 4, 3701, 2025), De Waele (PRB 94, 235418)** | The nearest occupiers of the headline claim, currently unread. Non-negotiable | **3-4** | ✓ |
| **H** | **Registration-integrity timeline** — amendments 1-11 against the earliest output timestamp each governs, with the two firings marked | Answers "you amended it eleven times, what did it constrain?" and makes the chain evidence rather than embarrassment | **6-10** | ✓ |
| **L** | **nsym-drop detector on this project's own outputs** — symmetry-op count per adslab vs its bare slab; force components exactly zero | A measured incidence rate from files already on disk | **3-5** | ✓ |
| **E** | **Declaration audit** over Divanis's 24 OER articles — how many state projector / symmetry / spin init / convergence protocol | The only thing that earns the word "undeclared" as a **counted fact**. Pairs with A: the deposit declares it in the files, the papers do not declare it in print | **10-15** | ✓ |
| **M** | **IrO2 bench replicate power run** — n >= 7 electrodes, **no ingot**, report replicate SD in η and minimum resolvable Δη | Decides S8 with the entrant's own number instead of a transferred figure | **6-10** | ✓ (September) |

---

## 7. CORRECTIONS TO THE RECORD

### 7.1 Errors in docs/72, found by docs/73's 51-agent census

- **The "free rows" premise was wrong.** Of 14 candidate free rows, **13 refuted, 1 survives.**
  "Close the unscored pile" is **not** a cheap win and must not be planned as one. The honest move
  for most of the pile is to accept WITHDRAWN-UNSCORED **deliberately and say so.**
- **Two of docs/72 §8's three named free rows do not exist** — P-SPIN-DELTA and P-FLOOR-U-SPIN are
  both blocked by a dated line written the same day docs/72 was.
- **P15 survives and is bigger than docs/72 thought**, not smaller; its stated scope limit is false
  and the gate is 100 % decidable from disk. The ortho-atomic companion (5.6688 / 5.6743 eV vs
  atomic 4.2251 — a **1.45 eV projector spread in U-space**) is a second projector observable on a
  second material, which directly answers the "flagship is n=1" attack.
- **docs/72:242 is false** — Amendment 1's check 4' bulk magnetic arm *has* a run.
- **docs/72:230's G8 grep ("no doc cites it") is self-refuting** — docs/72 itself printed the
  number, so the grep became false the moment the file was written. A negative existence claim must
  exclude the document asserting it.

### 7.2 Corrections against the STS precedent findings

- **"STS publishes no judging rubric" is REFUTED.** The 2027 Official Rules publish a SELECTION
  PROCESS with **four named evaluation areas**: Research Report and Scientific Merit; **Student
  Contribution to the Research**; Academic Aptitude and Achievement; Overall Potential as a Future
  Leader — and verbatim, *"the research project, while important, is not the only factor for award
  decisions."* Two of four areas are **not about the project at all**, and this project's strongest
  asset (owning all five research acts) is therefore backed by *published criteria*, not inference.
  **Every doc in this repo repeating "no rubric exists," including docs/70:827-832 and docs/72 §5,
  is wrong on this point.**
- **"A 15-person cross-disciplinary panel" is not published.** The rules say only "an additional
  judging panel of doctoral scientists, mathematicians and engineers." The 300-cut is by three or
  more doctoral scientists **"in the appropriate scientific discipline."**
- **A published line bearing on S8 was never cited:** *"Evaluators consider student circumstances
  and access to labs… in relation to student achievement."*
- **A second finalist judging stage exists and nothing has prepared for it:** *"panel judging,
  designed to evaluate the depth and breadth of their general scientific knowledge"* — half of
  finalist judging is explicitly **not** about the project.
- **A FABRICATED QUOTATION, in the document written to prevent them.** The comparison quoted the
  2025 finalists page as *"Using a density function approach."* That string does not exist; the page
  reads *"Using a mathematical strategy called a density function…"* — and it classifies Patlolla as
  a **physics / quantum-computing** project. **Treat him as UNCONFIRMED, not as a DFT precedent.**
- **Name collision:** there are two Vincent Huangs — 2019 (9th, refugee-migration model) and Vincent
  Weisi Huang (2024 Finalist, LauePt4). Always cite the year.
- **"No verified entry reports a majority-negative scorecard" is unsupported** — a category
  mismatch. STS publishes ~100-word promotional blurbs, not scorecards; *no* finalist reports a
  scorecard of any sign.
- **The "zero withdrawn hypotheses in nine years" sweep is fallible** — it missed Michael Yuanchao
  Ma (2018), whose profile says his results *"enabled him to disprove a previously published
  mathematical conjecture,"* while `disprov*` was on the term list.

### 7.3 Claims corrected during this review

- The claim that the project has "no deliverable" and "no proposed candidates" is **wrong.**
  `results/r4_melt_list.json` holds a designed melt set — Ni31Cr29Cu5Mn35 (activity end,
  η_pred 0.440), Fe25Co25Ni25Cr25 and Cu26Ni9Cr31Co33 (interior front), Cu22Fe30Co32Mn15
  (stability end + poor anchor), FeCoNi (ablation) — spanning the activity/stability front with a
  predicted-poor anchor and an ablation. That is an experimental design, not a ranking.
- **"tier_v3 does not exist"** was carried from a docs/43 archive dated **2026-08-09**. `docs/45:79`
  records S3 — tier_v3 crossed coverage x symmetry x basin, **8 metals** — as **LAUNCHED**, waves
  1-4 plus rounds 3-11, run Aug 23-27 under the deposited protocol.
- "Six metals, small n" describes only the **A0 census**; the **S3 corrected-protocol
  arm is eight** (tier_v2 seven + TiO2), 48 potential pairs. Quoting one arm as the project is misleading.
- "A 15-person cross-disciplinary panel" and "STS publishes no rubric" are both wrong, per §7.2.
- **Standing correction to the entrant's own recollection:** the *fine-tuned MLIP* is dead by his
  own decision (`docs/44:78-81`, and docs/70's not-worth-doing list). The corrected **DFT protocol**
  is the live deliverable; the fine-tuned model is not. And **no ingot has been melted** — S8
  remains an undecided go/no-go.

---

## 8. S8 — THE EVIDENCE IS NOW ONE-SIDED

Every independent line run today points the same way:

- **C7 ranked LAST of eight claims: mean 1.67, 0 of 3 judge lenses voting it survives.**
- **It is scooped outright.** Lun et al., *Adv. Energy Mater.* 2025 already ran DFT screen → synth →
  191 mV at 10 mA/cm2 → PEMWE device `[OPENED]`. Zero novelty even executed perfectly.
- **Modality buys nothing at STS** (§5) — three experimental materials projects capped at Top 40
  while zero-experiment projects took three consecutive first places.
- **The rules publish that lab access is weighed contextually**, which supports a no-go directly.
- docs/70 already ruled: "an S8 ingot that cannot complete… a partial chain is worse than none."

**The strongest interview answer if no-go**, and it is a good one: *the measurement would not have
adjudicated the finding — the audit is about rutile(110) DFT+U, and a melted high-entropy alloy is
a different material system that cannot tell me which projector is right.* Followed, unflinching,
by the schedule reason.

**Action M** (n >= 7 IrO2 replicates on the already-booked potentiostat, **no ingot**, ~6-10 h)
decides it with the entrant's own number and is reportable whatever it returns.

**This remains the entrant's dated line.** Three independent sessions now recommend the same
direction; none of them is a decision of record.

---

## 9. WHAT THE ENTRANT OWES

1. **Action A — the Xu census.** 6-10 h, 0 SU, not blocked. Highest novelty-per-hour in the project.
2. **Action I — open the deposits.** 1 h. A restricted DOI is a permission wall in November.
3. **The claim sentence**, re-authored in his own words from §2. Overdue.
4. **S8 dated line**, either way (§8).
5. **Action B**, or the C6 thesis sentence must be rewritten as non-cancellation and re-derived.
6. **Read Bajaj & Kulik.** The most dangerous omission in the draft.
7. **Fix the conv_thr documentation defect** (registered 1e-6 = 13.6 meV against meV-level claims;
   runs met 1e-8). Open at `tasks/todo.md:616`. A judge who opens the input files finds it in ten
   minutes.
8. **Correct the arithmetic and units in the magnetic class** (§3.4).
9. **Reference hygiene, every entry opened by hand.** The published top reason projects failed to
   qualify in 2026 is *"Fake references and/or citations in Research Report."* Both sweeps today
   produced fabricated or mis-scoped citations that their own critics caught. This buys no tier and
   protects everything.
