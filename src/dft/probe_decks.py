#!/usr/bin/env python3
"""Fixed-geometry probe decks: isolate ONE protocol variable at a time (docs/41).

Why this exists
---------------
`docs/32-anchor-gate-verdict.md` records a FAILED pre-registered external gate:

    RuO2(110)  eta = 0.787 V   literature 0.37-0.42 V   error +0.39 V
    IrO2(110)  eta = 0.781 V   literature 0.54-0.58 V   error +0.22 V

Both errors are POSITIVE and both anchor chains converged first pass (fmax
0.0014-0.0019 Ry/au), so this is method error, not a convergence artifact. The
production protocol departs from the project's own spec in docs/22 in several
places at once, and a full re-relaxation of every variant is unaffordable on the
remaining budget.

The cheap, decisive move is that the four states are ALREADY RELAXED. Adding a
perturbation and re-running a single SCF step at the *same* geometry gives the
leading-order change in every Delta-G, hence in eta, for cents instead of dollars.
Geometry relaxation under the perturbation is a second-order correction on top of
that -- this is a SENSITIVITY analysis, and every artifact it writes says so.

The control matters as much as the perturbations. Variant `base` re-runs the
unperturbed SCF at the extracted geometry; it MUST reproduce the relaxation's own
final energy to within SCF noise. If it does not, the coordinate extraction is
wrong and every other variant in the batch is meaningless. `probe_eta.py` refuses
to score a batch whose `base` control has drifted.

Variants
--------
base         control; no change. Validates extraction.
dipole       sawtooth dipole correction (tefield/dipfield, edir=3, eamp=0). The
             adslabs are adsorbed on ONE face, so they carry a net dipole that
             the periodic images talk to. docs/22:76 specifies this; production
             omitted it to match a UMA protocol.
vacXX        cell c stretched to XX Angstrom, slab recentred. Production runs a
             FIXED c = 25.41 A, so the true adsorbate-to-image gap is
             adsorbate-DEPENDENT: 16.58 A bare, 13.98 *OH, 14.73 *O, 12.83 *OOH.
             That differential is exactly the kind of error eta does not cancel.
dipole+vacXX both, to separate additive from cooperative.
uXX          Hubbard U scaled to XX x the production value, for the 3d metals.
             The headline result (Cr 0.491, Co 0.544 beating both noble anchors)
             crosses the PBE+U / plain-PBE boundary, so its U-sensitivity is a
             project-falsifying test, not a refinement.

Usage
-----
  PYTHONPATH=src python src/dft/probe_decks.py build runs/Ru_anchor \
      --variants base dipole vac32 dipole+vac32 --outdir runs/probe/Ru
  PYTHONPATH=src python src/dft/probe_decks.py build runs/Cr_slab \
      --variants base u0.0 u0.5 u1.35 --outdir runs/probe/Cr
"""
from __future__ import annotations

import argparse
import json
import os
import re

RY_EV = 13.605693122

_ELEMENT_RE = re.compile(r"^[A-Z][a-z]?$")


# ---------------------------------------------------------------- parsing ---

