#!/usr/bin/env python3
"""Shared machinery for the Amendment-5 LIT deck generators (docs/43 A5.2 / A5.3).

Why this module exists
----------------------
`build_lit2_ruo2_ladder.py` and `build_lit3_ooh_anatomy.py` are two
implementations of the emission discipline `build_cellsym_pilot.py` established
for block 1A: pre-registration anchors checked before anything is built, an
emit-then-guard path that re-reads the bytes about to be written rather than
trusting the code that wrote them, the queue_r1.sh manifest format, and the
measured cost model. The pieces that ARE that discipline live here once.
Everything REGISTERED (states, thresholds, geometry choices) stays in the two
builders, where it can be read line-by-line against docs/43.

Nothing in this module launches anything. Both builders mark every manifest
NOT-DEPLOYED: docs/43 A5.7 -- "LIT decks queue only after the 1A manifest on a
box is drained, or on a separately provisioned box" -- and launch authority is
Frank's, not this code's.
"""
from __future__ import annotations

import hashlib
import math
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from probe_decks import parse_input_deck  # noqa: E402
from build_cellsym_pilot import (  # noqa: E402
    DOC43, DOC43_PATH, MIN_BOND_A, MIN_OFFPLANE_DY_A,
    _FORBIDDEN, _CHECK_KEYS, _scalars,
    parse_input_deck_text, min_distance)

#: queue geometry shared with block 1A: the LIT jobs run on the same fleet boxes
#: (23.04 usable cores), NP must be an exact multiple of every -nk (hard rule 4).
NP_LONG = 20          # manifest-B configuration: one job at a time, full ranks
NCONC_LONG = 1


def prereg_check(prereg: dict, tag: str) -> dict:
    """Refuse to build if docs/43 no longer says what a PREREG table claims.

    Same two-layer check as build_cellsym_pilot._prereg_check (whose round-2
    finding N1 and verify-round drift finding are the reason both layers exist):
    (1) every anchor substring must still be present in docs/43; (2) every
    numeric value must literally appear inside its own anchor text, so the value
    cannot drift away from the clause that pins it.
    """
    if not os.path.exists(DOC43_PATH):
        raise SystemExit(f"refusing to build {tag}: {DOC43} not found at "
                         f"{DOC43_PATH}. These decks implement that "
                         "pre-registration; they will not build without it.")
    txt = open(DOC43_PATH, encoding="utf-8").read()
    missing = [(k, sec, anc) for k, (_, sec, anc) in prereg.items()
               if anc not in txt]
    if missing:
        lines = "\n".join(f"    {k}  ({DOC43} {sec})  anchor not found: {anc!r}"
                          for k, sec, anc in missing)
        raise SystemExit(f"refusing to build {tag}: docs/43 anchors moved. "
                         "Re-read the builder against the pre-registration; "
                         "never patch the anchor.\n" + lines)
    drift = []
    for k, (v, sec, anc) in prereg.items():
        vals = ()
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            vals = (v,)
        elif isinstance(v, tuple) and v and all(
                isinstance(x, (int, float)) and not isinstance(x, bool)
                for x in v):
            vals = v
        for x in vals:
            forms = {f"{x}", f"{x:g}", f"{abs(x):g}",
                     f"{float(x):.2f}".rstrip("0").rstrip(".")}
            if not any(f in anc for f in forms):
                drift.append(f"    {k}: value {x} does not appear in its "
                             f"anchor {anc!r}")
    if drift:
        raise SystemExit(f"refusing to build {tag}: a PREREG value drifted "
                         "away from the anchor that pins it. Change docs/43 by "
                         "amendment, then the anchor, then the value -- never "
                         "the value alone.\n" + "\n".join(drift))
    return {k: dict(value=v, clause=f"{DOC43} {sec}", anchor=anc)
            for k, (v, sec, anc) in prereg.items()}


