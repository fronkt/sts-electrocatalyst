#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A7_3_SPIN CENSUS READOUT: the equalised sensitivity census, committed BEFORE extraction.

WHY THIS SCRIPT EXISTS, AND WHY NOW (the committed-before-extraction precedent)
-------------------------------------------------------------------------------
docs/66 SS2 row 17 records the precedent: "DISCHARGED-BY-BUILD recorded (extractor
committed 9bd19e1, before any spin-arm Loewdin extraction)". tasks/todo.md's
2026-08-31 builders list names the gap this file closes: "a7_3_spin census readout
script". This readout is committed BEFORE any Stage-1 / CMF seed-search .out
exists, so the selection rule, the floor, the tie-break, the guards and the census
arithmetic are all fixed in code before a single number they will act on is known.
build_a0spin.py's docstring registers the split: "POST-RUN assertions (A13-A17:
k-set, electron count, variational floor, endpoint branch continuity, Stage-0
control pass) live in the readout, not here." This is that readout. Mapping:
CEN-g == A13 (k-set), CEN-h == A14 (electron count), CEN-f == A15 (variational
floor), the guard-3 branch report == A16 (endpoint branch continuity), CEN-n ==
A17 (Stage-0 control pass).

THE SELECTION RULE (registered; docs/43 AMENDMENT 11, A11.R1, elected under the
docs/66 SS1 directive)
-------------------------------------------------------------------------------
[A11.6 SEEDS+SELECTION 2026-08-31: AS PROPOSED, with two dated riders] -- "seed set
S = {0.10, 0.30, 0.50}; selection = lowest converged total energy per (metal,
state, U) across the three seeds AND the banked nspin = 1 energy, hard variational
floor ('must be <= 0' -- equality passes; no additional tolerance is introduced),
ties within 1 meV to the smallest |seed|; both magnetizations reported."
  Rider 1: "extension seed 0.05 is pre-named NOW, for the Ir-slab contingency
  only ... it is not a member of S for any other cell."
  Rider 2: "at the (Ti, s0_OOH, u900) cell the banked null-seed row
  -1298.17043625 Ry (totmag 1.04) is NAMED into the candidate pool as the free
  fifth candidate (docs/62:220-222), under the same selection rule."
The Cr/Mn/Fe analogue (docs/43 A11.R3, [CR/MN/FE SEED SEARCH 2026-08-31: RUNS]):
"Selection: the A11.6-ANALOGUE rule -- lowest converged total energy per (metal,
state, U) across the grid seeds AND the banked FM row as incumbent (these metals
have no nspin = 1 floor; the banked FM energy is the incumbent candidate), ties
within 1 meV to the smallest |seed|. Winners enter the a7_3_spin sensitivity
census ONLY; no banked A0 row is replaced (SSA11.9)."
The variational floor's refusal semantics are docs/61 SSA11.7 guard 2, adopted:
"Any converged candidate landing above its banked nspin = 1 counterpart is a
search failure, rejected, not banked." Floor arithmetic: dE = E(candidate) -
E(incumbent) "must be <= 0" with EQUALITY PASSING (docs/62:86 idiom; docs/66 SS2
row 7: "floor equality passes ('must be <= 0', docs/62:86), no additional
tolerance introduced").
The Ir-slab contingency resolution is FIXED IN ADVANCE (docs/43 A11.R3,
[IR-SLAB CONTINGENCY 2026-08-31]): if no seed (0.10/0.30/0.50, then the pre-named
0.05) clears the floor, "the (Ir, slab, U) cell resolves BY THE SELECTION RULE --
the banked nspin = 1 energy is in the candidate set (A11.6) and the floor passes
equality -- so the equalised row EXISTS, equals the banked nspin = 1 row, and is
reported as EQUALISED-BY-SELECTION(nspin=1) with the full rejection record."

Tie-break seed magnitudes, read from the decks (never a constant): a grid
candidate's |seed| is its own deck's nonzero starting_magnetization; the Rider-2
null row's |seed| is 0.0 (every seed in its deck is 0.0); a Cr/Mn/Fe FM
incumbent's |seed| is its own banked starting_magnetization (0.6 Cr, 0.5 Mn,
0.5/0.1 Fe -- re-read per deck, per state); a Ru/Ir/Ti nspin = 1 incumbent carries
no starting_magnetization and enters the tie-break at |seed| = 0.0 (qe_slab.py's
own fixed-point sentence: nspin = 2 with every seed at zero reproduces the
nspin = 1 answer). The |seed| = 0.0 assignment for the unseeded incumbent is an
interpretation of the registered sentence, disclosed here; it is conservative --
a tie resolves toward the un-polarised row, which can manufacture no spin effect.

WHAT THE CENSUS IS, AND WHAT IT CAN NEVER DO (A11.5, elected)
-------------------------------------------------------------------------------
[A11.5 HEADLINE CENSUS 2026-08-31: AS-BUILT 3-of-6] -- "the as-built 3 of 6
remains the registered score of A7.3 and remains the headline; the spin-equalised
census is a registered sensitivity whose only power is to select which caveat
sentence is true; it cannot promote A7.3 to CONFIRMED". This script therefore:
  * quotes the banked as-built census VERBATIM from docs/figs/a0main_readout.json
    (the banked artifact) and NEVER recomputes or re-scores it (CEN-m);
  * emits the equalised table with sensitivity_only = true and never emits the
    token CONFIRMED for it;
  * makes no denominator election: docs/43 A11.R2 rule (iii) -- "the denominator
    is set solely by the docs/59 SS3c countersignature, never by this table" --
    and the A7.7 middle-band disposition is "never quoted bare".
Census arithmetic: A7.3's quantity is span(c_M)/2 at FIXED endpoints U = 0 and
U = U_max, c_M = dG_OOH - dG_OH. E_slab and every gas reference cancel identically
in c_M (docs/62 SS2: "Delta c_M = Delta E_*OOH - Delta E_*OH exactly"), so
    c_M_equalised(U) = c_M_banked(U)
                     + [ (E_sel_OOH(U) - E_inc_OOH(U))
                       - (E_sel_OH(U)  - E_inc_OH(U)) ] * RY_EV
with the incumbents' banked energies read from runs/a0/main/. CEN-k proves the
cancellation on the bank itself before using it: c_M_banked(U) -
(E_OOH - E_OH)*RY_EV must be one constant across all 12 banked endpoint rows.
D_M = Delta c_M(U_max) - Delta c_M(0) is reported per metal with the registered
A11.3 context (threshold 0.026 eV on >= 2 licensed metals; falsification band
0.005 eV; middle band mapped in advance); this script applies NO P-SPIN-DELTA
verdict -- scoring is the registered act, on the operative denominator.

CONVERGENCE / MOMENTS: THE GATE-(h) RECIPE, VERBATIM
-------------------------------------------------------------------------------
From the h_afm_probe manifest (src/dft/build_ru_afm_probe.py): "converged iff
'convergence has been achieved' >= 1 AND 'convergence NOT achieved' == 0 AND a
final '^!' line exists (success is NEVER 'JOB DONE' alone); E = last '^!';
totmag/absmag = last printed pair."

