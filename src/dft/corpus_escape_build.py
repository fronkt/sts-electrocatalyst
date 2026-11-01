#!/usr/bin/env python3
"""Corpus escape (2026-11-01): held and escape relaxation decks for the locked Xu four-layer *OOH and *OH outputs.

Design note of record: docs/research/corpus-escape-2026-11-01.md (selection rule, displacement recipe, deviations
from the deposited settings, decision rule). Exploratory and post-census. This file launches nothing.

Inputs, all read-only:
  - the Xu corpus tree (env STS_XU, default as in the report's figstyle.py); every deposited pwscf.in/out used here
    is checked against the sha256 the census registered for it (corpus_identity.files);
  - the census, results/s2_2026-09-18/xu_census.json: rows with layers == 4 and silentgate verdict LOCKED; locked
    axis = force.every_step_all_atom_zero_lateral_axes; adsorbate atoms = force.eligible_adsorbate_indices (1-based);
  - the runner files pinned by the B1 re-relaxation (the relax path of research_batch_seeded.py), the QE binary
    pins and node exclusions of round 7 (results/arm_c_ext_r7_2026-11-01/launch_spec.json).

Per selected case two decks:
  <metal>__<job>__held    the deposited deck at the deposited final geometry (last printed geometry where the
                          deposited run stopped unconverged), symmetry on;
  <metal>__<job>__escape  the same deck, adsorbate atoms displaced along the locked axis (binding O 0.050 A,
                          distal O 0.075 A, H 0.100 A), nosym = .true. (no noinv: registered change S0(b)).
Deviations from the deposited namelists are exactly DEVIATIONS below; every other deposited key is copied verbatim
and the guard re-parses each emitted deck to prove it.

    python src/dft/corpus_escape_build.py                      # write everything (refuses to overwrite differing files)
    python src/dft/corpus_escape_build.py --check              # rebuild in memory and compare with the files on disk
    python src/dft/corpus_escape_build.py --decision "<Frank's words>" --decision-date 2026-11-02 --replace
                                                               # license the manifests (rewrites manifests, spec, Slurm)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "2026-11-01"
TAG = "corpus_escape_2026-11-01"
DESIGN = "docs/research/corpus-escape-2026-11-01.md"
PACKAGE = "results/" + TAG
RUN_DIR = TAG                                   # runs/<RUN_DIR>/<job>.in
SLURM_REL = "anvil/106_corpus_escape.slurm"
REMOTE = "/anvil/projects/x-che260157/sts_" + TAG
CORPUS = Path(os.environ.get("STS_XU", r"C:\Users\frank\sts-corpora\xu\extracted\zhongnanxu-rutile-OER-c4cb892"))
CENSUS_REL = "results/s2_2026-09-18/xu_census.json"
R7_SPEC_REL = "results/arm_c_ext_r7_2026-11-01/launch_spec.json"
B1_SPEC_REL = "results/b1_rerelax_2026-10-19/launch_spec.json"
RUNNER_FILES = ("src/dft/research_batch_seeded.py", "src/dft/projection_qc.py",
                "src/dft/hea_panel_readout.py", "src/dft/hea_geometry.py")
PYTHON_ANVIL = "/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3"

METALS = ("CrO2", "IrO2", "MnO2", "MoO2", "NbO2", "PtO2", "ReO2", "RhO2", "RuO2", "TiO2")
TIERS = {"tier1": {"states": ("OOH",), "expected": 10, "per_metal": 1},
         "tier2": {"states": ("OH",), "expected": 20, "per_metal": 2}}
ARMS = ("held", "escape")
AXIS_INDEX = {"x": 0, "y": 1}
#: displacement along the locked axis, Angstrom, by adsorbate role (design note, "Displacement recipe")
DISPLACEMENT_A = {"O_bind": 0.050, "O_distal": 0.075, "H": 0.100}
#: deposited UPF identities: MD5 printed by every deposited output that read the file (asserted per case below)
PSEUDO_MD5 = {
    "o_pbe_v1.01.uspp.F.UPF": "2bcb18d16ea4b960afae9ec6d52f22d2",
    "h_pbe_v1.uspp.F.UPF": "3408e3ff4ec8b0a4e358431e7e038a48",
    "cr_pbe_v1.uspp.F.UPF": "68b6f918d1762dccfb11451fe85b0e0e",
    "ir_pbe_v1.uspp.F.UPF": "abf987a9674477536ede83817f8f8b70",
    "mn_pbe_v1.uspp.F.UPF": "5fd7c7b5c956fd19902447332617373a",
    "mo_pbe_v1.uspp.F.UPF": "30c4dcd161f5d35cd49bb5239c51a633",
    "nb_pbe_v1.uspp.F.UPF": "573aab8a2fa660278ed4a62cd769473f",
    "pt_pbe_v1.uspp.F.UPF": "4c71d6ad5ef119f1eb26a4d0b7884226",
    "re_pbe_v1.uspp.F.UPF": "6f5a5dcaf9c96c20d0ffdde0de57afc6",
    "rh_pbe_v1.uspp.F.UPF": "37b626987ad0dd8ec6bf4cc9ef289918",
    "ru_pbe_v1.uspp.F.UPF": "df00be1c11b23341d9806d8f1dfa10cf",
    "ti_pbe_v1.uspp.F.UPF": "bcc8f6961b3b91f0cac3ca967d22d0fb",
}

# Deposited namelist keys that are copied verbatim (lower-case; starting_magnetization(i) by prefix).
KEPT = {"CONTROL": ("calculation", "tprnfor", "tstress"),
        "SYSTEM": ("ibrav", "nat", "ntyp", "tot_magnetization", "starting_magnetization", "ecutwfc", "ecutrho",
                   "occupations", "degauss", "smearing", "nspin"),
        "ELECTRONS": ("mixing_beta",),
        "IONS": ()}
# Deposited keys that are removed, with the reason (design note table). Anything not KEPT or DROPPED refuses.
DROPPED = {"disk_io": "runner retains density/XML and projwfc.x needs wavefunctions; default 'low'",
           "pseudo_dir": "rewritten by the runner at execution",
           "nbnd": "pw.x default (1.2 x occupied); deposited count is unaffordable (cost_estimate.json)",
           "hubbard_u": "all zero and lda_plus_u never set: inert; pw.x 7.5 reads DFT+U only from a HUBBARD card",
           "hubbard_alpha": "all zero and lda_plus_u never set: inert"}
# Keys added in both arms, in emission order per namelist, and the escape-only key.
ADDED = {"CONTROL": [("prefix", None), ("outdir", "'./tmp'"), ("pseudo_dir", "'./pseudo'"),
                     ("forc_conv_thr", "1.0d-4"), ("nstep", "100")],
         "ELECTRONS": []}
ESCAPE_ONLY = ("SYSTEM", "nosym", ".true.")
DEVIATIONS = {
    "prefix/outdir/pseudo_dir": "runner contract: prefix = job name; outdir and pseudo_dir rewritten at execution",
    "disk_io": DROPPED["disk_io"],
    "nbnd": DROPPED["nbnd"],
    "Hubbard_U(i), Hubbard_alpha(i)": DROPPED["hubbard_u"],
    "&CELL": "empty and ignored for 'relax' (deposited output: 'Warning: card &CELL ignored')",
    "forc_conv_thr": "1.0d-4 Ry/bohr (deposited default 1e-3): stall guard at the 0.10 A start",
    "nstep": "100 (deposited default 50): more BFGS steps at the tighter threshold",
    "escape: nosym": ".true. in the escape arm only; noinv unset (registered change S0(b))",
    "ATOMIC_SPECIES UPF files": "current GBRV v1.5 in place of the deposited v1/v1.01 files, which are no longer distributed (Frank, 2026-11-01; SUBSTITUTE); Mo and Nb byte-identical",
}

#: Run pseudopotentials (Frank, 2026-11-01: "Current GBRV v1.5"). The deposited GBRV v1/v1.01 files are no longer
#: distributed (results/s2_2026-09-18/xu_molecules/README.md; rechecked 2026-11-01), so both arms of every case read
#: the current GBRV v1.5 UPFs from all_pbe_UPF_v1.5.tar.gz (physics.rutgers.edu/gbrv). Mo and Nb are byte-identical to
#: the deposited files. PSEUDO_MD5 above stays the check that each deposited output read the deposited file.
SUBSTITUTE = {
    "o_pbe_v1.01.uspp.F.UPF": ("o_pbe_v1.2.uspp.F.UPF", "734c27235a0248c51dbae37a1fbe46ec"),
    "h_pbe_v1.uspp.F.UPF": ("h_pbe_v1.4.uspp.F.UPF", "761ae9a214b05c3daf00ab9f6b793d6f"),
    "cr_pbe_v1.uspp.F.UPF": ("cr_pbe_v1.5.uspp.F.UPF", "0d52af634a40206e4dee301ad30da4bf"),
    "ir_pbe_v1.uspp.F.UPF": ("ir_pbe_v1.2.uspp.F.UPF", "8836f839c3459d2b385c504ce6d91f2c"),
    "mn_pbe_v1.uspp.F.UPF": ("mn_pbe_v1.5.uspp.F.UPF", "82ef2b46521d7a7d9e736dc3972e4928"),
    "mo_pbe_v1.uspp.F.UPF": ("mo_pbe_v1.uspp.F.UPF", "30c4dcd161f5d35cd49bb5239c51a633"),
    "nb_pbe_v1.uspp.F.UPF": ("nb_pbe_v1.uspp.F.UPF", "573aab8a2fa660278ed4a62cd769473f"),
    "pt_pbe_v1.uspp.F.UPF": ("pt_pbe_v1.4.uspp.F.UPF", "f09d6de1a584b5a045c4fc126da2d0c4"),
    "re_pbe_v1.uspp.F.UPF": ("re_pbe_v1.2.uspp.F.UPF", "85f993410f3e006da9d71c142b4ad953"),
    "rh_pbe_v1.uspp.F.UPF": ("rh_pbe_v1.4.uspp.F.UPF", "761627e959a2e3a1f56b0b5fe687810e"),
    "ru_pbe_v1.uspp.F.UPF": ("ru_pbe_v1.2.uspp.F.UPF", "7158a806dd851261a58e6920c40ebe78"),
    "ti_pbe_v1.uspp.F.UPF": ("ti_pbe_v1.4.uspp.F.UPF", "88a00a6731bd790ddea75d31a80cb452"),
}
RUN_MD5 = {run: md5 for run, md5 in SUBSTITUTE.values()}


def species_lines(dep: dict) -> list:
    """The deposited ATOMIC_SPECIES lines with each UPF name replaced by its run file (SUBSTITUTE)."""
    out = []
    for line in dep["cards"]["ATOMIC_SPECIES"]["lines"]:
        tok = line.split()
        out.append(line.replace(tok[2], SUBSTITUTE[tok[2]][0]))
    return out

NK = 8                      # 9 or 10 k-points (nspin 1), 18 or 20 (nspin 2): 8 pools, 16 ranks each, the mirror-row shape
MAX_ITERATIONS = 126        # the runner's registered SCF ceiling for a relaxation leg
PROJECTION_SECONDS = 900
#: Launch groups, in launch order. Tier 1 is split by whether the deposited relaxation converged: a held arm that
#: must finish an unconverged deposited relaxation costs about 2.5x more (cost_estimate.json).
GROUPS = {"tier1a": ("tier1", True), "tier1b": ("tier1", False), "tier2": ("tier2", None)}
#: Slurm wall per stage (minutes), from cost_estimate.json: about 1.4-1.7x the planning wall of the stage's slowest
#: row, so that each group's reservation fits the balance. SCF wall = Slurm wall - projection - 300 s.
WALL_MINUTES = {"tier1a_held": 180, "tier1a_escape": 360, "tier1b_held": 420, "tier1b_escape": 420,
                "tier2_held": 180, "tier2_escape": 360}
SYM_TOL_A = 1e-6            # reflection match tolerance (the program's mirror-start tolerance, build_s3.SYM_TOL_A)
NUM = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][+-]?\d+)?"


class Refuse(Exception):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ------------------------------------------------------------------------------------------------ parsing ---

def parse_pw_input(text: str) -> dict:
    """Strict reader for the deposited (and emitted) deck layout: namelists, then the four cards."""
    lines = text.splitlines()
    namelists, order, i, current = {}, [], 0, None
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if current is None and s.startswith("&"):
            current = s[1:].upper()
            if current in namelists:
                raise Refuse("namelist repeated: " + current)
            namelists[current] = []
            order.append(current)
        elif s == "/":
            if current is None:
                raise Refuse("stray '/' at line %d" % (i + 1))
            current = None
        elif current is not None:
            if s.count("=") != 1 or "," in s:
                raise Refuse("unexpected namelist line: " + s)
            key, value = (t.strip() for t in s.split("="))
            namelists[current].append((key, value))
        else:
            break
        i += 1
    cards, name = {}, None
    for raw in lines[i:]:
        s = raw.strip()
        if not s:
            continue
        head = s.split()[0].upper()
        if head in ("K_POINTS", "ATOMIC_SPECIES", "ATOMIC_POSITIONS", "CELL_PARAMETERS"):
            name = head
            if name in cards:
                raise Refuse("card repeated: " + name)
            cards[name] = {"header": raw, "lines": []}
        elif name is None:
            raise Refuse("text before the first card: " + s)
        else:
            cards[name]["lines"].append(raw)
    for need in ("K_POINTS", "ATOMIC_SPECIES", "ATOMIC_POSITIONS", "CELL_PARAMETERS"):
        if need not in cards:
            raise Refuse("missing card " + need)
    nat = int(dict(namelists["SYSTEM"])["nat"])
    ntyp = int(dict(namelists["SYSTEM"])["ntyp"])
    if len(cards["ATOMIC_POSITIONS"]["lines"]) != nat or len(cards["ATOMIC_SPECIES"]["lines"]) != ntyp:
        raise Refuse("card line counts differ from nat/ntyp")
    if len(cards["CELL_PARAMETERS"]["lines"]) != 3 or len(cards["K_POINTS"]["lines"]) != 1:
        raise Refuse("cell or k-point card malformed")
    atoms = []
    for raw in cards["ATOMIC_POSITIONS"]["lines"]:
        t = raw.split()
        if len(t) != 7:
            raise Refuse("position line without three if_pos flags: " + raw)
        atoms.append({"label": t[0], "s": [float(v) for v in t[1:4]], "if_pos": " ".join(t[4:7])})
    cell = [[float(v) for v in raw.split()] for raw in cards["CELL_PARAMETERS"]["lines"]]
    return {"namelists": namelists, "order": order, "cards": cards, "atoms": atoms, "cell": cell, "nat": nat}


def parse_deposited_output(text: str, nat: int) -> dict:
    """Final geometry (crystal) and the header facts the decks must reproduce."""
    converged = "bfgs converged" in text
    if converged:
        block = text[text.index("Begin final coordinates"):text.index("End final coordinates")]
        heads = [m.end() for m in re.finditer(r"ATOMIC_POSITIONS \(crystal\)\s*\n", block)]
        if len(heads) != 1:
            raise Refuse("final-coordinates block without one crystal ATOMIC_POSITIONS")
        body, source = block[heads[0]:], "final coordinates (bfgs converged)"
    else:
        heads = [m.end() for m in re.finditer(r"ATOMIC_POSITIONS \(crystal\)\s*\n", text)]
        if not heads:
            raise Refuse("no printed geometry")
        body, source = text[heads[-1]:], "last printed geometry (%d printed; run stopped before converging)" % len(heads)
    rows = []
    for raw in body.splitlines()[:nat]:
        t = raw.split()
        if len(t) not in (4, 7):
            raise Refuse("geometry block truncated or malformed: " + raw)
        rows.append({"label": t[0], "s": [float(v) for v in t[1:4]]})
    if len(rows) != nat:
        raise Refuse("geometry block has %d of %d atoms" % (len(rows), nat))
    sym = re.findall(r"^\s*(\d+) Sym\. Ops\..*found", text, re.M)
    if not sym and re.search(r"No symmetry found", text):
        sym = ["1"]
    pseudo = re.findall(r"PseudoPot\. #\s*\d+ for (\S+)\s+read from file:\s*\n\s*(\S+)\s*\n\s*MD5 check sum:\s*([0-9a-f]{32})", text)
    nks = re.findall(r"number of k points=\s*(\d+)", text)
    nelec = re.findall(r"number of electrons\s*=\s*(" + NUM + ")", text)
    nbnd = re.findall(r"number of Kohn-Sham states=\s*(\d+)", text)
    absmag = re.findall(r"absolute magnetization\s*=\s*(" + NUM + ")", text)
    return {"positions": rows, "geometry_source": source, "bfgs_converged": converged,
            "job_done": text.count("JOB DONE"), "n_symops": [int(v) for v in sym],
            "pseudo": [{"element": e, "file": Path(f.replace("\\", "/")).name, "md5": m} for e, f, m in pseudo],
            "nks_printed": int(nks[0]) if nks else None, "nelec": float(nelec[0]) if nelec else None,
            "nbnd": int(nbnd[0]) if nbnd else None, "absmag_last": float(absmag[-1]) if absmag else None}


# ---------------------------------------------------------------------------------------------- geometry ---

def lengths(cell):
    for i in range(3):
        for j in range(3):
            if i != j and abs(cell[i][j]) > 0.0:
                raise Refuse("cell is not diagonal; locked axes are Cartesian x/y")
    return [cell[0][0], cell[1][1], cell[2][2]]


def min_image(d: float) -> float:
    return d - round(d)


def reflection_mismatch(atoms, axis: int, plane: float, L) -> float:
    """Largest distance (A) between an atom's mirror image and the nearest same-label, same-mask atom."""
    worst = 0.0
    for a in atoms:
        image = list(a["s"])
        image[axis] = 2.0 * plane - image[axis]
        best = math.inf
        for b in atoms:
            if b["label"] != a["label"] or b["if_pos"] != a["if_pos"]:
                continue
            d = math.sqrt(sum((min_image(image[k] - b["s"][k]) * L[k]) ** 2 for k in range(3)))
            best = min(best, d)
        worst = max(worst, best)
    return worst