def parse_input_deck(path: str) -> dict:
    """Pull the pieces of a production .in we need to rebuild it faithfully."""
    txt = open(path).read()

    def scalar(key, cast=float, default=None):
        m = re.search(rf"^\s*{key}\s*=\s*([^\s,!/]+)", txt, re.M | re.I)
        if not m:
            return default
        raw = m.group(1).strip().strip("'\"")
        if cast is float:
            return float(raw.replace("d", "e").replace("D", "e"))
        return cast(raw)

    cell = []
    m = re.search(r"CELL_PARAMETERS\s+\S+\s*\n((?:\s*[-\d.eE+]+\s+[-\d.eE+]+\s+[-\d.eE+]+\s*\n){3})", txt)
    if m:
        for line in m.group(1).strip().split("\n"):
            cell.append([float(x) for x in line.split()])

    species = []
    m = re.search(r"ATOMIC_SPECIES\s*\n((?:\s*\S+\s+[\d.]+\s+\S+\s*\n)+)", txt)
    if m:
        for line in m.group(1).strip().split("\n"):
            p = line.split()
            species.append((p[0], float(p[1]), p[2]))

    positions, flags = [], []
    m = re.search(r"ATOMIC_POSITIONS\s+\S*\s*\n((?:.*\n)+?)(?=K_POINTS|CELL_PARAMETERS|HUBBARD|\Z)", txt)
    if m:
        for line in m.group(1).rstrip().split("\n"):
            p = line.split()
            if len(p) >= 4 and _ELEMENT_RE.match(p[0]):
                positions.append((p[0], float(p[1]), float(p[2]), float(p[3])))
                flags.append(" ".join(p[4:7]) if len(p) >= 7 else "1 1 1")

    kpts = None
    m = re.search(r"K_POINTS\s+(\S+)\s*\n?(?:\s*([\d\s]+)\n)?", txt)
    if m:
        kpts = (m.group(1), (m.group(2) or "").split())

    hubbard = []
    m = re.search(r"HUBBARD\s*\([^)]*\)\s*\n((?:\s*U\s+\S+\s+[\d.]+\s*\n)+)", txt)
    if m:
        for line in m.group(1).strip().split("\n"):
            p = line.split()
            hubbard.append((p[1], float(p[2])))

    mags = {}
    for mm in re.finditer(r"starting_magnetization\((\d+)\)\s*=\s*([-\d.eE+]+)", txt):
        mags[int(mm.group(1))] = float(mm.group(2))

    return dict(
        cell=cell, species=species, positions=positions, flags=flags, kpts=kpts,
        hubbard=hubbard, mags=mags,
        ecutwfc=scalar("ecutwfc"), ecutrho=scalar("ecutrho"),
        degauss=scalar("degauss", default=0.01),
        nspin=scalar("nspin", int, default=1),
        nosym=bool(re.search(r"nosym\s*=\s*\.true\.", txt, re.I)),
        assume_isolated=scalar("assume_isolated", str, default=None),
        ibrav=scalar("ibrav", int, default=0),
        celldm1=scalar("celldm\\(1\\)", default=None),
        raw=txt,
    )


def parse_final_coordinates(outfile: str):
    """Relaxed ATOMIC_POSITIONS from a pw.x relax output, or None.

    Prefers the `Begin/End final coordinates` block. Falls back to the LAST
    ATOMIC_POSITIONS block, which is what a run that hit `nstep` leaves behind --
    the caller is told which, because a non-final geometry must not be presented
    as a relaxed one.
    """
    txt = open(outfile, errors="replace").read()
    m = re.search(r"Begin final coordinates(.*?)End final coordinates", txt, re.S)
    provenance = "final"
    if not m:
        blocks = list(re.finditer(r"ATOMIC_POSITIONS\s+\(?\w*\)?\s*\n((?:\s*[A-Z][a-z]?\s+[-\d.eE+]+.*\n)+)", txt))
        if not blocks:
            return None, None
        m = blocks[-1]
        provenance = "last-step (NOT a converged final geometry)"
    body = m.group(1)
    out = []
    for line in body.strip().split("\n"):
        p = line.split()
        if len(p) >= 4 and _ELEMENT_RE.match(p[0]):
            out.append((p[0], float(p[1]), float(p[2]), float(p[3])))
    return (out or None), provenance


def relax_final_energy_ev(outfile: str):
    """Last `!    total energy` in Ry -> eV. The number `base` must reproduce."""
    txt = open(outfile, errors="replace").read()
    hits = re.findall(r"^!\s+total energy\s+=\s+([-\d.]+)\s+Ry", txt, re.M)
    return float(hits[-1]) * RY_EV if hits else None


# ------------------------------------------------------------ perturbation ---

def vacuum_report(positions, cell):
    """(z_extent, cell_c, true_gap_to_image) in Angstrom."""
    zs = [p[3] for p in positions]
    c = cell[2][2]
    return max(zs) - min(zs), c, c - (max(zs) - min(zs))