THE TI GATE (docs/59 SS3c + SS5)
-------------------------------------------------------------------------------
docs/59 carries "[SS3c LICENCE 2026-08-31: GRANTED -- EXECUTED UNDER DIRECTIVE,
COUNTERSIGNATURE PENDING; s0_OH@u900 FIRST among Ti compute]" and the rule that
it "completes only at the entrant's own dated confirmation line in SS5 below --
and NO TI DECK SUBMITS BEFORE THAT LINE EXISTS."
  CEN-b: if any Ti deck is in scope and docs/59 lacks the literal
         '[SS3c LICENCE 2026-08-31: GRANTED' line, this script REFUSES TO RUN.
  CEN-c: while the entrant confirmation line is absent, every Ti row is EXCLUDED
         from the output and reported PENDING-CONFIRMATION instead. The reserved
         template in docs/59 SS5 ("e.g. [SS3c CONFIRMED 2026-__-__ ...]") carries
         a placeholder date and IS NOT a confirmation: the detector requires
         '[SS3c CONFIRMED' followed by a fully dated 20xx-xx-xx stamp.
         Additionally, while unconfirmed, any Ti .out beyond the two banked
         __sp2null controls is a VIOLATION (a Ti submission happened before the
         line) and the readout refuses.
(SS is the section sign in the actual docs; the search literals in code carry the
real character.)

READ-ONLY CONTRACT AND OUTPUT SEMANTICS
-------------------------------------------------------------------------------
This is a READOUT: it opens every input read-only, md5-logs each file at first
read and re-verifies the whole log before exiting (CEN-a) -- banked evidence is
inviolate. The human-readable report goes to stdout; the JSON report goes to the
path given on argv, which is REFUSED if it lies under runs/ or docs/ (the banked
artifact docs/figs/a0main_readout.json lives there) or if it already exists
(no overwrite, the S1-c posture). The JSON carries no timestamp; two runs on the
same tree are byte-identical (the determinism proof is md5-comparing a double
run).

FATAL ASSERTIONS (CEN-a .. CEN-n; every failure dies, style of build_a0spin_s1)
-------------------------------------------------------------------------------
CEN-a  read-only sweep: every file read under runs/ and docs/figs is md5-logged
       at first read and unchanged at exit; the JSON path is refused under
       runs/ or docs/ and refused if it exists
CEN-b  SS3c licence gate: Ti decks in scope require the GRANTED line, else the
       whole readout refuses to run
CEN-c  SS3c confirmation gate: no dated CONFIRMED line -> Ti rows excluded,
       PENDING-CONFIRMATION; a non-null Ti .out while unconfirmed is fatal
