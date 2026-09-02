# 63 — The owed S0(h) AFM re-anchors: built, held by the deposited registration, and the 33–64 meV class re-projected onto the quantity A7.3 actually scores — 2026-08-30

**Provenance:** AI-drafted disclosed infrastructure. Every energy below is read from a
committed `.out` under `runs/s0/h_afm_anchor/` (the banked gate-(h) SCFs, commit
`946c3aa`, 4/4 ADOPT_AFM) or from the NM parent energies tabulated in that directory's
own README. **Zero new compute was run for this document.** Registration: docs/43
AMENDMENT 8 §A8.5 (docs/43:1638-1645, deposited, Zenodo 10.5281/zenodo.21963144);
docs/43 A7.4 row (h) (:1391); docs/41 P11 (:402-422). New code: `src/dft/build_h_afm_relax.py`,
`tests/test_build_h_afm_relax.py`, `tests/test_probe_decks_afm.py`, and a parser fix in
`src/dft/probe_decks.py`.

**Status: the four relaxation decks are BUILT and are NOT LAUNCHED.** The launch
manifest is withheld by the builder itself, mechanically, because the deposited
registration holds the family. See §2 — that HOLD is not mine to lift.

---

**One-paragraph summary.** The owed compute is four 2×1v AFM relaxations. They cannot
launch: docs/43:1645, an ADOPTION NOTE inside the deposited text, leaves it open whether
they are four standalone S3-class jobs or the Ru second seed inside tier_v3's crossed
magnetic-basin factor — up to sixteen relaxations, a 4× difference in deck count and
SU — and states in terms that **no default was drafted**. So this session built
everything that is not downstream of that decision: the committed builder that docs/51
recorded as missing, the four decks (identical under both readings), the GATE-1 path,
the `probe_decks.py` fix without which no AFM deck parses at all, and 20 tests. Then,
with zero compute, it asked what the banked gate-(h) data already says about A7.3 — and
found that the **33–64 meV NM-vs-AFM class quoted in docs/45, docs/60 and docs/61 is an
adsorption-energy class, while A7.3 scores c_M. Projected onto c_M the same data gives
−25.9 meV**, because the largest component of the AFM effect sits on the clean slab and
cancels. docs/60's conclusion survives — 25.9 meV still exceeds Ru's 15.5 meV — but the
sentence that carries it was comparing two different kinds of quantity, and one
**PROPOSED** threshold in docs/61 is anchored to the wrong one.

## 1. What is owed

docs/43:1638-1644, verbatim from the deposited amendment:

> **A consequence worth registering explicitly.** Gate (h) returned 4/4 ADOPT_AFM on the
> RuO2 anchors (−144, −80, −85, −111 meV against NM, against a −20 meV rule), and the
> adsorption energies move 33–64 meV once the anchor is AFM. Those four AFM points are
> single points on NM-relaxed geometries — P11 limit (ii), a lower bound. Adopting AFM as
> the anchor's magnetic row therefore owes **four 2×1v AFM relaxations**, which are
> S3-class jobs and are priced in A8.6, not in S0's closed budget.

## 2. Why they are not launched, and why that is not a scheduling call

The very next line of the deposited text, docs/43:1645:

> [ADOPTION NOTE 2026-08-23: **still open** — this paragraph and the A8.1 magnetic-basin
> row collide (docs/52 row 26; docs/51 skeptic addition iii): whether these four are the
> Ru second seed inside tier_v3's crossed magnetic-basin factor (then crossed with cell
> and symmetry, **up to 16 relaxations**) or four standalone S3-class jobs, and what the
> A8.1 row's "wherever triage allows" resolves to. **No default was drafted, so the
> blanket adoption decides nothing here; the resolution is the entrant's to write in a
> dated line. Until he does, the gate-(h) AFM relaxations remain HOLD** (0 built —
> docs/51) and the S3 deck count this amendment fixes is fixed only up to this family.]

Three things follow. The HOLD is **in the deposited registration**, not in a working
note. It has **no default**, so there is nothing to fall back on. And the two readings
differ by **4× in deck count and SU**, so choosing one is choosing a budget as well as a
protocol. A8 itself *was* adopted 2026-08-23 ("they pass with me"); docs/51's older
"HOLD on A8 / undeposited" line is stale and is superseded here — the amendment is
registered, and it is this family, specifically, that the amendment left open.

