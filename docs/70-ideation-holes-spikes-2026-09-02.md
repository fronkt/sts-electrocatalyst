# docs/70 — Ideation round: holes, verified literature, and where to spike (2026-09-02)

## 0. Status of this document

**This is AI-drafted infrastructure, not a registration.** Nothing here licenses a deck, moves a
threshold, scores a prediction, or amends a deposited section. Every registration-shaped sentence
below is a *proposal for a dated line the entrant writes*, and is marked as such. Per docs/43 A7.7
the entrant paraphrases; no sentence of this file is report prose, and per the STS 2027 Research
Report Guidelines item 1 (quoted verbatim in §4.1) the report itself is written without generative
AI.

Two facts in the brief that generated this round are **stale**, and are corrected here from the
tree:

| the brief said | the tree says (2026-09-02) | source |
|---|---|---|
| Balance 64,977.8 CPU SU; queue empty | **59,761.1 CPU SU**; queue empty | `tasks/todo.md`, "A11.R6 LADDER EXHAUSTED" block; docs/68 §11 |
| A11.R6 rung ladder queued/next; 16 rung-1 decks built, no `.out` in the tree | **Both rungs RAN. 0 of 16 converged at each rung. Ladder total 5,216.7 SU. Nothing in AMENDMENT 11 is unrun.** | docs/68 §11; `tasks/review/a7_3_spin_census_2026-09-02_LADDER-EXHAUSTED.json` |

This matters beyond bookkeeping. Two of the surviving ideas (the fixed-spin-moment scan, the
U-continuation chain) were pitched to run *before* the ladder spent and to *register a prediction
of its outcome*. That option no longer exists, and a prediction of an observed outcome would be a
pre-registration violation rather than a rigor gain. Both are re-scored in §5 on that basis.

---

## 1. Purpose and provenance

**Workflow** `wf_10c6483e-8a7`, run 2026-09-02. Design: 10 literature dimensions × (sweep +
adversarial source-verification), 6 ideation lenses, one critic per idea, and this synthesis.

**Agent accounting, as recorded by the entrant in `tasks/todo.md`:** first pass 61 of 100 agents
completed; 39 died on the session limit (31 verifiers, all 6 ideation lenses, the synthesis and the
completeness critic), so docs/70 was not written on that pass. Resumed 2026-09-02 05:32 UTC from
cache with only the 39 re-run; a third resume produced this file. **Read the workflow's completeness
critic before trusting this document** — that instruction is the entrant's own and it stands.

**What reached the synthesizer:** 10 dimension digests, a 12-item audit of an external note, 18
surviving ideas with per-idea critiques, and 13 rejected ideas with reasons. 31 ideas were
generated; 13 were killed by their critics before reaching this file.

### The verification rule used here

1. **Repo claims** carry a `path:line` pointer. Every claim a ranking or a spike depends on was
   re-read against the tree by the synthesizer, not taken on trust from the upstream agent. Where an
   upstream claim failed that re-read, the failure is recorded in place.
2. **Literature claims** are *carried from the dimension agent that opened the source* unless marked
   **[SYNTH-OPENED]**. Carried claims are usable; they were not independently re-opened here, and
   §4.2 lists the ones the verification pass already found wrong.
3. **Sources the synthesizer opened in this session (4):** arXiv:2403.10028 (Hiraishi 2024),
   arXiv:2310.06909 (Smolyanyuk 2024), arXiv:2601.21056 (Warford 2026), and the STS 2027 *Research
   Report Guidelines* PDF, read in full (2 pp.).
4. **Numbers are re-derived where cheap.** Hole H-3 and spike S-4 rest on an interpolation computed
   from `docs/figs/a0main_readout.json` in this session, and on per-SCF wall times read off five
   banked `.out` files. Both derivations are shown so they can be checked.
5. **Errors the synthesizer made and caught are recorded, not silently fixed.** On first read I took
   the `crossings` field of `a0main_readout.json` to be the pls crossing. It is not:
   `src/dft/a0main_readout.py:192` defines `crossings()` against `APEX`, the volcano-apex crossing at
   D = 1.6 eV. The pls flips live in `pls_flips` / `a7_2.flip_brackets`, and **no pls crossing is
   located anywhere in the banked readout.** That correction is what produced H-3, the cheapest
   high-value hole in this file.

---

## 2. The external note, item by item

**Net: 0 of 12 items identified an unknown defect.** Three (5, 9, 10) are true and already known;
one (6) is flatly false; four (1, 2, 4, 8) are stale readings of superseded repo text. The note's
real value is that items 9–12 name the four standing risks correctly.

| # | Item (abbreviated) | Verdict | The line that decides it |
|---|---|---|---|
| 1 | `upscale=1.0` is "the single highest-value call"; 3 rows burned ~6,800 SU | **PARTLY TRUE; framing SUPERSEDED** | R1 is open (`tasks/todo.md:606`, `:681`), but docs/45:1652-1657 already downgraded it — it "trims ~15 % off the healthy ones" (35 of 236 iterations). docs/45:1785-1792: `upscale` never engaged on the 3 remaining S3 failures, so it is *irrelevant to every one of them*. The ~6,800 SU is rounds 4–9 in total, not those three rows. |
| 2 | Co U-ladder built but never submitted | **FALSE on compute; TRUE on scoring** | `runs/probe/Co_uladder` holds 12 `.in` **and 12 `.out`**, each "JOB DONE" + "convergence has been achieved" (Vast, 2026-08-09); docs/51:17 confirms. Stale source: `tasks/todo.md:695`. Co is genuinely outside the A0 six-metal roster and has no converged `*OOH` at any U — and no registered scorer consumes a Co ladder. |
| 3 | One held-out DFT point (Cu) | **PARTLY TRUE** | "Held-out DFT points in the entire project: **zero**" (docs/40:34, re-read). But Cu is *ruled on*: A7.5 puts CuO₂ on the exclusion row, docs/43:1408-1409 lists it under Exclusions, docs/51:24 marks `runs/Cu_slab` SUPERSEDED. Reviving it is an amendment, not a launch. |
| 4 | RPBE half-finished; gas refs stalled | **STALE** | `runs/probe/Ru_rpbe` and `runs/probe/Ir_rpbe` each hold 10 decks and 10 `.out`, all JOB DONE and converged; gas refs reran 2026-08-09. docs/41:759 already reads **"P9 — RPBE: REFUTED, and it moves η the wrong way."** The open functional item is A10/P-BEEF, not RPBE. |
| 5 | Warm-start `starting_magnetization` from the parent moment is untried | **TRUE** | `tasks/todo.md:692`; docs/45:1701-1706, :1796-1799. Scope is 3 S3 rows at ~13 SU per single-SCF child. Density-seeded children (`startingpot='file'`) *were* tried — a different warm start. |
| 6 | ΔG may be missing ZPE/entropy (~0.2–0.4 eV) | **FALSE** | `src/hea_oer/referencing.py:18` — `ZPE_TS_CORRECTION = {"OH": 0.35, "O": 0.05, "OOH": 0.40}` (Man 2011 / Valdés 2008), applied in `delta_G()` and consumed by every DFT scorer. Re-read this session. Residual: the constants are borrowed, not computed in-house — no ph.x table was delivered. |
| 7 | Extend the Mn AFM method to Fe (hematite is AFM) | **PARTLY TRUE, mis-targeted** | Fe is a thin A7.2 leg but is **not** one of the 3 robust members (docs/60:97-101). "Hematite" occurs nowhere in the repo; α-Fe₂O₃ is corundum and says nothing registered about rutile FeO₂, which docs/43:1405 registers as a MODEL PHASE. docs/67 §1 firewalls the arm from A7.2/A7.3 in any case. |
| 8 | Solvation / second-code U / SECOND_SEED_CROSSED are low priority | **PARTLY TRUE — each is DECIDED, not merely deprioritised** | Solvation killed (docs/44:78-80), carried as a TRANSFERRED row; no VASP path exists (docs/43:1834); SECOND_SEED_CROSSED **resolved** by Frank's dated line `[AFM-SCOPE RESOLVED 2026-08-30: STANDALONE_FOUR]` (`tasks/todo.md:780`). Only the Xu-repair (a)/(b) disposition is genuinely open (docs/43:1938). |
| 9 | RISK: zero physical results caps placement | **TRUE — with a correction to docs/18** | docs/18:59-65; `results/r4_melt_list.json` mtime 2026-08-05, unchanged. **But docs/18 is dated 2026-06-26 and its cap is an inference from one precedent.** See H-6 and §4.1 (sts-judging): three compute-only DFT *Finalists* exist and four consecutive first places were computational. |
| 10 | RISK: the one positive claim is withdrawn; the story is a methods critique | **TRUE** | `tasks/todo.md:24-30`; docs/41:631. Nuance: A7.2 P-PLS is a CONFIRMED positive registered prediction, and the Ir symmetry-trap fix (η 0.781 → 0.490 V) is a positive method result. |
| 11 | RISK: A7.2 rests on two single rows; the Ru A7.3 near-miss is unpriceable | **TRUE, and now closed by measurement** | `a7_2.census_robustness` (re-read): Fe `rests_on_single_row: true`, carrying margin **81.72 meV** at U = 9; Ru likewise at 44.3 meV. docs/68 §11: no spin-polarised Ru solution exists at U = 9 under three mixing settings — a *measured* sentence now, not a provisional one. |
| 12 | RISK: the HEA screen has had far less adversarial scrutiny | **PARTLY TRUE** | DFT tier of record n = 7 (docs/36:15); 12 candidates screened; held-out zero (docs/40:34); melt list unfrozen. The note conflates the n=7 tier with the 12 screened candidates. The asymmetry is real: no refute pass over docs/36–40 since 2026-08-05. |

---

## 3. Holes in the project, ranked

Ranked by (damage to defensibility × probability a competent reader lands on it) ÷ cost to close.
"Before Oct 15" is answered against the *writing* window; the operative deadline is the entrant's
REPORT LOCK line, backstop **Nov 5 2026 8:00 pm ET** (docs/43 dated addendum 2026-08-31, :2249-2265).

### H-1 — The RuO₂ antiferromagnetism premise is refuted, and the repo asserts the overturned claim as fact — CRITICAL

The campaign states, in three places including a code comment that generated decks, that RuO₂ is an
itinerant antiferromagnet on the authority of Berlijn et al., PRL 118, 077201 (2017):
docs/41:269 and :276 ("*For RuO₂ that is factually wrong*"), docs/41:513,
`src/dft/probe_decks.py:251-252`, `src/dft/qe_slab.py:49`. A grep for
`altermagnet|muSR|Hiraishi|Kessler|Smolyanyuk` across `docs/` returns **one** hit, docs/68:311,
and it is a *prohibition* on discussing altermagnetism, not a citation. The 2024–2026 reversal is
absent from the record. This premise is load-bearing: gate (h) returned 4/4 ADOPT_AFM on the RuO₂
anchors (docs/63:38-43 quoting docs/43:1638-1644).