def guard_deck(text: str, src_path: str, job: str, expect: dict) -> dict:
    """Refuse to write unless every quantity we did not intend to change is equal.

    Compares the deck we are ABOUT to write, re-parsed from its own bytes,
    against the production deck it was derived from. `expect` declares what IS
    intended to differ:

      allowed          extra scalar keys allowed to differ (on top of the
                       always-per-job prefix/outdir/nat/calculation and the
                       symmetry-arm nosym/noinv)
      expected_mags    starting_magnetization dict the emitted deck must carry
                       (None = must equal the source deck's)
      cell_mult        a1 multiplier vs the source cell (a2/a3 must not move)
      kmesh            required Monkhorst-Pack mesh, no offset
      nat / flags      exact atom count and per-atom constraint flags
      dy_checks        [(atom_index, reference_y)] -- the off-plane start must
                       be PERFORMED: max |y_i - ref_y| >= 0.30 A (docs/43
                       s2-A.1; `nosym` on an exactly symmetric input does
                       nothing, lessons.md 2026-08-09). Empty list + \
                       require_offplane=False for fixed-geometry children.
      max_seconds      required value, present exactly once, inside &CONTROL
    """
    def die(msg):
        raise SystemExit(f"refusing to write {job}: {msg}")

    allowed = {"prefix", "outdir", "nat", "nosym", "noinv",
               "calculation"} | set(expect.get("allowed", ()))
    src = open(src_path, encoding="utf-8").read()
    a, b = _scalars(src), _scalars(text)
    for k in _CHECK_KEYS:
        if k in allowed:
            continue
        if a[k] != b[k]:
            die(f"{k} changed {a[k]!r} -> {b[k]!r} vs {src_path}")

    for k in _FORBIDDEN:
        if re.search(rf"^\s*{k}\s*=", text, re.M | re.I):
            die(f"deck carries forbidden key {k!r}")

    ms_hits = re.findall(r"^\s*max_seconds\s*=\s*(\d+)\s*$", text, re.M)
    if len(ms_hits) != 1:
        die(f"{len(ms_hits)} max_seconds lines, expected exactly 1")
    if int(ms_hits[0]) != int(expect["max_seconds"]):
        die(f"max_seconds {ms_hits[0]} != computed {expect['max_seconds']}")
    if text.index("max_seconds") > text.index("&SYSTEM"):
        die("max_seconds is outside &CONTROL")

    d_src, d_new = parse_input_deck(src_path), parse_input_deck_text(text)

    if d_src["species"] != d_new["species"]:
        die(f"ATOMIC_SPECIES changed {d_src['species']} -> {d_new['species']}")
    if d_src["hubbard"] != d_new["hubbard"]:
        die(f"HUBBARD changed {d_src['hubbard']} -> {d_new['hubbard']}")
    exp_mags = expect.get("expected_mags")
    if exp_mags is None:
        if d_src["mags"] != d_new["mags"]:
            die(f"starting_magnetization changed {d_src['mags']} -> "
                f"{d_new['mags']}")
    else:
        if d_new["mags"] != exp_mags:
            die(f"starting_magnetization {d_new['mags']} != declared "
                f"{exp_mags}")

    for i in (1, 2):
        for j in range(3):
            if abs(d_src["cell"][i][j] - d_new["cell"][i][j]) > 1e-9:
                die(f"cell vector a{i+1} changed -- vacuum/lateral b must "
                    "not move")
    r = d_new["cell"][0][0] / d_src["cell"][0][0]
    if abs(r - expect["cell_mult"]) > 1e-9:
        die(f"a1 multiplier {r:.6f}, expected {expect['cell_mult']}")
    if abs(d_new["cell"][0][1]) + abs(d_new["cell"][0][2]) > 1e-9:
        die("a1 acquired off-diagonal components")

    if tuple(d_new["kpts"][1][:3]) != tuple(expect["kmesh"]):
        die(f"k-mesh {d_new['kpts'][1][:3]} != declared {list(expect['kmesh'])}")
    if tuple(d_new["kpts"][1][3:]) != ("0", "0", "0"):
        die(f"k-mesh acquired an offset {d_new['kpts'][1][3:]}")

    nat = len(d_new["positions"])
    if nat != expect["nat"]:
        die(f"nat {nat} != expected {expect['nat']}")
    if d_new["flags"] != list(expect["flags"]):
        for i, (got, want) in enumerate(zip(d_new["flags"], expect["flags"])):
            if got != want:
                die(f"constraint flag of atom {i} is {got!r}, expected {want!r}")
        die(f"{len(d_new['flags'])} constraint flags for {len(expect['flags'])} "
            "expected")

    has_nosym = bool(re.search(r"^\s*nosym\s*=\s*\.true\.", text, re.M | re.I))
    has_noinv = bool(re.search(r"^\s*noinv\s*=\s*\.true\.", text, re.M | re.I))
    if not (has_nosym and has_noinv):
        die("every LIT deck runs the off-plane arm's symmetry treatment; "
            "nosym AND noinv are required (docs/43 A5.7 standing protocol)")

    max_dy = 0.0
    for idx, ref_y in expect.get("dy_checks", ()):
        max_dy = max(max_dy, abs(d_new["positions"][idx][2] - ref_y))
    if expect.get("require_offplane", True):
        if not expect.get("dy_checks"):
            die("require_offplane set but no dy_checks declared -- the "
                "displacement, not the flag, is what breaks the plane")
        if max_dy < MIN_OFFPLANE_DY_A:
            die(f"off-plane start reached only |dy| = {max_dy:.4f} A < "
                f"{MIN_OFFPLANE_DY_A} A -- nosym alone does nothing on an "
                "exactly symmetric input")

    dmin = min_distance(d_new["positions"], d_new["cell"])
    if dmin < MIN_BOND_A:
        die(f"minimum interatomic distance {dmin:.3f} A < {MIN_BOND_A} -- "
            "the assembly overlapped two atoms")

    zext = (max(q[3] for q in d_new["positions"])
            - min(q[3] for q in d_new["positions"]))
    return dict(nat=nat, dmin=round(dmin, 4), z_extent=round(zext, 4),
                vac_gap=round(d_new["cell"][2][2] - zext, 4),
                max_start_dy=round(max_dy, 4))