**The HOLD is now enforced by code rather than by memory.** `build_h_afm_relax.py`
writes the decks unconditionally — they cost no SU and, being the 2×1v/off arm, they are
common to *both* readings — and refuses to write the manifest the submit script consumes
until a dated line appears in docs/43 whose machine-readable head is exactly one of:

    [AFM-SCOPE RESOLVED YYYY-MM-DD: STANDALONE_FOUR]
    [AFM-SCOPE RESOLVED YYYY-MM-DD: SECOND_SEED_CROSSED]

The entrant's own sentence goes on the same line; only the bracketed head is parsed.
`test_build_h_afm_relax.py` exercises the gate in both directions, including four
near-miss lines (wrong scope token, undated, unbracketed, prose alone) that must **not**
lift it.

## 3. What was built, and the two defects that had made "nothing to launch" true

docs/51:25 gave the concrete reason the family had zero decks: *"no decks, manifest or
committed builder exist (the gate-(h) SCF builder lives only in a scratchpad;
`build_cellsym_pilot.py` hardcodes Ru nspin = 1; `probe_decks.py` cannot parse the
Ru1/Ru2 species)."* All three are addressed.

**(a) The builder is committed.** `src/dft/build_h_afm_relax.py`, 13 fatal build-time
assertions in the `build_a0spin.py` idiom. The transformation is deliberately trivial and
therefore auditable: the banked SCF parents already carry `&IONS ion_dynamics='bfgs'`,
`tprnfor`, `forc_conv_thr = 2.0d-3` and `nstep = 200`, so each relaxation is its parent
with **exactly two lines changed** — `calculation` and `prefix` — and assertion A10 pins
the diff to exactly those two rather than trusting the claim. Verified on all four.

**(b) `probe_decks.py` could not see a single atom of an AFM deck.** `_ELEMENT_RE =
^[A-Z][a-z]?$` was applied to every `ATOMIC_POSITIONS` line. The registered AFM idiom
splits the metal into two species *labels* `Ru1`/`Ru2` — identical mass, identical
pseudopotential, opposite `starting_magnetization` — and neither label is an element
symbol. Every position line was skipped and the deck parsed to **zero atoms, silently**:
no exception, no warning, an empty structure. Fixed by keying off the labels the deck
*declares* in its own `ATOMIC_SPECIES` block, with a widened pattern kept only as the
fallback for `.out` parsing where no such block is at hand — the same read-it-from-the-deck
rule as `build_a0spin.py` assertion A1. The four decks now parse at nat = 36/37/38/39,
matching each deck's own `nat`.

**(c) The species-index trap is present in this family too, and the banked parents got it
right.** `ref`/`s0_O` are `ntyp = 3` `[Ru1, Ru2, O]` → sublattices at indices **1, 2**;
`s0_OH`/`s0_OOH` are `ntyp = 4` `[H, Ru1, Ru2, O]` → sublattices at **2, 3**, because H
sorts first. A per-deck constant would have seeded H or O. All four banked gate-(h) decks
were checked and are correct, so the 4/4 ADOPT_AFM result stands; assertions A3/A4
re-derive the pair from each deck's own block rather than trusting that check, and refuse
if the pair is not unique.

`build_cellsym_pilot.py`'s hardcoded `nspin = 1` is untouched and unused here — this
builder does not call it.

## 4. The zero-compute result: what the banked data already says about A7.3

The four banked AFM single points, against the NM parents tabulated in
`runs/s0/h_afm_anchor/README.md`:

| state | E_AFM (Ry) | E_NM (Ry) | ΔE (meV) | totmag | absmag |
|---|---|---|---|---|---|
| `ref` (clean slab) | −3261.34603391 | −3261.33545254 | **−144.0** | −2.09 | 6.19 |
| `s0_O` | −3302.93769258 | −3302.93178971 | −80.3 | −1.62 | 4.49 |
| `s0_OH` | −3304.20342621 | −3304.19715356 | −85.3 | −1.21 | 3.85 |
| `s0_OOH` | −3345.68881990 | −3345.68064313 | −111.3 | −0.24 | 4.79 |

