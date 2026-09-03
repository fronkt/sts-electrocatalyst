# 74 — AMENDMENT 10, DRAFT v2 — the XC row: what σ_BEEF is, what it may be compared against, and on which metals

**Status: DRAFT v2. NOT ADOPTED, NOT DEPOSITED. Nothing here is registered.** Research
infrastructure governed by A7.7 (docs/43 :1441-1447), whose operative requirement for a document
like this one is that **no sentence of any amendment is reproduced verbatim in the report, essays
or application answers — the entrant paraphrases.** **Every threshold below is marked THRESHOLD
and must be re-authored by Frank in his own words before this text is appended to docs/43 and
re-deposited.** A number proposed here is a proposal; it becomes a registration only when he
writes it. Where a fact needed for a registration does not exist in the repo, this draft says
UNKNOWN and names what resolves it.

**Deadline:** deposit by **Sep 18 2026** (docs/45 §D row A10 :55; both lit-sweep syntheses head
the amendment *"before the first BEEF job"*). Today is 2026-09-03 — **15 days**.

**Governs:** S5 — the BEEF-vdW σ row (docs/45 §E :81; the stage spec is round-2 :286-291), and
the disposition of **P-BEEF**, which holds one of the six body-figure ledger rows (docs/43 :2183).

---

## A10.-1 — What v1 of this draft got wrong, recorded rather than quietly replaced

v1 (commit `cfb5711`) drew **9 BLOCKER / 25 MAJOR / 20 MINOR** findings from a five-lens
adversarial pass. It is superseded, and its failures are listed here because three of them were
the exact error class this campaign exists to indict, committed inside the document meant to
register against it.

| # | v1 error | corrected in v2 |
|---|---|---|
| 1 | Built from round-2's *Amendment 10* block (`:489-491`) alone; **never read round-2 `:286-291`**, which is the operative S5 stage spec | §A10.4 and §A10.5 are now derived from `:286-291` |
| 2 | **σ_BEEF(η) was never defined** — every threshold sat on an undefined estimator | new **A10-σ** (§A10.1) writes it out longhand |
| 3 | Compared `span(c_M)/2`, which is A7.3's **scaling-floor descriptor**, not the U-sensitivity of η. Consequently "all of it under 0.10 V" was **false** and the motivating example **inverted** | §A10.2 uses the banked same-metal η swings, both conventions |
| 4 | Cost model built on the **1×1** probe (nat 18) when S5 runs **2×1v** (nat 36–38); ~2–10× low, and it walked into round-2 `:291`'s own "3–5× under-count" warning | §A10.5 re-derived, range widened, warning quoted |
| 5 | Registered a Hubbard clause for a set that carries **no U** — round-2 `:289`: Ru, Ir, Ti are "all three nspin = 1 and **U = 0**, so there is no BEEF+U ambiguity at all" | §A10.4 scopes deck (iv) to the extension arm only |
| 6 | Called geometry "UNKNOWN" when `:289` specifies **fixed PBE+U `tier_v3`** | §A10.4 adopts it |
| 7 | **A10-X moved the falsification bound** from the registered absolute ≥2 to ≥3 — adverse-verdict-suppressing, and forbidden by A11.R2 rule (ii), which v1 omitted while citing rule (i) | falsification is now **absolute ≥2 at every denominator** |
| 8 | A10-X **broke the monotonicity A10-D claimed to honour** (0.750 → 0.667 on a drop-out) | two separate ladders, fixed by the election **before** any job runs; both verified monotone |
| 9 | Called the 0.291 V figure **"retired"**, contradicting docs/43 `:1515`, which registers it as **coverage-conditional** | §A10.2 uses the registered **pair**, never one end |
| 10 | Two of six "differences" in the election table did not exist — round-1 `:120` already drops the σ(c_M) test, and `:191`/`:85` already carry member-index matching | table corrected; the election now rests only on docs/43 `:1930` |

**What v1 got right and v2 keeps:** every docs/43 and docs/45 pointer; the four-deck S0(a) gate
table in all twelve cells; the A7.3 span/2 values; the probe wall times; the middle-band mapping;
the denominator ladder taken alone; and the finding that "gated on S0(a)" is stale.

