# 86 — P-DIVANIS: the rulings owed before the arithmetic runs

**Status: recommendations only. Nothing here is a ruling, and no floor margin is computed in
this file.** P-DIVANIS is registered at `docs/43-prereg-week1-factorial.md:1898` with a **Sep 15**
date on one limb. Every quotation below was re-verified verbatim against the deposited text on
2026-09-04; no line number above the deposit line had drifted.

The arithmetic is genuinely free — the corpus is `docs/research/2026-08-15-sampling/divanis_esi.txt`,
already on disk, already read, and `:1963` settles that reading a published table **is not
parsing**. What is not settled is **who may compute the scored number**, and six smaller things
that decide what the number means. They are cheap to answer now and impossible to answer cleanly
once the count is visible.

---

## RULING 1 — who computes it. This one gates all the others.

**`docs/43:1910` (A9.3.7):** *"Deliverable: the census tables plus the paired
site-symmetry/input-set result and the coded literature table, **all census numbers computed from
raw outputs the entrant parsed himself, and all literature codes entered by him** (round-2 :237)."*

Its cited source, `docs/research/2026-08-15-lit-sweep-round2-synthesis.md:237`, reads *"three
census tables plus the paired site-symmetry/input-set result, all computed from raw outputs the
entrant parsed himself"* — **and the Divanis product is one of those three.**

Two readings, and the text supports both:

- **Narrow.** "raw outputs" means QE/OC20 outputs. The Divanis ESI is a published table, not a raw
  output, so the clause does not reach it and a tool may compute the rate.
- **Broad.** The clause governs the *census numbers*, all three products, whatever their input.
  Divanis is Census product 3. Round-2 :237 applies it to all three by name.

**Recommendation: rule it BROAD, and let a tool do everything except the scored number.** The
narrow reading wins on a literalism about "raw outputs" while the sentence's evident subject is
the census. And note the one other place the registration names an actor for this specific
arithmetic — the denominator clause at `:1898` — says *"**the entrant** counts it from
`divanis_esi.txt`."* That governed a pre-deposit act which lapsed, but it is the only place the
question is answered explicitly, and it answers it the same way.

The cost of ruling broad is small and the cost of ruling narrow is not symmetric: a
tool-computed headline in a project whose thesis is that undisclosed methodological choices
change published conclusions is a sentence a referee gets to write for you.

> `[P-DIVANIS AUTHORSHIP 2026-09-__: BROAD | NARROW]` — the scored floor-margin rate is computed
> by ____; the extraction, the row-selection audit and the δ-curve plotting are tool work, logged
> in the provenance record.

---

## RULING 2 — which 38 rows. The count is fixed; the *rule* is written nowhere.

`:1898` fixes the population at **38 bare rutile MO₂ rows from 3 articles (Man 26, Mom 11,
Frydendal 1)**. The number is registered. The *selection rule that reproduces it* is not in any
document. A rule that reproduces 26/11/1 exactly has been derived and independently re-derived,
but until it is written down the population is a magic number.

Two disclosures belong in the same line, because neither is in the source:

- The trailing `b` on `PtO2b` / `PbO2b` / `SnO2b` / `NiO2b` **has no legend anywhere in the ESI.**
- Man 2011's two blocks repeat the same materials with **no in-file coverage label**; the
  "high-coverage" attribution comes from round-2 :413, not from the source.

> `[P-DIVANIS ROW RULE 2026-09-__]` — the 38 rutile-only rows are those satisfying ____;
> reproduces Man 26 / Mom 11 / Frydendal 1. The `b` suffix is unlegended in the source and the
> coverage attribution is external to it; both are reported on the figure face.

---

## RULING 3 — the unnamed verdict band. Same defect A7.3 already cost the campaign.

The prediction is **≥25 % HELD, <10 % FALSIFIED**. On a denominator of 38 that is **≥10 rows
HELD** and **≤3 rows FALSIFIED**.

**Counts of 4 through 9 — 10.5 % to 23.7 % — have no word.** `:1930`'s vocabulary is
HELD / TRIGGERED / WITHDRAWN and none of them fits. This is precisely the hole A7.3 fell into,
and A12.R3 was written specifically because *"the cost of that is still being paid."* Pre-state
the resolution now, while the count is unknown.

> `[P-DIVANIS MIDDLE BAND 2026-09-__]` — a count of 4–9 of 38 is reported as ____, with the
> per-article breakdown as the result and no class claim.

---

## RULING 4 — δ. The register already used a value; the Sep 15 limb may already be discharged.

`:1898` says the floor margin is reported as a curve over **δ = corr_OOH − 0.35 eV, δ ∈ [0.00,
0.10]**, with the registered shift **Δ(floor margin) = +δ/2 (pls 3), −3δ/2 (pls 4), −δ/2
(pls ∈ {1,2})**, and: *"If δ is not resolved from Nørskov 2004 by **Sep 15**, only the δ-curve is
reported and no single-δ number is quoted."*

**The registered CrO₂ guard reproduces only at δ = 0.05.** Measured: η = 1.9600 / ΔG₄ = −0.4600 /
ΔG_OOH = 5.3800 at δ = 0.05, against 1.9100 / −0.4100 / 5.3300 at δ = 0.00 and 2.0100 / −0.5100 /
5.4300 at δ = 0.10. The register's own guard sentence therefore already commits to δ = 0.05.

That is worth naming for two reasons. It **pins the rung convention** harder than any derivative
test. And it sits against `:1898`'s own statement that *"the '+0.40 eV \*OOH correction' is
ABSENT"* from Table SI-1, plus the 2026-09-04 addendum at `:3980-3987` recording that the +0.40 eV
constant **has no primary source in this repository**. The δ question and that open provenance
debt are the same question wearing two hats.

