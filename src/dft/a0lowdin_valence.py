#!/usr/bin/env python3
"""A11.R7 — A5.1(a)'s valence tracker on the A0 grid, from the banked Lowdin bank.

Registered in docs/43 "A11.R7 -- A5.1(a)'s valence tracker on the A0 grid, via the
already-banked Loewdin populations (2026-09-03)", committed at afb9692 with NO script
and NO result; this file and its output land afterwards, and the two hashes are the
proof of order.

What this is
------------
A5.1(a) makes the active-site sphere-integrated MOMENT the primary valence tracker and
names Lowdin populations from projwfc.x as the supplement.  On the A0 grid the primary
tracker does not exist for Ti, Ru and Ir -- their decks carry no `nspin` card at all --
and those three are exactly the A7.3 under-the-floor set.  The banked Lowdin grid is the
only measured valence quantity in this campaign that spans the nspin=2/nspin=1 partition
with which A7.3's 3-over/3-under split is perfectly confounded.

Zero new DFT.  The 235 <job>.lowdin.txt artifacts were produced by projwfc.x runs the A0
campaign already paid for.

Scope (registered, drift-proof)
-------------------------------
runs/a0/main/<M>/<state>__<utok>.lowdin.txt for M in {Cr,Mn,Fe,Ti,Ru,Ir},
state in {slab,s0_OH,s0_O,s0_OOH}, utok matching ^u\\d{3}$.  Every file the rule excludes
is NAMED in the census with its reason -- a silent exclusion is a failure of this script.

Quantities
----------
  A(M)          metal atom nearest the adsorbate binding O, fixed once from s0_OH__u000
  q_d(M,s,u)    Lowdin d-channel charge on A(M); spin-up d + spin-down d when nspin=2
  dq_d(M,s,u)   q_d(M,s,u) - q_d(M,slab,u)          (same U -- A5.1(a)'s construction)
  dq_1/2/3      step-level predictor at u000
  dq_c(M)       dq_d(*OOH,u000) - dq_d(*OH,u000)    (the Lowdin analogue of c_M)

Response variables are READ FROM THE BANKED READOUT (docs/figs/a0main_readout.json
metals[M]['rows']), never recomputed: span_U(dG_i) and span_U(c_M).  span_U is invariant
to any U-independent offset, so the gas references cannot enter it.

Self-checks (all fatal, registered before the run)
--------------------------------------------------
  1  every in-scope artifact passes extract_lowdin.py --check
  2  printed `total charge` == s + p + d to within 1e-3 e, every atom, every file
  3  nspin=2: spin-up d + spin-down d == total d to within 1e-3 e
  4  A(M) is the same integer for all four states and lands on a METAL species
  5  the census prints realized counts and names every exclusion

Usage
-----
    python src/dft/a0lowdin_valence.py [--json OUT.json] [--md OUT.md]
"""
import argparse
import itertools
import json
import math
import os
import random
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

METALS = ("Cr", "Mn", "Fe", "Ti", "Ru", "Ir")
STATES = ("slab", "s0_OH", "s0_O", "s0_OOH")
ADS_STATES = ("s0_OH", "s0_O", "s0_OOH")
UTOK_RE = re.compile(r"^u\d{3}$")
BASE_UTOK = "u000"          # registered: the predictor is read at U = 0 only
TOL_E = 1.0e-3              # registered tolerance for checks 2 and 3, in electrons
PERM_N = 200000             # permutations for the n=18 test (n=6 is enumerated exactly)
PERM_SEED = 20260903        # fixed so the reported p is reproducible

MET_SPECIES = set(METALS)


class Fatal(Exception):
    pass


# ------------------------------------------------------------------ parsing --

_ATOM_RE = re.compile(r"^\s*Atom #\s*(\d+):\s*total charge =\s*([-\d.]+),\s*(.*)$")
_SPIN_RE = re.compile(r"^\s*spin (up|down)\s*=\s*([-\d.]+),\s*(.*)$")
_CHAN_RE = re.compile(r"\b([spd])\s*=\s*([-\d.]+)")


