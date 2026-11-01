"""Independent check of the corpus-escape decks against the deposited Xu inputs and outputs.

Uses parsers that the builder does not use: ASE's Fortran-namelist and espresso-in readers for the decks and the
deposited inputs, ASE's espresso-out reader for the deposited final geometry of converged runs (a plain regex for
the four runs that stopped unconverged, whose last printed geometry ASE does not return), and spglib for the
symmetry each start will present to pw.x. Writes deck_verification.json next to this file; exit 1 on any failure.

Usage: python results/corpus_escape_2026-11-01/verify_decks.py
"""
import json
import os
import re
import sys
from pathlib import Path

import numpy as np
import spglib
from ase.io import read
from ase.io.espresso import read_fortran_namelist

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CASES = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
CORPUS = Path(os.environ.get("STS_XU", CASES["corpus_root_default"]))
# Namelist keys whose difference from the deposited input is declared in the design note.
DECLARED = {
    "control": {"prefix": "added", "outdir": "added", "pseudo_dir": "changed", "forc_conv_thr": "added",
                "nstep": "added", "disk_io": "removed"},
    "system": {"nbnd": "removed", "hubbard_u": "removed", "hubbard_alpha": "removed", "nosym": "escape only"},
    "electrons": {},
    "ions": {},
    "cell": {},
}
EXPECTED_ADDED = {"prefix": None, "outdir": "./tmp", "pseudo_dir": "./pseudo", "forc_conv_thr": 1e-4,
                  "nstep": 100}
DISPLACEMENT = CASES["displacement_A"]


def namelist(path):
    with open(path, encoding="utf-8") as handle:
        data, cards = read_fortran_namelist(handle)
    flat = {}
    for section, values in data.items():
        for key, value in values.items():
            flat[(section.lower(), key.lower())] = value
    return flat, [c.strip() for c in cards if c.strip()]


def card_block(cards, name, count):
    i = next(k for k, c in enumerate(cards) if c.upper().startswith(name))
    return cards[i:i + 1 + count]


def last_printed_positions(path, nat):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    heads = [m.end() for m in re.finditer(r"ATOMIC_POSITIONS \(crystal\)\n", text)]
    rows = [line.split() for line in text[heads[-1]:].splitlines()[:nat]]
    return np.array([[float(v) for v in r[1:4]] for r in rows])


def n_ops(atoms):
    cell = (atoms.cell.array, atoms.get_scaled_positions(wrap=True), atoms.numbers)
    data = spglib.get_symmetry(cell, symprec=1e-5)
    return len(data["rotations"])