def element(label: str) -> str:
    return re.match(r"[A-Z][a-z]?", label).group(0)


def assign_roles(atoms, ads_idx, L):
    """Binding O = adsorbate O nearest any metal atom; distal O = the other O; H = H."""
    metals = [a for a in atoms if element(a["label"]) not in ("O", "H")]
    oxygens = [i for i in ads_idx if element(atoms[i]["label"]) == "O"]
    hydrogens = [i for i in ads_idx if element(atoms[i]["label"]) == "H"]
    if len(hydrogens) != 1 or len(oxygens) not in (1, 2):
        raise Refuse("adsorbate is not OH or OOH: " + str([atoms[i]["label"] for i in ads_idx]))

    def metal_distance(i):
        return min(math.sqrt(sum((min_image(atoms[i]["s"][k] - m["s"][k]) * L[k]) ** 2 for k in range(3)))
                   for m in metals)
    ranked = sorted(oxygens, key=metal_distance)
    out = {ranked[0]: "O_bind", hydrogens[0]: "H"}
    if len(ranked) == 2:
        if metal_distance(ranked[1]) - metal_distance(ranked[0]) < 0.3:
            raise Refuse("binding O ambiguous")
        out[ranked[1]] = "O_distal"
    return out


# ------------------------------------------------------------------------------------------------- decks ---