*Severity:* critical — a field reviewer or an in-domain judge lands on it in one read, and the
project's whole thesis is that unexamined premises move answers.
*Cheapest closure:* a **dated correction of record** (not an edit — docs/41 is a pre-registration) plus
one docs/45 §A row, "RuO₂ magnetic ground state — literature reversed 2024". **0 SU, 2–3 h.**
*Before Oct 15:* **YES.**
*Note:* the correction *strengthens* the campaign. Its production convention for Ru is nspin = 1, which
is what the 2024 literature supports; and Xu 2015's own deposited RuO₂ ladder was run at nspin = 1
with `starting_magnetization = 0` (carried, ruo2-magnetism dimension). The correction converts an
apology into an alignment.

### H-2 — A deposited prediction rests on a premise the repo refuted three days earlier, and no withdrawal exists — HIGH

docs/43:363-366 (§7 prediction 3, deposited 2026-08-09) registers "*`omat` is trained on OMat24,
which does not share that convention*" and makes the discriminating test Δρ(MACE) more negative than
Δρ(omat). docs/40:108-119 — dated **2026-08-06, three days earlier** — establishes the opposite from
the source ("following Materials Project defaults", "MPRelaxSet"), concluding "*Independence gained
on the U axis by switching MACE → omat is zero*"; `tasks/todo.md:360-363` banks it as CONFIRMED.
Externally, the Warford 2026 abstract **[SYNTH-OPENED]** names MPtrj, Alexandria **and OMat24**
together as encoding the Materials Project's selective U. docs/43:373 says "Nothing in this section
may be revised after the deposit" — so the instrument is a *disclosure*, not a revision. Grep for
"P18" across docs/44–68 and `tasks/todo.md`: no withdrawal recorded.

*Severity:* high — a live defect inside a deposited pre-registration, in a project whose credibility
is the pre-registration.
*Cheapest closure:* one dated paragraph recording that prediction 3's premise was already refuted at
deposit time, citing docs/40 §1.4, and stating what the prediction can and cannot now score.
**0 SU, 1–2 h.** *Before Oct 15:* **YES.**

### H-3 — A7.2's registered "first-class deliverable" is not delivered: no pls crossing is located anywhere — HIGH, and cheap

docs/43:1351-1353 registers: "**The U at which each metal's pls flips is a first-class
deliverable.**" The banked readout delivers *brackets*, never a located U. From
`docs/figs/a0main_readout.json` (`a7_2.flip_brackets`, re-read this session):

| metal | flip | bracket | width |
|---|---|---|---|
| Cr | 3 → 2 | [3.5, 4.0] | 0.5 eV |
| Ru | 3 → 2 | [7.5, 9.0] | 1.5 eV |
| Ir | 3 → 2 | [3.0, 4.5] | 1.5 eV |
| Mn | 3 → 2 | [0.0, 1.5] | 1.5 eV |
| Mn | 2 → 1 | [6.0, 7.5] | 1.5 eV |
| Fe | 2 → 1 | [7.5, 9.0] | 1.5 eV |

Cr is narrow only because it is the one metal on the 0.5-eV ladder (19 points); the other five run on
8-point grids at 1.5 eV spacing. docs/66 §6 item 1 already names the fix "**the single highest-value
phase-2 item**" and says in terms that "the endpoint-only re-read detects a flip but cannot locate
the crossing" — but prices it only in its expensive, spin-equalised form (~360 SCFs, 1,800–6,840 SU).

**Zero-compute interim, computed here.** ΔG₂ − ΔG₃ (and ΔG₂ − ΔG₁ for the 2 → 1 flips) is smooth in U
and changes sign exactly at the flip. Linear interpolation inside each bracket, from the banked rows:

| metal | flip | f(lo) (eV) | f(hi) (eV) | interpolated U\* |
|---|---|---|---|---|
| Cr | 3→2 | −0.0981 | +0.1844 | **3.674 eV** |
| Ru | 3→2 | −0.1536 | +0.0443 | **8.665 eV** |
| Ir | 3→2 | −0.0937 | +0.0446 | **4.017 eV** |
| Mn | 3→2 | −0.3221 | +0.3373 | **0.733 eV** |
| Mn | 2→1 | +0.0095 | −0.1359 | **6.098 eV** |
| Fe | 2→1 | +0.0683 | −0.0817 | **8.183 eV** |

One result falls straight out and is worth a sentence in the report on its own: **Mn's second flip
sits 9.5 meV from the U = 6.0 grid row** — inside the NM-vs-AFM class (33–64 meV) and an order of
magnitude inside the 1×1 cell class (0.11–0.36 eV). That crossing is *not resolvable by this
protocol*, which is the thesis in miniature.

*Severity:* high — it is the one prediction that CONFIRMED, and its own registered deliverable is
under-delivered on 5 of 5 flipping metals.
*Cheapest closure:* the interpolation table above, at **0 SU**, plus ~24 SCFs to test it (§6 S-4),
**~150–600 SU**. *Before Oct 15:* **YES.**

### H-4 — The Sep 20 six-row displacement and the claim sentence are undecided, with 8–9 claimants — HIGH (procedural)

docs/43:1930 lays out the arithmetic: P7, P-PROJ, P-PLS, P-FLOOR-U, P-SYMCOV, P-BEEF — "**six: the
cap is reached before A9 adds anything**", with P-XU proposed for the body. docs/43:2182-2183 keeps
the ledger at six and puts A11's two new claimants in the appendix. The displacement itself and the
claim sentence are "the entrant's, in writing before Sep 20" (docs/43:1950; `tasks/todo.md:760`).
Every downstream presentation decision — including the §6 S-2 figure — waits on this.

*Cheapest closure:* one dated line. **0 SU, 3–6 h of deciding.** *Before Oct 15:* **YES** (Sep 20).

### H-5 — STS disqualification surfaces are unimplemented — HIGH (compliance), near-zero cost

From the STS 2027 *Research Report Guidelines* **[SYNTH-OPENED, read in full]**, verbatim:

- item 1: "*The Student Researcher is required to write the paper without the use of generative AI
  (ChatGPT or other programs).*"
- item 2: "*Every single image, graph, table, chart, etc. that appears in the Research Report must be
  cited per the Citation Guide in Appendix 3 on page 33. This includes images created by the Student
  Researcher. Failure to cite an image could result in disqualification.*"
- item 4a: "*The paper should be 20 pages or less … Pages of content beyond page 20 … will not be read
  or considered.*"  item 4e: "*Appendices count toward the 20-page limit.*"
- item 4f: "*Entrants should generate their reference lists without the use of AI, which is known to
  hallucinate and create fake or altered references. Discovery of a fake reference will result in
  disqualification.*"
- closing: "*Adults reviewing research reports should suggest areas for improvement, but not provide
  the student with replacement text or rewrite any portion of the entry.*"

The repo has no citation-resolution gate and no figure-citation checklist. Given how much of this
campaign's literature arrived through LLM sweeps — and that this project's own memory rule records a
**17 % unusable rate on LLM literature findings, including one inverted central claim and one
fabricated attribution attached to correct numbers** — an unresolved reference is a live
disqualification risk, not a hypothetical one.

*Cheapest closure:* a DOI-resolution pass over the bibliography (every entry resolves at
`api.crossref.org/works/{doi}` with a title match) plus a figure-by-figure citation checklist.
**0 SU, 3–5 h.** *Before Oct 15:* **YES.**

### H-6 — No physical result, no re-rank code, and a partial S8 is worse than none — HIGH (placement)

`tasks/todo.md:267` — "[~] **F. BUILT, awaiting Frank's freeze decision**"; `:286` — the melt list is
"deliberately NOT regenerated" until freeze; `:488` — "Melt decision at FWM — Frank's call".
`results/r4_melt_list.json` is unchanged since 2026-08-05. A grep for `rerank|re-rank` across `src/`
returns **no file**, yet docs/45:82 makes the re-rank gate a precondition of the freeze. No ingot has
been melted.

The eligibility rule makes this sharper than "we might not finish". Verbatim **[SYNTH-OPENED]**:
"*Students must have completed an independent scientific investigation and have results to report.
Research proposals, **investigations not yet completed**, literature reviews and essays are not
eligible for this competition. Students may not submit additional research after the application
deadline.*" A half-executed melt→measure chain does not add a partial credit; it adds an
incompleteness the report has to explain.

**Correction to docs/18, which the entrant should make before using it to decide.** docs/18:59-65
infers a Scholar cap from one precedent (Hirshorn 2026). The sts-judging dimension (carried) found
**three compute-only DFT Finalists** — Guan 2021 (DFT methane-activation catalyst), Iyer 2021
(first-principles Cr/Mo-doped VOPO₄, published as Iyer & Goddard, *J. Phys. Chem. C* 125, 275-282,
2021), Andreasen 2022 — and **four consecutive computational first places** (2023 Moudgal, 2024
Rajaram, 2025 Paz, 2026 Hill), plus a 2025 ninth place ($50,000) for an electronic-structure method
whose headline was a 0.6 % accuracy gain. The honest reading is: make-and-measure is **not** a
Finalist precondition, though the 2026 cycle's chemistry/materials Finalists were all experimental.

*Cheapest closure:* a **dated S8 go/no-go**. **0 SU, 1–2 h to decide.**
*Before Oct 15:* the *decision*, yes. A complete re-rank → freeze deposit → melt → OER measurement →
writeup chain by REPORT LOCK is the open question (§7 Q-5).

### H-7 — The hidden-knob magnitudes have never been put on one axis, and the joint effect is unmeasured — MEDIUM-HIGH

The thesis sentence exists as a 4-row text table (docs/44 §7) and a ~30-row prose ledger
(docs/45 §A–B). `docs/figs/` holds parity, volcano and Pourbaix PNGs only — **no cross-knob figure
exists**. Worse, the crossed factor sets that exist are thin: cell × U on **Cr only**, projector at a
**single Cr/U point**, spin × U at endpoints for **three metals**. So the *joint* effect of the knobs
is unmeasured, and the ledger's per-row magnitudes may not add.

*Two traps that must be handled in the figure or it does more harm than good.* (i) The naive
conversion "energy/2 for a single-rung shift" is **wrong**: under the imposed 4.92 eV telescoping, a
shift *d* on one intermediate moves |Δη| by *d* if that state carries the PLS rung and by 0 otherwise
— never *d*/2. Only c_M/2 is a legitimate halving, and only for pls ∈ {2,3}, which A7.2 CONFIRMED is
violated somewhere in U by 5 of 6 metals. (ii) Every ledger magnitude is a per-class **maximum on one
metal** (projector on Cr, trap on Ir at 1×1 where it collapses to −0.018 eV at 2×1v, geometry on Fe),
while 0.03–0.08 V is a *typical* separation. Max-versus-typical inflates the ratio by construction and
is the first thing an adversarial reader will say.

*Cheapest closure:* the magnitude ladder as a status-coloured bar chart with per-bar conversion
printed, **ranges not maxima**, MEASURED / BOUNDED / TRANSFERRED / NOT MEASURED tokens, and an
explicit "the joint effect is unmeasured; these are one-factor-at-a-time magnitudes off one baseline"
limitation. **0 SU, 12–20 h + entrant adjudication.** *Before Oct 15:* **YES.**

### H-8 — Neither count rule has an operating characteristic, and "3 of 6" fell in an undefined band — MEDIUM

