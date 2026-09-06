# 87 — The claim sentence: registered constraints, corrected numbers, prior drafts, tensions (2026-09-05)

**Status:** supporting infrastructure under A7.7 — *the draft proposes, the entrant decided, the
report paraphrases and never copies* (`docs/43:1441-1447`, `:1479-1480`). Nothing here is report
prose and no sentence of it may be reproduced verbatim in the report, essays or application
answers. The entrant's own claim sentence is owed as a dated line in `docs/45` §D and is re-tested
on **Sep 20** against only what has landed (`docs/43:1932`); the Sep 15 date in the Phase-2 plan
belongs to F8 (`docs/43:1945`), not to this sentence.

Every number and every constraint below was read from the tree on 2026-09-05 at the cited line.

---

## 0. The Phase-2 plan's instruction, and why it cannot be executed as written

Plan text: *"Draft the new claim sentence reflecting the docs/84:44 1×1 restriction (0.1725 V) and
the docs/83:27 MIDDLE BAND class claim. Discard the stale 0.4869 V draft."*

Three corrections, each load-bearing:

1. **0.1725 V is not the 1×1 number.** `docs/84:37-38`: the 1×1 (A7.1) pair is η 1.1554 V (pls 2)
   vs 1.6423 V (pls 1), |Δη| **0.4869 V**; the **2×1v adopted-cell** pair is 0.9240 V (pls 1) vs
   1.0965 V (pls 1), |Δη| **0.1725 V**. `docs/84:44` carries no number at all — it is the
   mechanism-scoping sentence ("the pls-flip sentence is now dead outside 1×1"). A sentence that
   attaches 0.17 V to the 1×1 restriction states the wrong cell's magnitude against the right
   cell's mechanism.
2. **0.4869 V cannot be discarded.** `docs/84:40`: "Both cells are always printed together from
   here, per A13.4's anti-selection clause." A13.4, `docs/43:3713-3714`: the result "is reported in
   the same table as A7.1's 1×1 pair so the two cells are always read together." `docs/84:130-131`
   puts on the may-not list: "0.487 V quoted without its cell and without the 0.17 V adopted-cell
   companion." What *is* stale is any **draft sentence** written before 2026-09-04 that led with
   0.487 V and read the pls flip as a general property of the projector — `docs/43:4090-4094`
   requires such a sentence to be re-authored, not patched.
3. **`docs/83:27` is a class verdict, not a class claim.** MIDDLE BAND, 3 of 5, whose registered
   wording ends *"the per-metal table is the result and no class claim is made"*
   (`docs/43:4031-4034`; `docs/83:31-33`). It enters a sentence as a per-metal statement or as the
   statement that the effect is not universal — never as "the class shows".

## 1. Numbers a claim sentence may carry — each with its cell and its pair

| quantity | value | where |
|---|---|---|
| 1×1 (A7.1) η, atomic → ortho-atomic | 1.1554 V (pls 2) → 1.6423 V (pls 1) | `docs/84:37` |
| 1×1 \|Δη\| | **0.4869 V** (0.4868562) | `docs/84:37`; `docs/43:3745` |
| 2×1v adopted-cell η, atomic → ortho-atomic | 0.9240 V (pls 1) → 1.0965 V (pls 1) | `docs/84:38` |
| 2×1v \|Δη\| | **0.1725 V** (0.1725164) | `docs/84:38`; `docs/43:4085` |
| ratio | the effect is 2.8× smaller in the production cell | `docs/84:50` |
| composition of the 1×1 Δη | constants +0.6500 eV, electronic **−0.1631 eV** (ortho is *lower* electronically); the constants table is 133.5 % of the number | `docs/43:3745-3752` |
| composition of the 2×1v Δη | entirely electronic, exactly insensitive to the ZPE/TS table | `docs/84:127-128` |
| robustness of the qualitative flip | survives 3.3× the ZPE band (1×1 only) | `docs/43` A13.6 |
| P-PROJ-6 class verdict | FIRES 3/5 {Fe, Ru, Ir} · INTERMEDIATE 1/5 {Mn} · NULL 1/5 {Ti}; Cr is calibration and enters no count | `docs/83:27-29`; `docs/43:4028-4034` |
| P-PROJ-6 per-metal Δη | see the table at `docs/83:14-22` (Ti +0.0010 V, Ru +0.4308 V, Ir +0.4596 V; Fe and Mn on their rows) | `docs/83:14-22` |