def fmt_pos(label, s, flags):
    return " %s %.9f %.9f %.9f %s" % (label, s[0], s[1], s[2], flags)


def deck_text(dep: dict, job: str, positions, arm: str) -> str:
    out = []
    for nl in ("CONTROL", "SYSTEM", "ELECTRONS", "IONS"):
        out.append("&" + nl)
        kept = [(k, v) for k, v in dep["namelists"].get(nl, []) if k.lower().split("(")[0] in KEPT[nl]]
        if nl == "CONTROL":
            # calculation first, then the runtime keys, then the rest in deposited order
            calc = [kv for kv in kept if kv[0].lower() == "calculation"]
            rest = [kv for kv in kept if kv[0].lower() != "calculation"]
            body = calc + [("prefix", "'" + job + "'"), ("outdir", "'./tmp'"), ("pseudo_dir", "'./pseudo'")] + rest
            body += [kv for kv in ADDED["CONTROL"] if kv[0] in ("forc_conv_thr", "nstep")]
        elif nl == "ELECTRONS":
            body = kept + ADDED["ELECTRONS"]
        else:
            body = list(kept)
        if nl == ESCAPE_ONLY[0] and arm == "escape":
            body.append((ESCAPE_ONLY[1], ESCAPE_ONLY[2]))
        out += ["  %s = %s" % (k, v) for k, v in body]
        out.append("/")
    out.append(dep["cards"]["K_POINTS"]["header"])
    out += dep["cards"]["K_POINTS"]["lines"]
    out.append(dep["cards"]["ATOMIC_SPECIES"]["header"])
    out += species_lines(dep)
    out.append(dep["cards"]["ATOMIC_POSITIONS"]["header"])
    out += [fmt_pos(a["label"], s, a["if_pos"]) for a, s in zip(dep["atoms"], positions)]
    out.append(dep["cards"]["CELL_PARAMETERS"]["header"])
    out += dep["cards"]["CELL_PARAMETERS"]["lines"]
    return "\n".join(out) + "\n"