---

## A10.0 — Why this amendment is being written now

docs/73 §5 item 5 found that **P-BEEF holds a registered body ledger row while AMENDMENT 10 exists
nowhere as registered text.** Searched: all of `docs/`, `tasks/`, `src/`, `tests/`, `README.md`,
plus `git log --all --grep`. The only hits are `docs/research/2026-08-15-lit-sweep-round1-synthesis.md:189`
and `...round2-synthesis.md:489` — planning documents in **no Zenodo deposit fileset** (the A11
fileset at docs/43 :2242-2244 is docs/43 + 59 + 61 + 62-67). A registered ledger row whose
criterion lives only in undeposited working files, in two versions, is the defect this closes.

### 1. The election: round-2 governs, and the deposited text already says so

| | round-1 (`:189-192`) | round-2 (`:489-491` + the stage spec `:286-291`) |
|---|---|---|
| confirmation | σ_BEEF(η) < 0.25 V on **≥6 of 7 metals** | < 0.25 V on **≥2 of the 3 metals it is measured on** (Ru, Ir, Ti) |
| falsification | ≥ 0.30 V on **≥3 metals** | ≥ 0.30 V on **≥2** |
| σ(c_M) < 0.5 × mean-of-individual-σ | **already dropped** at round-1 `:120`, as near-tautological | drop restated at `:491` |
| member-index-matched ΔG | **already present** at round-1 `:191` and `:85` | restated at `:491` |
| ledger label | — | **"XC only"** |
| gas references | in-box | in-box **and inside the ensemble** |
| cell / geometry / U | not stated | **2×1v**, fixed PBE+U `tier_v3`, **U = 0 on all three** (`:286-291`) |

**docs/43 `:1930` — deposited — cites "round-2 :487-489" for A10's P-BEEF**, landing on round-2's
Amendment 10 heading. So **round-2 governs and round-1's ≥6-of-7 is superseded.** Note the last
two rows are the real differences; the σ(c_M) and member-index rows are *not* differences, and v1
wrongly counted them as such.

> **THRESHOLD A10-E.** *Proposed:* the operative P-BEEF criterion is round-2's — its Amendment 10
> block **and** its S5 stage spec at `:286-291` together — and round-1's is struck as superseded,
> with docs/43 `:1930`'s pointer as the reason of record.

### 2. The middle band, unmapped in both sources

At n = 3 the two bands do not tile the outcome space: **confirmed** is ≥2 below 0.25 V,
**falsified** is ≥2 at or above 0.30 V, and outcomes such as {0.20, 0.27, 0.28} (one below, none
above), {0.20, 0.27, 0.31} and {0.26, 0.27, 0.28} are in neither. They cannot both fire (2 + 2 > 3).
A11.R2 and A7.7 were adopted **2026-08-31**, sixteen days after both sources were written, so
neither could have used the vocabulary.

> **THRESHOLD A10-M.** *Proposed:* any outcome in neither band maps to **SCORED — MIDDLE BAND /
> NOT MET** in the A11.R2 vocabulary (docs/43 :2088-2095): reported with its count and its
> per-metal σ attached, **never quoted bare**, licensing **no** registered consequence, and
> **neither HELD, nor TRIGGERED, nor WITHDRAWN-UNSCORED**.

### 3. The denominator, enumerated in advance — two ladders, and the election picks one

docs/73 §4 found P-SPIN-DELTA and P-FLOOR-U-SPIN both unscoreable because a later dated line moved
their denominators to values A11.R2's table does not enumerate, and rule (iv) at docs/43 `:2107`
requires *"a new dated line BEFORE scoring"*. P-BEEF is one non-convergence from the same fate.

**A11.R2 rule (ii) is binding and v1 broke it:** the FALSIFIED bound **stays the registered
absolute**; only the confirmation bar may rise. So falsification is **≥2 at every denominator**.

