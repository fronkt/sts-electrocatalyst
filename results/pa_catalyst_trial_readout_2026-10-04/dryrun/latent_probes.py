"""Zero-SU offline latent-mismatch probes against the real mirrored control output.

(1) static audit: every XML tag / attribute name the frozen adapter requires (AST walk), checked against the
    tag/attribute names present in the real QE 7.5 control XML, per section (input / step / output);
(2) dynamic audit: every lookup the patched copy actually makes on the real XML through _one;
(3) later-stage readers run on the real control files where the format allows it: read_bfgs on the real
    .bfgs, compare_trajectories on the real evaluations, _xml_evaluation on the real <output> node
    (the node type the fresh arm would use);
(4) real-tiny-run and unit-test fixture coverage of a Hubbard deck.

Read-only; the only file written is the new JSON named on the command line.
Usage: python -B latent_probes.py OUT.json
"""
import ast
import importlib.util
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SCRATCH = HERE / "scratch"
REPO = HERE.parents[2]
MIRROR = HERE.parent / "mirror" / "trial_results"
ARM = MIRROR / "control"
PREFIX = "slab_c5low__pa_boundary"
XML = ARM / "outdir" / (PREFIX + ".save") / "data-file-schema.xml"
FROZEN = REPO / "src" / "dft" / "pa_qe_adapter.py"
SPEC = json.loads((REPO / "results/pa_catalyst_trial_2026-10-03/launch_spec.json").read_text(encoding="utf-8"))
SOURCE_DECK = REPO / "runs/hea/lowtail_low_state_restart_2026-09-22/Cu8Cr23Mn35Co34__s20_site2/slab_c5low__relax.in"
TINY = REPO / "results/s2_2026-09-25/full_text/sequential_2026-10-03/pa_tiny_raw/tiny_results"
TESTS = REPO / "tests" / "test_pa_qe_adapter.py"

sys.path.insert(0, str(SCRATCH))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


patched = load("pa_qe_adapter_patched", SCRATCH / "pa_qe_adapter.py")


def local(tag):
    return tag.rsplit("}", 1)[-1]


def section_index(root):
    """tag -> set of top-level sections (input/step/output/other) in which an element of that name occurs;
    attribute name -> set of tags carrying it."""
    tags, attrs = {}, {}
    for top in root:
        sec = local(top.tag)
        for node in top.iter():
            name = local(node.tag)
            tags.setdefault(name, set()).add(sec)
            for key in node.attrib:
                attrs.setdefault(key, set()).add(name)
    return tags, attrs


def static_requirements(path):
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = func.id if isinstance(func, ast.Name) else (func.attr if isinstance(func, ast.Attribute) else None)
            if name in ("_one", "value") and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str):
                found.append({"line": node.lineno, "kind": "required_child_tag", "via": name, "name": node.args[1].value})
            elif name == "_xml_source_ranges" and len(node.args) >= 3 and isinstance(node.args[2], ast.Constant):
                found.append({"line": node.lineno, "kind": "source_range_tag", "via": name, "name": node.args[2].value})
            elif name == "get" and isinstance(func, ast.Attribute) and isinstance(func.value, ast.Attribute) and func.value.attr == "attrib" \
                    and node.args and isinstance(node.args[0], ast.Constant):
                found.append({"line": node.lineno, "kind": "attribute", "via": "attrib.get", "name": node.args[0].value})
    # tag names compared in iteration loops: _tag(x) == "name" / tag == "name" / name in {..}
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) and isinstance(node.left, (ast.Call, ast.Name)):
            left = node.left
            lname = (left.func.id if isinstance(left, ast.Call) and isinstance(left.func, ast.Name) else getattr(left, "id", None))
            if lname in ("_tag", "tag", "name") and node.comparators:
                comp = node.comparators[0]
                if isinstance(comp, ast.Constant) and isinstance(comp.value, str):
                    found.append({"line": node.lineno, "kind": "tag_compare", "via": lname, "name": comp.value})
                elif isinstance(comp, ast.Set):
                    for elt in comp.elts:
                        if isinstance(elt, ast.Constant):
                            found.append({"line": node.lineno, "kind": "tag_compare", "via": lname, "name": elt.value})
    return found