A7.3 registers ≥4/6 CONFIRMED, ≤1/6 FALSIFIED (docs/43:1361-1368); the outcome was 3/6, which
docs/60 §6 fact 4 concedes is "a band the registration never defined". A11.R2 fixed the *vocabulary*
(SCORED — MIDDLE BAND / NOT MET, never quoted bare, docs/43:2086-2111) but nobody computed how large
the band is. Exact binomial at p = 0.5 per metal: A7.3's middle band is 35/64 = **0.547** at n = 6
(20/32 = 0.625 at n = 5); A7.2's ≥3/6 has P = 42/64 = **0.656**.

*Honest caveats that must travel with those numbers, or they are worse than nothing.* (a) p = 0.5 is
"half the metals flip", **not** a no-effect null; the no-U-effect null is p → 0, where 5/6 and 3/6 are
not chance events. Stated carelessly ("A7.2's bar was beatable two times in three") this is a
self-inflicted wound on the entry's only CONFIRMED prediction. (b) The six metals are not independent
trials — they share gas references, code and protocol. Positive correlation **shrinks** the middle
band and **inflates** both false verdicts (beta-binomial at ρ = 0.33: middle 0.286, spurious CONFIRMED
0.451), so the correlation caveat is worse for the rules, not softer.

*Cheapest closure:* two footnote numbers plus one resolution sentence, subordinated to A11.5 (the
as-built 3-of-6 is the headline and no sensitivity can promote it). **0 SU, 3–4 h.**
*Before Oct 15:* **YES.**

### H-9 — The ledger has no pseudopotential/basis class, and A6.3's headline crosses two PP families — MEDIUM

UPF census over `runs/a0/main` (re-read): `Ru_ONCV_PBE-1.0.oncvpsp.upf` ×32 — the only norm-conserving
metal — against `Ir_pbe_v1.2.uspp` ×32, `cr_pbe_v1.5.uspp` ×76, `mn_pbe_v1.5.uspp` ×32,
`ti_pbe_v1.4.uspp` ×28 and `Fe.pbe-spn-kjpaw_psl` ×39. docs/45 §A has **no pseudopotential row**
(grep: 0 hits). A6.3's headline — η(Ir) − η(Ru) = +0.464 V at U = 9, scored as clearing "every
measured error class" (docs/58:88-102) — is a cross-metal comparison between a GBRV ultrasoft and an
ONCV norm-conserving potential, and no such class exists in the list it clears.

*Cheapest closure:* one TRANSFERRED / NOT MEASURED sentence naming the confound (**0 SU**), or a
12-SCF Ru GBRV control at the three Ru anchors (**~30–60 SU**) reframed as an *anchor-pair
comparability control*, not a new error class. Note the repo's own convergence sweep already locked
80/640 Ry and the k-grid with both knobs flat to < 1 meV/atom (docs/23 §4), and gate (i) passed a
second cutoff ladder at 1.09–1.19 meV/atom — so the cutoff and k-mesh legs of any such arm are
already answered and should not be re-run.
*Before Oct 15:* **YES.**

### H-10 — The scored `*OOH` member is not the lowest banked conformer, and one banked "conformer" is a desorbed state — MEDIUM

docs/54:422-424 item 10 and docs/56:506-507 F(2) leave the scored-member change "undecided". The
bridge-protonated `*OO–H` was computed at production U only, for Cr/Ir/Ru, and never entered an η(U)
row. Measured offsets against the 1×1 off-arm minimum: Ru −0.111 eV, Ir −0.019, Cr −0.021 (carried).
**New this round, and it corrects a banked sentence:** the Cr "oosh" final geometry has O–O 1.227 Å
with both O atoms 3.09/3.77 Å from the nearest Cr and H on a bridging O — a physisorbed O₂ + H_br
state, not an `*OOH` conformer. docs/54 item 10's "lowest banked 1×1 `*OOH` on all three metals" is
therefore **wrong for Cr**, and scoring it as an `*OOH` member would put an O₂-release energy into
c_Cr. *(Carried from the idea critic; the geometry was not re-measured by the synthesizer — verify
before writing the correction.)*

*Cheapest closure:* correct docs/54 item 10 (**0 SU**); optionally 1 SCF for the Ru U = 9 conformer
endpoint (**~2–5 SU**; the U = 0 endpoint already exists, since Ru production carries no HUBBARD
card). *Before Oct 15:* **YES.**

### H-11 — Zero held-out points, and the screen's ranked statistic has never been tested — MEDIUM (and expensive)

docs/40:34: "Held-out DFT points in the entire project: **zero**." The screen's actual ranked
statistic is a min over 12 sites on a mixed-cation surface; the n = 7 tier cannot test it at all.

*Cheapest closure: there is none that is cheap.* Seven DFT single points on a 72-atom four-3d-species
nspin = 2 +U slab price at **1,750–6,600 SU**, and the project's own basin discipline (second seeds,
GATE-1 children) pushes that to **4,000–15,000 SU** before it is bankable. Co/Ni `*OOH` already fail
4–7 times each in 20-atom cells, so UNSCORED is the modal outcome; and the target is a proxy whose
Fe/Co/Ni rutile lattice constants are "model values on the rutile trend"
(`src/hea_oer/surfaces_rutile.py:33`) for phases that do not exist.
*Before Oct 15:* technically yes, practically no. **Recommend NOT** — see §6.

*A 0-SU partial substitute exists and is worth doing* (§5, idea I-11): the site-tail claim in
docs/37 §1 is an order statistic. Every clean candidate's "best site 0.44–0.60 V below the site mean"
is within ~0.1 V of the expected minimum of 12 draws from that candidate's own site spread, and
ρ(η_best, −η_std) = +0.886 over the 6 clean candidates. Also unreported: **all three activity picks
win on a Cr cus site**, and MACE's own CrO₂ endmember (0.353 V) lies below every HEA η_best — so
under a matched predictor no HEA beats the Cr endmember. *(Carried; arithmetic reproduced by the idea
critic, not by the synthesizer. Note the critic's correction: the self-normalised constant at n = 12
is −1.742, not −1.63.)*

### H-12 — Protocol non-uniformity on `conv_thr`, and the methods sentence is wrong as written — MEDIUM-LOW

`upscale` is set in no deck; QE's default 100 silently tightens `conv_thr` to a 1e-8 floor during a
relax (docs/45:339-341). 39 banked rows therefore converged at 1e-8 while the deposited protocol says
1e-6, and 10 of 60 non-convergent outputs (17 %) had already met the registered threshold
(docs/45:1414-1436). No open row's *outcome* depends on this (docs/45:1785-1792).

*Cheapest closure:* one dated line declaring `upscale` for any future relax deck, plus the methods
sentence correction the entrant re-authors (`tasks/todo.md:695`). **0 SU.** The ~50 SU confirming
pilot is optional and would demonstrate only the already-measured 15 % trim. *Before Oct 15:* **YES.**

### H-13 — The S3 tail has an untried lever and no disposition — LOW-MEDIUM

Three rows remain (Co `s0_O__2x1v_mir`, Co `s0_OH__2x1v_off`, Ni `s0_OOH__2x1v_mir`). Every resume
kept the **cold** `starting_magnetization`; none carries its parent's converged moment
(`tasks/todo.md:692`; docs/45:1701-1706).
*Cheapest closure:* **0 SU** — record A8.4 rung-(iii) NOT_CONVERGED / A8.3 MULTISTABLE; or **~40 SU**
(3 single-SCF children at a parent-derived seed) behind a dated line, since it changes a registered
input. *Before Oct 15:* **YES.**

### H-14 — The S1 silentgate core is entrant-written, unstarted, and blocks the S2 census — LOW-MEDIUM (authorship)

docs/45:75 — S1 is "gated only on the entrant-written core (A9.1 authorship boundary)"; AI may write
tests, fixtures, CI and packaging, and did (docs/45:1853, CI harness built 2026-08-27). The core
itself is not started.
*Cheapest closure:* the entrant writes it. **0 SU, hours unknown.** *Before Oct 15:* entrant-dependent
— and if it will not be written, the S2 census should be withdrawn explicitly rather than left owed.

---

## 4. Verified literature

### 4.1 Surviving claims, by dimension

Carried from the dimension agents except where marked **[SYNTH-OPENED]**. Each entry gives the claim,
the source, and the sentence relied on.

**(1) ruo2-magnetism — the most consequential dimension in this round.**

- Bulk RuO₂ is nonmagnetic by direct probe. **[SYNTH-OPENED]** Hiraishi, Okabe, Koda, Kadono, Muroi,
  Hirai & Hiroi, *Phys. Rev. Lett.* **132**, 166702 (2024), arXiv:2403.10028 — abstract: "*The spin
  precession signal due to the spontaneous internal magnetic field B_loc, which is expected in the
  magnetically ordered phase, was not observed in the temperature range 5–400 K*"; upper limit on the
  ordered Ru moment **4.8(2)×10⁻⁴ μ_B**, and "the AFM order, as reported, is unlikely to exist in the
  bulk crystal". Corroborated (carried) by Keßler et al., *npj Spintronics* (2024),
  DOI 10.1038/s44306-024-00055-y: ≤1.14×10⁻⁴ μ_B/Ru bulk, ≤7.5×10⁻⁴ μ_B/Ru films, with **multiple
  scattering** identified as the source of the earlier neutron signal.
- The +U magnetism of RuO₂ is a parameter artifact. **[SYNTH-OPENED]** Smolyanyuk, Mazin,
  Garcia-Gassull & Valentí, *Phys. Rev. B* **109**, 134424 (2024), arXiv:2310.06909 — abstract: "*we
  show that the electronic properties of stoichiometric RuO₂ are described in terms of a smaller
  Hubbard U within DFT+U than the value required to have magnetism*". **Scope note:** the specific
  onset values (U_eff ≈ 1.06 eV onset, ≈1.23 eV ground state) are **body-text numbers reported by the
  dimension agent from the PDF; they are not in the abstract and were not re-verified here.** Use the
  abstract sentence for any load-bearing statement.
- Berlijn et al. 2017 — the paper the repo cites as establishing AFM — themselves report that U = 4 eV
  opens a 0.5 eV gap "contradicting the experimental fact that RuO₂ is a metal" (carried, OSTI OA
  copy).
- Xu, Rossmeisl & Kitchin's deposited RuO₂ ladder (Zenodo 10.5281/zenodo.12635, CC0) ran **nspin = 1,
  `starting_magnetization = 0`, `U_projection_type = 'atomic'`** on 2-layer slabs at 40/500 Ry
  (carried, deposit opened) — i.e. the field's reference Ru rows share this campaign's nspin = 1
  convention and were never allowed to polarise.

