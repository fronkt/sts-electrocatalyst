#!/usr/bin/env python
"""Read the fixed-geometry Ru GBRV control alongside the ONCV bank (docs/89).

The primary quantity uses only OH/OOH at U=0 and 9; each secondary eta needs
all four states and the unchanged Ru_anchor gas references. No repaired run,
alternate seed, equalised row, or extra U rung is selected. Thresholds are the
pre-stated docs/89 bands; this module neither licenses a run nor changes any
historical verdict. Absolute total energies from different UPFs are not compared.

Usage: PYTHONPATH=src python src/dft/ru_pp_readout.py
       PYTHONPATH=src python src/dft/ru_pp_readout.py --json docs/figs/ru_pp_readout.json
Exit 2 means some required local evidence is absent or fails QC. Individual
quantities retain their own scoreability; missing unrelated rows do not erase Q.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dft import qe_qc
from hea_oer.descriptors import oer_overpotential
from hea_oer.referencing import delta_G

ROOT = Path(__file__).resolve().parents[2]
STATES = ("slab", "s0_O", "s0_OH", "s0_OOH")
RUNGS = {"u000": 0.0, "u673": 6.73, "u900": 9.0}
OLD_PP = "Ru_ONCV_PBE-1.0.oncvpsp.upf"
NEW_PP = "ru_pbe_v1.2.uspp.F.UPF"
OLD_MD5 = "be037bb81c227cfb9b1461a9f099f4bd"
NEW_MD5 = "7158a806dd851261a58e6920c40ebe78"
Q_REFERENCE = 0.09225
Q_FLOOR = 0.100
Q_MARGIN = 0.0078
ETA_RU = {"u000": 0.787, "u673": 0.413, "u900": 0.290}
ETA_IR = {"u673": 0.637, "u900": 0.754}


def checksum(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def read_energy(path: Path, expected_ru_md5: str | None = None) -> dict:
    """Require physical completion, a finite energy, and the expected Ru UPF."""
    path = Path(path)
    deck = path.with_suffix(".in")
    rec = qe_qc.scan(str(path), str(deck))
    reasons = []
    if not deck.is_file():
        reasons.append("matching input deck absent")
    if rec["verdict"] != "TRUSTWORTHY":
        reasons.extend(rec["reasons"] or [rec["verdict"]])
    if not rec["n_scf_ok"]:
        reasons.append("no explicit SCF convergence")
    if rec["energy_ev"] is None or not math.isfinite(rec["energy_ev"]):
        reasons.append("no finite total energy")
    text = path.read_text(errors="replace") if path.is_file() else ""
    if "Error in routine" in text:
        reasons.append("QE Error in routine")
    if re.search(r"IEEE_(?:INVALID|DIVIDE_BY_ZERO|OVERFLOW)(?:_FLAG)?"
                 r"|segmentation fault|SIGSEGV|SIGFPE|floating.point exception|MPI_ABORT"
                 r"|Program received signal", text, re.I):
        reasons.append("severe numerical or process failure")
    if any(path.with_suffix(ext).is_file() for ext in (".KILLED", ".REJECTED")):
        reasons.append("explicit KILLED or REJECTED sidecar")
    if text.count("JOB DONE") != 1:
        reasons.append("expected exactly one JOB DONE")
    if "convergence NOT achieved" in text:
        reasons.append("SCF did not converge")
    if expected_ru_md5:
        if rec["n_energies"] != 1:
            reasons.append("fixed-geometry Ru SCF requires exactly one energy")
        hashes = re.findall(
            r"PseudoPot\.\s*#\s*\d+\s+for Ru\s+read from file:\s*\n"
            r"[^\n]+\n\s*MD5 check sum:\s*([0-9a-fA-F]{32})", text)
        if hashes != [expected_ru_md5]:
            reasons.append("Ru pseudopotential hash absent, repeated, or unexpected")
        if rec["calculation"] != "scf":
            reasons.append("Ru control requires calculation='scf'")
    return {"path": str(path), "status": "SCOREABLE" if not reasons else "UNSCORED",
            "energy_eV": rec["energy_ev"] if not reasons else None,
            "reasons": sorted(set(reasons)), "sha256": checksum(path),
            "input_sha256": checksum(deck), "qe_verdict": rec["verdict"],
            "fmax_free_eV_A": rec["fmax_free_ev_ang"]}


def deck_pair_check(control: Path, source: Path) -> list[str]:
    """Admit only the frozen prefix/UPF substitution, including all coordinates."""
    if not control.is_file() or not source.is_file():
        return ["control or banked input absent"]
    old = source.read_text()
    new = control.read_text()
    stem = source.stem
    prefix = "prefix = '" + stem + "'"
    if old.count(prefix) != 1 or old.count(OLD_PP) != 1:
        return ["source prefix or ONCV pseudopotential is not unique"]
    expected = old.replace(prefix, "prefix = '" + stem + "_gbrv'", 1)
    expected = expected.replace(OLD_PP, NEW_PP, 1)
    if new != expected:
        return ["control differs from banked source beyond prefix and Ru UPF"]
    return []


def primary_band(q: float) -> str:
    # Decimal comparisons preserve the literal inclusive edges in docs/89.
    value = Decimal(str(q))
    if not math.isfinite(q) or q < 0:
        raise ValueError("Q must be finite and nonnegative")
    if value >= Decimal("0.100"):
        return "PP-SENSITIVE"
    if abs(value - Decimal("0.09225")) <= Decimal("0.0078"):
        return "CONFIRMS-COMPARABILITY"
    return "MIDDLE"


def secondary_band(token: str, eta: float) -> dict:
    if not math.isfinite(eta):
        raise ValueError("eta must be finite")
    v = Decimal(str(eta))
    if token == "u900":
        margin = Decimal("0.754") - v
        band = ("CLEARS-MEASURED-ERROR-CLASSES" if margin > Decimal("0.36")
                else "INVERTED-WITHIN-CELL-CLASS" if margin >= Decimal("0.20")
                else "PP-CONDITIONAL")
        return {"margin_Ir_minus_Ru_V": float(margin), "band": band,
                "banked_margin_V": 0.464}
    if token == "u000":
        shift = v - Decimal("0.787")
        return {"delta_eta_vs_ONCV_V": float(shift),
                "band": "COMPARABLE" if abs(shift) <= Decimal("0.20") else "PP-CONDITIONAL"}
    if token == "u673":
        margin = Decimal("0.637") - v
        return {"margin_Ir_minus_Ru_V": float(margin),
                "band": "PP-ROBUST" if margin > 0 else "OPPOSITE-SIGN" if margin < 0 else "TIE-NO-CORROBORATION",
                "banked_margin_V": 0.224, "label": "PROJECTOR-MISMATCHED"}
    raise ValueError("unsupported rung: " + token)


def primary_readout(energies: dict) -> dict:
    needed = [(u, st) for u in ("u000", "u900") for st in ("s0_OH", "s0_OOH")]
    missing = [u + "/" + st for u, st in needed if energies.get(u, {}).get(st) is None]
    if missing:
        return {"status": "UNSCORED", "missing_or_failed": missing}
    c_difference = ((energies["u000"]["s0_OOH"] - energies["u000"]["s0_OH"])
                    - (energies["u900"]["s0_OOH"] - energies["u900"]["s0_OH"]))
    q = abs(c_difference) / 2
    return {"status": "SCORED", "span_over_2_V": q,
            "c_M_u0_minus_u9_eV": c_difference, "delta_vs_ONCV_V": q - Q_REFERENCE,
            "comparator_ONCV_V": Q_REFERENCE, "comparison_margin_V": Q_MARGIN,
            "floor_V": Q_FLOOR, "band": primary_band(q),
            "equalised_ONCV_V_context_only": 0.09574,
            "equalised_ONCV_label": "BRANCH-CONDITIONAL; not scoreable into a span"}


def eta_readout(energies: dict, gas: dict) -> dict:
    missing = [s for s in STATES if energies.get(s) is None]
    missing += [s for s in ("H2", "H2O") if gas.get(s) is None]
    if missing:
        return {"status": "UNSCORED", "missing_or_failed": missing}
    dg = {sp: delta_G(energies["slab"], energies["s0_" + sp], sp, gas["H2O"], gas["H2"])
          for sp in ("OH", "O", "OOH")}
    result = oer_overpotential(dg["OH"], dg["O"], dg["OOH"])
    return {"status": "SCORED", "dG_eV": dg, "eta_V": result.overpotential,
            "steps_eV": [result.dG1, result.dG2, result.dG3, result.dG4],
            "potential_limiting_step": result.potential_limiting_step}


def build_readout(root: Path = ROOT) -> dict:
    root = Path(root)
    records, controls, oncv = {}, {}, {}
    gas_records = {g: read_energy(root / "runs" / "Ru_anchor" / (g + ".out"))
                   for g in ("H2", "H2O")}
    gas = {g: row["energy_eV"] for g, row in gas_records.items()}
    for u in RUNGS:
        controls[u], oncv[u] = {}, {}
        for state in STATES:
            stem = state + "__" + u
            source = root / "runs" / "a0" / "main" / "Ru" / (stem + ".out")
            control = root / "runs" / "a0" / "ru_pp" / "Ru" / (stem + "_gbrv.out")
            row = read_energy(control, NEW_MD5)
            row["input_pair_reasons"] = deck_pair_check(control.with_suffix(".in"), source.with_suffix(".in"))
            if row["input_pair_reasons"]:
                row["status"], row["energy_eV"] = "UNSCORED", None
                row["reasons"].extend(row["input_pair_reasons"])
            bank = read_energy(source, OLD_MD5)
            records[u + "/" + state] = {"GBRV": row, "ONCV": bank}
            controls[u][state], oncv[u][state] = row["energy_eV"], bank["energy_eV"]
    primary = primary_readout(controls)
    bank_primary = primary_readout(oncv)
    # Bank replication is an independent consistency check, not a new comparator.
    bank_agrees = (bank_primary["status"] == "SCORED"
                   and abs(bank_primary["span_over_2_V"] - Q_REFERENCE) <= 0.000005)
    secondary = {}
    for u, value in RUNGS.items():
        row = eta_readout(controls[u], gas)
        bank_row = eta_readout(oncv[u], gas)
        if row["status"] == "SCORED":
            row["comparison"] = secondary_band(u, row["eta_V"])
        secondary[u] = {"U_eV": value, "GBRV": row, "ONCV_recomputed": bank_row,
                        "ONCV_reference_V": ETA_RU[u]}
    ready = (all(r["GBRV"]["status"] == "SCOREABLE" and r["ONCV"]["status"] == "SCOREABLE"
                 for r in records.values())
             and all(r["status"] == "SCOREABLE" for r in gas_records.values()) and bank_agrees)
    return {
        "schema_version": 1, "control": "RU-PP", "local_evidence_root": str(root.resolve()),
        "readiness": "COMPLETE" if ready else "INCOMPLETE",
        "control_scoreable_outputs": sum(r["GBRV"]["status"] == "SCOREABLE" for r in records.values()),
        "control_expected_outputs": 12, "primary": primary, "secondary": secondary,
        "ONCV_primary_recomputed": bank_primary, "ONCV_primary_agrees_with_printed_comparator": bank_agrees,
        "records": records, "gas_records": gas_records,
        "unchanged_banked_verdicts": {"A7.3": "NOT MET at 3 of 6", "A6.3": "INVERTED"},
        "limits": [
            "Fixed ONCV-relaxed coordinates; no GBRV-consistent relaxation or geometry validation.",
            "Nonmagnetic nspin=1 throughout; no magnetic ground-state claim.",
            "80/640 Ry and 8x4x1 inherited; no Ru-specific cutoff or k-mesh ladder.",
            "Nominal U is matched; atomic Ru-4d projectors differ between the pseudopotentials.",
            "U=6.73 is PROJECTOR-MISMATCHED Xu corroboration, not an A7.3 endpoint.",
            "ONCV and GBRV Lowdin bases differ; populations are not compared.",
            "Failed or absent fixed rows remain unscored; no replacement, repair, or alternate seed selection.",
            "SCF completion verifies a fixed-geometry numerical calculation, not chemical stability.",
            "Primary Q uses four endpoint outputs; gas, slab and ZPE/TS cancel in this span only.",
            "An exact zero Xu margin is a tie and provides no positive-sign corroboration.",
        ],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", type=Path, help="separate readout artifact; omitted prints JSON")
    args = parser.parse_args(argv)
    if args.json:
        target = args.json.resolve()
        bank = (args.root / "docs/figs/a0main_readout.json").resolve()
        run_tree = (args.root / "runs").resolve()
        if target == bank or target == run_tree or run_tree in target.parents:
            parser.error("refusing to overwrite banked data or the run tree")
    result = build_readout(args.root)
    payload = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(payload, encoding="utf-8", newline="\n")
        print("RU-PP " + result["readiness"] + ": " + str(args.json))
    else:
        print(payload, end="")
    return 0 if result["readiness"] == "COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