def main(out):
    root = ET.parse(str(XML)).getroot()
    tags, attrs = section_index(root)
    result = {"control_xml": str(XML.relative_to(REPO)), "adapter_audited": str(FROZEN.relative_to(REPO))}

    # (1) static audit
    rows = []
    for item in static_requirements(FROZEN):
        name = item["name"]
        if item["kind"] == "attribute":
            holders = sorted(attrs.get(name, []))
            rows.append({**item, "present_in_real_xml": bool(holders), "carried_by_tags": holders})
        else:
            secs = sorted(tags.get(name, []))
            rows.append({**item, "present_in_real_xml": bool(secs), "sections": secs})
    rows.sort(key=lambda r: (r["line"], r["name"]))
    result["static_audit"] = rows
    result["static_required_but_absent_from_real_xml"] = [r for r in rows if not r["present_in_real_xml"]]
    result["static_counts"] = {"rows": len(rows), "absent": len(result["static_required_but_absent_from_real_xml"])}

    # (2) dynamic audit through the patched copy (frozen behaviour except the one removed requirement)
    log = []
    original = patched._one

    def traced(node, name):
        values = [v for v in node if patched._tag(v) == name]
        log.append({"parent": patched._tag(node), "wanted": name, "found": len(values)})
        return original(node, name)
    patched._one = traced
    expected = patched.parse_deck(SOURCE_DECK, SPEC["source_deck"]["sha256"])
    deck = patched.parse_deck(ARM / "input.in")
    try:
        identity = patched._check_xml_input(root, deck)
        result["dynamic_check_xml_input"] = {"ok": True, "xml_identity": identity}
    except Exception as exc:
        result["dynamic_check_xml_input"] = {"ok": False, "error": "%s: %s" % (type(exc).__name__, exc)}
    patched._one = original
    seen = {}
    for entry in log:
        key = (entry["parent"], entry["wanted"])
        seen.setdefault(key, set()).add(entry["found"])
    result["dynamic_lookups"] = [{"parent": k[0], "wanted": k[1], "found_counts": sorted(v)} for k, v in sorted(seen.items())]
    result["dynamic_lookups_not_exactly_one"] = [r for r in result["dynamic_lookups"] if r["found_counts"] != [1]]

    # Hubbard comparison table (XML vs source card), independent of the adapter's own arithmetic path
    dft_in = next(c for c in next(c for c in root if local(c.tag) == "input") if local(c.tag) == "dft")
    dftu = next(c for c in dft_in if local(c.tag) == "dftU")
    ry_ev = patched.RY_EV
    xml_u = {(c.attrib["specie"], c.attrib["label"]): float(c.text) * 2 * ry_ev for c in dftu if local(c.tag) == "Hubbard_U"}
    card = deck["settings"]["hubbard"]
    src_u = {(r[1].rsplit("-", 1)[0], r[1].rsplit("-", 1)[1]): float(r[2]) for r in card["rows"]}
    result["hubbard"] = {
        "dftU_children_in_real_input_xml": [local(c.tag) for c in dftU_children(dftu)],
        "dftU_attributes": dict(dftu.attrib), "source_card_unit": card["unit"],
        "xml_U_projection_type": next(c.text for c in dftu if local(c.tag) == "U_projection_type"),
        "xml_lda_plus_u_kind": next(c.text for c in dftu if local(c.tag) == "lda_plus_u_kind"),
        "xml_Hubbard_U_eV": {"%s-%s" % k: v for k, v in xml_u.items()},
        "source_Hubbard_U_eV": {"%s-%s" % k: v for k, v in src_u.items()},
        "max_abs_difference_eV": max(abs(xml_u[k] - src_u[k]) for k in src_u),
        "keys_equal": set(xml_u) == set(src_u),
        "lda_plus_u_element_count_in_real_xml": sum(1 for n in root.iter() if local(n.tag) == "lda_plus_u")}

    # (3) later-stage readers on real control files
    probes = []

    def probe(name, fn):
        try:
            probes.append({"probe": name, "result": "PASS", "value": fn()})
        except Exception as exc:
            probes.append({"probe": name, "result": "FAIL", "error": "%s: %s" % (type(exc).__name__, exc)})
    process = json.loads((ARM / "process_receipt.json").read_text(encoding="utf-8"))
    mapping = {}
    stdout = (ARM / "stdout.log").read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r"PseudoPot\.\s*#\s*\d+\s+for\s+\S+\s+read from file:[ \t]*\n?[ \t]*([^\r\n]+)", stdout):
        mapping[m.group(1).strip()] = str(MIRROR / "common_pseudo" / Path(m.group(1).strip()).name)
    expected["upf_pins"] = {Path(p["path"]).name: p["sha256"] for p in SPEC["upfs"]}
    expected["upf_read_path_map"] = mapping
    shape = {"nprocs": 128, "nthreads": 1, "ntasks": 1, "nbgrp": 1, "npool": 8, "ndiag": 16}
    arm = patched.read_qe_arm(ARM / "input.in", ARM / "stdout.log", ARM / "stderr.log", XML, process,
                              expected_settings=expected, expected_parallel=shape, expected_exit="clean_stop",
                              expected_evaluations=3)
    last = arm["evaluations"][-1]

    def bfgs_probe():
        saved = patched.read_bfgs(ARM / "outdir" / (PREFIX + ".bfgs"), nat=72, cell_bohr=last["geometry"]["cell"], evaluated=last)
        return {k: saved[k] for k in ("scf_count", "bfgs_count", "gdiis_count", "dimension", "tr_min_hit", "nr_step_length_bohr",
                                       "inactive_tail_max_abs", "prior_energy_Ry")}
    probe("read_bfgs on the real control .bfgs against the third evaluated step (candidate-stage reader)", bfgs_probe)

    def bfgs_unbound():
        saved = patched.read_bfgs(ARM / "outdir" / (PREFIX + ".bfgs"), nat=72, cell_bohr=last["geometry"]["cell"], evaluated=None)
        return {"scf_count": saved["scf_count"], "bfgs_count": saved["bfgs_count"], "prior_energy_Ry": saved["prior_energy_Ry"],
                "third_evaluated_energy_Ry": last["energy_Ry"]}
    probe("read_bfgs structure/dimension only (no evaluated correspondence)", bfgs_unbound)

    def self_compare():
        c = patched.compare_trajectories(arm["evaluations"], arm["evaluations"])
        return {"evaluations": c["evaluations"], "within_tolerances": c["within_tolerances"]}
    probe("compare_trajectories on the real control evaluations vs themselves (reader sanity only)", self_compare)

    def output_eval():
        node = next(c for c in root if local(c.tag) == "output")
        return patched._xml_evaluation(node, deck, {"path": "x", "sha256": "0", "line_start": 1, "line_end": 1})
    probe("_xml_evaluation on the real <output> node of the relax stop (fresh-arm node type)", output_eval)
    out_children = [local(c.tag) for c in next(c for c in root if local(c.tag) == "output")]
    result["real_control_output_children"] = out_children
    result["real_control_step_children"] = [local(c.tag) for c in next(c for c in root if local(c.tag) == "step")]
    result["probes"] = probes

    # (4) Hubbard coverage in real tiny-run files and unit-test fixtures
    tiny_hits = []
    for path in sorted(TINY.rglob("*")):
        if path.is_file() and path.stat().st_size < 5_000_000 and path.suffix not in (".hdf5", ".wfc1"):
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if re.search(r"HUBBARD|<dftU|lda_plus_u|Hubbard_U", text):
                tiny_hits.append(str(path.relative_to(TINY)))
    tests_text = TESTS.read_text(encoding="utf-8").splitlines()
    result["hubbard_coverage"] = {
        "tiny_run_files_scanned": sum(1 for p in TINY.rglob("*") if p.is_file()),
        "tiny_run_files_with_any_hubbard_token": tiny_hits,
        "tiny_run_deck_calculation_values": sorted({m for p in TINY.rglob("input.in") for m in re.findall(r"calculation\s*=\s*'(\w+)'", p.read_text(encoding='utf-8'))}),
        "unit_test_lines_mentioning_lda_plus_u": [{"line": i + 1, "text": t.strip()[:160]} for i, t in enumerate(tests_text) if "lda_plus_u" in t],
        "unit_test_lines_with_HUBBARD_card": [{"line": i + 1, "text": t.strip()[:160]} for i, t in enumerate(tests_text) if "HUBBARD" in t],
    }
    other = []
    for path in sorted((REPO / "runs" / "a0" / "pproj6").rglob("data-file-schema.xml"))[:40]:
        text = path.read_text(encoding="utf-8", errors="ignore")
        other.append({"path": str(path.relative_to(REPO)), "has_dftU": "<dftU" in text,
                      "has_lda_plus_u_element": "<lda_plus_u>" in text,
                      "qe_version": (re.search(r'<creator NAME="PWSCF" VERSION="([^"]+)"', text) or [None, None])[1]})
    result["other_real_qe_hubbard_xml_in_repo"] = other
    with open(out, "x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: result[k] for k in ("static_counts", "dynamic_check_xml_input")}, indent=1, default=str)[:1500])
    print("static required but absent:", [(r["line"], r["kind"], r["name"]) for r in result["static_required_but_absent_from_real_xml"]])
    print("dynamic lookups not exactly one:", result["dynamic_lookups_not_exactly_one"])
    print("hubbard:", json.dumps(result["hubbard"], default=str)[:1200])
    for p in probes:
        print(p["result"], "|", p["probe"], "|", str(p.get("value") or p.get("error"))[:300])
    print("tiny hubbard hits:", tiny_hits, "| tiny calc:", result["hubbard_coverage"]["tiny_run_deck_calculation_values"])
    print("other real hubbard xml:", [(o["path"].replace(chr(92), "/").split("pproj6/")[1], o["has_dftU"], o["has_lda_plus_u_element"], o["qe_version"]) for o in other][:6], len(other))
    return 0


def dftU_children(node):
    return list(node)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