**(2) scf-magnetic-oxides.** Meredig, Thompson, Hansen, Wolverton & van de Walle, *Phys. Rev. B* **82**,
195128 (2010): which self-consistent DFT+U solution is reached depends on "(i) the magnitude of U;
(ii) initial correlated orbital occupations; (iii) lattice geometry; (iv) whether lattice symmetry is
enforced on the charge density; and (v) even electronic mixing parameters", differing "by hundreds of
meV per atom". Barat, Levitt & Torrent, arXiv:2606.26693 (2026): spin-channel SCF stalling near a
magnetic instability comes from a near-zero dielectric eigenvalue, and QE's `mix_rho` applies TF /
local-TF screening to the **total charge only, never the magnetisation** — so `mixing_mode` cannot
damp a spin mode. Tompsett, Middlemiss & Islam, *Phys. Rev. B* **86**, 205126 (2012): for β-MnO₂ the
Dudarev U_eff form predicts a gapless ferromagnet (FM below AFM by 48 meV/f.u.) while explicit
U = 6.7 / J = 1.2 eV reverses it to AFM by 20 meV/f.u. with a ~0.8 eV gap.

**(3) hubbard-u-determination.** Projector pairing is quantitative and code-specific: β-MnO₂ U differs
by ~1.4–2.2 eV between atomic and ortho-atomic projectors (Mahajan, Timrov, Marzari & Kashyap,
*Phys. Rev. Materials* **5**, 104402, 2021), and rutile TiO₂ gives Ti-3d U = 3.81 eV atomic vs 6.10 eV
ortho-atomic (Kirchner-Hall, Zhao, Xiong, Timrov & Dabo, *Appl. Sci.* **11**, 2395, 2021) — bracketing
this campaign's own +1.45 eV, and showing the registered [3.0, 7.0] eV Ti gate is **projector-blind**.
Environment spread of linear-response U is 0.6–1.2 eV 1σ per element (Moore et al., *Phys. Rev.
Materials* **8**, 014409, 2024, Table II: Mn 4.953 ± 0.635, Fe 4.936 ± 0.700, Ni 5.622 ± 1.221).
U-sensitivity is a **valence-change** effect (Tripkovic, Hansen, García-Lastra & Vegge, *J. Phys.
Chem. C* **122**, 1135, 2018: LaCrO₃ ΔE(*O) 0.80 → 2.82 eV over U = 0–5 eV as Cr goes +3 → ~+5, while
valence-conserving steps are nearly U-independent). **Citation rule already in the repo and worth
re-stating:** docs/43:1344-1346 forbids citing the HP code paper (10.1016/j.cpc.2022.108455) as
evidence for projector dependence of η — the campaign's own +1.45 eV is the evidence.

**(4) beyond-dftu.** A hybrid-vs-semilocal switch flips the same index P-PLS scores: on IrO₂(110) the
potential-limiting step moves from ΔG₄ (RPBE) to ΔG₂ (HSE06, α = 0.305) and the material ordering by
ΔG₂ is not preserved (Gono & Pasquarello, *J. Chem. Phys.* **152**, 104712, 2020). HSE cannot arbitrate
U — results are as sensitive to α as to U (Tripkovic 2018). The XC floor this campaign has not
measured: GGA/vdW-DF-class functionals deviate from RPA by ~0.2 eV on average and up to ~0.6 eV for
individual surfaces on 200 adsorption reactions (Schmidt & Thygesen, *J. Phys. Chem. C* **122**,
4381-4390, 2018) — **metals only, no oxides**, so it is a transfer, not a measurement. Oxide formation
energies per O: PBE MAE 0.55, BEEF-vdW 0.40 eV, with TiO₂ under-bound by 0.45–0.47 eV/O while RuO₂ is
within 0.04–0.05 (Jauho, Olsen, Bligaard & Thygesen, *Phys. Rev. B* **92**, 115140, 2015). Every
meta-GGA/hybrid arm is gated on relinking QE with libxc — **not linked** (docs/42:22).

**(5) spin-state-oer.** At plain PBE the clean RuO₂(110) 1×1 slab is magnetic: spin-polarised 38 meV
per slab cell below non-magnetic, Ru-bridge +0.60 μ_B / Ru-cus −0.24 μ_B (Torun, Fang, de Wijs & de
Groot, *J. Phys. Chem. C* **117**, 6353, 2013) — so **surface** Ru moments are not excluded by the bulk
μSR bounds, and the H-1 correction must be scoped to bulk. Liang, Bieberle-Hütter & Brocks, *J. Phys.
Chem. C* **126**, 1337-1345 (2022): AFM RuO₂(110) gives η = 0.41–0.49 V vs NM 0.63–0.67 V on mixed
O/OH terminations — a ~0.2 V magnetic-treatment effect, **not** the 0.4–0.5 V the repo's docs/28
paraphrase claims (see §4.2). Fixed-spin-moment (Schwarz & Mohn, *J. Phys. F* **14**, L129, 1984) maps
E(M) including the barrier between minima; QE implements the exact constraint via `tot_magnetization`.

**(6) mlip-sensitivity.** **[SYNTH-OPENED]** Warford, Thiemann & Csányi, "Better without U: Impact of
Selective Hubbard U Correction on Foundational MLIPs", arXiv:2601.21056 (28 Jan 2026) — abstract:
"*fMLIPs trained on large datasets such as MPtrj, Alexandria, and OMat24 encode inconsistencies from
the Materials Project's selective use of the Hubbard U correction*", producing spurious repulsion
between U-corrected metals and O/F species; MACE-OMAT and MACE-MPA named. **Note: arXiv lists no
journal reference; the "Mach. Learn.: Sci. Technol. 7, 035033 / DOI 10.1088/2632-2153/ae6be5" citation
carried by two dimension agents is NOT confirmed on the arXiv record and must be checked before it
enters a bibliography** (H-5). Same-flavour MLIP-vs-DFT ceiling on rutile IrO₂(110) is 0.2 eV
(single-point) to 0.3 eV (after MLIP relaxation), 3–10× the 0.03–0.08 V candidate separations
(Jana et al. 2026, Research Square 10.21203/rs.3.rs-9284189/v1 — **preprint, under review, and one
critic could not open it: treat as unverified**). Universal MLIPs systematically soften surfaces and
other high-energy states (Deng et al., *npj Comput. Mater.* **11**, 9, 2025; arXiv:2405.07105), with a
one-point *fine-tune* — not a linear correction — as the remedy.

**(7) prereg-sensitivity-compsci.** The field's reproducibility standard is bulk-EOS-only: Δ ≈ 1 meV/atom
across 15 codes and 71 elemental crystals (Lejaeghere et al., *Science* **351**, aad3000, 2016), extended
to 960 EOS including oxides but still no surfaces (Bosoni et al., *Nat. Rev. Phys.* **6**, 45-58, 2024).
**No Δ-gauge-style verification lineage exists for surface adsorption energies or η** — which is the
wedge this campaign occupies, and the reason the internal-reproducibility framing is the right one.
Convergence-failure selection is standard practice, not a local artefact: OC20 terminated relaxations
still running after ~5,000 core-hours and excluded them from the dataset, and treats a single-point
check failing within 60 electronic steps as "incorrect" (Chanussot et al., *ACS Catalysis* **11**,
6059-6072, 2021). **No pre-registered DFT or computational-catalysis study was found** in three
targeted searches; the nearest precedents are organiser-blinded challenges (CCDC CSP blind tests;
SAMPL).

**(8) uq-descriptors.** Ensemble errors are correlated across catalysts, so relative rates carry
considerably smaller uncertainty than absolute ones (Medford et al., *Science* **345**, 197-200, 2014).
BEEF error estimates referenced to a metal surface are ~0.1 eV vs 0.3–0.4 eV against gas-phase
references (Deshpande, Kitchin & Viswanathan, *ACS Catal.* **6**, 5251-5259, 2016). "Prediction
efficiency" and expected activity are the defined instruments for "can this method tell these
candidates apart" (Krishnamurthy, Sumaria & Viswanathan, *J. Phys. Chem. Lett.* **9**, 588-595, 2018).
Confidence in the **classification** problem (which mechanism/step) is much better than in the
**prediction** problem (the activity value) (Sumaria, Krishnamurthy & Viswanathan, *ACS Catal.* **8**,
9034-9042, 2018) — which is exactly the A7.2-versus-A7.3 asymmetry this campaign measured. The BEEF
peroxide-bond systematic is 0.19 ± 0.02 eV, falling to 0.04–0.06 eV after one per-member O–O
correction (Christensen et al., *J. Phys. Chem. C* **120**, 24910, 2016).

**(9) electrochemical-realism.** Constant-potential corrections to the PCET ladder on rutile IrO₂(110)
are small (0.01–0.05 V on coverage crossovers, Lee, Kang, Lee & Soon, *Adv. Sci.* 2026, e14939), and
the O–O-forming step is where the 0.5 e⁻ transfer actually sits (Ping, Nielsen & Goddard, *JACS*
**139**, 149-155, 2017) — three independent lines say **grand-canonical DFT is not the missing physics**,
supporting the existing kill. On RuO₂(110) at 1.5 V_RHE the cus species is **–OO stabilised by an
H-bond from a neighbouring –OH**, and cus-*OOH is unstable (Rao et al., *Energy Environ. Sci.* **10**,
2626-2637, 2017) — the physical basis for H-10. AEM-only is defensible for pristine rutile IrO₂
(3.5 ± 0.7 % lattice-O exchange in the top 0.5 nm, Schweinar, Gault, Mouton & Kasian, *J. Phys. Chem.
Lett.* **11**, 5008, 2020) but not for doped/3d candidates. RuO₂(110)/(100) OER is pH-independent on
the RHE scale (Stoerzinger et al., *Chem* **2**, 668-675, 2017) — but polycrystalline ingots are outside
that guarantee.

**(10) sts-judging-computational.** See H-5 for the four verbatim rules **[SYNTH-OPENED]**. Additionally
(carried): STS publishes **no rubric** ("Regeneron STS does not share rubrics"); the only published
Society for Science rubric is ISEF's Grand Award, which scores "reproducibility of results" inside
Execution (20 pts) and "understanding interpretation and limitations of results and conclusions" in
the interview (25 pts) — **that is an ISEF instrument and this is an STS entry; do not present it as
the STS criterion.** The 2027 application carries Q13 "What didn't you do?" (150 w) and Q14
"limitations", defined as methodological/resource constraints — the natural homes for an unclosed
hole. Q15 accepts a preprint (arXiv/ChemRxiv) or a manuscript under review.

### 4.2 Refuted, corrected, or unverified — do not cite as support

