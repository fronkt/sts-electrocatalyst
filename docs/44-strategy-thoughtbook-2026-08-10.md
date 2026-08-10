# 44 — Strategy Thoughtbook (2026-08-10)

Not a pre-registration, not a results doc. This is a running notebook of strategic
discussion (competitiveness, scope, sequencing) from a separate planning session,
captured here so it doesn't evaporate. Revisit and prune as decisions get made.

## 1. Where the Week-1 campaign result actually sits

The 1C Hessian pilot landed CONFIRMED (b48cc78): the mirror-locked Ir `*OOH` geometry
is a genuine saddle point (i167 cm⁻¹, f_y=1.000, above the i103 noise floor, all gates
passed). This upgrades the symmetry-trap claim from an energy observation ("releasing
the constraint drops η 0.781→0.490 V") to a mechanically proven instability. It is the
first fully positive, fully confirmed result of the campaign after several weeks of
retractions (Cr, Co, the confounded UMA-head claim) — worth remembering when morale
reads the campaign as "mostly withdrawals."

Scope discipline held: Cr's Hessian stays deliberately withheld per docs/43 §3-A.7
until block 1A's cell verdict lands. One CONFIRMED does not fire the §3 consequence.

## 2. Competitiveness worry: are we building the wrong kind of headline?

Raised concern: most visible STS Top 40 projects have a one-sentence, legible hook
(new material, algorithm that beats X, a proof) — this project's pivot from "better
catalyst" to "three silent error classes in computational catalyst screening" is a
harder sell to a non-specialist judge.

Working resolution:
- The **first-round filter** (3 in-field PhD reviewers reading the full report) rewards
  rigor and depth more than a punchy one-liner — that's the round methodology findings
  are built to win.
- The **risk is legibility, not substance**. Don't manufacture a flashier materials
  claim (the scaling-floor analysis already closed that door honestly — the original
  Cr number was scaling-limited, not a real breakthrough).
- Fix: frame the writeup around stakes a general judge immediately gets — "AI is now
  used to screen materials for the energy transition; this project shows three
  specific, previously-undetected ways that screening silently gives the wrong answer,
  with a demonstrated fix" — not the audit-log version of events. The Ir Hessian result
  is a vivid, explainable centerpiece for that framing (a textbook-symmetric geometry
  turns out to be mechanically unstable).
- If melt+measure lands, that supplies the legible "and here's a real material" hook
  on top, resolving the worry more directly than any amount of extra reframing.

## 3. Going beyond three error classes — candidate additions, ranked

Everything below is scoped against `src/dft/probe_decks.py` / `orient_starts.py`
machinery that already exists, or the QE capabilities already validated in docs/42.
None of these require new binaries or install work beyond what docs/42 confirmed
reachable.

**Do unconditionally (cheap, no new relaxations, uses existing converged geometries):**
1. **BEEF-vdW ensemble error bars** — `libbeef` already compiled per docs/42. Fixed-
   geometry variant deck, same pattern as the existing dipole/vac/U/spin probes. Gives
   a 4th silent axis: functional choice alone moves η with zero red flag anywhere in
   the QC.
2. **Ru AFM magnetic-structure test** — one fixed-cell SCF with antiferromagnetic
   starting config on the Ru anchor (RuO₂ magnetism is literature-contested; current
   anchors assume nspin=1 per docs/41 open questions). Cheap, closes an acknowledged
   loose end rather than opening a new investigation.

**Do if Week-1 finishes on schedule (needs new full relaxations, real wall-clock):**
3. **Extend the symmetry trap to the 3d metals** — never tested beyond Ru/Ir (docs/41
   §"open research questions"). Reuses `orient_starts.py`. Turns "one anecdote" into
   "a systematic pathology" if it recurs — a materially stronger claim. This is the
   one lane that most deserves its own dedicated box(es) given job count (5 metals ×
   3 adsorbates).

**Stretch goals only, and only after melt+measure is secured — don't let these eat the
schedule:**
4. **ZPE/entropy via `ph.x`** — real physics (routinely tens–150 meV per intermediate,
   large enough to flip a pls assignment), but should run on *final* corrected
   geometries. Running it now risks redoing expensive phonon work once Week-1's
   cell/symmetry verdict lands. **Sequence after Week-1, not parallel with it.**
5. **Implicit solvation (3D-RISM)** — binary works per docs/42, but needs `.MOL`
   solvent files fetched from QE source (one-time setup). Runs on existing converged
   geometries once available, so it's schedulable in parallel with Week-1, just not
   free the way #1/#2 are.

**Explicitly not adding back:** MLIP fine-tuning, SQS HEA tiers, full Environ
solvation, OSCDFT — already correctly killed in docs/41; re-adding them risks turning
a tight, defensible 5–6-class taxonomy into an unfinished 10-class survey, which reads
worse to a judge than fewer, fully-closed results.

## 4. Making melt+measure the second half of the story, not a checkbox

Strongest version isn't "melt one alloy, measure it, done":
- **Melt and measure ≥2 candidates**: the naive (uncorrected) top pick and the
  corrected (post-error-fix) top pick, if they differ. If the corrected model's pick
  outperforms experimentally, that is the single most powerful piece of evidence in
  the whole project — proof the error-taxonomy work changed the actual decision and
  that the change was correct.
- **Include a known-catalyst positive control** (commercial IrO₂ or NiFe-LDH) measured
  on the same rig, anchoring the experimental side the same way the DFT tier is
  anchored against literature RuO₂/IrO₂.
- **Replicate measurements** where time allows — a single point can't be distinguished
  from rig noise, and reproducibility is exactly what a skeptical judge probes.

## 5. Running additional error-class lanes in parallel with Week-1 — setup sketch

Principle: physically and logically separate from the 9 live boxes. Do not share
cores with anything on the critical path.

- **New, dedicated boxes only.** The 9 running boxes are near their cgroup caps;
  sharing risks the kind of accidental-kill/thrash incidents this campaign has
  already hit (wrong `pkill` pattern, PRRTE oversubscription, etc.). Rent 2–3 fresh
  cheap CPU boxes for the new lanes.
- **New branch**, not `r0-catalysis-revival` — e.g. `error-classes-round2` — so new
  work doesn't collide with the in-flight docs/43 amendments on the live branch.
  Merge/rebase once both sides are stable.
- **Dependency-ordered launch:**
  - Launch now, no dependency: BEEF-vdW, Ru AFM test (need only existing geometries).
  - Launch now, but budget real wall-clock and its own box(es): 3d-metal symmetry-trap
    extension (full relaxations).
  - Hold until Week-1's cell/symmetry verdict lands: ZPE/`ph.x` (avoid redoing phonon
    work on a geometry that later changes).
  - Fetch solvent files first, then launch independently: RISM solvation.