> **THRESHOLD A10-D.** *Proposed:* which ladder applies is fixed by the A10-X election below,
> **before any BEEF job runs**, and never afterwards.
>
> **Ladder B — base set {Ru, Ir, Ti}, n = 3 registered**
>
> | scoreable σ | confirmation | falsification | else |
> |---|---|---|---|
> | 3 | ≥2 below 0.25 V (0.667) | ≥2 at/above 0.30 V | MIDDLE BAND |
> | 2 | **both** below 0.25 V (1.000) | ≥2 at/above 0.30 V | MIDDLE BAND |
> | 1 | **not scoreable** — the single σ is reported with its metal named, no verdict | | |
> | 0 | WITHDRAWN-UNSCORED with its date | | |
>
> **Ladder X — extended set {Ru, Ir, Ti, Cr}, n = 4 registered** (applies only if A10-X is elected)
>
> | scoreable σ | confirmation | falsification | else |
> |---|---|---|---|
> | 4 | ≥3 below 0.25 V (0.750) | ≥2 at/above 0.30 V | MIDDLE BAND |
> | 3 | **≥3 of 3** below 0.25 V (1.000) | ≥2 at/above 0.30 V | MIDDLE BAND |
> | 2 | **both** below 0.25 V (1.000) | ≥2 at/above 0.30 V | MIDDLE BAND |
> | 1 / 0 | as Ladder B | | |
>
> **Verified before proposing:** in every rung of both ladders the two bands are mutually exclusive
> (0 outcomes satisfy both), a middle band exists (39 / 19 / 7 / 13 outcomes over an L/M/H lattice),
> and **the confirmation fraction never falls** as a metal drops out — Ladder B 0.667 → 1.000,
> Ladder X 0.750 → 1.000 → 1.000. That is the guarantee docs/43 `:2063-2064` makes and which
> P-SPIN-DELTA could not honour at n = 1.
>
> A metal is **non-scoreable** if its BEEF SCF prints "convergence NOT achieved", carries an
> `Error in routine` block, or emits no `BEEFens` line. Every exclusion is reported with its reason.
>
> **Disclosure, per A11.R2 rule (v):** these tables were written with the A7.3 census, the A11.R6
> convergence history and the S0(a) probe result **already known**, and with **no σ_BEEF in
> existence**. No row in either table can flip P-BEEF between CONFIRMED and FALSIFIED — the bands
> are absolute in σ and only the counting rule varies.

### 4. Gate (a) PASSED: "gated on S0(a)" is a stale blocking clause

docs/43 `:2022` says *"A10 (P-BEEF) remains gated on S0(a) and undrafted"*; docs/45 `:33`/`:55`/`:81`
repeat it. Re-measured from the four banked outputs 2026-09-03 (`runs/s0/a_beef/`, bytes not grep):

| deck | switch under test | `BEEFens` | `Error in routine` | JOB DONE |
|---|---|---|---|---|
| `slab__beefens` | `calculation='scf'` + `ensemble_energies=.true.` | 0 | **1** (`read_namelists (1)`) | 0 |
| `slab__beefctl` | `calculation='scf'` + BEEF-vdW — **the control** | **0** | 0 | 1 |
| `slab__beefcalc` | `calculation='ensemble'` + BEEF-vdW | **1** (`BEEFens 2000 ensemble energies`) | 0 | 1 |
| `slab__beefhub` | `calculation='ensemble'` + BEEF-vdW + **HUBBARD card** | **1** (2000) | 0 | 1 |

The design is docs/43 `:1384`'s registered four decks; the control retires the registered kill
("*striking the XC row on a null a grep cannot interpret*"). **The conclusion is already deposited**
at docs/43 `:1497-1498` — *"BEEF is reachable only through `calculation='ensemble'`"* — inside
A8.0. Only the **result column of the A7.4 gate table** is missing (`:1384` has none).

> **THRESHOLD A10-G.** *Proposed:* record gate (a) as **PASSED — SELECT-WINNER = deck (ii)
> `calculation='ensemble'`**, with the table above as evidence, and strike "gated on S0(a)" from
> docs/43 `:2022` and docs/45 `:33`/`:55`/`:81` by dated erratum. **No compute is owed.**

---

## A10.1 — What σ_BEEF(η) IS. Registered before any member is read