All four clear the registered −20 meV ADOPT_AFM rule. As a check that these are the same
numbers the campaign banked, the four CHE step shifts they imply are **+58.7 / +5.0 /
−31.0 / −32.7 meV**, reproducing commit `946c3aa`'s recorded "+58.6/+5.0/−30.9/−32.7"
to 0.1 meV.

**Now project them onto A7.3's own quantity.** A7.3 scores `span(c_M)/2` with
`c_M = ΔG_OOH − ΔG_OH`. The clean slab and every gas reference cancel identically in c_M
(`referencing.py` `_REF_COEFFS`), so

>  Δc_M = ΔE(\*OOH) − ΔE(\*OH) = −111.3 − (−85.3) = **−25.9 meV**

| quantity | value | what it is |
|---|---|---|
| NM-vs-AFM class as quoted in docs/45, docs/60 §6, docs/61 §A11.0/§A11.3 | 33–64 meV | move in **adsorption energies** |
| the same data projected onto c_M | **25.9 meV** | move in **A7.3's own quantity** |
| Ru's distance to the A7.3 floor | 15.5 meV | required **swing in Δc_M across the U band** |

**Why the class shrinks.** The largest single component of the AFM effect is on the
**clean slab** (−144.0 meV), and the clean slab is exactly what c_M cancels. Commit
`946c3aa` already noticed the shape of this — "NM anchor error concentrates in \*→\*OH" —
and that step, ΔG₁ = G(\*OH) − G(\*), is the one c_M does not contain. This is the same
cancellation A0-SPIN Stage 0 measured on the FM side, where Ru's individual state energies
moved up to 174 meV while c_M moved 7.1 meV (docs/62 §2).

### 4.1 What survives, and what has to be restated

**docs/60's conclusion survives.** 25.9 meV still exceeds Ru's 15.5 meV, so "A7.3 NOT MET
is not settled while S0(h) is owed" holds — and now holds on the right quantity, which
makes it a better sentence, not a weaker one.

**But the comparison as written in docs/60 §6 fact 2 compares two different kinds of
number, and that must not travel.** It reads Ru as "short by 15.5 meV of |Δc_M| — …
2–4× smaller than the NM-vs-AFM class". The 15.5 meV is a required *swing in Δc_M across
U = 0 → 9*; the 33–64 meV is a *level shift at a single U* (gate (h) ran at U = 0 only).
By the A11.1 arithmetic that governs this whole family — `Δ[span/2] = −D_M/2` with
`D_M = Δc_M(U_max) − Δc_M(0)` — **a U-independent offset cancels exactly, at any size.**
So neither 33–64 meV nor 25.9 meV bounds A7.3's error: both are levels, and A7.3 scores a
difference of two levels. The honest statement is that the AFM treatment moves c_M by
25.9 meV at U = 0 and that **its U-dependence has never been measured**.

### 4.2 A consequence for a live PROPOSED threshold — docs/61 decision item 3

docs/61 §A11.3 sets P-SPIN-DELTA's **PROPOSED** movement threshold at
`|D_M| ≥ 0.033 eV`, justified as "the *bottom* of gate (h)'s measured 33–64 meV class, so
it is anchored to a prior measurement rather than invented." The anchoring is the right
instinct, but 33 meV is the bottom of the **adsorption-energy** class, while D_M is a
**c_M** quantity. Re-anchored to the same data through c_M the figure is **25.9 meV**,
and it is a level rather than the U-swing D_M actually measures. Recommendation, the
entrant's to accept or reject: re-anchor the threshold to 0.026 eV and state in the
amendment that it is a level-derived proxy for a swing, or drop the gate-(h) anchoring and
choose the number on other grounds. Either way it should not stay at 0.033 eV citing a
justification that points at a different quantity.

### 4.3 And a limit on what the owed compute can settle