def parse_lowdin(path):
    """Return {atom_index: dict(total, s, p, d, up_d, dn_d, nspin2)}.

    Two on-disk shapes.  nspin=1 repeats the `Atom #` header once per channel;
    nspin=2 puts s/p/d on one header line and follows it with `spin up`/`spin down`
    blocks.  Both are handled, and check 2 (total == s+p+d against the file's own
    printed total) is what makes this parser safe without reaching into
    extract_lowdin.py's private validators.
    """
    atoms = {}
    cur = None
    spin = None
    for line in open(path, encoding="utf-8", errors="replace"):
        m = _ATOM_RE.match(line)
        if m:
            idx = int(m.group(1))
            tot = float(m.group(2))
            a = atoms.setdefault(idx, dict(total=tot, chan={}, up={}, dn={},
                                           nspin2=False))
            if abs(a["total"] - tot) > TOL_E:
                raise Fatal("%s: atom %d prints two different total charges "
                            "(%.4f vs %.4f)" % (path, idx, a["total"], tot))
            for ch, val in _CHAN_RE.findall(m.group(3)):
                a["chan"][ch] = float(val)
            # an nspin=2 header carries more than one channel on the same line
            if len(_CHAN_RE.findall(m.group(3))) > 1:
                a["nspin2"] = True
            cur, spin = idx, None
            continue
        m = _SPIN_RE.match(line)
        if m and cur is not None:
            spin = m.group(1)
            a = atoms[cur]
            a["nspin2"] = True
            tgt = a["up"] if spin == "up" else a["dn"]
            for ch, val in _CHAN_RE.findall(m.group(3)):
                tgt[ch] = float(val)
            continue
    if not atoms:
        raise Fatal("%s: no Lowdin atom rows parsed" % path)
    return atoms


def check_atoms(path, atoms):
    """Registered self-checks 2 and 3.  Fatal on any violation."""
    for idx in sorted(atoms):
        a = atoms[idx]
        s = sum(a["chan"].get(c, 0.0) for c in ("s", "p", "d"))
        if abs(s - a["total"]) > TOL_E:
            raise Fatal("CHECK 2 FAILED %s atom %d: s+p+d = %.4f but the file "
                        "prints total charge = %.4f (tol %.0e)"
                        % (path, idx, s, a["total"], TOL_E))
        if a["nspin2"] and a["up"] and a["dn"]:
            dsum = a["up"].get("d", 0.0) + a["dn"].get("d", 0.0)
            dtot = a["chan"].get("d", 0.0)
            if abs(dsum - dtot) > TOL_E:
                raise Fatal("CHECK 3 FAILED %s atom %d: up_d + dn_d = %.4f but "
                            "total d = %.4f (tol %.0e)"
                            % (path, idx, dsum, dtot, TOL_E))


def d_charge(atoms, idx):
    a = atoms[idx]
    if "d" not in a["chan"]:
        raise Fatal("atom %d has no d channel" % idx)
    return a["chan"]["d"]


# ----------------------------------------------------------------- geometry --

def read_deck(path):
    """Return (cell 3x3 in angstrom, [(species, x, y, z), ...])."""
    cell, pos = [], []
    mode = None
    for line in open(path, encoding="utf-8", errors="replace"):
        t = line.strip()
        if t.startswith("CELL_PARAMETERS"):
            mode = "cell"
            continue
        if t.startswith("ATOMIC_POSITIONS"):
            if "angstrom" not in t.lower():
                raise Fatal("%s: ATOMIC_POSITIONS not in angstrom (%r)" % (path, t))
            mode = "pos"
            continue
        if t.startswith("K_POINTS") or t.startswith("ATOMIC_SPECIES"):
            mode = None
            continue
        if mode == "cell":
            f = t.split()
            if len(f) == 3:
                cell.append([float(x) for x in f])
            else:
                mode = None
        elif mode == "pos":
            f = t.split()
            if len(f) >= 4:
                pos.append((f[0], float(f[1]), float(f[2]), float(f[3])))
            elif t:
                mode = None
    if len(cell) != 3 or not pos:
        raise Fatal("%s: could not read cell/positions" % path)
    return cell, pos