v1's worst defect: every threshold was stated against a quantity the draft never defined. A 0.25 V
bar on an undefined estimator is a number an analyst can hit or miss by choosing a definition after
the members are in hand — the exact failure class this campaign indicts.

> **THRESHOLD A10-σ.** *Proposed, written longhand:*
>
> 1. **Per member.** For ensemble member *i* ∈ {1 … N}, take the total energy of that member from
>    each of the four states (slab, `s0_O`, `s0_OH`, `s0_OOH`) of metal M and from **each of the two
>    gas references**, all at index *i* and no other index.
> 2. **ΔG per member.** Assemble ΔG₁…ΔG₄ from member *i* by the campaign's existing CHE ladder —
>    the same `hea_oer.referencing.delta_G` path production uses — with the **member-independent**
>    ZPE and TS corrections added **identically to every member**. Corrections are not ensembled;
>    only the XC total energies are.
> 3. **η per member.** η_i = max(ΔG₁,ᵢ … ΔG₄,ᵢ) / e − 1.23 V, i.e. the same
>    `hea_oer.descriptors.oer_overpotential` definition every other row in this campaign uses. The
>    potential-limiting step **may differ between members**; that is a result, not an error, and the
>    per-member pls histogram is reported alongside σ.
> 4. **σ.** σ_BEEF(η, M) = the **sample standard deviation** of {η_i} over the N members, in volts.
>    Not a percentile, not a half-width, not BEEF's internal scaled estimate. N is reported per
>    metal and must equal the emitted member count.
> 5. **If N differs between the states of one metal**, that metal is **non-scoreable** under A10-D —
>    index matching is impossible and a truncation would silently manufacture σ.
> 6. **Emitted by one script**, `src/dft/p_beef_readout.py`, on the pattern every other scored row
>    in this repo uses (`a0main_`, `a0cell_`, `lit2_`, `pproj_`, `s3_`) — and, as `p15_readout.py`
>    does, it **parses its thresholds out of docs/43 rather than copying them**, and refuses to score
>    if it cannot find them.
>
> **Stated as a limit, not hidden:** σ so defined is the spread of η under the BEEF-vdW ensemble at
> **fixed geometry**. It does not include the geometry's own XC dependence. That is a real and
> separate error term, it is **not measured here**, and the report says so.

---

## A10.2 — What σ_BEEF may be compared against. The v1 comparison was the wrong quantity

Round-2 `:491` registers the threshold and its motivation in one sentence: σ_BEEF(η) < 0.25 V,
*"i.e. smaller than the 1.122 V U-swing and smaller than the 0.291 V Ir symmetry shift."* **Both
baselines are wrong for the metals σ_BEEF is measured on, and v1 replaced them with a third wrong
one.**

**Measured, 2026-09-03:**

- **The σ set {Ru, Ir, Ti} is exactly the nspin = 1 set** (`src/dft/a0spin_valence.py:10`) **and
  exactly the three metals UNDER the A7.3 floor** (`span(c_M)/2`: Ti 0.0438, Ir 0.0637, Ru 0.0922 V,
  floor 0.100). The three **over** it are Cr 0.3435, Fe 0.6102, Mn 0.6307 V.
- **The 1.122 V swing is Cr's** (docs/43 `:936`, `:955`, `:1187`). **Cr is not in the σ set.**
- **v1's replacement was also wrong.** `span(c_M)/2` is A7.3's **scaling-floor descriptor**
  (docs/43 `:1368`), not the U-sensitivity of η. The U-sensitivity **of η** is separately banked in
  `docs/figs/a0main_readout.json`:

  | metal | \|η(U=9) − η(U=0)\| — fixed endpoints | max − min over the grid | n_U |
  |---|---|---|---|
  | **Ru** | **0.4968 V** | 0.4968 V | 8 |
  | **Ti** | **0.2459 V** | 0.2459 V | 7 |
  | **Ir** | **0.0266 V** | **0.1979 V** | 8 |
  | *(Cr, for the cross-metal note)* | *0.1058 V* | *1.1774 V* | *19* |

  So v1's "all of it under 0.10 V" is **false on η** — Ru 0.497 and Ti 0.246 are both over — and
  v1's example inverted: a σ of 0.15 V would be *smaller* than the same-metal η swing on 2 of 3.

