"""P-XU / P-XU-SPAN adapter over the pinned Xu Zenodo deposit.

The silentgate instrument supplies force, header, deck and energy evidence.
This adapter applies the distinct registered population clauses and retains
incomplete evidence. Corpus files are read only and remain outside the repo.
"""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from silentgate.classify import classify
from silentgate.readers.qe import read_qe

METALS = ("CrO2", "IrO2", "MnO2", "MoO2", "NbO2", "PtO2", "ReO2", "RhO2", "RuO2", "TiO2")
SEEN = ("CrO2", "MnO2", "IrO2", "TiO2")
U_VALUES = tuple(f"{i / 2:.1f}" for i in range(17))
STATES = ("bare", "O", "OH", "OOH")
ARCHIVE_MD5 = "e193c56cf17c6d98827bbb19752d04b3"
TREE_SHA256 = "d20af9dbfbbbdc05714b352ac15b176e75b4096f5bff475159395187c957e8b9"
TREE = ROOT / "docs/research/2026-08-15-sampling/xu_tree.json"
RY_EV = Decimal("13.605693122")
NUM = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][+-]?\d+)?"
ENERGY = re.compile(r"^\s*!\s+total energy\s*=\s*(" + NUM + r")\s+Ry\b", re.M | re.I)


def digest(path, algorithm="sha256"):
    h = hashlib.new(algorithm)
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def decimal(token):
    value = Decimal(token.replace("D", "e").replace("d", "e"))
    if not value.is_finite():
        raise ValueError("nonfinite number")
    return value


def population():
    rows = []
    for metal in METALS:
        jobs = [(2, f"{state}-U-{u}", state, u) for u in U_VALUES for state in STATES]
        jobs += [(2, state + suffix, state, None) for suffix in ("", "-relax-surf") for state in STATES[1:]]
        jobs += [(4, "bare", "bare", None)]
        jobs += [(4, state + suffix, state, None) for suffix in ("", "-relax") for state in STATES[1:]]
        for layer, job, state, u in jobs:
            folder = f"supporting-data/{metal}/Eads-{layer}-layers/{job}"
            rows.append(dict(metal=metal, layers=layer, job=job, state=state, u_eV=u,
                             output=folder + "/pwscf.out", input=folder + "/pwscf.in"))
    return rows