def dipole_block(positions, cell):
    """tefield/dipfield sawtooth placed in the MIDDLE of the vacuum.

    QE drops the sawtooth over [emaxpos, emaxpos + eopreg] in fractional units of
    the cell along `edir`. Put that window in vacuum or the correction cuts
    through the slab and the run is worse than no correction at all. The slab is
    centred, so the vacuum wraps the cell boundary and the midpoint is computed
    modulo 1.
    """
    zs = [p[3] for p in positions]
    c = cell[2][2]
    zlo, zhi = min(zs) / c, max(zs) / c
    vac_len = 1.0 - (zhi - zlo)
    emaxpos = (zhi + vac_len / 2.0) % 1.0
    eopreg = min(0.10, max(0.02, vac_len * 0.25))
    # keep the whole drop window clear of the slab
    if not (emaxpos + eopreg < zlo or emaxpos > zhi):
        eopreg = max(0.02, (zlo - emaxpos) * 0.8) if emaxpos < zlo else 0.05
    return (f"  tefield = .true.\n  dipfield = .true.\n  edir = 3\n"
            f"  emaxpos = {emaxpos:.4f}\n  eopreg = {eopreg:.4f}\n  eamp = 0.0d0\n"), emaxpos, eopreg


def apply_vacuum(positions, cell, new_c):
    """Stretch c to `new_c` and recentre the slab, so the image gap is uniform."""
    zs = [p[3] for p in positions]
    zmid = (min(zs) + max(zs)) / 2.0
    shift = new_c / 2.0 - zmid
    newpos = [(s, x, y, z + shift) for (s, x, y, z) in positions]
    newcell = [list(cell[0]), list(cell[1]), [cell[2][0], cell[2][1], float(new_c)]]
    return newpos, newcell


def parse_variant(v: str):
    """'dipole+vac32' -> dict(dipole=True, vac=32.0, uscale=None)."""
    spec = dict(dipole=False, vac=None, uscale=None, name=v)
    for tok in v.split("+"):
        tok = tok.strip().lower()
        if tok == "base":
            continue
        elif tok == "dipole":
            spec["dipole"] = True
        elif tok.startswith("vac"):
            spec["vac"] = float(tok[3:])
        elif tok.startswith("u"):
            spec["uscale"] = float(tok[1:])
        else:
            raise ValueError(f"unknown variant token {tok!r} in {v!r}")
    return spec


# ---------------------------------------------------------------- emitting ---

def write_probe(deck, positions, spec, prefix, pseudo_dir, outdir_scratch,
                calculation="scf"):
    cell = deck["cell"]
    if spec["vac"]:
        positions, cell = apply_vacuum(positions, cell, spec["vac"])

    extra, emaxpos, eopreg = ("", None, None)
    if spec["dipole"]:
        extra, emaxpos, eopreg = dipole_block(positions, cell)

    mag = ""
    if deck["nspin"] == 2:
        mag = "  nspin = 2\n" + "".join(
            f"  starting_magnetization({i}) = {m}\n" for i, m in sorted(deck["mags"].items()))
    sym = "  nosym = .true.\n  noinv = .true.\n" if deck["nosym"] else ""

    head = f"""&CONTROL
  calculation = '{calculation}'
  prefix = '{prefix}'
  outdir = '{outdir_scratch}'
  pseudo_dir = '{pseudo_dir}'
  tprnfor = .true.
  forc_conv_thr = 2.0d-3
  nstep = 200
/
&SYSTEM
  ibrav = 0
  nat = {len(positions)}
  ntyp = {len(deck['species'])}
  ecutwfc = {deck['ecutwfc']}
  ecutrho = {deck['ecutrho']}
  occupations = 'smearing'
  smearing = 'mv'
  degauss = {deck['degauss']}
{sym}{mag}{extra}/
&ELECTRONS
  conv_thr = 1.0d-6
  mixing_mode = 'local-TF'
  mixing_beta = 0.3
  electron_maxstep = 200
/
&IONS
  ion_dynamics = 'bfgs'
/
ATOMIC_SPECIES
"""
    spec_block = "".join(f"  {s}  {m:.3f}  {p}\n" for s, m, p in deck["species"])
    cellp = "CELL_PARAMETERS angstrom\n" + "".join(
        f"  {cell[i][0]:.8f}  {cell[i][1]:.8f}  {cell[i][2]:.8f}\n" for i in range(3))
    pos = "ATOMIC_POSITIONS angstrom\n"
    for (s, x, y, z), fl in zip(positions, deck["flags"]):
        pos += f"  {s}  {x:.8f}  {y:.8f}  {z:.8f}  {fl}\n"
    kind, kvals = deck["kpts"]
    kpts = (f"K_POINTS {kind}\n" + ("  " + " ".join(kvals) + "\n" if kvals else ""))

    hub = ""
    if deck["hubbard"]:
        scale = 1.0 if spec["uscale"] is None else spec["uscale"]
        scaled = [(lbl, u * scale) for lbl, u in deck["hubbard"]]
        # u0.0 must be genuinely plain PBE, not "+U with U set to zero": the whole
        # point of that rung is to put a 3d metal on the EXACT protocol Ru and Ir
        # ran under, and those decks carry no HUBBARD card at all. Emitting one
        # with U = 0 would leave the projector machinery in the loop and make the
        # comparison inexact in precisely the way the rung exists to rule out.
        if any(u > 0 for _, u in scaled):
            hub = "HUBBARD (atomic)\n" + "".join(f"U {lbl} {u:.4f}\n" for lbl, u in scaled)

    return head + spec_block + cellp + pos + kpts + hub, dict(
        emaxpos=emaxpos, eopreg=eopreg, cell_c=cell[2][2],
        vac_gap=vacuum_report(positions, cell)[2])