- **Ir is non-monotone**: 0.0266 V at fixed endpoints against 0.1979 V max−min, a **7.4×**
  difference. A comparison that does not name its convention is meaningless on Ir.
- **The 0.291 V symmetry figure is not "retired" — it is registered as a PAIR.** docs/43 `:1515`
  (deposited): the trap is *"**coverage-conditional**: 0.291 V on Ir at 1×1, −0.018 eV at 2×1v half
  coverage. **A single-coverage symmetry measurement would have reported either number as the
  effect.**"* And `:1546-1549` registers the claim scope as *"a coverage-conditional effect, the
  range stated per metal"*. v1 struck one end — precisely what `:1515` names as the error.

> **THRESHOLD A10-C.** *Proposed:*
>
> 1. **The bands are untouched:** confirmation < 0.25 V, falsification ≥ 0.30 V, both absolute.
> 2. **The primary comparison is same-metal, on η, at fixed endpoints U = 0 → U = 9** — A7.3's own
>    convention (docs/43 `:1368`) — quoting **Ru 0.497, Ti 0.246, Ir 0.027 V**. The max−min column
>    is reported **beside** it for every metal, and **Ir's 7.4× gap between the two conventions is
>    stated explicitly** wherever Ir is quoted.
> 3. **The cross-metal 1.122 V figure may be used as context and never bare:** any sentence putting
>    σ_BEEF next to it must name that it is **Cr's** and that **Cr is outside the σ set** unless
>    A10-X ran.
> 4. **The symmetry baseline, if used at all, is the registered pair with both coverages attached**
>    (docs/43 `:1515`) — **never either end alone**.
> 5. **Both directions pre-stated.** If σ_BEEF exceeds the same-metal fixed-endpoint η swing on ≥2
>    of the scoreable metals, then **on the non-magnetic metals XC is the larger error class**, and
>    the report says so — the "convergence-invisible classes dominate" framing is weakened there
>    **and not defended**. If it is smaller on ≥2, the report says that, with the scope limit of
>    §A10.3 attached and without generalising to Cr, Mn or Fe.

---

## A10.3 — Scope limit, and the extension arm

**σ_BEEF is measured on the three metals whose U-sensitivity is smallest by the A7.3 descriptor and
whose spin treatment is nspin = 1.** It prices XC error where the campaign's other error classes
are small and says nothing about XC error on Cr, Mn or Fe — the three over the A7.3 floor, carrying
0.34–0.63 V of descriptor sensitivity between them.

> **THRESHOLD A10-S.** *Proposed:* the S5 row is labelled **"XC only, non-magnetic three"** rather
> than round-2's "XC only", and σ_BEEF may not be generalised beyond the scoreable set without the
> extension arm having run.

