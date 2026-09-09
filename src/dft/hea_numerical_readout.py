"""Read-only paired numerical sensitivity and bounded recovery readout.

Only accepted raw SCF/projection files with matching stored QC enter differences.
No numerical-accuracy threshold, magnetic-basin assignment, or ranking is inferred.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re

try:
    from . import hea_force_audit as force
    from . import hea_numerical_guard as guard
    from . import hea_followup_qc as qc
except ImportError:  # Existing QC also supports direct script invocation.
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import hea_force_audit as force
    import hea_numerical_guard as guard
    import hea_followup_qc as qc

SCHEMA = "hea-numerical-readout-v1"
SOURCE_DIR = "runs/hea/controls_2026-09-07"
EXPECTED = {
    "hn__leader_builder__atomic__tight": ("builder", "atomic", "fragment", "tight"),
    "hn__leader_pull2.10__atomic__tight": ("pull2.10", "atomic", "fragment", "tight"),
    "hn__leader_builder__ortho__tight": ("builder", "ortho", "fragment", "tight"),
    "hn__leader_pull2.10__ortho__tight": ("pull2.10", "ortho", "fragment", "tight"),
    "hn__leader_pull2.10__ortho__recover_baseline": ("pull2.10", "ortho", "baseline", "recovery"),
    "hn__leader_builder__ortho__recover_metal_alternating": ("builder", "ortho", "metal_alternating", "recovery"),
}


def evidence(path):
    return dict(path=str(path), sha256_bytes=hashlib.sha256(path.read_bytes()).hexdigest())


def qc_consistent(stored, actual, path=()):
    """Exact raw hashes/parsed values; <=4 ULP only for derived force norms.

    Python/libm versions can round math.hypot differently. This accommodates
    serialization/runtime roundoff, never a scientific accuracy tolerance.
    """
    if isinstance(actual, dict):
        if not isinstance(stored, dict) or set(stored) != set(actual):
            return False
        return all(key == "path" or qc_consistent(stored[key], value, path+(key,))
                   for key, value in actual.items())
    if isinstance(actual, list):
        return (isinstance(stored, list) and len(stored) == len(actual)
                and all(qc_consistent(a, b, path+(i,)) for i, (a, b) in enumerate(zip(stored, actual))))
    norm = ((len(path) == 2 and path[0] == "scf" and path[1] in ("fmax_all_ev_A", "fmax_free_ev_A"))
            or (len(path) == 4 and path[:2] == ("scf", "per_atom")
                and path[3] in ("norm_all_ev_A", "norm_free_ev_A")))
    if norm and type(stored) in (int, float) and type(actual) in (int, float):
        return (math.isfinite(stored) and math.isfinite(actual)
                and abs(stored-actual) <= 4*max(math.ulp(stored), math.ulp(actual)))
    return type(stored) is type(actual) and stored == actual


def _omit_assignments(text, fields):
    pattern = re.compile(r"^\s*(?:" + "|".join(map(re.escape, fields)) + r")\s*=", re.I)
    return [line.strip() for line in text.splitlines() if line.strip() and not pattern.match(line)]


def validate_lineage(source, target, job):
    """Only the declared scalar/startup changes; all physical cards remain identical."""
    guard.validate_deck(target.encode("utf-8"), job)
    for key, expected in (("conv_thr", 1e-6), ("mixing_beta", 0.3),
                          ("electron_maxstep", 300), ("max_seconds", 13200)):
        if force.number(guard._assignment(source, key)) != expected:
            raise ValueError("unexpected source " + key)
    if guard._assignment(source, "prefix") != "'" + job["prefix"] + "'":
        raise ValueError("source prefix mismatch")
    if guard._assignment(target, "outdir") != "'./tmp_" + job["job"] + "'":
        raise ValueError("target outdir mismatch")
    for key in ("restart_mode", "startingpot", "startingwfc"):
        if re.search(r"(?im)^\s*" + key + r"\s*=", source):
            raise ValueError("source has unexpected startup assignment")
    changed = ("restart_mode", "startingpot", "startingwfc", "conv_thr", "mixing_beta", "outdir")
    if _omit_assignments(source, changed) != _omit_assignments(target, changed):
        raise ValueError("undeclared source-to-target input change")
    _, projector, _, _ = EXPECTED[job["job"]]
    expected_projector = "atomic" if projector == "atomic" else "ortho-atomic"
    if re.findall(r"(?im)^HUBBARD\s*\(([^)]+)\)\s*$", target) != [expected_projector]:
        raise ValueError("projector does not match job")
    force.input_atoms(target)


def validate_runtime(prepared, runtime):
    if prepared != runtime:
        raise ValueError("runtime input differs from exact frozen prepared bytes")


def startup_evidence(text, mode):
    result = guard.validate_startup(text, mode)
    end = text.find("End of self-consistent calculation")
    marker = "The initial density is read from file"
    wave = "Starting wfcs from file" if mode == "tight" else "Starting wfcs are"
    if end < 0 or text.index(marker) > end or text.index(wave) > end:
        raise ValueError("startup marker occurs after SCF completion")
    return result


def hubbard_occupations(input_text, output_text):
    """Final printed collinear 3d occupations; excludes initial/iteration tables."""
    labels, _, _ = force.input_atoms(input_text)
    u_rows = re.findall(r"(?m)^\s*U\s+(\S+)\s+(\S+)\s*$", input_text)
    if not u_rows or any(not re.fullmatch(r"[A-Za-z0-9]+-3d", row[0]) for row in u_rows):
        raise ValueError("readout requires explicit supported 3d Hubbard manifolds")
    species = {row[0][:-3] for row in u_rows}
    expected = [i for i, label in enumerate(labels) if label in species]
    ends = list(re.finditer(r"End of self-consistent calculation", output_text))
    if len(ends) != 1:
        raise ValueError("one final SCF boundary required for Hubbard occupations")
    tail = output_text[ends[0].end():]
    headers = list(re.finditer(r"=+ HUBBARD OCCUPATIONS =+", tail))
    stop = list(re.finditer(r"Number of occupied Hubbard levels\s*=\s*(" + force.NUM + r")\s*\n", tail))
    if len(headers) != 1 or len(stop) != 1 or headers[0].end() >= stop[0].start():
        raise ValueError("missing or malformed final Hubbard occupation table")
    block = tail[headers[0].end():stop[0].start()]
    chunks = re.split(r"\s*-+ ATOM\s+(\d+) -+\s*", block)
    if chunks[0].strip() or len(chunks) != 2*len(expected)+1:
        raise ValueError("incomplete Hubbard atom table")
    atoms = []
    for index, (number, body) in zip(expected, zip(chunks[1::2], chunks[2::2])):
        if int(number) != index + 1:
            raise ValueError("missing, duplicate or reordered Hubbard atom")
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        trace = re.fullmatch(r"Tr\[ns\(\s*(\d+)\)\] \(up, down, total\)\s*=\s*(" + force.NUM + r")\s+(" + force.NUM + r")\s+(" + force.NUM + r")", lines[0]) if lines else None
        moment = re.fullmatch(r"Atomic magnetic moment for atom\s+(\d+)\s*=\s*(" + force.NUM + r")", lines[1]) if len(lines) > 1 else None
        if not trace or not moment or int(trace[1]) != index+1 or int(moment[1]) != index+1:
            raise ValueError("malformed Hubbard trace or atom moment")
        atom = dict(index=index, species=labels[index], trace_up_e=force.number(trace[2]),
                    trace_down_e=force.number(trace[3]), trace_total_e=force.number(trace[4]),
                    moment_muB=force.number(moment[2]), spins=[])
        cursor = 2
        for spin in (1, 2):
            if cursor >= len(lines) or not re.fullmatch(r"SPIN\s+" + str(spin), lines[cursor]):
                raise ValueError("incomplete Hubbard spin block")
            cursor += 1
            if cursor >= len(lines) or lines[cursor] != "eigenvalues:":
                raise ValueError("missing Hubbard eigenvalues")
            cursor += 1
            def row(position):
                if position >= len(lines):
                    raise ValueError("truncated Hubbard matrix")
                tokens = lines[position].split()
                if len(tokens) != 5:
                    raise ValueError("Hubbard 3d row requires five finite entries")
                return [force.number(token) for token in tokens]
            eigenvalues = row(cursor)
            cursor += 1
            if cursor >= len(lines) or lines[cursor] != "eigenvectors (columns):":
                raise ValueError("missing Hubbard eigenvector block")
            cursor += 1
            for offset in range(5):
                row(cursor + offset)
            cursor += 5
            if cursor >= len(lines) or lines[cursor] != "occupation matrix ns (before diag.):":
                raise ValueError("missing Hubbard occupation matrix")
            cursor += 1
            matrix = [row(cursor + offset) for offset in range(5)]
            cursor += 5
            atom["spins"].append(dict(spin=spin, eigenvalues=eigenvalues, occupation_matrix=matrix))
        if cursor != len(lines):
            raise ValueError("extra Hubbard atom data")
        atoms.append(atom)
    return dict(status="COMPLETE", atoms=atoms, total_occupied_levels=force.number(stop[0][1]),
                interpretation="Final printed Hubbard 3d traces/eigenvalues/matrices at finite print precision; distinct from Lowdin populations")


def accepted_endpoint(folder, job, prepared=None, mode=None, receipt=None):
    paths = {name: guard._path(folder, job + suffix) for name, suffix in
             (("input", ".run.in"), ("output", ".out"), ("projection", ".projwfc.out"), ("qc", ".qc.json"))}
    record = dict(job=job, status="PENDING", reasons=[], audit=None, hubbard=None,
                  files={key: evidence(path) for key, path in paths.items() if path.is_file()})
    try:
        if paths["output"].is_file():
            text = paths["output"].read_text(encoding="utf-8")
            if qc.FAILURES.search(text):
                raise ValueError("SCF failure marker in raw output")
        missing = [key for key, path in paths.items() if not path.is_file()]
        if missing:
            record["reasons"] = ["awaiting artifacts: " + ", ".join(missing)]
            return record
        runtime = paths["input"].read_bytes().decode("utf-8")
        if prepared is not None:
            validate_runtime(prepared, runtime)
        audit = qc.audit_files(paths["input"], paths["output"], paths["projection"])
        if audit["status"] != "COMPLETE":
            if "JOB DONE" not in text and not qc.FAILURES.search(text):
                record["reasons"] = ["SCF output incomplete"]
                return record
            raise ValueError("raw QC rejected: " + "; ".join(audit["reasons"]))
        stored = guard._json(paths["qc"].read_bytes())
        if not qc_consistent(stored, audit):
            raise ValueError("stored QC does not match recomputed raw scientific fields/hashes")
        if mode is not None:
            record["startup"] = startup_evidence(text, mode)
            receipt_path, expected_receipt = receipt
            if not receipt_path.is_file():
                record["reasons"] = ["awaiting checkpoint clone receipt"]
                return record
            actual = guard._json(receipt_path.read_bytes())
            if actual != expected_receipt:
                raise ValueError("checkpoint clone receipt differs from frozen source inventory")
            record["files"]["clone_receipt"] = evidence(receipt_path)
        record["hubbard"] = hubbard_occupations(runtime, text)
        record.update(status="ACCEPTED", audit=audit,
                      stored_qc_consistency="Exact raw hashes and parsed values; only derived force norms permit <=4 ULP runtime roundoff")
    except (OSError, UnicodeError, ValueError, IndexError, KeyError) as exc:
        record.update(status="REJECTED", reasons=[str(exc)], audit=None, hubbard=None)
    return record


def endpoint_difference(source, target):
    """Target minus source; same-geometry force vectors, no atomwise spin alignment."""
    left, right = source["audit"], target["audit"]
    sforce, tforce = left["scf"]["per_atom"], right["scf"]["per_atom"]
    satoms, tatoms = left["projection"]["atoms"], right["projection"]["atoms"]
    if not len(sforce) == len(tforce) == len(satoms) == len(tatoms):
        raise ValueError("atom count mismatch in paired diagnostics")
    atoms, free_norms, sum_squares, nfree = [], [], 0.0, 0
    for sf, tf, sa, ta in zip(sforce, tforce, satoms, tatoms):
        if any(sf[k] != tf[k] for k in ("index", "species", "if_pos")) or any(sa[k] != ta[k] for k in ("index", "species")):
            raise ValueError("atom identity or Cartesian free-coordinate mask mismatch")
        delta = [b-a for a, b in zip(sf["force_ev_A"], tf["force_ev_A"])]
        free = [value*mask for value, mask in zip(delta, sf["if_pos"])]
        free_norm = math.hypot(*free)
        if any(sf["if_pos"]):
            free_norms.append(free_norm)
        sum_squares += sum(v*v for v in free)
        nfree += sum(sf["if_pos"])
        orbital = {}
        if set(sa["orbital_populations"]) != set(ta["orbital_populations"]):
            raise ValueError("Lowdin channel mismatch")
        for channel, values in sa["orbital_populations"].items():
            other = ta["orbital_populations"][channel]
            if set(values) != set(other):
                raise ValueError("Lowdin orbital field mismatch")
            orbital[channel] = {key: other[key]-value for key, value in values.items()}
        atoms.append(dict(index=sf["index"], species=sf["species"], if_pos=sf["if_pos"],
                          delta_force_ev_A=delta, delta_free_force_ev_A=free,
                          delta_free_force_norm_ev_A=free_norm,
                          **{"delta_" + key: ta[key]-sa[key] for key in ("charge_e", "spin_up_e", "spin_down_e", "moment_muB")},
                          delta_lowdin_orbital_populations=orbital))
    sh, th = source["hubbard"]["atoms"], target["hubbard"]["atoms"]
    if [(x["index"], x["species"]) for x in sh] != [(x["index"], x["species"]) for x in th]:
        raise ValueError("Hubbard atom mismatch")
    hubbard = []
    for a, b in zip(sh, th):
        item = dict(index=a["index"], species=a["species"],
                    **{"delta_"+key: b[key]-a[key] for key in ("trace_up_e", "trace_down_e", "trace_total_e", "moment_muB")}, spins=[])
        for sa, ta in zip(a["spins"], b["spins"]):
            item["spins"].append(dict(spin=sa["spin"],
                delta_eigenvalues=[v-u for u, v in zip(sa["eigenvalues"], ta["eigenvalues"])],
                delta_occupation_matrix=[[v-u for u, v in zip(ar, br)] for ar, br in zip(sa["occupation_matrix"], ta["occupation_matrix"])]))
        hubbard.append(item)
    moments = {}
    for key in ("total_moment_muB", "absolute_moment_muB"):
        a, b = left["scf"][key], right["scf"][key]
        moments["delta_"+key] = None if a is None or b is None else b-a
    return dict(source_job=source["job"], target_job=target["job"],
                delta_energy_eV=right["scf"]["energy_eV"]-left["scf"]["energy_eV"],
                source_fmax_free_ev_A=left["scf"]["fmax_free_ev_A"], target_fmax_free_ev_A=right["scf"]["fmax_free_ev_A"],
                n_free_components=nfree, max_free_vector_difference_ev_A=max(free_norms, default=None),
                rms_free_component_difference_ev_A=math.sqrt(sum_squares/nfree) if nfree else None,
                atoms=atoms, hubbard_atoms=hubbard, **moments,
                interpretation="Signed target-minus-source diagnostics in the original atom, coordinate and global spin frame; no automatic basin classification")


def build_readout(root, spec_path):
    root = Path(root).resolve(strict=True)
    spec_path = Path(spec_path)
    spec = guard.validate_spec(guard._json(spec_path.read_bytes()))
    if [job["job"] for job in spec["jobs"]] != list(EXPECTED):
        raise ValueError("readout requires exact ordered six numerical jobs")
    manifest = guard._path(root, spec["manifest"])
    inventory_path = guard._path(root, spec["source_checkpoints"])
    if evidence(manifest)["sha256_bytes"] != spec["manifest_sha256"] or evidence(inventory_path)["sha256_bytes"] != spec["source_checkpoints_sha256"]:
        raise ValueError("manifest or source inventory hash mismatch")
    inventory = guard.validate_inventory(guard._json(inventory_path.read_bytes()), spec)
    expected_rows = ["{dir} {job} {suffix} {nk}".format(**job) for job in spec["jobs"]]
    if [line for line in manifest.read_text().splitlines() if line.strip() and not line.lstrip().startswith("#")] != expected_rows:
        raise ValueError("manifest rows differ from spec")
    sources, endpoints = {}, []
    for job in spec["jobs"]:
        endpoint, projector, seed, mode = EXPECTED[job["job"]]
        source_job = "hc__leader_" + endpoint + "__" + projector + "__" + seed
        if job["prefix"] != source_job or job["mode"] != mode:
            raise ValueError("job lineage/mode differs from frozen design")
        folder = guard._path(root, "runs/" + job["dir"])
        source_folder = guard._path(root, SOURCE_DIR)
        source_input = guard._path(root, SOURCE_DIR + "/" + source_job + ".run.in")
        prepared_path = guard._path(root, "runs/" + job["dir"] + "/" + job["job"] + ".in")
        prepared = prepared_path.read_bytes().decode("utf-8")
        if evidence(prepared_path)["sha256_bytes"] != job["sha256"]:
            raise ValueError("prepared input hash mismatch: " + job["job"])
        validate_lineage(source_input.read_text(encoding="utf-8"), prepared, job)
        if mode == "tight":
            sources[source_job] = accepted_endpoint(source_folder, source_job)
        else:
            # Failed SCFs are lineage only. Never extract a comparison energy from them.
            failed_output = guard._path(root, SOURCE_DIR + "/" + source_job + ".out")
            failed_audit = force.audit_files(source_input, failed_output)
            if failed_audit["status"] == "VALID_SCF":
                raise ValueError("recovery source unexpectedly has valid SCF; review lineage")
            sources[source_job] = dict(job=source_job, status="UNRESOLVED_SOURCE", reasons=failed_audit["reasons"],
                                       input=evidence(source_input), output=evidence(failed_output))
        checkpoint = inventory[source_job]
        receipt = dict(schema="hea_numerical_clone_v1", job=job["job"], prefix=source_job, mode=mode,
                       source=checkpoint["dir"], destination=job["dir"] + "/tmp_" + job["job"] + "/" + source_job + ".save",
                       source_checkpoints_sha256=spec["source_checkpoints_sha256"], files=checkpoint["files"])
        record = accepted_endpoint(folder, job["job"], prepared, mode,
                                   (folder / (job["job"] + ".clone_receipt.json"), receipt))
        record.update(source_job=source_job, endpoint=endpoint, projector=projector, mode=mode,
                      prepared_input=evidence(prepared_path), source_input=evidence(source_input))
        endpoints.append(record)
    indexed = {row["job"]: row for row in endpoints}
    paired = []
    for projector in ("atomic", "ortho"):
        targets = [indexed["hn__leader_"+endpoint+"__"+projector+"__tight"] for endpoint in ("builder", "pull2.10")]
        originals = [sources[row["source_job"]] for row in targets]
        item = dict(projector=projector, status="PENDING", source_gap_eV=None, target_gap_eV=None, delta_gap_eV=None, endpoints=[])
        if all(row["status"] == "ACCEPTED" for row in originals):
            item["source_gap_eV"] = originals[1]["audit"]["scf"]["energy_eV"]-originals[0]["audit"]["scf"]["energy_eV"]
        if all(row["status"] == "ACCEPTED" for row in originals + targets):
            item["target_gap_eV"] = targets[1]["audit"]["scf"]["energy_eV"]-targets[0]["audit"]["scf"]["energy_eV"]
            item["delta_gap_eV"] = item["target_gap_eV"]-item["source_gap_eV"]
            item["endpoints"] = [endpoint_difference(a, b) for a, b in zip(originals, targets)]
            item["status"] = "COMPLETE"
        elif any(row["status"] == "REJECTED" for row in originals + targets):
            item["status"] = "REJECTED"
        paired.append(item)
    recoveries = []
    for job, partner in (("hn__leader_pull2.10__ortho__recover_baseline", "hc__leader_builder__ortho__baseline"),
                         ("hn__leader_builder__ortho__recover_metal_alternating", "hc__leader_pull2.10__ortho__metal_alternating")):
        target = indexed[job]
        sources[partner] = accepted_endpoint(guard._path(root, SOURCE_DIR), partner)
        original = sources[partner]
        item = dict(job=job, partner_job=partner, status="PENDING", gap_pull_minus_builder_eV=None,
                    failed_source_energy_used=False,
                    interpretation="Density/Hubbard warm start, atomic+random wavefunctions, fresh mixing and beta=0.1; partner uses baseline solver. Not exact restart or mixing-only isolation.")
        if target["status"] == original["status"] == "ACCEPTED":
            gap = target["audit"]["scf"]["energy_eV"]-original["audit"]["scf"]["energy_eV"]
            item.update(status="COMPLETE", gap_pull_minus_builder_eV=gap if target["endpoint"] == "pull2.10" else -gap)
        elif "REJECTED" in (target["status"], original["status"]):
            item["status"] = "REJECTED"
        recoveries.append(item)
    counts = {status.lower(): sum(row["status"] == status for row in endpoints) for status in ("ACCEPTED", "PENDING", "REJECTED")}
    source_counts = {status.lower(): sum(row["status"] == status for row in sources.values())
                     for status in ("ACCEPTED", "PENDING", "REJECTED", "UNRESOLVED_SOURCE")}
    complete = all(row["status"] == "COMPLETE" for row in paired + recoveries)
    rejected = counts["rejected"] > 0 or source_counts["rejected"] > 0 or any(row["status"] == "REJECTED" for row in paired + recoveries)
    result = dict(schema=SCHEMA, checked_at_utc=datetime.now(timezone.utc).isoformat(),
                  status="REJECTED" if rejected else "COMPLETE" if complete else "PENDING",
                  batch_readout_complete=complete, counts=counts, source_counts=source_counts, spec=evidence(spec_path),
                  source_inventory=evidence(inventory_path), endpoints=endpoints, sources=list(sources.values()),
                  paired_tight=paired, recovery_pairs=recoveries,
                  numerical_accuracy_status="NOT_INFERRED", gap_definition="E(pull2.10)-E(builder)",
                  limitations=["Finite-setting sensitivity at this composition and geometry; no calibrated error bound or general convergence proof.",
                               "Tight runs also warm-start density, Hubbard occupations and wavefunctions; signed state diagnostics require interpretation.",
                               "Lowdin populations and Hubbard occupations are separate finite-precision diagnostics; no automatic same-basin or magnetic-ground-state claim.",
                               "Large residual forces remain valid fixed-geometry SCF diagnostics; no relaxed geometry or candidate ranking claim.",
                               "Raw file/QC/receipt consistency is checked; remote checkpoint cloning and pseudopotential identity rely on separately retained launch verification."])
    json.dumps(result, allow_nan=False)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = build_readout(args.root, args.spec)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(result, handle, indent=2, allow_nan=False)
            handle.write("\n")
    except (OSError, ValueError) as exc:
        print("REFUSE: " + str(exc))
        return 2
    print(json.dumps(dict(status=result["status"], counts=result["counts"], source_counts=result["source_counts"], batch_readout_complete=result["batch_readout_complete"])))
    return 2 if result["status"] == "REJECTED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
