# silentgate 0.1.0 core — 2026-09-13

The core implements QE output/deck readers, compressed OC20 extended-XYZ trajectories, all-step classification, per-atom direction maps, census assembly and an installable JSON CLI. The user explicitly authorized AI-assisted core implementation; the historical entrant-only assertion is preserved as superseded, not relabeled true.

## Scientific behavior

The elected run-level rule is ALL: at least one common lateral axis is exactly zero for every eligible adsorbate in every printed force step. No numerical tolerance is used for LOCKED, including signed zero. Both header-supported and force-only verdicts are emitted. Header/force disagreement is explicit, with force evidence preserved.

The negative-control rule is separately ANY: an individual eligible adsorbate with a persistent zero lateral component fails the control. The September 4 election preserved that wording. The CLI emits both `locked_force_only` (ALL run-level) and `locked_any_atom_force_only` (ANY diagnostic), plus each atom’s directional evidence. Production QE-negative and OC20 gates use the ANY pointer. The 96-row witness comparison and positive controls retain ALL.

QE’s noise floor is read per deck as `forc_conv_thr / 20`, defaulting to the QE threshold 0.001 Ry/bohr when absent. ON_PLANE requires a no-symmetry witness; a nonzero below-floor component with retained or unknown symmetry is labeled UNRESOLVED. OC20 uses no ON_PLANE or noise-floor classification: only exact-zero locking evidence and not-LOCKED, in its stored eV/angstrom precision.

Force contribution blocks are excluded from ionic total forces. NUL-spliced leading truncations are scored only when all identified adsorbate atoms survive. Missing target atoms, empty force blocks, malformed/nonfinite/underflowing force values, invalid coordinates or uncertain adsorbate identification cannot manufacture a negative control. JSON reports unscorable entries rather than dropping requested paths. Truncation and parser issues remain visible.

QE adsorbates are identified by same-metal bare-deck atom count, species sequence and the above-top-metal O/H check, not adsorbate filename tags. Ambiguous or absent bare references are UNIDENTIFIED. Exact sibling `.in` is the default companion; callers of the reader may supply an explicit deck. Unsupported coordinate conventions are refused rather than inferred. Validation on this corpus and synthetic grammar variants does not establish arbitrary QE-format coverage.

## Use

```text
python -m pip install .
silentgate --version
silentgate census --paths-from paths.txt --json
silentgate census --oc20 sample_dir --json
```

A paths file has one QE output path per line. OC20 accepts plain or xz-compressed extended XYZ, with tags and move masks from each frame. Standard output is one JSON object; every requested input receives a record. An unscorable input is data in that result, while CLI argument/read failures are nonzero process errors. Instrument source hashes are included; source-repository HEAD is null for a standalone installed wheel. A census invocation does not certify its own CI status.

## Verification

Final test totals, source hashes and control artifacts are preserved in `results/silentgate_core_2026-09-13/`. The fixed OC20 archive is SHA256-pinned, and all 500 individual compressed files are checked against the committed draw before scoring. The observed aggregate exact-zero component count is 524; incidental zero components are distinct from persistent atom/axis locks.

Local controls and hosted GitHub CI are reported separately. Hosted CI must execute on the pushed commit; local green does not imply a hosted run has completed.

## Remaining scope

The instrument does not automatically score new external-corpus predictions, change the frozen validation selection, or resolve material-performance claims. Future corpus formats need their own fixtures and identity checks. Research threshold decisions remain separate from parser implementation.
