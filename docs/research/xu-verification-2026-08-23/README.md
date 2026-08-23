# Xu deposit verification — A9.7 act 1 + act 2, 2026-08-23

Executed after the A9 DOI line existed (10.5281/zenodo.22072991, docs/43 A9.7). Machine:
Purdue Anvil (ACCESS CHE260157, STS-scope). Artefacts stay outside git: the zip lives at
`$SCRATCH/sts/corpora/xu/rutile-OER-v1.0.zip` with a durability copy at
`$PROJECT/corpora/xu/` (scratch is purge-eligible).

## Act 1 — zip fetch + listing comparison (a listing operation, A9.3.1 / A9.6)

- Fetched `rutile-OER-v1.0.zip` from 10.5281/zenodo.12635: **572,402,421 bytes, md5
  `e193c56cf17c6d98827bbb19752d04b3`** — matches the Zenodo record's stated checksum.
- The zip's single top-level directory is **`zhongnanxu-rutile-OER-c4cb892/`** — the
  Zenodo deposit IS the GitHub mirror snapshot at the same commit `c4cb892...` that
  `xu_tree.json` (docs/research/2026-08-15-sampling/) hashed.
- Comparison per the registered unit (`xu_zip_compare.py`, report
  `xu_zip_compare_report.json`): **6,989 zip file entries vs 6,989 tree blobs — all
  paths common, 0 only-in-zip, 0 only-in-tree, 0 size mismatches; 815/815 `pwscf.out`
  git-blob SHA-1s recomputed from the zip bytes match the mirror listing; 0 mismatches.**
- Consequence (registered in A9.3.1): the zip population and the hashed mirror listing
  coincide, so every count formerly carried "per the GitHub mirror at `c4cb892`" is now
  a count of the Zenodo zip itself. The metal directories sit under `supporting-data/`
  inside the snapshot (e.g. `supporting-data/RuO2/Eads-4-layers/...`); `xu_tree.json`
  paths carry the same `supporting-data/` prefix, so the A9.3.1 counts are unchanged.

## Act 2 — header-format validation (the first parse, A9.1 / A9.7)

Metal chosen: **RuO₂** — the metal already seen by record (A9.0's cached pair), so the
six blind metals of P-XU clause (iii) stay unread. The four named paths (zip-internal),
each read only to its symmetry-ops header line:

| path (under `zhongnanxu-rutile-OER-c4cb892/`) | header line found | form |
|---|---|---|
| `supporting-data/RuO2/Eads-4-layers/bare/pwscf.out` | `      4 Sym. Ops. (no inversion) found` (l.101) | count-first |
| `supporting-data/RuO2/Eads-4-layers/O-relax/pwscf.out` | `      4 Sym. Ops. (no inversion) found` (l.99) | count-first |
| `supporting-data/RuO2/Eads-4-layers/OH-relax/pwscf.out` | `      2 Sym. Ops. (no inversion) found` (l.110) | count-first |
| `supporting-data/RuO2/Eads-4-layers/OOH-relax/pwscf.out` | `      2 Sym. Ops. (no inversion) found` (l.111) | count-first |

**Outcome:** all four are the count-first form; the older docstring form
(`Sym. Ops., with inversion, found N`) was not encountered. No reader fix is needed;
the registered both-forms-by-regex rule stands, with the form logged per file as
registered. (The op counts and the OOH-relax file size 1,328,638 B match the one
cached 2014 output — consistency, not new census content.)