CEN-d  per-deck sanity, read from EACH DECK'S OWN ATOMIC_SPECIES (never a
       constant): the single nonzero starting_magnetization sits on the metal's
       own index; the seed equals the stem's sp2mNNN token; an exactly-0.0 seed
       is separately fatal EXCEPT the two whitelisted __sp2null controls
       (A11.6: "Exactly 0.0 is separately fatal ... the only whitelisted
       exemption"); endpoints u000/u900 only; sp2m005 legal at (Ir, slab, U)
       only (Rider 1); CMF incumbents are nspin = 2 FM decks with u000 == u900
       banked seed (the A11.R3 coverage convention re-verified); Ru/Ir/Ti
       incumbents carry no nspin key
CEN-e  convergence by the gate-(h) recipe, nothing weaker
CEN-f  variational floor: dE = E(candidate) - E(incumbent) must be <= 0,
       equality passes, no tolerance; violators are REJECT-FLOOR, never banked
CEN-g  symmetry/k-set guard (docs/61 SSA11.7 guard 1): candidate .out matches
       its incumbent .out on the Sym. Ops. line and the k-point count, else the
       row is disqualified from being differenced
CEN-h  electron-count identity: candidate 'number of electrons' equals the
       incumbent's
CEN-i  selection exactly by the registered rule (lowest converged E across the
       admitted pool AND the incumbent; ties within 1 meV to smallest |seed|)
CEN-j  Rider 2: the (Ti, s0_OOH, u900) pool contains the banked null-seed row,
       whose .out must reproduce the registered literal -1298.17043625 Ry
CEN-k  reference-cancellation constant: c_M_banked(U) - (E_OOH - E_OH)*RY_EV is
       one constant across all 12 banked endpoint rows (spread <= 1e-6 eV)
CEN-l  census arithmetic identity: with every selection at the incumbent the
       equalised row equals the as-built row exactly
CEN-m  the as-built census is quoted verbatim from the banked artifact, whose
       status must still read the banked 'NOT MET' at 3 over -- any drift means
       the artifact this sensitivity is anchored to has moved, and dies
CEN-n  Stage-0 control pass (A17): the 8 P11 reproductions match
       build_a0spin.P11_REF to <= 5e-6 Ry and the docs/62 SS4 floor deltas to
       <= 0.005 meV; the Ir slab candidate is REFUSED BY THE FLOOR (+0.583 meV,
       REJECT, exactly as docs/61 SSA11.7 predicted and docs/62 SS4 banked); the
       null controls reproduce docs/62 SS5 (slab: |dE| <= 25x conv_thr read from
       the deck, |totmag| ~ 0; s0_OOH: BREAKS, dE = -153.072 meV, totmag 1.04)

USAGE
-----
    python src/dft/a0spin_census.py                 # stdout report only
    python src/dft/a0spin_census.py OUT.json        # + JSON report (new file,
                                                    #   never under runs/ or docs/)

Any other argument is refused.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import build_a0spin as B  # P11_REF, species_order, ntyp_of -- imported, not copied
import qe_qc

RY_EV = qe_qc.RY_EV       # never hard-coded here (build_a0spin.py posture)

MAIN = os.path.join(ROOT, "runs", "a0", "main")
SPIN = os.path.join(ROOT, "runs", "a0", "spin")
DOCS59 = os.path.join(ROOT, "docs", "59-a0-roster-correction-2026-08-28.md")
BANKED_JSON = os.path.join(ROOT, "docs", "figs", "a0main_readout.json")

#: registered A0-SPIN endpoint tokens (docs/61 SSA11.2: Xu anchors excluded).
UTOKS = ("u000", "u900")
#: registered seed grid S (A11.6, elected AS PROPOSED).
GRID = (0.10, 0.30, 0.50)
#: Rider-1 extension seed, (Ir, slab, U) only.
EXT_SEED = 0.05
#: A11.R6 (2026-09-02): the two pre-named rungs for the sixteen unconverged Ru
#: U = 9 spin rows. Parameters are READ from each rung deck and compared to
#: this table; a rung stem anywhere but a (Ru, state, u900) cell is fatal; a
#: rung-2 deck whose rung-1 twin is missing or converged is fatal. Lexicographic
#: stem order already realises "residual ties to the lowest rung"
#: (stem < stem__rung1 < stem__rung2), so the tie-break code is unchanged.
RUNG_TABLE = {1: dict(beta=0.15, ndim=8.0, maxstep=400.0),
              2: dict(beta=0.075, ndim=16.0, maxstep=600.0)}
RUNG_METAL, RUNG_UTOK = "Ru", "u900"
#: registered a7_3 floor (docs/43:1361-1379) and A11.3 context (docs/43 A11.R1).
A73_FLOOR_V = 0.10
A113_THRESHOLD_EV = 0.026
A113_FALSIFY_EV = 0.005
#: the metal families and their registered cell sets. Ru/Ir/Ti: the equalised
#: arm (4 states -- s0_OH/s0_OOH for a7_3_spin, slab/s0_O for the A7.2 re-read,
#: docs/43 A11.R3 [A7.2 EQUALISED RE-READ]); Cr/Mn/Fe: the seed-search cells
#: (adsorbate states only -- "winners enter the a7_3_spin sensitivity census
#: ONLY").
FAMILY_RIT = ("Ru", "Ir", "Ti")
FAMILY_CMF = ("Cr", "Mn", "Fe")
STATES_RIT = ("slab", "s0_O", "s0_OH", "s0_OOH")
STATES_CMF = ("s0_OH", "s0_OOH")
CM_STATES = ("s0_OH", "s0_OOH")   # the two states c_M is built from (docs/62 SS5.1)

#: the two whitelisted null-seed machinery controls (A11.6: "the only
#: whitelisted exemption"; stems, under runs/a0/spin/Ti/).
NULL_WHITELIST = (("Ti", "slab", "u900"), ("Ti", "s0_OOH", "u900"))
#: Rider 2 (docs/43 A11.R1): the banked null-seed row NAMED into this cell's
#: candidate pool, with its registered literal (verified against the .out, CEN-j).
RIDER2_CELL = ("Ti", "s0_OOH", "u900")
RIDER2_E_RY = -1298.17043625
RIDER2_TOTMAG = 1.04

#: docs/62 SS4 banked floor deltas (meV), the Stage-0 control literals (CEN-n).
S0_FLOOR_MEV = {
    ("Ru", "slab"): -71.934, ("Ru", "s0_O"): -88.041,
    ("Ru", "s0_OH"): -73.640, ("Ru", "s0_OOH"): -66.547,
    ("Ir", "slab"): +0.583, ("Ir", "s0_O"): -173.724,
    ("Ir", "s0_OH"): -0.500, ("Ir", "s0_OOH"): -9.226,
}
#: docs/62 SS5 null-control literals (CEN-n).
NULL_SLAB_DE_MEV = +0.339      # even-electron control, <= 25x conv_thr
NULL_OOH_DE_MEV = -153.072     # odd-electron: BREAKS, SPIN-UNSTABLE lower bound

TIE_RY = 1.0e-3 / RY_EV        # "ties within 1 meV", expressed in Ry

#: docs/59 gate literals (CEN-b / CEN-c). The section sign is the real character.
GRANT_LIT = "[§3c LICENCE 2026-08-31: GRANTED"
CONFIRM_RE = re.compile(r"\[§3c CONFIRMED\s+20\d{2}-\d{2}-\d{2}")

#: md5 log of every file read (CEN-a): path -> md5 at first read.
READ_LOG: dict[str, str] = {}


def die(msg: str) -> None:
    sys.exit("READOUT REFUSED: " + msg)


def md5_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def read_logged(path: str) -> str:
    """Read a banked input read-only, md5-logging it at first read (CEN-a)."""
    if not os.path.exists(path):
        die("banked input missing: %s" % path)
    if path not in READ_LOG:
        READ_LOG[path] = md5_file(path)
    return io.open(path, encoding="utf-8", errors="replace").read()


def sweep_read_log() -> int:
    """CEN-a: every logged input unchanged on disk at exit."""
    for p, h in sorted(READ_LOG.items()):
        if md5_file(p) != h:
            die("CEN-a BANKED INPUT ALTERED DURING READOUT: %s" % p)
    return len(READ_LOG)


# --------------------------------------------------------------------------
# docs/59 gates (pure function over the text -- testable on fixtures)
# --------------------------------------------------------------------------

def gates_from_text(txt: str) -> dict:
    """CEN-b/CEN-c detectors. The docs/59 SS5 reserved template ('e.g.
    [SS3c CONFIRMED 2026-__-__ ...]') has a placeholder date and must NOT
    register as a confirmation; the detector requires a fully dated stamp."""
    return {
        "licence_granted": GRANT_LIT in txt,
        "confirmed": bool(CONFIRM_RE.search(txt)),
    }


# --------------------------------------------------------------------------
# pw.x output parsing -- the gate-(h) recipe, verbatim
# --------------------------------------------------------------------------

def parse_pw_out(txt: str) -> dict:
    """Gate-(h) recipe (h_afm_probe manifest, quoted in the module docstring):
    converged iff 'convergence has been achieved' >= 1 AND 'convergence NOT
    achieved' == 0 AND a final '^!' line exists (success is NEVER 'JOB DONE'
    alone); E = last '^!'; totmag/absmag = last printed pair."""
    ach = txt.count("convergence has been achieved")
    nach = txt.count("convergence NOT achieved")
    bang = re.findall(r"^!\s+total energy\s+=\s+(-?\d+\.\d+)\s+Ry", txt, re.M)
    tm = re.findall(r"total magnetization\s+=\s+(-?\d+\.\d+)", txt)
    am = re.findall(r"absolute magnetization\s+=\s+(-?\d+\.\d+)", txt)
    ne = re.findall(r"number of electrons\s+=\s+(-?\d+\.\d+)", txt)
    sym = re.findall(r"(\d+)\s+Sym\. Ops\.", txt)
    nosym = "No symmetry found" in txt
    kp = re.findall(r"number of k points\s*=\s*(\d+)", txt)
    return dict(
        converged=(ach >= 1 and nach == 0 and len(bang) >= 1),
        energy_ry=(float(bang[-1]) if bang else None),
        totmag=(float(tm[-1]) if tm else None),
        absmag=(float(am[-1]) if am else None),
        n_electrons=(float(ne[-1]) if ne else None),
        sym_line=("No symmetry found" if nosym
                  else ("%s Sym. Ops." % sym[-1] if sym else None)),
        k_points=(int(kp[-1]) if kp else None),
    )


def load_out(path: str) -> dict:
    return parse_pw_out(read_logged(path))


# --------------------------------------------------------------------------
# deck reading -- species/seed ALWAYS from the deck's own ATOMIC_SPECIES
# --------------------------------------------------------------------------

def deck_info(path: str, metal: str) -> dict:
    """CEN-d per-deck facts, read from the deck itself, never from a constant.
    The metal's species index is STATE- and METAL-dependent (Cr/Fe sort before
    H, Mn/Ru/Ir/Ti after -- docs/61 SSA11.8 item 2), so it is re-read here off
    every deck's own ATOMIC_SPECIES block."""
    txt = read_logged(path)
    order = B.species_order(txt)
    if metal not in order:
        die("CEN-d %s: %s not in ATOMIC_SPECIES %r" % (path, metal, order))
    ntyp = B.ntyp_of(txt)
    if len(order) != ntyp:
        die("CEN-d %s: ntyp %d but %d species" % (path, ntyp, len(order)))
    midx = order.index(metal) + 1
    nspin = re.findall(r"^\s*nspin\s*=\s*(\d+)", txt, re.M)
    sm = re.findall(r"^\s*starting_magnetization\((\d+)\)\s*=\s*(-?\d+\.?\d*)",
                    txt, re.M)
    seeds = {int(i): float(v) for i, v in sm}
    nz = {i: v for i, v in seeds.items() if v != 0.0}
    ct = re.search(r"^\s*conv_thr\s*=\s*([\d.]+)[dDeE]([+-]?\d+)", txt, re.M)
    conv_thr = float("%se%s" % (ct.group(1), ct.group(2))) if ct else None
    return dict(species=order, ntyp=ntyp, metal_index=midx,
                nspin=(int(nspin[-1]) if nspin else 1),
                seeds=seeds, nonzero=nz, conv_thr=conv_thr)


def seed_of_stem(stem: str):
    """('sp2m050' -> 0.50, 'sp2null' -> None). Grammar of build_a0spin/_s1,
    plus the A11.R6 rung suffix '__rung1' / '__rung2' (2026-09-02): rung=0 for
    a plain stem, parent=the stem without its suffix."""
    m = re.match(r"^(slab|s0_O|s0_OH|s0_OOH)__(u\d{3})__sp2(m(\d{3})|null)"
                 r"(?:__rung([12]))?$", stem)
    if not m:
        return None
    rung = int(m.group(5)) if m.group(5) else 0
    return dict(state=m.group(1), utok=m.group(2),
                null=(m.group(3) == "null"),
                seed=(None if m.group(3) == "null" else int(m.group(4)) / 100.0),
                rung=rung,
                parent=(stem[:-len("__rung%d" % rung)] if rung else stem))


def check_rung_deck(metal: str, path: str, p: dict) -> None:
    """A11.R6 CEN-d for a rung stem: cell scope, parameters against the
    registered table, byte-identity to the rung-0 parent outside the licensed
    lines (prefix, mixing_beta, mixing_ndim, electron_maxstep), and the
    rung-2-only-after-rung-1-failed rule."""
    if not (metal == RUNG_METAL and p["utok"] == RUNG_UTOK):
        die("CEN-d %s: A11.R6 rung stem outside the twelve (Ru, state, u900) "
            "cells" % path)
    want = RUNG_TABLE[p["rung"]]
    txt = read_logged(path)

    def num(key, default=None):
        m = re.search(r"^\s*%s\s*=\s*([-+\d.dDeE]+)" % key, txt, re.M)
        if not m:
            return default
        return float(m.group(1).replace("d", "e").replace("D", "e"))

    got = dict(beta=num("mixing_beta"), ndim=num("mixing_ndim", 8.0),
               maxstep=num("electron_maxstep"))
    for k in ("beta", "ndim", "maxstep"):
        if got[k] is None or abs(got[k] - want[k]) > 1e-9:
            die("CEN-d %s: rung %d %s = %r, registered %r (A11.R6)"
                % (path, p["rung"], k, got[k], want[k]))
    ppath = os.path.join(os.path.dirname(path), p["parent"] + ".in")
    if not os.path.exists(ppath):
        die("CEN-d %s: rung deck without its rung-0 parent %s" % (path, ppath))
    ptxt = read_logged(ppath)
    lic = re.compile(r"^\s*(prefix|mixing_beta|mixing_ndim|electron_maxstep)\s*=")
    if [l for l in txt.splitlines() if not lic.match(l)] != \
            [l for l in ptxt.splitlines() if not lic.match(l)]:
        die("CEN-d %s: a line outside the licensed rung lines differs from the "
            "rung-0 parent (A11.R6)" % path)
    m = re.search(r"^\s*prefix\s*=\s*'([^']+)'", txt, re.M)
    if not m or m.group(1) != "%s__rung%d" % (p["parent"], p["rung"]):
        die("CEN-d %s: rung prefix does not equal the rung stem" % path)
    if p["rung"] == 2:
        r1 = os.path.join(os.path.dirname(path), p["parent"] + "__rung1.out")
        if not os.path.exists(r1) or parse_pw_out(read_logged(r1))["converged"]:
            die("CEN-d %s: rung 2 exists but rung 1 is missing or CONVERGED -- "
                "A11.R6 licenses rung 2 only on rows rung 1 leaves unconverged"
                % path)


def check_candidate_deck(metal: str, path: str, stem: str) -> dict:
    """CEN-d on one candidate .in under runs/a0/spin/<metal>/."""
    p = seed_of_stem(stem)
    if p is None:
        die("CEN-d unregistered stem grammar under the arm's tree: %s" % path)
    if p["utok"] not in UTOKS:
        die("CEN-d %s: U token %s is outside the registered endpoints %s "
            "(docs/61 SSA11.2: interior/Xu rungs are not this arm's cells)"
            % (path, p["utok"], list(UTOKS)))
    info = deck_info(path, metal)
    if info["nspin"] != 2:
        die("CEN-d %s: candidate deck is not nspin = 2" % path)
    if sorted(info["seeds"]) != list(range(1, info["ntyp"] + 1)):
        die("CEN-d %s: starting_magnetization lines not contiguous 1..ntyp" % path)
    if p["null"]:
        if (metal, p["state"], p["utok"]) not in NULL_WHITELIST:
            die("CEN-d %s: a __sp2null deck outside the two whitelisted "
                "machinery controls -- 'Exactly 0.0 is separately fatal' "
                "(A11.6) and the whitelist is by stem, never by silence" % path)
        if info["nonzero"]:
            die("CEN-d %s: null control carries a nonzero seed" % path)
    else:
        if len(info["nonzero"]) != 1:
            die("CEN-d %s: %d nonzero seeds, need exactly 1 (an all-zero seed "
                "block on a non-null stem is the separately-fatal 0.0 seed of "
                "A11.6)" % (path, len(info["nonzero"])))
        (idx, val), = info["nonzero"].items()
        if idx != info["metal_index"]:
            die("CEN-d %s: seed on species index %d but this deck's own "
                "ATOMIC_SPECIES puts %s at %d -- the state-dependent-index "
                "blocker" % (path, idx, metal, info["metal_index"]))
        if abs(val - p["seed"]) > 1e-9:
            die("CEN-d %s: deck seed %s != stem token %s" % (path, val, p["seed"]))
        if abs(p["seed"] - EXT_SEED) < 1e-9 and not (metal == "Ir"
                                                     and p["state"] == "slab"):
            die("CEN-d %s: extension seed 0.05 is pre-named for the Ir-slab "
                "contingency ONLY and 'is not a member of S for any other "
                "cell' (A11.R1 Rider 1)" % path)
        if p["seed"] not in GRID and abs(p["seed"] - EXT_SEED) > 1e-9:
            die("CEN-d %s: seed %s is not in the registered set S nor the "
                "pre-named extension" % (path, p["seed"]))
        if p["rung"]:
            check_rung_deck(metal, path, p)          # A11.R6, 2026-09-02
    return dict(stem_parse=p, info=info)


def check_incumbent_deck(metal: str, state: str, utok: str) -> dict:
    """CEN-d on the incumbent's .in under runs/a0/main/<metal>/."""
    path = os.path.join(MAIN, metal, "%s__%s.in" % (state, utok))
    info = deck_info(path, metal)
    if metal in FAMILY_RIT:
        if info["nspin"] != 1 or info["seeds"]:
            die("CEN-d %s: a Ru/Ir/Ti incumbent must be the banked nspin = 1 "
                "deck (no nspin key, no seeds)" % path)
        inc_seed = 0.0   # the unseeded/unpolarised row (docstring: disclosed)
    else:
        if info["nspin"] != 2 or len(info["nonzero"]) != 1:
            die("CEN-d %s: a Cr/Mn/Fe incumbent must be the banked nspin = 2 "
                "FM deck with exactly one nonzero seed" % path)
        (idx, val), = info["nonzero"].items()
        if idx != info["metal_index"]:
            die("CEN-d %s: FM seed off the metal's own index" % path)
        inc_seed = val
    return dict(path=path, info=info, seed=inc_seed)


# --------------------------------------------------------------------------
# cell machinery
# --------------------------------------------------------------------------

def enumerate_cells():
    cells = []
    for m in FAMILY_RIT:
        for st in STATES_RIT:
            for u in UTOKS:
                cells.append((m, st, u))
    for m in FAMILY_CMF:
        for st in STATES_CMF:
            for u in UTOKS:
                cells.append((m, st, u))
    return cells


def scan_spin_tree() -> dict:
    """Map (metal, state, utok) -> sorted candidate stems; die on strays."""
    found: dict[tuple, list] = {}
    for m in FAMILY_RIT + FAMILY_CMF:
        d = os.path.join(SPIN, m)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith(".projwfc.out"):
                continue
            # 2026-09-01 (A11 wave-1 drain): the arm's tree now also carries
            # the registered A6.5(1) Loewdin artifact <stem>.lowdin.txt (the
            # class runs/a0/main/ has banked since tranche 1), the runner's
            # <stem>.projwfc.in, and preserved failed attempts
            # <stem>.out.<tag>_YYYY-MM-DD (docs/45: a re-run must never read
            # as a first attempt). None is evidence this census reads; they are
            # tolerated by CLASS, never by name, and every other class still
            # dies. No number can depend on this line -- the whitelist gates
            # presence only -- and run A (this code as first committed, with
            # the sidecars moved aside) and run B (this code) are compared in
            # tasks/review/a7_3_spin_census_2026-09-01_run{A,B}*.json.
            if (f.endswith(".lowdin.txt") or f.endswith(".projwfc.in")
                    or re.search(r"\.out\.[A-Za-z0-9]+_\d{4}-\d{2}-\d{2}$", f)):
                continue
            stem, ext = os.path.splitext(f)
            if ext not in (".in", ".out"):
                die("CEN-d unregistered file class under the arm's tree: %s"
                    % os.path.join(d, f))
            p = seed_of_stem(stem)
            if p is None:
                die("CEN-d unregistered stem under the arm's tree: %s"
                    % os.path.join(d, f))
            if ext == ".out" and not os.path.exists(os.path.join(d, stem + ".in")):
                die("CEN-d orphan evidence (a .out with no .in): %s"
                    % os.path.join(d, f))
            if ext == ".in":
                key = (m, p["state"], p["utok"])
                found.setdefault(key, [])
                if stem not in found[key]:
                    found[key].append(stem)
    return found


def required_seeds(metal: str, inc_seed: float):
    """The A11.R3 coverage convention: 'a banked seed equal to a grid member
    covers that cell AT BOTH ENDPOINTS'. For Ru/Ir/Ti the full grid is
    required; for Cr/Mn/Fe the incumbent's own banked seed, when it is a grid
    member, is covered by the incumbent."""
    if metal in FAMILY_RIT:
        return list(GRID)
    return [s for s in GRID if abs(s - inc_seed) > 1e-9]


def build_cell(metal: str, state: str, utok: str) -> dict:
    inc = check_incumbent_deck(metal, state, utok)
    inc_out_path = os.path.join(MAIN, metal, "%s__%s.out" % (state, utok))
    inc_out = load_out(inc_out_path)
    if not inc_out["converged"]:
        die("CEN-e incumbent .out fails the gate-(h) recipe: %s" % inc_out_path)

    # A11.R3 coverage convention re-verified: banked u000 seed == banked u900
    # seed per (metal, state) -- read from the decks, both endpoints.
    if metal in FAMILY_CMF:
        other = "u900" if utok == "u000" else "u000"
        inc2 = check_incumbent_deck(metal, state, other)
        if abs(inc["seed"] - inc2["seed"]) > 1e-9:
            die("CEN-d %s %s: banked seed differs across endpoints (%s vs %s) "
                "-- the A11.R3 coverage convention does not hold" %
                (metal, state, inc["seed"], inc2["seed"]))

    req = required_seeds(metal, inc["seed"])
    stems = scan_spin_tree().get((metal, state, utok), [])

    candidates = []
    admitted = []
    for stem in stems:
        cpath = os.path.join(SPIN, metal, stem + ".in")
        chk = check_candidate_deck(metal, cpath, stem)
        p = chk["stem_parse"]
        rider2 = (p["null"] and (metal, state, utok) == RIDER2_CELL)
        if p["null"] and not rider2:
            continue    # the even-electron null is a control, never a candidate
        seed = 0.0 if p["null"] else p["seed"]
        cand = dict(stem=stem, seed=seed,
                    kind=("null-seed row, NAMED into this pool (A11.R1 Rider 2)"
                          if rider2 else
                          ("rung-%d candidate (A11.R6)" % p["rung"] if p["rung"]
                           else "grid seed")))
        opath = os.path.join(SPIN, metal, stem + ".out")
        if not os.path.exists(opath):
            cand["status"] = "PENDING-RUN"
        else:
            out = load_out(opath)
            cand["totmag"], cand["absmag"] = out["totmag"], out["absmag"]
            if not out["converged"]:
                cand["status"] = "UNCONVERGED"          # CEN-e: recorded, excluded
            else:
                e = out["energy_ry"]
                cand["energy_ry"] = e
                de = e - inc_out["energy_ry"]
                cand["dE_vs_incumbent_meV"] = de * RY_EV * 1000.0
                if rider2 and abs(e - RIDER2_E_RY) > 5e-9:
                    die("CEN-j Rider-2 row %s: parsed %r != registered literal "
                        "%r" % (opath, e, RIDER2_E_RY))
                if de > 0.0:                            # CEN-f: equality passes
                    cand["status"] = ("REJECT-FLOOR (dE > 0: a search failure, "
                                      "rejected, not banked -- docs/61 SSA11.7 "
                                      "guard 2)")
                elif out["sym_line"] != inc_out["sym_line"] or \
                        out["k_points"] != inc_out["k_points"]:
                    cand["status"] = ("DISQUALIFIED-KSET (guard 1: %r/%r vs "
                                      "incumbent %r/%r)"
                                      % (out["sym_line"], out["k_points"],
                                         inc_out["sym_line"], inc_out["k_points"]))
                elif out["n_electrons"] != inc_out["n_electrons"]:
                    cand["status"] = ("DISQUALIFIED-NEL (%r vs incumbent %r)"
                                      % (out["n_electrons"],
                                         inc_out["n_electrons"]))
                else:
                    cand["status"] = "ADMITTED"
                    admitted.append((e, seed, stem))
        candidates.append(cand)

    # CEN-j: the Rider-2 row must actually BE in this cell's pool
    if (metal, state, utok) == RIDER2_CELL:
        if not any("Rider 2" in c["kind"] for c in candidates):
            die("CEN-j the (Ti, s0_OOH, u900) pool lacks the banked null-seed "
                "row named by A11.R1 Rider 2")

    # ---- selection (CEN-i) ------------------------------------------------
    inc_label = ("EQUALISED-BY-SELECTION(nspin=1)" if metal in FAMILY_RIT
                 else "INCUMBENT-FM")
    pool = admitted + [(inc_out["energy_ry"], inc["seed"], "__incumbent__")]
    e_min = min(e for e, _s, _n in pool)
    tied = [c for c in pool if c[0] - e_min <= TIE_RY]
    # ties within 1 meV to the smallest |seed|; residual ties (equal |seed|)
    # resolve to the incumbent first, then lexicographic stem -- deterministic.
    tied.sort(key=lambda c: (abs(c[1]), 0 if c[2] == "__incumbent__" else 1, c[2]))
    win_e, win_seed, win_name = tied[0]
    tie_applied = len(tied) > 1

    built_stems = {c["stem"] for c in candidates if "Rider 2" not in c["kind"]}
    missing_builds = [s for s in req
                      if not any(abs(seed_of_stem(st)["seed"] - s) < 1e-9
                                 for st in built_stems)]
    pending_runs = [c["stem"] for c in candidates if c["status"] == "PENDING-RUN"]

    if missing_builds:
        status = "PENDING-BUILD (grid seeds not yet built: %s)" % \
                 ", ".join("%.2f" % s for s in missing_builds)
    elif pending_runs:
        status = "PENDING-RUN (%d of %d built decks await a .out)" % \
                 (len(pending_runs), len(built_stems))
    elif metal == "Ir" and state == "slab" and not admitted:
        has_ext = any(abs(c["seed"] - EXT_SEED) < 1e-9 for c in candidates)
        if not has_ext:
            status = ("CONTINGENCY-OPEN (no grid seed admitted; the pre-named "
                      "extension seed 0.05 runs next -- A11.R3 IR-SLAB "
                      "CONTINGENCY stage A)")
        else:
            status = "FINAL"
    else:
        status = "FINAL"

    resolution = (inc_label if win_name == "__incumbent__"
                  else "SEEDED(%s)" % win_name)
    sel = dict(status=status,
               rule=("lowest converged total energy across the admitted pool "
                     "AND the incumbent; hard variational floor must be <= 0, "
                     "equality passes; ties within 1 meV to the smallest "
                     "|seed| (A11.R1 [A11.6 SEEDS+SELECTION], and its "
                     "A11.6-ANALOGUE for Cr/Mn/Fe)"),
               winner=("incumbent" if win_name == "__incumbent__" else win_name),
               resolution=resolution,
               energy_ry=win_e, seed=win_seed, tie_break_applied=tie_applied)
    if status != "FINAL":
        sel["note"] = ("PROVISIONAL minimum over what exists today; the FINAL "
                       "selection needs every required grid seed terminal")
    if win_name == "__incumbent__":
        sel["totmag"], sel["absmag"] = inc_out["totmag"], inc_out["absmag"]
    else:
        wc = next(c for c in candidates if c["stem"] == win_name)
        sel["totmag"], sel["absmag"] = wc.get("totmag"), wc.get("absmag")

    return dict(metal=metal, state=state, utok=utok,
                incumbent=dict(kind=("banked nspin = 1 row" if metal in FAMILY_RIT
                                     else "banked FM row (incumbent candidate)"),
                               path=os.path.relpath(inc_out_path, ROOT).replace(os.sep, "/"),
                               energy_ry=inc_out["energy_ry"],
                               seed=inc["seed"],
                               totmag=inc_out["totmag"], absmag=inc_out["absmag"]),
                required_seeds=["%.2f" % s for s in req],
                covered_by_incumbent=(metal in FAMILY_CMF
                                      and any(abs(s - inc["seed"]) < 1e-9
                                              for s in GRID)),
                candidates=candidates, selection=sel)


# --------------------------------------------------------------------------
# Stage-0 controls (CEN-n == the readout's A17)
# --------------------------------------------------------------------------

def stage0_controls() -> dict:
    rows = {}
    for (m, st), ref in sorted(B.P11_REF.items()):
        spath = os.path.join(SPIN, m, "%s__u000__sp2m050.out" % st)
        mpath = os.path.join(MAIN, m, "%s__u000.out" % st)
        s = load_out(spath)
        n1 = load_out(mpath)
        if not (s["converged"] and n1["converged"]):
            die("CEN-n Stage-0 control unconverged under the gate-(h) recipe: "
                "%s / %s" % (spath, mpath))
        if abs(s["energy_ry"] - ref) > 5e-6:
            die("CEN-n %s %s: Stage-0 energy %.8f fails the P11 reproduction "
                "band (banked %.8f, docs/62 SS2 max |dE| 3.21e-6 Ry)"
                % (m, st, s["energy_ry"], ref))
        de_mev = (s["energy_ry"] - n1["energy_ry"]) * RY_EV * 1000.0
        lit = S0_FLOOR_MEV[(m, st)]
        if abs(de_mev - lit) > 0.005:
            die("CEN-n %s %s: floor delta %+.3f meV != docs/62 SS4 literal "
                "%+.3f meV" % (m, st, de_mev, lit))
        rows[f"{m}/{st}"] = dict(
            p11_reproduction="PASS (<= 5e-6 Ry of the banked P11 literal)",
            dE_vs_nspin1_meV=de_mev,
            floor=("REJECT -- refused by the variational floor (dE > 0), "
                   "exactly as docs/61 SSA11.7 predicted and docs/62 SS4 banked"
                   if de_mev > 0.0 else "PASS (dE <= 0)"))
    if "REJECT" not in rows["Ir/slab"]["floor"]:
        die("CEN-n the Ir slab Stage-0 row was NOT refused by the floor -- "
            "the banked REJECT (+0.583 meV) did not reproduce")
    return rows


def null_controls(confirmed: bool) -> dict:
    """docs/62 SS5.2 as authorised by A11.R1 [A11.7 NULL-SEED RE-REGISTRATION]:
    '(a) the index-rule leg PASSES as run; (b) the stability leg is reported,
    not scored -- Ti s0_OOH at U = 9.0: BREAKS, >= 153.07 meV, SPIN-UNSTABLE.
    Numeric tolerance for the leg-(a) reproduction: within <= 25x conv_thr with
    absmag ~ 0, as measured on the even-electron control.'"""
    out = {}
    for st, lit in (("slab", NULL_SLAB_DE_MEV), ("s0_OOH", NULL_OOH_DE_MEV)):
        stem = "%s__u900__sp2null" % st
        ipath = os.path.join(SPIN, "Ti", stem + ".in")
        opath = os.path.join(SPIN, "Ti", stem + ".out")
        info = deck_info(ipath, "Ti")
        if info["nonzero"] or info["nspin"] != 2:
            die("CEN-n null control %s: not an all-zero nspin = 2 deck" % ipath)
        # leg (a): the seed block spans this deck's own ATOMIC_SPECIES exactly
        if sorted(info["seeds"]) != list(range(1, info["ntyp"] + 1)):
            die("CEN-n null control %s: leg (a) fails -- seed lines do not "
                "span 1..ntyp" % ipath)
        o = load_out(opath)
        n1 = load_out(os.path.join(MAIN, "Ti", "%s__u900.out" % st))
        if not (o["converged"] and n1["converged"]):
            die("CEN-n null control unconverged: %s" % opath)
        de_mev = (o["energy_ry"] - n1["energy_ry"]) * RY_EV * 1000.0
        if abs(de_mev - lit) > 0.005:
            die("CEN-n null %s: dE %+.3f meV != docs/62 SS5 literal %+.3f"
                % (st, de_mev, lit))
        if st == "slab":
            if info["conv_thr"] is None or \
                    abs(de_mev) / 1000.0 / RY_EV > 25.0 * info["conv_thr"]:
                die("CEN-n even-electron control outside 25x conv_thr")
            if abs(o["totmag"]) > 0.05:
                die("CEN-n even-electron control totmag %r not ~ 0" % o["totmag"])
            verdict = ("CONTROL-PASS -- leg (a) index rule + leg (b) stable: "
                       "reproduces the banked nspin = 1 row within 25x "
                       "conv_thr at totmag ~ 0 (docs/62 SS5.2)")
        else:
            if abs(o["energy_ry"] - RIDER2_E_RY) > 5e-9:
                die("CEN-n/CEN-j Rider-2 literal drift: %r" % o["energy_ry"])
            if abs(o["totmag"] - RIDER2_TOTMAG) > 0.01:
                die("CEN-n odd-electron control totmag %r != banked 1.04"
                    % o["totmag"])
            verdict = ("CONTROL-BREAKS -- SPIN-UNSTABLE, >= 153.07 meV lower "
                       "bound, reported not scored (docs/62 SS5.2 leg (b))")
        row = dict(verdict=verdict)
        if confirmed:
            row.update(energy_ry=o["energy_ry"], dE_vs_nspin1_meV=de_mev,
                       totmag=o["totmag"], absmag=o["absmag"])
        else:
            row["values"] = ("withheld from this report pending the docs/59 "
                             "SS5 confirmation line (verified internally; "
                             "banked publicly in docs/62 SS5)")
        out[stem] = row
    return out


# --------------------------------------------------------------------------
# the census
# --------------------------------------------------------------------------

def banked_artifact() -> dict:
    j = json.loads(read_logged(BANKED_JSON))
    a73 = j["a7_3"]
    # CEN-m: the artifact this sensitivity anchors to must still be the banked
    # one -- as-built NOT MET with 3 over (docs/43 A11.R2 disclosure (v)).
    if a73["status"] != "NOT MET" or sorted(a73["exceeds"]) != ["Cr", "Fe", "Mn"]:
        die("CEN-m the banked as-built census has moved (status %r, over %r) "
            "-- this readout anchors to the banked artifact and refuses to "
            "run against a drifted one" % (a73["status"], a73["exceeds"]))
    return a73


def cancellation_constant(a73: dict) -> dict:
    """CEN-k: c_M_banked(U) - (E_OOH - E_OH)*RY_EV is ONE constant over all 12
    banked endpoint rows (docs/62 SS2: every reference cancels identically)."""
    ks = []
    for m in FAMILY_RIT + FAMILY_CMF:
        for utok, key in (("u000", "c_M_lo"), ("u900", "c_M_hi")):
            eo = load_out(os.path.join(MAIN, m, "s0_OOH__%s.out" % utok))
            eh = load_out(os.path.join(MAIN, m, "s0_OH__%s.out" % utok))
            if not (eo["converged"] and eh["converged"]):
                die("CEN-k banked endpoint row unconverged for %s %s" % (m, utok))
            ks.append(a73["per_metal"][m][key]
                      - (eo["energy_ry"] - eh["energy_ry"]) * RY_EV)
    spread = max(ks) - min(ks)
    if spread > 1e-6:
        die("CEN-k reference-cancellation constant is NOT constant (spread "
            "%.3e eV) -- the banked artifact and the banked .out energies "
            "disagree" % spread)
    return dict(constant_eV=min(ks), spread_eV=spread, rows=len(ks))


def census(confirmed: bool) -> dict:
    a73 = banked_artifact()
    cancel = cancellation_constant(a73)

    cells: dict[str, dict] = {}
    for (m, st, u) in enumerate_cells():
        if m == "Ti" and not confirmed:
            continue
        cells.setdefault(m, {}).setdefault(st, {})[u] = build_cell(m, st, u)

    per_metal = {}
    for m in FAMILY_CMF + FAMILY_RIT:
        row = dict(as_built={k: a73["per_metal"][m][k]
                             for k in ("c_M_lo", "c_M_hi", "span_over_2_V",
                                       "exceeds_floor", "nspin")})
        if m == "Ti" and not confirmed:
            row["equalised"] = "PENDING-CONFIRMATION"
            row["note"] = ("Ti rows are excluded from this output while the "
                           "entrant's dated confirmation line is absent from "
                           "docs/59 SS5 (the SS3c grant is executed under "
                           "directive but completes only at that line; NO TI "
                           "DECK SUBMITS BEFORE IT EXISTS)")
            per_metal[m] = row
            continue
        cell = {(st, u): cells[m][st][u] for st in CM_STATES for u in UTOKS}
        pend = sorted("%s@%s" % (st, u) for (st, u), c in cell.items()
                      if c["selection"]["status"] != "FINAL")
        if pend:
            row["equalised"] = ("PENDING (non-final cells: %s)" % ", ".join(pend))
        else:
            dc = {}
            for u in UTOKS:
                dc[u] = ((cell[("s0_OOH", u)]["selection"]["energy_ry"]
                          - cell[("s0_OOH", u)]["incumbent"]["energy_ry"])
                         - (cell[("s0_OH", u)]["selection"]["energy_ry"]
                            - cell[("s0_OH", u)]["incumbent"]["energy_ry"])) * RY_EV
            c_lo = row["as_built"]["c_M_lo"] + dc["u000"]
            c_hi = row["as_built"]["c_M_hi"] + dc["u900"]
            half = abs(c_lo - c_hi) / 2.0
            # CEN-l: all-incumbent selections must reproduce the banked row
            if all(cell[(st, u)]["selection"]["winner"] == "incumbent"
                   for st in CM_STATES for u in UTOKS):
                if abs(half - row["as_built"]["span_over_2_V"]) > 1e-12:
                    die("CEN-l equalised != as-built under all-incumbent "
                        "selection on %s" % m)
            wl = {(st, u): cell[(st, u)]["selection"] for st in CM_STATES
                  for u in UTOKS}
            branch = dict(
                winner_seed_lo={st: wl[(st, "u000")]["seed"] for st in CM_STATES},
                winner_seed_hi={st: wl[(st, "u900")]["seed"] for st in CM_STATES},
                totmag_lo={st: wl[(st, "u000")]["totmag"] for st in CM_STATES},
                totmag_hi={st: wl[(st, "u900")]["totmag"] for st in CM_STATES})
            flag = any(wl[(st, "u000")]["seed"] != wl[(st, "u900")]["seed"]
                       for st in CM_STATES)
            branch["flag"] = (
                "REVIEW-REQUIRED -- endpoint winners differ in seed; docs/61 "
                "SSA11.7 guard 3: a pair whose winners sit in different "
                "magnetic branches is BRANCH-CONDITIONAL and may not be "
                "scored into a span (adjudication is the guard's, reported "
                "here, never auto-cleared)" if flag else
                "no indicator (same winning seed at both endpoints; moments "
                "reported for the guard-3 reading)")
            row["equalised"] = dict(
                c_M_lo=c_lo, c_M_hi=c_hi, span_over_2_V=half,
                exceeds_floor=bool(half > A73_FLOOR_V),
                dc_M_lo_eV=dc["u000"], dc_M_hi_eV=dc["u900"],
                D_M_eV=dc["u900"] - dc["u000"],
                branch_guard=branch)
        per_metal[m] = row

    over_eq = sorted(m for m, r in per_metal.items()
                     if isinstance(r["equalised"], dict)
                     and r["equalised"]["exceeds_floor"])
    n_final = sum(1 for r in per_metal.values() if isinstance(r["equalised"], dict))

    return dict(
        artifact="a7_3_spin -- the spin-equalised sensitivity census",
        sensitivity_only=True,
        headline=("A11.5 (elected): the as-built 3 of 6 remains the registered "
                  "score of A7.3 and remains the headline; this census is a "
                  "registered sensitivity whose only power is to select which "
                  "caveat sentence is true; it cannot promote A7.3 to "
                  "CONFIRMED. A11.R2: a middle-band count is never quoted "
                  "bare; the denominator is set solely by the docs/59 SS3c "
                  "countersignature, never by this table."),
        as_built_headline=dict(status=a73["status"],
                               over=sorted(a73["exceeds"]),
                               artifact="docs/figs/a0main_readout.json",
                               conditionality_pointer="a7_3.conditionality in "
                                                      "the banked artifact "
                                                      "travels with any quote"),
        floor_V=A73_FLOOR_V,
        p_spin_delta_context=dict(
            threshold_eV=A113_THRESHOLD_EV, falsification_eV=A113_FALSIFY_EV,
            note=("registered context only (docs/43 A11.R1 [A11.3 THRESHOLD "
                  "2026-08-31: 0.026 eV; FALSIFICATION 0.005 eV]); this "
                  "readout reports measured D_M and applies NO P-SPIN-DELTA "
                  "verdict -- scoring is the registered act on the operative "
                  "denominator")),
        reference_cancellation=cancel,
        per_metal=per_metal,
        equalised_over_floor=dict(
            metals=over_eq, n_final_rows=n_final,
            note=("sensitivity count over FINAL rows only; NEVER a "
                  "confirmation count (A11.5) and never quoted bare "
                  "(A11.R2)")),
        cells=cells)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def refuse_bad_out_path(out_path: str) -> str:
    ap = os.path.abspath(out_path)
    for banned in (os.path.join(ROOT, "runs"), os.path.join(ROOT, "docs")):
        if os.path.normcase(ap).startswith(os.path.normcase(banned + os.sep)) \
                or os.path.normcase(ap) == os.path.normcase(banned):
            die("CEN-a output path %s is inside %s -- the banked trees are "
                "read-only to this readout" % (out_path, banned))
    if os.path.exists(ap):
        die("CEN-a refusing to overwrite existing output %s (pick a new "
            "path; banked evidence and prior reports are never overwritten)"
            % out_path)
    return ap


def main(argv) -> dict:
    out_path = None
    for a in argv:
        if a.startswith("-"):
            die("unsupported argument %r -- this readout takes at most one "
                "JSON output path" % a)
        if out_path is not None:
            die("unsupported extra argument %r" % a)
        out_path = refuse_bad_out_path(a)

    d59 = read_logged(DOCS59)
    gates = gates_from_text(d59)

    # CEN-b -- Ti decks in scope (the two banked null controls are always in
    # scope, and the registered census itself carries Ti cells) => the GRANTED
    # line is a precondition of RUNNING AT ALL.
    # Ti is ALWAYS in scope for this census: the two banked null controls
    # live under runs/a0/spin/Ti and the registered census carries Ti cells.
    ti_ins = sorted(f for f in os.listdir(os.path.join(SPIN, "Ti"))
                    if f.endswith(".in")) if os.path.isdir(
                        os.path.join(SPIN, "Ti")) else []
    if not gates["licence_granted"]:
        die("CEN-b Ti decks are in scope (%d under runs/a0/spin/Ti, and the "
            "registered census carries Ti cells) but docs/59 lacks the "
            "'[SS3c LICENCE 2026-08-31: GRANTED' line -- refusing to run"
            % len(ti_ins))

    confirmed = gates["confirmed"]
    # CEN-c -- while unconfirmed, any Ti .out beyond the two banked null
    # controls means a Ti deck ran before the entrant's line: refuse.
    if not confirmed and os.path.isdir(os.path.join(SPIN, "Ti")):
        for f in sorted(os.listdir(os.path.join(SPIN, "Ti"))):
            if f.endswith(".out") and not f[:-len(".out")].split(".")[0].endswith("__sp2null"):
                die("CEN-c VIOLATION: Ti evidence %s exists but docs/59 SS5 "
                    "carries no dated confirmation line -- 'NO TI DECK "
                    "SUBMITS BEFORE THAT LINE EXISTS'" % f)

    print("A7_3_SPIN CENSUS READOUT -- sensitivity only; the as-built census "
          "is the headline (A11.5)")
    print("  gates: licence_granted=%s confirmed=%s -> Ti rows %s"
          % (gates["licence_granted"], confirmed,
             "included" if confirmed else "EXCLUDED (PENDING-CONFIRMATION)"))

    s0 = stage0_controls()
    nulls = null_controls(confirmed)
    body = census(confirmed)

    print("\nSTAGE-0 CONTROL PASS (CEN-n == A17):")
    for k in sorted(s0):
        r = s0[k]
        print("  %-10s %s  dE=%+9.3f meV  %s"
              % (k, "P11 PASS", r["dE_vs_nspin1_meV"],
                 "FLOOR-REJECT" if "REJECT" in r["floor"] else "floor pass"))
    for k in sorted(nulls):
        print("  Ti/%s: %s" % (k, nulls[k]["verdict"].split(" -- ")[0]))

    print("\nTHE a7_3_spin TABLE (span(c_M)/2 vs %.2f V; as-built quoted "
          "verbatim from the banked artifact):" % A73_FLOOR_V)
    for m in ("Cr", "Mn", "Fe", "Ru", "Ir", "Ti"):
        r = body["per_metal"][m]
        ab = r["as_built"]
        eq = r["equalised"]
        eqs = ("span/2=%.4f V %s  D_M=%+.4f eV"
               % (eq["span_over_2_V"],
                  "EXCEEDS" if eq["exceeds_floor"] else "below",
                  eq["D_M_eV"])) if isinstance(eq, dict) else eq
        print("  %-3s as-built span/2=%.4f V %-7s | equalised: %s"
              % (m, ab["span_over_2_V"],
                 "EXCEEDS" if ab["exceeds_floor"] else "below", eqs))
    print("  (A11.R2: never quoted bare; conditionality travels from the "
          "banked artifact.)")

    result = dict(
        readout="src/dft/a0spin_census.py",
        gates=dict(licence_granted=gates["licence_granted"],
                   confirmed=confirmed,
                   ti_disposition=("included under the completed SS3c "
                                   "countersignature" if confirmed else
                                   "PENDING-CONFIRMATION -- excluded from "
                                   "every output row")),
        controls=dict(stage0_p11=s0, ti_null=nulls),
        a7_3_spin=body,
        provenance=dict(
            git_head=git_head(),
            banked_artifact_md5=READ_LOG.get(BANKED_JSON),
            docs59_md5=READ_LOG.get(DOCS59)),
    )

    n = sweep_read_log()   # CEN-a
    result["assertions"] = {k: "PASS" for k in
                            ("CEN-a", "CEN-b", "CEN-c", "CEN-d", "CEN-e",
                             "CEN-f", "CEN-g", "CEN-h", "CEN-i", "CEN-j",
                             "CEN-k", "CEN-l", "CEN-m", "CEN-n")}
    result["assertions_note"] = ("every CEN check is fatal; a report only "
                                 "exists because all of them passed. CEN-a "
                                 "swept %d read files unchanged." % n)

    if out_path is not None:
        with io.open(out_path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(result, fh, sort_keys=True, indent=1)
            fh.write("\n")
        print("\n  wrote %s (read-only over runs/; %d inputs md5-swept "
              "unchanged)" % (out_path, n))
    print("\nREADOUT OK -- 0 files written under runs/ or docs/; the banked "
          "as-built census is untouched and remains the headline.")
    return result


def git_head() -> str:
    try:
        return subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"],
                              capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return "unavailable"


if __name__ == "__main__":
    main(sys.argv[1:])
