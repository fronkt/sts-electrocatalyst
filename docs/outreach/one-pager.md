---
geometry: margin=0.75in
fontsize: 10pt
colorlinks: true
header-includes:
  - \pagenumbering{gobble}
  - \setlength{\parskip}{0.4em}
---

# Silent Failure Modes in DFT Screening of Oxygen-Evolution Electrocatalysts

**Frank Cai** — High-school senior; Research Assistant, Dept. of Engineering Technology,
Purdue University Fort Wayne; PI, ACCESS allocation CHE260157 (Anvil). One-page project
summary, August 2026.

## Problem

Earth-abundant oxide electrocatalysts for the oxygen evolution reaction (OER) are
routinely screened by DFT, but the screens are rarely stress-tested against their own
methodological choices. This project builds a multi-fidelity screen — a machine-learned
interatomic potential (Meta's UMA) proposes high-entropy-alloy oxide candidates, and
Quantum ESPRESSO (PBE+U) re-ranks the top candidates on rutile(110) surfaces with
*OH/*O/*OOH intermediates and computational-hydrogen-electrode referencing — and then
turns the same rigor on the screen itself. The result is a project about what silently
breaks a DFT overpotential ranking, not just what the ranking says.

## What broke, and what it means

Before quoting results, a set of robustness checks was pre-registered (i.e., the
acceptance/failure criteria were written down before the calculations ran, so the
outcome couldn't be reinterpreted after the fact). Two of them fired:

- **U-sensitivity (project-falsifying).** The initial headline — that an earth-abundant
  rutile (Cr) outperforms the noble-metal anchors RuO₂/IrO₂ — depended on a Hubbard-U
  value the project had not derived from anything. Re-running the same ranking across
  a defensible U range moved η(Cr) by **1.12 V**, roughly 7.5× the pre-registered
  falsification threshold. The claim was withdrawn, on schedule and in writing, rather
  than softened.
- **Magnetic multistability.** Several adsorbate relaxations that reported clean BFGS
  convergence had actually settled into a metastable magnetic solution — a basin the
  optimizer never left. One case sat 175–405 meV above the true minimum despite a
  textbook-looking force trace. A systematic audit found this in 5 of 7 magnetic 3d
  endmembers checked so far; it does not affect the two non-magnetic noble-metal anchors.
- **A symmetry-constrained relaxation trap**, found by comparing production
  (mirror-plane-constrained) adsorbate geometries against orientationally unconstrained
  restarts: one anchor's *OOH intermediate was ~0.29 eV lower off the mirror plane,
  moving that anchor's overpotential from outside the literature range to inside it.
  The effect turned out to be coverage-conditional, not tier-wide, once tested at the
  correct unit cell — itself a finding that needed disconfirming, not assuming.

None of this was found by getting a "wrong" number and going looking for a bug — every
one of these was a **clean-looking result** (converged forces, sensible geometry,
plausible energy) that turned out to be silently wrong for a reason the standard
convergence checks don't see. That is the actual subject of the STS entry: cataloguing
and, where possible, generalizing the failure modes, not just reporting a corrected
overpotential table.

## Status now

The DFT production cell and coverage choice are now settled by a 22-point internal
consistency gate (all SCFs agree; no undetected basin drift). An ACCESS Explore
allocation (CHE260157, 100,000 Anvil CPU-SUs, PI) is provisioning to run the next
campaign — a crossed coverage × symmetry × basin-restart study across an 8-oxide tier —
launching in the next two weeks. In parallel, melt access is confirmed at Fort Wayne
Metals (arc-melting, six to eight high-entropy-alloy-oxide candidates) with an
electrochemistry bench at Purdue for OER benchmarking against the NiFe-LDH standard,
so the computational rankings will face a real measurement before the project's mid-
October data freeze.

## What I'm asking for

This is a Regeneron Science Talent Search entry (due November 5, 2026); any input from
a mentor is purely advisory — all report prose stays the student's own, per STS policy.
I'm looking for a brief conversation and, if the project seems sound, occasional
feedback through the fall: specifically, whether the failure modes above are recognized
patterns in the field, whether the diagnostic protocol is sound, and where it's still
missing something.

**Contact:** Frank Cai · frankyc11223@gmail.com · ORCID 0009-0003-0041-1459
