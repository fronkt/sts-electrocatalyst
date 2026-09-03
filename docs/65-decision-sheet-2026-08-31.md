# 65 — Decision sheet for the entrant, 2026-08-31

This sheet is an draft INDEX of open decisions, not a source: the cited drafts govern,
and where this sheet and a draft disagree, the draft wins. Nothing here adds an option,
removes an option, or elects among options on any verdict-bearing row — where a draft
itself flags a PROPOSED or recommended value, that value is quoted AS the draft flags it
and remains a proposal until re-authored. Every threshold and convention election is the
entrant's (Frank's). Each row states the one dated line that discharges it.

**Provenance:** supporting infrastructure (per A7.7 and the docs/55 disclosure
style); the entrant may override any line here by a later dated line. **Scope:** this sheet
consolidates the decisions live in the docs/58–64 arc plus tasks/todo.md's 2026-08-31 plan
(:884-895). The older docs/52 / docs/55 layer is NOT re-verified here; those sheets remain
the index for their own rows.

> **[SHEET DISCHARGED 2026-08-31, later the same day]** — every verdict-bearing row
> on this sheet was elected under the entrant's 2026-08-31 directive; the elections,
> their adversarial verification, and the instruments that carry the dated lines are
> indexed in **docs/66** (docs/43 Amendment 11 + the P-DISPOSITION addendum; docs/59
> §3c GRANTED; docs/67). Corrections to THIS sheet recorded there (docs/66 §7): the
> status header's "Oct 15 hard freeze" line is superseded (REPORT LOCK, backstop
> Nov 5 8:00 pm ET); the 76-SCF tally omitted Family C's 20 Ru/Ir slab/s0_O decks;
> the SU tops read 532/228/380/76 at the sheet's own band (the 28/12/20/4-SCF sets)
> and the closing 380–1,420 reads 380–1,444; Row 9's "24 banked SCFs" is 28 (4
> states × 7 U rungs). This sheet stays as the historical index; the drafts +
> docs/66 govern.

**Status header — facts of record, 2026-08-31:**

- **Oct 15 hard freeze.** Per the registered P-DISPOSITION rule, any prediction not scored
  by Oct 15 is WITHDRAWN-UNSCORED with its date (docs/43 A7.7 :1436-1440, as indexed by
  docs/52 row 65).
- **Zenodo ride-along exists Sep 18** — A10's deposit date ("A10 | BEEF row | NOT DRAFTED;
  gated on S0(a) | Sep 18", docs/52 row 62; docs/61 §A11.11).
- **Anvil balance 69,783.7 SU, queue EMPTY.** "All scored compute is entrant-gated
  (docs/59 §3c uncountersigned; docs/61 decisions 1-4 open; item 10 open). Anvil queue
  EMPTY, 69,783.7 SU. Plan: submit NOTHING; make every arm launch-ready."
  (tasks/todo.md:886-887.)

