# B1 pre-launch review (2026-10-16)

**Reviewer:** Codex `gpt-6.1-sol`, xhigh, read-only, no network. Thread 01a147fb-29d4-7040-8b90-919bdfb7de60.
**Brief:** `PRELAUNCH_REVIEW_REQUEST.md`.
**Verdict:** FIX FIRST. Every item is folded as below.

## Findings and what was done

1. **BLOCKER: the package was not in HEAD.** Expected at review time. The package is committed with explicit paths
   (the gitignored `results/` files are force-added) and pushed before `stage`.
2. **FIX: a banked reference carries `IEEE_INVALID_FLAG`.**
   - `runs/a0/cell/s0_OH__2x1v_mir__u715.out` carries the marker. B1's runner would reject such a run, but `qe_qc`
     labels the file TRUSTWORTHY.
   - The scorer now applies the runner's severe markers to every banked reference. A relaxation energy measured
     against a flagged reference is reported as n/a, with the flag shown.
   - This caveat already applied to the fixed-geometry 0.1725 V (A13), which uses that output; B1 does not change
     that result. The relaxed atomic *OH leg gives an independent value.
3. **FIX: unregistered H criterion.** The scorer had an extra condition: H must sit closer to its adsorbate O than to
   any slab O. This is removed. H counts as bonded within 1.15 Å of an adsorbate O, as registered, and the slab
   distance is printed as a diagnostic only.
4. **FIX: unresolved arms hid diagnostics.** Every available per-state energy, GATE-1 value, relaxation energy,
   magnetization, chemistry class and off-plane result, and every branch mismatch, is now printed and written to JSON
   before the unresolved exit. Only η scoring is suppressed.
5. **NOTE: the fixed η pair is now printed** (0.9239810 and 1.0964974 V).

## Checked and found correct by the reviewer

- **Decks:** all eight reproduce from the builder, and paired legs differ only in prefix and Hubbard card. Kicks,
  symmetry flags and the 14 fixed atoms match between legs.
- **Hashes:** the spec, source and Slurm-embedded hashes match the bytes, and runner validation passes.
- **Timing:** QE stops at 20,000 s, the runner ceiling is 20,700 s, projection gets 600 s, and the Slurm wall is
  21,600 s.
- **Runner settings:** the 126-iteration ceiling, pools, relaxation checks, projection and density retention are
  consistent.
- **Launch gates:** the round-6 gates are preserved, and `1-8%8` with throttle 8 validates. Ceilings are 6,144 SU
  for stage 1 and 7,488 SU overall.
- **Scorer formulas:** η, the bands, GATE-1 and the limiting-step split match the registration.

## Scorer test after the fixes

The eight banked single points stood in for both the relaxations and the terminal SCFs, in a scratch directory with
COMPLETE receipts. The scorer reproduced:
- the fixed-geometry pair exactly: 0.9239810 and 1.0964974 V, Δη +0.1725164 V, both limited by step 1;
- GATE-1 = 0 for every state;
- the IEEE flag on the atomic *OH reference.