**Never in the sentence:** an absolute η for Cr, Fe, Co or Ni as a materials claim (A7.5,
`docs/43:1399-1401`, enforced by S7). The η values above exist only to define the paired
differences; the differences are what may be quoted.

## 2. The registered constraints

| id | constraint | source |
|---|---|---|
| C1 | No absolute η for Cr/Fe/Co/Ni as a materials claim; paired within-metal differences only | `docs/43:1399-1401` (A7.5) |
| C2 | Both cells always together; 0.487 V never without its cell and its 0.17 V companion | `docs/43:3713-3714` (A13.4); `docs/84:40, 130-131` |
| C3 | The pls flip is a **1×1-only** sentence in every statement of A7.1; a sentence reading it as general is stale and is re-authored | `docs/43:4085-4094` (A13.R8); `docs/84:44` |
| C4 | No class claim from P-PROJ-6: "real on some systems and not others; not universal; the per-metal table is the result"; any "this keyword moves η" carries "on some materials and not others" | `docs/43:4031-4034` (A12.R11); `docs/83:27-39` |
| C5 | The 1×1 0.487 V is 133.5 % constants table with an opposite-signed electronic part; quoting it without that disclosure over-reads it | `docs/43:3727-3752` (A13.6) |
| C6 | The arm does not say which projector is right; single points on atomic-relaxed geometries; one U, one material; nothing generalises beyond Cr | `docs/43:3724-3731` (A13.5); `docs/84:131-132` |
| C7 | **Ordering:** detector + exposure census leads; floor movement second; coverage-conditionality third; the central claim must be scorable from S1 + S2 + S6 alone | `docs/43:1932`; round-2 Q6, `docs/research/2026-08-15-lit-sweep-round2-synthesis.md:553-554` |
| C8 | **Eligibility:** "results to date of an unfinished study" is ineligible — nothing not yet landed may be stated as a result | round-2 F3, `docs/research/2026-08-15-lit-sweep-round2-synthesis.md:507-508`; `docs/43:1932` |
| C9 | No amendment sentence reproduced verbatim; the entrant paraphrases | `docs/43:1441-1447` (A7.7) |
| C10 | On any symmetry-ON corpus only LOCKED counts (lower bounds on exposure) may be claimed; "not LOCKED" is never "free" or "searched" | `docs/43:1870` |
| C11 | The sentence is the entrant's: "what does not exist is the entrant's own claim sentence"; STS Guidelines item 1 | `docs/43:1932`; `docs/70:189` |

## 3. Prior drafts, and the status of each

| draft | text | status |
|---|---|---|
| round-1 (a), `docs/research/2026-08-15-lit-sweep-round1-synthesis.md:227` | "A standard way of setting up catalyst simulations silently traps the calculation in the wrong geometry; I built a detector that finds it from a finished output file, showed it is present in the deposited data behind the field's canonical paper, and measured what it costs." | **Live in shape** (detector leads, C7) — but clauses two and three describe S1 and S2, neither of which has landed, so today it fails C8. It is the Sep-20 target shape, not a sentence that can be written today. |
| round-1 (b), same line | "The parameter choice that no convergence check constrains moves the exact thermodynamic limit of a catalyst by 0.22 V — 25 times the margin by which my own withdrawn result beat it." | **Stale.** The 0.22 V floor number predates A7/A13; the current paired numbers are 0.4869 V (1×1) / 0.1725 V (2×1v). Round-2 Q6 already ranked it second because it "reads as being about your own error". |
| `docs/44:176-180`, the one-sentence story | "I set out to find a cheap alloy to beat iridium. My screen's hidden errors turned out to be 10× larger than the differences I was ranking — …" | **Narrative, not the abstract's claim.** `docs/43:1932` asks the entrant to say which it is, as a dated line in `docs/45` §D; that line is still owed. |
| any sentence before 2026-09-04 leading with 0.487 V and a general pls flip | — | **Stale** by `docs/43:4090-4094` and now by C2/C3/C5 jointly. |

