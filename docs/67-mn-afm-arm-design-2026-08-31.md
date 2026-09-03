# 67 — The Mn AFM arm: design of record — 2026-08-31

**Status:** design of record for the A7.5 Mn AFM condition, elected IN SCOPE by the
entrant's 2026-08-31 directive (docs/66 §2 row 14). AI-drafted disclosed
infrastructure; every threshold below is a REUSE of an already-registered number,
written down before any Mn AFM energy exists. **Licence:** the Mn-arm registered line
inside docs/43 Amendment 11 — necessary because docs/43:2008 (the gate-(h) AFM-scope
addendum) explicitly excludes "any AFM deck in 1×1" from the only prior AFM licence,
so even the minimal arm is new licensed compute. **Firewall:** no number from this
arm enters the banked A7.2/A7.3 scores; the arm exists to decide whether
materials-facing Mn sentences (η(Mn) as an absolute) may be used at all.

## 1. The registered condition this arm discharges

docs/43:1406-1407 (A7.5, registered): "β-MnO₂ is antiferromagnetic and
`gen_rutile.py` initialises it FM — either the AFM arm runs or every materials-facing
Mn sentence is struck." Current state: UNMET — "the Mn column is FM-initialised and
may not be used as a materials-facing absolute η" (docs/60:243-244). Mn "carries the
largest span in the numerator (0.6307 V)" (docs/61:260-261). The strike lifts ONLY by
the arm RUNNING — on any outcome (AFM adopted, multistable, or measured FM null); a
deferral would have accepted the struck-sentence consequence permanently.

## 2. What is banked for Mn (the FM reference frame)

- 1×1 rutile MnO₂ (110) slab decks under `runs/a0/main/Mn/`: slab, s0_O, s0_OH,
  s0_OOH across the A0 U grid; production row u390 (U Mn-3d = 3.9 eV); K_POINTS
  9 4 1; nspin = 2, FM-uniform `starting_magnetization` 0.5.
- 6 Mn per 1×1 cell, split 3+3 across the two rutile combs (corner comb x ≈ 0,
  body-centre comb x ≈ c/2); max comb x-deviation across the four u390 parents
  0.0064 Å (worst: s0_OH__u390.in; s0_OOH alone is 0.0029 Å; slab ≤ 4e-7 Å, s0_O
  ≤ 1.3e-5 Å) — so the sublattice assignment is geometrically clean in every parent.
- Species index is STATE-dependent (the docs/61 §A11.8 item-2 correction): Mn sits at
  index 2 in adsorbate decks (H < Mn < O ordering) and index 1 in slab/s0_O decks.
  Any builder MUST read the index from each deck's own ATOMIC_SPECIES.
- The FM comparator of record = the frozen banked u390 SCF energies (the .out
  energies at the banked geometries), NOT the relax-derived η chain — like-for-like
  at identical coordinates, mirroring gate-(h)'s frozen-comparator idiom.

## 3. The physics election, stated honestly

β-MnO₂'s measured magnetic ground state is an incommensurate screw/helical structure
(Yoshimori 1959; turn angle ≈ 129° per c along the [001] chains **[ERRATUM 2026-09-03: WRONG AS WRITTEN. Two independent sources give q = (0,0,≈2/7), a pitch of 7/2 c, i.e. ≈103° per c. See the §7 item 1 verification at the end of this document.]**; T_N ≈ 92 K; neutron
refinement Regulski et al. ~2003-2004). **These citations are from model knowledge and
are UNVERIFIED against any source in this repository — flagged per the campaign's
verify-AI-literature rule; the entrant verifies them before the report quotes them.**
No collinear pattern is "the" AFM state; every collinear DFT treatment is an
approximant. Candidates admitted by the rutile lattice:

- **P-A — rutile-sublattice AFM** (corner comb up, body-centre comb down; intra-chain
  FM): the MnF₂-type rutile AFM pattern and the gate-(h) Ru template; expressible in
  the 1×1 cell (3+3).
- **P-B — intra-chain AFM** along the [001] chains (the closest collinear approximant
  of the ~129°/c screw): needs the cell doubled along [001]; two phase variants
  (B1/B2) by inter-chain registry.

