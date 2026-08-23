# 51 — What is left to run: triage of every staged deck without an output, 2026-08-23

**Date:** 2026-08-23. **Machine:** Purdue Anvil, ACCESS CHE260157, queue empty at the start
(1,081.7 SU spent of 100,000). **Method:** one read-only classifier per deck family
(registration, supersession, launch shape, cost) and one independent skeptic per verdict,
instructed to refute it; every verdict below was confirmed by its skeptic. The classifier
and skeptic outputs (12 agents, 457 tool calls, file:line evidence throughout) are the
working record; this file is the decision log. Nothing here changes a registered rule.

Input: the 51 staged `.in` decks on the Anvil mirror that had no `.out`, in twelve
directories.

## 1. Verdicts

| family | decks | verdict | governing text | action taken |
|---|---|---|---|---|
| `runs/probe_new/*` (Co_uladder 12, Fe/Mn/Ni audits 11, Ir/Ru dipole 8) | 31 | **STALE DUPLICATES** | — | every deck byte-identical to a `runs/probe/*` deck that ran on Vast Aug 8–9 with `JOB DONE` (Co_uladder, audits: 27/27) or to the `runs/probe/{Ir,Ru}/*__dipole.in` decks that ran (P2 refuted, docs/41); an untracked Aug-8 staging copy that was rsynced to Anvil with the tree. **Moved aside**, not deleted: local → scratchpad `stale/probe_new-2026-08-23`, Anvil → `$PROJECT/xfer/stale/probe_new-2026-08-23`. Never committed, so no history changes. |
| `runs/s0/i_cutoff_ladder/sno2__ecut{60,80,100,120}` | 4 | **LAUNCH** | A7.4 row (i) (deposited); precondition (Sn UPF) discharged 2026-08-22 | **Launched, job 20094699** (manifest `runs/s0/m_s0_sno2.txt`, 20 ranks / `-nk 2`). The Anvil copies still carried the builder-guessed lowercase `sn_` filename — the exact failure the skeptic predicted — and were re-staged from commit 729c427 (md5-matched both ends) before submission. Capability/admission-only: a PASS qualifies the pseudo inside 80/640; SnO₂'s tier admission stays PENDING A7.5 (Mom 2014 cus-site confirmation by Sep 1, no confirmation in the repo). |
| `runs/probe/Ru_lit2/cov_2OH__2x1_off` | 1 | **LAUNCH** (re-run of an UNBANKED row) | A5.2 + A5.7 (deposited) | The deck ran to `JOB_DONE` on Vast 2026-08-14 (ledger: rc=0, SCF_FAIL=0, F_LAST 0.005640, 14,801 s) but its `.out` was never pulled — the Aug 19 pulls were per-directory and skipped `Ru_lit2`; the box was destroyed Aug 22; no copy exists anywhere on this machine. No number was ever banked, so A8.8's no-replacement clause does not bite; the re-run is a **fresh realisation, not parity evidence**. **Launched, job 20094762** (`runs/probe/m_lit2_ru_rerun.txt`, header records the loss). |
| `runs/probe/Cr_lit2/cov_{2OH,Ovac}__2x1_off.out` | 2 outputs | **BANK** | A5.2 | Both complete (`bfgs converged`, `JOB DONE`, 0 SCF failures; 8 and 16 ionic steps; E −3189.97897994 / −3062.86770500 Ry; M 22.00 / 26.00) and sitting **untracked** since the Aug 19 pull. Committed (d207a78). |
| LIT-2 GATE-1 children for those two Cr relaxations | 2 (new) | **BUILD + LAUNCH** | A5.7 (deposited): every new Cr relaxation gets a fresh-density fixed-geometry `__g1` SCF | Emitted by `build_lit2_ruo2_ladder.py --gate1` (refuses unless both parents are converged — they are), **launched, job 20094768** (`runs/probe/m_lit2_gate1.txt`, 20 ranks / `-nk 4`). |
| `runs/hp_costmodel/crslab_nosym__*` (scf + 8 hp.x) | 9 | **SUPERSEDED** | §4-A (deposited) registers the cost model; the nosym arm registers nothing | Existed only to price sym-vs-nosym for block 3Y, which the reconciled board (docs/45 §E) no longer carries; the sym arm ran 2026-08-10 (4/4 `Convergence has not been reached after 80 iterations`); S4's slab hp.x scope is "existing runs + ONE relaunch under 72 h" with settings these decks do not have; the three q-mesh counts were already **measured** on the nosym ground state (`build_hp_validation.py` CRSLAB_NQ_MEASURED_NOSYM). No hp.x path exists on Anvil (driver is pw.x-only; `queue_hp.sh` hardcodes Vast paths; array semantics would race one shared SCF). Left in place; not launchable without a registration. |
| `runs/Co_slab/s0_OOH` + `runs/probe/Co/s0_OOH__restart` | 2 | **SUPERSEDED** | A5 D9 "LIT-7: Co *OOH attempt — deferred and NOT registered"; A5.5 firewall ("the Co *OOH and Cu holes remain holes") | No converged Co *OOH exists anywhere. The Co_slab deck is the attempt-1 recipe that already failed 0-for-4; running it in place would write into the banked tier_v1/v2 source tree and `score_n7.py` would silently flip Co from `bounded` to `chain` — exactly the silent replacement A8.8 forbids. The restart deck (2026-08-09) is a drift-derived 0.64 Å off-plane geometry matching neither S3 arm, reverts to the recipe predicted to SCF-fail, and was never in any manifest. Co *OOH is re-owned by A8/S3 (docs/47 A8.4) under the off-plane/mirror/second-seed protocol in 2×1v. |
| `runs/Cu_slab/{slab,s0_O,H2,H2O}` | 4 | **SUPERSEDED** / gas refs DONE_ELSEWHERE | A7.5 (deposited) puts CuO₂ on the exclusion row; A5.5 firewall | H₂/H₂O are byte-identical to the gas decks converged in seven other directories (metal-independent; computed once). slab/s0_O are Jul-2026 1×1 nosym+noinv decks for a metal time-boxed out (docs/26 §6), rescue declined twice (docs/30, docs/34), never in tier_v1/v2; the Cu PAW pseudo is not among the 12 UPFs staged on Anvil (preflight would refuse); stale `convergence NOT achieved` + `JOB DONE` outputs in the directory would trip the driver's stale-`.out` refusal. An unregistered revival thread (Cu as the held-out MLIP metal, tasks/todo.md / docs/40) is a registration question for a future amendment, not a launch trigger. |
| S0 gate (h) RuO₂ AFM re-anchors — the four 2×1v AFM **relaxations** | 0 built | **HOLD on A8** | exists only in docs/47 A8.5 (undeposited); A7.4 row (h)'s four AFM SCFs are DONE and banked (4/4 ADOPT_AFM, commit 946c3aa) | Nothing to launch: no decks, manifest or committed builder exist (the gate-(h) SCF builder lives only in a scratchpad; `build_cellsym_pilot.py` hardcodes Ru nspin = 1; `probe_decks.py` cannot parse the Ru1/Ru2 species). What the skeptic added: (i) the deposited GATE-1 rule (docs/43:311-314) makes the owed family **≥ 8 decks** (4 relax + 4 `__g1` children, with the ≥ 5 meV re-relax loop and A8.3's draft 1 meV above-parent refusal); (ii) the banked AFM SCFs carry residual forces 0.012–0.023 Ry/bohr against `forc_conv_thr` 2e-3, so these are genuine multi-step nspin = 2 BFGS runs and docs/48's ~237 SU/relax (nspin = 1 TiO₂) understates them, likely 2–4×; (iii) A8.1's "second seed" basin factor and A8.5's standalone four collide — whether the AFM Ru row is the Ru second seed inside tier_v3 (then crossed with 1×1/2×1v and off/mirror, up to 16 relaxations) or the standalone four must be settled in the A8 re-authoring. |

