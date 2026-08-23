# OC20 val_id negative-control corpus — A9.7 act 3, 2026-08-23

Executed after the A9 DOI line existed (10.5281/zenodo.22072991), in registered order
(after act 1 and act 2). Machine: Purdue Anvil (ACCESS CHE260157, STS-scope). Files stay
outside git per A9.2.1: tar + drawn sample at `$SCRATCH/sts/corpora/oc20/` with a
durability copy at `$PROJECT/corpora/oc20/` (scratch is purge-eligible).

## The artefact, as downloaded

- `is2res_val_id_trajectories.tar` from
  `https://dl.fbaipublicfiles.com/opencatalystproject/data/is2res_val_id_trajectories.tar`
  — **6,296,166,400 bytes, md5 `fcb71363018fb1e7127db2500e39e11a` — matches the md5
  registered in A9.2.1** (copied there from fairchem's DATASET.md before deposit).
  Licence CC-BY-4.0 as registered.
- Contents: **24,945 member files**, all `is2res_val_id_trajectories/is2res_val_id_trajectories/random*.extxyz.xz`
  (xz-compressed extended-XYZ relaxation trajectories). The documentation says
  "~25K trajectories" with an update note revising system counts 24,946 → 24,943; the
  member count found is recorded here as the fact of the artefact.

## The registered draw (N = 500, first-500 ascending lexical)

- `first500.txt` — the first 500 member names in ascending lexical order (the registered
  rule; sort of full member paths ≡ sort of basenames, single directory).
- `first500.SHA256SUMS` — sha256 manifest of the 500 extracted files (the committed
  manifest A9.2.1 requires). Extraction dir: `val_id_first500/` on both Anvil copies.
- No re-draw, no substitution, no second sample (A9.2.1). Any enlargement is additive
  and disclosed.

## Stored force precision (the dated fact A9.2.1 requires)

Format observation only — no census was run (`oc20_precision_check.py`; the census is
act 4, entrant's `silentgate`):

- Frames carry `Properties=species:S:1:pos:R:3:move_mask:L:1:tags:I:1:forces:R:3` —
  per-atom species, position, **`move_mask` (the FixAtoms constraint mask)**, **`tags`
  (integer; adsorbate = 2)**, forces.
- **Forces are fixed-point decimal TEXT with exactly 8 digits after the point, in eV/Å**
  (extxyz convention). Verified on every force component of 5 of the 500 drawn
  trajectories (draw indices 1, 100, 250, 400, 500): 141,435 components, all matching
  `^-?\d+\.\d{8}$`; Properties string identical in all 5.
- Consequence for the LOCKED criterion: "exactly zero at the stored precision" means the
  literal token `0.00000000` (or `-0.00000000`). This bounds what the control certifies
  exactly as A9.2.1's over-reading guard states.
- Forces are stored RAW (a `move_mask F` atom shows nonzero force components), so the
  constrained-atom exclusion is done by the mask column, not assumed from zeros; the
  `tags` column supplies the adsorbate rule (`tags == 2`) without ASE inference.
  (A9.1 registered the OC20 reader against ASE `.traj`; the artefact is extxyz text —
  same reader contract, `tags`/constraint semantics carried in-file. Reader detail, not
  a threshold.)
