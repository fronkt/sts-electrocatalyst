# S0 — Nine capability gates (master manifest)

Stage S0 of the pre-registered error-budget program. Registered as EXACTLY 29 jobs /
~35 box-h in docs/43-prereg-week1-factorial.md AMENDMENT 7 (A7.4 nine-gate table;
Zenodo deposit DONE, DOI 10.5281/zenodo.21963144) and
docs/research/2026-08-15-lit-sweep-round2-synthesis.md lines 182-202 (per-gate counts
and decision rules). Program board: docs/45-error-ledger.md section E.

Every gate is RECORDED whichever way it goes. A failed gate is a measured capability
result, not a discarded run. Deck builds may not deviate from the registration without
a recorded DEVIATION line (each gate's README carries its own).

## Launch preconditions

1. LIT-2/3 on box 47662258 (ssh8.vast.ai:22258) must show TWO `QUEUE_ALL_DONE` lines
   in its queue log, OR the campaign is explicitly PARKED with a recorded decision,
   before S0 occupies the box (synthesis S0 section).
2. Amendment 7 Zenodo deposit: DONE (DOI 10.5281/zenodo.21963144).
3. SnO2 arm of gate (i): `ls /usr/share/espresso/pseudo` must confirm the Sn UPF
   (see i_cutoff_ladder/PSEUDOS_NEEDED.txt) before the four sno2__*.in launch.
   The TiO2 arm has no precondition.
4. Gate (a) deck (iv) `slab__beefhub.in` does NOT exist yet by design (SELECT-WINNER,
   wave 2): copy the winning template after decks (i)-(iii) drain (a_beef/README.md).
   The runner below logs SKIP_MISSING for it instead of aborting.

## Gate table (29 registered jobs, ~33.7 est box-h built vs ~35 registered)

| Gate | Dir | Jobs | Est box-h | Decides | Scoring recipe |
|------|-----|------|-----------|---------|----------------|
| (a) BEEF ensemble emission | `a_beef/` | 4 (3 built + 1 SELECT-WINNER) | 4.0 | Which switch makes this build emit the BEEF-vdW ensemble block; XC row struck only if all of (i)-(iii) fail (F5). Deck (iv) = winner + PROBE-U card (capability-only). | a_beef/README.md (confirm ensemble stdout signature vs box QE source BEFORE scoring — null grep on unconfirmed string is NOT a fail) |
| (b) noinv exactness | `b_noinv/` | 2 | 3.8 | Whether dropping `noinv` (16→10 k, ~38% saving) is exact: \|E1−E2\| < 1 meV. Gates deck-building elsewhere — gate (g) may not drop noinv unless (b) has REPORTED a pass. | b_noinv/README.md |
| (c) mirror-arm nosym invariance | `c_nosym_mir/` | 1 | 2.0 | Whether the sym-ON mirror arm (9 k) equals the full 16-point set: \|E − (−3188.70496977 Ry)\| < 1 meV → mirror stays symmetry-ON program-wide. | c_nosym_mir/README.md |
| (d) Hessian timing + sigma_F | `d_hess_timing/` | 1 | 2.5 | Whether conv_thr 1e-10 is REACHED at 2x1v scale + wall clock vs ~2.4 h repricing; if not reached, the Hessian minimum claim is struck before the 19-deck 1C battery (F6). TIMED — the runner's elapsed-seconds field is the deliverable. | d_hess_timing/README.md |
| (e) ortho-atomic projector | `e_proj/` | 2 | 2.0 | FIRST an acceptance test (does the build take the ortho-atomic card); paired dE is one P-PROJ point (full 8-SCF pairing runs under A0, A7.1). Rejection → fifth grid point PROJECTOR-UNVERIFIABLE. | e_proj/README.md |
| (f) GATE-1 U-ladder | `f_gate1_uladder/` | 6 | 5.0 | Fresh-density + second-seed audit of the Cr *OOH LIT-1 ladder points; A7.3 trigger: >50 meV → re-derive the 0.223 V floor and record before dating. | f_gate1_uladder/README.md |
| (g) TiO2 2x1v timing | `g_tio2_timing/` | 1 | 4.0 | Measured (not extrapolated) nspin=1 2x1v relaxation cost before S3 is costed. RELAXATION — long wall clock is expected, not a hang (max_seconds 28800 in-deck). No pass/fail; non-convergence is itself the recorded result. | g_tio2_timing/README.md |
| (h) RuO2 AFM anchor | `h_afm_anchor/` | 4 | 8.0 | E_AFM − E_NM per state (two-sublattice ±0.5); AFM adopted only if lower by >20 meV; collapse = measured null. Discharges P11 limit (i). LONGEST POLE — start early so it drains in parallel. | h_afm_anchor/README.md |
| (i) Ti/Sn cutoff ladders | `i_cutoff_ladder/` | 8 | 2.4 | Tier admission: \|dE(80,100)\| < 5 meV/atom per oxide inside the frozen 80/640 protocol; SnO2 arm capability-only per A7.5. Run the TiO2 arm before/alongside (g) — a TiO2 failure voids (g)'s tier relevance. | i_cutoff_ladder/README.md |

Totals: 29 registered jobs; 28 runnable decks on disk + 1 deferred (beefhub wave-2).
Sum est box-h = 33.7 (registered ~35).

## Recommended launch order

Cheapest decisive gates first — (b) and (e) are acceptance results that gate
deck-building elsewhere; (h) is the longest pole and should enter the pool early;
(i) TiO2 precedes (g); (i) SnO2 is pseudo-gated; (a) deck (iv) runs only after
(i)-(iii) drain and a winner is selected:

```
b → e → h(start early, drains in parallel) → c → d → i(TiO2) → a(i-iii) → f → g → i(SnO2, after pseudo verified) → a(iv, after SELECT-WINNER)
```

The embedded job list in `queue_s0.sh` follows this order. QUEUE_ALL_DONE in the
queue log = drain marker; `JOB DONE` in a .out is NEVER success by itself (check
SCF_FAIL and each gate's convergence recipe).

## Runner

`queue_s0.sh` (this dir) — modeled on src/dft/queue_dft.sh; per-job nk taken from
each gate's manifest.json and embedded in the job list. NP must be a multiple of
every nk in the list (4 and 2): NP=20 default. Machine-readable union of all nine
manifests: `s0_manifest.json`.