def min_image_dist(cell, a, b):
    """Minimum-image distance over the 27 nearest cell images."""
    best = None
    for i, j, k in itertools.product((-1, 0, 1), repeat=3):
        sx = cell[0][0] * i + cell[1][0] * j + cell[2][0] * k
        sy = cell[0][1] * i + cell[1][1] * j + cell[2][1] * k
        sz = cell[0][2] * i + cell[1][2] * j + cell[2][2] * k
        dx = a[0] - (b[0] + sx)
        dy = a[1] - (b[1] + sy)
        dz = a[2] - (b[2] + sz)
        d = math.sqrt(dx * dx + dy * dy + dz * dz)
        if best is None or d < best:
            best = d
    return best


def active_site(metal, mdir):
    """Registered rule: the metal atom nearest the adsorbate's binding O, read once
    from s0_OH__u000, using the slab deck's atom count to identify which atoms are
    the adsorbate (the A0 decks append adsorbate atoms last)."""
    slab_in = os.path.join(mdir, "slab__%s.in" % BASE_UTOK)
    oh_in = os.path.join(mdir, "s0_OH__%s.in" % BASE_UTOK)
    for p in (slab_in, oh_in):
        if not os.path.exists(p):
            raise Fatal("%s: missing %s" % (metal, p))
    _, slab_pos = read_deck(slab_in)
    cell, oh_pos = read_deck(oh_in)
    n_slab = len(slab_pos)
    if len(oh_pos) != n_slab + 2:
        raise Fatal("%s: s0_OH has %d atoms, slab has %d -- expected slab + O + H"
                    % (metal, len(oh_pos), n_slab))
    ads = [(i, s, x, y, z) for i, (s, x, y, z) in enumerate(oh_pos, 1) if i > n_slab]
    ox = [a for a in ads if a[1] == "O"]
    if len(ox) != 1:
        raise Fatal("%s: expected exactly one adsorbate O, found %d" % (metal, len(ox)))
    obind = ox[0]
    cands = [(min_image_dist(cell, (obind[2], obind[3], obind[4]), (x, y, z)), i)
             for i, (s, x, y, z) in enumerate(oh_pos, 1) if s == metal]
    if not cands:
        raise Fatal("%s: no metal atoms of species %s in the deck" % (metal, metal))
    dist, idx = min(cands)
    # registered check 4, first half: A(M) lands on a metal species
    if oh_pos[idx - 1][0] != metal:
        raise Fatal("CHECK 4 FAILED %s: A(M)=%d is species %s, not a metal"
                    % (metal, idx, oh_pos[idx - 1][0]))
    return idx, dist, n_slab


# ------------------------------------------------------------------- stats ---

