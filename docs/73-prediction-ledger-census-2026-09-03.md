# docs/73 — Prediction-ledger census: what is scored, what can still be, and what only a dated line can unlock (2026-09-03)

## 0. Status of this document

**AI-drafted census, not a registration.** Nothing here scores a prediction, moves a
threshold, licenses a deck, amends a deposited section, or supersedes docs/43. Every verdict
below is a *proposal for a dated line the entrant writes*. Per docs/43 A7.7 the entrant
paraphrases; no sentence of this file is report prose, and the report itself is written
without generative AI.

**Question this answers.** docs/72 §4.2 named the project's degradation precisely — *"the
registration is growing faster than the scoring"* — and §9 decision 4 said to *"close the
unscored pile before it auto-converts"*, on the premise that **9+ predictions are
measured-but-unscored** and that §8's items are **free rows** closable "with a decision or a
paragraph, not with compute." This file tests that premise against the tree.

**Verification rule used.** Two workflows, **51 agents**. Pass 1 enumerated every registered
prediction from eight independent slices plus a **bottom-up verdict map** built only from grep
hits, deliberately blind to any summary document's list. Pass 2 then tried to **refute** every
candidate free row with three hostile lenses each (already-scored / data-reality /
criterion-licence), defaulting to REFUTED under uncertainty. Every claim carries a `path:line`
or a re-runnable command. **The refutation pass changed the answer**, which is the reason it
exists.

---

## 1. The finding, in three lines

- **The premise is wrong, and the error is expensive in the safe direction.** Of **14 candidate
  free rows**, **13 are refuted** and **one survives**. The unscored pile is not a paragraph
  away; it is mostly a *dated entrant line* away, or unreachable.
- **P15 is the one real free row — and it is bigger than docs/72 thought**, not smaller. Its
  scope limit is false and the gate is 100 % decidable from disk.
- **Two of docs/72 §8's three named free rows do not exist.** P-SPIN-DELTA and P-FLOOR-U-SPIN
  are both blocked by a dated line **written the same day docs/72 was**.

> Stated plainly, because it is the actionable part: **"close the unscored pile" is not a cheap
> win and should not be planned as one.** The honest move for most of the pile is to accept
> WITHDRAWN-UNSCORED deliberately and say so — which docs/72 §4.2 already gestured at
> ("a pattern the report should name deliberately rather than let a reviewer notice it first").

---

## 2. The census, counted

199 distinct prediction-shaped tokens were enumerated. After dedup and after removing tokens
that are rules, elections, deliverables or classification instruments rather than predictions:

| | count |
|---|---|
| Tokens enumerated | 199 |
| Carrying a dated verdict somewhere in the tree | 124 |
| Unscored | 65 |
| Conflicting or unclear | 10 |
| **Unscored + data banked → candidate free rows** | **38 (→ 14 families)** |
| **Families surviving adversarial refutation** | **1 (P15)** |

**Calibration note on the vocabulary.** ~250 `CONFIRMED` and ~199 `REFUTED` hits repo-wide
reduce to **~30 actual verdict applications**. The bulk are adversarial-audit findings being
confirmed or refuted, plus `src/dft/hessian_analyze.py` PREREG docstrings quoting the
registered vocabulary back at itself. Any count of "predictions scored" taken from a raw grep
will be off by an order of magnitude.

---

## 3. The one real free row — P15 (hp.x linear-response Hubbard U)

**Survives all three hostile lenses unanimously, HIGH confidence.** Every number below was read
off disk this session.

