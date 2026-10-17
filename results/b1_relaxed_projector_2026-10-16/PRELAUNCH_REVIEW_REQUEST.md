# B1 pre-launch review request (2026-10-16)

Repo: C:\Users\frank\sts-electrocatalyst (Quantum ESPRESSO 7.5 on ACCESS Anvil, wholenode, 128 ranks). Nothing in B1
has been submitted. The package below spends up to 6,144 SU (stage 1) of a 7,488 SU registered ceiling; the live
balance is 15,124.2 SU.

## Read these
- Registration (committed before any deck existed): `docs/research/b1-relaxed-projector-2026-10-16.md`
- Builder: `src/dft/b1_relaxed_projector_build.py`; its outputs `runs/b1_relaxed_projector_2026-10-16/*.in`,
  `runs/m_b1_relaxed_projector_2026-10-16_relax.txt`, `results/b1_relaxed_projector_2026-10-16/launch_spec.json`
- Sources: `runs/a0/cell/*__u715.in` (atomic) and `runs/a0/pproj_cell/*__u715_ortho.in` (ortho-atomic); their banked
  outputs `.out` beside them; the fixed-geometry scorer `src/dft/pproj_cell_readout.py` and
  `docs/figs/pproj_cell_readout.json`
- Runner (pinned, unchanged): `src/dft/research_batch_seeded.py` (stage kind "relax"), relaxation readout
  `src/dft/hea_panel_readout.py::parse_out(allow_relax=True)`
- Slurm: `anvil/102_b1_relax.slurm`; launch phases: `results/b1_relaxed_projector_2026-10-16/launch_ops.py`
  (adapted from `results/arm_c_ext_r6_2026-10-11/launch_ops.py`, which ran successfully on 10-11)
- Scorer written before outputs: `src/dft/b1_relaxed_projector_readout.py` (reads stage-2 terminal SCFs that do not
  exist yet; stage 2 is a later, separately pinned launch)

## Questions
1. Will any of the eight relaxations fail or be rejected for a reason visible now (deck edits, namelist placement of
   `nosym`, `max_seconds` vs the runner's `scf_seconds` 20,700 and the 06:00:00 Slurm limit, the 126-iteration
   ceiling, IEEE notes, projwfc after a relax, retained-density check, k-points/pools with nosym)?
2. Is the off-plane start (+0.30 A along y on the outermost adsorbate atom of *O and *OH, nosym added) a sound and
   symmetric treatment of both legs, and is anything else about the two legs unequal?
3. Does the scorer compute what the registration says (eta from terminal SCFs, bands, GATE-1, branch mismatch,
   chemistry thresholds, off-plane metrics), and is any registered reading missing or mis-implemented?
4. Does launch_ops.py still enforce everything the round-6 version did (push check, committed-bytes pins, preflight
   gates, held submit, validate fields including ArrayTaskId/ArrayTaskThrottle for a 1-8%8 array, ceilings)?
5. Anything that would waste SU or make the result uninterpretable.

Report concrete defects with file:line and the fix. Say plainly what is correct. Do not propose new machinery, hashing
schemes or extra safeguards without a defect they fix.