## 2. What this leaves on Anvil

Running at the end of this triage: 20094699 (SnO₂ ×4), 20094762 (Ru LIT-2 ×1),
20094768 (Cr LIT-2 GATE-1 ×2). Everything else staged without an output is superseded
or held on A8. The next compute that can launch without a decision is **none** — S3, the
gate-(h) relaxations and the Co *OOH re-attempt all wait on A8's re-authoring and
re-deposit (due Aug 24); the external census (S1/S2) waits on A9.

## 3. Record corrections surfaced by the triage

- `runs/s0/s0_manifest.json` gate-(i) `launch_precondition` still carried the
  pre-discharge text → superseded in place (c807c1c), old text kept inside the field.
- `runs/probe/lit2_manifest.json` said `NOT_DEPLOYED` while `m_lit2_np20.txt`'s header said
  DEPLOYED 2026-08-13 → status now records the deployment, the Cr banking, the Ru loss
  and re-run, and the GATE-1 launch (d207a78).
- docs/45 §D still said A8 "NOT DRAFTED" and §E's S0 row still said "launch awaits LIT-2/3
  drain" → corrected in the same commit as this file.
- The LIT-2 block had no row on the program board; the Ru output loss and the missing Cr
  `__g1` children were unrecorded → §E gains a LIT-2 line.
- `anvil/README.md:117` "S0 stays on Vast as registered" predates the box's destruction;
  the machine change is registered in A8.5 (draft). Both the SnO₂ arm and the LIT-2
  re-run are pre-A8 runs of deposited-amendment work on Anvil under PARITY_PASS, with the
  block 1C waves as precedent; A8.5 should name them.
- A5.2's readout (PASS/FAIL of the coarsened-Qiu ladder → label on the Cr termination
  column) has **no scorer** yet (the builder's docstring: "The readout (not built here)").
  It becomes scoreable once 20094762 and 20094768 land; writing it is owed.
