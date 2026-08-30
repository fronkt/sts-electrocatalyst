#!/usr/bin/env python3
"""Repair: add the TiO2 s0_OOH record to runs/probe/Ti_audit/probe_manifest.json.

WHY THIS EXISTS (wave-5 audit finding, 2026-08-29)
--------------------------------------------------
`build_a0main_w3b.build_base()` wrote `runs/probe/Ti_audit/s0_OOH__base.in`
through `probe_decks.write_probe` + a direct file write, deliberately bypassing
`probe_decks.cmd_build` -- which is the ONLY code path that appends a job record
to `probe_manifest.json`. The builder compensated in
`runs/a0/main/manifest.json["tranche_3b"]` and nowhere else, so the probe
manifest listed three jobs (slab, s0_OH, s0_O) while four primary decks sat on
disk.

Two measured consequences, both reproducible before this repair:

  1. `probe_eta.py` enumerates work exclusively from `man["jobs"]`, so
     `PYTHONPATH=src python src/dft/probe_eta.py runs/probe/Ti_audit` ran GATE 1
     over only slab/s0_O/s0_OH and then printed "No variant has a complete
     slab + OH + O + OOH set yet." -- with a converged `s0_OOH__base.out`
     sitting in that directory. The state that DECIDES A7.3 escaped the gate.

  2. `a0main_readout.py` banks a `control_note` saying the genuine extraction
     control "lives in ... `probe_manifest` `relax_reference_ev` for Mn/Fe/Ti".
     For Ti's s0_OOH there was no record and therefore no `relax_reference_ev`,
     so for the one state whose re-anchoring provenance is the tranche's
     headline, the named control did not exist.

WHAT IT DOES
------------
Re-derives the record with the SAME `probe_decks` functions `cmd_build` would
have used -- `parse_final_coordinates` (geometry provenance),
`relax_final_energy_ev` (the relax reference), `vacuum_report` (vac gap) -- from
`runs/Ti_slab/s0_OOH_r3.out`, the re-anchored relaxation selected by tranche
2c's exactly-one-converged rule.

IDEMPOTENT. If the record is already present it is RECOMPUTED and compared
field by field; any disagreement is fatal. Re-running is therefore a
verification, never a second append.
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(HERE))

import probe_decks as P                                          # noqa: E402

SRC_RELAX = os.path.join(ROOT, "runs", "Ti_slab", "s0_OOH_r3.out")
DST = os.path.join(ROOT, "runs", "probe", "Ti_audit")
DECK = os.path.join(DST, "s0_OOH__base.in")
MANIFEST = os.path.join(DST, "probe_manifest.json")

NOTE_SUFFIX = (
    " | WAVE-5: the s0_OOH record was added 2026-08-29 by "
    "src/dft/add_ti_ooh_manifest.py. build_a0main_w3b.py wrote s0_OOH__base.in "
    "through write_probe directly rather than cmd_build, which is the only path "
    "that appends here, so the state that DECIDES A7.3 was absent from this "
    "manifest and invisible to probe_eta.py's GATE 1. Geometry provenance and "
    "relax_reference_ev are re-derived from runs/Ti_slab/s0_OOH_r3.out by the "
    "same probe_decks functions cmd_build would have used.")


def build_record() -> dict:
    for p in (SRC_RELAX, DECK, MANIFEST):
        if not os.path.exists(p):
            sys.exit("missing required input: %s" % p)
    deck = P.parse_input_deck(DECK)
    pos, prov = P.parse_final_coordinates(SRC_RELAX)
    if prov != "final":
        sys.exit("s0_OOH_r3 geometry provenance is %r, not 'final' -- the "
                 "relaxation did not converge and no record may be written"
                 % prov)
    cell = deck["cell"]
    return dict(job="s0_OOH", variant="base", file="s0_OOH__base.in",
                geometry_provenance=prov,
                relax_reference_ev=P.relax_final_energy_ev(SRC_RELAX),
                emaxpos=None, eopreg=None, cell_c=cell[2][2],
                vac_gap=P.vacuum_report(pos, cell)[2])


def main() -> None:
    rec = build_record()
    man = json.load(io.open(MANIFEST, encoding="utf-8"))
    existing = [j for j in man["jobs"] if j.get("job") == "s0_OOH"]
    if existing:
        bad = [k for k, v in rec.items() if existing[0].get(k) != v]
        if bad:
            sys.exit("s0_OOH record already present but DISAGREES on %s:\n"
                     "  on disk:   %s\n  re-derived: %s"
                     % (bad, {k: existing[0].get(k) for k in bad},
                        {k: rec[k] for k in bad}))
        print("s0_OOH record already present and re-derives identically "
              "(%d fields checked) -- nothing to do." % len(rec))
        return
    man["jobs"].append(rec)
    if NOTE_SUFFIX not in man.get("note", ""):
        man["note"] = man.get("note", "") + NOTE_SUFFIX
    io.open(MANIFEST, "w", encoding="utf-8", newline="\n").write(
        json.dumps(man, indent=1) + "\n")
    print("appended s0_OOH: %s" % json.dumps(rec))


if __name__ == "__main__":
    main()