Which collinear pattern is "standard" in the β-MnO₂ DFT literature could not be
verified from the repo — that unverifiability is exactly why the ordering is
**MEASURED, not elected**: run FM, P-A, P-B1, P-B2 in one 2×1 frame and let the
energies decide.

## 4. Elections of record (docs/66 §2 row 14; dated 2026-08-31)

- **E1 ORDERING: MEASURED** — 2×1 slab set {FM, P-A, P-B1, P-B2}; lowest adopted
  under the E4 threshold.
- **E2 CELL:** stage 1 in 2×1 (doubled along [001]: x-length 5.752 Å = 2 × 2.876,
  12 Mn / 24 O) at K_POINTS 4 4 1; the banked 1×1 mesh 9 4 1 has odd n1, so no 2×1
  mesh folds onto it — any cross-cell ENERGY comparison claim requires the k-bridge
  family (1×1 @ 8 4 1 + 2×1 @ 4 4 1; docs/54:177 precedent). Stage 1 makes no
  cross-cell claim (FM and AFM candidates all sit in the same 2×1 frame), so the
  k-bridge is CONTINGENT, built only if such a claim is later wanted.
- **E3 GEOMETRY: FIXED-FIRST + RELAX FAMILY** — the core runs fixed-geometry SCFs at
  the banked FM-relaxed production geometries (byte-minimal diffs off banked decks,
  exactly comparable to the FM references at identical coordinates; the registered
  lower-bound limitation stated), then the relax family (4 relax + 4 fresh-density
  `__g1` children) under the deposited GATE-1 rule (docs/43:1985-1990 idiom, the
  h_afm_relax precedent). Known fragility carried into the relax family's risk
  register: the production Mn relax found *OOH genuinely weakly bound (2.480 Å).
- **E4 PROTOCOL: GATE-(H) VERBATIM, IN-FRAME** — ΔE_mag = E_AFM − E_FM at IDENTICAL
  geometry, in the SAME cell and mesh: at stage 1 the FM reference is the in-frame
  2×1 FM deck (built with the set); the frozen banked u390 .out energies are the FM
  reference only for 1×1 comparisons (the P-A branch); if P-B wins, the core's FM
  references are 2×1 FM twins at each U — added to MN-AFM-PROD-2X1's content and
  count (+8: FM states at u000/u900) — and any comparison to banked 1×1 energies
  additionally requires MN-KBRIDGE. Verdict rule: > 20 meV lower → AFM ADOPTED as
  Mn's magnetic row; |Δ| ≤ 20 meV → MULTISTABLE, recorded with its range; collapse
  to the FM solution or E_AFM higher → measured null, Mn stays FM. M_abs is the
  witness that an AFM solution was actually held. Thresholds reused, not invented;
  no adjustment after any AFM energy is seen.
- **E5 U SCOPE: u390 + ENDPOINTS u000/u900, FIREWALLED** — η(Mn, AFM) at production
  U is the quantity A7.5 gates; the endpoints measure whether the FM-vs-AFM gap is
  U-dependent. No Mn AFM endpoint number is an A7.3/D_M input — the firewall is
  absolute and mirrors item 10's "recorded either way, not entering the score".
- **E6 COLLINEAR LIMIT: REGISTERED** — the screw ground state and the collinear
  approximation are stated limitations wherever this arm is reported; the
  noncollinear spot-check is NOT elected (first-in-campaign machinery class), kept as
  a registered follow-on (docs/66 §6 item 3).
- **E7 TREE + CODE:** all decks under `runs/s0/mn_afm/` (a NEW tree — never
  `runs/a0/main/`, per docs/61:89-90); a dedicated asserted builder
  (`src/dft/build_mn_afm_order.py` for stage 1; core/relax builders follow the
  pattern) committed BEFORE any run; the AFM-split decks name BOTH sublattice labels
  in the HUBBARD card (`U Mn1-3d 3.9` AND `U Mn2-3d 3.9` — the one-label card would
  silently leave a sublattice at U = 0, the exact trap the Ru probe build caught); an
  AFM-capable η extractor (Mn1/Mn2-split decks; the a0main readout addresses
  runs/a0/main literally and cannot read them) is committed before any η is
  extracted from this arm — the Row-17/§A11.8 committed-before-extraction precedent.

