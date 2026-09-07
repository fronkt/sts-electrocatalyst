"""Strict fixed-geometry QE force audit; high residual force is not an SCF failure.

Input/output pairing is supplied by the caller and recorded by byte hashes.
Only one completed SCF and one full force block are accepted. This deliberately
refuses relax trajectories, concatenated runs, truncated tables and missing masks.
Force norms use Cartesian if_pos components, including partially fixed atoms.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

RY_TO_EV = 13.605693122
RY_BOHR_TO_EV_A = 25.71104309541616
NUM = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][+-]?\d+)?"
FORCE = re.compile(r"^\s*atom\s+(\d+)\s+type\s+(\d+)\s+force\s*=\s*(" + NUM + r")\s+(" + NUM + r")\s+(" + NUM + r")\s*$", re.M)


def number(value: str) -> float:
    result = float(value.replace("D", "e").replace("d", "e"))
    if not math.isfinite(result):
        raise ValueError("nonfinite numerical value")
    return result


def input_atoms(text: str) -> tuple[list[str], list[list[int]], list[int]]:
    clean = "\n".join(line.split("!", 1)[0] for line in text.splitlines())
    calculations = re.findall(r"\bcalculation\s*=\s*['\"]([^'\"]+)['\"]", clean, re.I)
    if len(re.findall(r"\bcalculation\s*=", clean, re.I)) != 1 or [c.lower() for c in calculations] != ["scf"]:
        raise ValueError("only explicit calculation='scf' is supported")
    nat_match = re.findall(r"\bnat\s*=\s*(\d+)\b", clean, re.I)
    if len(nat_match) != 1 or int(nat_match[0]) <= 0:
        raise ValueError("one positive nat required")
    nat = int(nat_match[0])
    lines = [line.strip() for line in clean.splitlines() if line.strip()]
    starts = [i for i, line in enumerate(lines) if line.upper().startswith("ATOMIC_POSITIONS")]
    if len(starts) != 1:
        raise ValueError("one ATOMIC_POSITIONS card required")
    species_starts = [i for i, line in enumerate(lines) if line.upper() == "ATOMIC_SPECIES"]
    if len(species_starts) != 1:
        raise ValueError("one ATOMIC_SPECIES card required")
    species = []
    for line in lines[species_starts[0] + 1:]:
        fields = line.split()
        if len(fields) != 3:
            break
        try:
            number(fields[1])
        except ValueError:
            break
        species.append(fields[0])
    if not species or len(set(species)) != len(species):
        raise ValueError("missing or duplicate species labels")
    labels, masks, types = [], [], []
    rows = lines[starts[0] + 1:starts[0] + 1 + nat]
    if len(rows) != nat:
        raise ValueError("incomplete ATOMIC_POSITIONS")
    for line in rows:
        fields = line.split()
        if len(fields) not in (4, 7) or fields[0] not in species:
            raise ValueError("invalid atom row or unknown species")
        for value in fields[1:4]:
            number(value)
        flags = fields[4:] or ["1", "1", "1"]
        if any(flag not in ("0", "1") for flag in flags):
            raise ValueError("if_pos flags must be 0 or 1")
        labels.append(fields[0])
        masks.append([int(flag) for flag in flags])
        types.append(species.index(fields[0]) + 1)
    return labels, masks, types


def audit_text(in_text: str, out_text: str | None, threshold_ev_a: float = 0.05) -> dict:
    if isinstance(threshold_ev_a, bool) or not math.isfinite(threshold_ev_a) or threshold_ev_a <= 0:
        raise ValueError("positive finite diagnostic threshold required")
    labels, masks, types = input_atoms(in_text)
    record = dict(schema="hea-force-audit-v1", status="PENDING", reasons=[],
                  geometry_stationarity="UNASSESSED", threshold_ev_A=threshold_ev_a,
                  threshold_role="diagnostic, not calibrated accuracy", energy_eV=None,
                  fmax_free_ev_A=None, fmax_all_ev_A=None, per_atom=[])
    if out_text is None:
        record["reasons"] = ["output absent"]
        return record
    failures = [term for term in ("convergence NOT achieved", "Maximum CPU time exceeded",
                "Program stopped by user request", "Error in routine", "MPI_ABORT") if term in out_text]
    if failures:
        record.update(status="REJECTED", reasons=failures)
        return record
    if "JOB DONE" not in out_text:
        record["reasons"] = ["no JOB DONE; incomplete output"]
        return record
    energies = list(re.finditer(r"^!\s+total energy\s*=\s*(" + NUM + r")\s+Ry\s*$", out_text, re.M))
    converged = list(re.finditer(r"convergence has been achieved in\s+\d+ iterations", out_text))
    headers = list(re.finditer(r"Forces acting on atoms\s*\(cartesian axes, Ry/au\):", out_text))
    nat = re.findall(r"number of atoms/cell\s*=\s*(\d+)", out_text)
    if (out_text.count("JOB DONE") != 1 or len(energies) != 1 or len(converged) != 1
            or len(headers) != 1 or nat != [str(len(labels))]):
        record.update(status="REJECTED", reasons=["expected one SCF, energy, matching nat and force block"])
        return record
    if not (energies[0].start() < converged[0].start() < headers[0].start() < out_text.index("JOB DONE")):
        record.update(status="REJECTED", reasons=["SCF/force/completion ordering invalid"])
        return record
    tail = out_text[headers[0].end():out_text.index("JOB DONE")]
    total = re.search(r"Total force\s*=", tail)
    if total is None:
        record.update(status="REJECTED", reasons=["force block has no terminator"])
        return record
    block = tail[:total.start()]
    matches = list(FORCE.finditer(block))
    # Reject duplicate/missing/out-of-order rows, unsupported numeric tokens and type mismatch.
    if (len(matches) != len(labels) or len(re.findall(r"^\s*atom\s+", block, re.M)) != len(labels)
            or [int(m[1]) for m in matches] != list(range(1, len(labels) + 1))
            or [int(m[2]) for m in matches] != types):
        record.update(status="REJECTED", reasons=["incomplete, duplicate, reordered or mismatched force rows"])
        return record
    for i, (match, flags) in enumerate(zip(matches, masks)):
        vector = [number(match[j]) * RY_BOHR_TO_EV_A for j in (3, 4, 5)]
        free_vector = [v * flag for v, flag in zip(vector, flags)]
        record["per_atom"].append(dict(index=i, species=labels[i], if_pos=flags,
            force_ev_A=vector, free_force_ev_A=free_vector,
            norm_all_ev_A=math.hypot(*vector), norm_free_ev_A=math.hypot(*free_vector)))
    all_max = max(row["norm_all_ev_A"] for row in record["per_atom"])
    free_rows = [row for row in record["per_atom"] if any(row["if_pos"])]
    free_max = max((row["norm_free_ev_A"] for row in free_rows), default=None)
    record.update(status="VALID_SCF", energy_eV=number(energies[0][1]) * RY_TO_EV,
                  fmax_free_ev_A=free_max, fmax_all_ev_A=all_max,
                  n_free_atoms=len(free_rows), n_free_components=sum(map(sum, masks)),
                  geometry_stationarity=("NO_FREE_COORDINATES" if free_max is None else
                    "ABOVE_THRESHOLD" if free_max > threshold_ev_a else "WITHIN_THRESHOLD"))
    for name in ("total", "absolute"):
        moments = re.findall(name + r" magnetization\s*=\s*(" + NUM + ")", out_text)
        record[name + "_moment_muB"] = number(moments[-1]) if moments else None
    return record


def audit_files(infile: Path, outfile: Path, threshold_ev_a: float = 0.05) -> dict:
    ib = Path(infile).read_bytes()
    ob = Path(outfile).read_bytes() if Path(outfile).exists() else None
    rec = audit_text(ib.decode("utf-8"), ob.decode("utf-8", "replace") if ob is not None else None, threshold_ev_a)
    rec["input"] = dict(path=str(infile), sha256_bytes=hashlib.sha256(ib).hexdigest())
    rec["output"] = dict(path=str(outfile), sha256_bytes=hashlib.sha256(ob).hexdigest() if ob is not None else None)
    rec["pairing"] = "caller-supplied input/output; verify runtime deck identity before scientific use"
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--json", type=Path, required=True)
    ap.add_argument("--threshold-ev-a", type=float, default=0.05)
    args = ap.parse_args()
    rec = audit_files(args.input, args.output, args.threshold_ev_a)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(rec, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({key: rec[key] for key in ("status", "geometry_stationarity", "fmax_free_ev_A")}))
    return {"VALID_SCF": 0, "PENDING": 3, "REJECTED": 2}[rec["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
