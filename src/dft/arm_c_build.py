"""Build the approved S8 arm-C fixed-geometry DFT+U package; launches nothing.

Design of record: docs/research/s8-arm-c-dft-design-2026-10-07.md (Frank, 2026-10-07:
"Go ahead. Yes to each add on."). Sites come from the MACE-MPA-0 census
(results/site_census_2026-09-06): each alloy's two arm-B p10 support sites (linear p10 over
adsorbate-intact sites), plus the approved best-site add-on. Geometries are the census relaxed
slab of the site's decoration and the site's relaxed OH/O/OOH states, rendered unchanged through
hea_deck.render_deck (atomic projector, production recipe). The three Fe25 seed-2 probe decks
differ from that alloy's production slab deck in exactly one registered respect each. The
unchanged September runner src/dft/research_batch.py executes the result.

    python src/dft/arm_c_build.py            # write decks, manifests, site plan and spec
    python src/dft/arm_c_build.py --check    # rebuild in memory and compare with the files
"""
from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import hea_deck as hd  # noqa: E402
import hea_validation_plan as hp  # noqa: E402

ROOT = HERE.parents[1]
DATE = "2026-10-07"
CSV_PATH = "results/site_census_2026-09-06/readout_full/per_site.csv"
RESULTS = "results/site_census_2026-09-06/results"
RUN_DIR = "hea/arm_c_" + DATE
PACKAGE = "results/arm_c_" + DATE
MANIFEST = {"arm_c_main": "runs/m_arm_c_" + DATE + "_main.txt",
            "arm_c_probe": "runs/m_arm_c_" + DATE + "_probe.txt"}
RUNNER_FILES = ("src/dft/research_batch.py", "src/dft/projection_qc.py",
                "src/dft/hea_force_audit.py", "src/dft/hea_followup_qc.py")
STATES = ("slab", "OH", "O", "OOH")
NK = 8
SCF_SECONDS = 8100        # 126 iterations at up to 64 s each; the iteration ceiling binds first
PROJECTION_SECONDS = 600  # measured 44-56 s in the September panel
MAX_ITERATIONS = 126      # HEA-4 ceiling, unchanged
WALL_MINUTES = 150        # per array task; 64 x 150 min x 128 cores = 20,480 SU
CONCURRENCY = {"arm_c_main": 60, "arm_c_probe": 3}

# Approved scope (design doc §3 and decision of record). The builder recomputes every entry
# from the census CSV and refuses to continue if the data no longer give exactly these sites.
ALLOYS = ("Cu8Cr23Mn35Co34", "Ni31Cr29Cu5Mn35", "Fe25Co25Ni25Cr25",
          "Cu26Ni9Cr31Co33", "Cu22Fe30Co32Mn15", "Ni34Fe6Cu29Co31")
APPROVED_SUPPORTS = {
    "Cu8Cr23Mn35Co34": ((16, 2, "1/2"), (26, 1, "1/2")),
    "Ni31Cr29Cu5Mn35": ((1, 0, "3/10"), (10, 2, "7/10")),
    "Fe25Co25Ni25Cr25": ((13, 0, "1/5"), (25, 2, "4/5")),
    "Cu26Ni9Cr31Co33": ((1, 0, "4/5"), (17, 1, "1/5")),
    "Cu22Fe30Co32Mn15": ((6, 1, "3/10"), (24, 3, "7/10")),
    "Ni34Fe6Cu29Co31": ((22, 0, "3/5"), (29, 1, "2/5")),
}
# Ni31's best site s1/0 is already its lower p10 support, so the best-site add-on adds four sites.
# Ni34's best site (s13/1) was not priced and is not in scope.
APPROVED_BEST = {"Cu8Cr23Mn35Co34": (20, 2), "Ni31Cr29Cu5Mn35": (1, 0), "Fe25Co25Ni25Cr25": (2, 0),
                 "Cu26Ni9Cr31Co33": (5, 2), "Cu22Fe30Co32Mn15": (27, 3)}
# Run order: alloy by alloy, K1 alloys first; within an alloy, support sites before the best site.
ORDER = ("Cu8Cr23Mn35Co34", "Ni31Cr29Cu5Mn35", "Fe25Co25Ni25Cr25", "Cu26Ni9Cr31Co33",
         "Cu22Fe30Co32Mn15", "Ni34Fe6Cu29Co31")
PROBE_SOURCE = ("Fe25Co25Ni25Cr25", 2, 0)
# Probe variants in registered priority order; none changes the Hamiltonian.
PROBE_VARIANTS = (("ndim16", "mixing_ndim = 16"),
                  ("cg", "diagonalization = 'cg'"),
                  ("hs", "high-spin start: starting_magnetization = 1.0 on every metal"))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def census_rows(root: Path = ROOT) -> list:
    with open(root / CSV_PATH, encoding="utf-8", newline="") as handle:
        rows = [r for r in csv.DictReader(handle)
                if r["tag"] == "mpa0" and r["arm"].startswith("CENSUS")]
    return rows


