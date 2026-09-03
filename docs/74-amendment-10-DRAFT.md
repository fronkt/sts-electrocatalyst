# 74 — AMENDMENT 10, DRAFT — the XC row: what σ_BEEF may be compared against, and on which metals

> # ⚠ NOT DEPOSITABLE AS IT STANDS — 9 BLOCKERS OPEN
>
> A five-lens adversarial pass on 2026-09-03 returned **9 BLOCKER, 25 MAJOR and 20 MINOR**
> findings against this draft. **Do not re-author, append or deposit any part of it until they
> are closed.** The premise survived — no BEEF production number exists anywhere, verified six
> ways including `git log --all -S` and a deleted-path sweep — so the window is intact and the
> thresholds are genuinely pre-data. What failed is the drafting.
>
> **Root cause of at least four of them: the wrong source block was used.** This draft was built
> from round-2's *Amendment 10* block (`:489-491`) alone. The operative S5 registration is
> **round-2 `:286-291`**, which was never read, and it already settles several things this draft
> calls UNKNOWN or gets wrong:
>
> | round-2 `:286-291` says | this draft says |
> |---|---|
> | S5 runs in **2×1v** (nat 36–38) | costed on the 1×1 probe (nat 18) — **§A10.4 is 2–10× low** |
> | **~1.5 h per SCF**, ~18 box-h + ~2 for gas refs | "within a factor of ~1.5 of the probe" |
> | a fresh-start BEEF SCF is **~3–7 h, a 3–5× under-count** | not mentioned — the draft walked into the warning |
> | all three metals are **U = 0**, "no BEEF+U ambiguity at all" | builds a Hubbard clause for a set that carries no U |
> | geometries are **fixed PBE+U `tier_v3`** | "UNKNOWN and the entrant's call" |
> | extension happens only if **BEEF+U converges cleanly AND the calendar allows** | A10-X states it differently |
>
> **The other five blockers:**
> 1. **σ_BEEF(η) is never defined** — every threshold is stated against an undefined estimator. No
>    CHE assembly, no dispersion statistic, no ZPE/TS handling, no script path. A 0.25 V bar on an
>    undefined quantity is exactly the failure class this campaign indicts.
> 2. **§A10.1 compares the wrong quantity.** `span(c_M)/2` is A7.3's scaling-floor descriptor, not
>    the U-sensitivity of η. The same-metal η swing is banked in `docs/figs/a0main_readout.json`:
>    **Ru 0.497 V, Ti 0.246 V, Ir 0.027 V.** So "all of it under 0.10 V" is **false**, and the
>    motivating hypothetical **inverts** — a σ of 0.15 V is *smaller* than the same-metal η swing on
>    2 of 3. The section's headline argument does not survive its own correction.
> 3. **A10-X weakens a registered threshold.** Round-2 fixes FALSIFIED at an absolute **≥2**;
>    A10-X moves it to ≥3. A11.R2 rule (ii) says the falsified bound stays the registered absolute
>    and only the confirmation bar may rise. The draft imports rule (i) and omits rule (ii) — the
>    one that cuts against it — and the effect is adverse-verdict-suppressing.
> 4. **A10-X also breaks the monotonicity A10-D claims to honour**: 3/4 = 0.750 at n = 4 falling to
>    2/3 = 0.667 if Cr drops out. (A10-D *alone* is monotone-safe and was verified so.)
> 5. **"The 0.291 V figure is retired" contradicts deposited text.** docs/43:1515 registers it as
>    **coverage-conditional**, and :1532-1537 registers that quoting *either* end alone is wrong.
>    A10-C.3 strikes one end — one of the two readings docs/43 names as wrong.
>
> Also: two of the six "differences" in the §A10.0 election table do not exist — round-1 `:120`
> already drops the σ(c_M) test and round-1 `:191`/`:85` already carry member-index matching — so
> the stated rationale for the election is weaker than written (the election still stands on
> docs/43:1930's pointer). And there is **no blindness disclosure**, **no both-outcomes table**
> (the registered "XC becomes a co-equal row" consequence is dropped), and **no P-DISPOSITION
> branch or submit-by date** for the one prediction sitting in the body figure.
>
> **What survived, verified:** every docs/43 and docs/45 pointer; the four-deck S0(a) gate table in
> all twelve cells; all six A7.3 span/2 values to 4 dp; the probe wall times to the second; the
> A10-M middle-band logic and the A10-D ladder taken alone; the Sep 18 date; and the finding that
> "gated on S0(a)" is stale. **A10-G, A10-M and A10-D are close to usable. A10-C, A10-X, A10.3 and
> A10.4 need rewriting from round-2 `:286-291`.**

**Status: DRAFT. NOT ADOPTED, NOT DEPOSITED. Nothing here is registered.** This file is
research infrastructure governed by A7.7 (docs/43 :1441-1447), whose operative requirement for a
document like this one is that **no sentence of any amendment is reproduced verbatim in the
report, essays or application answers — the entrant paraphrases.** **Every threshold below is
marked THRESHOLD and must be re-authored by Frank in his own words before this text is appended
to docs/43 and re-deposited.** A number proposed here is a proposal; it becomes a registration
only when he writes it. Where a fact needed for a registration does not exist in the repo, this draft says
UNKNOWN and names what resolves it.

**Deadline:** deposit by **Sep 18 2026** (docs/45 §D row A10 :55, and both lit-sweep syntheses'
own heading: *"before the first BEEF job"*). Today is 2026-09-03 — **15 days**, and no BEEF
production job has run, so the window is intact.

**Governs:** S5 — the BEEF-vdW σ row (docs/45 §E :81), and the disposition of **P-BEEF**, which
holds one of the six body-figure ledger rows (docs/43 :2183).

**Why it is being written now.** docs/73 §5 item 5 found that **P-BEEF holds a registered body
ledger row while AMENDMENT 10 exists nowhere as registered text.** Searched: all of `docs/`,
`tasks/`, `src/`, `tests/`, `README.md`, plus `git log --all --grep`. The only two hits are
`docs/research/2026-08-15-lit-sweep-round1-synthesis.md:189` and
`docs/research/2026-08-15-lit-sweep-round2-synthesis.md:489` — **planning documents that are in
no Zenodo deposit fileset** (the A11 fileset at docs/43 :2242-2244 is docs/43 + 59 + 61 + 62-67).
And the two give **different criteria**. A registered ledger row whose criterion lives only in an
undeposited working file, in two versions, is the defect this amendment closes.

---

## A10.0 — Three things this amendment must fix, and one it must record

### 1. The election between the two drafts is already made in deposited text — record it, do not re-choose

| | round-1 (`:189-192`) | round-2 (`:489-491`) |
|---|---|---|
| confirmation | σ_BEEF(η) < 0.25 V on **≥6 of 7 metals** | σ_BEEF(η) < 0.25 V on **≥2 of the 3 metals it is measured on (Ru, Ir, Ti)** |
| falsification | ≥ 0.30 V on **≥3 metals** | ≥ 0.30 V on **≥2** |
| σ(c_M) < 0.5 × mean-of-individual-σ | present | **DROPPED** as near-tautological |
| ledger label | — | **"XC only"** |
| gas references | in-box | in-box **and inside the ensemble** |
| ΔG assembly | — | **member-index-matched** |

**docs/43 :1930 — deposited — cites "round-2 :487-489" for A10's P-BEEF.** That pointer lands on
round-2's *Amendment 10* heading. So **round-2 governs and round-1's ≥6-of-7 is superseded**, and
this amendment's job is to say so in a dated line rather than to make a fresh choice after seeing
anything. Round-2 is also the later document, is narrower, and explicitly revises round-1 by
dropping one test.

> **THRESHOLD A10-E (election).** *Proposed:* the operative P-BEEF criterion is round-2's, and
> round-1's is struck as superseded, with docs/43 :1930's pointer cited as the reason of record.

### 2. The middle band is unmapped in BOTH drafts, and that is the defect this project has already been burned on twice

With a denominator of 3, round-2's two bands do not tile the outcome space:

- **confirmed** — ≥2 of 3 below 0.25 V
- **falsified** — ≥2 of 3 at or above 0.30 V
- **neither** — e.g. {0.20, 0.27, 0.28} (one below, none above), or {0.20, 0.27, 0.31}, or
  {0.26, 0.27, 0.28} (none below, none above)

The two bands are mutually exclusive at n = 3 (2 + 2 > 3), so there is no overlap — but there is a
real gap. **An unmapped middle band is exactly what A11.R2 and A7.7 exist to prevent**, and both
of those were adopted **2026-08-31**, sixteen days *after* these drafts were written, so neither
draft could have used the vocabulary.

> **THRESHOLD A10-M (middle band, mapped before the fact).** *Proposed:* any outcome meeting
> neither band maps to **SCORED — MIDDLE BAND / NOT MET** in the A11.R2 vocabulary (docs/43
> :2088-2095): reported with its count and its per-metal σ attached, **never quoted bare**,
> licensing **no** registered consequence, and **neither HELD, nor TRIGGERED, nor
> WITHDRAWN-UNSCORED**.

### 3. The denominator must be enumerated now, or P-BEEF inherits the trap that just killed two siblings

docs/73 §4 found P-SPIN-DELTA and P-FLOOR-U-SPIN both **unscoreable** — not for want of data, but
because a later dated line moved their denominators to values A11.R2's table does not enumerate,
and rule (iv) at docs/43 :2107 requires **"a new dated line BEFORE scoring"** for any denominator
not enumerated. P-BEEF is one non-convergence away from the same fate: BEEF-vdW is self-consistent
here, and this campaign has already seen 0-of-16 convergence on a spin-polarised Ru ladder
(A11.R6, 19,200 SCF iterations, closest approach 595× threshold).

> **THRESHOLD A10-D (denominator, enumerated in advance).** *Proposed:*
>
> | metals with a scoreable σ | confirmation | falsification | middle |
> |---|---|---|---|
> | **3** (registered) | ≥2 below 0.25 V | ≥2 at/above 0.30 V | otherwise |
> | **2** (one fails to converge) | **both** below 0.25 V | **both** at/above 0.30 V | otherwise |
> | **1** | **not scoreable** — reported as a single measured σ with its metal named, no verdict | | |
> | **0** | WITHDRAWN-UNSCORED with its date | | |
>
> The confirmation bar never falls under an exclusion (the guarantee A11.3 :2063-2064 makes for
> P-SPIN-DELTA and which that prediction then could not honour at n = 1). A metal is
> **non-scoreable** if its BEEF SCF prints "convergence NOT achieved", carries an
> `Error in routine` block, or emits no `BEEFens` line; the exclusion is reported with its reason,
> never silently.

### 4. Record the S0(a) gate: it PASSED, and "gated on S0(a)" is now a stale blocking clause

docs/43 :2022 says *"A10 (P-BEEF) remains gated on S0(a) and undrafted"* and docs/45 :33/:55/:81
repeat it. **The gate passed on 2026-08-22.** Re-measured from the four banked outputs on
2026-09-03 (`runs/s0/a_beef/`, bytes not grep):

| deck | switch under test | `BEEFens` lines | `Error in routine` | JOB DONE |
|---|---|---|---|---|
| `slab__beefens` | `calculation='scf'` + `ensemble_energies=.true.` | 0 | **1** (`read_namelists (1)`) | 0 |
| `slab__beefctl` | `calculation='scf'` + BEEF-vdW — **the control** | **0** | 0 | 1 |
| `slab__beefcalc` | `calculation='ensemble'` + BEEF-vdW | **1** (`BEEFens 2000 ensemble energies`) | 0 | 1 |
| `slab__beefhub` | `calculation='ensemble'` + BEEF-vdW + **HUBBARD card** | **1** (2000) | 0 | 1 |

The design is docs/43 :1384's registered four decks, and the fourth is the load-bearing one:
production is PBE+U, so the route had to survive the Hubbard card, and it does. The control
confirms the ensemble lines do not appear without the switch — the registered purpose was
*"striking the XC row on a null a grep cannot interpret"*, and that risk is retired.

**The conclusion is already in the deposited pre-registration** at docs/43 :1497-1498 — *"BEEF is
reachable only through `calculation='ensemble'`"* — inside A8.0 item 1. What is missing is only
the **result column of the A7.4 gate table** (docs/43 :1384 has none). So docs/52 :441's "no
doc-level verdict line for the probe exists" is half right: the finding is deposited, the table
row is blank.

> **THRESHOLD A10-G.** *Proposed:* record gate (a) as **PASSED — SELECT-WINNER = deck (ii)
> `calculation='ensemble'`**, with the four-deck table above as its evidence, and strike "gated on
> S0(a)" from docs/43 :2022 and docs/45 :33/:55/:81 by dated erratum. **No compute is owed for
> this**; repeating the clause as though compute were owed has cost eleven days of planning
> already (docs/73 §5 item 6).

---

## A10.1 — The finding that changes what P-BEEF may claim, and the only window in which it can be fixed

**This is the substantive content of the amendment. Read it before A10-E is signed.**

Round-2 registers the comparison in the same sentence as the threshold: σ_BEEF(η) < 0.25 V,
*"i.e. smaller than the 1.122 V U-swing and smaller than the 0.291 V Ir symmetry shift."*
**Both baselines are wrong for the metals σ_BEEF is measured on, and in the same direction.**

**Measured, 2026-09-03:**

- **P-BEEF's metal set {Ru, Ir, Ti} is exactly the nspin = 1 set** (`src/dft/a0spin_valence.py:10`)
  **and exactly the three metals UNDER the A7.3 floor.** From
  `tasks/review/a7_3_spin_census_2026-09-02_FINAL.json`, as-built `span_over_2_V`:

  | over the 0.100 V floor | | under it — **the P-BEEF set** | |
  |---|---|---|---|
  | Mn | 0.6307 V | Ru | 0.0922 V |
  | Fe | 0.6102 V | Ir | 0.0637 V |
  | Cr | 0.3435 V | Ti | 0.0438 V |

- **The 1.122 V U-swing is on Cr** (docs/43 :936, :955, :1187 — "the 1.122 V Cr swing", "the
  1.122 V η(Cr) swing"). **Cr is not in the σ_BEEF set.**
- **The 0.291 V Ir symmetry shift is the 1×1 number that block 1A RETIRED** under ADOPT_2X1V. It
  collapses to **−0.018 eV at 2×1v half-coverage**, and docs/45 :20 already carries both figures.

**So the registered sentence compares a σ measured on {Ru, Ir, Ti} against a U-swing measured on a
metal it is not measured on, and against a symmetry shift from a retired cell.** On the three
metals σ *is* measured on, the U-sensitivity is **0.044–0.092 V — all of it under 0.10 V**.

The consequence is not cosmetic. Suppose σ_BEEF comes back at 0.15 V on all three. Under the
registered sentence that is **P-BEEF CONFIRMED, "smaller than the 1.122 V U-swing"** — while on
those same metals XC error (0.15 V) would be **larger than the U-sensitivity (0.044–0.092 V) by a
factor of 1.6 to 3.4**. A true sentence and a badly misleading one. It is also the exact defect
docs/70 H-7 named for the campaign's headline ratio: *"Max-versus-typical inflates the ratio by
construction and is the first thing an adversarial reader will say."*

**Fixing this after the SCFs run is the move this whole project indicts.** Fixing it now, before
any BEEF production job exists, is ordinary pre-registration.

> **THRESHOLD A10-C (the comparison, registered before the data).** *Proposed:* P-BEEF's
> confirmation threshold stays **0.25 V** and its falsification band stays **0.30 V** — those are
> absolute and unaffected. What is registered alongside them:
>
> 1. **The primary comparison is same-metal.** For each metal M in the σ set, σ_BEEF(η, M) is
>    compared against **that metal's own** span(c_M)/2 from the A7.3 census (Ru 0.0922, Ir 0.0637,
>    Ti 0.0438 V). The report states, per metal, whether XC error is larger or smaller than
>    U-sensitivity **on that metal**.
> 2. **The cross-metal comparison is retained as context and may never be quoted bare.** Any
>    sentence putting σ_BEEF next to the 1.122 V figure must name that the 1.122 V is **Cr's** and
>    that Cr is outside the σ set.
> 3. **The 0.291 V Ir symmetry figure is struck from this comparison entirely.** It is a retired
>    1×1 number (−0.018 eV at 2×1v). If a symmetry baseline is wanted, it is the 2×1v value with
>    its cell named.
> 4. **Pre-stated, both directions:** if σ_BEEF exceeds the same-metal span/2 on ≥2 of 3, then
>    **on the non-magnetic metals XC is the larger error class**, and the report says so — the
>    "convergence-invisible classes dominate" framing is weakened there **and not defended**,
>    exactly as round-2 already requires for the absolute band.

---

## A10.2 — The scope limit, registered rather than discovered later

**σ_BEEF is measured on the three metals whose U-sensitivity is smallest and whose spin treatment
is nspin = 1. It therefore prices XC error precisely where the campaign's other error classes are
small, and says nothing about XC error on Cr, Mn or Fe — the three metals over the A7.3 floor,
which carry 0.34–0.63 V of U-sensitivity between them.**

This is not a flaw in the design (the three were chosen for cost and for convergence
tractability); it is a limit that must be on the record **before** a result exists, because the
sentence "XC error is smaller than the errors this campaign measures" would otherwise be read as
covering all six.

> **THRESHOLD A10-S.** *Proposed:* the S5 row is labelled **"XC only, non-magnetic three"** rather
> than round-2's "XC only", and the report may not generalise σ_BEEF beyond {Ru, Ir, Ti} without
> the extension arm below having run.

### The extension arm, pre-declared instead of left as "if clean"

docs/45 :81 already contemplates *"extension to +U metals if clean"*. "If clean" is not a
criterion. Since the extension is what would close A10.2's gap by **measurement** rather than by
disclosure, and since it is cheap (A10.4), it is worth specifying now.

> **THRESHOLD A10-X (extension arm).** *Proposed, entrant's election:* **Cr is added to the σ
> set**, making it {Ru, Ir, Ti, Cr} with denominator 4 (confirmation ≥3 of 4, falsification ≥3 of
> 4, denominators 4/3/2 enumerated as in A10-D). Cr is the choice rather than Mn or Fe because it
> is the metal that carries the 1.122 V swing the comparison sentence invokes, so adding it makes
> the headline comparison **same-metal on the metal that matters**.
>
> **Stated against it, honestly:** Cr's BEEF SCF is nspin = 2 and this campaign has a measured
> history of spin-polarised non-convergence (A11.R6: 0 of 16 at U = 9, 19,200 iterations). If Cr
> fails, A10-D's denominator ladder absorbs it and the result is the registered 3-metal statement
> — no rescue, no re-registration. **The election must be made before any BEEF job runs**, because
> adding a metal after seeing three σ values is selection.

---

## A10.3 — The S5 protocol, carried over from round-2 and made executable

All six protocol clauses of round-2 :491 are adopted verbatim in content:

1. **Self-consistent BEEF-vdW first** — not a post-hoc functional evaluation on a PBE+U density.
2. **Gas references in-box and inside the ensemble** — H₂O and H₂ in the Martyna-Tuckerman box,
   themselves run under `calculation='ensemble'` so they carry their own 2000 members.
3. **Member-index-matched ΔG** — ensemble member *i* of a slab or adsorbate state is combined
   **only** with member *i* of the gas references. Mixing indices would manufacture σ.
4. **σ belongs to BEEF-vdW, not to PBE+U.**
5. **E_U is outside the ensemble entirely** — the Hubbard energy is applied (deck (iv) proves the
   card survives the ensemble route) but is not varied by it.
6. **The row is labelled "XC only"** — amended to **"XC only, non-magnetic three"** per A10-S.

**Geometries.** UNKNOWN and the entrant's call: σ_BEEF may be evaluated at the **PBE+U-relaxed**
geometries already banked (cheap, and consistent with "E_U outside the ensemble"), or at
BEEF-relaxed geometries (a different and much more expensive quantity). *Proposed:* PBE+U
geometries, single-point BEEF-vdW, stated as the approximation it is — the same convention P15
uses for U held fixed per metal across a metal's four rungs.

**Deck count.** 4 states × 3 metals = **12** BEEF SCFs, + **2** in-box gas references = **14**
(or 18 with the A10-X Cr arm). Each must emit a `BEEFens` line or be excluded per A10-D.

---

## A10.4 — What it costs, measured rather than estimated

The S0(a) probe is **size-representative of production**, which is the fact that makes this cheap:

- probe: 18-atom 1×1 Ru slab, 32 k points, `calculation='ensemble'` + BEEF-vdW →
  **25m20s WALL** (`slab__beefcalc`); with the HUBBARD card, **25m56s WALL** (`slab__beefhub`);
  the plain-SCF control was **35m31s**.
- production A0-main cells, read this session: slab **nat = 18, nk = 32**; `s0_OH`/`s0_O`
  **nat = 20**; `s0_OOH` **nat = 21**, and the adsorbate states run **nk = 15** on Ru and Ir
  (32 on Ti).

So a production BEEF SCF is within a factor of ~1.5 of the probe. At docs/43 :1662's measured
**6.6–7.5 SU per step, flat from 40 to 128 ranks**, and the probe's ~0.43 h at NP = 20
(`runs/s0/m_s0_beefhub.txt`) ≈ **9 SU**:

| arm | decks | SU (order of magnitude) |
|---|---|---|
| S5 base, {Ru, Ir, Ti} × 4 states | 12 | **~110–180** |
| gas references, in-box, in-ensemble | 2 | **~10–40** |
| A10-X Cr extension | 4 | **~50–90** |
| **total with extension** | **18** | **~170–310** |

**Against a balance of 59,761.1 SU with an empty queue, S5 is ~0.3–0.5 % of remaining compute.**
Compute is not the constraint on A10 and never was; the constraint was that nobody had written it.

> **Stated as a bound, not a promise:** these are extrapolations from one 18-atom probe. If a
> production BEEF SCF turns out to cost 5× the probe, the arm is still under 1,600 SU. There is no
> budget scenario in which S5 is unaffordable.

---

## A10.5 — What this amendment does NOT license

- It does **not** license a BEEF-relaxed geometry arm, a BEEF phonon, or any XC arm beyond the σ
  measurement above.
- It does **not** license quoting σ_BEEF against the 1.122 V figure without Cr's name attached
  (A10-C.2), nor against the 0.291 V figure at all (A10-C.3).
- It does **not** license generalising σ_BEEF to Cr, Mn or Fe unless A10-X ran (A10-S).
- It does **not** resolve the **body-ledger displacement**. P-BEEF is one of the registered six
  (docs/43 :2183); docs/43 :1930's THRESHOLD leaves the displacement decision — which registered
  prediction moves to the appendix, or whether P-XU stays there — **the entrant's, in writing
  before Sep 20**. That is a separate dated line from this amendment.
- It does **not** touch P15, whose readout (`src/dft/p15_readout.py`) emits BULK GO / SLAB NO-GO
  and whose own dated line is also owed.

---

## A10.6 — Deposit obligation

Every amendment goes to Zenodo **before the first act it governs** (docs/45 :58-61; docs/43 A7.8
:1449-1464). The act A10 governs is the first BEEF production job, and **none has run** — verified
by `find runs -iname '*beef*'`, which returns only the four S0(a) probe decks and their manifest.
So the ordering is intact and A10 can be deposited clean.

**Required order:**

1. Frank re-authors A10-E, A10-M, A10-D, A10-G, A10-C, A10-S, A10-X and the geometry election in
   his own words, in a dated line.
2. The text is appended to docs/43 as **AMENDMENT 10** and re-deposited to Zenodo; the DOI and the
   commit hash are recorded beside it.
3. **Only then** are the 14 (or 18) BEEF decks built and submitted.
4. The stale "gated on S0(a)" clauses are struck by dated erratum (A10-G).

**Deposit fileset:** docs/43 plus whatever docs/45 rows change under A10-G. This draft (docs/74)
is not part of the fileset — it is the historical draft, on the docs/50 pattern.

---

## A10.7 — Open items this draft does not decide

| # | item | who |
|---|---|---|
| 1 | The A10-E election (round-2 governs) — recorded, not re-chosen | entrant |
| 2 | A10-X: is Cr added to the σ set? **Must be decided before any BEEF job runs** | entrant |
| 3 | Geometry election: PBE+U-relaxed single-point vs BEEF-relaxed | entrant |
| 4 | The body-ledger displacement, before Sep 20 (docs/43 :1930) | entrant |
| 5 | Whether the A7.4 gate table gains a result column or the erratum stands alone | entrant |
| 6 | Christensen's functional-independence claim: round-1 says test it **across materials**, round-2 says "tested across materials **or not claimed**". With 3 metals the across-materials test is n = 3. *Proposed:* **not claimed**, and say so | entrant |