- **Independent tmux + log per new box**, exactly mirroring the existing `queue_r1.sh`
  pattern, so the monitor watching the 9 live boxes isn't fed a mixed log stream.

## 6. Tier-1 logistics — not computational, but can sink the whole entry if missed

Restated here as a standing checklist, not new information (see docs/25, project
memory):
- [ ] STS sponsor of record — still unresolved as of last check.
- [ ] Educator + project recommenders lined up — target ~September.
- [ ] AI disclosure compliance pass (Task 4 100-word answer + AI Usage Chart) —
  AI may not write report/essay prose; verify before submission.
- [ ] Risk-assessment paperwork for the melt/draw campaign, dated *before* the first
  melt.
- [ ] Data freeze discipline — results must be complete, not proposed; hold the
  mid-October freeze so there's ~3 weeks left for Frank to write.
- [ ] Verify the two prior-art citations before the report is finalized (Deshpande
  et al., ACS Catal. 6, 5251 (2016); Goniakowski & Gillan, Surf. Sci. 350, 145 (1996),
  arXiv:mtrl-th/9508009) — controls how much of the "novel error class" framing survives.

These compete for the same calendar as the compute work and are easy to let slide
while attention is on the DFT campaign. Treat locking down the sponsor + recommenders
as the single highest-leverage non-compute action available right now.