| # | The claim as it circulated | Status and correction |
|---|---|---|
| R-1 | RuO₂ is an itinerant antiferromagnet (Berlijn 2017) — **asserted as fact in this repo** | **REFUTED by 2024 μSR ×2** (Hiraishi; Keßler), which bound the ordered moment 67–439× below Berlijn's 0.05 μ_B and re-identify the neutron peak as multiple scattering. Scope: **bulk**. Surface moments on (110) slabs are *not* excluded (Torun 2013), so the correction must not over-claim. See H-1. |
| R-2 | "`omat` … does not share [the MP U] convention" (docs/43:363) | **REFUTED by the repo's own docs/40 §1.4 three days before deposit**, and by OMat24's methods ("following Materials Project defaults") and Warford 2026 **[SYNTH-OPENED]**. See H-2. |
| R-3 | QE exposes only two occupation-side controls, and no held-occupation constraint exists | **CORRECTED:** pw.x exposes **three** — `Hubbard_occ`, `starting_ns_eigenvalue`, and `mixing_fixed_ns` (PW/src/electrons.f90 resets ns for `iter <= mixing_fixed_ns`). `starting_ns_eigenvalue` + `mixing_fixed_ns` reproduces the Allen–Watson set-hold-release pattern, restricted to eigenvalues and to SCF iterations. The repo's docs/43 A7.6 #2 correction is right that `starting_ns_eigenvalue` alone is an initial guess, **wrong to imply no hold exists**. `mixing_fixed_ns` appears nowhere in the repo. |
| R-4 | Bulk RuO₂ hosts multiple altermagnetic phases *coexisting* in Hubbard space | **CORRECTED:** Hou et al., arXiv:2604.14764 report three *successive* phases across adjacent U windows (NM < 0.9; AM1 ≈ 0.1 μ_B from 0.95; AM2 > 0.7 μ_B above 1.05 eV), separated by phase boundaries — not coexisting at a single U. |
| R-5 | 99Ru Mössbauer + phonons show the **XC functional**, not U, fixes RuO₂'s lattice dynamics | **OVERSTATED.** Yumnam et al., *Cell Rep. Phys. Sci.* **6**, 102852 (2025) bound a static moment at ≤0.03(1) μ_B, but on the IXS dispersion **both** SCAN(NM) *and* PBE+U=2 (AFM) agree well; the authors write "It remains unclear why non-magnetic SCAN appears superior" and call the U = 0 failure "probably a coincidence". They do **not** conclude functional-not-U, and with no NM U = 2 arm they cannot. |
| R-6 | Xu 2015: "a linear-response U always makes adsorption more endothermic and does not break scaling" | **SCOPED WRONG.** True for late 4d/5d rutiles. On **CrO₂ and MnO₂** `*OOH` desorbs above U ≈ 4 eV, breaking OH/OOH scaling *below* their own linear-response U (7.15 and 6.63 eV), and on TiO₂ `*OOH` becomes *more* exothermic with U — TiO₂, MnO₂ and CrO₂ were excluded from Xu's volcano. This is directly relevant to spike S-4's Fe/Mn interior rows. |
| R-7 | DFT+U+V is "essential for redox thermodynamics in TM oxides" | **SCOPED WRONG.** Timrov et al., *PRX Energy* **1**, 033003 (2022) establish this for **olivine phosphates**, not oxides; the closest oxide result (Ricca 2020) is defect, not redox, thermodynamics. |
| R-8 | Sumaria 2018 shows classification-beats-prediction **for OER** | **WRONG REACTION.** That paper is **chlorine** evolution on rutile(110); OER is not studied in it. The OER extension must cite Krishnamurthy et al., JPCL 2018 instead — which the repo already holds. |
| R-9 | Rutile(110) slab properties oscillate odd–even with trilayer count, so the repo's 3→5 test is blind | **PARTLY TRUE, SOURCE MIS-ATTRIBUTED.** The oscillation is established on **TiO₂**(110) (Bredow 2004; Kowalski 2009; Zhuang 2022) and is largely removed by fixing the bottom two trilayers — which is *this campaign's own construction rule*. Kowalski, Meyer & Marx, PRB **79**, 115410 (2009) is titled on oxygen depletion/hydroxylation/water adsorption, not thickness convergence; the "oscillation suppressed by fixing two trilayers" parenthetical is unsupported in what was opened. |
| R-10 | Hegde 2023 traces database magnetisation disagreement to "magnetic-configuration sampling" | **MIS-QUOTED.** The abstract attributes the larger discrepancies to "pseudopotentials, the DFT+U formalism, and elemental reference states". The 10–15 % magnetisation-disagreement and 0.105 eV/atom median figures are correct; the attribution is not. |
| R-11 | Liang 2022 "swings η by 0.4–0.5 V" (the repo's docs/28 paraphrase) | **WRONG.** 0.41–0.49 V is the **AFM η**, not the swing. The AFM-vs-NM effect is ~0.2 V (0.17–0.24 V) on mixed O/OH terminations, ~0 on the fully O-covered surface. **Fix the docs/28 paraphrase before it is quoted in the report.** |
| R-12 | Warford 2026 = *Mach. Learn.: Sci. Technol.* **7**, 035033, DOI 10.1088/2632-2153/ae6be5 | **UNCONFIRMED.** arXiv:2601.21056 **[SYNTH-OPENED]** lists no journal reference. Cite the arXiv record, or verify the journal version before it enters the bibliography (H-5). |
| R-13 | Smolyanyuk's onset values U_eff = 1.06 / 1.23 eV | **UNVERIFIED HERE.** Not in the abstract **[SYNTH-OPENED]**; body-text values carried from the dimension agent. Use the abstract sentence for load-bearing statements, or open the PDF before registering anything against those numbers. |
| R-14 | Jana et al. 2026 (the 0.2/0.3 eV IrO₂ MLIP ceiling) | **UNVERIFIED.** Research Square preprint, under review; one critic's attempt to open it returned HTTP 403. Do not quote the numbers as read. |
| R-15 | "Specification curve analysis is the established method to report across defensible specifications, with joint inference" | **METHOD REAL, APPLICATION INVALID HERE.** Simonsohn, Simmons & Nelson, *Nat. Hum. Behav.* **4**, 1208-1214 (2020) require first "identifying the set of theoretically justified, statistically valid and non-redundant specifications". This repo has **4** admissible cells for the A7.3 count (as-built/equalised × denominator 6/5), all reading 3 — a four-point flat line, and docs/43:2106-2111 rule (v) already states that invariance in words. |
| R-16 | ISEF's "reproducibility of results" is the criterion this entry is judged on | **WRONG COMPETITION.** That is the ISEF Grand Award rubric. STS publishes no rubric; "reproducibility" does not appear on its judging page. |

---

## 5. Ideas

### 5.1 The table

Scores are the **critic-adjusted** values (rigor / novelty / STS, each out of 5), not the proposer's.
Cost is SU plus entrant-hours. "Dep." lists what must happen first. **I-19 is
synthesizer-originated and has NOT been through a critic** — the only entry in this table that has
not; weigh it accordingly.

| ID | Idea | Lens | Cost | R | N | S | Pre-registration line (abbreviated) | Dep. | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **I-19** | **Locate the A7.2 pls crossings** — test the interpolated U\* (§3 H-3) with ~24 interior SCFs + a Ti control | *synth* | **150–600 SU**, 8–14 h | **4** | 2 | **4** | Interior rungs are added to *locate* crossings already bracketed and to test a stated interpolation; a Ti arm at equal density is run where no flip is bracketed; any newly found flip updates the count in either direction | dated line | **SPIKE S-4** |
| I-8 | Magnitude-ladder figure: every knob in η-equivalent units vs the 0.03–0.08 V band | sts-narrative | 0 SU, 12–20 h | 2 | 2 | **4** | Bars are drawn only from a frozen (value, unit, η-conversion, status, docs/45 row) tuple; TRANSFERRED and NOT MEASURED are never summed with MEASURED | H-4 | **SPIKE S-2** |
| I-2 | Hidden-knob error budget → Monte-Carlo Δ95, P(η_i<η_j), prediction efficiency | statistics-uq | 0 SU, 10–16 h | 3 | 2 | **4** | Distribution families fixed before sampling; Δ95 is never applied to, or quoted beside, any registered threshold or verdict | H-4 | **SPIKE S-2 (reduced)** |
| I-9b | RuO₂ correction of record (the non-compute half of the onset-U idea) | devils-advocate | 0 SU, 2–3 h | 3 | 2 | 3 | Dated correction; docs/45 §A row; scoped to **bulk** | — | **SPIKE S-1** |
| I-7 | Conformer-resolved endpoint re-read: score `*OO–H` at U = 0 and U = 9 | electrochem | 2–10 SU, 3–5 h | 3 | 2 | 3 | Second, **non-replacing** `*OOH` member; c_M reported as a bracket; never enters the A7.3 score | H-10 | **fold into S-1/S-4** |
| I-12 | Pseudopotential/basis knob arm on the Ru anchor | devils-advocate | 30–60 SU, 4–6 h | 3 | 2 | 2 | PP arm only, as an anchor-pair comparability control, not a new ledger class | — | **reduce to a sentence (S-1)** |
| I-1 / I-10 | Fixed-spin-moment E(M) scan on Ru U = 9 (`tot_magnetization`) — *the same idea from two lenses* | dft-numerics / devils | 900–3,800 SU, 10–16 h | 3 | 3 | 2 | Diagnostic only; FSM rows never enter the A7.3 pool; must disclose it was chosen after the ladder's outcome | new dated line lifting A10 ban | **NOT NOW** (§6) |
| I-3 | Held-out DFT point on Fe25Co25Ni25Cr25 site tail | mlip-heldout | 1,750–15,000 SU, 3 wk | 3 | 3 | 3 | Prediction deposited before decks; UNSCORED if any state fails A8.4; no outcome re-ranks the melt list | A12 + Zenodo | **NOT NOW** |
| I-11 | Order-statistic null + winner's-curse column on the melt list | mlip-heldout | 0 SU, 3–4 h | 3 | 2 | 2 | Descriptive re-analysis, **no HELD/FAIL verdict**; the site metal of the winning site is printed | S8 go/no-go | **do iff S8 = go** |
| I-4 | Density-chained U-continuation (both directions) on Ru spin rows | dft-numerics | 600–7,700 SU, 8–12 h | 3 | 3 | 2 | Chain rows are a knob measurement (U-path dependence), never census cells | new dated line | **NOT NOW** |
| I-5 | Designed replicate-variance floor + `--bind-to` arm | dft-numerics | 150–500 SU, 6–10 h | 3 | 2 | 3 | Per-class floors; **no rerun replaces a banked energy** | — | **0-SU version only** |
| I-6 | Liechtenstein U+J re-score of the Mn AFM quartet | dft-numerics | 200–1,100 SU, 8–12 h | 2 | 4 | 2 | Non-gating, firewalled from A7.2/A7.3; J fixed **before** the build | A12 + deposit | **NOT NOW** |
| I-13 | Registered-Report outcome table (verbatim registration, band, flip distance) | statistics-uq | 0 SU, 6–8 h | 2 | 1 | 3 | Columns fixed; no row omitted because its band is NOT MET | H-4 | **merge into S-2** |
| I-15 | Pre-registered attack ledger + simulated judge panel | sts-narrative | 0 SU, 8–12 h | 2 | 1 | 3 | Pointer-only cells (docs/ line + status token), no prose | — | **ledger yes, panel no** |
| I-16 | Exact operating characteristics of the count thresholds | statistics-uq | 0 SU, 3–4 h | 2 | 1 | 2 | Descriptive of the **rules**, not of the metals; cannot move a verdict | — | **merge into S-2** |
| I-17 | Finite-sample conformal band on the screener (n = 7) | mlip-heldout | 0 SU, 2–3 h | 2 | 1 | 2 | Band **reported**, never used as a resolution rule | S8 go/no-go | **do iff S8 = go** |
| I-14 | Buy-and-measure commercial RuO₂/IrO₂ powders on the Purdue bench | sts-narrative | 0 SU + consumables, 3–5 bench days | 1 | 2 | 3 | Observable is sign(η_IrO₂ − η_RuO₂); scoring is the U-window on the banked ladder | sponsor, risk assessment | **entrant decision (§7 Q-6)** |
| I-18 | Hubbard-occupation branch census (label basins by ns eigenvalues) | dft-numerics | 0 SU, 6–10 h | 2 | 1 | 1 | Labels fixed before the table exists; cannot move a banked number | — | **one finding only** |

**Deduplication note.** I-1 and I-10 are the same technique (`tot_magnetization` E(M) scan on Ru
U = 9) proposed independently by the dft-numerics and devil's-advocate lenses. Counting them as two
ideas overstates the convergence of the round; they are one.

**Of I-18, one sub-finding is worth keeping even though the census is not:** all three A11 Ru seeds
started from the **identical Hund's-rule Hubbard occupation** (Tr[ns] = 5.00000 / 1.00000 / 6.00000 on
all 6 Ru, 24 μ_B/cell), because `init_ns.f90` takes only the *sign* of `starting_magnetization`. The
seed grid therefore varied the charge-density spin start while holding Meredig's factor (ii) fixed.
That is a one-sentence caveat the docs/68 §11 methods sentence should carry, at zero cost. *(Carried
from the critic; the `.out` blocks were not re-read by the synthesizer.)*