**Recommendation: test δ-invariance of the verdict first — it is free.** If the count is the same
at δ = 0.00, 0.05 and 0.10, the Sep 15 limb is moot and the verdict is robust. If it is not, the
registered fallback yields a curve and **no verdict**, and the product goes WITHDRAWN-UNSCORED at
the sweep despite complete arithmetic. Better to know that now than on Nov 5.

> `[P-DIVANIS δ 2026-09-__]` — the verdict is / is not invariant over δ ∈ [0.00, 0.10]; the
> in-document anchor δ = 0.05 is / is not adopted, on the ground that the registered CrO₂ guard
> reconstructs only at that value.

---

## RULING 5 — "per-paper rate (n = 24)" is arithmetically impossible here

`:1898` asks for the *"per-paper rate (n = 24)"* alongside. But the 38 rutile-only rows span
**3 articles**, not 24. The n = 24 is the article count of the **whole 515-row corpus**, carried
into a clause about a 38-row subpopulation.

**Recommendation: report n = 3 and name the discrepancy.** It does not move the scored rate.
Silently reporting "n = 24" would be a number that cannot be reconstructed from the population.

> `[P-DIVANIS PER-PAPER n 2026-09-__]` — the per-paper rate is reported at **n = 3** (Man, Mom,
> Frydendal); the registered "n = 24" is the whole-corpus article count and is corrected here.

---

## RULING 6 — the unphysical set is larger than the one registered row

`:1898` registers one guard: Man 2011's high-coverage CrO₂ row, ΔG_OOH = 5.38 > 4.92, ΔG₄ =
−0.46 eV, unphysical under the imposed 4.92 — *"never quoted without that note."*

**It is not the only one.** `divanis_esi.txt:299` (article 7, PbO₂) carries ΔG_OOH = 5.22 > 4.92
on a raw column read. So the ΔG₄ < 0 flag must be **a computed population over all 38**, not a
lookup of the single named row.

This has a second-order consequence worth stating before the numbers exist: **every additional
unphysical row is a material-specific overpotential**, and `:1959` / `:1939` forbid quoting an
absolute η for any single material, external corpora included, in the nouns *lock* or
*constraint* only — never *trap*, *bug*, *error* or *pathology*.

> `[P-DIVANIS UNPHYSICAL SET 2026-09-__]` — the ΔG₄ < 0 population is computed over all 38 rows
> and reported as a count; individual rows beyond the registered CrO₂ guard are named only where
> `:1939`'s vocabulary permits.

---

## RULING 7 — the registered guard sentence will trip your own S7 parser

The one material-specific η that `:1898` **requires** to be quoted is the CrO₂ guard: η = 1.96 V.

`docs/43:1399-1401` (A7.5): *"The report may therefore never quote an absolute η for **Cr**, Fe,
Co or Ni as a materials claim; they appear only inside paired within-metal differences.
**Enforced by the pre-submission script (S7).**"*

Cr is in the named set. A registered obligation to quote a Cr overpotential meets a registered
pre-submission script configured to reject exactly that. **Whichever way this is ruled, it must be
ruled before S7 is written**, or S7 gets an undocumented exception at freeze — which is the shape
of the defect this campaign exists to indict.

> `[P-DIVANIS × A7.5 2026-09-__]` — the CrO₂ guard η is an **external-corpus reconstruction, not
> an in-house materials claim**, and is exempt from the S7 assertion / is rewritten as ____. The
> exemption is written into S7 as a named, dated carve-out, never as a silent pass.

---

## Corrections carried into this sheet rather than left in a draft

Recorded because each was in a working draft of this arm and each would otherwise have reached a
dated addendum on a deposited pre-registration:

- **`:1960` is not the anti-selection authority.** It is about the OC20 sample and per-corpus
  noise floors. The correct citation for completing a registration in a dated line before the arm
  runs is **`:1902` (A9.3.5)**.
- **The deposit target is `10.5281/zenodo.22304889`** (the record through A13), not 22072991
  (A1–A9).
- **Measurement corrections to the corpus description:** data rows end at `divanis_esi.txt:644`,
  not :663 (:663 is a page marker); unmatched lines are **60**, not 46; Table SI-1 spans **:70-81**
  (nine rows, four carrying a ΔZPE−TΔS value at :73-76), not :70-78; SI-1 uses **comma decimals**
  while SI-2 uses periods; SI-2 is whitespace-separated with an 8-line split header, not a
  fixed-column table. None of these moves a registered figure — 515 / 24 / 122 / 75 and
  38 = {Man 26, Mom 11, Frydendal 1} all reproduce exactly — but every one of them would have gone
  into a dated line as fact.
- **F8's five materials are PbO₂ / OsO₂ / SnO₂ / GeO₂ / PtO₂** (`:1945`). **NiO₂ is not among
  them**, and OsO₂ and GeO₂ appear in no row of the 38 — so the F8-touched rows inside this
  population are **PbO₂ / SnO₂ / PtO₂ only**.

---

## What is free and worth doing regardless of Ruling 1

Pseudo-replication is the referee's target here: **Man 2011 is 26 of 38 = 68 %** of the
population — far more clustered than the 24 % that already got the pooled |z| gate withdrawn as a
correction of record. `:1898`'s registered mitigation is denominator composition **on the figure
face**. Make sure it is literally on the face, not in a caption.

And do not resurrect the |z| ≥ 3 gate against the pooled 3.18 ± 0.12 eV: `:1898` withdrew it as a
correction of record and the z column is retained as reported only.