def cmd_build(args):
    src = args.rundir
    manifest_path = os.path.join(src, "manifest.json")
    jobs = json.load(open(manifest_path))["jobs"]
    names = [j["name"] for j in jobs if j["kind"] in ("slab", "adslab")]
    if args.jobs:
        names = [n for n in names if n in args.jobs]

    os.makedirs(args.outdir, exist_ok=True)
    out_manifest = {
        "source_run": src,
        "note": ("FIXED-GEOMETRY single points on already-relaxed structures. This is a "
                 "leading-order SENSITIVITY analysis: relaxation under the perturbation "
                 "is NOT included and the artifacts must not be reported as relaxed."),
        "calculation": args.calculation,
        "variants": args.variants,
        "jobs": [],
    }

    for name in names:
        inp = os.path.join(src, name + ".in")
        outp = os.path.join(src, name + ".out")
        if not (os.path.exists(inp) and os.path.exists(outp)):
            print(f"  SKIP {name}: missing {'in' if not os.path.exists(inp) else 'out'}")
            continue
        deck = parse_input_deck(inp)
        pos, prov = parse_final_coordinates(outp)
        if pos is None:
            print(f"  SKIP {name}: no coordinates in {outp}")
            continue
        if len(pos) != len(deck["positions"]):
            print(f"  SKIP {name}: {len(pos)} relaxed coords vs {len(deck['positions'])} in deck")
            continue
        e_relax = relax_final_energy_ev(outp)

        for v in args.variants:
            spec = parse_variant(v)
            prefix = f"{name}__{v}"
            text, meta = write_probe(deck, pos, spec, prefix, args.pseudo_dir,
                                     args.scratch, calculation=args.calculation)
            path = os.path.join(args.outdir, prefix + ".in")
            with open(path, "w", newline="\n") as f:
                f.write(text)
            out_manifest["jobs"].append(dict(
                job=name, variant=v, file=os.path.basename(path),
                geometry_provenance=prov, relax_reference_ev=e_relax, **meta))
        print(f"  {name}: {len(args.variants)} variants  (geometry: {prov}, "
              f"relax E = {e_relax:.4f} eV)")

    with open(os.path.join(args.outdir, "probe_manifest.json"), "w") as f:
        json.dump(out_manifest, f, indent=2)
    n = len(out_manifest["jobs"])
    print(f"\nwrote {n} probe decks + probe_manifest.json -> {args.outdir}")
    if "base" not in args.variants:
        print("WARNING: no 'base' control in this batch -- probe_eta.py will refuse to score it.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="write fixed-geometry probe decks")
    b.add_argument("rundir", help="a completed run dir, e.g. runs/Ru_anchor")
    b.add_argument("--outdir", required=True)
    b.add_argument("--variants", nargs="+", default=["base", "dipole", "vac32", "dipole+vac32"])
    b.add_argument("--jobs", nargs="*", default=None, help="subset of job names")
    b.add_argument("--pseudo-dir", default="/usr/share/espresso/pseudo")
    b.add_argument("--scratch", default="./tmp")
    b.add_argument("--calculation", default="scf", choices=["scf", "relax"])
    b.set_defaults(func=cmd_build)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