## 5. The deck program (staged; counts and triggers pre-stated)

| family | decks | trigger | content |
|---|---|---|---|
| MN-AFM-ORDER (stage 1) | 4 | licensed now | 2×1 slab at u390: FM, P-A, P-B1, P-B2; fixed geometry (banked slab geometry tiled ×2 along [001]) |
| MN-AFM-CORE | 12 | E1's measured winner (any AFM candidate ≤ FM + 20 meV; else the arm records the FM null and stops) | 4 states × {u000, u390, u900}, winning pattern, fixed FM-relaxed geometries; in 1×1 iff the winner is P-A (expressible), in 2×1 iff P-B |
| MN-AFM-RELAX | 4 + 4 | core banked | relax + `__g1` children under GATE-1 |
| MN-KBRIDGE | 4 | only if a cross-cell energy comparison is claimed | 1×1 @ 8 4 1 + 2×1 @ 4 4 1 pairs |
| MN-AFM-PROD-2X1 | 4 (+8 E4 FM twins at u000/u900) | only if P-B wins E1 | production states in 2×1, with in-frame FM twins per E4 |

Worst case ≈ 24 SCFs + 8 relax-family jobs; measured-band cost ≈ 140–2,750 SU
(≈ 0.2–4 % of balance); stage 1 alone 20–76 SU.

## 6. What this arm may and may not do

**MAY:** lift the A7.5 strike (by running, on any outcome); adopt an AFM magnetic row
for Mn's materials-facing η under the E4 rule; report ΔE_mag, the ordering
measurement, and the U-dependence of the gap as this arm's own deliverables, with the
E6 limitation attached.

**MAY NOT:** enter any number into the banked A7.2/A7.3 scores; touch any banked file
(`runs/a0/main/Mn/` stays frozen; new tree only); choose or adjust a threshold after
any AFM energy is seen; present any collinear result as "the" β-MnO₂ ground state;
quote the §3 literature values before the entrant verifies them.

## 7. Open items (the entrant's)

1. Verify the §3 literature citations before the report quotes them.
2. The AFM-capable η extractor lands with the core family (E7); stage 1 needs only
   total energies and moments (gate-(h) recipe reads).
3. The E1 measurement executes its own adoption rule; the entrant countersigns the
   outcome as a dated line when the stage-1 energies land.

> **[MN E1 COUNTERSIGNED 2026-09-02]** — the entrant's directive of 2026-09-02, verbatim
> *"Sign D3"*, given after docs/68 §4 and the D3 elaboration (the frame-bound reading:
> FM-relaxed geometry, collinear patterns, a 2×1 cell that cannot hold the screw ordering,
> U = 3.9, and no scored quantity depending on it) were put to the entrant. Outcome
> countersigned: **measured null, FM stands.** P-A +664.6 meV and P-B1/P-B2 +1,219.5 meV
> above FM in the 2×1 FM-relaxed frame, AFM solutions genuinely held (M_abs 42.5 / 43.1 vs
> 46.2 μB; M_tot 4.33 / 0.00 vs 36.00). MN-AFM-CORE not triggered; the arm closes at stage 1;
> the A7.5 strike is lifted by running; the E6 limitation travels with every Mn magnetic
> sentence. Item 1 above (verify the §3 literature values before the report quotes them)
> remains open. Reflected in `a0main_readout.py`'s `mn_afm` text the same day; the banked
> readout JSON is NOT regenerated (its numbers are unchanged; its `mn_afm` sentence is
> superseded by this line).

---

## §7 item 1 DISCHARGED — 2026-09-03: the §3 literature verified against primary sources, and one number is wrong

*Executed under the entrant's 2026-09-03 directive ("decisions that maximize placement at STS").
§7 item 1 was the last open item on the Mn AFM arm: "verify the §3 literature citations before
the report quotes them." Verified this date against OpenAlex bibliographic records and two
independent full texts. Zero SU. The disposition line at the end is still the entrant's.*