def verify_identity(corpus, archive, tree_path=TREE):
    corpus, archive = Path(corpus).resolve(), Path(archive).resolve()
    if corpus == ROOT or ROOT in corpus.parents:
        raise ValueError("corpus must remain outside the repository")
    if digest(tree_path) != TREE_SHA256:
        raise ValueError("registered mirror-tree bytes differ")
    if digest(archive, "md5") != ARCHIVE_MD5:
        raise ValueError("registered archive MD5 differs")
    tree = json.loads(Path(tree_path).read_text(encoding="utf-8"))
    manifest = {r["path"]: r for r in tree["tree"] if r["type"] == "blob"}
    expected = {r["output"] for r in population()}
    actual = {p.relative_to(corpus).as_posix() for p in corpus.glob("supporting-data/*/Eads-*/**/pwscf.out")}
    if actual != expected:
        raise ValueError(f"population differs: missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    files = []
    for row in population():
        for kind in ("input", "output"):
            relative = row[kind]
            data = (corpus / relative).read_bytes()
            source = manifest[relative]
            blob = git_blob(data)
            if len(data) != source["size"] or blob != source["sha"]:
                raise ValueError("deposited bytes differ: " + relative)
            files.append(dict(path=relative, bytes=len(data), git_blob_sha1=blob,
                              sha256=hashlib.sha256(data).hexdigest()))
    return dict(archive=str(archive), archive_md5=ARCHIVE_MD5, extraction_root=str(corpus),
                tree_sha256=TREE_SHA256, selected_outputs=810, selected_inputs=810,
                comparison="all selected input/output bytes match registered Git blob hashes and sizes", files=files)


def assignments(text):
    """Supplement the approved deck reader with declared namelist fields it omits."""
    clean = re.sub(r"'[^']*'|\"[^\"]*\"|![^\n]*", lambda m: "" if m[0].startswith("!") else m[0], text)
    out = {}
    for key, token in re.findall(r"(?m)^\s*([A-Za-z_]\w*(?:\s*\(\s*\d+\s*\))?)\s*=\s*([^\n,]+)", clean):
        key, token = re.sub(r"\s", "", key).lower(), token.strip()
        if token[:1] in ("'", '"'):
            value = token[1:-1]
        elif token.lower() in (".true.", ".false.", "t", "f"):
            value = token.lower() in (".true.", "t")
        else:
            try:
                value = float(decimal(token))
            except Exception:
                value = token
        out[key] = value
    return out


def energy_evidence(text, calculation, energies):
    """Energy usability is separate from lock evidence and requires convergence."""
    tokens = ENERGY.findall(text)
    reasons = []
    severe = re.findall(r"convergence NOT achieved|Maximum (?:CPU|wall) time exceeded|"
                        r"maximum number of steps has been reached|Error in routine|MPI_ABORT|SIGSEGV|SIGFPE|"
                        r"IEEE_(?:INVALID|OVERFLOW|DIVIDE_BY_ZERO)(?:_FLAG)?|Program stopped by user request", text, re.I)
    converged = re.findall(r"convergence has been achieved in\s+(\d+)\s+iterations", text)
    ionic = re.findall(r"bfgs converged in\s+(\d+)\s+scf cycles and\s+(\d+)\s+bfgs steps", text, re.I)
    if severe:
        reasons.append("failure markers")
    if text.count("JOB DONE") != 1:
        reasons.append("expected exactly one JOB DONE")
    if not tokens or len(tokens) != len(converged) or len(tokens) != len(energies):
        reasons.append("SCF energies/convergence witnesses differ or missing")
    if calculation == "relax":
        if len(ionic) != 1 or int(ionic[0][0]) != len(tokens):
            reasons.append("ionic convergence missing or cycle count differs")
    elif calculation != "scf":
        reasons.append("unsupported or missing calculation type")
    elif len(tokens) != 1:
        reasons.append("SCF calculation has multiple energies")
    values = [decimal(t) for t in tokens]
    if any(abs(float(v) - parsed) > 1e-10 for v, parsed in zip(values, energies)):
        reasons.append("independent token/approved energy reader disagreement")
    return dict(usable=not reasons, reasons=reasons, failure_markers=sorted(set(severe)),
                job_done_count=text.count("JOB DONE"), scf_iterations=[int(x) for x in converged],
                ionic_converged=bool(ionic), ionic_scf_cycles=int(ionic[0][0]) if len(ionic) == 1 else None,
                ionic_steps=int(ionic[0][1]) if len(ionic) == 1 else None,
                energies_Ry=[str(v) for v in values],
                final_energy_Ry=str(values[-1]) if values and not reasons else None)


def force_evidence(raw):
    """Three distinct records: final-step ALL, every-step intersection, and core verdict."""
    atoms, steps = raw["adsorbate_indices"], raw["force_steps"]
    identified = raw["identified_adsorbate_indices"]
    reasons = list(raw.get("force_issues", []))
    if raw["unidentified"]:
        reasons.append("UNIDENTIFIED")
    if not steps:
        reasons.append("NO_FORCE_BLOCK")
    if not atoms:
        reasons.append("NO_ELIGIBLE_ADSORBATE_ATOMS")
    if any(any(i not in step for i in identified) for step in steps):
        reasons.append("identified adsorbate missing in force step")
    scorable = not reasons
    final = [axis for k, axis in enumerate(("x", "y")) if all(steps[-1][i][k] == 0.0 for i in atoms)] if scorable else None
    all_steps = [axis for k, axis in enumerate(("x", "y")) if all(step[i][k] == 0.0 for step in steps for i in atoms)] if scorable else None
    core = classify(raw)
    return dict(scorable=scorable, reasons=sorted(set(reasons)), n_force_steps=len(steps), single_block=len(steps) == 1,
                identified_adsorbate_indices=identified, eligible_adsorbate_indices=atoms,
                excluded_adsorbate_indices=sorted(set(identified)-set(atoms)),
                n_if_pos_excluded_all_atoms=raw["n_if_pos_excluded"],
                final_all_atom_zero_lateral_axes=final, final_clause=(bool(final) if scorable else None),
                every_step_all_atom_zero_lateral_axes=all_steps,
                per_atom_per_step=[{str(i): [v == 0.0 for v in step[i]] for i in atoms if i in step} for step in steps],
                per_atom_directions=core.get("per_atom_directions", {}),
                silentgate_verdict=core["verdict"], silentgate_unscorable=core["unscorable"],
                silentgate_reasons=core["unscorable_reasons"], issues=raw["issues"])


def analyse_row(corpus, row):
    out, deck = Path(corpus) / row["output"], Path(corpus) / row["input"]
    raw = read_qe(out, deck_path=deck)
    text = out.read_text(encoding="utf-8", errors="replace")
    declared = assignments(deck.read_text(encoding="utf-8", errors="replace"))
    metadata = {k: declared.get(k) for k in ("calculation", "nspin", "tot_magnetization", "forc_conv_thr", "conv_thr", "electron_maxstep", "nstep", "ecutwfc", "ecutrho", "u_projection_type")}
    return dict(row, header={k: raw[k] for k in ("n_symops", "header_form", "symmetry_headers", "symmetry_conflict")},
                declared=metadata, declared_namelist=declared,
                deck={k: raw["deck"][k] for k in ("nat", "nspin", "tot_magnetization", "U", "forc_conv_thr", "nosym", "issues")},
                noise_floor_Ry_bohr=raw["forc_conv_thr"] / 20,
                bare_nat=raw["bare_nat"], bare_references=[Path(p).relative_to(corpus).as_posix() for p in raw["bare_references"]],
                unidentified=raw["unidentified"], force=force_evidence(raw),
                energy=energy_evidence(text, declared.get("calculation"), raw["energies_ry"]))


def fraction_clause(successes, unknown, denominator):
    if denominator <= 0:
        outcome = "INCOMPLETE EVIDENCE"
    elif successes * 100 >= 90 * denominator:
        outcome = "HELD"
    elif (successes + unknown) * 100 < 75 * denominator:
        outcome = "FALSIFIED"
    elif unknown:
        outcome = "INCOMPLETE EVIDENCE"
    else:
        outcome = "SCORED — MIDDLE BAND / NOT MET"
    return dict(successes=successes, unknown=unknown, denominator=denominator,
                known_failures=denominator-successes-unknown, lower_count=successes, upper_count=successes+unknown,
                lower_fraction=successes/denominator if denominator else None,
                upper_fraction=(successes+unknown)/denominator if denominator else None, outcome=outcome)


def score_census(rows):
    if len(rows) != 810 or Counter(r["metal"] for r in rows) != Counter({m: 81 for m in METALS}):
        raise ValueError("P-XU population must be 810 / 81 per metal")
    headers = fraction_clause(sum(r["header"]["n_symops"] is not None and r["header"]["n_symops"] > 1 for r in rows),
                              sum(r["header"]["n_symops"] is None for r in rows), 810)
    ads = [r for r in rows if r["state"] != "bare"]
    if len(ads) != 630:
        raise ValueError("registered adsorbate population must be 630")
    unidentified = [r["output"] for r in ads if r["unidentified"]]
    no_force = [r["output"] for r in ads if not r["force"]["n_force_steps"]]
    excluded = set(unidentified) | set(no_force)
    eligible = [r for r in ads if r["output"] not in excluded]
    force = fraction_clause(sum(r["force"]["final_clause"] is True for r in eligible),
                            sum(r["force"]["final_clause"] is None for r in eligible), len(eligible))
    force.update(original_denominator=630, unidentified_outputs=unidentified, no_force_block_outputs=no_force,
                 excluded_union=len(excluded), no_eligible_adsorbate_outputs=[r["output"] for r in eligible if not r["force"]["eligible_adsorbate_indices"]])
    pairs, maps = [], []
    for metal in METALS:
        group = [r for r in rows if r["metal"] == metal]
        pair = {state: next(r for r in group if r["layers"] == 4 and r["job"] == state + "-relax") for state in ("OH", "OOH")}
        directions = {s: r["force"]["every_step_all_atom_zero_lateral_axes"] for s, r in pair.items()}
        known = all(v is not None for v in directions.values())
        orthogonal = (all(len(v) == 1 for v in directions.values()) and directions["OH"] != directions["OOH"]) if known else None
        pairs.append(dict(metal=metal, members={s:r["output"] for s,r in pair.items()}, locked_sets=directions,
                          orthogonal=orthogonal, seen_force_sample=metal in SEEN, blind_by_record=metal not in SEEN,
                          blind_by_availability=metal not in (*SEEN, "RuO2")))
        group = [r for r in group if r["state"] in ("OH", "OOH")]
        if len(group) != 42:
            raise ValueError("direction-map population must be 42 per metal")
        deviations = [r["output"] for r in group if r["force"]["every_step_all_atom_zero_lateral_axes"] is not None
                      and directions[r["state"]] is not None and r["force"]["every_step_all_atom_zero_lateral_axes"] != directions[r["state"]]]
        unknowns = [r["output"] for r in group if r["force"]["every_step_all_atom_zero_lateral_axes"] is None]
        maps.append(dict(metal=metal, denominator=42, mixed=bool(deviations), deviating_jobs=deviations, unscorable_jobs=unknowns,
                         outputs=[dict(output=r["output"], state=r["state"], axes=r["force"]["every_step_all_atom_zero_lateral_axes"]) for r in group]))
    n = sum(p["orthogonal"] is True for p in pairs)
    unknown = sum(p["orthogonal"] is None for p in pairs)
    direction_outcome = "HELD" if n >= 8 else "FALSIFIED" if n+unknown <= 4 else "INCOMPLETE EVIDENCE" if unknown else "SCORED — MIDDLE BAND / NOT MET"
    direction = dict(successes=n, unknown=unknown, denominator=10, lower_count=n, upper_count=n+unknown, outcome=direction_outcome, pairs=pairs)
    direction["subsets"] = {label: dict(metals=[p["metal"] for p in pairs if predicate(p)],
                                           successes=sum(p["orthogonal"] is True for p in pairs if predicate(p)),
                                           unknown=sum(p["orthogonal"] is None for p in pairs if predicate(p)))
                            for label, predicate in (("seen", lambda p:p["seen_force_sample"]), ("blind_by_record", lambda p:p["blind_by_record"]),
                                                     ("blind_by_availability", lambda p:p["blind_by_availability"]))}
    outcomes = [headers["outcome"], force["outcome"], direction["outcome"]]
    combined = "FALSIFIED" if "FALSIFIED" in outcomes else "HELD" if all(v == "HELD" for v in outcomes) else "INCOMPLETE EVIDENCE" if "INCOMPLETE EVIDENCE" in outcomes else "SCORED — MIDDLE BAND / NOT MET"
    oxygen = [r for r in rows if r["state"] == "O" and r["declared"]["calculation"] == "relax"]
    return dict(outcome=combined, header=headers, final_force=force, named_pair_direction=direction, direction_maps=maps,
                P_A2_descriptive=dict(denominator=len(oxygen), both_axes=sum(r["force"]["final_all_atom_zero_lateral_axes"] == ["x", "y"] for r in oxygen),
                                     unknown=sum(r["force"]["final_all_atom_zero_lateral_axes"] is None for r in oxygen)))


def score_spans(rows):
    ladder = [r for r in rows if r["u_eV"] is not None]
    if len(ladder) != 680:
        raise ValueError("registered ladder must contain 680 outputs")
    metals = []
    for metal in METALS:
        rungs = []
        for u in U_VALUES:
            states = {r["state"]:r for r in ladder if r["metal"] == metal and r["u_eV"] == u}
            if set(states) != set(STATES):
                raise ValueError("four-state rung incomplete in population")
            rec = dict(u_eV=u, usable_states=[s for s,r in states.items() if r["energy"]["usable"]],
                       outputs={s:r["output"] for s,r in states.items()})
            for key, left, right in (("cM_electronic_eV", "OOH", "OH"), ("dG2_electronic_eV", "O", "OH")):
                rec[key] = str((decimal(states[left]["energy"]["final_energy_Ry"])-decimal(states[right]["energy"]["final_energy_Ry"]))*RY_EV) if all(states[s]["energy"]["usable"] for s in (left,right)) else None
            rungs.append(rec)
        summaries = {}
        for key in ("cM_electronic_eV", "dG2_electronic_eV"):
            values = [decimal(r[key]) for r in rungs if r[key] is not None]
            span = max(values)-min(values) if values else None
            summaries[key] = dict(paired_usable_rungs=len(values), full_ladder=len(values)==17,
                                  primary_span_eV=str(span) if len(values)==17 else None,
                                  observed_range_lower_bound_eV=str(span) if span is not None else None,
                                  missing_u_eV=[r["u_eV"] for r in rungs if r[key] is None])
        metals.append(dict(metal=metal, complete_four_state_rungs=sum(len(r["usable_states"])==4 for r in rungs), rungs=rungs, spans=summaries))
    primary = [m["spans"]["cM_electronic_eV"] for m in metals]
    n = sum(p["full_ladder"] and decimal(p["primary_span_eV"]) > Decimal("0.20") for p in primary)
    missing = sum(not p["full_ladder"] for p in primary)
    outcome = "HELD" if n>=5 else "FALSIFIED" if n+missing<3 else "INCOMPLETE EVIDENCE" if missing else "SCORED — MIDDLE BAND / NOT MET"
    return dict(outcome=outcome, denominator=10, ladder_output_denominator=680, full_ladder_exceeding_count=n,
                incomplete_metals=missing, possible_max_count=n+missing, metals=metals,
                gas_reference_scope="Ranges of E_OOH-E_OH and E_O-E_OH; constant references and corrections cancel.",
                absolute_overpotential="NOT COMPUTED", floor_margin="DEFERRED until exact matching molecule references pass")


def source_commit():
    git = ROOT / ".git"
    if not git.is_dir():
        return None
    head = (git / "HEAD").read_text(encoding="utf-8").strip()
    if not head.startswith("ref: "):
        return head
    ref = head[5:]
    if (git / ref).exists():
        return (git/ref).read_text().strip()
    for line in (git / "packed-refs").read_text().splitlines() if (git/"packed-refs").exists() else []:
        if line.endswith(" " + ref):
            return line.split()[0]
    return None


def run(corpus, archive):
    identity = verify_identity(corpus, archive)
    rows = []
    for index, row in enumerate(population(), 1):
        rows.append(analyse_row(corpus, row))
        if index % 81 == 0:
            print(f"Parsed {index}/810: {row['metal']}", flush=True)
    return dict(schema="s2-xu-census-v1", source_commit=source_commit(), corpus_identity=identity,
                code_sha256={p.relative_to(ROOT).as_posix():digest(p) for package in (ROOT/"silentgate", Path(__file__).parent) for p in sorted(package.rglob("*.py"))},
                registration="docs/43 A9.3.2–3; docs/research/s2-operating-decisions-2026-09-18.md",
                attribution="Xu, Rossmeisl & Kitchin (2015), doi:10.1021/jp511426q; Zenodo doi:10.5281/zenodo.12635, CC0",
                rows=rows, P_XU=score_census(rows), P_XU_SPAN=score_spans(rows))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", required=True, type=Path, help="extracted zhongnanxu-rutile-OER-c4cb892 directory")
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    if args.corpus.resolve() in args.out.resolve().parents:
        parser.error("write results outside the corpus")
    result = run(args.corpus.resolve(), args.archive)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps({key:result[key]["outcome"] for key in ("P_XU", "P_XU_SPAN")}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