def guard(text: str, dep: dict, job: str, arm: str, positions, case: dict) -> dict:
    """Re-parse the emitted deck and prove it is the deposited deck plus exactly the declared deviations."""
    d = parse_pw_input(text)
    if d["order"] != ["CONTROL", "SYSTEM", "ELECTRONS", "IONS"]:
        raise Refuse(job + ": namelist order " + str(d["order"]))
    for nl in ("CONTROL", "SYSTEM", "ELECTRONS", "IONS"):
        got = dict((k.lower(), v) for k, v in d["namelists"][nl])
        dep_nl = dict((k.lower(), v) for k, v in dep["namelists"].get(nl, []))
        for k, v in dep_nl.items():
            base = k.split("(")[0]
            if base in KEPT[nl]:
                if got.get(k) != v:
                    raise Refuse("%s: kept key %s changed (%r -> %r)" % (job, k, v, got.get(k)))
            elif base in DROPPED:
                if k in got and not (k == "pseudo_dir" and got[k] == "'./pseudo'"):
                    raise Refuse("%s: dropped key %s present" % (job, k))
            else:
                raise Refuse("%s: deposited key %s is neither kept nor dropped" % (job, k))
        extra = {k: v for k, v in got.items() if k not in dep_nl}
        want = {}
        if nl == "CONTROL":
            want = {"prefix": "'" + job + "'", "outdir": "'./tmp'", "forc_conv_thr": "1.0d-4", "nstep": "100"}
            if got.get("pseudo_dir") != "'./pseudo'":
                raise Refuse(job + ": pseudo_dir placeholder missing")
        if nl == "SYSTEM" and arm == "escape":
            want = {"nosym": ".true."}
        if extra != want:
            raise Refuse("%s: added keys in &%s are %r, declared %r" % (job, nl, extra, want))
        if any(k.startswith("noinv") for k in got):
            raise Refuse(job + ": noinv present (S0(b) drops it)")
    for card in ("K_POINTS", "CELL_PARAMETERS"):
        if d["cards"][card] != dep["cards"][card]:
            raise Refuse("%s: card %s differs from the deposited card" % (job, card))
    if d["cards"]["ATOMIC_SPECIES"] != dict(dep["cards"]["ATOMIC_SPECIES"], lines=species_lines(dep)):
        raise Refuse("%s: ATOMIC_SPECIES differs from the deposited card plus the UPF substitution" % job)
    if d["cards"]["ATOMIC_POSITIONS"]["header"] != dep["cards"]["ATOMIC_POSITIONS"]["header"]:
        raise Refuse(job + ": ATOMIC_POSITIONS units changed")
    for a, b, s in zip(d["atoms"], dep["atoms"], positions):
        if a["label"] != b["label"] or a["if_pos"] != b["if_pos"]:
            raise Refuse(job + ": species or if_pos order differs from the deposited deck")
        if any(abs(x - y) > 6e-10 for x, y in zip(a["s"], s)):
            raise Refuse(job + ": emitted coordinate differs from the intended one")
    upfs = [line.split()[2] for line in d["cards"]["ATOMIC_SPECIES"]["lines"]]
    if any(u not in RUN_MD5 for u in upfs):
        raise Refuse(job + ": UPF without a run MD5 pin (SUBSTITUTE)")
    L = lengths(d["cell"])
    axis, plane = AXIS_INDEX[case["locked_axis"]], case["plane_crystal"]
    off = max(abs(min_image(d["atoms"][i]["s"][axis] - plane)) * L[axis] for i in case["adsorbate_index0"])
    mismatch = reflection_mismatch(d["atoms"], axis, plane, L)
    if arm == "held" and (mismatch > SYM_TOL_A or off > SYM_TOL_A):
        raise Refuse("%s: held start not mirror-symmetric (mismatch %.2e A, adsorbate off-plane %.2e A)"
                     % (job, mismatch, off))
    if arm == "escape" and abs(off - DISPLACEMENT_A["H"]) > 1e-6:
        raise Refuse("%s: escape start H offset %.6f A != %.3f A" % (job, off, DISPLACEMENT_A["H"]))
    return {"start_max_adsorbate_off_plane_A": round(off, 9), "start_reflection_mismatch_A": mismatch}


