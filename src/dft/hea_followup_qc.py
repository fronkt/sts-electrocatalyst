"""Fixed-geometry SCF and complete collinear Lowdin-table checks for HEA follow-up.

Large residual forces are retained diagnostics, not SCF rejection criteria. Raw input,
SCF and projection files are read only; this module never deletes scratch or retries a job.
Pseudopotential and runtime-job correspondence remain separately verified by the caller.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re

import hea_force_audit as force

SCHEMA = "hea-followup-qc-v1"
FAILURES = re.compile(r"convergence NOT achieved|Maximum (?:CPU|wall) time exceeded|"
                      r"Program stopped by user request|Error in routine|MPI_ABORT|"
                      r"SIGTERM|SIGINT|SIGSEGV|Segmentation fault|Floating point exception|"
                      r"IEEE_INVALID_FLAG|IEEE_OVERFLOW_FLAG|forrtl:\s*severe", re.I)
ASSIGNMENT = re.compile(r"^([A-Za-z][A-Za-z0-9_ -]*)\s*=\s*(" + force.NUM + r")$")
ATOM = re.compile(r"^Atom\s+#\s*(\d+)\s*:\s*(.*)$")


def _assignments(text):
    fields = [f.strip() for f in text.split(",")]
    if fields[-1] == "":
        fields.pop()
    if not fields or any(not f for f in fields):
        raise ValueError("empty Lowdin assignment")
    values, tokens = {}, {}
    for field in fields:
        match = ASSIGNMENT.fullmatch(field)
        if not match:
            raise ValueError("malformed Lowdin numerical assignment")
        key, token = match[1].strip(), match[2]
        if key in values:
            raise ValueError("duplicate Lowdin assignment")
        values[key], tokens[key] = force.number(token), token
    return values, tokens


def _rounding_half_unit(token):
    value = Decimal(token.replace("D", "e").replace("d", "e"))
    return Decimal(5).scaleb(value.as_tuple().exponent - 1)


def _consistent(tokens, target, left, right, sign):
    """Only check consistency to the uncertainty of the printed decimal places."""
    decimals = {k: Decimal(tokens[k].replace("D", "e").replace("d", "e"))
                for k in (target, left, right)}
    error = abs(decimals[target] - (decimals[left] + sign*decimals[right]))
    bound = sum(_rounding_half_unit(tokens[k]) for k in decimals)
    if error > bound:
        raise ValueError("Lowdin total charge/polarization inconsistent with printed spin totals")


def projection_text(text, labels):
    """One ordered full Lowdin table; no fragment or spin-ground-state inference."""
    failures = sorted(set(m[0] for m in FAILURES.finditer(text)))
    if failures:
        raise ValueError("projection failure markers: " + ", ".join(failures))
    headers = list(re.finditer(r"^\s*Lowdin Charges:\s*$", text, re.M))
    spills = list(re.finditer(r"^\s*Spilling Parameter:\s*(" + force.NUM + r")\s*$", text, re.M))
    if text.count("JOB DONE") != 1 or text.count("Lowdin Charges") != 1 or len(headers) != 1:
        raise ValueError("expected one JOB DONE and one Lowdin header")
    if text.count("Spilling Parameter") != 1 or len(spills) != 1:
        raise ValueError("missing or malformed Spilling Parameter terminator")
    if not headers[0].end() < spills[0].start() < text.index("JOB DONE"):
        raise ValueError("Lowdin/completion ordering invalid")
    spilling = force.number(spills[0][1])
    block = text[headers[0].end():spills[0].start()]
    rows, current = [], None
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        atom = ATOM.fullmatch(stripped)
        if atom:
            if current is not None:
                rows.append(current)
            values, tokens = _assignments(atom[2])
            if next(iter(values)) != "total charge":
                raise ValueError("atom row lacks leading total charge")
            current = dict(qe_index=int(atom[1]), values={"total charge": values.pop("total charge")},
                           tokens={"total charge": tokens["total charge"]},
                           orbital_populations={"charge": values, "spin up": {}, "spin down": {}, "polarization": {}},
                           line_counts={"spin up": 0, "spin down": 0, "polarization": 0}, stage=0)
            continue
        if current is None:
            raise ValueError("Lowdin field before first atom")
        values, tokens = _assignments(stripped)
        channel = next(iter(values))
        if channel not in current["line_counts"]:
            raise ValueError("unexpected Lowdin row")
        stage = {"spin up": 1, "spin down": 2, "polarization": 3}[channel]
        if stage < current["stage"] or current["stage"] == 3:
            raise ValueError("reordered or duplicate Lowdin spin/polarization row")
        current["stage"] = stage
        value = values.pop(channel)
        if channel in current["values"] and current["values"][channel] != value:
            raise ValueError("repeated spin totals disagree")
        current["values"][channel] = value
        current["tokens"][channel] = tokens[channel]
        current["line_counts"][channel] += 1
        orbitals = current["orbital_populations"][channel]
        if set(orbitals) & set(values):
            raise ValueError("duplicate orbital field within a spin channel")
        orbitals.update(values)
    if current is not None:
        rows.append(current)
    # Count any malformed or extra atom markers as well as successfully parsed rows.
    if (len(rows) != len(labels) or [r["qe_index"] for r in rows] != list(range(1, len(labels)+1))
            or len(re.findall(r"^\s*Atom\s*#", text, re.M)) != len(labels)):
        raise ValueError("partial, duplicated, reordered or extra Lowdin atom rows")
    atoms = []
    for i, row in enumerate(rows):
        counts = row["line_counts"]
        if counts["polarization"] != 1 or counts["spin up"] < 1 or counts["spin down"] < 1:
            raise ValueError("incomplete atom spin/polarization fields")
        orbitals = row["orbital_populations"]
        if set(orbitals["spin up"]) != set(orbitals["spin down"]):
            raise ValueError("incomplete spin-channel orbital rows")
        if not set(orbitals["charge"]) <= set(orbitals["spin up"]):
            raise ValueError("missing aggregate orbital populations in both spin channels")
        if set(orbitals["charge"]) != set(orbitals["polarization"]):
            raise ValueError("incomplete polarization orbital fields")
        _consistent(row["tokens"], "total charge", "spin up", "spin down", 1)
        _consistent(row["tokens"], "polarization", "spin up", "spin down", -1)
        values = row["values"]
        atoms.append(dict(index=i, species=labels[i], charge_e=values["total charge"],
                          spin_up_e=values["spin up"], spin_down_e=values["spin down"],
                          moment_muB=values["polarization"], orbital_populations=orbitals))
    return dict(status="COMPLETE", nat=len(labels), atoms=atoms, spilling_parameter=spilling,
                interpretation="Lowdin projected charge/spin populations; no oxidation-state or spin-ground-state assignment")


def evidence(path):
    path = Path(path)
    return dict(path=str(path), sha256_bytes=hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None)


def audit_files(infile, outfile, projection=None):
    rec = dict(schema=SCHEMA, status="REJECTED", reasons=[], scf=None, projection=None,
               pairing="Caller verifies runtime input, projection-job correspondence and pseudopotential identity separately.")
    try:
        rec["input"], rec["output"] = evidence(infile), evidence(outfile)
        if projection is not None:
            rec["projection_file"] = evidence(projection)
        rec["scf"] = force.audit_files(Path(infile), Path(outfile))
        if rec["scf"]["status"] != "VALID_SCF":
            rec["reasons"] = ["SCF not valid: " + reason for reason in rec["scf"]["reasons"]]
            return rec
        # The force auditor's pre-existing failure list is intentionally unchanged.
        out_text = Path(outfile).read_text(encoding="utf-8", errors="replace")
        failures = sorted(set(m[0] for m in FAILURES.finditer(out_text)))
        if failures:
            raise ValueError("SCF failure markers: " + ", ".join(failures))
        if projection is None:
            rec["status"] = "VALID_SCF"
        else:
            labels = [a["species"] for a in rec["scf"]["per_atom"]]
            rec["projection"] = projection_text(Path(projection).read_text(encoding="utf-8", errors="strict"), labels)
            rec["status"] = "COMPLETE"
        json.dumps(rec, allow_nan=False)
    except (OSError, UnicodeError, ValueError, ArithmeticError) as error:
        rec["status"] = "REJECTED"
        rec["reasons"] = [str(error)]
    try:
        json.dumps(rec, allow_nan=False)
    except ValueError:
        rec.update(status="REJECTED", scf=None, projection=None,
                   reasons=["nonfinite derived SCF/projection audit values"])
    return rec


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--projection", type=Path)
    parser.add_argument("--json", type=Path, required=True)
    args = parser.parse_args(argv)
    raw_paths = {p.resolve() for p in (args.input, args.output, args.projection) if p is not None}
    if args.json.resolve() in raw_paths:
        parser.error("JSON output must not overwrite a raw file")
    rec = audit_files(args.input, args.output, args.projection)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    with args.json.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(rec, handle, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps(dict(status=rec["status"], reasons=rec["reasons"])))
    return 0 if rec["status"] in ("VALID_SCF", "COMPLETE") else 2


if __name__ == "__main__":
    raise SystemExit(main())