def check_case(case):
    out = {"metal": case["metal"], "job": case["job"], "tier": case["tier"], "failures": []}
    fail = out["failures"].append
    dep_in = CORPUS / case["census_input"]
    dep_out = CORPUS / case["census_output"]
    dep_nl, dep_cards = namelist(dep_in)
    nat = case["nat"]
    # deposited final geometry, crystal units
    # ASE's reader trips on 5.0.2 LSDA eigenvalue blocks unless results are optional; its last image is the
    # last printed geometry. The regex parse is a second reading of the same block.
    final = read(dep_out, format="espresso-out", index=-1, results_required=False).get_scaled_positions(wrap=False)
    regex = last_printed_positions(dep_out, nat)
    out["ase_vs_regex_final_max"] = float(np.abs(final - regex).max())
    if out["ase_vs_regex_final_max"] > 1e-9:
        fail("ASE and regex readings of the deposited final geometry disagree")
    out["deposited_final_source"] = "ase espresso-out (results optional), last image; regex cross-read"
    decks = {}
    for arm in ("held", "escape"):
        path = ROOT / case["decks"][arm]
        nl, cards = namelist(path)
        atoms = read(path, format="espresso-in")
        decks[arm] = {"nl": nl, "cards": cards, "atoms": atoms}
        # namelist: every deposited key kept with its value unless declared
        for (section, key), value in dep_nl.items():
            base = key.split("(")[0]
            if base in DECLARED.get(section, {}):
                if DECLARED[section][base] == "removed" and (section, key) in nl:
                    fail("%s: %s.%s should be removed" % (arm, section, key))
                continue
            if (section, key) not in nl:
                fail("%s: deposited %s.%s missing" % (arm, section, key))
            elif nl[(section, key)] != value:
                fail("%s: %s.%s = %r, deposited %r" % (arm, section, key, nl[(section, key)], value))
        for (section, key), value in nl.items():
            if (section, key) in dep_nl and DECLARED.get(section, {}).get(key.split("(")[0]) != "changed":
                continue
            base = key.split("(")[0]
            if base == "nosym":
                if arm != "escape" or value is not True:
                    fail("%s: nosym = %r" % (arm, value))
                continue
            if base not in EXPECTED_ADDED:
                fail("%s: undeclared key %s.%s" % (arm, section, key))
                continue
            want = case["metal"] + "__" + case["job"] + "__" + arm if base == "prefix" else EXPECTED_ADDED[base]
            if value != want:
                fail("%s: %s = %r, declared %r" % (arm, key, value, want))
        if arm == "held" and ("system", "nosym") in nl:
            fail("held: nosym present")
        if any(k[1].startswith("noinv") for k in nl):
            fail("%s: noinv present" % arm)
        if ("system", "lda_plus_u") in nl or any(c.upper().startswith("HUBBARD") for c in cards):
            fail("%s: DFT+U switched on" % arm)
        # cards: k-points, species and cell exactly as deposited
        for name, count in (("K_POINTS", 1), ("CELL_PARAMETERS", 3)):
            if [c.split() for c in card_block(cards, name, count)] != [c.split() for c in card_block(dep_cards, name, count)]:
                fail("%s: card %s differs from the deposited card" % (arm, name))
        # species: deposited symbol and mass, UPF replaced by the run file recorded for this case (2026-11-01)
        sub = {p["deposited_upf"]: p["run_upf"] for p in case["pseudopotentials"].values()}
        dep_block = [c.split() for c in card_block(dep_cards, "ATOMIC_SPECIES", case_ntyp(dep_nl))]
        want = dep_block[:1] + [[t[0], t[1], sub[t[2]]] for t in dep_block[1:]]   # header line, then one per species
        if [c.split() for c in card_block(cards, "ATOMIC_SPECIES", case_ntyp(dep_nl))] != want:
            fail("%s: ATOMIC_SPECIES differs from the deposited card plus the substitution" % arm)
    held, esc = decks["held"]["atoms"], decks["escape"]["atoms"]
    dep_atoms = read(dep_in, format="espresso-in")
    if list(held.get_chemical_symbols()) != list(dep_atoms.get_chemical_symbols()):
        fail("species order differs")
    if not np.allclose(held.cell.array, dep_atoms.cell.array, atol=1e-12):
        fail("cell differs")
    L = np.diag(held.cell.array)
    held_s = held.get_scaled_positions(wrap=False)
    dev = np.abs(held_s - final) * L
    out["held_vs_deposited_final_max_A"] = float(dev.max())
    if dev.max() > 1e-8:
        fail("held start differs from the deposited final geometry by %.2e A" % dev.max())
    axis = {"x": 0, "y": 1}[case["locked_axis"]]
    ads = [i - 1 for i in case["adsorbate_index1"]]
    d = (esc.get_scaled_positions(wrap=False) - held_s) * L
    others = [i for i in range(nat) if i not in ads]
    if np.abs(d[others]).max() > 1e-9:
        fail("escape moves a non-adsorbate atom")
    for i in ads:
        role = case["displacement"][str(i + 1)]["role"]
        want = np.zeros(3)
        want[axis] = DISPLACEMENT[role]
        if np.abs(d[i] - want).max() > 1e-8:
            fail("escape displacement of atom %d is %s, recipe %s" % (i + 1, d[i].round(6).tolist(), want.tolist()))
    out["escape_displacement_A"] = {str(i + 1): d[i].round(9).tolist() for i in ads}
    # fixed-atom masks: ASE reads if_pos into constraints; compare the constrained index sets
    def fixed(atoms):
        return sorted(int(i) for c in atoms.constraints for i in getattr(c, "index", []))
    if fixed(held) != fixed(dep_atoms) or fixed(esc) != fixed(dep_atoms):
        fail("fixed-atom set differs from the deposited deck")
    out["n_fixed_atoms"] = len(fixed(dep_atoms))
    out["spglib_ops_held"] = n_ops(held)
    out["spglib_ops_escape"] = n_ops(esc)
    if out["spglib_ops_held"] != case["deposited_n_symops"]:
        fail("held start has %d operations, deposited header %d" % (out["spglib_ops_held"], case["deposited_n_symops"]))
    if out["spglib_ops_escape"] != 1:
        fail("escape start keeps %d operations" % out["spglib_ops_escape"])
    out["passed"] = not out["failures"]
    return out


def case_ntyp(nl):
    return int(nl[("system", "ntyp")])


def main():
    rows = [check_case(c) for c in CASES["cases"]]
    report = {"schema": "corpus-escape-deck-verification-v1", "cases_sha256": __import__("hashlib").sha256(
                  (HERE / "cases.json").read_bytes()).hexdigest(),
              "tools": {"ase": __import__("ase").__version__, "spglib": spglib.__version__, "numpy": np.__version__},
              "n_cases": len(rows), "n_passed": sum(r["passed"] for r in rows), "rows": rows}
    (HERE / "deck_verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    for r in rows:
        print("%-5s %-5s %-10s %s ops held/escape %d/%d  held-vs-deposited %.1e A  %s" % (
            r["tier"], r["metal"], r["job"], "PASS" if r["passed"] else "FAIL", r["spglib_ops_held"],
            r["spglib_ops_escape"], r["held_vs_deposited_final_max_A"], "; ".join(r["failures"])))
    print("%d of %d cases pass" % (report["n_passed"], report["n_cases"]))
    return 0 if report["n_passed"] == report["n_cases"] else 1


if __name__ == "__main__":
    sys.exit(main())
