"""P-BUILDER execution script: retention rates per family x adsorbate (docs/43 A9.3.5).

    python -m s2.p_builder.run_census --families rutile110 --out <path>        # non-blind arm
    python -m s2.p_builder.run_census --allow-blind --out <path>              # after the boundary commit

Order of operations, each recorded in the output:
 1. manifest.json is checked: every census input (structures/, slabs/, configs/,
    denominators.json, decision.json) and every src/s2/p_builder/*.py file by sha256, in both
    directions (a file on disk missing from the manifest also fails); for blind runs also
    p-builder.md. A file that matches only after CRLF -> LF normalisation (a Windows checkout
    under core.autocrlf) is accepted and listed as such;
 2. blind families (perovskite001, spinel001, fcc111) run only with --allow-blind AND a
    boundary (boundary_status): every boundary path -- p-builder.md, manifest.json,
    decision.json, denominators.json, every slab / config / structure file and every
    src/s2/p_builder/*.py -- is tracked; the boundary commit is the earliest commit at which
    all of them exist; none of them changed between that commit and HEAD; none has an
    uncommitted change;
 3. the slab is rebuilt from the structure file with the registered SlabGenerator arguments
    and compared with the prestate slab; the enumerator is re-run on the prestate slab and
    compared with the prestate configurations;
 4. the operational definition is applied to the prestate configurations (census.py);
 5. verdicts are read from decision.json (X, F, construction checks) under the per-adsorbate
    reading; the pooled rate over *O, *OH and *OOH is reported with no verdict.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

import numpy as np
from pymatgen.core.surface import Slab

from .census import census_family
from .decision import verdict
from .enumeration import enumerate_configs, max_config_difference, record_from_json
from .registered import (ADSORBATE_ORDER, CODE_DIR, DECISION_DOC, DOCS43, FAMILIES, FAMILY_ORDER, PRESTATE_DIR,
                         REPO)
from .slabs import generate_slabs, select_termination
from .structures import load_bulk, sha256_file

DISCLOSURE_RE = re.compile(
    r"clean slab (?P<sg>\w+), (?P<ops>\d+) ops; \*O and \*OH: (?P<k>\d+) of (?P<n>\d+) configurations retain a "
    r"mirror, (?P<p1>\d+) of (?P<n2>\d+) P1; bent \*OOH: (?P<ooh_p1>\d+) of (?P<n3>\d+) P1")

# census inputs; other files in the prestate directory (gate record, rutile re-run, tables) are outputs
CENSUS_INPUT_PREFIXES = ("structures/", "slabs/", "configs/", "denominators.json", "decision.json")
CENSUS_INPUT_DIRS = ("structures", "slabs", "configs")


class BoundaryError(RuntimeError):
    pass


def read_rutile_disclosure(docs43: Path = DOCS43) -> dict:
    """The disclosed 2026-08-15 rutile arm, parsed from docs/43 (A9.3.5)."""
    for lineno, line in enumerate(docs43.read_text(encoding="utf-8").splitlines(), start=1):
        m = DISCLOSURE_RE.search(line)
        if m:
            g = {k: (int(v) if v.isdigit() else v) for k, v in m.groupdict().items()}
            g["docs43_line"] = lineno
            return g
    raise ValueError("rutile disclosure sentence not found in docs/43")


def sha256_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _compare(path: Path, digest: str | None) -> str:
    """'exact', 'crlf' (matches after CRLF -> LF), or the failure reason."""
    if digest is None:
        return "not in manifest"
    if not path.exists():
        return "missing"
    if sha256_file(path) == digest:
        return "exact"
    if sha256_lf(path) == digest:
        return "crlf"
    return "sha256 mismatch"


def verify_manifest(prestate: Path, code_dir: Path = CODE_DIR, repo: Path = REPO, include_doc: bool = False,
                    doc: Path = DECISION_DOC) -> dict:
    man = json.loads((prestate / "manifest.json").read_text(encoding="utf-8"))
    status: dict[str, str] = {}
    inputs = {rel: d for rel, d in man["prestate_sha256"].items() if rel.startswith(CENSUS_INPUT_PREFIXES)}
    on_disk = {p.relative_to(prestate).as_posix() for d in CENSUS_INPUT_DIRS
               for p in (prestate / d).glob("*") if p.is_file()}
    for rel in sorted(set(inputs) | on_disk):
        status[f"prestate/{rel}"] = _compare(prestate / rel, inputs.get(rel))
    code_man = {Path(k).name: v for k, v in man["code_sha256"].items()}
    code_disk = {p.name for p in code_dir.glob("*.py")}
    for name in sorted(set(code_man) | code_disk):
        p = code_dir / name
        status[f"code/{name}"] = "not on disk" if name not in code_disk else _compare(p, code_man.get(name))
    verified = [[k, (inputs.get(k[len("prestate/"):]) if k.startswith("prestate/") else code_man.get(k[len("code/"):]))]
                for k in sorted(status)]
    out = dict(n_census_inputs=len(inputs), n_code_files=len(code_man))
    if include_doc:
        key = doc.resolve().relative_to(repo.resolve()).as_posix()
        status[f"doc/{key}"] = _compare(doc, man["inputs_sha256"].get(key))
    out.update(
        mismatches={k: v for k, v in status.items() if v not in ("exact", "crlf")},
        matched_after_crlf_normalisation=sorted(k for k, v in status.items() if v == "crlf"),
        decision_doc_checked=include_doc,
        verified_set_sha256=hashlib.sha256(json.dumps(verified).encode("utf-8")).hexdigest(),
    )
    return out


def boundary_paths(prestate: Path, code_dir: Path = CODE_DIR, doc: Path = DECISION_DOC) -> list[Path]:
    paths = [doc, prestate / "manifest.json", prestate / "decision.json", prestate / "denominators.json"]
    if (prestate / ".gitattributes").exists():
        paths.append(prestate / ".gitattributes")
    for d in CENSUS_INPUT_DIRS:
        paths += sorted(p for p in (prestate / d).glob("*") if p.is_file())
    paths += sorted(code_dir.glob("*.py"))
    return paths


def boundary_status(prestate: Path = PRESTATE_DIR, repo: Path = REPO, code_dir: Path = CODE_DIR,
                    doc: Path = DECISION_DOC) -> dict:
    """The boundary commit: the earliest commit at which every boundary path exists, with no
    boundary path changed between it and HEAD and none changed in the working tree."""
    def git(*args):
        return subprocess.run(["git", "-c", "core.quotepath=off", "-C", str(repo), *args],
                              capture_output=True, text=True)
    root = repo.resolve()
    rels = [p.resolve().relative_to(root).as_posix() for p in boundary_paths(prestate, code_dir, doc)]
    head = git("rev-parse", "HEAD")
    if head.returncode != 0:
        return dict(ok=False, problems=["no HEAD commit"], boundary_commit=None, head=None, n_paths=len(rels))
    head = head.stdout.strip()
    problems = []
    tracked = set(git("ls-files", "--", *rels).stdout.splitlines())
    problems += [f"untracked: {r}" for r in rels if r not in tracked]
    first_add: dict[str, str] = {}
    for block in git("log", "--diff-filter=A", "--format=%x00%H", "--name-only", "--", *rels).stdout.split("\0"):
        lines = [l for l in block.splitlines() if l.strip()]
        if not lines:
            continue
        for name in lines[1:]:
            first_add[name] = lines[0]  # log runs newest first: the last assignment is the earliest add
    boundary = None
    candidates = sorted({first_add[r] for r in rels if r in first_add})
    if candidates and not problems:
        tops = [c for c in candidates
                if all(git("merge-base", "--is-ancestor", d, c).returncode == 0 for d in candidates)]
        if len(tops) != 1:
            problems.append("no single commit descends from every path's first-add commit")
        else:
            boundary = tops[0]
            at_boundary = set(git("ls-tree", "-r", "--name-only", boundary, "--", *rels).stdout.splitlines())
            problems += [f"not present at boundary commit: {r}" for r in rels if r not in at_boundary]
            problems += [f"changed after boundary commit: {r}"
                         for r in git("diff", "--name-only", boundary, "HEAD", "--", *rels).stdout.splitlines()]
    problems += [f"uncommitted change: {r}" for r in git("diff", "--name-only", "HEAD", "--", *rels).stdout.splitlines()]
    date = git("show", "-s", "--format=%cI", boundary).stdout.strip() if boundary else None
    return dict(ok=bool(boundary) and not problems, problems=problems, boundary_commit=boundary,
                boundary_commit_date=date, head=head, n_paths=len(rels))


def load_prestate_configs(prestate: Path, fam: str, ads: str) -> list[dict]:
    data = json.loads((prestate / "configs" / f"{fam}__{ads}.json").read_text(encoding="utf-8"))
    return [record_from_json(d) for d in data]


def reproduce_family(prestate: Path, fam: str) -> tuple[dict, dict]:
    spec = FAMILIES[fam]
    saved = Slab.from_dict(json.loads((prestate / "slabs" / f"{fam}.json").read_text(encoding="utf-8")))
    rebuilt_slabs = generate_slabs(load_bulk(fam, prestate), spec["miller"])
    _, rebuilt = select_termination(rebuilt_slabs, spec["termination"])
    same_species = [s.species_string for s in rebuilt] == [s.species_string for s in saved]
    slab_diff = float(np.abs(rebuilt.cart_coords - saved.cart_coords).max()) if same_species and \
        len(rebuilt) == len(saved) else float("inf")
    configs, enum_diff = {}, {}
    for ads in ADSORBATE_ORDER:
        configs[ads] = load_prestate_configs(prestate, fam, ads)
        enum_diff[ads] = max_config_difference(enumerate_configs(saved, ads), configs[ads])
    check = dict(slab_rebuild_max_abs_diff_A=slab_diff, enumerator_rerun_max_abs_diff_A=enum_diff,
                 reproducible=bool(slab_diff < 1e-6 and all(v < 1e-6 for v in enum_diff.values())))
    return check, configs


def pooled_rate(res: dict) -> dict:
    k = sum(res[a]["retained"] for a in ADSORBATE_ORDER)
    n = sum(res[a]["n_configurations"] for a in ADSORBATE_ORDER)
    return dict(retained=k, n_configurations=n, fraction=f"{k}/{n}", rate=(float(Fraction(k, n)) if n else None),
                verdict=None, note="pooled over *O, *OH, *OOH; reported with no verdict (decision.json reading)")


def run(families, prestate: Path = PRESTATE_DIR, allow_blind: bool = False, boundary_fn=boundary_status,
        code_dir: Path = CODE_DIR) -> dict:
    families = list(families)
    unknown = [f for f in families if f not in FAMILIES]
    if unknown:
        raise ValueError(f"unknown families {unknown}")
    blind = [f for f in families if FAMILIES[f]["blind"]]
    boundary = None
    if blind:
        if not allow_blind:
            raise BoundaryError(f"blind families {blind} need --allow-blind after the boundary commit")
        boundary = boundary_fn(prestate)
        if not boundary["ok"]:
            raise BoundaryError(f"boundary not established: {boundary}")
    man = verify_manifest(prestate, code_dir=code_dir, include_doc=bool(blind))
    if man["mismatches"]:
        raise RuntimeError(f"prestate or code does not match manifest: {man['mismatches']}")
    decision = json.loads((prestate / "decision.json").read_text(encoding="utf-8"))
    denominators = json.loads((prestate / "denominators.json").read_text(encoding="utf-8"))
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    out = dict(generated_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               head=head, boundary=boundary, manifest_check=man, reading=decision["reading"],
               decision_sha256=sha256_file(prestate / "decision.json"),
               denominators_sha256=sha256_file(prestate / "denominators.json"), families={})
    for fam in families:
        check, configs = reproduce_family(prestate, fam)
        res = census_family(configs)
        dec = decision["families"][fam]
        n_expected = denominators["families"][fam]["adsorbates"]
        counts_ok = all(res[a]["n_configurations"] == n_expected[a]["n_configurations"] for a in ADSORBATE_ORDER)
        o_eq_oh = [x["retained"] for x in res["O"]["configurations"]] == \
            [x["retained"] for x in res["OH"]["configurations"]]
        ooh_zero = res["OOH"]["retained"] == 0
        void = [] if (counts_ok and o_eq_oh and ooh_zero and check["reproducible"]) else \
            [name for name, ok in [("denominator mismatch", counts_ok), ("O != OH", o_eq_oh),
                                   ("OOH retained != 0", ooh_zero), ("not reproducible", check["reproducible"])]
             if not ok]
        verdicts = {}
        for ads in ("O", "OH"):
            v = verdict(res[ads]["retained"], res[ads]["n_configurations"], dec["X"]["HELD_if_retained_at_least"])
            verdicts[ads] = "VOID" if void else v
        fam_out = dict(label=FAMILIES[fam]["label"], blind=FAMILIES[fam]["blind"], reproduction=check,
                       construction_checks=dict(denominators_match=counts_ok, O_equals_OH=o_eq_oh,
                                                OOH_zero=ooh_zero, void_reasons=void),
                       X=dec["X"], FALSIFIED_if_retained_at_most=dec["FALSIFIED_if_retained_at_most"],
                       verdicts=verdicts, pooled_all_adsorbates=pooled_rate(res), census=res)
        if fam == "rutile110":
            disc = read_rutile_disclosure()
            clean_sg = denominators["families"][fam]["clean_slab_symmetry"]
            fam_out["disclosure_2026_08_15"] = disc
            fam_out["reproduces_disclosure"] = bool(
                clean_sg["space_group_symbol"] == disc["sg"] and clean_sg["n_operations"] == disc["ops"]
                and res["O"]["n_configurations"] == disc["n"] and res["O"]["retained"] == disc["k"]
                and res["O"]["n_space_group_P1"] == disc["p1"] and res["OH"]["retained"] == disc["k"]
                and res["OOH"]["n_space_group_P1"] == disc["ooh_p1"] and res["OOH"]["n_configurations"] == disc["n3"])
        out["families"][fam] = fam_out
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--families", nargs="+", default=list(FAMILY_ORDER))
    ap.add_argument("--prestate", type=Path, default=PRESTATE_DIR)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--allow-blind", action="store_true")
    args = ap.parse_args(argv)
    try:
        res = run(args.families, args.prestate, args.allow_blind)
    except BoundaryError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 3
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1)
        fh.write("\n")
    for fam, r in res["families"].items():
        print(fam, {a: f"{r['census'][a]['retained']}/{r['census'][a]['n_configurations']}" for a in ADSORBATE_ORDER},
              r["verdicts"], r["construction_checks"]["void_reasons"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
