"""Build the B1 repair: continue the failed stage-1 relaxations with stronger SCF damping (registered 2026-10-18).

Registration: docs/research/b1-relaxed-projector-2026-10-16.md, "Repair". Each deck is its stage-1 relaxation deck
with only the prefix, max_seconds, the mixing lines and the ATOMIC_POSITIONS coordinates changed. The ortho-atomic
adsorbate legs restart from the last geometry their stage-1 output printed (the geometry of the stalled SCF); the
atomic *OH leg restarts from its final coordinates. Species order and every if_pos flag are kept from the deck, and
fixed atoms must not have moved. Writes the decks, one manifest per array and launch_spec.json once (refuses to
overwrite).

Usage: python src/dft/b1_repair_build.py [--check]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELAX_SPEC = ROOT / "results/b1_relaxed_projector_2026-10-16/launch_spec.json"
TAG = "b1_repair_2026-10-18"
RESULTS_REL = f"results/{TAG}"
PROJECTION_SECONDS = 600
SRC_PINS = ["src/dft/research_batch_seeded.py", "src/dft/projection_qc.py", "src/dft/hea_panel_readout.py",
            "src/dft/hea_geometry.py"]
WALL_MINUTES = {"b1r_ortho": 480, "b1r_short": 60}
RECIPES = {"t1": {"mixing_mode": "'local-TF'", "mixing_beta": "0.1", "mixing_ndim": "16"},
           "t2": {"mixing_mode": "'plain'", "mixing_beta": "0.1", "mixing_ndim": "16"}}
# (stage-1 job, recipe, array, restart geometry, stage-1 receipt it must carry)
REPAIRS = [
    ("s0_OOH__2x1v_escape__u715_ortho_relax", "t1", "b1r_ortho", "last", ("REJECTED", "SCF iteration ceiling")),
    ("s0_O__2x1v_mir__u715_ortho_relax", "t1", "b1r_ortho", "last", ("REJECTED", "SCF iteration ceiling")),
    ("s0_OH__2x1v_mir__u715_ortho_relax", "t1", "b1r_ortho", "last", ("REJECTED", "SCF iteration ceiling")),
    ("s0_OH__2x1v_mir__u715_atomic_relax", "t1", "b1r_short", "final",
     ("REJECTED", "relaxation not complete/clean: REJECTED")),
    ("s0_OH__2x1v_mir__u715_atomic_relax", "t2", "b1r_short", "final",
     ("REJECTED", "relaxation not complete/clean: REJECTED")),
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rows_of(block):
    rows = [r.split() for r in block.splitlines() if r.strip()]
    return [(r[0], [float(x) for x in r[1:4]], r[4:]) for r in rows]


def restart_geometry(out_text, source):
    if source == "final":
        m = re.search(r"Begin final coordinates\s*\n(?:.*\n)*?ATOMIC_POSITIONS \(angstrom\)\s*\n(.*?)\n"
                      r"End final coordinates", out_text, re.S)
        assert m, "no final-coordinates block"
        return rows_of(m.group(1))
    blocks = re.findall(r"(?m)^ATOMIC_POSITIONS \(angstrom\)\s*\n(.*?)\n\s*\n", out_text, re.S)
    assert blocks, "no printed geometry"
    assert "Begin final coordinates" not in out_text, "a stalled run must not have final coordinates"
    return rows_of(blocks[-1])


def build(job, recipe, source, scf_seconds):
    deck = ROOT / "runs" / job["dir"] / (job["job"] + ".in")
    text = deck.read_text(encoding="utf-8")
    assert sha(deck) == job["sha256"], "stage-1 deck changed"
    geometry = restart_geometry((ROOT / "runs" / job["dir"] / (job["job"] + ".out")).read_text(
        encoding="utf-8", errors="strict"), source)
    block = re.search(r"(?ms)^ATOMIC_POSITIONS angstrom\s*\n(.*?)^K_POINTS", text)
    rows = [r for r in block.group(1).splitlines() if r.split()]
    assert len(rows) == len(geometry), "atom count differs"
    new_rows = []
    for row, (sym, xyz, flags) in zip(rows, geometry):
        parts = row.split()
        assert parts[0] == sym, f"species order differs: {parts[0]} vs {sym}"
        if parts[4:] == ["0", "0", "0"]:
            assert flags == ["0", "0", "0"], "fixed flags differ"
            assert all(abs(a - float(b)) < 1e-6 for a, b in zip(xyz, parts[1:4])), "a fixed atom moved"
        else:
            assert not flags, "a free atom printed with flags"
        new_rows.append(f"  {sym}  {xyz[0]:.8f}  {xyz[1]:.8f}  {xyz[2]:.8f}  {' '.join(parts[4:])}".rstrip())
    name = f"{job['job']}_{recipe}"
    new = text[:block.start(1)] + "\n".join(new_rows) + "\n" + text[block.end(1):]
    edits = {"prefix": f"'{name}'", "max_seconds": str(scf_seconds - 700),
             "mixing_mode": RECIPES[recipe]["mixing_mode"], "mixing_beta": RECIPES[recipe]["mixing_beta"]}
    for key, value in edits.items():
        new, n = re.subn(rf"(?m)^(\s*{key}\s*=\s*).*$", lambda m, v=value: m[1] + v, new)
        assert n == 1, key
    assert not re.search(r"(?m)^\s*mixing_ndim\s*=", new), "mixing_ndim already set"
    new, n = re.subn(r"(?m)^(\s*)(mixing_beta\s*=.*)$", lambda m: f"{m[1]}{m[2]}\n{m[1]}mixing_ndim = "
                     + RECIPES[recipe]["mixing_ndim"], new)
    assert n == 1
    # Only the registered lines may differ from the stage-1 deck.
    old_lines, new_lines = text.splitlines(), new.splitlines()
    allowed = re.compile(r"^\s*(prefix|max_seconds|mixing_mode|mixing_beta|mixing_ndim)\s*=")
    start = next(i for i, s in enumerate(old_lines) if s.startswith("ATOMIC_POSITIONS"))
    head_old = [s for s in old_lines[:start] if not allowed.match(s)]
    head_new = [s for s in new_lines[:start + 1] if not allowed.match(s)]
    assert head_old == head_new, "a non-registered header line differs"
    assert old_lines[start + 1 + len(rows):] == new_lines[start + 2 + len(rows):], "a card after the positions differs"
    return name, new


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    relax = json.loads(RELAX_SPEC.read_text(encoding="utf-8"))
    by_name = {j["job"]: j for j in relax["stages"]["b1_relax"]["jobs"]}
    built = []
    for stage1, recipe, array, source, (status, reason) in REPAIRS:
        job = by_name[stage1]
        rec = json.loads((ROOT / "runs" / job["dir"] / (stage1 + ".qc.json")).read_text(encoding="utf-8"))
        assert (rec.get("status"), rec.get("reason")) == (status, reason), f"{stage1}: unexpected stage-1 receipt"
        scf_seconds = WALL_MINUTES[array] * 60 - 900
        name, text = build(job, recipe, source, scf_seconds)
        built.append((job, name, text, recipe, array, source, scf_seconds))
        print(f"{name}: {array}, restart from {source} geometry of {stage1} ({rec['reason']})")
    if args.check:
        return 0
    results = ROOT / RESULTS_REL
    assert not (results / "launch_spec.json").exists(), "refusing to overwrite the spec"
    results.mkdir(parents=True, exist_ok=True)
    stages, files = {}, {}
    for array, wall in WALL_MINUTES.items():
        jobs = []
        for job, name, text, recipe, arr, source, scf_seconds in built:
            if arr != array:
                continue
            path = ROOT / "runs" / job["dir"] / f"{name}.in"
            with path.open("x", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
            out = ROOT / "runs" / job["dir"] / (job["job"] + ".out")
            jobs.append(dict(dir=job["dir"], job=name, sha256=sha(path), nk=job["nk"], scf_seconds=scf_seconds,
                             projection_seconds=PROJECTION_SECONDS, max_iterations=126, recipe="relax", role="b1",
                             mixing=recipe, restart_geometry=source,
                             source_relaxation=f"runs/{job['dir']}/{job['job']}.out", source_relaxation_sha256=sha(out),
                             stage1_deck=f"runs/{job['dir']}/{job['job']}.in", stage1_deck_sha256=job["sha256"]))
            files[f"runs/{job['dir']}/{name}.in"] = sha(path)
        manifest_rel = f"runs/m_{TAG}_{array}.txt"
        with (ROOT / manifest_rel).open("x", encoding="utf-8", newline="\n") as fh:
            fh.write("# APPROVED 2026-10-18: docs/research/b1-relaxed-projector-2026-10-16.md, Repair (Frank: \"Repair\")\n")
            fh.write(f"# B1 repair, array {array}: continuations of failed stage-1 legs; no automatic retries.\n")
            fh.write(f"# SUBMIT WITH EXCLUDE={relax['exclusions']}\n# NP=128 NCONC=1\n")
            for j in jobs:
                fh.write(f"{j['dir']} {j['job']} .in {j['nk']}\n")
        files[manifest_rel] = sha(ROOT / manifest_rel)
        stages[array] = dict(kind="relax", manifest=manifest_rel, concurrency=len(jobs), wall_minutes=wall, jobs=jobs)
    for rel in SRC_PINS:
        files[rel] = sha(ROOT / rel)
    ceilings = {a: len(s["jobs"]) * s["wall_minutes"] * 128 // 60 for a, s in stages.items()}
    spec = dict(schema="research-batch-2026-09-16", np=128, exclusions=relax["exclusions"], date="2026-10-18",
                design=relax["design"], decision_ref='Frank, 2026-10-18: "Repair" (B1 stage 1 unresolved)',
                allocation=dict(account="che260157", partition="wholenode", cores_per_task=128,
                                launch_ceiling_cpu_su=sum(ceilings.values()), stage_ceilings_cpu_su=ceilings,
                                b1_total_ceiling_cpu_su=relax["allocation"]["launch_ceiling_cpu_su"],
                                b1_stage1_billed_cpu_su=1653.2),
                qe_binaries_sha256=relax["qe_binaries_sha256"], files=dict(sorted(files.items())),
                pseudo_md5=relax["pseudo_md5"], stages=stages)
    with (results / "launch_spec.json").open("x", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(spec, indent=2) + "\n")
    print(f"wrote {len(built)} decks, {len(stages)} manifests, {RESULTS_REL}/launch_spec.json "
          f"(sha256 {sha(results / 'launch_spec.json')}); ceilings {ceilings}, total {sum(ceilings.values())} SU")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