# ------------------------------------------------------------------------------------------------- build ---

def manifest_text(stage: str, jobs: list, exclusions: str, decision) -> str:
    if decision:
        first = "# APPROVED %s: %s (Frank: \"%s\")" % (decision["date"], DESIGN, decision["words"])
    else:
        first = "# NOT LICENSED: awaiting Frank's decision (%s); the UPF pins block too" % DESIGN
    head = [first,
            "# Corpus escape (%s): held and escape relaxations of locked Xu four-layer outputs; exploratory, "
            "post-census; no automatic retries." % stage,
            "# SUBMIT WITH EXCLUDE=" + exclusions,
            "# NP=128 NCONC=1"]
    return "\n".join(head + ["%s %s .in %d" % (j["dir"], j["job"], j["nk"]) for j in jobs]) + "\n"


def slurm_text(spec_sha: str, runner_sha: str, stages) -> str:
    stage_case = "|".join(stages)
    return f"""#!/bin/bash
# Corpus escape ({DESIGN}). Held (symmetry on) and escape (nosym, adsorbate displaced along the locked
# axis) relaxations of locked Xu four-layer *OOH (tier 1) and *OH (tier 2) outputs, one pw.x relaxation per array
# task through the pinned seeded runner as stages of kind "relax". Resources, held state, time limit and the array
# throttle are set at submission and validated before release. No retry or requeue.
#SBATCH --account=che260157
#SBATCH --partition=wholenode
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --mem=200G
#SBATCH --no-requeue
#SBATCH --output={REMOTE}/logs/corpus_escape_%A_%a.log
#SBATCH --error={REMOTE}/logs/corpus_escape_%A_%a.log
set -euo pipefail
PROJECT=/anvil/projects/x-che260157
ROOT="$PROJECT/sts_{TAG}"
SPEC="$ROOT/{PACKAGE}/launch_spec.json"
RUNNER="$ROOT/src/dft/research_batch_seeded.py"
PYTHON={PYTHON_ANVIL}
[ "${{SLURM_NTASKS:-}}" = 128 ] || {{ echo 'REFUSE: requires 128 ranks'; exit 2; }}
case "${{STAGE:-}}" in {stage_case}) ;; *) echo 'REFUSE: stage'; exit 2;; esac
check_hash() {{ [ "$(sha256sum "$1" | awk '{{print $1}}')" = "$2" ] || {{ echo "REFUSE: hash $1"; exit 2; }}; }}
check_hash "$SPEC" {spec_sha}
check_hash "$RUNNER" {runner_sha}
export OMP_NUM_THREADS=1 OMP_THREAD_LIMIT=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 OMP_DYNAMIC=FALSE MKL_DYNAMIC=FALSE
echo "STAGE $STAGE TASK ${{SLURM_ARRAY_TASK_ID:?}} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \\
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$ROOT/pseudo" --qe "$PROJECT/qe/env"
"""


