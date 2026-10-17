"""Build B1, stage 1: eight U = 7.15 eV relaxations of the 2x1 CrO2(110) states under both Hubbard projectors.

Design of record: docs/research/b1-relaxed-projector-2026-10-16.md (Frank, 2026-10-16: "Go ahead").

Each relaxation deck is its banked single-point deck (runs/a0/cell, atomic; runs/a0/pproj_cell, ortho-atomic) with
only these lines changed, identically in both legs:
  - prefix -> the job name, calculation 'scf' -> 'relax', max_seconds -> MAX_SECONDS;
  - *O and *OH (the __mir decks): nosym = .true. added as the last &SYSTEM line, and the outermost adsorbate atom
    (O of *O, H of *OH) moved +0.30 A along y, off the y = 1.56305954 A mirror (build_s3.py:135 minimum |dy|).
The clean slab and the escaped *OOH keep their banked symmetry flags and coordinates. The builder refuses any other
difference, checks that each atomic/ortho pair still differs only in prefix and HUBBARD card, and writes the decks,
the manifest and launch_spec.json once (it refuses to overwrite).

Usage: python src/dft/b1_relaxed_projector_build.py [--check]
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "2026-10-16"
TAG = f"b1_relaxed_projector_{DATE}"
RUN_DIR_REL = TAG                                   # under runs/
RUN_DIR = ROOT / "runs" / RUN_DIR_REL
MANIFEST_REL = f"runs/m_{TAG}_relax.txt"
RESULTS_REL = f"results/{TAG}"
SPEC_REL = f"{RESULTS_REL}/launch_spec.json"
DESIGN = "docs/research/b1-relaxed-projector-2026-10-16.md"
DECISION = 'Frank, 2026-10-16: "Go ahead" (B1 of the DFT contingency plan)'
EXCLUDE = "a024,a049,a050,a088,a196,a220,a223,a171,a120,a200"   # as in the round-6 spec

STEMS = ["ref__2x1v", "s0_O__2x1v_mir", "s0_OH__2x1v_mir", "s0_OOH__2x1v_escape"]
LEGS = {"atomic": ("runs/a0/cell", "{stem}__u715.in", "HUBBARD (atomic)"),
        "ortho": ("runs/a0/pproj_cell", "{stem}__u715_ortho.in", "HUBBARD (ortho-atomic)")}
MIRROR_Y = "1.56305954"
KICK_A = 0.30
KICK = {"s0_O__2x1v_mir": "O", "s0_OH__2x1v_mir": "H"}   # outermost adsorbate atom, moved off the mirror
NOSYM_ADD = set(KICK)

WALL_MINUTES = 360                                  # Slurm --time per task
PROJECTION_SECONDS = 600
SCF_SECONDS = WALL_MINUTES * 60 - PROJECTION_SECONDS - 300   # runner's pw.x ceiling
MAX_SECONDS = 20000                                 # pw.x stops itself (and saves) before the runner's ceiling
NK = 8
RELAX_MAX_ITERATIONS = 126
STAGE_CEILINGS = {"b1_relax": 8 * WALL_MINUTES * 128 // 60, "b1_scf": 768, "repair": 576}
CEILING = 7488
SPENT_NOTE = "live mybalance 2026-10-17 03:43Z: che260157 CPU balance 15,124.2 SU"

SRC_PINS = ["src/dft/research_batch_seeded.py", "src/dft/projection_qc.py", "src/dft/hea_panel_readout.py",
            "src/dft/hea_geometry.py"]
R6_SPEC = ROOT / "results/arm_c_ext_r6_2026-10-11/launch_spec.json"   # QE binaries and pseudopotential md5s


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def job_name(stem, leg):
    return f"{stem}__u715_{leg}_relax"


def set_line(text, key, value, count=1):
    new, n = re.subn(rf"(?m)^(\s*{key}\s*=\s*).*$", lambda m: m[1] + value, text)
    assert n == count, f"{key}: {n} matches, expected {count}"
    return new


def add_nosym(text):
    assert not re.search(r"(?m)^\s*nosym\s*=", text), "deck already sets nosym"
    m = re.search(r"(?ms)^&SYSTEM\s*\n.*?^/\s*$", text)
    assert m, "no &SYSTEM namelist"
    close = m.end() - len(m.group(0).splitlines()[-1])
    return text[:close] + "  nosym = .true.\n" + text[close:]


def kick(text, species):
    """Move the last ATOMIC_POSITIONS row of `species` (it must sit on the mirror) by +KICK_A along y."""
    block = re.search(r"(?ms)^ATOMIC_POSITIONS angstrom\s*\n(.*?)^K_POINTS", text)
    assert block, "no ATOMIC_POSITIONS angstrom block"
    rows = block.group(1).splitlines()
    idx = max(i for i, r in enumerate(rows) if r.split() and r.split()[0] == species)
    assert idx == len(rows) - 1, "kicked atom is not the last (outermost) row"
    zs = [float(r.split()[3]) for r in rows if r.split()]
    assert float(rows[idx].split()[3]) == max(zs), "kicked atom is not the highest atom"
    parts = rows[idx].split()
    assert parts[2] == MIRROR_Y, f"{species} row is not on the mirror: {rows[idx]!r}"
    assert parts[4:] == ["1", "1", "1"], "kicked atom must be free"
    y = float(parts[2]) + KICK_A
    new_row = f"  {parts[0]}  {parts[1]}  {y:.8f}  {parts[3]}  {' '.join(parts[4:])}"
    rows[idx] = new_row
    start = block.start(1)
    return text[:start] + "\n".join(rows) + "\n" + text[block.end(1):], (parts, new_row.split())


def changed_lines(a, b):
    return [l for l in difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm="", n=0)
            if l[:1] in "+-" and not l.startswith(("+++", "---"))]


def build_deck(stem, leg):
    src_dir, pattern, card = LEGS[leg]
    src = ROOT / src_dir / pattern.format(stem=stem)
    raw = src.read_bytes()
    assert b"\r" not in raw
    text = raw.decode("utf-8")
    if not text.endswith("\n"):
        text += "\n"
    assert text.count(card + "\n") == 1 and "U Cr-3d 7.1500" in text, f"{src}: Hubbard card not as banked"
    name = job_name(stem, leg)
    out = set_line(text, "prefix", f"'{name}'")
    out = set_line(out, "calculation", "'relax'")
    out = set_line(out, "max_seconds", str(MAX_SECONDS))
    moved = None
    if stem in NOSYM_ADD:
        out = add_nosym(out)
    if stem in KICK:
        out, moved = kick(out, KICK[stem])
    assert out.count(card + "\n") == 1 and "U Cr-3d 7.1500" in out, "Hubbard card lost"
    assert re.findall(r"(?m)^\s*nat\s*=\s*(\d+)", out) == re.findall(r"(?m)^\s*nat\s*=\s*(\d+)", text)
    allowed = 3 + (1 if stem in NOSYM_ADD else 0) + (1 if stem in KICK else 0)
    diff = changed_lines(text, out)
    added = [l for l in diff if l.startswith("+")]
    assert len(added) == allowed, f"{name}: {len(added)} changed lines, expected {allowed}: {added}"
    return src, name, out, moved


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="build in memory and print, write nothing")
    args = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    decks, report = {}, []
    for stem in STEMS:
        pair = {}
        for leg in LEGS:
            src, name, text, moved = build_deck(stem, leg)
            pair[leg] = (src, name, text)
            decks[name] = (src, text, moved)
        # the paired legs still differ in prefix and HUBBARD card only
        d = changed_lines(pair["atomic"][2], pair["ortho"][2])
        assert len(d) == 4 and all(("prefix" in l) or ("HUBBARD" in l) for l in d), f"{stem}: pair diff {d}"
        s = changed_lines((ROOT / LEGS["atomic"][0] / LEGS["atomic"][1].format(stem=stem)).read_text("utf-8"),
                          (ROOT / LEGS["ortho"][0] / LEGS["ortho"][1].format(stem=stem)).read_text("utf-8"))
        assert len(s) == 4, f"{stem}: banked pair no longer differs in exactly two lines"

    for name, (src, text, moved) in decks.items():
        line = f"{name}: from {src.relative_to(ROOT).as_posix()}"
        if moved:
            line += f"; {moved[0][0]} y {moved[0][2]} -> {moved[1][2]}"
        report.append(line)
    print("\n".join(report))
    print(f"stage ceiling {STAGE_CEILINGS['b1_relax']} SU; launch ceiling {CEILING} SU; {SPENT_NOTE}")
    if args.check:
        return 0

    assert not RUN_DIR.exists(), f"refusing to overwrite {RUN_DIR}"
    results = ROOT / RESULTS_REL
    assert not (results / "launch_spec.json").exists(), "refusing to overwrite the spec"
    RUN_DIR.mkdir(parents=True)
    results.mkdir(parents=True, exist_ok=True)
    jobs = []
    for name, (src, text, moved) in decks.items():
        path = RUN_DIR / f"{name}.in"
        with path.open("x", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        jobs.append(dict(dir=RUN_DIR_REL, job=name, sha256=sha(path), nk=NK, scf_seconds=SCF_SECONDS,
                         projection_seconds=PROJECTION_SECONDS, max_iterations=RELAX_MAX_ITERATIONS,
                         recipe="relax", role="b1", source_deck=src.relative_to(ROOT).as_posix(),
                         source_sha256=sha(src),
                         off_plane_kick=(None if not moved else
                                         dict(atom=moved[0][0], y_from=moved[0][2], y_to=moved[1][2]))))
    manifest = ROOT / MANIFEST_REL
    with manifest.open("x", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# APPROVED 2026-10-16: {DESIGN} (Frank: \"Go ahead\")\n")
        fh.write("# B1 stage 1: eight U = 7.15 eV relaxations of the 2x1 CrO2(110) slab, *O, *OH and escaped *OOH "
                 "under the atomic and ortho-atomic projectors; terminal SCFs are a separate stage; no automatic "
                 "retries.\n")
        fh.write(f"# SUBMIT WITH EXCLUDE={EXCLUDE}\n# NP=128 NCONC=1\n")
        for j in jobs:
            fh.write(f"{j['dir']} {j['job']} .in {j['nk']}\n")
    r6 = json.loads(R6_SPEC.read_text(encoding="utf-8"))
    files = {f"runs/{j['dir']}/{j['job']}.in": j["sha256"] for j in jobs}
    files[MANIFEST_REL] = sha(manifest)
    for rel in SRC_PINS:
        files[rel] = sha(ROOT / rel)
    spec = dict(schema="research-batch-2026-09-16", np=128, exclusions=EXCLUDE, date=DATE, design=DESIGN,
                decision_ref=DECISION,
                allocation=dict(account="che260157", partition="wholenode", cores_per_task=128,
                                balance_note=SPENT_NOTE, launch_ceiling_cpu_su=CEILING,
                                stage_ceilings_cpu_su=STAGE_CEILINGS),
                qe_binaries_sha256=r6["qe_binaries_sha256"],
                files=dict(sorted(files.items())),
                pseudo_md5={k: r6["pseudo_md5"][k] for k in
                            ("cr_pbe_v1.5.uspp.F.UPF", "O.pbe-n-kjpaw_psl.0.1.UPF", "H.pbe-rrkjus_psl.1.0.0.UPF")},
                stages={"b1_relax": dict(kind="relax", manifest=MANIFEST_REL, concurrency=8,
                                         wall_minutes=WALL_MINUTES, jobs=jobs)})
    with (results / "launch_spec.json").open("x", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(spec, indent=2) + "\n")
    print(f"wrote {len(jobs)} decks, {MANIFEST_REL}, {SPEC_REL} (sha256 {sha(results / 'launch_spec.json')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