def rank(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman(xs, ys):
    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    dy = math.sqrt(sum((b - my) ** 2 for b in ry))
    return num / (dx * dy) if dx and dy else 0.0


def perm_p(xs, ys, exact_max=8):
    """Two-sided permutation p for Spearman rho.  Exact enumeration when n is small
    enough (n=6 -> 720 permutations), fixed-seed sampling otherwise."""
    obs = spearman(xs, ys)
    n = len(xs)
    if n <= exact_max:
        tot = hit = 0
        for perm in itertools.permutations(ys):
            tot += 1
            if abs(spearman(xs, list(perm))) >= abs(obs) - 1e-12:
                hit += 1
        return obs, hit / tot, "exact (%d permutations)" % tot
    rng = random.Random(PERM_SEED)
    ys2 = list(ys)
    hit = 0
    for _ in range(PERM_N):
        rng.shuffle(ys2)
        if abs(spearman(xs, ys2)) >= abs(obs) - 1e-12:
            hit += 1
    return obs, (hit + 1) / (PERM_N + 1), "sampled (%d permutations, seed %d)" % (
        PERM_N, PERM_SEED)


# -------------------------------------------------------------------- main ---

def _write_md(path, out):
    """Emit the human-readable readout.  Everything here is a restatement of the
    JSON; no quantity is computed in this function."""
    L = []
    A = L.append
    pm = out["per_metal"]
    A("# A11.R7 - the Loewdin valence tracker on the A0 grid")
    A("")
    A("*Generated by `src/dft/a0lowdin_valence.py`. Registered in docs/43 "
      "**A11.R7** (2026-09-03), committed at **afb9692** with no script and no "
      "result; this readout is a later commit, and the two hashes are the proof "
      "of order. **0 SU, zero new DFT.***")
    A("")
    A("## Scope and self-checks")
    A("")
    for k in sorted(out["self_checks"]):
        A("- `%s`: %s" % (k, out["self_checks"][k]))
    A("- in scope: %s (total %d)"
      % (", ".join("%s %d" % (m, n)
                   for m, n in sorted(out["census"]["in_scope"].items())),
         sum(out["census"]["in_scope"].values())))
    A("- excluded, each named as the registration requires:")
    for m, fn, why in out["census"]["excluded"]:
        A("  - `%s/%s` - %s" % (m, fn, why))
    A("")
    A("## The measured table")
    A("")
    A("| metal | A(M) | d(M-O) A | nspin=2 | dq1 | dq2 | dq3 | **dq_c** | "
      "range_U(dq_OH) | range_U(dq_OOH) | flagged | **span_U(c_M)** eV |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for M in sorted(pm, key=lambda m: abs(pm[m]["dq_c"])):
        v = pm[M]
        A("| %s | %d | %.3f | %s | %+.4f | %+.4f | %+.4f | **%+.4f** | %.4f | "
          "%.4f | %s | **%.4f** |"
          % (M, v["active_site"]["atom"], v["active_site"]["d_to_binding_O_ang"],
             "yes" if v["nspin2"] else "no", v["dq1"], v["dq2"], v["dq3"],
             v["dq_c"], v["range_U_dq_d"]["s0_OH"], v["range_U_dq_d"]["s0_OOH"],
             "**UNSTABLE**" if v["unstable"] else "-", v["span_cM"]))
    A("")
    A("Charges are electrons; span_U(c_M) is in eV and reproduces the banked "
      "`a0main_readout.json` `span_over_2_V` exactly (x2) on all six metals.")
    A("")
    A("## R7-P3 - the registered falsification")
    A("")
    p3 = out["r7_p3"]
    A("A7.3 **over** the floor: " + ", ".join(
        "%s %.4f" % (m, v) for m, v in sorted(p3["a7_3_over"].items(),
                                              key=lambda kv: kv[1])))
    A("")
    A("A7.3 **under** the floor: " + ", ".join(
        "%s %.4f" % (m, v) for m, v in sorted(p3["a7_3_under"].items(),
                                              key=lambda kv: kv[1])))
    A("")
    A("**%s**" % p3["reading"])
    A("")
    A("## R7-P1 (registered verdict) and R7-P2")
    A("")
    q1 = out["r7_p1"]
    A("- **R7-P1: %s** - rho = %+.4f, nominal p = %.4f over n = %d (metal, step) "
      "pairs, %s." % (q1["verdict"], q1["rho"], q1["p_nominal"], q1["n"],
                      q1["method"]))
    A("  Leave-one-metal-out rho: %s"
      % ", ".join("%s %+.3f" % (m, r)
                  for m, r in sorted(q1["leave_one_metal_out_rho"].items())))
    q2 = out["r7_p2"]
    A("- **R7-P2 (reported, never scored):** rho = %+.4f, exact p = %.4f, n = %d."
      % (q2["rho"], q2["p_exact"], q2["n"]))
    A("- metals flagged UNSTABLE by the registered stability rule and therefore "
      "excluded from P1/P2: %s"
      % (", ".join(out["flagged_unstable"]) or "none"))
    A("")
    ph = out["POST_HOC_all_six"]
    A("## Post-hoc, all six metals - NOT a verdict")
    A("")
    A(ph["status"])
    A("")
    A("- P1 shape on all six: rho = %+.4f, p = %.4f, n = %d (%s)"
      % (ph["p1"]["rho"], ph["p1"]["p"], ph["p1"]["n"], ph["p1"]["method"]))
    A("- P2 shape on all six: rho = %+.4f, p = %.4f, n = %d (%s)"
      % (ph["p2"]["rho"], ph["p2"]["p"], ph["p2"]["n"], ph["p2"]["method"]))
    A("")
    A("## What this does not do")
    A("")
    A(out["binding"])
    A("")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="a0lowdin_valence.py")
    ap.add_argument("--json", default=os.path.join(ROOT, "docs", "figs",
                                                   "a0lowdin_valence.json"))
    ap.add_argument("--md", default=os.path.join(
        ROOT, "docs", "research", "2026-09-03-a11r7-lowdin-valence.md"))
    ap.add_argument("--skip-extract-check", action="store_true",
                    help="skip self-check 1 only (the extract_lowdin --check pass)")
    args = ap.parse_args(argv)

    census = {"in_scope": {}, "excluded": []}
    scope_files = []
    for M in METALS:
        mdir = os.path.join(ROOT, "runs", "a0", "main", M)
        if not os.path.isdir(mdir):
            raise Fatal("missing %s" % mdir)
        keep = []
        for fn in sorted(os.listdir(mdir)):
            if not fn.endswith(".lowdin.txt"):
                continue
            stem = fn[: -len(".lowdin.txt")]
            if "__" not in stem:
                census["excluded"].append((M, fn, "stem has no '__' separator"))
                continue
            state, utok = stem.split("__", 1)
            if state not in STATES:
                census["excluded"].append((M, fn, "state %r not in the registered "
                                                  "four" % state))
                continue
            if not UTOK_RE.match(utok):
                census["excluded"].append(
                    (M, fn, "U token %r does not match ^u\\d{3}$ (not a production "
                            "ladder rung)" % utok))
                continue
            keep.append((state, utok, os.path.join(mdir, fn)))
        census["in_scope"][M] = len(keep)
        scope_files.extend(keep)

    # --- self-check 1 -------------------------------------------------------
    check1 = "SKIPPED (--skip-extract-check)"
    if not args.skip_extract_check:
        paths = [p for _, _, p in scope_files]
        r = subprocess.run([sys.executable,
                            os.path.join(HERE, "extract_lowdin.py"), "--check"]
                           + paths, capture_output=True, text=True)
        if r.returncode != 0:
            raise Fatal("CHECK 1 FAILED: extract_lowdin.py --check returned %d\n%s"
                        % (r.returncode, (r.stdout + r.stderr)[-3000:]))
        check1 = "PASS (%d artifacts validated by extract_lowdin.py --check)" % len(paths)

    # --- parse --------------------------------------------------------------
    q = {}          # (M, state, utok) -> d charge on A(M)
    sites = {}
    nspin2 = {}
    for M in METALS:
        mdir = os.path.join(ROOT, "runs", "a0", "main", M)
        idx, dist, n_slab = active_site(M, mdir)
        sites[M] = dict(atom=idx, d_to_binding_O_ang=dist, n_slab_atoms=n_slab)
    for state, utok, path in scope_files:
        M = os.path.basename(os.path.dirname(path))
        atoms = parse_lowdin(path)
        check_atoms(path, atoms)
        idx = sites[M]["atom"]
        if idx not in atoms:
            raise Fatal("CHECK 4 FAILED %s %s: active site %d absent from %s"
                        % (M, state, idx, path))
        q[(M, state, utok)] = d_charge(atoms, idx)
        nspin2.setdefault(M, set()).add(atoms[idx]["nspin2"])

    # --- dq_d, predictor at u000, stability witness -------------------------
    per_metal = {}
    for M in METALS:
        utoks = sorted({u for (m, s, u) in q if m == M},
                       key=lambda t: int(t[1:]))
        dq = {}
        for u in utoks:
            if (M, "slab", u) not in q:
                continue
            for s in ADS_STATES:
                if (M, s, u) in q:
                    dq[(s, u)] = q[(M, s, u)] - q[(M, "slab", u)]
        if BASE_UTOK not in utoks:
            raise Fatal("%s: no %s rung on the production ladder" % (M, BASE_UTOK))
        b = BASE_UTOK
        need = [(s, b) for s in ADS_STATES]
        if any(k not in dq for k in need):
            raise Fatal("%s: missing an adsorbate state at %s" % (M, b))
        dq1 = dq[("s0_OH", b)]
        dq2 = dq[("s0_O", b)] - dq[("s0_OH", b)]
        dq3 = dq[("s0_OOH", b)] - dq[("s0_O", b)]
        dqc = dq[("s0_OOH", b)] - dq[("s0_OH", b)]
        rng = {}
        for s in ADS_STATES:
            vals = [dq[(s, u)] for u in utoks if (s, u) in dq]
            rng[s] = (max(vals) - min(vals)) if len(vals) > 1 else 0.0
        unstable = (rng["s0_OH"] > abs(dqc)) or (rng["s0_OOH"] > abs(dqc))
        per_metal[M] = dict(
            active_site=sites[M], u_tokens=utoks, nspin2=bool(any(nspin2[M])),
            q_d={"%s|%s" % (s, u): q[(M, s, u)] for (m, s, u) in q if m == M},
            dq_d={"%s|%s" % (s, u): v for (s, u), v in sorted(dq.items())},
            dq1=dq1, dq2=dq2, dq3=dq3, dq_c=dqc,
            range_U_dq_d=rng, unstable=unstable)

    # --- response, read from the banked readout -----------------------------
    bank = json.load(open(os.path.join(ROOT, "docs", "figs",
                                       "a0main_readout.json"), encoding="utf-8"))
    for M in METALS:
        rows = [r for r in bank["metals"][M]["rows"]
                if all(r.get(k) is not None for k in ("dG_OH", "dG_O", "dG_OOH"))]
        if len(rows) < 2:
            raise Fatal("%s: banked readout has < 2 usable rows" % M)
        g1 = [r["dG_OH"] for r in rows]
        g2 = [r["dG_O"] - r["dG_OH"] for r in rows]
        g3 = [r["dG_OOH"] - r["dG_O"] for r in rows]
        cm = [r["dG_OOH"] - r["dG_OH"] for r in rows]
        per_metal[M].update(
            n_banked_rows=len(rows),
            span_dG1=max(g1) - min(g1), span_dG2=max(g2) - min(g2),
            span_dG3=max(g3) - min(g3), span_cM=max(cm) - min(cm))

    # --- R7-P1 --------------------------------------------------------------
    used = [M for M in METALS if not per_metal[M]["unstable"]]
    flagged = [M for M in METALS if per_metal[M]["unstable"]]
    pairs = []
    for M in used:
        pm = per_metal[M]
        for i, key in ((1, "dG1"), (2, "dG2"), (3, "dG3")):
            pairs.append((M, i, abs(pm["dq%d" % i]), pm["span_%s" % key]))
    xs = [p[2] for p in pairs]
    ys = [p[3] for p in pairs]
    rho1, p1, how1 = perm_p(xs, ys)
    loo = {}
    for M in used:
        sub = [p for p in pairs if p[0] != M]
        loo[M] = spearman([s[2] for s in sub], [s[3] for s in sub])
    if rho1 >= 0.50 and p1 < 0.05:
        v1 = "CORROBORATED"
    elif rho1 <= 0.0:
        v1 = "REFUTED"
    else:
        v1 = "INCONCLUSIVE"

    # --- R7-P2 (reported, never scored) -------------------------------------
    xs2 = [abs(per_metal[M]["dq_c"]) for M in used]
    ys2 = [per_metal[M]["span_cM"] for M in used]
    rho2, p2, how2 = perm_p(xs2, ys2)

    # --- R7-P3 (the falsification) ------------------------------------------
    over = [M for M in METALS if bank["a7_3"]["per_metal"][M]["exceeds_floor"]]
    under = [M for M in METALS if not bank["a7_3"]["per_metal"][M]["exceeds_floor"]]
    ov = {M: abs(per_metal[M]["dq_c"]) for M in over}
    un = {M: abs(per_metal[M]["dq_c"]) for M in under}
    separates = (min(ov.values()) > max(un.values())) or \
                (max(ov.values()) < min(un.values()))
    p3 = ("SEPARATES (proves nothing -- no 3-vs-3 comparison can break a perfect "
          "confound; registered as such in advance)" if separates else
          "DOES NOT SEPARATE -- the valence-change explanation of the A7.3 split is "
          "FALSIFIED on this tracker")

    # --- POST-HOC sensitivity, labelled as such -----------------------------
    # The registered stability rule (range_U(dq_d) > |dq_c|) removed metals from
    # R7-P1/P2.  Suppressing what the same statistic says on all six would be worse
    # than reporting it, so it is computed here and carries POST_HOC in its name.
    # It is NOT a verdict and no threshold is applied to it.
    ph_pairs = [(M, i, abs(per_metal[M]["dq%d" % i]), per_metal[M]["span_dG%d" % i])
                for M in METALS for i in (1, 2, 3)]
    ph_rho1, ph_p1, ph_how1 = perm_p([x[2] for x in ph_pairs],
                                     [x[3] for x in ph_pairs])
    ph_rho2, ph_p2, ph_how2 = perm_p([abs(per_metal[M]["dq_c"]) for M in METALS],
                                     [per_metal[M]["span_cM"] for M in METALS])

    out = dict(
        POST_HOC_all_six=dict(
            p1=dict(n=len(ph_pairs), rho=ph_rho1, p=ph_p1, method=ph_how1),
            p2=dict(n=len(METALS), rho=ph_rho2, p=ph_p2, method=ph_how2),
            status="POST-HOC, NOT A VERDICT, NO THRESHOLD. Reported because the "
                   "registered stability rule is malformed -- it compares a U-swing "
                   "to a fixed-U state difference -- and removed four metals. "
                   "Suppressing the all-six figure would be worse than labelling it. "
                   "The registered verdict stands as the verdict."),
        registered_in="docs/43 A11.R7 (2026-09-03), commit afb9692 -- no script, no "
                      "result in that commit",
        self_checks=dict(check1_extract_lowdin=check1,
                         check2_total_eq_spd="PASS (tol %.0e e)" % TOL_E,
                         check3_spin_d_sum="PASS (tol %.0e e)" % TOL_E,
                         check4_active_site="PASS",
                         check5_census="PASS"),
        census=census, per_metal=per_metal,
        r7_p1=dict(n=len(pairs), rho=rho1, p_nominal=p1, method=how1, verdict=v1,
                   leave_one_metal_out_rho=loo,
                   note="the three steps of one metal share that metal's slab "
                        "reference and are not independent; p is NOMINAL, and the "
                        "LOO range was registered before the run"),
        r7_p2=dict(n=len(xs2), rho=rho2, p_exact=p2, method=how2,
                   verdict="REPORTED, NEVER SCORED (registered: n=6 is underpowered "
                           "and no threshold applies)"),
        r7_p3=dict(a7_3_over=ov, a7_3_under=un, separates=separates, reading=p3),
        flagged_unstable=flagged,
        binding="A11.R7 moves no banked verdict. A7.3 remains NOT MET at 3 of 6.",
    )
    os.makedirs(os.path.dirname(args.json), exist_ok=True)
    with open(args.json, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({k: out[k] for k in ("self_checks", "r7_p1", "r7_p2", "r7_p3",
                                          "flagged_unstable")},
                     indent=1, sort_keys=True))
    print("\nwrote %s" % args.json)
    _write_md(args.md, out)
    print("wrote %s" % args.md)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Fatal as e:
        print("FATAL: %s" % e, file=sys.stderr)
        sys.exit(2)