| leg | measured | registered bar | result |
|---|---|---|---|
| External U(Ti-3d), atomic projectors | **4.2245 eV** (q222), **4.2251** (q333), **4.2245** (q444) | in **[3.0, 7.0] eV** | **GO** |
| q-mesh convergence | max \|dU\| **0.0006 eV** over three rungs | < 0.2 eV vs next finer mesh | **PASS**, measured twice |
| `find_atpert = 4` reproducibility | both Ti at **4.2251**, agreement **0.0000 eV** | ≤ 0.05 eV | **PASS** |
| **check 4′ bulk magnetic arm (CrO₂)** | **U(Cr-3d) = 6.1635 eV**, JOB DONE, **0** "Convergence has not been reached"; parent SCF total magnetisation 4.00 µB/cell | finite U, zero non-convergence | **PASS** |
| amplitude independence | — | **WITHDRAWN** by Amendment 1 as unperformable | n/a |
| χ-matrix symmetry | — | **DEMOTED** to reported diagnostic by Amendment 1 | n/a |
| CrO₂ **slab** arm | 4/4 carry "Convergence has not been reached", no `Hubbard_parameters.dat`; 8 `crslab_nosym` decks have no `.out` at all | — | **NO-GO, separate gate** (docs/43:292-295) |

Files: `runs/hp_tio2/hp__atomic_q{222,333,444}.Hubbard_parameters.dat`,
`hp__atomic_q333_allatoms`, `hp__cro2_q222.{in,out,Hubbard_parameters.dat}`, `scf__cro2.in`;
slab failures in `runs/hp_costmodel/`. Convergence hygiene, counted this session:
**25 of 25** hp.x runs under `runs/hp_tio2` are clean — every one prints `JOB DONE` with **zero**
"Convergence has not been reached" — which independently reproduces commit `dc38c23`'s
"25/25 zero NOTCONV". Under `runs/hp_costmodel`, 6 of 10 are clean and the **4 non-converged ones
are exactly the slab arms** below.