## 4. Tensions no draft can resolve — they are the entrant's

**T1 — Flagship versus registered ordering.** `docs/43:3618` and `:4091` call A7.1 / P-PROJ "this
campaign's flagship"; `docs/43:1932` and round-2 Q6 register that the detector plus the exposure
census *leads*. Today S1 (the core) and S2 (the Xu census) have not landed. A sentence that leads
with them states unlanded work as a result (C8); a sentence that leads with the projector result
inverts the registered ordering (C7). The two exits are (i) hold C7 and accept that the claim
sentence is not writable until S1 + S2 land — which is exactly what the Sep 20 re-test exists for
("if it does not stand, a stage is cut rather than hoped for"); or (ii) the entrant re-registers the
ordering by a dated line, a governance act that is his alone. Drafting cannot choose between them.

**T2 — Qualitative versus quantitative projector claim.** The qualitative claim (the limiting step
flips) survives 3.3× the ZPE band but is 1×1-only and its magnitude is 133.5 % constants table.
The quantitative adopted-cell claim (0.17 V, purely electronic) survives the cell change but carries
no mechanism. One sentence can carry one of them cleanly, or both with two explicit scopes; it
cannot carry the 1×1 magnitude as if it were the production-cell effect.

**T3 — "Class" language.** P-PROJ-6's registered finding *is* metal-dependence. The honest sentence
is about non-universality — a weaker-sounding but registered result — and the per-metal table is the
result, not an illustration.

## 5. Candidate sentences

Four were drafted and all four were refuted; they are reproduced with their defects in §6 so that
the reasons stay attached to the text. None is offered for paraphrase. What survives of them — the
clauses that passed every lens — is listed at the end of §6.

## 6. The adversarial pass of 2026-09-05 — four candidates, twelve refutations, none survives

Four candidate sentences were drafted against §1–§4 (one per possible lead) and each was attacked
by three refuters with distinct lenses (textual compliance; a hostile in-field reader; unlanded
work / verbatim reuse / undisclosed constants). **All twelve refutations returned `survives =
false`.** The candidates are reproduced here so that the reasons are attached to them; none is
offered for paraphrase.