> **THRESHOLD A10-X (extension arm — entrant's election, before any BEEF job runs).** *Proposed:*
> **Cr is added, giving {Ru, Ir, Ti, Cr} and Ladder X.** Cr rather than Mn or Fe because Cr is the
> metal whose swing the registered motivation sentence invokes, so adding it makes the headline
> comparison same-metal on the metal that matters.
>
> **Recorded against it, in both directions:**
> - Cr's BEEF SCF is **nspin = 2 and carries U ≠ 0**, so it is the only arm where BEEF+U ambiguity
>   exists at all, and deck (iv) is the evidence that the route survives a Hubbard card.
> - This campaign has measured spin-polarised non-convergence: A11.R6 returned **0 of 16** at U = 9
>   over 19,200 SCF iterations. If Cr fails, Ladder X's n = 3 rung absorbs it at a **stricter**
>   bar (≥3 of 3) — no rescue, no re-registration.
> - **Cr is the strictest available choice, not the most favourable.** Its `span(c_M)/2` is 0.3435 V
>   against Mn 0.6307 and Fe 0.6102, so substituting Mn or Fe would make a "σ is smaller"
>   conclusion **easier**. Stated because the opposite would be the natural suspicion.
> - Round-2 `:291` conditions the extension on BEEF+U converging cleanly **and the calendar
>   allowing**; A10-X converts that into the Ladder X / non-scoreable machinery above rather than
>   leaving "if clean" as a criterion.

---

## A10.4 — The S5 protocol, from round-2 `:286-291`

Adopted in content:

1. **Cell: 2×1v** (`:287`). nat ≈ 36–38, against the S0(a) probe's 18.
2. **Geometries: fixed PBE+U `tier_v3`** (`:289`) — single-point BEEF-vdW, no BEEF relaxation.
3. **U: zero on all three base metals.** `:289` — Ru, Ir and Ti are *"all three nspin = 1 and
   U = 0, so there is no BEEF+U ambiguity at all."* **So deck (iv)'s HUBBARD-card evidence is
   load-bearing only for the A10-X Cr arm**, and clause 6 below applies only there. v1 registered
   it for the base set, which carries no U.
4. **Self-consistent BEEF-vdW first**, not a post-hoc functional evaluation on a PBE+U density.
   Note `startingpot` is forbidden by the repo's `_FORBIDDEN` guard, so these are **fresh starts** —
   which is what `:291` prices.
5. **Gas references in-box and inside the ensemble** — H₂O and H₂ in the Martyna-Tuckerman box,
   themselves under `calculation='ensemble'`, carrying their own members. One H₂ and one H₂O are
   reused across metals (identical md5 per species), so index matching across metals is well defined.
6. **E_U, where it exists (A10-X only), is outside the ensemble** — held at the production value,
   applied identically to every member, never varied by it.
7. **σ belongs to BEEF-vdW, not to PBE+U.**
8. **Deck count:** 4 states × 3 metals = **12**, + **2** gas references = **14**; with A10-X, **18**.

---

## A10.5 — Cost, re-derived from the governing text rather than from the probe

**v1 priced this on the 1×1 probe and was 2–10× low.** Round-2 `:287-291` prices the stage itself
and warns about exactly the mistake v1 made:

- `:287` — *"~14 jobs, ~20 box-hours, **2x1v**."*
- `:289` — *"12 self-consistent BEEF-vdW SCFs at fixed PBE+U `tier_v3` geometries at **~1.5 h** ≈
  18 box-h, plus 2 gas references ≈ 2 box-h. The ~2000-member ensemble is free post-processing."*
- `:291` — *"a **fresh-start** BEEF-vdW SCF with nonlocal correlation and no `startingpot`
  (forbidden by the repo's `_FORBIDDEN` guard) is **~3–7 h — a 3–5× under-count**."*

Anchors, measured: the probe is **0.43 h at NP = 20 ≈ 8.6 SU** on an 18-atom 1×1 cell
(`runs/s0/m_s0_beefhub.txt` records `NP=20`; wall 25m56s). Production is 2×1v at nat 36–38, roughly
double the atoms. Anvil bills `max(cores, ⌈mem_GB/2⌉)` per hour, which for these shapes is
cores × hours, and docs/43 `:1662` measures SU per step **flat from 40 to 128 ranks**, so SU is
rank-independent and wall-clock is a scheduling choice, not a cost one.

| arm | decks | per deck | SU |
|---|---|---|---|
| S5 base, {Ru, Ir, Ti} × 4 states | 12 | ~1.5 h (`:289`) → ~3–7 h fresh-start (`:291`) | **~360 – 1,700** |
| gas references, in-box, in-ensemble | 2 | small molecules in a box | **~10 – 40** |
| A10-X Cr extension (nspin = 2, ~1.4× per-deck) | 4 | | **~170 – 800** |
| **total with extension** | **18** | | **~540 – 2,540** |

**Against 59,761.1 SU with an empty queue that is ~0.9 – 4.3 % of remaining compute.** The
conclusion v1 reached survives its own correction: **compute is not the constraint on A10, and
never was.** But the honest range is **4–10× v1's**, and it is quoted as a range because the
fresh-start band is a factor of ~2.3 wide in the governing text itself.

**Stated as a bound:** if a production BEEF SCF costs 2× the top of `:291`'s band, the full arm is
still ≈ 5,000 SU, under 9 % of balance. There is no scenario in which S5 is unaffordable — only
scenarios in which it is slow, which is what §A10.8's submit-by date is for.

---

## A10.6 — Both outcomes stated before the first SCF

v1 omitted this and dropped a registered consequence with it. A9 has a dedicated section (A9.4)
written because an earlier round wrongly assumed A8 already carried one.

| outcome | claim scope, registered in advance |
|---|---|
| **CONFIRMED** (Ladder B/X confirmation met) | The report may say XC error on the scoreable metals is below 0.25 V and, per A10-C.2, compare it same-metal on η. It may **not** generalise beyond the scoreable set (A10-S), and it does **not** license "XC is negligible" — only "XC is under 0.25 V on these metals, at fixed geometry." |
| **FALSIFIED** (≥2 metals at/above 0.30 V) | **XC becomes a co-equal error row** — the registered consequence, carried from round-1 `:190` and round-2 `:491`, which v1 dropped. docs/45 §B row 8 moves from NOT MEASURED to a measured class with its size, and the "convergence-invisible classes dominate" framing is **weakened in the report, not defended**. |
| **MIDDLE BAND** | A10-M: reported with count and per-metal σ, never bare, licensing no consequence, neither HELD nor TRIGGERED nor WITHDRAWN-UNSCORED. |
| **fewer than 2 scoreable** | Ladder B/X: not scoreable, or WITHDRAWN-UNSCORED at n = 0, with the exclusions and their reasons. |
| **standing regardless of outcome** | S5 delivers, on any result: a measured σ_BEEF(η) per scoreable metal with N stated; the per-member pls histogram; and the first XC row this campaign has of any kind. docs/45 §B row 8 stops reading "not yet measured here" either way. |

---

## A10.7 — Blindness, disclosed rather than assumed

**"No production job has run" is not the same claim as "nothing about the BEEF spread is known,"**
and it is the second that makes A10-σ's and A10-C's choices legitimate. A9.0 item 3 set the
precedent by disclosing pre-registration sampling in full and marking one item *"blind by record,
not by availability."*

**What exists.** Two complete 2000-member ensembles are banked and have been since 2026-08-21:
`runs/s0/a_beef/slab__beefcalc.out` and `slab__beefhub.out`. Parsed this session (the values are
in E-notation; a naive `\d+\.\d+` regex silently drops the exponent and understates the spread
~23×, which happened once before this table was right):

| file | N | mean | s.d. |
|---|---|---|---|
| `slab__beefcalc.out` | 2000 | −0.2895 Ry | **10.9296 Ry = 148.71 eV** |
| `slab__beefhub.out` | 2000 | −0.2896 Ry | **10.9369 Ry = 148.80 eV** |

**Why this is not a latent σ_BEEF(η).** Both are ensembles of **absolute total energy for a bare
1×1 Ru slab**. σ_BEEF(η) requires four states plus index-matched gas references, and the
cancellation between them is the whole point; a bare-slab spread is ~600× the 0.25 V threshold and
bears no relation to it. **No ΔG, no η and no σ on η has been formed from these**, and A10-σ's
estimator choice cannot have been informed by them.

**Blind by record.** Whether anyone inspected the member distribution of these two files before
this amendment was drafted is **not recorded**. On the A9.0 precedent that makes the per-state
spread *blind by record, not by availability* — it is one command away for any reader.

---

## A10.8 — The P-DISPOSITION branch, the kill criterion, and the submit-by date

v1 omitted the sweep for the one prediction sitting in the body figure. **The realistic failure
mode is not "0 metals converge" — it is "the 14–18 decks are never built."**

A7.7's P-DISPOSITION sweep (docs/43 `:1436-1440`, date amended at `:2249-2268`) is **self-executing
at the entrant's REPORT LOCK line, backstop Nov 5 2026 8:00 pm ET**, and marks any unscored
prediction **WITHDRAWN-UNSCORED with its date**. No REPORT LOCK line exists yet.

> **THRESHOLD A10-K.** *Proposed:*
> 1. **P-BEEF is subject to P-DISPOSITION by name.** If unscored when the sweep executes, it is
>    WITHDRAWN-UNSCORED with its date, and the body ledger carries that row as withdrawn.
> 2. **Submit-by date: the decks are built and submitted within 7 days of the A10 deposit, and in
>    no case later than Oct 10 2026.** Past that, S5 is **CUT** in a dated line and P-BEEF is
>    withdrawn deliberately rather than hoped for — docs/70 `:816-818` calls an owed-but-unwritten
>    row at lock the worst of the three outcomes, and this clause exists to prevent it.
> 3. **The deliberate-withdrawal option was considered and not taken.** docs/73 §9 item 4 put
>    "withdraw the body row deliberately" on the table as co-equal. It is not taken because the gate
>    has passed, the compute is ~1–4 % of balance, and S5 is the campaign's **only** XC row of any
>    kind — docs/45 §B row 8 currently reads "not yet measured here." If A10-K.2 fires, that
>    reasoning is superseded by the calendar and the row is withdrawn.

---

## A10.9 — What this amendment does NOT license

- No BEEF-relaxed geometry arm, no BEEF phonon, no XC arm beyond the σ measurement above. The
  geometry's own XC dependence is **not measured** (A10-σ limit).
- No quoting σ_BEEF against the 1.122 V figure without Cr's name attached (A10-C.3), and no quoting
  either end of the coverage-conditional symmetry pair alone (A10-C.4).
- No generalising σ_BEEF beyond the scoreable set unless A10-X ran (A10-S).
- **No resolution of the body-ledger displacement.** P-BEEF is one of the registered six (docs/43
  `:2183`); `:1930`'s THRESHOLD leaves the displacement — which registered prediction moves to the
  appendix, or whether P-XU stays there — **the entrant's, in writing before Sep 20**. Separate line.
- No change to P15, whose readout emits BULK GO / SLAB NO-GO and whose dated line is also owed.

---

## A10.10 — Deposit obligation

Every amendment goes to Zenodo **before the first act it governs** (docs/45 `:58-61`; docs/43 A7.8
`:1449-1464`). The act A10 governs is the first BEEF production job. **None has run** — verified
six ways: `find` over the tree, `grep -ril` for `BEEFens`/`ensemble_energies`/`σ_BEEF` over every
tracked type, directory inspection of `runs/ results/ data/ docs/figs/ anvil/`,
`git log --all --grep`, `git log --all -S`, and a `--diff-filter=D` sweep for any beef path ever
added then deleted (none). The ordering is intact.

**Required order:** (1) Frank re-authors A10-E, A10-M, A10-D, A10-G, A10-σ, A10-C, A10-S, A10-X and
A10-K in his own words, in a dated line; (2) the text is appended to docs/43 as **AMENDMENT 10** and
re-deposited, with the DOI and commit hash recorded beside it — **and it carries the 2026-09-03
terminology addendum at docs/43's bottom with it**; (3) only then are the 14 or 18 decks built;
(4) the stale "gated on S0(a)" clauses are struck by dated erratum (A10-G).

---

## A10.11 — Open items this draft does not decide

| # | item | who |
|---|---|---|
| 1 | A10-E: round-2 governs — recorded, not re-chosen | entrant |
| 2 | **A10-X: is Cr added? This selects Ladder B or Ladder X and must be decided before any BEEF job runs** | entrant |
| 3 | A10-C.2: fixed-endpoint η swing as the primary convention, with max−min beside it | entrant |
| 4 | A10-K.2's submit-by date (proposed: 7 days from deposit, hard stop Oct 10) | entrant |
| 5 | The body-ledger displacement, before Sep 20 (docs/43 `:1930`) | entrant |
| 6 | Whether the A7.4 gate table gains a result column or the A10-G erratum stands alone | entrant |
| 7 | Christensen's functional-independence claim: at n = 3 (or 4) an across-materials test is n = 3. *Proposed:* **not claimed**, and say so | entrant |
| 8 | Whether A10's deposit also re-deposits for the terminology change, or lets it ride | entrant |