§3 as written asserts four things, all flagged UNVERIFIED at the time: **(a)** Yoshimori 1959,
**(b)** turn angle ~129 deg per c, **(c)** T_N ~ 92 K, **(d)** neutron refinement Regulski et al.
~2003-2004.

| claim | verdict | evidence |
|---|---|---|
| **(a) Yoshimori 1959** | **VERIFIED, exactly** | Akio Yoshimori, *"A New Type of Antiferromagnetic Structure in the Rutile Type Crystal"*, **J. Phys. Soc. Jpn. 14(6), 807 (1959)** (OpenAlex, DOI 10.1143/jpsj.14.807; 554 citations). Credited in the literature with first determining the helical order: *"The full helical magnetic order with a pitch of (7/2)c first determined by Yoshimori"* (arXiv:1211.5518). |
| **(c) T_N ~ 92 K** | **VERIFIED, two independent sources** | *"It orders magnetically at T_N = 92 K"* (arXiv:1211.5518); *"beta-MnO2 is known as a classical example of magnetic materials with a well-defined screw magnetic order below TN = 92 K"* (arXiv:2401.02109, Okabe et al., PRB 103, 155121). |
| **(d) Regulski ~2003-2004** | **VERIFIED, and there are TWO papers** | M. Regulski, R. Przeniosło, I. Sosnowska, J.-U. Hoffmann, *"Incommensurate magnetic structure of beta-MnO2"*, **Phys. Rev. B 68, 172401 (2003)** (OpenAlex, DOI 10.1103/physrevb.68.172401); and the same four authors, **J. Phys. Soc. Jpn. 73, 3444 (2004)** (cited as ref. 27 of arXiv:2401.02109). The "~2003-2004" hedge was right for the reason that both exist. |
| **(b) turn angle ~129 deg per c** | **NOT VERIFIED — and WRONG AS WRITTEN** | Both full texts give the propagation vector, not an angle: *"Defining a propagation vector k = (0,0,k_z = 2/7)"* and *"This results in a helical antiferromagnetic order with pitch (7/2)c"* (arXiv:1211.5518); *"incommensurate magnetic modulation [propagation vector q_m = (0, 0, ~2/7)]"* (arXiv:2401.02109). A pitch of 7/2 c is a rotation of **360 x 2/7 = 102.9 deg per c**, not 129 deg. |

### The correction, and an honest note about where 129 probably came from

**The report must not say "~129 deg per c".** The sourced statement is: *beta-MnO2 orders below
T_N = 92 K in an incommensurate helical (screw) structure with propagation vector
q = (0, 0, ~2/7), i.e. a pitch of 7/2 c, or ~103 deg of rotation per c* (Yoshimori 1959;
Regulski et al. 2003, 2004).

**A caveat on the near-miss, flagged as a derivation and not as a source.** 129 deg is close to
**180 - 360/7 = 128.6 deg**, which is what one gets for the angle between *nearest-neighbour* Mn
moments if the two rutile sublattices (offset by c/2) are counted in sequence rather than the
advance per c. So the number is probably not invented — it is plausibly the right angle carrying
the wrong qualifier. **But neither source I read states it**, so it is recorded here as an
unverified reconstruction and **must not be quoted as sourced.** If the report wants a
nearest-neighbour angle it takes a citation that actually prints one.

### Why this was worth the hour

This is the campaign's verify-AI-literature rule catching exactly what it exists to catch: three
citations that were right, and one number, attached to them, that was wrong in a way no reader
would question — a plausible angle, in the right range, beside correct bibliography. It sat in
the physics paragraph of an arm that has already been countersigned and closed.

### Owed from the entrant — one dated line

`**[MN AFM §3 LITERATURE 2026-__-__: VERIFIED AS CORRECTED]**` — adopting the sourced sentence
above and striking "~129 deg per c"; or `STRUCK` (no literature magnetic-structure number is
quoted at all); or `DEFERRED` to report-writing. Discharging it closes docs/67 §7 entirely and
with it the last thread of the Mn AFM arm.