def census_rows(census: dict):
    pins = {f["path"]: f["sha256"] for f in census["corpus_identity"]["files"]}
    rows = [r for r in census["rows"] if r["layers"] == 4 and r["force"].get("silentgate_verdict") == "LOCKED"]
    if len(rows) != 50:
        raise Refuse("expected 50 locked four-layer rows, found %d" % len(rows))
    return rows, pins


def build_case(row: dict, tier: str, pins: dict) -> tuple:
    metal, job, state = row["metal"], row["job"], row["state"]
    inp, out = CORPUS / row["input"], CORPUS / row["output"]
    raw_in, raw_out = inp.read_bytes(), out.read_bytes()
    for rel, data in ((row["input"], raw_in), (row["output"], raw_out)):
        if pins.get(rel) != sha256(data):
            raise Refuse("deposited bytes differ from the census pin: " + rel)
    f = row["force"]
    axes = f["every_step_all_atom_zero_lateral_axes"]
    if axes != f["final_all_atom_zero_lateral_axes"] or not axes or len(axes) != 1:
        raise Refuse("%s %s: locked axis not a single, stable axis (%r)" % (metal, job, axes))
    axis_name = axes[0]
    axis = AXIS_INDEX[axis_name]
    if f["eligible_adsorbate_indices"] != f["identified_adsorbate_indices"] or f["excluded_adsorbate_indices"]:
        raise Refuse("%s %s: adsorbate atoms partly constrained" % (metal, job))
    dep = parse_pw_input(raw_in.decode("utf-8"))
    nat = dep["nat"]
    ads0 = [i - 1 for i in f["eligible_adsorbate_indices"]]
    if ads0 != list(range(nat - len(ads0), nat)):
        raise Refuse("%s %s: adsorbate atoms are not the last %d" % (metal, job, len(ads0)))
    labels = [element(dep["atoms"][i]["label"]) for i in ads0]
    if labels != (["O", "O", "H"] if state == "OOH" else ["O", "H"]):
        raise Refuse("%s %s: adsorbate species %r" % (metal, job, labels))
    for i in ads0:
        if dep["atoms"][i]["if_pos"] != "1 1 1":
            raise Refuse("%s %s: adsorbate atom fixed in the deposited deck" % (metal, job))
    # namelist content checks: only known keys; U all zero; lda_plus_u absent
    for nl, pairs in dep["namelists"].items():
        if nl not in ("CONTROL", "SYSTEM", "ELECTRONS", "IONS", "CELL"):
            raise Refuse("unexpected namelist &" + nl)
        if nl == "CELL" and pairs:
            raise Refuse("&CELL is not empty")
        for k, v in pairs:
            base = k.lower().split("(")[0]
            if nl != "CELL" and base not in KEPT.get(nl, ()) and base not in DROPPED:
                raise Refuse("%s %s: unexpected deposited key %s" % (metal, job, k))
            if base in ("hubbard_u", "hubbard_alpha") and float(v) != 0.0:
                raise Refuse("%s %s: nonzero %s" % (metal, job, k))
    sysd = dict((k.lower(), v) for k, v in dep["namelists"]["SYSTEM"])
    if "lda_plus_u" in sysd:
        raise Refuse("lda_plus_u present")
    calc = dict((k.lower(), v) for k, v in dep["namelists"]["CONTROL"]).get("calculation")
    if calc != "'relax'":
        raise Refuse("deposited calculation is %s" % calc)
    kline = dep["cards"]["K_POINTS"]["lines"][0].split()
    if dep["cards"]["K_POINTS"]["header"].split()[1:] != ["{automatic}"] or kline != ["4", "4", "1", "0", "0", "0"]:
        raise Refuse("k-points not the deposited 4 4 1 0 0 0 automatic mesh")
    if dep["cards"]["ATOMIC_POSITIONS"]["header"].split()[1:] != ["{crystal}"]:
        raise Refuse("positions not in crystal units")
    L = lengths(dep["cell"])
    o = parse_deposited_output(raw_out.decode("utf-8", "replace"), nat)
    if o["bfgs_converged"] != row["energy"]["ionic_converged"]:
        raise Refuse("%s %s: convergence differs from the census" % (metal, job))
    if [p["label"] for p in o["positions"]] != [a["label"] for a in dep["atoms"]]:
        raise Refuse("%s %s: output species order differs from the deck" % (metal, job))
    if not o["n_symops"] or o["n_symops"][0] != row["header"]["n_symops"] or o["n_symops"][0] != 2:
        raise Refuse("%s %s: header symmetry count %r" % (metal, job, o["n_symops"]))
    for a, p in zip(dep["atoms"], o["positions"]):
        if a["if_pos"] == "0 0 0" and any(abs(x - y) > 1e-9 for x, y in zip(a["s"], p["s"])):
            raise Refuse("%s %s: a fixed atom moved" % (metal, job))
    species_upf = {line.split()[0]: line.split()[2] for line in dep["cards"]["ATOMIC_SPECIES"]["lines"]}
    printed = {(p["file"], p["md5"]) for p in o["pseudo"]}
    for upf in species_upf.values():
        if (upf, PSEUDO_MD5.get(upf)) not in printed:
            raise Refuse("%s %s: printed MD5 for %s differs from the pin" % (metal, job, upf))
    final = [p["s"] for p in o["positions"]]
    held_atoms = [dict(a, s=s) for a, s in zip(dep["atoms"], final)]
    plane_vals = {round(final[i][axis], 9) for i in ads0}
    if len(plane_vals) != 1:
        raise Refuse("%s %s: adsorbate atoms not on one plane along %s" % (metal, job, axis_name))
    plane = plane_vals.pop()
    if min(abs(min_image(plane - 0.0)), abs(min_image(plane - 0.5))) > 1e-9:
        raise Refuse("%s %s: mirror plane at %.9f is not a lattice mirror" % (metal, job, plane))
    mismatch = reflection_mismatch(held_atoms, axis, plane, L)
    if mismatch > SYM_TOL_A:
        raise Refuse("%s %s: deposited final geometry not mirror-symmetric (%.2e A)" % (metal, job, mismatch))
    role = assign_roles(held_atoms, ads0, L)
    escape = [list(s) for s in final]
    disp = {}
    for i, r in role.items():
        escape[i][axis] = final[i][axis] + DISPLACEMENT_A[r] / L[axis]
        disp[str(i + 1)] = {"role": r, "species": dep["atoms"][i]["label"], "angstrom": DISPLACEMENT_A[r],
                            "crystal": round(DISPLACEMENT_A[r] / L[axis], 12)}
    # emitted coordinates are rounded to 9 decimals; the guard compares against the rounded intent
    held_pos = [[round(v, 9) for v in s] for s in final]
    esc_pos = [[round(v, 9) for v in s] for s in escape]
    case = {"tier": tier, "metal": metal, "job": job, "state": state, "locked_axis": axis_name,
            "plane_crystal": plane, "adsorbate_index0": ads0}
    texts, checks = {}, {}
    for arm, pos in (("held", held_pos), ("escape", esc_pos)):
        name = "%s__%s__%s" % (metal, job, arm)
        text = deck_text(dep, name, pos, arm)
        checks[arm] = guard(text, dep, name, arm, pos, case)
        texts[arm] = (name, text)
    # the two arms differ only by prefix, the nosym line and the adsorbate coordinates
    h, e = texts["held"][1].splitlines(), texts["escape"][1].splitlines()
    diff_e = [line for line in e if line not in h]
    expect = {"  prefix = '%s'" % texts["escape"][0], "  nosym = .true."}
    expect |= {fmt_pos(dep["atoms"][i]["label"], esc_pos[i], "1 1 1") for i in ads0}
    if set(diff_e) != expect or len(e) != len(h) + 1:
        raise Refuse("%s %s: escape differs from held by more than declared" % (metal, job))
    nspin = int(float(sysd["nspin"]))
    vol = L[0] * L[1] * L[2]
    record = dict(case, adsorbate_index1=[i + 1 for i in ads0],
                  census_output=row["output"], census_input=row["input"],
                  deposited_output_sha256=sha256(raw_out), deposited_input_sha256=sha256(raw_in),
                  deposited_geometry_source=o["geometry_source"], deposited_converged=o["bfgs_converged"],
                  deposited_final_energy_Ry=row["energy"]["final_energy_Ry"],
                  deposited_scf_iterations=row["energy"]["scf_iterations"],
                  deposited_n_symops=o["n_symops"][0], deposited_nks_printed=o["nks_printed"],
                  deposited_nelec=o["nelec"], deposited_nbnd=o["nbnd"], deposited_absmag_last=o["absmag_last"],
                  nat=nat, nspin=nspin, tot_magnetization=sysd.get("tot_magnetization"),
                  cell_lengths_A=L, volume_A3=round(vol, 6), kmesh="4 4 1 0 0 0",
                  pseudopotentials={k: {"deposited_upf": v, "deposited_md5": PSEUDO_MD5[v], "run_upf": SUBSTITUTE[v][0],
                                        "run_md5": SUBSTITUTE[v][1]} for k, v in species_upf.items()},
                  deposited_final_reflection_mismatch_A=mismatch,
                  displacement=disp, start_checks=checks,
                  decks={arm: "runs/%s/%s.in" % (RUN_DIR, texts[arm][0]) for arm in ARMS})
    return record, texts