def intact(rows: list, formula: str) -> list:
    """Adsorbate-intact census sites of one alloy, ascending eta (arm B's admission policy)."""
    chosen = [r for r in rows if r["formula"] == formula and r["all_states_adsorbate_intact"] == "True"]
    if len({(r["seed"], r["site_index"]) for r in chosen}) != len(chosen):
        raise ValueError("duplicate census site: " + formula)
    for r in chosen:
        if not math.isfinite(float(r["eta_V"])):
            raise ValueError("nonfinite census eta: " + formula)
    return sorted(chosen, key=lambda r: float(r["eta_V"]))


def p10_supports(rows: list, formula: str) -> dict:
    """Linear-rule p10 (numpy default) with exact interpolation weights."""
    ordered = intact(rows, formula)
    n = len(ordered)
    position = Fraction(n - 1, 10)
    lo = math.floor(position)
    frac = position - lo
    hi = lo + 1 if frac else lo
    pairs = [(ordered[lo], 1 - frac)] + ([(ordered[hi], frac)] if frac else [])
    p10 = sum(float(w) * float(r["eta_V"]) for r, w in pairs)
    return {"n": n, "p10_V": p10, "supports": pairs, "best": ordered[0]}


def selection(root: Path = ROOT) -> list:
    """Every approved site with its roles, recomputed from the census and checked against scope."""
    rows = census_rows(root)
    sites = {}
    for formula in ALLOYS:
        result = p10_supports(rows, formula)
        got = tuple((int(r["seed"]), int(r["site_index"]), str(w)) for r, w in result["supports"])
        if got != APPROVED_SUPPORTS[formula]:
            raise ValueError(f"{formula}: census supports {got} differ from the approved {APPROVED_SUPPORTS[formula]}")
        for (row, weight), slot in zip(result["supports"], ("support_lo", "support_hi")):
            key = (formula, int(row["seed"]), int(row["site_index"]))
            entry = sites.setdefault(key, {"row": row, "roles": {}})
            entry["roles"][slot] = {"weight": str(weight), "p10_V": result["p10_V"], "n_intact": result["n"]}
        best = result["best"]
        if formula in APPROVED_BEST:
            if (int(best["seed"]), int(best["site_index"])) != APPROVED_BEST[formula]:
                raise ValueError(f"{formula}: census best site differs from the approved one")
            key = (formula, int(best["seed"]), int(best["site_index"]))
            sites.setdefault(key, {"row": best, "roles": {}})["roles"]["best"] = {"n_intact": result["n"]}
    out = []
    for formula in ORDER:
        own = [(k, v) for k, v in sites.items() if k[0] == formula]
        own.sort(key=lambda kv: (0 if any(r.startswith("support") for r in kv[1]["roles"]) else 1,
                                 float(kv[1]["row"]["eta_V"])))
        for (f, seed, index), value in own:
            row = value["row"]
            out.append({"formula": f, "seed": seed, "site_index": index, "manifest": row["manifest"],
                        "site_metal": row["initial_metal"], "eta_mlip_V": float(row["eta_V"]),
                        "dG_mlip_eV": {s: float(row["dG_" + s]) for s in ("OH", "O", "OOH")},
                        "O_category": row["O_category"], "roles": value["roles"],
                        "dir": f"{RUN_DIR}/{f}__s{seed}_site{index}"})
    if len(out) != 16 or sum(len(s["roles"]) for s in out) != 17:
        # 12 support slots + 5 best slots on 16 distinct sites (Ni31's best site s1/0 is also a support)
        raise ValueError("approved scope is 16 distinct sites")
    return out


