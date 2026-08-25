# 57 — Post-Compute Stretch: Generalized DFT-Screening Audit Checklist

Status: **NOT STARTED.** This doc lives on branch `stretch-checklist-generalization`,
created 2026-08-25 specifically to hold this plan without touching the live S3
campaign on `r0-catalysis-revival`. Do not begin §3 until the precondition in §1 is
met. Do not merge this branch into the active campaign line before then either.

## 0. Origin

Prompted by comparing this project's compute half against Frances Liang's
PLI-Analyzer (2026 Regeneron STS Finalist) — a platform that audits AI-predicted
protein-protein complexes (AlphaFold3, Boltz-2) against sequence-database ground
truth, found ~50% of predicted complexes wrong, and shipped it as an open-source,
reusable tool. Our compute half audits a different kind of prediction (DFT, not a
learned model) but is the same genre of project: a rigorous framework that catches
an existing computational method giving a wrong answer, and that already overturned
a real conclusion (the earth-abundant-rutile headline — todo.md "HEADLINE
WITHDRAWN", triggered by the P7 U-sensitivity test in docs/41 §5).

The open question: does packaging this project's gate battery into a named,
portable checklist — and testing it on a system genuinely outside this HEA-OER
pipeline — close the gap with Frances's reusable-artifact contribution?

## 1. Decision: sequence after core lock, do not run in parallel

Precondition to start §3: the S3 factorial closes (current round-5 arrays drained
and scored), the RuO₂ AFM re-anchors land, physical melt+test results are in hand,
and a first full draft of the R4 write-up exists. Physical testing and DFT compute
run on separate infrastructure and could technically overlap in wall-clock time —
that is not the constraint being managed here.

## 2. Why not parallel

**(a) The constraint is attention, not compute-hours.** This campaign's own record
is the evidence: the A8.4 rung ladder (retry_bh restarts, beta escalations),
branch-flip diagnosis (Ni s0_OOH, Co s0_O), the `upscale`/`mixing_ndim` unregistered-
parameter corrections, and the a024/a088 node-exclusion workaround have all needed
close, repeated, hands-on triage (docs/45), not fire-and-forget queuing. A second,
independently convergence-prone DFT system competes for exactly that kind of
attention against closing S3 and drafting R4 — regardless of which boxes it runs on.

**(b) Order of operations.** Several gate thresholds are still live decisions, not
frozen constants — e.g. the R1–R5 registered-parameter calls in todo.md
(`upscale`, `mixing_ndim`, `electron_maxstep`), and the A8.8 banking question for
the Fe/Mn below-parent minima. Testing whether a checklist "generalizes" before its
own thresholds are frozen risks having to redo the portability test the moment a
threshold changes.

**(c) The two halves of "generalizing" have very different costs**, and only one is
expensive:

- **Cheap (do now, as part of the R4 write-up — not this branch):** name and write
  up the gate battery that has *already* been applied across a set of oxides, not
  one element. This is real generalization evidence already in hand:
  1. **Magnetic-metastability audit (GATE-1)** — a fresh SCF at the relaxation's
     frozen final geometry must reproduce its own energy, or the state is refused.
     Origin: the Fe/Mn/Ni magnetic-metastability probe (docs/41); now the
     acceptance test for every S3 relax (docs/43–56).
  2. **Symmetry / finite-size trap test** — off-plane vs mirror-symmetrized cell
     comparison, vacuum-separation check. Already caught one real error (Ir's
     *OOH scaling moved from outside to inside the universal band once the
     symmetry trap was corrected; docs/41 §6c) and one non-error (Ru's trap was
     82 meV, descriptor untouched).
  3. **Hubbard-U sensitivity ladder (P7)** — sweep U across a multiplier range at
     fixed geometry; a pre-registered 0.15 V threshold falsifies the headline
     if any descriptor moves past it. This is the test that actually withdrew
     the headline claim (docs/41 §5).
  4. **Coverage as a live variable** — not fixed as a modeling convenience;
     GATE-1 verdicts showed it changes outcomes (docs/32).

  Writing these four up as a named, explicit checklist with pass/fail criteria
  costs no new compute — it is a description of what this project already did
  across Cr/Mn/Fe/Co/Ni/Ru/Ir, not a relabeling of a single case.

- **Expensive (deferred, this branch):** apply the *frozen* four-item checklist to
  one catalyst system genuinely outside this rutile-OER pipeline, to test whether
  it transfers. This is the part that needs new DFT convergence work and is being
  deferred.

## 3. Stretch protocol, if pursued

1. **Precondition check.** S3 closed and scored, RuO₂ AFM anchors in hand, physical
   results in hand, R4 write-up drafted, all four checklist criteria frozen
   (no open R1–R5-style threshold decisions).
2. **Pick target system** at pickup time — a documented literature DFT-screening
   dispute or a different reaction/oxide family, unrelated to rutile(110) OER, so
   the test is a real transfer rather than a variant of the existing pipeline.
   Not chosen yet; do not pre-commit a system now while the core campaign is live.
3. **Time-box it.** Pick a kill date roughly one week before the Oct 15 data
   freeze. Apply the same discipline already validated on this project: the
   endmember-parity campaign's Co/Cu exclusion (docs/26 §5–6, documented protocol
   instead of indefinite chasing) and the current campaign's rung-(iii)
   NOT_CONVERGED gap declaration (docs/45). If the second system is not cleanly
   converged (GATE-1 clean, no SCF_FAIL, forces under the registered threshold) by
   the kill date, exclude it and ship the checklist writeup without a second-system
   point.
4. **No threshold loosening to force convergence.** Same rule this project already
   enforces on itself (A8.4 ladder escalates mixing/beta parameters, never the
   force/energy acceptance criteria) — a checklist "validated" by loosening its own
   pass bar to fit isn't validated.

## 4. What would make this not worth doing at all

If R4 write-up time runs long, or the physical-testing results need more
computational follow-up than expected, drop this branch entirely. The cheap
writeup in §2(c) is the load-bearing deliverable for matching Frances's
reusable-contribution framing; the expensive second-system test is a bonus, not a
requirement, and this project's existing exclusion discipline (§3.3) is the
precedent for saying so cleanly rather than leaving it an open thread.
