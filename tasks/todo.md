# STS 2027 — TODO

## Status
Ideation complete; **one framing not yet locked.** Decision is gated on the four
logistics answers below.

## Decision gates (answer these to lock a framing)

- [ ] **1. Instrument access + booking lead time.** Which can you get *hands-on*
      before October, and how soon must you book?
  - Magnets / magnetocaloric → **VSM / PPMS** (make-or-break here)
  - Heat-spreader alloy → **laser-flash diffusivity** (→κ) + **dilatometry** (CTE)
  - Separation → **ICP-MS / ICP-OES**
  - **Catalysis (lead path) → potentiostat/EIS at Purdue — the only must-book instrument**
  - General **XRD, SEM/EBSD** — ✅ now covered on-site at FWM (no Purdue dependency)
- [x] **2. Fort Wayne Metals — ANSWERED (best case).** Hands-on R&D access,
      mentor-supervised: student personally runs **arc/button + vacuum-induction
      melting, wire-drawing/thermomechanical, and annealing**, with **XRD,
      SEM/EDS, metallography + hardness on-site**, and **any custom 3d-metal
      composition** allowed. ⇒ Fabrication + structural characterization are a
      self-contained, student-run, fast loop at FWM; Purdue is needed *only* for
      electrochemistry. Big independence plus; round-2 active learning is real.
- [ ] **3. DFT / first-principles experience.** Have you personally run VASP/QE +
      phonon/BTE (phono3py, ShengBTE)? For magnets: spin-orbit DFT for
      magnetocrystalline anisotropy (harder than κ)? Or lean on pretrained
      foundation MLIPs (MACE/SevenNet)?
- [ ] **4. STS sponsor + independence.** Who signs the forms, and is the *idea*
      yours vs. a slice of a mentor's grant? (STS judges probe independence hard.)

## Pick one framing
- [ ] Choose from [`docs/06-project-shortlist.md`](../docs/06-project-shortlist.md):
      **R1** magnets · **R2** magnetocaloric · **R3** REE separation · **T1**
      heat-spreader alloy · **T2** cold-plate surrogate · **T3** MLIP κ+defects.
      *(Current recommendation: R1, or R2 to keep the cooling theme.)*

## Next actions (once framing is locked)
- [ ] Optional: dispatch a focused deep-research pass on the chosen direction
      (datasets, baselines, prior art to beat).
- [ ] Stand up the ML/compute pipeline (reuse existing stack).
- [ ] Confirm + book the validation instrument and the FWM sample run.
- [ ] Define the **one baseline** to beat and the **one quantified metric**.
- [ ] Build a week-by-week plan: data frozen by **early Oct**, paper drafted Oct,
      submit **~Nov 5, 2026**.

## Timeline anchor
- Today: 2026-06-25 · Effective runway: ~3.5 months (Jul → early Oct)
- Entry due: ~Nov 5, 2026 · Scholars: Jan 2027 · Finalists: late Jan · DC: Mar 2027

## Open question to resolve
- [ ] Eligibility sanity-check: confirm 12th-grade / final-year status for the
      STS 2027 cycle (the "postdoc"/"assistant researcher" roles were described as
      *access channels*, not the entrant's own standing — confirm).