**Two verdicts are available today, and they point opposite ways — which is what makes writing
them worthwhile:** **P15 BULK = GO** (external window met with a 333× margin on the q-mesh
check and 0.0000 eV on the reproducibility check) and **P15 SLAB = NO-GO**. A gate that returns
GO on the bulk and NO-GO on the slab is a more useful result than either alone, and the registered
text already keeps them separate (docs/43:290-292, "**A successful bulk validation does not
license a slab U**").

**Why it alone was never scored:** there is **no hp readout script**. `src/dft/` holds only the
builder (`build_hp_validation.py`, whose :25 says "This file registers **nothing**") and
`queue_hp.sh`. Every other scored family in this repo has a `src/dft/*_readout.py` that
emits its verdict (`a0main_`, `a0cell_`, `lit2_`, `pproj_`, `s3_`); block 1B has a builder only,
so nothing ever wrote its line. **This is a structural explanation, not an excuse** — and it
predicts where the next unscored-but-decidable row will be found.

**Supporting number worth carrying to the report:** the ortho-atomic arm gives
`hp__ortho_q222` = **5.6688 eV** and `hp__ortho_q333` = **5.6743 eV** against atomic's 4.2251 —
a **1.45 eV projector spread on the same material**. That is the U-space companion to P-PROJ's
already-scored **0.487 V** η split, and it is the measurement docs/43:1344-1346 calls "the
campaign's own evidence" while naming no file (§5 item 9).

### Three riders the verdict line owes — none costs compute

1. **The slab stays a separate gate at NO-GO.** It is not part of the bulk GO.
2. **The literature side-check is now owed**, the Xu gate having been discharged 2026-08-12
   (docs/43:269-270, :1294-1295). Xu Table 1 TiO₂ = **4.95 eV**, so **4.2245 − 4.95 = −0.73 eV**.
   Flag: that offset **exceeds the 0.5 eV figure** used in the unrelated §9 falsifier at
   docs/43:410 — the two must not be quoted as if they agreed.
3. **The χ-symmetry diagnostic is settleable for free** — every deck ran `iverbosity = 2` and the
   per-rung `.chi*.dat` files are preserved, so the raw χ can be compared against the symmetric
   matrix in `.Hubbard_parameters.dat`. It is still **PENDING**
   (`runs/hp_costmodel/cost_model.json:9`, `prereg.demoted_to_diagnostic.status`). It is
   **demoted to a reported diagnostic and never gated** (docs/43 §4-A.4) "whichever way the
   pending measurement resolves", so it cannot block the GO — but it is a free row of its own,
   and `find_atpert = 4` makes χ(1,2) vs χ(2,1) a genuine measurement either way.

### Two facts docs/72 states about P15 that are false

- **docs/72:242 — "Amendment 1's check 4′ bulk magnetic arm has no run."** It has a run, it
  converged, and it matches every registered specifier in docs/43:619-627 term for term
  (`nq 2×2×2`, `find_atpert = 1`, `conv_thr_chi 1.0d-5`; parent `scf__cro2.in` `nspin = 2`,
  `smearing='mv'`, `degauss=0.01`, `starting_magnetization(1)=0.6`, `U Cr-3d 1.d-8`). **Found
  independently by four agents.** And it was not obscure: **git commit `dc38c23`, Mon Aug 10
  2026** records it in its own message — *"CrO2 U(Cr)=6.16 eV spin-polarized"*. The claim that
  the arm has no run was contradicted by the repo's own history for 24 days.
  Consequence: docs/72 uses that claim to scope the conversion to "the TiO₂ leg only", when
  check 4′ is precisely the registered escape from docs/43:620-621's closed-shell restriction.
  **The available GO is a BULK GO, not a TiO₂-only one.**
- **docs/72:230 — G8's "no doc cites it"** is self-refuting: docs/72:228-229 and :238-239 print
  both numbers, and `tasks/todo.md:1414` prints both. The grep was right about the corpus it ran
  on and wrong as a claim.

**One in-code addition, and the artifact handles it correctly.**
`runs/hp_costmodel/cost_model.json:173` states check 4′'s pass condition with an extra conjunct
docs/43 does not carry — "AND a non-zero total magnetization in the SCF log … a zero-moment
solution means the magnetic branch was never exercised (N24)". Under docs/43's rule that in-code
PREREG copies lose, it has no force; it is also **satisfied** (4.00 µB/cell). Worth recording as
the good case rather than a defect: the same file's `:5` says "this JSON registers nothing; where
they disagree with docs/43, docs/43 wins", its `:6` deliberately **refuses to copy the external
window** for exactly the reason that a widened window in a build artifact "is the single most
damaging thing an STS judge could find", and its `:9`-`:13`
(`prereg.demoted_to_diagnostic.status`) carries the χ-symmetry diagnostic as **PENDING** with the
procedure for settling it. That is the in-code-PREREG rule working as designed.

---

## 4. The thirteen refuted families, and what each actually needs

| family | why it is not a free row | what would unlock it |
|---|---|---|
| **P-SPIN-DELTA** | Registered population is **exactly {Ti, Ru, Ir}** (docs/61:1, :102-105) — Cr/Mn/Fe are nspin=2 incumbents with D_M ≡ 0 by construction and are **not in it**. `[D2 GUARD-3 ADJUDICATED 2026-09-03]` then makes Ru and Ir "**not scored into a span**", and docs/43:2816-2819 enforced that against *this very quantity* hours later. Operative **denominator 1**, unenumerated by A11.3; at n=1 the "≥2 of the licensed metals" bar is arithmetically unsatisfiable | entrant's dated line resolving n=1, then MIDDLE BAND on **Ti alone** — a much weaker deliverable than "a verdict today" |
| **P-FLOOR-U-SPIN** | Same D2 line leaves the equalised sensitivity on **Cr, Mn, Fe, Ti** → denominator **4**, absent from A11.R2's table; rule (iv) at docs/43:2107 requires "a new dated line **BEFORE** scoring". The banked census still says `n_final_rows: 6`, written **one day earlier** — a live artifact-vs-dated-line inconsistency | entrant's dated line fixing the denominator |
| **P-SYMCOV** | Registered criterion forbids a bare verdict; its own artifact declines — `runs/s3/readout/p_symcov_2026-08-24.md`, "Claim-scope branch … **NOT RESOLVED HERE**" — because the per-metal aggregation and the numeric cut for "large" are **both unregistered** | a registration, not a calculation |
| **A7.2 equalised re-read** | **Already scored.** `[TI CONVENTION 2026-09-03: NSPIN=1 STANDS, FINAL]` at docs/43:2656 states at :2666 "A7.2 stays CONFIRMED at 5 of 6, with Ti FLAT either way" | nothing — remove from the list |
| **A7.4 gate (f)** | **Already scored — by the entrant on 2026-08-21, in git history.** No working-tree grep reaches a commit message. Registered text also does not make gate (f) scoreable | nothing — remove from the list |
| **A5.1 (c)(d)(e)** | (c) already scored, and calling it unscored is **a logged error of this project** (`tasks/todo.md:738` stale, retracted at :1196). (c) is a deliverable with no threshold; (d) is a question plus a *motivating prior*, no registered numeric bar | (e) legs 1-2 are two text edits, zero DFT — the only live remnant |
| **A5.3 / A5.5 / A5.6** | Method and reporting clauses, not predictions — no falsifiable direction | nothing to score |
| **A7.5** | **A rule**, not a prediction (docs/43:1394-1416, "the phase-reality ledger and the MODEL-PHASE scoping rule") | nothing to score |
| **P4 / P5 / P6** | **Not registered predictions under docs/43 at all** — they live in docs/41, and docs/43:465-466 states the rule that docs/43 is the only pre-registration. Family also closed by a dated line 25 days before the census ran | nothing — remove from the list |
| **P12 / P13 / P19** | P13's prior is **already scored FAILED** (docs/72:117 — though it mis-points to docs/43:187; the prior is at **:177-179**). P12's bins need a Δη column that `cellsym_readout.json` does not have, and Cr's three *OOH pairs are all magnetically CONFOUNDED (Δm_abs 1.11-1.87 µB) | new Cr compute at matched magnetisation — the S3 arm that never completed |
| **A9 census (P-XU, P-XU-SPAN, P-DIVANIS, P-BUILDER, P-LIT)** | **Not "measured-but-unscored" — UNSCORED AND UNMEASURED.** The detector does not exist; the census has never run; `run_controls.py` prints **RESULT: NOT GREEN** with all six control rows NOT MEASURED. **Four of five cannot be scored from this repo even with a working detector** — the Xu 810-output corpus and OC20 are **not on this machine**, they live on Anvil `$SCRATCH`, which both READMEs describe as **purge-eligible** (an unlogged risk to the whole S2 arm). P-BUILDER's threshold and four denominators are **literally blank**; P-LIT's search string, databases, date window and predicted proportion are **all blank** — incomplete registrations that can only ever receive WITHDRAWN-UNSCORED | entrant-written silentgate core + the 7 blank rulings; and a compute box for the corpora |
| **P-DISPOSITION** | **Not a prediction.** It is the self-executing sweep rule itself — no quantity, no threshold, no denominator, no falsification branch | nothing — remove from the list |
| **§9-F3** | Not a CONFIRMED/NOT-MET prediction; a **conditional** clause (docs/43:404-409) | nothing to score |

**P-DIVANIS is the one near-miss worth a second look:** it is the only A9 member whose entire
corpus is local (`divanis_esi.txt` + the 3.5 MB ESI PDF) and whose denominator is already fixed
by written default to all 38 rutile-only rows (docs/43:1898). Zero compute; needs arithmetic plus
one literature resolution (δ from Nørskov 2004), registered deadline **Sep 15**.

---

## 5. Corrections of record this census forces

Each is a claim in a live document that measurement contradicts. Listed rather than silently
fixed, per the project's convention.

1. **docs/72:107-109's "9+ measured-but-unscored"** conflates *unmeasured* with *unscored*. For
   the A9 five, nothing is measured. docs/72 contradicts itself on this at :52 and :142, which
   both say the census is blocked on a detector that does not exist.
2. **docs/72:242** — check 4′ "has no run." False; see §3.
3. **docs/72:230** — G8's "no doc cites it." Self-refuting nine lines above itself.
4. **docs/72:117-118** — P13's failed prior mis-pointed to docs/43:187; it is at **:177-179**.
   The verdict is right, the pointer sends a reader to a different, unscored prediction.
5. **P-BEEF is not a registered prediction at all**, yet holds one of the **six** body-figure
   ledger rows (docs/43:2183). Amendment 10 **does not exist as registered text anywhere** —
   searched all of docs/ (78 files), tasks/, src/, tests/, results/, README.md; the only two hits
   are the 2026-08-15 round-1 and round-2 lit-sweep syntheses, **neither of which is in any
   Zenodo deposit fileset**. Worse, those two give **conflicting criteria** (≥6 of 7 metals vs
   ≥2 of 3) with no dated line electing either. A governance hole distinct from "A10 is late".
6. **"A10 is gated on S0(a)" is a stale blocking clause.** The gate physically passed weeks ago —
   verified on disk: switch (ii) `calculation='ensemble'` emits "BEEFens 2000 ensemble energies",
   the control emits none. Only the verdict line is missing (docs/52:441). Do not repeat it as if
   compute were owed. **A10's deadline is Sep 18 — 15 days out.**
7. **docs/43:1864 (deposited) is factually wrong in one clause.** It names eleven post-Aug-9
   probe families as "present on disk and not in the Aug 9 CSV"; **two of the eleven are in the
   CSV** — `docs/figs/symops_audit.csv:67` (`probe/Cr_basin/s0_OOH.out`) and `:115`
   (`probe/Ni_basin/s0_OH.out`). A correction-of-record candidate against deposited text.
8. **`docs/figs/volcano_endmembers.json` carries RETRACTED DFT columns without self-labelling**
   (Cr 1.726 trapped `s0_O`, Ni 1.751 unconverged). The three superseded parity JSONs do label
   themselves; this one does not. A live quotation hazard.
9. **The A7.1 evidence sentence points at files no document names.** docs/43:1344-1346 forbids
   citing the HP code paper for projector dependence and says "the campaign's own measured
   +1.45 eV is the evidence." That is `runs/hp_tio2` ortho minus atomic = 5.6743 − 4.2251 =
   **1.4492 eV**. Greps for `5.6743` and `6.1635` over docs/, tasks/, src/, results/, tests/,
   README.md return **zero** real hits. A deposited amendment's load-bearing evidence is unnamed.
10. **A5.4 has nothing at all** — no script, no swept column, no surviving-conclusions statement.
    Its one registered negative ("no static water bilayer will be run") holds trivially. Do not
    confuse it with A8.2's non-additivity threshold.
11. **docs/45:79's "slab hp.x one relaunch under 72 h cap RESTORED" is unexecuted.** A repo-wide
    enumeration of every hp.x run — `grep -arl "Program HP" --include='*.out' runs/` — returns
    **35 files: 25 in `runs/hp_tio2`, 10 in `runs/hp_costmodel`**, and no later slab relaunch
    anywhere. The scope line marks S4 EXECUTED while carrying an item that never ran.
12. **The registered U window survived an attempted widening, and that is worth keeping.**
    docs/43:607-608 records the builder trying to widen the P15 gate from **[3.0, 7.0]** to
    **[2.0, 8.0]**; the narrower registered window was re-affirmed. The GO below is scored against
    [3.0, 7.0]. A gate that was widened after the number was known would have been worthless, and
    the record shows it was not.

---

## 6. Five conflicting verdicts already in the tree, ranked by damage

1. **P14 / block 1C: `CONFIRMED` exists only in prose.** CONFIRMED at docs/49:248 and docs/72:102
   — but `grep -ranI 'VERDICT:' runs` returns exactly five artifacts and **none says CONFIRMED**:
   `runs/probe/Cr_hess/…:37` **UNDERPOWERED**, `runs/probe_d02/Cr_hess/…:39` **VOID**,
   `runs/s3/Cr/hessian_analysis_esc_2026-08-24.txt:42` **REFUTED**, plus docs/49:262 **PARTIAL
   PILOT**. Three reconcile (docs/49:259 declares UNDERPOWERED/VOID "a label, not a verdict"
   under the superseded pre-A8.7 instrument; the REFUTED is a *different state*). The unresolved
   part: docs/49:262-266 says banking the re-scored analysis "is the commit step" — **that commit
   appears not to have happened.** So the campaign's second-strongest positive lives in one
   document's prose while every machine-readable artifact on disk disagrees. **This is the single
   most citable inconsistency an auditor could find, and it costs one commit to fix.**
2. **`P-FLOOR-U` is one token string with two live verdicts.**
   `docs/research/2026-08-15-lit-sweep-round2-synthesis.md:55` says **WITHDRAWN** while five
   locations score it **NOT MET at 3 of 6**. Both are right about *different quantities*:
   docs/43:1361 renamed the withdrawn round-1 ratio **P-U-SPLIT** and reused the string for the
   span(c_M)/2 replacement — and only that one line disambiguates. Anyone grepping
   `P-FLOOR-U` + WITHDRAWN lands on a real dated line saying the flagship was withdrawn.
   **Fix: annotate :55 with the rename.**
3. **P9** — docs/41:597 "NOT SCORED. Gas references died" vs :759 "REFUTED, and it moves η the
   wrong way." §6e supersedes §6c and REFUTED is operative; nothing marks :597 as superseded.
4. **P2** — docs/41:590 "NOT RUN. Deck bug" vs :744 "REFUTED by direct DFT." Same pattern.
5. **A7.3's denominator moved under a stable verdict word** — `runs/a0/main/manifest.json:310` and
   `docs/figs/a0_verification_findings_2026-08-29.txt:490` record **3 of 5**; the banked score is
   **3 of 6**. Not a verdict conflict (NOT MET either way, and docs/43:2110 registers in advance
   that no denominator choice flips it), but a grep for "3 of 5" returns a live stale number.

**Also: A7.3's own verdict string is contested.** Seven addenda lines say "NOT MET at 3 of 6"
**bare**, while docs/43:2284 and the A11.R2 instrument at :2088-2095 make 3 of 6 a MIDDLE BAND
count whose registered label is "**SCORED — MIDDLE BAND / NOT MET**, never quoted bare." The
bare phrase as it appears in five countersignatures is arguably the thing docs/43:2646 forbids. A
writing-time decision is owed on which string the report uses.

---

## 7. The body-figure ledger: three of six rows are unreachable

docs/43:2183 names six body rows: **P7, P-PROJ, P-PLS, P-FLOOR-U, P-SYMCOV, P-BEEF**.

- **P-BEEF** — no registration exists (§5 item 5).
- **P-SYMCOV** — no scoreable claim-scope branch; aggregation and the "large" cut unregistered.
- **P-LIT**, a row-in-waiting for the appendix, has four blank fields.

P-DISPOSITION converts each to **WITHDRAWN-UNSCORED** at REPORT LOCK. **One third of the body
ledger is currently unreachable**, and no committed REPORT LOCK line exists yet — 20 `REPORT
LOCK` hits across docs/ and tasks/ are all definitional or forward-looking, so the sweep has
**not** executed and nothing is yet withdrawn.

---

## 8. Stale owed-lists, again — fourteen in `tasks/todo.md` alone

Fourteen open checkboxes in `tasks/todo.md` are closed elsewhere, **mostly later in the same
file**: `:17`+`:502`, `:437`, `:441`, `:736`, `:738`, `:739`, `:751`, `:772`, `:1102`, `:1210`,
`:1220`, `:1227`, `:1330`, `:760`. Anyone re-reading top-to-bottom repeats all fourteen.

Two that bite hardest:

- **`:730` conditionality fact (5)** still says A7.3's Ti rows rest on an "UNGRANTED A6.6
  licence — denominator 6→5". The licence was **granted 2026-08-31** (docs/59:309). The stale
  sentence sits *inside the verdict paragraph itself*, and docs/60:141 carries the same wording.
  **Quote A7.3 from `:1216` or docs/45:31, never from `:730`.**
- **`:738`** asserts "no script in the repo reads a `.lowdin.txt` at all." **355 exist and four
  scripts read them.** Same line's A5.1(a)/(c) claim is retracted at `:1196`.

**And a new place the resolution can hide:** A7.4 gate (f)'s verdict is in a **git commit
message**. Every "grep the whole tree" protocol in this repo misses it. Add `git log --all
--grep` to the resolution-token search, or the next stale-list audit will repeat this one.

---

## 9. What this changes for the plan

1. **docs/72 §9 decision 4 should be rewritten.** "Close the unscored pile" is one free row
   (P15) plus one near-miss (P-DIVANIS, deadline Sep 15), not nine. Everything else needs a
   *dated entrant line* — a scarcer resource than a paragraph.
2. **Score P15 as a BULK GO with its three riders.** It is the cheapest genuine scored row
   available and it is currently under-claimed by its own assessment.
3. **Commit P14's re-scored artifact** (§6 item 1). One commit removes the most citable
   inconsistency in the repo.
4. **Decide P-BEEF before Sep 18.** Either elect one of the two conflicting criteria in a dated
   line and draft A10, or withdraw the body row deliberately. Note the gate it is "blocked on"
   already passed.
5. **Accept WITHDRAWN-UNSCORED deliberately for the rest, and name the pattern in the report.**
   A preregistered report that says "these nine were registered, measured or not, and here is
   why each was not scored" is stronger than one where a reviewer finds nine dated withdrawals.
6. **Add `git log --grep` to the resolution-token protocol** (§8).

---

## 10. Errors made in producing this file

- **My own pass-1 census got the free-row list wrong**, and the refutation pass is what caught
  it. Pass 1 reported P-SPIN-DELTA and P-FLOOR-U-SPIN as scoreable-today on arithmetic that
  ignored a dated line from the same day. Two of my eight enumeration agents also re-imported
  `tasks/todo.md:738`'s A5.1(c) claim — a stale line this project had **already** logged as an
  error. A top-down census inherits the stale lists it reads; only the per-token refutation
  broke that.
- **I briefed the refutation agents with two trap figures that are wrong** — "263 of 1,042 `.out`
  files" and "grep silently skips NUL files" — taken from docs/71 before they were re-measured.
  Both are corrected in docs/71 as of this session (196 of 1,042; grep suppresses the *lines*
  and prints "Binary file … matches", so `-c` and `-l` stay reliable). Neither affected a verdict
  here — no lens depended on either figure — but the briefing was wrong when written.
- **One agent reported the NUL file as holding 1,859 NUL bytes.** A byte read gives **exactly 1**,
  at offset 81,105. docs/71's original "1 NUL" was right.
- The "199 tokens" count is **after** a regex sweep that produced some artifacts (high-numbered
  `P##` strings that are line numbers and pseudopotential fragments). It is a ceiling on the
  namespace, not a count of predictions.
- **Coverage limit, stated rather than papered over:** the 14 families were built from the 38
  candidates that pass-1 flagged as *unscored + data banked*. A registered prediction that pass 1
  wrongly filed as SCORED would not have reached the refutation pass at all. The bottom-up verdict
  map was run precisely to bound that risk and found no such case, but it is the one hole this
  design cannot close from the inside.
