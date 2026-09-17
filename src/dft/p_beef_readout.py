"""S5 BEEF-vdW QC and paired-member CHE readout (base Ru/Ir/Ti).

Parser/QC is stdlib-only, including --check-output for remote preflight.
QE's 2000 printed perturbations are counted and checked, not index-matched
across MPI jobs. ASE regenerates one common N=2000, seed=0 coefficient set
from QE's 32 Ry basis contributions. BEEFEnsemble returns TOTAL energies.
This is XC-only spread at fixed PBE geometries with PBE pseudopotentials.

Source conventions: QEF/q-e qe-7.5 PW/src/beef.f90; vossjo/libbeef
src/beefun.c beefensemble_ (32-term dot product); ase/dft/bee.py.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import sys

RY_EV = 13.605693122  # campaign qe_qc/qe_slab convention
SIZE = 2000
SEED = 0
METALS = ("Ru", "Ir", "Ti")
STEMS = {"slab": "ref__2x1v__beef", "OH": "s0_OH__2x1v_mir__beef",
         "O": "s0_O__2x1v_mir__beef", "OOH": "s0_OOH__2x1v_mir__beef"}
NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?"


def _number(token):
    if re.fullmatch(NUMBER, token) is None:
        raise ValueError("malformed/nonfinite number: " + token)
    value = float(token.replace("D", "E").replace("d", "e"))
    if not math.isfinite(value):
        raise ValueError("nonfinite number")
    return value


def parse_text(text):
    """Strict single-run output parser; raises ValueError on invalid evidence."""
    if "\x00" in text:
        raise ValueError("NUL bytes in output")
    fatal = (r"convergence\s+NOT\s+achieved", r"Error in routine",
             r"IEEE_(?:INVALID|OVERFLOW|DIVIDE_BY_ZERO|DIVBYZERO)",
             r"Maximum CPU time exceeded", r"stopping.*(?:EXIT|user)")
    for pattern in fatal:
        if re.search(pattern, text, re.I):
            raise ValueError("failed output: " + pattern)
    ieee_flags = set(re.findall(r"\bIEEE_[A-Z_]+\b", text))
    unaccepted_flags = ieee_flags - {"IEEE_UNDERFLOW_FLAG", "IEEE_DENORMAL"}
    if unaccepted_flags:
        raise ValueError("unaccepted IEEE flags: " + ", ".join(sorted(unaccepted_flags)))
    if len(re.findall(r"JOB DONE\.", text)) != 1:
        raise ValueError("expected one JOB DONE")
    if len(re.findall(r"Program PWSCF", text)) != 1:
        raise ValueError("expected one PWSCF run")
    if not re.search(r"Exchange-correlation\s*=\s*BEEF-VDW\b", text, re.I):
        raise ValueError("missing BEEF-vdW functional identity")
    energies = list(re.finditer(r"(?m)^!\s+total energy\s*=\s*(\S+)\s+Ry\s*$", text))
    if len(energies) != 1:
        raise ValueError("expected one final SCF energy")
    energy = _number(energies[0].group(1))
    starts = list(re.finditer(r"(?m)^\s*BEEFens\s+(\d+)\s+ensemble energies\s*$", text))
    ends = list(re.finditer(r"(?m)^\s*BEEF-vdW xc energy contributions\s*$", text))
    if len(starts) != 1 or len(ends) != 1:
        raise ValueError("expected one ensemble and one XC contribution block")
    start, end = starts[0], ends[0]
    if int(start.group(1)) != SIZE:
        raise ValueError("emitted ensemble count must be 2000")
    done = text.index("JOB DONE.")
    if not energies[0].end() < start.start() < end.start() < done:
        raise ValueError("SCF/ensemble/contribution/completion order invalid")
    if not re.search(r"convergence has been achieved", text[energies[0].end():start.start()]):
        raise ValueError("missing converged SCF evidence")
    tokens = text[start.end():end.start()].split()
    if len(tokens) != SIZE:
        raise ValueError("truncated or oversized emitted ensemble block")
    # The QE block is an emission/QC control, not the paired ASE member source.
    emitted = [_number(x) for x in tokens]
    tail = text[end.end():done]
    lines = tail.lstrip("\r\n").splitlines()
    if len(lines) < 32:
        raise ValueError("truncated XC contribution block")
    contributions = []
    for i, line in enumerate(lines[:32], 1):
        match = re.fullmatch(r"\s*(\d+)\s*:\s*(\S+)\s*", line)
        if match is None or int(match.group(1)) != i:
            raise ValueError("malformed or out-of-order XC contribution " + str(i))
        contributions.append(_number(match.group(2)))
    if any(re.match(r"\s*\d+\s*:", line) for line in lines[32:]):
        raise ValueError("oversized XC contribution block")
    warnings = sorted(set(re.findall(r"IEEE_(?:UNDERFLOW_FLAG|DENORMAL)\b", text)))
    return dict(energy_Ry=energy, energy_eV=energy*RY_EV,
                xc_contributions_Ry=contributions,
                xc_contributions_eV=[x*RY_EV for x in contributions],
                emitted_members=len(emitted), warnings=warnings,
                emitted_member_role="count and finiteness QC only")


def check_output(path):
    """Return auditable QC, without importing numpy, ASE or the package."""
    path = Path(path)
    result = dict(path=str(path), status="MISSING", reasons=[])
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        result["reasons"] = ["missing output"]
        return result
    result["sha256_bytes"] = hashlib.sha256(data).hexdigest()
    try:
        result.update(parse_text(data.decode("utf-8")))
        result["status"] = "VALID_BEEF"
    except (ValueError, UnicodeError) as error:
        result.update(status="INVALID_BEEF", reasons=[str(error)])
    return result


parse_output = check_output


def ensemble_totals(record):
    """Regenerate common member indices; baseline is added ONCE by ASE."""
    if record.get("status") != "VALID_BEEF" or record["emitted_members"] != SIZE:
        raise ValueError("invalid BEEF record cannot enter estimator")
    import numpy as np
    from ase.dft.bee import BEEFEnsemble
    contributions = np.asarray(record["xc_contributions_eV"], dtype=float)
    energy = record["energy_eV"]
    if contributions.shape != (32,) or not np.isfinite(contributions).all() or not math.isfinite(energy):
        raise ValueError("nonfinite or malformed estimator inputs")
    totals = BEEFEnsemble(e=energy, contribs=contributions, xc="BEEF-vdW", verbose=False).get_ensemble_energies(size=SIZE, seed=SEED)
    if totals.shape != (SIZE,) or not np.isfinite(totals).all():
        raise ValueError("malformed regenerated ensemble")
    return totals


def ensemble_provenance():
    """Fingerprint the actual common coefficient matrix and installed generator."""
    import ase
    import ase.dft.bee as bee
    import ase.dft.pars_beefvdw as parameters
    coefficients = bee.BEEFEnsemble(e=0., contribs=[0.]*32, xc="BEEF-vdW", verbose=False).get_beefvdw_ensemble_coefs(SIZE, SEED)
    return dict(ase_version=ase.__version__, size=SIZE, seed=SEED,
                coefficients_float64_le_sha256=hashlib.sha256(coefficients.astype("<f8").tobytes()).hexdigest(),
                generator_source_sha256=hashlib.sha256(Path(bee.__file__).read_bytes()).hexdigest(),
                covariance_source_sha256=hashlib.sha256(Path(parameters.__file__).read_bytes()).hexdigest())


def summarize_members(energies):
    """Memberwise production CHE followed by maximum, then sample SD."""
    import numpy as np
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from hea_oer.referencing import delta_G
    from hea_oer.descriptors import oer_overpotential
    if set(energies) != {"slab", "OH", "O", "OOH", "H2", "H2O"}:
        raise ValueError("all four slab states and both gas references required")
    arrays = {key: np.asarray(value, dtype=float) for key, value in energies.items()}
    lengths = {value.shape for value in arrays.values()}
    if len(lengths) != 1 or any(value.ndim != 1 or len(value) < 2 or not np.isfinite(value).all() for value in arrays.values()):
        raise ValueError("member counts must match and all energies must be finite")
    n = len(arrays["slab"])
    etas, pls = [], []
    for i in range(n):
        g = [delta_G(arrays["slab"][i], arrays[sp][i], sp, arrays["H2O"][i], arrays["H2"][i]) for sp in ("OH", "O", "OOH")]
        if not all(math.isfinite(value) for value in g):
            raise ValueError("nonfinite member CHE energy")
        oer = oer_overpotential(*g)
        etas.append(float(oer.overpotential))
        pls.append(int(oer.potential_limiting_step))
    return dict(N=n, sigma_eta_V=float(np.std(etas, ddof=1)), eta_mean_V=float(np.mean(etas)),
                eta_members_V=etas, pls_histogram={str(i): pls.count(i) for i in range(1, 5)},
                estimator="sample std (ddof=1) of memberwise CHE maxima")


def ladder_b(sigmas):
    """Base-set absolute bands; missing metals never change denominator to a new set."""
    if set(sigmas) - set(METALS):
        raise ValueError("Ladder B admits only Ru, Ir, Ti")
    if any(not math.isfinite(v) or v < 0 for v in sigmas.values()):
        raise ValueError("invalid sigma")
    n = len(sigmas)
    low = sum(v < 0.25 for v in sigmas.values())
    high = sum(v >= 0.30 for v in sigmas.values())
    verdict = ("WITHDRAWN-UNSCORED" if n == 0 else "NOT SCOREABLE" if n == 1 else
               "CONFIRMED" if low >= 2 else "FALSIFIED" if high >= 2 else "MIDDLE BAND")
    return dict(ladder="B", registered_metals=list(METALS), n_scoreable=n,
                below_0_25_V=low, at_or_above_0_30_V=high, verdict=verdict)


def readout(base):
    """Read the 14 prepared production paths; never impute missing states."""
    base = Path(base)
    gases = {g: check_output(base / "gas" / (g + "__beef.out")) for g in ("H2", "H2O")}
    metals, sigmas = {}, {}
    for metal in METALS:
        records = {state: check_output(base / metal / (stem + ".out")) for state, stem in STEMS.items()}
        records.update(gases)
        invalid = {key: value["reasons"] for key, value in records.items() if value["status"] != "VALID_BEEF"}
        item = dict(outputs=records, status="NON_SCOREABLE" if invalid else "SCORED", exclusions=invalid)
        if not invalid:
            item.update(summarize_members({key: ensemble_totals(value) for key, value in records.items()}))
            sigmas[metal] = item["sigma_eta_V"]
        metals[metal] = item
    pending = any(r["status"] == "MISSING" for item in metals.values() for r in item["outputs"].values())
    score = ladder_b(sigmas)
    if pending:
        score["verdict"] = "PENDING OUTPUTS"
    return dict(schema="p-beef-readout-v1", date=datetime.now(timezone.utc).isoformat(),
                metals=metals, score=score, complete=not pending,
                generator_provenance=ensemble_provenance() if sigmas else None,
                ensemble=dict(source="ASE BEEFEnsemble total energies", size=SIZE, seed=SEED,
                              member_matching="same coefficient row across four states and both gases", ry_to_eV=RY_EV),
                scope="XC only, non-magnetic three; fixed PBE geometry and PBE-generated pseudopotentials; no geometry-XC uncertainty")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-output", type=Path)
    parser.add_argument("--base", type=Path, default=Path(__file__).resolve().parents[2]/"runs/s5")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = check_output(args.check_output) if args.check_output else readout(args.base)
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(text)
    else:
        print(text, end="")
    return (0 if result["status"] == "VALID_BEEF" else 1) if args.check_output else (0 if result["complete"] else 1)


if __name__ == "__main__":
    raise SystemExit(main())