| id | sentence (verbatim from the pass) | fatal defects |
|---|---|---|
| **A — detector lead** | "The object this study builds is a detector for a symmetry-and-force lock in plane-wave DFT outputs, with its controls fixed and dated before any external corpus was opened, and it is read out over all 810 deposited outputs of a public rutile-oxide corpus, so the exposure it reports is a lower bound measured across a complete corpus rather than an estimate drawn from a sample." | States S1 and S2 as landed in the present indicative (C8; the core does not exist, the Xu census has not run). "Controls fixed before any external corpus was opened" is a negative-existence claim the repository contradicts (the 2026-08-15 sampling act, `docs/43:1811`). Fuses the header and force denominators (810 vs the force-block subset, `docs/43:1886, :1890`). "In plane-wave DFT outputs" claims a code class the controls have not certified (`docs/43:1958`). "Over all 810 deposited outputs" is lifted verbatim from round-2 (C9). Pre-commits to the HELD branch of P-XU before it is scored (`docs/43:1920`). |
| **B — floor lead** | "On one rutile slab with the geometry held fixed, the scaling-limited floor of the computed overpotential moves by 0.223 V as the Hubbard U is swept - measured non-blind on data already seen, and about twenty-five times the 9 meV by which that slab's own production point sat above its floor - under a parameter that no convergence criterion in the protocol constrains." | Leads with the registered *second* result (C7). 0.223 V is the four-point LIT-1 ladder value, superseded by A7.3's dense grid, which landed NOT MET at 3 of 6 — quoted bare without its verdict state. The 25× denominator (9 meV) is a withdrawn grid artefact (`docs/70:252-258`). Leans on the +0.40 eV *OOH constant whose provenance is still owed (C5). "No convergence criterion … constrains" is a negative-existence claim (`docs/75:95-96`). Re-lineates `docs/43:1928` rather than paraphrasing it. |
| **C — metal-dependence lead** | "With the relaxed geometry, the functional, the pseudopotential and every convergence setting held fixed, and at a single Hubbard U, swapping between the two Hubbard projectors that ship in the same plane-wave binary moves the computed overpotential on some rutile endmembers and not others - three of the five blind metals clear the pre-registered 0.10 V trigger, one falls between the bounds and is reported unrounded, one moves by 1.0 meV - so the per-metal table is the result and no class claim follows, and the measurement says how far the answer moves when a documented convention changes without saying which convention is right." | Entirely S4 compute — not scorable from S1 + S2 + S6 (C7, C8). **"The pseudopotential … held fixed" is false at roster level** (three PP families across the five, `docs/83:14-22`), and the k-mesh disclosure A12.R6 requires is absent. Quotes Ti's number alone, against `docs/83:159` ("no subset of the five without the other four"). By anonymising the firing metals into a count it makes Fe — 502.6 % constants, electronic part pointing the other way (`docs/83:91-93`) — indistinguishable from Ir (100 % electronic). Presents the atomic-projector-relaxed geometry as a neutral control (A13.5 item 2). Lifts "the per-metal table is the result and no class claim" nearly verbatim (C9). |
| **D — flagship mechanism lead** | "On this campaign's flagship material in a 1x1 cell and in that cell only, the projector switch changes which elementary step the model reports as potential-limiting - the sturdier half of the result, since flipping it back would need the ZPE/TS constants moved by at least 3.3 times their registered band - while the magnitude that travels with it, 0.487 V, is a 1x1 number of which 133.5 % is that fixed constants table against a raw electronic difference of -0.163 eV in the opposite direction, and which becomes 0.17 V, entirely electronic, in the adopted 2x1v cell, at one Hubbard U, on one material, with no statement about which projector is right." | The drafter submitted it as the proof that the joint constraint set is unsatisfiable in one sentence, and the refuters agreed: quoting 0.487 V owes four items (`docs/81:133-142`) — the split with its sign reversal, the ±0.15 V band and why the coefficient is 2, the flip margin, and that the constants were **not** recomputed per projector — and the sentence carries two. Its causal verb ("the projector switch changes which step…") over-reads a single-point comparison. Missing the "on some materials and not others" qualifier (`docs/83:37-39`). Leads with S4 work (C7). ~105 words; fails the graspability criterion (`docs/75:95-96`). |

**Two defects are common to all four and are the finding of this pass.**

1. **No claim sentence is writable today under the registered rules.** The registered lead (S1 +
   S2, `docs/43:1932`) has not landed, so any sentence that leads with it states unlanded work
   (C8); every sentence that leads with something else inverts the ordering (C7) and rests on S4
   compute the registration says the central claim must not depend on. This is T1 of §4, and the
   pass confirms there is no wording that escapes it. The exits are the two named there, and both
   are the entrant's.
2. **A process gate is unmet that no wording clears.** `docs/43:1932` (adoption note 2026-08-23)
   owes the entrant's dated line in `docs/45` §D saying whether the `docs/44:176-183` sentence is
   the claim sentence or only the narrative. `docs/45` §D (:46-66) contains no such line;
   `docs/75:382` already calls it overdue. Until it exists, no candidate — drafted or the entrant's
   own — has an antecedent.

**What the candidates get right, so it is not lost when the entrant writes his own:** none quotes an
absolute η for any metal (C1 clean in all four); C and D say the projectors "ship in" the binary,
never "default"; D scopes the flip to 1×1 and prints both cells together (C2, C3 clean); A uses the
permitted noun "lock" and says "lower bound" (`docs/43:1939, :1870`).

## 7. Defects in the record the pass surfaced, verified in the tree, and owed elsewhere

These are not about the sentence; they are things a reader of the readouts cannot recover and a
judge will ask.