**SU arithmetic, derived once here and reused per row (arithmetic, not a recommendation):**
Stage 0 of A0-SPIN was array 20221409, 10 tasks, all COMPLETED exit 0:0, 02:22–08:41
elapsed on 128 cores (docs/62:5 provenance block; docs/62:59-60 "Stage 0 ran 29 Aug 2026 on
128 cores"). The elapsed unit is mm:ss — QE WALL times in `runs/a0/spin/*/*.out` run
2m01.61s–8m15.18s, confirming it. Anvil CPU SU = core-hours, so the measured cost per
equalised 1×1 SCF ≈ 128 × (142–521 s) / 3600 ≈ **5–19 SU/SCF**. Calibration point: the
S0(h) family's measured cost was **1,067.9 SU** (70,851.6 → 69,783.7, docs/64:24) against
its 4,000–7,600 SU pre-estimate (docs/43:1997) — actuals ran ~4–7× under estimate; that is
a calibration, not a promise. The sum of ALL gated deck sets on this sheet ≈ 76 SCFs ≈
**380–1,420 SU ≈ 0.5–2 % of the 69,783.7 SU balance**. The binding constraint is
signatures, not compute.

**How to discharge a row:** write one dated line in the named place (the campaign's
dated-line instrument — the style of docs/43:1979's `[AFM-SCOPE RESOLVED 2026-08-30:
STANDALONE_FOUR]`). The `Sign:` field on each row gives the shape of that line with the
election slot left blank; the choice inside the brackets is the entrant's alone.

---

## Critical path — the minimal signature set that unblocks the highest-information compute

Each line: signature → what it unblocks — consequence — cost.

1. **docs/59 §3c countersignature (Row 1)** → the Ti arm, and specifically Ti `s0_OH` at
   u900 — "the single highest-information deck in the arm … the term that decides whether
   the 153 meV cancels" (docs/62:253-255) — 1 SCF ≈ 5–19 SU (full Ti Stage 1: 12 SCFs ≈
   60–225 SU); ungranted, it also holds A7.3's denominator at a provisional 6 (docs/60:139-143).
2. **docs/61 decisions 1–3 (Rows 3–5), with Row 1 and the deposit (Rows 2/18)** → Stage-1
   Ru/Ir submission — the first scored decks of the arm ("Items 1–4 gate the first scored
   deck", docs/61:242) — 20 SCFs ≈ 100–370 SU, pre-built 2026-08-31, NOT submitted.
3. **docs/61 item 10 (Row 15)** → the Ru AFM probe at both U endpoints — "now the only
   live path to A7.3" (docs/64:145-147); "Only the docs/61 item 10 Ru AFM probe, run at
   both U endpoints, acts on A7.3" (docs/64 §3) — 4 SCFs ≈ 20–75 SU, pre-built 2026-08-31, NOT
   submitted.

---

## I. docs/59 — the signature that moves a banked verdict (two acts)

**1. docs/59 act 1 of 2 — re-author/countersign the roster correction, including the §3c licence for the seven Ti relaxations**
Where: docs/59 §3c (:116-206; licence sentence :200-203; footprint :185-188), §5 item 1
(:272-273), :180; docs/60 §6 fact 5 (:139-143), §11 (:238-246); docs/62 §6 (:207-211), §7
(:213-222), §8 (:224-238), §9 (:240-259); docs/64 §4 (:109-111), §6; tasks/todo.md:886-891.
Decides: Whether Frank countersigns docs/59, and inside §3c whether he GRANTS or WITHHOLDS
the licence for the seven 1×1 TiO₂ relaxations — "4 in tranche 3 (slab + 3 adslabs) and 3
escalation repairs (`s0_OOH_r1`/`r2`/`r3`), seven in total, all in the 1×1 cell"
(docs/59:187-188) — run outside A6.6's declared footprint ("~160 fixed-geometry SCFs and
zero relaxations"; it "does not license … any relaxation in any cell", docs/59:185-186,
docs/60:139-141).
**Flag: this signature MOVES a banked verdict.** docs/60 §6 fact 5: "If withheld, the Ti
rows are WITHDRAWN-UNSCORED, the denominator falls 6 → 5 and the status reverts to 'NOT
YET MET — UNDECIDED'. **Two banked fields are provisional on a signature.**"
Options as drafted: GRANT (the Ti rows stand; A7.3's denominator stays 6; the status stays
NOT MET 3/6) vs WITHHOLD ("A7.3's denominator shrinks and the Ti rows are
WITHDRAWN-UNSCORED under A7.7", docs/59:201-203). NO default and NO recommendation is
drafted anywhere — "the licence is the entrant's to grant or withhold when countersigning
this document" (docs/59:200-201), and §5 item 1 states there are "no thresholds to set"
(docs/59:272-273).
New evidence the docs route to this row (listed, not weighed): the Ti `s0_OOH` U = 9
spontaneous spin-symmetry breaking, ≥ 153.07 meV from a genuinely zero seed (docs/62 §5,
:121, :134); the s0_O AFM flat-moment instability — "itself evidence for the open
NM-vs-AFM class discussion (docs/59 §3c, docs/61)" (docs/64:109-111).
Unblocks: the Ti half of A0-SPIN Stage 1 — exactly 12 SCFs: Ti `s0_OH` + `s0_OOH` × u000
+ u900 × seeds {0.10, 0.30, 0.50} (docs/62:213-218), including the arm's single
highest-information deck Ti `s0_OH`@u900 (Row 8); +12 more (Ti slab + `s0_O` at both
endpoints) iff A7.2 is re-read (Row 13); use of any Ti Stage-0 row as scored evidence
(docs/62 §8 MAY NOT "use any Ti row from this arm — Stage 0's included — as evidence for a
scored claim while docs/59 §3c is uncountersigned"); the 2026-08-31 build track REFUSES Ti
Stage-1 decks pending §3c (tasks/todo.md:890-891). One free candidate already banked: the
null-seed (s0_OOH, u900) energy −1298.17043625 Ry, which the §A11.6 selection rule may
consider alongside the three seeds (docs/62:220-222).
Cost: 12 SCFs ≈ 60–225 SU (+12 SCFs ≈ 60–225 SU for the Row-13 A7.2 re-read).
Deadline: none dated in the drafts; coupling — "decision item 4 has moved from bookkeeping
onto the critical path: it now gates the most informative measurement in the arm, against
an Oct 15 hard freeze" (docs/62:209-211).
Sign: one dated line at countersignature, in docs/59 §3c —
`[§3c LICENCE 2026-__-__: GRANTED]` or `[§3c LICENCE 2026-__-__: WITHHELD]`.

**2. docs/59 act 2 of 2 — the deposit** *(an act, not an election; the vehicle election is Row 18)*
Where: docs/59 header (:6), §5 item 2 (:274-275).
Decides: When the correction of record becomes a registration — docs/59 §5 lists the two
acts separately: "1. Re-author / countersign this document … 2. Deposit it". "Until
deposited, its authority is its commit timestamp" (docs/59:6).
Blocks: the correction of record becoming a registration; every A11-governed job
downstream of Row 18's vehicle choice.
Deadline: none dated; bound to Row 18's arithmetic.
Sign: the deposit itself is the signature (dated DOI line in docs/59 once Row 18 is
elected).

---

## II. Amendment 11 — the gates on the first scored Stage-1 deck

docs/61's own ordering: "Ordered by what blocks what. Items 1–4 gate the first scored
deck." (docs/61:242.) Item 4 is Row 1 above. Rows 6–8 entered from Stage 0 (docs/62 §9)
and sit in the same gate.

**3. (docs/61 item 1) The headline census election — §A11.5**
Where: docs/61 §A11.5 (:116-133), :244.
Decides: Which census is A7.3's headline.
Options as drafted: **PROPOSED, and recommended** (as the draft itself flags it): "the
as-built **3 of 6 remains the registered score of A7.3 and remains the headline**. The
spin-equalised census is a registered **sensitivity** whose only power is to select which
caveat sentence is true. It cannot promote A7.3 to CONFIRMED." (docs/61:120-122.)
Alternative as drafted: "The entrant may instead elect the equalised census as primary.
That election must be dated and committed before any Stage 1 deck is submitted, not
after." (docs/61:132-133.)
Unblocks: with Rows 4–5, Row 1 and the deposit — the Ru+Ir Stage-1 deck set:
`s0_OH`/`s0_OOH` × u000/u900 × 3 seeds = 24, minus 4 banked-free rungs (u000 seed-0.50 =
the P11 rows, reproduced in Stage 0 to ≤ 0.044 meV, docs/62:18) = **20 SCFs**. The build
track pre-builds these 2026-08-31, NOT submitted (tasks/todo.md:890-891).
Cost: (of the deck set it gates) 20 SCFs ≈ 100–370 SU.
Deadline: "before any Stage 1 deck is submitted, not after" (docs/61:133); Oct 15 behind
everything.
Sign: one dated line — `[A11.5 HEADLINE CENSUS 2026-__-__: AS-BUILT 3-of-6]` or
`[… : EQUALISED-PRIMARY]`.

**4. (docs/61 item 2) The seed set and the selection tolerances — §A11.6**
Where: docs/61 §A11.6 (:135-164), :245.
Decides: The starting-guess rule and the per-(metal, state, U) selection rule, registered
before any deck runs.
Options as drafted: **PROPOSED seed set S = {0.10, 0.30, 0.50}** — 0.50 "mandatory, not
merely incumbent: it is the seed of the eight banked P11 SCFs … the campaign's **only**
cross-machine determinism control on a spin-polarised code path"; 0.10 "the only seed this
campaign has ever scored and selected (the Fe *OOH pilot winner)"; 0.30 "the detector for
a non-monotone seed→basin map" (the Fe pilot measured "0.5, sandwiched between two that
work, traps +276.57 meV up"). Selection **PROPOSED**: "lowest converged total energy per
(metal, state, U) across the three seeds **and** the banked nspin = 1 energy, with a hard
variational floor; ties within 1 meV to the smallest |seed|". "Exactly 0.0 is separately
fatal" except the two whitelisted null-seed machinery controls (§A11.7).
Unblocks: the same Ru+Ir deck set as Row 3.
Deadline: before Stage-1 submit (gate on the first scored deck, docs/61:242).
Sign: one dated line — `[A11.6 SEEDS+SELECTION 2026-__-__: AS PROPOSED]` or the entrant's
re-authored rule.

**5. (docs/61 item 3) P-SPIN-DELTA's movement threshold and falsification band — §A11.3, now three live options**
Where: docs/61 §A11.3 (:102-105), :246; docs/63 §4.2 (:166-178), §7 item 2 (:227-228);
docs/64 §3 (:62-70).
Decides: The registered movement threshold for D_M and its falsification band.
Options as drafted — the drafts themselves now put three positions on the table:
(i) as drafted in docs/61: "**PROPOSED** threshold: |D_M| ≥ 0.033 eV on ≥2 of 3 metals —
the *bottom* of gate (h)'s measured 33–64 meV class" — but docs/63 §4.2 found that
justification points at the WRONG quantity (33–64 meV is an adsorption-energy class; D_M
is a c_M quantity; the same data through c_M gives 25.9 meV): "it should not stay at
0.033 eV citing a justification that points at a different quantity" (docs/63:176-177);
(ii) docs/63's re-anchor: "Re-anchor to 0.026 eV, or re-justify" (docs/63:228);
(iii) docs/64 §3's third position: the relaxed measurement lands the c_M level at
0.0325 eV ≈ 0.033 — "Live options: 0.026 (fixed-geometry c_M level) or 0.033 (relaxed c_M
level — keeps the registered number, replaces its justification). Either way the
amendment must state it is a level standing proxy for a swing."
Falsification band **PROPOSED** (docs/61:104-105): "all three show |D_M| < 0.005 eV.
*Both numbers are the entrant's to re-author.*"
Unblocks: scoring of the arm's mechanism prediction; part of the A11 deposit text.
Deadline: before Stage-1 submit (gate on the first scored deck, docs/61:242).
Sign: one dated line — `[A11.3 THRESHOLD 2026-__-__: 0.026 | 0.033-REJUSTIFIED | other +
justification; FALSIFICATION 0.005 | other]`.

**6. (docs/62 §9 new item 1) Authorise the §5.2 re-registration of the ntyp=3 null-seed control**
Where: docs/62 §5 (:113-181; §5.2 :169-181), §9 item 1 (:248-249); docs/61 §A11.7.
Decides: Whether the registered null-seed criterion is re-registered. As registered it is
UNSATISFIABLE as written on an odd-electron state whose unpolarised solution is unstable —
Ti `s0_OOH`@u900 spontaneously broke spin symmetry from a genuinely zero seed, −153.072
meV, totmag 1.04 (docs/62:121, :134).
Options as drafted: the PROPOSED replacement (docs/62 §5.2, "entrant's to authorise"):
"(a) index-rule leg — PASSES as run; (b) stability leg, reported not scored … **Ti
`s0_OOH` at U = 9.0: BREAKS, ≥ 153.07 meV, SPIN-UNSTABLE.**" No alternative is drafted;
declining leaves the criterion as registered and unmeetable.
Blocks: any Stage-1 row being scored against docs/61 §A11.7 as written — "before any
Stage-1 row is scored against docs/61 §A11.7 as written" (docs/62:248-249).
Deadline: before the first Stage-1 row is scored.
Sign: one dated line — `[A11.7 NULL-SEED RE-REGISTRATION 2026-__-__: AUTHORISED]` or
`[… : DECLINED]`.

**7. (docs/62 §9 new item 2) The Ir-slab contingency**
Where: docs/62 §4 (:84-112; the firing :94, predicted from P11 :100-102; scope :105-106),
§9 item 2 (:250-252).
Decides: What an Ir slab with no floor-clearing spin-equalised row IS. The variational
floor fired on the Ir slab at seed 0.50 (+0.583 meV above nspin = 1, predicted in advance
from P11's +0.592 meV). "The registered seed set {0.10, 0.30, 0.50} supplies two further
attempts at the Ir slab in Stage 1."
Options as drafted: "If none of {0.10, 0.30, 0.50} clears the variational floor on the Ir
slab, Ir has no spin-equalised slab row and no equalised η. Decide now whether that is a
WITHDRAWN row, an extended seed set, or a stated omission." (docs/62:250-252.) "That
contingency is not covered by docs/61" (docs/62 §4).
Note (scope as the doc states it): "E_slab cancels identically in c_M, so A7.3's quantity
is untouched by this rejection" (docs/62:105-106) — it binds on every ΔG/η and any A7.2
re-read (couples to Row 13).
Deadline: "Decide now" (docs/62:252) — i.e. before Stage-1 submit.
Sign: one dated line — `[IR-SLAB CONTINGENCY 2026-__-__: WITHDRAWN-ROW | EXTENDED-SEEDS |
STATED-OMISSION]`.

**8. (docs/62 §9 new item 3) Ti sequencing: s0_OH@u900 first** *(sub-row inside Row 1's licence)*
Where: docs/62 §9 item 3 (:253-255), §6 (:187, :207-211); docs/61 §A11.10 (:227).
Decides: The order of Ti compute IF Row 1 grants the licence.
Options as drafted: "Ti's `s0_OH` at U = 9 is the single highest-information deck in the
arm — it is the term that decides whether the 153 meV cancels. If any Ti compute is
licensed at all, it should be licensed first." (docs/62:253-255.) docs/61 §A11.10's
governance sequencing ("Ru first, then Ir, and Ti only after countersignature",
docs/61:227) is "unchanged and still correct" while §3c is unsigned (docs/62:207-211).
Cost: 1 SCF ≈ 5–19 SU.
Deadline: with Row 1.
Sign: folds into Row 1's dated line (append `; s0_OH@u900 FIRST` or the entrant's own
order).

---

## III. The Ti convention question

**9. (docs/60 §11 + docs/62 §9 new item 4) Should the Ti arm run nspin = 2 throughout?**
Where: docs/60 §11 (:240-242); docs/62 §9 item 4 (:256-259), §5.1 (:166-167); docs/59:180.
Decides: A convention change across all 4 Ti states and 24 already-banked SCFs —
"conventions are the entrant's to set, not the assistant's" (docs/59:180).
Options as drafted: NONE is proposed anywhere. The question "now has evidence. ≥ 153.07
meV is the measured cost of the nspin = 1 convention at one point of the Ti ladder. It is
still a convention change across 4 states and 24 banked SCFs, and it is still Frank's."
(docs/62:256-259.) Sharpened by docs/62 §5.1: on all three nspin = 1 metals every term
entering A7.3's quantity (`s0_OH`, `s0_OOH`) is an odd-electron state described as a
closed shell — "a problem confined to, and unavoidable in, the numerator"
(docs/62:166-167).
Blocks: nothing named until elected; if elected, a re-run scope decision follows (not
drafted anywhere).
Deadline: none stated.
Sign: one dated line — `[TI CONVENTION 2026-__-__: NSPIN=1 STANDS | NSPIN=2 THROUGHOUT +
re-run scope to follow]`.

---

## IV. Amendment 11 — the remaining decisions (docs/61 items 5–12)

**10. (docs/61 item 5) The A7.7 disposition mapping for a middle band**
Where: docs/61 :248-249; docs/60 §6 fact 4 (:134-138); docs/64 §6 ("A7.7 disposition"
open-items line).
Decides: What a 2-or-3 outcome licenses — "A7.3 registered consequences for ≥4 and ≤1
only; 2-or-3 maps to nothing, in the old census and the new one alike" (docs/61:248-249).
Options as drafted: none — the vocabulary gap is the finding: "'NOT MET' is a token the
scorer invents; it is **not** in A7.7's vocabulary (WITHDRAWN-UNSCORED / HELD / TRIGGERED)
and nothing registered says what a middle outcome licenses. Reported, not mapped — the
entrant decides the disposition." (docs/60:134-138.)
Blocks: what the report may state A7.3's outcome AS; every A7.3 sentence.
Deadline: none dated; before any report sentence scores A7.3; Oct 15 behind everything.
Sign: one dated line — `[A7.7 MIDDLE-BAND DISPOSITION 2026-__-__: <the entrant's mapping,
in A7.7's vocabulary or his own>]`.

**11. (docs/61 item 6) The denominator rule**
Where: docs/61 :250-252.
Decides: The count's survival under withdrawal — "rewrite '≥4 of the 6' as a fraction or
an explicit per-denominator table, so the count survives Ti's rows being withdrawn
(6 → 5). '≥4 of the 6' is undefined against five metals and that contingency is live
right now." (docs/61:250-252.) Couples to Row 1.
Options as drafted: fraction vs explicit per-denominator table (both from the quoted
sentence; no preference drafted).
Blocks: A7.3's scoring rule under a withheld licence; part of the A11 deposit text.
Deadline: with the A11 deposit.
Sign: one dated line — `[A7.3 DENOMINATOR RULE 2026-__-__: FRACTION | TABLE, as written
out in A11]`.

**12. (docs/61 item 7) Whether Cr/Mn/Fe owe a matching seed search (~28 SCFs)**
Where: docs/61 :253-256.
Decides: Search-effort parity — "Without it the arm equalises the spin *keyword* but not
the search *effort*: Cr ran one seed, Mn one, and only Fe *OOH got a three-seed pilot — so
the three new metals would be searched harder than the three they are compared against."
Options as drafted: yes/no, and the draft flags its own position: "**Recommended: yes.**"
(docs/61:256.)
Cost: ~28 SCFs ≈ 140–520 SU.
Deadline: none dated; Oct 15 behind everything.
Sign: one dated line — `[CR/MN/FE SEED SEARCH 2026-__-__: RUNS | DOES NOT RUN + reason]`.

**13. (docs/61 item 8) Whether A7.2 is re-read on the equalised rows — §A11.9**
Where: docs/61 :257-258, §A11.9 (:205-212); docs/62 §7 (:216-218).
Decides: Whether the arm re-reads A7.2 or states the omission — §A11.9: the arm may not
re-score only the prediction that failed; "if the equalised rows are read for A7.3, A7.2
is re-read on the same rows or the omission is stated with its reason" (docs/61:210-212).
Options as drafted: re-read vs stated omission with reason.
Cost: if re-read, Ti needs +12 SCFs (Ti slab + `s0_O` at both endpoints, docs/62:216-218)
≈ 60–225 SU; Ru/Ir re-reads run through the Ir-slab contingency (Row 7).
Deadline: with the equalised census reading.
Sign: one dated line — `[A7.2 EQUALISED RE-READ 2026-__-__: RE-READ | OMITTED + reason]`.

**14. (docs/61 item 9) Whether Mn's A7.5 AFM condition is in scope or explicitly deferred**
Where: docs/61 :259-261; docs/43:1406-1407 (A7.5, registered); docs/60 §11 (:243-244).
Decides: Scope only — no arm is designed or priced anywhere in the read set.
Options as drafted: in scope vs explicitly deferred. The registered condition:
"β-MnO₂ is antiferromagnetic and `gen_rutile.py` initialises it FM — either the AFM arm
runs or every materials-facing Mn sentence is struck" (docs/43:1406-1407). Currently
UNMET — "the Mn column is FM-initialised and may not be used as a materials-facing
absolute η" (docs/60:243-244); Mn "carries the largest span in the numerator (0.6307 V)"
(docs/61:260-261).
Blocks: every materials-facing Mn sentence — per the registered either/or they stay
struck unless the arm runs; a written deferral accepts that consequence, it does not
lift it.
Deadline: none dated; Oct 15 behind everything.
Sign: one dated line — `[A7.5 MN AFM ARM 2026-__-__: IN SCOPE (design to follow) |
DEFERRED + the struck-sentence consequence accepted]`.

**15. (docs/61 item 10) Whether the Ru AFM probe runs — now the ONLY live path to A7.3**
Where: docs/61 :262-264; docs/63 §4.3, §7 item 4; docs/64 §3 (:56-61), §6 (:145-147);
tasks/todo.md:892.
Decides: Whether the probe runs — as drafted: "(4 SCFs, gate-(h) recipe, recorded either
way, not entering the A7.3 score)" (docs/61:262-263). The item's second half — sequencing
with the owed S0(h) re-anchors — no longer has anything to sequence against: that family
reached terminal state 2026-08-30 (docs/64 §1), and docs/64's own restatement of the item
carries only the probe half ("Ru AFM probe — now the only live path to A7.3", :145-147).
Options as drafted: runs vs does not run.
Status upgrade, quoted: docs/63 §4.3 — "The deck set that would act on A7.3 is docs/61
decision item 10's Ru AFM probe, and even that needs both U endpoints to produce a D_M";
docs/64 — "Only the docs/61 item 10 Ru AFM probe, run at both U endpoints, acts on A7.3"
(§3) and "Ru AFM probe — now the only live path to A7.3" (:145-147).
Context that makes it decisive (facts, not weights): Ru sits +15.5 meV from A7.3's floor
(docs/60:127); the AFM c_M level at U = 0 is −25.9 meV fixed-geometry (docs/63:135) /
−32.5 meV relaxed (docs/64:41), both exceeding 15.5 — but both are LEVELS whose
U-dependence is unmeasured (docs/63 §4.1; docs/64 §3).
The 2026-08-31 build track pre-builds the probe decks at both U endpoints, NOT submitted
(tasks/todo.md:892).
Cost: 4 SCFs ≈ 20–75 SU.
Deadline: none dated; Oct 15 behind everything.
Sign: one dated line — `[RU AFM PROBE 2026-__-__: RUNS (both U endpoints) | DOES NOT
RUN]`.

**16. (docs/61 item 11) Amendment number and ledger placement**
Where: docs/61 :265-267; sibling: docs/52 row 63 (the six-row-cap decision, "before
Sep 20").
Decides: Where P-FLOOR-U-SPIN and P-SPIN-DELTA live — "The body cap at docs/43:1930 is
already reached; P-FLOOR-U-SPIN and P-SPIN-DELTA cannot silently become a seventh and
eighth body row." (docs/61:265-267.)
Options as drafted: none enumerated here; the sibling docs/52 row 63 mechanism (name the
displaced prediction, or appendix placement) is that row's text, not re-verified here.
Blocks: part of the A11 deposit text; the body-figure ledger.
Deadline: docs/52 row 63's sibling date — before Sep 20.
Sign: one dated line — `[A11 LEDGER PLACEMENT 2026-__-__: <numbers + body/appendix
placement, in the entrant's words>]`.

**17. (docs/61 item 12) Commit the Löwdin extractor before this arm's Löwdin is extracted — §A11.8 item 4** *(conditional — may be DISCHARGED-BY-BUILD 2026-08-31)*
Where: docs/61 :268, §A11.8 item 4 (:201-204); tasks/todo.md:893.
Decides: Nothing verdict-bearing — the recipe "exists only in shell history; no script is
in the repo" (docs/61:201), and the nspin = 2 Löwdin block has a different shape.
Status: the 2026-08-31 launch-readiness plan assigns this to the build track ("Löwdin extractor
committed (docs/61 §A11.8 item 4 / decision 12), validated on banked outs",
tasks/todo.md:893). If that track lands, this row is DISCHARGED-BY-BUILD and needs no
signature; if it does not land, the row reverts to an open obligation.
Deadline: before this arm's Löwdin is extracted.
Sign: none owed if the build track lands; otherwise one dated line acknowledging the
obligation.

---

## V. The deposit vehicle

**18. Deposit vehicle for docs/59 and Amendment 11: own Zenodo version now, or the A10 ride-along on Sep 18**
Where: docs/59 §5 item 2 (:274-275); docs/61 §A11.11 (:231-237); docs/52 row 62 (A10's
Sep 18 date).
Decides: The vehicle — docs/59: "Deposit it (own Zenodo record, or alongside A10 on
Sep 18 — entrant's choice; the registration's own instrument is the dated deposit)."
docs/61 §A11.11: "Whether this deposits as its own Zenodo version now or is appended with
A10 on Sep 18 is the entrant's call; under A7.8/A8.9/A9.7 the deposit precedes the first
*governed* job either way."
Options as drafted: deposit-now vs Sep 18 ride-along. Neither is recommended anywhere —
both are "the entrant's call/choice" verbatim.
Consequence, pure date arithmetic (stated as such, not a recommendation): the ride-along
means no A11-governed scored deck runs before Sep 18, compressing the Stage-1 window from
~6.5 to ~4 weeks before the Oct 15 freeze; deposit-now lets Stage 1 launch as soon as
Rows 1+3+4+5 are signed.
Deadline: the choice binds every governed job; the ride-along's own date is Sep 18.
Sign: one dated line — `[A11+59 DEPOSIT VEHICLE 2026-__-__: OWN VERSION NOW | A10
RIDE-ALONG SEP 18]`.

---

## VI. Sentence corrections owed (zero compute)

**19. (docs/63 §7 item 3) Restate docs/60 §6 fact 2 so the level-vs-swing distinction travels**
Where: docs/63 §7 item 3 (:229-230), §4.1 (:150-164); docs/64 §3; the sentence itself:
docs/60:127-129.
Decides: The restatement of a banked-artifact sentence — entrant-owned for exactly that
reason. The banked sentence compares a required swing (Ru's 15.5 meV of |Δc_M| across U)
to a level shift at a single U (the 33–64 meV class); "neither 33–64 meV nor 25.9 meV
bounds A7.3's error: both are levels, and A7.3 scores a difference of two levels"
(docs/63:162-163).
Options as drafted: restate only — "The conclusion does not change" (docs/63:230): 25.9
meV (now −32.5 relaxed, docs/64:41) still exceeds 15.5 meV, so "NOT MET is not settled"
survives on the right quantity.
Cost: zero compute.
Deadline: before the sentence is quoted anywhere downstream.
Sign: one dated line adjacent to the banked sentence (or in the error ledger) carrying
the restated wording in the entrant's words.

---

## VII. FYI — not decisions

*(Tagged as docs/52 tags non-verdict rows: nothing below elects anything.)*

**F1. RCAC-ticket standing rule** *(FYI — standing rule already stated; submission is the entrant's act)*
docs/64 §5 (:115-127): two early-phase OOM kills on two distinct nodes (a120, a200; a200
intermittent, not dead), MaxRSS far under the 237 GB allocation. Standing rule as stated:
"If a third early OOM lands, send the drafted ticket (anvil/rcac_ticket_draft_2026-08-24.md)
with the node list and timestamps." Count of record is 2-on-2 — the todo's earlier
"third/fourth OOM" lines were corrected in the docs/64-arc verification pass ("Also fixed:
my OOM miscount (2 on 2 nodes, not 'three/third' — caught pre-workflow)",
tasks/todo.md:876-877); docs/64 §5 governs. Submission is the entrant's act
(docs/55 Ruling 4 precedent: "nothing is sent by the assistant").

**F2. The dirty CI files** *(an action, not an election)*
`.github/ci/run_oc20.py` + `.github/workflows/s1-controls.yml` (the S1 CI handoff,
docs/57) carry the uncommitted `S1_OC20_ASSET_SHA256` pin — assigned to the 2026-08-31 build
track ("CI: finish + verify the uncommitted S1_OC20_ASSET_SHA256 pin … commit",
tasks/todo.md:889); open in docs/59 §5 item 3 and docs/60 §11 until committed.

**F3. Closed since the last sheets (so the tally is checkable)**
The gate-(h) AFM scope — RESOLVED by the entrant's dated line
`[AFM-SCOPE RESOLVED 2026-08-30: STANDALONE_FOUR]` at docs/43:1979 (the crossed reading
DEFERRED with reasons, not silently dropped) — discharging docs/63 §7 item 1 and docs/52
row 26. The S0(h) family itself — CLOSED OUT at 3 relaxed + GATE-1-confirmed rows + 1
recorded s0_O NOT_CONVERGED gap, 1,067.9 SU (docs/64 §1). Stage 0 of A0-SPIN is READ
(docs/62); Stage 1 is NOT built as of docs/62 and is being pre-built unsubmitted by
the 2026-08-31 parallel track (tasks/todo.md:890-892).

---

## Pre-staged launch assets (assembled 2026-08-31)

Facts of the tree, not decisions. Every asset below is UNSUBMITTED, carries a
NOT-LICENSED header naming the rows that gate it, and was adversarially verified
(byte-level deck-vs-parent diffs, independent index re-derivation, double-build md5
determinism) before landing. Nothing runs until the named row is signed.

- **Stage-1 A0-SPIN decks (Rows 3–5; Ti additionally Row 1):** 20 decks under
  `runs/a0/spin/{Ru,Ir}/` — s0_OH/s0_OOH × u000/u900 × the PROPOSED seeds
  {0.10, 0.30, 0.50}, minus the 4 Stage-0-banked u000-seed-0.50 rungs, which are
  inherited, not rebuilt. Builder `src/dft/build_a0spin_s1.py` (assertions A1–A12
  inherited from `build_a0spin.py`, plus Stage-1 guards S1-a..S1-g); manifest
  `runs/a0/m_a0spin_s1.txt` in the 4-field 47_submit row grammar with per-deck md5s
  as header comments. The builder HARD-REFUSES any Ti request until docs/59 §3c is
  countersigned; if Row 4 re-authors the seed set, one rebuild regenerates the tree.
- **Ru AFM probe decks (Row 15):** 4 decks under `runs/s0/h_afm_probe/` —
  {s0_OH, s0_OOH} × {AFM, NM} at U = 9.0, fixed 2×1v NM-relaxed geometry; the U = 0
  legs are banked, not re-run. Builder `src/dft/build_ru_afm_probe.py`; manifest
  `runs/s0/m_h_afm_probe.txt`. The manifest carries a QUESTION-FOR-THE-ENTRANT: the
  4-SCF enumeration is DERIVED (docs/61 registers only a count and "gate-(h) recipe")
  and the NM-relaxed-geometry choice is a live option — countersign both when electing
  Row 15. The AFM decks' HUBBARD card names BOTH Ru sublattice labels
  (`U Ru1-4d 9.0000` + `U Ru2-4d 9.0000`); a one-label card would silently leave the
  other sublattice at U = 0.
- **Löwdin extractor (Row 17 — DISCHARGED-BY-BUILD with this commit):**
  `src/dft/extract_lowdin.py` + `tests/test_extract_lowdin.py`; parses both the
  nspin = 1 shape and the nspin = 2 up/down/polarization shape, validated over every
  committed Stage-0 `*.projwfc.out`; wrote nothing under `runs/` — tree extraction
  happens after the commit, per Row 17's registered ordering.
- **OC20 CI pin (F2 — done):** the `S1_OC20_ASSET_SHA256` pin in
  `.github/ci/run_oc20.py` + `.github/workflows/s1-controls.yml` is finished and
  locally proven on all registered paths (pin-unset refuses BEFORE the download;
  a mismatch refuses before tar; case/whitespace-normalised). Electing mechanism (a)
  now requires the third repository variable — the bare 64-hex sha256. docs/57 §5.3's
  two-variable recipe is a dated record that predates the pin; correcting it is a
  dated addendum, never an in-place rewrite.

---

## Closing tally (checkable)

19 rows + 3 FYI entries. Row 2 is an act, not an election. Rows 8 and 17 are
conditional/sub-rows (8 folds into Row 1's licence line; 17 is DISCHARGED-BY-BUILD if
the 2026-08-31 build track commits the extractor). Row 19 is a sentence correction. All other rows are
verdict-bearing elections reaching the entrant with recommendations only where the drafts
themselves flag them — Rows 3, 5, 12 carry drafted recommendations (docs/61 §A11.5's
"PROPOSED, and recommended"; docs/63/64's live re-anchor options; docs/61 item 7's
"Recommended: yes"), and Row 1 explicitly carries NONE.

Compute unblocking map (arithmetic from the header note, not a recommendation):
- Rows 1+3+4+5 (+ the Row 2/18 deposit) → Ru+Ir Stage 1: 20 SCFs ≈ 100–370 SU; with
  Row 1 granted, Ti Stage 1: 12 SCFs ≈ 60–225 SU (`s0_OH`@u900 first per Row 8).
- Row 15 → Ru AFM probe: 4 SCFs ≈ 20–75 SU — the only deck set that acts on A7.3.
- Row 12 → Cr/Mn/Fe seed search: ~28 SCFs ≈ 140–520 SU.
- Row 13 → +12 Ti SCFs ≈ 60–225 SU.
- Total gated ≈ 76 SCFs ≈ 380–1,420 SU ≈ 0.5–2 % of the 69,783.7 SU balance.