### 5.2 The top eight

**1. I-19 — Locate the A7.2 crossings (the only compute I recommend).** The one prediction that
CONFIRMED under-delivers its own registered first-class deliverable: no pls crossing is located, and
the brackets are 1.5 eV wide on 5 of 6 flipping metals. The interpolation in §3 H-3 costs nothing and
already yields a reportable result (Mn's second crossing is 9.5 meV from a grid row, i.e. inside every
measured error class). Testing it costs ~24 fixed-geometry SCFs at measured rates. It adds no
threshold, cannot rescue anything, and — with the Ti control — is symmetric. **Risks, stated:**
interior points can only *add* flips, never remove them, so the Ti arm at equal density is what makes
it honest; and R-6 (Xu 2015) predicts `*OOH` trouble on the **Mn and Fe** interior rows specifically,
where 3d `*OOH` desorbs above U ≈ 4 — those two brackets carry a real UNSCORED tail while the Ru/Ir
ones are cheap and safe.

**2. I-8 — The magnitude ladder.** The thesis sentence ("millimetres with a ruler that wobbles
centimetres") exists only as prose and a 4-row table; `docs/figs/` has no cross-knob figure. This is
the single picture a non-specialist judge and a PhD reviewer both need in the first minute. It is only
worth doing if the two traps in H-7 are handled: the η-conversion must be per-bar and correct (not
"energy/2"), and bars must be ranges over the roster with n and the carrier metal on the face, because
every ledger magnitude is a per-class maximum on one metal while the comparison band is a typical
separation. Add the "joint effect unmeasured" limitation explicitly — the crossed sets are Cr-only,
one-point, and endpoint-only.

**3. I-2 — The hidden-knob error budget, reduced.** The formal statement of the thesis: propagate the
*measured* magnitudes through η and report a resolution number. Critic-adjusted to rigor 3 for four
reasons that must be answered in the text: the number is **prior-dominated** (a uniform U over [0,9]
manufactures σ ≈ 0.3–0.6 V on Cr/Fe/Mn by construction, so it must be reported at the registered
bracket {0, MP U, hp.x/Xu} as well as the full grid); the numerics class is **bimodal, not Gaussian**
(29 GATE-1 pairs ≤ 0.044 meV vs 6 pairs 7.4–747 meV, zero overlap, factor 168 — a two-point mixture is
the right family); the closed form **breaks at pls ∈ {1,4}**, which Fe and Mn endpoints occupy, so use
η = max(ΔG_i) − 1.23 and say it is not the A7.2 closed form; and a P(η_i < η_j) heatmap is a second,
unregistered pairwise instrument that must be subordinated to A5.1(b) or the report contradicts
itself. **The hard rule:** Δ95 will almost certainly exceed A7.3's 0.10 V floor, and any sentence of
the form "the threshold was inside our resolution, so NOT MET is uninformative" is precisely the
post-hoc move A11.5 and docs/43:1960 forbid.

**4. I-9b — The RuO₂ correction of record.** The compute half (a bulk onset-U locator, ~36 SCFs,
50–500 SU) is cheap and defensible as a measurement, but the interpretive payload it was proposed to
buy — annotating Ru rows OUTSIDE-BULK-PHYSICAL-U — is the worst thing in the idea and should be
dropped: it retroactively qualifies the registered endpoint of a *failed* prediction on the one metal
4.3 meV from flipping it, and it is **asymmetric**, because Ru's A7.2 flip also rests on that same
U = 9 row (kill the row and CONFIRMED 5/6 → 4/6, robust members 3 → 2, below the registered ≥3). Keep
the correction, drop the annotation. Scope it to **bulk** (Torun 2013 says the (110) surface is
magnetic at plain PBE), and note it bears on whether the deferred SECOND_SEED_CROSSED branch
(16,000–30,000 SU) should ever be bought.

**5. I-7 — The conformer member.** Rao 2017 and Di Liberto 2023 both say the species on RuO₂(110) is
not cus-`*OOH` — the proton sits on a neighbouring O. The repo computed that conformer at production U
only and never let it enter an η(U) row. The cheap, honest version is: correct docs/54 item 10 (the Cr
"oosh" is a desorbed O₂ + H_br state, not a conformer), and compute the Ru U = 9 endpoint (~2–5 SU;
U = 0 already exists because Ru production carries no HUBBARD card). Report c_M as a bracket. **Do not**
build the Mn/Fe/Ti arm: those need a relax licence and sit in the `*OOH` desorption regime. And be
honest that this is now a *third* arm touching the Ru cell, so it must be firewalled exactly as
docs/61 item 10 was.

**6. I-1/I-10 — The fixed-spin-moment scan.** Genuinely untried (`tot_magnetization` is on the
FORBIDDEN list of all three builders and appears in zero decks), and it targets the one hole docs/68
§11 explicitly leaves open: "*that a different mixer, occupation-matrix control, or a smaller U would
not converge it — none of those was run*". Pinning M deletes the soft spin mode that has no
preconditioner in pw.x. **But** its sequencing pitch is dead (the ladder ran), the M-range as drafted
(0–12 μ_B) never reaches the 18–24 μ_B attractor the failures actually sit in, the seed formula is
wrong (`starting_magnetization` is a fraction of Z_val = 16, so M\*/96, not M\*/6), and it would be the
**fourth** arm on the cell 4.3 meV from flipping a failed prediction, requiring a "chosen after seeing
the outcome" disclosure. Its honest deliverable is a *bound* on how far below the nspin = 1 floor the
U = 9 ground state lies. **Only worth buying if the entrant wants that hole closed for its own sake**,
and then only with a symmetric Ir control arm (Ir is also EQUALISED-BY-SELECTION, at 0.0591 V, where
no result could help).

**7. I-3 — The held-out HEA point.** Highest ceiling of any idea here: it would convert "held-out
points: zero" into one, on the screen's *actual* ranked statistic. It is also the most expensive
(1,750–6,600 SU bare, 4,000–15,000 with the basin replication the project's own rules require), the
most likely to end UNSCORED, and it validates a proxy built on invented lattice constants for phases
that do not exist. Nine weeks from the deadline, with the report unwritten, it is the wrong bet.

**8. I-15 — The attack ledger (ledger only, not the panel).** A two-column (attack → evidence pointer
+ status token) table, closed on a date. Its "why new" claim is false — docs/43 A5.6 is already a
binding eight-item wording/attribution obligation list, and the lens digest is already an
attack-to-defence map — so it is a consolidation, not an instrument. The simulated three-judge panel
should be dropped: docs/66 already ran 13 adversarial agents plus a 4-auditor pass, and a panel
scoring against a rubric that does not exist is unfalsifiable output. Two of its seed rows (R-1, R-2)
are worth more than the container and are S-1.

---

## 6. Where to spike: 2026-09-02 → REPORT LOCK

### The framing fact

**Compute is not the constraint, and has not been for some time.** The balance is 59,761.1 SU with an
empty queue and AMENDMENT 11 fully run. The plan below spends **150–600 SU — 0.25 % to 1.0 % of the
balance** — and that is the correct amount. What is scarce is entrant-hours against a hard external
deadline and a 20-page limit that counts appendices. Every remaining hole that matters is closed by
*deciding* or *writing*, not by computing. The one exception is S-4, and it is small.

Hour figures below are **task sizes, not a schedule claim** about availability.

### S-1 — Corrections of record and the compliance gate (Sep 2 – Sep 8)

**Closes:** H-1, H-2, H-12, H-5, plus the sentence versions of H-9 and H-10.
**Cost:** 0 SU, 10–16 h.
**Contents:** (a) the RuO₂ bulk-magnetism correction of record, as a **dated addendum** — docs/41 is a
pre-registration and the round-2 synthesis is deposit-adjacent, so neither may be edited — with a new
docs/45 §A row and the three repo sentences re-anchored on Hiraishi 2024 / Keßler 2024 / Smolyanyuk
2024, scoped to bulk. (b) The §7 prediction-3 disclosure. (c) The `upscale` declaration and the
methods `conv_thr` sentence (entrant re-authors). (d) The PP-family confound as a TRANSFERRED / NOT
MEASURED sentence on A6.3. (e) The docs/54 item 10 correction (Cr "oosh" is a desorbed state) and the
docs/28 Liang paraphrase fix (R-11). (f) The compliance gate: every bibliography entry resolves at
`api.crossref.org/works/{doi}` with a title match — R-12 and R-14 are already known failures — and a
figure-by-figure citation checklist, since an uncited student-made figure is disqualifying.
**Why first:** two of these are defects a competent reader finds in one pass, and (f) is a
disqualification surface at near-zero cost. Against the STS criteria this is Q14/limitations material
and, more importantly, insurance.

### S-2 — The magnitude ladder and the resolution statement (Sep 8 – Sep 17)

**Closes:** H-7, H-8.
**Cost:** 0 SU, 16–24 h.
**Contents:** the η-equivalent bar figure with per-bar conversion, ranges with n and carrier metal on
the face, MEASURED / BOUNDED / TRANSFERRED / NOT MEASURED tokens, the 0.03–0.08 V band and the 0.10 V
threshold shaded, and an explicit "joint effect unmeasured — these are one-factor-at-a-time magnitudes
off one baseline" limitation. Beside it: the Monte-Carlo resolution number reported at **both** the
full grid and the registered U bracket, and the two exact-binomial band-mass footnotes with the
correlation caveat stated in the same paragraph. Merge I-13's outcome-table columns (registration
paraphrase + date, threshold, observed/denominator, band, distance-to-band-edge **labelled
"not an uncertainty"**, measured error class, all applied uniformly to every registered prediction —
including A7.2's zero-margin CONFIRMED, or it reads as scaffolding around A7.3).
**Why:** the report's central claim is currently a sentence and a 4-row table. This is the artefact
that makes it checkable, and it is what the Sep 20 displacement decision needs in front of it.

### S-3 — Execute the September decisions (Sep 15 – Sep 20)

**Closes:** H-4, H-6 (the decision), and the D2/D3/D4 backlog.
**Cost:** 0 SU, 6–10 h.
**Contents:** by **Sep 18** — A10/P-BEEF drafted or explicitly withdrawn (it is NOT DRAFTED, gated on
S0(a), and it currently occupies a body-ledger row it may not use). By **Sep 20** — the six-row
displacement and the claim sentence, in writing. Also: D2 guard-3 adjudication (now unblocked and with
a suggested line already in docs/68 §11: Ru and Ir BRANCH-CONDITIONAL, Cr and Ti SAME-BRANCH), D4
(send or skip the RCAC ticket), and the **S8 go/no-go**.
**Why:** these are dated obligations the project set itself, and everything in S-5 is shaped by them.

### S-4 — Locate the A7.2 crossings (Sep 20 – Oct 6)

**Closes:** H-3.
**Cost:** **150–600 SU**, 8–14 h.
**Design:** one dated line first. Then, for each bracketed flip, four fixed-geometry SCFs (slab, `*O`,
`*OH`, `*OOH`) at the interpolated U\* of §3 H-3, plus a **Ti arm at equal density** (3 interior U)
where no flip is bracketed. Registered prediction, both outcomes named: the measured crossing lies
within ±0.2 eV of the interpolated U\* on ≥4 of the 5 locatable crossings; a miss on ≥2 refutes the
linear-interpolation estimate and the brackets are reported as brackets.
**Pricing, from wall times read off banked `.out` files this session at 128 ranks:** Ru 1m03.75s
(≈2.3 SU/SCF), Ir 1m27.20s (≈3.1), Fe 3m44.84s (≈8.0), Mn 3m44.21s (≈8.0), Ti 3m19.53s (≈7.1); Cr not
re-measured (≈5–7). One test point per crossing = 24 SCFs ≈ **141 SU**; one bisection round on any
miss ≈ +141 SU; the Ti control ≈ **85 SU**. Nominal ≈ 370 SU; with A6.5 escalation on the Fe/Mn `*OOH`
rows, **150–600 SU**.
**Why this and not the alternatives:** it delivers a *registered deliverable* rather than adding an
arm; it is the only compute that touches the prediction that CONFIRMED; it is convergent (nspin = 1,
fixed geometry, ~1–4 min per SCF); it cannot rescue a failed prediction; and docs/66 §6 item 1 already
identifies it as the highest-value phase-2 item — this version is a tenth the price of the
spin-equalised form it prices there.
**Known risk:** R-6 — Xu 2015 found 3d `*OOH` desorbing above U ≈ 4 eV, and the Fe [7.5, 9.0] and
Mn [6.0, 7.5] interior points sit squarely there; Fe `*OOH` also carries a measured +276.60 meV
cold-start trap. Expect the Ru/Ir/Cr legs to land and budget for one or both 3d legs to return
UNSCORED. That outcome is itself reportable.

### S-5 — Write, self-audit, lock (Oct 6 → REPORT LOCK, backstop Nov 5 8:00 pm ET)

**Cost:** 0 SU.
**Contents:** the report, written by the entrant without generative AI; a self-audit against the five
verbatim STS rules in H-5 (20 pages including appendices; every figure cited; every reference
resolving; no links in the body); and the dated REPORT LOCK line, which under docs/43:2249-2265 is
what converts anything unscored to WITHDRAWN-UNSCORED. Optional and cheap: a preprint before the
deadline, which Q15 accepts.
**Hard boundary:** nothing may be added to the investigation after the application deadline, and an
incomplete investigation is not eligible. Anything not closed by REPORT LOCK belongs in Q13/Q14 or the
limitations section, never in Results as "pending".

### What is NOT worth doing

1. **A fourth arm on the Ru U = 9 cell** — FSM, U-ramping, occupation-matrix control, `mixing_fixed_ns`,
   a different mixer. The ladder is exhausted, docs/68 §11 says a further rung needs a new dated line
   that discloses it was chosen after the outcome, and **A11.5 means no outcome can promote A7.3**. The
   equalised gap is 4.3 meV. Three arms have already been spent there. *(If the entrant wants the
   "different mixer was never run" hole closed for its own sake, the FSM arm is the right instrument
   — with the M-range extended to 24 μ_B, the seed formula corrected to M\*/96, and a symmetric Ir
   control. That is a preference, not a rigor gain.)*
2. **An S8 ingot that cannot complete.** Under the eligibility rule a partial chain is worse than none.
   Melt only if re-rank → freeze deposit → melt → OER measurement → writeup all fit before REPORT LOCK.
3. **Any new error class.** The single-water arm (D7), the bridging-O vacancy LOM flag, a fifth `*OO`
   state, grand-canonical/work-function arms, a second-code cross-check, the Co ladder revival, the Cu
   held-out point. docs/44:78-80 is explicit that re-adding these "risks turning a tight, defensible
   5–6-class taxonomy into an unfinished 10-class survey", and three independent citations now say
   grand-canonical DFT is not the missing physics.
4. **New MLIP work.** The `omat` re-screen (`tasks/todo.md:335` — "Do NOT re-screen on `omat`"), the
   cross-model disagreement map, the binding-curve arm, and any conformal band used as a *gate*. The
   MLIP chapter is closed as a reproducibility check within one level of theory.
5. **The specification-curve / multiverse framing.** Four admissible cells, all reading 3, is not a
   curve, and docs/43:2106-2111 rule (v) already states the invariance in words. Adding axes to
   manufacture a distribution is the forking-paths garden dressed as its remedy.
6. **Re-measuring the replicate floor.** It already exists at n = 29 (≤0.044 meV matched-branch) and
   n = 8 across a 32× decomposition change (≤0.0437 meV, derived Δc_M floor 0.052 meV). Every margin in
   play is ≥10× above it. Print the existing numbers; do not spend 24 SCFs re-deriving them. *(The one
   live piece is the `--bind-to` question, and its honest experiment is ~6 SCFs on the single deck
   known to flip, not a 72-SCF census.)*

---

## 7. Open questions for the entrant — each is a dated-line decision

**Q-1 (Sep 20, already owed).** Which registered prediction is displaced from the six-row body ledger,
and what is the claim sentence? docs/43:1930 lists six claimants before A9 adds anything, and A11 adds
two more. *Consequence:* everything in S-2 and S-5 is shaped by this.

**Q-2 (Sep 18, already owed).** A10 / P-BEEF: drafted, or withdrawn? It is NOT DRAFTED and gated on
S0(a), and it currently holds a body-ledger row. *Consequence:* if withdrawn, a row frees and Q-1
becomes easier; if drafted, it is the schedule's only remaining large-compute item, and libxc is not
linked so the meta-GGA variants are unreachable in this build.

**Q-3 (now).** D2 guard-3 adjudication — one dated line each for Ru, Ir, Cr, Ti. docs/68 §11 supplies
the wording. *Consequence:* until written, none of the four equalised spans is scoreable.

**Q-4 (S-1).** Does the RuO₂ correction of record go in as a dated addendum with a docs/45 row, and is
the deferred SECOND_SEED_CROSSED branch (16,000–30,000 SU) formally closed on the strength of it?
*Consequence:* leaving Berlijn-2017-as-fact in the record is the highest-probability reviewer hit in
this file.

**Q-5 (S-3).** **S8 go/no-go.** If go: the re-rank gate has no code and must be written, the freeze
deposit precedes the first ingot, and the whole chain must complete before REPORT LOCK. If no-go: say
so in a dated line, and the honest framing is that the entry is a computational methods result — which
docs/18's Scholar cap over-states, given three compute-only DFT Finalists and four consecutive
computational first places (H-6). *Consequence:* this is the largest single fork remaining.

**Q-6 (S-3, only if Q-5 is no-go).** Do the two commercial-powder anchor measurements happen? *For:* it
is the only route to a self-collected datum and moves Rules-Wizard Part I E off "no self-collected
data". *Against:* the RuO₂ > IrO₂ alkaline ordering is textbook, so the sign is a demonstration not a
test; the U-window it would select ([4.5, 7.5] by bracket) is computable today at zero cost and every
point in it sits inside the campaign's own 1×1 cell class; and it re-opens a hazardous-materials /
sponsor-of-record branch (`tasks/todo.md:492`, still open) three weeks from the writing window.
*Recommendation:* compute the window now for free; treat the powders as an optional provenance upgrade
that is never the registered object.

**Q-7 (S-4).** Is the crossing-location arm licensed, and does the Ti control arm run at equal density?
*Consequence:* without the Ti arm the design is asymmetric — interior points can only add flips — and a
reviewer will say so.

**Q-8 (S-1).** `upscale` declaration for future relax decks, and the corrected methods `conv_thr`
sentence. *Consequence:* the deposited protocol currently says 1e-6 while 39 banked rows met 1e-8.

**Q-9 (now).** The three S3 tail rows: record NOT_CONVERGED / MULTISTABLE at 0 SU, or license the
parent-moment warm start (~40 SU, a registered-input change)? *Consequence:* leaving them owed at
REPORT LOCK means they are WITHDRAWN-UNSCORED anyway.

**Q-10 (now).** The S1 silentgate core is entrant-written and unstarted, and it blocks the S2 census.
Will it be written, or is S2 withdrawn? *Consequence:* an owed-but-unwritten gate at lock is the worst
of the three outcomes.

**Q-11 (S-1).** The Xu-repair disposition, (a) cut on evidence or (b) minimum-viable re-run
(docs/43:1938) — the last genuinely open item from the external note.

---

### Uncertainty, stated plainly

The three things in this file most likely to be wrong: (i) the H-10 Cr-conformer geometry claim, which
is carried and not re-measured; (ii) the S-4 cost band, whose Fe/Mn legs sit in a regime where this
campaign's `*OOH` rows have historically failed, so 600 SU is a soft ceiling rather than a hard one;
and (iii) the docs/18 placement correction, which rests on a carried survey of STS finalist pages
rather than on any published rubric — STS publishes none, so *every* placement claim in this project,
including docs/18's original one, is inference from precedent.

## 8. Completeness critique, and the corrections it forces (2026-09-02, appended after §1–§7 were written)

§1's rule was that every claim in this file is re-checkable. A completeness critic was run over the
finished file and the project brief; **I then re-verified its load-bearing findings against the tree
myself before recording any of them here** (the campaign's own rule for AI-produced claims: an
AI summary of your own repo is a claim like any other). What follows is what survived that
re-verification. Nothing above this section has been silently edited; read §§2–7 through this one.

### 8.1 Errors in this file — do not carry these forward

| # | Where | Error | Status |
|---|---|---|---|
| C-1 | `:481-483` | **Lee, Kang, Lee & Soon, *Adv. Sci.* e14939 is mis-scoped and load-bearing.** Crossref 10.1002/advs.202514939 is *"Atomistic Insights into the Electrochemical Oxygen Evolution Activity of **Hollandite** IrO₂ Surfaces"* — hollandite (100)/(112), not rutile (110) — and it is *itself* a grand-canonical + implicit-solvation study reporting **lower overpotentials than rutile (110)**. It is cited here as one of three lines showing grand-canonical DFT is *not* the missing physics, i.e. cited backwards, in support of an existing KILL (`docs/44:78-80`). **WITHDRAWN as support.** The KILL may still be right; it now rests on two lines, not three. | confirmed present at `:482` |
| C-2 | `:229-231` | **Iyer 2021 is described as first-principles Cr/Mo-doped VOPO₄ catalysis; it is a Li-ion cathode paper** (10.1021/acs.jpcc.0c10156, *ε-Li_xVOPO₄* cathodes). Authors/volume/pages correct, subject wrong. Its STS-Finalist attribution is unverified, **as are Andreasen 2022, Moudgal 2023, Rajaram 2024, Paz 2025, Hill 2026 and the "2025 ninth place / 0.6 % accuracy gain" claim** — six un-opened sources, all of which carry Q-5, the file's largest fork. **Treat every STS-precedent attribution in §3 H-6 as unverified until opened.** | confirmed |
| C-3 | `:217` | "A grep for `rerank\|re-rank` across `src/` returns **no file**" is false as written — `src/README.md:58` matches. The true claim is that no *implementation* exists. In a file whose §1 promises re-checkability, a pointer that fails on re-check is the worst kind of error. | confirmed |
| C-4 | `:166-168` | The Mn "9.5 meV from a grid row" result is **already banked**, not produced this round: `docs/figs/a0main_readout.json` → `a7_2.census_robustness.Mn.smallest_pls_margin_eV = 0.009489` at `smallest_at_u = 6.0`. The interpolated U\* table itself reproduces the banked rows exactly (all six values independently checked). Also, "9.5 meV from the U = 6.0 grid row" reads as a distance in U; **the U-distance is 0.098 eV**. | confirmed |
| C-5 | `:159` | The pls interpolant assumes only two rungs contend at the endpoint. At Cr U = 4.0 the file's f = ΔG₂−ΔG₃ = 0.1844 eV, but the true max-minus-runner-up margin is 0.0760 eV — the runner-up is rung 1, not rung 3. It survives on Cr; the assumption is unstated and untested on the Mn/Fe legs where pls ∈ {1,4} contends. | confirmed |
| C-6 | `:227-234` | **H-6 rebuts a claim docs/18 does not make.** docs/18 §1 already tables **three** compute-only Finalists (Guan 2021 DFT catalysis, Kim 2023 ScGAN, D'Halleweyn 2024 ML+XANES) and states the criterion as **stage, not modality**: "even the pure-compute Finalists (Guan, D'Halleweyn) had a *finished* computational deliverable applied to real systems", verdict **"Ceiling: Finalist-credible — conditional on the wet-lab loop landing"**, with computational-work-alone as "your **Scholar floor with a Finalist upside**". H-6's "correction to docs/18" is withdrawn; docs/18's actual criterion has still **not** been tested against the present state (withdrawn headline + one failed registered prediction), and that test is what Q-5 needs. | confirmed by reading docs/18 §1, §4, §5 |
| C-7 | §6 S-4 | Four defects, any one of which blocks it as written: it **registers a ninth ledger claimant while H-4 says the ledger is over cap at eight**, and never says where the row goes; its registered prediction (crossing within ±0.2 eV of U\*) **is not evaluable by its own decks** — one quartet at U\* returns only the sign of f, i.e. a halved bracket, and the bisection that would detect a miss is priced as contingent *on detecting a miss*; its denominator disagrees with its deck count (**"≥4 of 5 crossings"** vs **24 SCFs = 6 crossings × 4 states**; the banked brackets hold six crossings across five metals, Mn having two); and **±0.2 eV is near-unfalsifiable on Cr**, whose bracket is 0.5 eV wide. It also drops the spin-equalisation docs/66 §6 item 1 requires, which matters because its Ru leg locates U\* ≈ 8.66 on a convention A11 has just recorded as EQUALISED-BY-SELECTION(nspin=1) for want of any converged spin-polarised Ru row at U = 9. **S-4 must be re-specified before it is proposed to the entrant.** | confirmed against `docs/43`, the banked brackets and docs/68 §11 |
| C-8 | §3 H-3 | "No pls crossing is located anywhere" overlooks the registration's own disclosure, `docs/43:1356`: "**DISCLOSED NON-BLIND:** Cr flips 3→2 between U = 1.85 and 3.70 (its production U landed 7 meV from the crossing)". Correct framing: *not located on the A0 grid for any blind metal.* | confirmed |
| C-9 | §3 H-1 | The "cheapest closure" is priced as prose edits, but two of the three sites — `src/dft/probe_decks.py:251-252` and `src/dft/qe_slab.py:49` — are **deck-generating code**. Correcting the prose while the generators still assert the refuted premise is half a correction; touching them is a code change inside the frozen build and needs its own line. | confirmed: `probe_decks.py:252` reads "established itinerant ANTIFERROMAGNETISM" |

### 8.2 Holes the file missed — one of them outranks most of §3

- **BASIN_DRIFT, and it is the largest un-actioned margin in the campaign.** `tasks/todo.md:683`:
  three banked parents sit in an **excited magnetic branch**, with the fixed-geometry GATE-1 child
  landing below its own parent, both sides converged, geometry byte-identical: **Fe `s0_OOH__1x1_off`
  −384.300 meV**, Co `s0_O__1x1_off` −77.009 meV, Mn `s0_OOH__2x1v_off` −20.616 meV — clearing the
  registered 5 meV trigger by 77×, 15× and 4×. The remedy is **deposited and not executed**
  (`docs/43:311-314`: re-relax from the child, loop until GATE-1 passes, publish the iteration
  count). "Every ΔG built on those three inherits the error", and **the Fe row is 0.384 eV — larger
  than every knob this study measures and ~45× the 8.5 meV that separates Ru from A7.3's floor.**
  Round 3 confirmed it deeper still (−428.5 meV, 400× the gate width) and it sits as entrant
  decisions R3/A8.8. `grep -c BASIN_DRIFT docs/70` = 0. **This belongs at the top of §3, not absent
  from it**, and its disposition costs 0 SU.
- **A5.1(a) and A5.1(c) have no readout on the A0 grid, and the primary tracker cannot exist there
  for half of it.** *(Corrected 2026-09-03 — this bullet first read "registered, zero-DFT, **unscored**"
  and "**no script in the repo reads a `.lowdin.txt`**". Both were false, both were mine, and both were
  one `grep` from refutation: `src/dft/lit1_urobustness.py` implements A5.1 (a)/(c)/(d) with tranche 1
  banked since 2026-08-12 at `docs/research/lit1_tranche1_uladder.json`, and `src/dft/extract_lowdin.py`
  produces **and validates** the artifacts, with `tests/test_extract_lowdin.py` T1 checking the whole
  bank of 265. See docs/45 "A11.R7 SCORED, 2026-09-03".)* What is true, and sharper: tranche 1 covers
  **Cr and Co on the P7 ladders only**, and says in its own scope section that "Löwdin populations
  (projwfc.x) are **not in this tranche**". The A0 grid — where A7.2 and A7.3 are scored — had no
  A5.1(a) readout, and the A0 main decks for **Ti, Ru and Ir carry no `nspin` card at all** (0 of 28,
  0 of 32, 0 of 32), so the sphere moment A5.1(a) makes primary is structurally unavailable on exactly
  the A7.3 under-the-floor set. **CLOSED 2026-09-03 by A11.R7** (docs/43, registered at `afb9692`;
  `src/dft/a0lowdin_valence.py`; 230 banked Löwdin artifacts, 0 SU): R7-P3's registered falsification
  fired — |δq_c| interleaves the two A7.3 groups completely while their spans differ 4–14×, so the
  valence-change explanation of the split is falsified on this tracker.
- **The census contradiction is owed**: `docs/45:255-256` records "38 AGREE / 0 REFUSED / 2
  UNVERIFIED" against 6 measured mismatches, to be reconciled *before any readout is quoted* — and
  §§3–6 quote `a0main_readout.json` throughout.
- **The TiO₂ *OOH placement recurrence** (2.041 Å, `adsorbate_starts`, `PULL_TO`: a solved defect
  whose remedy never propagated from the MACE path to the DFT deck path) is the file's own thesis in
  miniature and is unnamed.
- **R2 is a third option Q-9 does not offer**: `electron_maxstep` 500 → 1500 on `Co s0_O__2x1v_mir`,
  ~500 SU, a separate open registered-parameter call.
- **Q-5 hides the S8 preconditions**: the Cr(VI) risk assessment and the STS sponsor-of-record gate
  any melt; both grep to 0 here.
- **The report itself is unpriced** — S-5 carries no hour estimate, against a hard page limit, no
  outline in the tree, while the file's own framing fact is that entrant-hours are the scarce
  resource.
- Dirty/uncommitted CI files (`.github/ci/run_oc20.py`, `.github/workflows/s1-controls.yml`).

### 8.3 Dimensions the sweep did not cover

Pseudopotential/basis-set sensitivity (H-9 prescribes a "TRANSFERRED / NOT MEASURED" sentence with
**no citation behind it** — SSSP/Prandini, GBRV/Garrity and the PP-family adsorption literature are
unopened); gas-phase reference error (the readout has a `gas_reference_disclosure` field and this is
among the most-cited silent errors in CHE-ladder OER work); the per-metal spread of ZPE−TΔS constants
(item 6 is correctly refuted, but the borrowed Man-2011/Valdés constants have no in-house ph.x table);
coverage / lateral interactions (7 of 9 rows > 0.10 eV, one of the largest measured knobs); and
experimental OER benchmarking protocol, while Q-6 proposes two bench measurements.

### 8.4 What the critique resolved in the file's favour

- **H-10's Cr `oosh` state is CONFIRMED a physisorbed O₂ + surface-H, by direct re-measurement** of
  the converged geometries: shortest O–O **1.227 Å**, those two O atoms 3.09/3.77 Å from the nearest
  Cr, and the H at 0.971 Å on a *different* O. The docs/54 item-10 correction is warranted.
- The file's own §0 stale-brief corrections check out (balance **59,761.1 SU**, ladder exhausted,
  32 rung outputs on disk; `runs/probe/Co_uladder` holds 12 converged `.out`).
- The H-8 binomial masses are arithmetically correct (A7.3 middle band 35/64 = 0.547; n = 5 → 0.625;
  A7.2 ≥3/6 = 42/64 = 0.656).
- All ~35 citations spot-checked against Crossref/arXiv/DataCite resolve as cited, **except C-1 and
  C-2 above**, and R-12's flag that Warford/Thiemann/Csányi arXiv:2601.21056 carries no journal-ref
  is correct.

### 8.5 One correction outside this file

docs/68 §8 quoted Ru as "4.3 meV short" of A7.3's floor and its neighbours as gaining/losing
3.5 / 8.4 / 4.6 meV. Those are half-distances in the volt convention and are **not commensurate with
the 15.5 meV** they invite comparison to — the mixing docs/60 §6 and docs/63 §6 explicitly forbid.
Corrected in place 2026-09-02: distances are 2 × (0.10 V − span/2) throughout, so **Ru closes from
15.5 to 8.5 meV, Ti from 112.5 to 95.6, Ir widens from 72.6 to 81.7 — each change exactly its D_M.**
The error was mine, in the same session that wrote this file's brief.
