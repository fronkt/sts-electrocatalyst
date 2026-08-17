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

## 7. (2026-08-16) The goal never changed — the word "fixed" became the project

Captured from the post-lit-sweep discussion, after Frank asked: *"I thought our goal
was to find a better OER alloy by using a fixed DFT to screen HEAs to beat iridium?"*
Answer: that sentence is still exactly the project. The last two months have been the
word **"fixed"** — it turned out to be a research project of its own. This section is
the plain-language map of why, for reuse in the report's framing and the interview.

**The arc.** The screen was built first (r4: 4,000 compositions → 12 candidates,
best η 0.440 V, melt list built — docs/36–37). Checking the ruler before melting is
what exposed the problem: the DFT's *silent* errors are larger than the differences
the screen was ranking.

| Silent error | Moves η by | Where measured |
|---|---|---|
| Symmetry trap (mirror-plane saddle) | 0.291 V on Ir (0.781→0.490), mechanically confirmed i167 cm⁻¹ | 1C Hessian |
| Hubbard-U choice | 1.12 V on Cr — fired P7, withdrew the headline | P7 probe |
| Magnetic basin | 0.1–0.4 eV drifts on our own runs | GATE-1 audits |
| Coverage/cell | 6/9 rows > 0.10 eV | block 1A |

Candidate separations in the screen are 0.03–0.08 V. **Ranking at 0.05 V with a
method that silently wobbles 0.1–1.1 V is measuring millimeters with a ruler that
wobbles centimeters.** The withdrawn Cr headline was that artifact happening to us;
the 6/12 desorption-invalid r4 candidates were it happening downstream.

**What each piece is, in one line each:**
- Endmember tier (CrO₂...IrO₂) = the calibration standards, never candidates. You
  don't melt your ruler.
- tier_v3 / corrected protocol = *the fixed DFT* — symmetry released, basin gated,
  U registered, coverage stated; every fix measured, not assumed.
- silentgate + the Xu 810 census = proof the errors are the field's, not our builder's
  bug — what makes the fix credible.
- S8 (registered 2026-08-16, round-2 synthesis addendum) = the loop closing: re-rank
  r4 under the fixed protocol → melt top 2–4 + a poor anchor at FWM → Purdue OER vs
  an IrO₂ reference on the SAME bench, predictions frozen before the first melt.
  Access to furnace + XRD + OER bench confirmed by Frank 2026-08-16.

**The one-sentence story (report framing + interview):** "I set out to find a cheap
alloy to beat iridium. My screen's hidden errors turned out to be 10× larger than the
differences I was ranking — so I measured every one of them, fixed the protocol,
showed the same errors sit in the field's published data, then re-ranked my
candidates, melted them, and measured them against iridium itself." One project, not
two: discovery-without-rigor dies in round 1 (three in-field PhDs); rigor-without-a-
payoff has no ending. This supersedes §2's worry — the melt hook is now registered,
not hypothetical, with a clean detachment rule if the furnace half runs long.

**Interview honesty note on "beat iridium":** in alkaline, NiFe-based catalysts
beating IrO₂ is already established in the literature. The claim is never "first to
beat iridium"; it is "**a screen you can trust found it, and the loop closed** —
predicted, made, measured, same bench." Do not let a judge land this first.

**Standing correction absorbed into all planning (2026-08-16):** budgets are sized to
the hard deadline, not to assumed hours/week. The lit-sweep's "21 effective days" and
its drop-two-deadlines ultimatum are void; budget-motivated cuts reverted to live
(round-2 synthesis addendum), physics kills stand.