def census_geometries(site: dict, root: Path = ROOT) -> dict:
    """The decoration's relaxed slab and the site's relaxed OH/O/OOH from the census result file."""
    path = root / RESULTS / (site["manifest"] + "_result.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "screen-diagnostic-v1" or payload.get("status") != "complete":
        raise ValueError("census result is not a complete screen-diagnostic file: " + str(path))
    if payload.get("results_sha256") != hp.identity(payload["results"]):
        raise ValueError("census result content hash mismatch: " + str(path))
    records = [r for r in payload["results"] if r.get("formula") == site["formula"]]
    if len(records) != 1 or records[0].get("status") != "evaluated":
        raise ValueError("census candidate record missing or not evaluated")
    row = records[0]["row"]
    slabs = [d for d in row["decoration_records"] if d["seed"] == site["seed"]]
    hits = [s for s in row["per_site_records"] if (s["seed"], s["site_index"]) == (site["seed"], site["site_index"])]
    if len(slabs) != 1 or len(hits) != 1:
        raise ValueError("census decoration or site not unique")
    record = hits[0]
    if record["eta"] != site["eta_mlip_V"] or record["bonds"].get("site_metal") != site["site_metal"]:
        raise ValueError("census site differs from the per-site table")
    states = dict(record["relaxed_states"], slab=slabs[0]["relaxed_slab"])
    out = {}
    for state in STATES:
        geometry = hp._geometry(states[state])
        if geometry is None:
            raise ValueError(f"geometry not usable: {site['dir']} {state}")
        out[state] = geometry
    if out["slab"]["cell_A"] != out["OH"]["cell_A"] or any(out[s]["cell_A"] != out["slab"]["cell_A"] for s in STATES):
        raise ValueError("cells differ within one chain")
    if out["slab"]["symbols"] != out["O"]["symbols"][:len(out["slab"]["symbols"])]:
        raise ValueError("adsorbate structure does not extend the slab atom order")
    return {"geometries": out, "result_file": str(path.relative_to(root)).replace("\\", "/"),
            "result_sha256_lf": hp.sha256_file(path, normalize_lf=True)}


def deck(job: str, geometry: dict) -> str:
    return hd.render_deck(job, geometry["symbols"], geometry["positions_A"], geometry["cell_A"],
                          geometry["fixed_atom_indices"], "atomic")


def probe_deck(variant: str, geometry: dict) -> str:
    """The production slab deck with exactly one registered change (asserted line by line)."""
    job = "slab__atomic_" + variant
    base = deck(job, geometry).split("\n")
    lines = list(base)
    if variant == "ndim16":
        lines.insert(lines.index("  mixing_beta = 0.3") + 1, "  mixing_ndim = 16")
    elif variant == "cg":
        lines.insert(lines.index("  mixing_beta = 0.3") + 1, "  diagonalization = 'cg'")
    elif variant == "hs":
        species = hd.species_order(geometry["symbols"])
        for i, element in enumerate(species, 1):
            if element in hd.METALS:
                old = f"  starting_magnetization({i}) = {hd.ELEMENTS[element]['mag']}"
                lines[lines.index(old)] = f"  starting_magnetization({i}) = 1.0"
    else:
        raise ValueError("unknown probe variant")
    changed = [d for d in difflib.ndiff(base, lines) if d[:2] in ("- ", "+ ")]
    if variant in ("ndim16", "cg") and changed != ["+ " + lines[lines.index("  mixing_beta = 0.3") + 1]]:
        raise ValueError("probe deck differs by more than one inserted line")
    if variant == "hs" and (not changed or any("starting_magnetization" not in d for d in changed)):
        raise ValueError("high-spin probe changes more than starting magnetization")
    return "\n".join(lines)


def manifest_text(stage: str, jobs: list) -> str:
    head = ["# APPROVED 2026-10-07: docs/research/s8-arm-c-dft-design-2026-10-07.md (Frank: \"Go ahead. Yes to each add on.\")",
            "# S8 arm C fixed-geometry DFT+U single points at census structures (" + stage + "); no automatic retries.",
            "# SUBMIT WITH EXCLUDE=" + hd.EXCLUDE,
            "# NP=128 NCONC=1"]
    return "\n".join(head + [f"{j['dir']} {j['job']} .in {j['nk']}" for j in jobs]) + "\n"


def build(root: Path = ROOT) -> dict:
    """Every output path -> bytes, plus the site plan; nothing is written here."""
    sites = selection(root)
    files, main_jobs, probe_jobs, plan_sites, elements = {}, [], [], [], set()
    for site in sites:
        loaded = census_geometries(site, root)
        for state in STATES:
            elements.update(loaded["geometries"][state]["symbols"])
        entry = {k: site[k] for k in ("formula", "seed", "site_index", "manifest", "site_metal",
                                      "eta_mlip_V", "dG_mlip_eV", "O_category", "roles", "dir")}
        entry["census_result_file"] = loaded["result_file"]
        entry["census_result_sha256_lf"] = loaded["result_sha256_lf"]
        entry["states"] = {}
        for state in STATES:
            geometry = loaded["geometries"][state]
            job = state + "__atomic"
            text = deck(job, geometry)
            path = f"runs/{site['dir']}/{job}.in"
            files[path] = text.encode("utf-8")
            entry["states"][state] = {"job": job, "deck": path, "deck_sha256": sha256(files[path]),
                                      "geometry_sha256": hp.identity(geometry), "nat": len(geometry["symbols"])}
            main_jobs.append({"dir": site["dir"], "job": job, "sha256": sha256(files[path]), "nk": NK,
                              "scf_seconds": SCF_SECONDS, "projection_seconds": PROJECTION_SECONDS,
                              "max_iterations": MAX_ITERATIONS})
        plan_sites.append(entry)
        if (site["formula"], site["seed"], site["site_index"]) == PROBE_SOURCE:
            probe_dir = f"{RUN_DIR}/probe__{site['formula']}__s{site['seed']}_site{site['site_index']}"
            for variant, description in PROBE_VARIANTS:
                text = probe_deck(variant, loaded["geometries"]["slab"])
                job = "slab__atomic_" + variant
                path = f"runs/{probe_dir}/{job}.in"
                files[path] = text.encode("utf-8")
                probe_jobs.append({"dir": probe_dir, "job": job, "sha256": sha256(files[path]), "nk": NK,
                                   "scf_seconds": SCF_SECONDS, "projection_seconds": PROJECTION_SECONDS,
                                   "max_iterations": MAX_ITERATIONS, "variant": description})
    if len(main_jobs) != 64 or len(probe_jobs) != 3:
        raise ValueError("expected 64 production and 3 probe SCFs")
    files[MANIFEST["arm_c_main"]] = manifest_text("arm_c_main", main_jobs).encode("utf-8")
    files[MANIFEST["arm_c_probe"]] = manifest_text("arm_c_probe", probe_jobs).encode("utf-8")
    upfs = sorted(hd.ELEMENTS[e]["pseudo"] for e in elements)
    september = json.loads((root / "results/research_launch_2026-09-16/launch_spec.json").read_text(encoding="utf-8"))
    pseudo_md5 = {name: september["pseudo_md5"][name] for name in upfs}
    preflight = hd.preflight_upfs()
    for name, digest in pseudo_md5.items():
        if preflight.get(name, digest) != digest:
            raise ValueError("pseudopotential md5 differs between records: " + name)
    pins = {path: sha256(data) for path, data in files.items()}
    for relative in RUNNER_FILES:
        pins[relative] = sha256((root / relative).read_bytes())
    spec = {
        "schema": "research-batch-2026-09-16",
        "np": 128,
        "exclusions": hd.EXCLUDE,
        "date": DATE,
        "design": "docs/research/s8-arm-c-dft-design-2026-10-07.md",
        "decision_ref": "Frank, 2026-10-07: \"Go ahead. Yes to each add on.\"",
        "allocation": {"account": "che260157", "partition": "wholenode", "cores_per_task": 128,
                       "approved_campaign_ceiling_cpu_su": 23680,
                       "this_launch_ceiling_cpu_su": 64 * WALL_MINUTES * 128 // 60 + 3 * WALL_MINUTES * 128 // 60,
                       "reserved_for_rerun_round_cpu_su": 1920},
        "files": dict(sorted(pins.items())),
        "pseudo_md5": pseudo_md5,
        "stages": {
            "arm_c_main": {"kind": "hea", "manifest": MANIFEST["arm_c_main"], "concurrency": CONCURRENCY["arm_c_main"],
                           "wall_minutes": WALL_MINUTES, "jobs": main_jobs},
            "arm_c_probe": {"kind": "hea", "manifest": MANIFEST["arm_c_probe"], "concurrency": CONCURRENCY["arm_c_probe"],
                            "wall_minutes": WALL_MINUTES, "jobs": probe_jobs},
        },
    }
    plan = {"schema": "s8-arm-c-site-plan-v1", "date": DATE, "design": spec["design"],
            "decision_ref": spec["decision_ref"], "census_csv": CSV_PATH,
            "census_csv_sha256_lf": hp.sha256_file(root / CSV_PATH, normalize_lf=True),
            "admission": "MACE-MPA-0 census sites with all_states_adsorbate_intact; linear p10 (numpy default)",
            "sites": plan_sites,
            "probe": {"source": {"formula": PROBE_SOURCE[0], "seed": PROBE_SOURCE[1], "site_index": PROBE_SOURCE[2]},
                      "control": "the production slab__atomic of that site in arm_c_main",
                      "priority": [v for v, _ in PROBE_VARIANTS]}}
    files[PACKAGE + "/site_plan.json"] = (json.dumps(plan, indent=2) + "\n").encode("utf-8")
    files[PACKAGE + "/launch_spec.json"] = (json.dumps(spec, indent=2) + "\n").encode("utf-8")
    return files


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare a fresh build with the files on disk")
    args = parser.parse_args(argv)
    files = build()
    problems = []
    for relative, data in files.items():
        if b"\r" in data:
            raise ValueError("CR byte in " + relative)
        path = ROOT / relative
        if args.check:
            if not path.exists() or path.read_bytes() != data:
                problems.append(relative)
        elif path.exists():
            if path.read_bytes() != data:
                raise ValueError("refusing to overwrite a differing file: " + relative)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "xb") as handle:
                handle.write(data)
    print(json.dumps({"files": len(files), "mismatches": problems,
                      "spec_sha256": sha256(files[PACKAGE + "/launch_spec.json"])}, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