def build(root: Path = ROOT, decision=None) -> dict:
    census_bytes = (root / CENSUS_REL).read_bytes()
    census = json.loads(census_bytes)
    if census.get("schema") != "s2-xu-census-v1":
        raise Refuse("unexpected census schema")
    rows, pins = census_rows(census)
    r7 = json.loads((root / R7_SPEC_REL).read_text(encoding="utf-8"))
    b1 = json.loads((root / B1_SPEC_REL).read_text(encoding="utf-8"))
    runner_pins = {rel: sha256((root / rel).read_bytes()) for rel in RUNNER_FILES}
    for rel, digest in runner_pins.items():
        if b1["files"].get(rel) != digest:
            raise Refuse("runner file differs from the B1 re-relaxation pin: " + rel)
    files, cases, stages = {}, [], {}
    jobs = {(g, arm): [] for g in GROUPS for arm in ARMS}
    for tier, rule in TIERS.items():
        chosen = sorted((r for r in rows if r["state"] in rule["states"]), key=lambda r: (r["metal"], r["job"]))
        if len(chosen) != rule["expected"]:
            raise Refuse("%s: %d rows, rule expects %d" % (tier, len(chosen), rule["expected"]))
        for m in METALS:
            if sum(r["metal"] == m for r in chosen) != rule["per_metal"]:
                raise Refuse("%s: %s does not have %d rows" % (tier, m, rule["per_metal"]))
        for row in chosen:
            record, texts = build_case(row, tier, pins)
            group = [g for g, (t, conv) in GROUPS.items()
                     if t == tier and conv in (None, record["deposited_converged"])]
            if len(group) != 1:
                raise Refuse("no unique launch group for %s %s" % (row["metal"], row["job"]))
            record["launch_group"] = group[0]
            cases.append(record)
            for arm in ARMS:
                name, text = texts[arm]
                data = text.encode("utf-8")
                files["runs/%s/%s.in" % (RUN_DIR, name)] = data
                stage = "%s_%s" % (group[0], arm)
                scf = WALL_MINUTES[stage] * 60 - PROJECTION_SECONDS - 300
                if not 0 < scf <= 60000:
                    raise Refuse("SCF wall outside the runner bound for " + stage)
                jobs[(group[0], arm)].append({
                    "dir": RUN_DIR, "job": name, "sha256": sha256(data), "nk": NK,
                    "scf_seconds": scf, "projection_seconds": PROJECTION_SECONDS,
                    "max_iterations": MAX_ITERATIONS, "recipe": "relax", "role": "corpus_escape",
                    "arm": arm, "tier": tier, "launch_group": group[0], "metal": row["metal"],
                    "census_job": row["job"], "locked_axis": record["locked_axis"],
                    "source_output": row["output"], "source_output_sha256": record["deposited_output_sha256"]})
    for (group, arm), rows_ in jobs.items():
        stage = "%s_%s" % (group, arm)
        manifest = "runs/m_%s_%s.txt" % (TAG, stage)
        files[manifest] = manifest_text(stage, rows_, r7["exclusions"], decision).encode("utf-8")
        stages[stage] = {"kind": "relax", "manifest": manifest, "concurrency": len(rows_),
                         "wall_minutes": WALL_MINUTES[stage], "jobs": rows_}
    if sorted(len(g["jobs"]) for g in stages.values()) != [4, 4, 6, 6, 20, 20]:
        raise Refuse("launch groups do not split 10 + 20 cases as 6 + 4 + 20")
    ceilings = {s: len(g["jobs"]) * g["wall_minutes"] * 128 // 60 for s, g in stages.items()}
    pinned = {p: sha256(d) for p, d in files.items()}
    pinned.update(runner_pins)
    spec = {
        "schema": "research-batch-2026-09-16",
        "np": 128,
        "exclusions": r7["exclusions"],
        "date": DATE,
        "design": DESIGN,
        "decision_ref": ("Frank, %s: \"%s\"" % (decision["date"], decision["words"])) if decision else
                        "NOT LICENSED: awaiting Frank's decision",
        "status": "exploratory, post-census; results reported whatever they show",
        "allocation": {"account": "che260157", "partition": "wholenode", "cores_per_task": 128,
                       "balance_cpu_su_2026_11_01": 9963.3,
                       "committed_running_array_21852915_cpu_su_estimate": 300,
                       "stage_ceilings_cpu_su": ceilings,
                       "group_ceilings_cpu_su": {g: ceilings[g + "_held"] + ceilings[g + "_escape"] for g in GROUPS}},
        "launch_groups": {g: {"tier": t, "deposited_converged": c, "stages": [g + "_held", g + "_escape"]}
                          for g, (t, c) in GROUPS.items()},
        "qe_binaries_sha256": r7["qe_binaries_sha256"],
        "files": dict(sorted(pinned.items())),
        "pseudo_md5": dict(sorted(RUN_MD5.items())),
        "pseudo_substitution": {"decision": "Frank, 2026-11-01: current GBRV v1.5 (deposited files no longer distributed)", "source": "https://www.physics.rutgers.edu/gbrv/all_pbe_UPF_v1.5.tar.gz",
                                "deposited_md5": dict(sorted(PSEUDO_MD5.items())),
                                "map": {k: v[0] for k, v in sorted(SUBSTITUTE.items())}},
        "stages": stages,
    }
    spec_bytes = (json.dumps(spec, indent=2) + "\n").encode("utf-8")
    files[PACKAGE + "/launch_spec.json"] = spec_bytes
    files[SLURM_REL] = slurm_text(sha256(spec_bytes), runner_pins["src/dft/research_batch_seeded.py"],
                                  list(stages)).encode("utf-8")
    table = {"schema": "corpus-escape-cases-v1", "date": DATE, "design": DESIGN,
             "census": {"path": CENSUS_REL, "sha256": sha256(census_bytes)},
             "corpus_root_default": str(CORPUS), "selection": {t: dict(v) for t, v in TIERS.items()},
             "launch_groups": {g: {"tier": t, "deposited_converged": c} for g, (t, c) in GROUPS.items()},
             "displacement_A": DISPLACEMENT_A, "deviations": DEVIATIONS, "nk": NK,
             "wall_minutes": WALL_MINUTES, "stage_ceilings_cpu_su": ceilings, "cases": cases}
    files[PACKAGE + "/cases.json"] = (json.dumps(table, indent=2) + "\n").encode("utf-8")
    return files


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--check", action="store_true", help="compare a fresh build with the files on disk")
    p.add_argument("--replace", action="store_true", help="overwrite differing files this builder owns")
    p.add_argument("--decision", help="Frank's words licensing the launch (written into the manifests and spec)")
    p.add_argument("--decision-date", default=DATE)
    a = p.parse_args(argv)
    decision = {"words": a.decision, "date": a.decision_date} if a.decision else None
    try:
        files = build(ROOT, decision)
    except Refuse as error:
        print("REFUSE: " + str(error))
        return 2
    problems, written = [], []
    for rel, data in files.items():
        if b"\r" in data:
            raise SystemExit("CR byte in " + rel)
        path = ROOT / rel
        if a.check:
            if not path.exists() or path.read_bytes() != data:
                problems.append(rel)
            continue
        if path.exists() and path.read_bytes() == data:
            continue
        if path.exists() and not a.replace:
            raise SystemExit("refusing to overwrite a differing file (use --replace): " + rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(data)
        written.append(rel)
    print(json.dumps({"files": len(files), "mismatches": problems, "written": len(written),
                      "spec_sha256": sha256(files[PACKAGE + "/launch_spec.json"]),
                      "licensed": bool(decision)}, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