The four relaxations discharge P11 limit (ii) — they replace single points on NM-relaxed
geometries with genuinely AFM-relaxed ones — and they firm up the anchor's magnetic row,
which is what A8.5 owes them for. **They do not bound A7.3's error**, and no version of
this family does, because they are all at U = 0 and in the 2×1v cell while A7.3's rows are
the 1×1 A0 grid across U ∈ [0, 9]. The deck set that would act on A7.3 is docs/61 decision
item 10's Ru AFM probe, and even that needs **both** U endpoints to produce a D_M. Nothing
here should be sequenced on the belief that finishing the owed compute closes the A7.3
question.

## 5. Cost, against the balance

Anvil `che260157`: **70,851.6 of 100,000 SU remaining** (29,148.3 used), measured
2026-08-30. docs/51 prices these at ~237 SU/relax "likely 2–4×" for genuine multi-step
nspin = 2 BFGS (the banked AFM single points carry residual forces 0.012–0.023 Ry/bohr
against `forc_conv_thr` 2e-3, so these are real relaxations, not near-converged nudges).

| reading | relaxations | family incl. GATE-1 children | rough SU | share of balance |
|---|---|---|---|---|
| STANDALONE_FOUR | 4 | ≥ 8 decks | ~4,000–7,600 | 6–11 % |
| SECOND_SEED_CROSSED | up to 16 | ≥ 32 decks | ~16,000–30,000 | 23–42 % |

Both fit. The second does not fit comfortably alongside A0-SPIN Stage 1, the S0(h)-adjacent
Ru AFM probe, and whatever S3 still owes, so the scope decision is a schedule decision as
well as a protocol one, six weeks from the Oct 15 freeze.

## 6. What the report may and may not say

- **MAY:** gate (h)'s AFM effect on RuO₂, projected onto the quantity A7.3 scores, is
  **−25.9 meV at U = 0** in the 2×1v cell, on NM-relaxed geometries and therefore a lower
  bound (P11 limit (ii)); it exceeds Ru's 15.5 meV distance to the floor, so A7.3's NOT MET
  is not settled; the AFM effect is dominated by the clean slab (−144.0 meV), which c_M
  cancels; the four owed relaxations are built, assertion-checked, and held by the
  registration's own open scope.
- **MAY NOT:** quote 33–64 meV as an error bar on A7.3 (wrong quantity) or 25.9 meV as one
  (right quantity, wrong kind — a level, not the U-swing A7.3 scores); claim the AFM
  treatment moves A7.3 in any direction, since its U-dependence is unmeasured; treat
  −25.9 meV as a converged or geometry-relaxed number; present the gate-(h) family as
  capable of settling A7.3; report any of this as though the relaxations had run.

## 7. Open items

**Frank's, and item 1 is the only thing between here and launch:**

1. **The AFM scope line** — `STANDALONE_FOUR` or `SECOND_SEED_CROSSED`, dated, in docs/43,
   per docs/43:1645. The builder is watching for it and will emit the manifest the moment
   it lands. This is a 4× budget decision as well as a protocol one (§5).
2. **docs/61 decision item 3** — P-SPIN-DELTA's threshold is anchored to the wrong
   quantity (§4.2). Re-anchor to 0.026 eV, or re-justify.
3. **docs/60 §6 fact 2's sentence** — restate so the level-vs-swing distinction travels
   with it (§4.1). The conclusion does not change.
4. Whether the Ru AFM probe (docs/61 item 10) is sequenced with this family, given that
   both act on Ru and only the probe can act on A7.3 (§4.3).

**Mine, unblocked:** the GATE-1 `__g1` children build from each relaxation's converged
final geometry and are a single command once the relaxations land (`--gate1`, which
refuses today and says why).

> **UPDATED 2026-09-02 → docs/68 §2.** The probe's U = 9 AFM legs (2×1v off-plane, NM-relaxed
> and AFM-relaxed geometries alike) hit `electron_maxstep = 200` without converging, as did
> every FM-seeded Ru row at U = 9 (0 of 15). The U-dependence §6 calls "unmeasured" is
> therefore **unmeasurable under the registered numerics**: the −25.9 meV level at U = 0
> stands, its U = 9 partner does not exist, and the family can neither move nor settle A7.3.
> The NM legs at U = 9 converged and agree across the two geometries to 0.1 / 0.8 meV.