def insert_max_seconds(text: str, max_seconds: int) -> str:
    """Same placement as build_cellsym_pilot (finding [8](iii)): end of &CONTROL,
    so pw.x stops cleanly and restartably instead of walking to nstep."""
    cut = text.index("\n/\n")
    return text[:cut] + f"\n  max_seconds = {int(max_seconds)}" + text[cut:]


def write_deck(outdir: str, name: str, text: str, dry: bool) -> str:
    """LF-only bytes (hard rule 1: a deck containing CR dies silently in tmux).
    Returns the md5 of the exact bytes (written or would-be-written)."""
    if "\r" in text:
        raise SystemExit(f"refusing to write {name}: deck text contains CR")
    blob = text.encode("utf-8")
    if not dry:
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, name + ".in"), "wb") as fh:
            fh.write(blob)
    return hashlib.md5(blob).hexdigest()


def write_text(path: str, text: str, dry: bool):
    if dry:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def nk_for(nkp: int, np_run: int) -> int:
    """Block-1A pool rule: nk = 2 below 12 k-points, else 4; NP must be an
    exact multiple (hard rule 4) and nk must not exceed the k-point count."""
    nk = 2 if nkp < 12 else 4
    if nk > nkp:
        raise SystemExit(f"-nk {nk} exceeds the {nkp} k-points pw.x will have")
    if np_run % nk:
        raise SystemExit(f"NP={np_run} is not an exact multiple of nk={nk} "
                         "(hard rule 4)")
    return nk


def species_index(deck: dict, symbol: str) -> int:
    """1-based ATOMIC_SPECIES index of `symbol` -- decks order species
    differently per metal (Cr: Cr/H/O; Ru: H/O/Ru), so always look up by name."""
    for i, (s, _, _) in enumerate(deck["species"]):
        if s == symbol:
            return i + 1
    raise SystemExit(f"species {symbol!r} not in deck ({deck['species']})")


def bridging_O_index(slab_pos, n_slab: int) -> int:
    """The bridging O of a rutile MO2(110) slab half: the highest-z O among the
    slab atoms. Verified against the production geometries: the bridging O sits
    ~1.15 A above every other top-layer O (e.g. runs/Cr_slab z=16.95 vs 15.76)."""
    cands = [i for i in range(n_slab) if slab_pos[i][0] == "O"]
    ib = max(cands, key=lambda i: slab_pos[i][3])
    zs = sorted((slab_pos[i][3] for i in cands), reverse=True)
    if len(zs) > 1 and zs[0] - zs[1] < 0.5:
        raise SystemExit("bridging-O detection ambiguous: two O atoms within "
                         f"0.5 A of the top ({zs[0]:.3f} vs {zs[1]:.3f}); "
                         "refusing to guess")
    return ib


def out_status(path: str, calculation: str) -> str:
    """Reuse-table status of an on-disk output. Hard rule 3: JOB DONE is not
    success -- a relax must carry `bfgs converged`, and an SCF failure is
    NOT_SCOREABLE whatever else the file says."""
    if not os.path.exists(path):
        return "PENDING (no .out on disk)"
    txt = open(path, errors="replace").read()
    if "convergence NOT achieved" in txt:
        return "NOT_SCOREABLE (SCF failure)"
    if calculation == "relax" and "bfgs converged" not in txt:
        return "NOT_SCOREABLE (no `bfgs converged`; JOB DONE alone is not " \
               "success)"
    return "CONVERGED"


def ceil_steps(measured: int, mult: float) -> int:
    return int(math.ceil(measured * mult))