| finding | verified | where it is owed |
|---|---|---|
| `docs/84` states **no Hubbard U anywhere** in its 132 lines; the 0.1725 V is a U = 7.15 number (A13.5 item 3, `docs/43:3730`) while the six-metal 3-of-5 is U = 7.50 (`docs/43:3345`). A reader of docs/84 alone cannot tell. | `grep -n "7.15\|Hubbard" docs/84…` → no match | a dated addendum to `docs/84`, or the cell/U pair on every statement of the two numbers |
| `docs/83` states **no cell** for the six-metal decks except in the A7.1 comparison row (:77); the decks are 1×1 (`runs/a0/main/<M>/<state>__u750.in`, `docs/43:3347`). | `grep -n "1×1\|2×1\|cell" docs/83…` → :77 only | same |
| `docs/75:85-90` is a **live draft** that quotes "from 1.155 V to 1.642 V" (absolute η, A7.5) and reads the flip as general (stale by `docs/43:4090-4094`); the 2026-09-04 staleness sweep classified docs/75 LIVE but indexed only line 171. | read | the staleness sweep's table, and docs/75 itself |
| `docs/76:222-223` — "It becomes a class claim about the METHOD … both must be written" — is contradicted by the readout one day later ("no class claim is made", `docs/83:33`; `docs/43:4031-4034`). docs/76 is dated before the readout; the readout governs. | read | a superseded-by line on docs/76 §5 |
| The FIRES 3-of-5 count leans on Fe, whose Δη is **502.6 % constants** with the electronic part pointing the other way (`docs/83:91-93`); docs/83 carries the caveat, and no sentence may quote Fe as evidence of a large electronic effect. | read | already in docs/83; carried here so the count is never quoted without it |
| The exposure-versus-consequence rule (`docs/43:1942`) forbids the in-house control and the external precision in one sentence and forbids multiplying a per-relaxation exposure rate into a per-metal consequence rate — which is precisely the rhetorical move round-1 (a) makes ("showed it is present … and measured what it costs"). | read | the entrant's Sep-20 sentence must split that into two sentences or drop the second half |

---

## Dated addendum — 2026-09-05 (session 3): three rows of §1, one tension and one candidate now carry a domain

Nothing above this line is edited. The dated correction at docs/84:162-219, same day, withdrew the sentence
that the two 2×1v legs "cannot differ" under the constants and replaced it with a measured domain: pair
(1,1) and a constant +0.1725164 V across the whole ±0.05 eV shared box; beyond it, out to ±0.30 eV,
Δη ∈ [0.1725, 0.1790] V with pairs (1,1), (1,2), (2,2) (docs/84:186-191). It ruled (docs/84:197-198) that
"exactly insensitive to the constants table" must carry either its shared-correction domain or its
fixed-active-step condition. Three places here quote that sentence bare:

- §1 row "composition of the 2×1v Δη" (:49): "entirely electronic, exactly insensitive to the ZPE/TS
  table" — read as exactly insensitive **within the ±0.05 eV shared box** (docs/84:193-195); the magnitude
  moves by at most 6.5 mV out to ±0.30 eV.
- T2 (:96): "0.17 V, purely electronic" — same domain.
- Candidate D (:123): "0.17 V, entirely electronic, in the adopted 2x1v cell" — same domain. Its
  refutation at :123 stands on its other grounds and is not reopened.

Two further rows gain their number. §1 row "P-PROJ-6 class verdict" (:51) and §7 row :155: under the same
±0.05 eV shared box the FIRES count reads 2 or 3 of 5 and the class verdict is MIDDLE BAND at every point,
while Mn's and Fe's individual bands are not constants-robust (docs/83 dated addendum 2026-09-05 (session
3); `docs/figs/pproj6_shared_box.json`). "FIRES 3 of 5" is quotable as the nominal count with that sentence
beside it. Ir's "100 % electronic" holds across the whole box, as a fixed-pair row.

No constraint C1–C11 changes; no candidate's verdict changes; the two exits of §4 remain the entrant's.

---

## Dated correction, 2026-09-06, to the addendum above

Nothing above this line is edited. Two slips in the addendum at :160-182: its heading says "three rows of §1"; the
rows it treats are two of §1 (:49, :51) and one of §7 (:155). And :162-163 puts "cannot differ" in quotation
marks as if docs/84 said it; docs/84:81 reads "two legs can be made to *differ*, and they cannot", and the
withdrawal at docs/84:181-182 reads "The assertion that the legs must move together throughout these boxes is
withdrawn." The substance is unchanged.
