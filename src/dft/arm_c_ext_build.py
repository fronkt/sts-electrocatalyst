"""Build the S8 arm-C extension: seeded SCFs for the states still missing at Cu8's and Fe25's
support sites; launches nothing.

Decision of record: Frank, 2026-10-08, "Let's rerun DFT for those and get values for them." The
extension is exploratory (freeze proposal §4b): arm C's registered readings stay final.

Recipe (docs/research/s8-arm-c-extension-2026-10-08.md): the production deck (geometry, PBE+U,
cutoffs, smearing, local-TF mixing at beta 0.3, conv_thr 1e-6) with its own prefix and one added
line, startingpot = 'file'. The starting density is the retained, converged density of the accepted
state at the same site with the fewest differing atoms. Its DFT+U occupations (occup.txt) and PAW
becsum (paw.txt) are rebuilt for the target's atom list: the 72 slab atoms in their common order
keep the seed's blocks; an adsorbate atom keeps the seed's block for the same role, a second O takes
the seed's first adsorbate O, a new adsorbate O takes the nearest slab O (minimum image in the
surface plane), and a new H starts from zero. The seeded runner (research_batch_seeded.py) copies
the density, its XML and these two files into the job's fresh scratch. A two-task canary (eight
iterations) checks that QE reads a rebuilt seed before the eleven-task main array is released.

    python src/dft/arm_c_ext_build.py            # write decks, seed files, manifests, plan and spec
    python src/dft/arm_c_ext_build.py --check    # rebuild in memory and compare with the files
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arm_c_build as cb  # noqa: E402
import hea_deck as hd  # noqa: E402

ROOT = HERE.parents[1]
DATE = "2026-10-08"
PACKAGE = "results/arm_c_ext_" + DATE
RUN_ROOT = "hea/arm_c_ext_" + DATE
CANARY_ROOT = RUN_ROOT + "/canary"
PRODUCTION_ROOT = "hea/arm_c_" + cb.DATE
RERUN_ROOT = "hea/arm_c_" + cb.DATE + "_rerun"
READOUT = "results/arm_c_" + cb.DATE + "_rerun/readout.json"
SOURCE_SPEC = "results/arm_c_" + cb.DATE + "/launch_spec.json"
RERUN_SPEC = "results/arm_c_" + cb.DATE + "_rerun/launch_spec.json"
RERUN_COLLECTION = "results/arm_c_" + cb.DATE + "_rerun/terminal_collection.json"
FETCH = PACKAGE + "/seed_fetch.json"
MANIFEST = {"ext_canary": "runs/m_arm_c_ext_" + DATE + "_canary.txt",
            "ext_main": "runs/m_arm_c_ext_" + DATE + "_main.txt"}
DECISION = "Frank, 2026-10-08: \"Let's rerun DFT for those and get values for them.\""
ALLOYS = ("Cu8Cr23Mn35Co34", "Fe25Co25Ni25Cr25")
RUNNER_FILES = ("src/dft/research_batch_seeded.py", "src/dft/projection_qc.py",
                "src/dft/hea_force_audit.py", "src/dft/hea_followup_qc.py")
SHARED_HELPERS = RUNNER_FILES[1:]
JOB_SUFFIX = "__atomic_seeded"
SLAB_ATOMS = 72
ROLES = {"slab": (), "O": ("O1",), "OH": ("O1", "H"), "OOH": ("O1", "O2", "H")}
NS_BLOCK = 50          # occup.txt: ns(5, 5, nspin=2, nat), one block per atom
BEC_BLOCK = 171        # paw.txt: becsum(18*19/2, nat, nspin=2)
LIMITS = {"ext_canary": {"max_iterations": 8, "scf_seconds": 1200, "projection_seconds": 600, "wall_minutes": 25},
          "ext_main": {"max_iterations": 200, "scf_seconds": 12600, "projection_seconds": 600, "wall_minutes": 225}}
CANARY = (("Cu8Cr23Mn35Co34__s16_site2", "slab"),     # seed with one more atom (O state)
          ("Fe25Co25Ni25Cr25__s13_site0", "OOH"))     # seed with three fewer atoms (slab)
EXPECTED_TARGETS = 11


def site_name(site_dir: str) -> str:
    return site_dir.rsplit("/", 1)[-1]


def nat_of(state: str) -> int:
    return SLAB_ATOMS + len(ROLES[state])


def targets(readout: dict) -> list:
    """States still failed after the re-run round at the Cu8 and Fe25 support sites, with seeds."""
    out = []
    for site in readout["sites"]:
        if site["formula"] not in ALLOYS or not {"support_lo", "support_hi"} & set(site["roles"]):
            continue
        accepted = {s: row for s, row in site["states"].items() if row["accepted"]}
        for state in ("slab", "OH", "O", "OOH"):
            if state in accepted:
                continue
            distance = {s: abs(nat_of(s) - nat_of(state)) for s in accepted}
            best = min(distance.values())
            nearest = sorted(s for s, d in distance.items() if d == best)
            if len(nearest) != 1:
                raise ValueError("seed tie at " + site["dir"] + " " + state + ": " + repr(nearest))
            seed_state = nearest[0]
            row = accepted[seed_state]
            from_rerun = "replaces" in row
            out.append({"site_dir": site["dir"], "formula": site["formula"], "state": state,
                        "failure": site["failures"][state],
                        "dir": f"{RUN_ROOT}/{site_name(site['dir'])}", "job": state + JOB_SUFFIX,
                        "seed": {"state": seed_state, "job": row["job"], "recipe": row["recipe"],
                                 "root": RERUN_ROOT if from_rerun else PRODUCTION_ROOT,
                                 "id": f"{site_name(site['dir'])}__{row['job']}"}})
    if len(out) != EXPECTED_TARGETS:
        raise ValueError(f"expected {EXPECTED_TARGETS} target states, found {len(out)}")
    return out


def seeded_deck(text: str, job: str) -> str:
    """The production deck with its own prefix and one added line, startingpot = 'file'."""
    lines = text.split("\n")
    prefixes = [i for i, line in enumerate(lines) if line.startswith("  prefix = '")]
    anchors = [i for i, line in enumerate(lines) if line == "  electron_maxstep = 300"]
    if len(prefixes) != 1 or len(anchors) != 1 or any("startingpot" in line for line in lines):
        raise ValueError("deck lacks a unique prefix/electron_maxstep line or already sets startingpot")
    lines[prefixes[0]] = f"  prefix = '{job}'"
    lines.insert(anchors[0] + 1, "  startingpot = 'file'")
    return "\n".join(lines)


def numbers(text: str) -> list:
    return [float(token.replace("D", "E").replace("d", "e")) for token in text.split()]


def render(values: list) -> bytes:
    return ("\n".join(repr(v) for v in values) + "\n").encode("ascii")


def geometry(text: str) -> tuple:
    """Cell (3 rows) and positions [(species, (x, y, z))] of a deck, in angstrom."""
    lines = text.split("\n")
    c = lines.index("CELL_PARAMETERS angstrom")
    cell = [[float(x) for x in lines[c + k].split()] for k in (1, 2, 3)]
    p = lines.index("ATOMIC_POSITIONS angstrom")
    atoms = []
    for line in lines[p + 1:]:
        parts = line.split()
        if len(parts) < 4 or parts[0] in ("K_POINTS", "HUBBARD"):
            break
        atoms.append((parts[0], tuple(float(x) for x in parts[1:4])))
    return cell, atoms


def in_plane_distance(cell: list, a: tuple, b: tuple) -> float:
    """Minimum-image distance with periodicity along the first two cell vectors."""
    (a1, a2, a3), (b1, b2, b3), (c1, c2, c3) = cell
    det = a1 * (b2 * c3 - b3 * c2) - a2 * (b1 * c3 - b3 * c1) + a3 * (b1 * c2 - b2 * c1)
    inv = [[(b2 * c3 - b3 * c2) / det, (a3 * c2 - a2 * c3) / det, (a2 * b3 - a3 * b2) / det],
           [(b3 * c1 - b1 * c3) / det, (a1 * c3 - a3 * c1) / det, (a3 * b1 - a1 * b3) / det],
           [(b1 * c2 - b2 * c1) / det, (a2 * c1 - a1 * c2) / det, (a1 * b2 - a2 * b1) / det]]
    d = [b[k] - a[k] for k in range(3)]
    f = [sum(d[r] * inv[r][k] for r in range(3)) for k in range(3)]
    f = [f[0] - round(f[0]), f[1] - round(f[1]), f[2]]
    return math.sqrt(sum(sum(f[r] * cell[r][k] for r in range(3)) ** 2 for k in range(3)))


def atom_sources(target_state: str, seed_state: str, deck_text: str) -> list:
    """Seed atom index (0-based) per target atom, None for a zero start, and how it was chosen."""
    cell, atoms = geometry(deck_text)
    if len(atoms) != nat_of(target_state):
        raise ValueError("deck atom count differs from the state's")
    slab_o = [i for i in range(SLAB_ATOMS) if atoms[i][0] == "O"]
    seed_roles = {role: SLAB_ATOMS + k for k, role in enumerate(ROLES[seed_state])}
    sources = [(i, "slab") for i in range(SLAB_ATOMS)]
    for k, role in enumerate(ROLES[target_state]):
        if role in seed_roles:
            sources.append((seed_roles[role], "seed " + role))
        elif role == "O2" and "O1" in seed_roles:
            sources.append((seed_roles["O1"], "seed O1"))
        elif role in ("O1", "O2"):
            position = atoms[SLAB_ATOMS + k][1]
            nearest = min(slab_o, key=lambda i: (in_plane_distance(cell, position, atoms[i][1]), i))
            sources.append((nearest, f"nearest slab O (atom {nearest + 1})"))
        else:
            sources.append((None, "zero"))
    return sources


def rebuilt_files(seed_occup: str, seed_paw: str, seed_state: str, sources: list) -> dict:
    """occup.txt and paw.txt for the target atom list from the seed's arrays."""
    nat_seed, nat_target = nat_of(seed_state), len(sources)
    ns, bec = numbers(seed_occup), numbers(seed_paw)
    if len(ns) != NS_BLOCK * nat_seed or len(bec) != BEC_BLOCK * nat_seed * 2:
        raise ValueError("seed occup/paw sizes do not match the seed's atom count")
    new_ns, new_bec = [], []
    for source, _ in sources:
        block = ns[NS_BLOCK * source:NS_BLOCK * (source + 1)] if source is not None else [0.0] * NS_BLOCK
        new_ns.extend(block)
    for spin in range(2):
        for source, _ in sources:
            if source is None:
                new_bec.extend([0.0] * BEC_BLOCK)
            else:
                start = BEC_BLOCK * (spin * nat_seed + source)
                new_bec.extend(bec[start:start + BEC_BLOCK])
    for k in range(SLAB_ATOMS, nat_target):  # adsorbate atoms carry no Hubbard U
        if any(new_ns[NS_BLOCK * k:NS_BLOCK * (k + 1)]):
            raise ValueError("nonzero Hubbard occupations on an adsorbate atom")
    return {"occup.txt": render(new_ns), "paw.txt": render(new_bec)}


def manifest_text(stage: str, jobs: list) -> str:
    head = ["# APPROVED 2026-10-08: docs/research/s8-arm-c-extension-2026-10-08.md (Frank: \"Let's rerun DFT for those and get values for them.\")",
            "# S8 arm C extension (" + stage + "): seeded fixed-geometry SCFs at the Cu8 and Fe25 support sites; exploratory; no automatic retries.",
            "# SUBMIT WITH EXCLUDE=" + hd.EXCLUDE,
            "# NP=128 NCONC=1"]
    return "\n".join(head + [f"{j['dir']} {j['job']} .in {j['nk']}" for j in jobs]) + "\n"


def spent_cpu_su(root: Path) -> float:
    """CPU SU already spent by arm C: the re-run spec's prior total plus the re-run's sacct rows."""
    rerun_spec = json.loads((root / RERUN_SPEC).read_text(encoding="utf-8"))
    collection = json.loads((root / RERUN_COLLECTION).read_text(encoding="utf-8"))
    rows = [line.split("|") for line in collection["sacct"].strip().splitlines()]
    seconds = [int(r[7]) for r in rows if "." not in r[0]]
    if len(seconds) != 33:
        raise ValueError("expected 33 accounted re-run tasks")
    return round(rerun_spec["allocation"]["spent_before_this_launch_cpu_su"] + sum(seconds) / 3600, 1)


def build(root: Path = ROOT) -> dict:
    """Every output path -> bytes; nothing is written here."""
    readout_bytes = (root / READOUT).read_bytes()
    readout = json.loads(readout_bytes)
    source_spec = json.loads((root / SOURCE_SPEC).read_text(encoding="utf-8"))
    fetch = json.loads((root / FETCH).read_text(encoding="utf-8"))
    rows = targets(readout)
    files, main_jobs, plan_rows = {}, [], []
    for row in rows:
        production = f"runs/{row['site_dir']}/{row['state']}__atomic.in"
        data = (root / production).read_bytes()
        if cb.sha256(data) != source_spec["files"][production]:
            raise ValueError("production deck differs from its launch pin: " + production)
        text = data.decode("utf-8")
        deck = seeded_deck(text, row["job"]).encode("utf-8")
        seed = row["seed"]
        fetched = fetch["seeds"][seed["id"]]
        expected_dir = f"/anvil/projects/x-che260157/sts_arm_c_{cb.DATE}{'_rerun' if seed['root'] == RERUN_ROOT else ''}/runs/{seed['root']}/{site_name(row['site_dir'])}/tmp_{seed['job']}/{seed['job']}.save"
        if fetched["save_dir"] != expected_dir:
            raise ValueError("fetched seed location differs: " + seed["id"])
        local = root / PACKAGE / "seed_files" / seed["id"]
        for name in ("occup.txt", "paw.txt"):
            if cb.sha256((local / name).read_bytes()) != fetched["sha256"][name]:
                raise ValueError("fetched seed file differs from its Anvil sha256: " + seed["id"] + "/" + name)
        sources = atom_sources(row["state"], seed["state"], text)
        bundle = f"{PACKAGE}/seeds/{site_name(row['site_dir'])}/{row['state']}"
        rebuilt = rebuilt_files((local / "occup.txt").read_text(encoding="ascii"),
                                (local / "paw.txt").read_text(encoding="ascii"), seed["state"], sources)
        for name, payload in rebuilt.items():
            files[f"{bundle}/{name}"] = payload
        files[f"runs/{row['dir']}/{row['job']}.in"] = deck
        scratch = {"save_dir": bundle,
                   "files": {"charge-density.hdf5": fetched["sha256"]["charge-density.hdf5"],
                             "data-file-schema.xml": fetched["sha256"]["data-file-schema.xml"],
                             "occup.txt": cb.sha256(rebuilt["occup.txt"]),
                             "paw.txt": cb.sha256(rebuilt["paw.txt"])}}
        main_jobs.append({"dir": row["dir"], "job": row["job"], "sha256": cb.sha256(deck), "nk": cb.NK,
                          **{k: LIMITS["ext_main"][k] for k in ("scf_seconds", "projection_seconds", "max_iterations")},
                          "recipe": "seeded", "role": "extension", "source_deck": production,
                          "seed": {"state": seed["state"], "job": seed["job"], "recipe": seed["recipe"],
                                   "save_dir": fetched["save_dir"]},
                          "scratch_source": scratch})
        plan_rows.append(dict(row, bundle=bundle, remote_copy={
            "charge-density.hdf5": fetched["save_dir"] + "/charge-density.hdf5",
            "data-file-schema.xml": fetched["save_dir"] + "/data-file-schema.xml"},
            atom_sources=[{"atom": SLAB_ATOMS + k + 1, "role": role, "from": label}
                          for k, (role, (_, label)) in enumerate(zip(ROLES[row["state"]], sources[SLAB_ATOMS:]))]))
    canary_jobs = []
    for site, state in CANARY:
        job = next(j for j in main_jobs if j["dir"].endswith("/" + site) and j["job"] == state + JOB_SUFFIX)
        canary_dir = f"{CANARY_ROOT}/{site}"
        files[f"runs/{canary_dir}/{job['job']}.in"] = files[f"runs/{job['dir']}/{job['job']}.in"]
        canary_jobs.append(dict(job, dir=canary_dir, role="canary",
                                **{k: LIMITS["ext_canary"][k] for k in ("scf_seconds", "projection_seconds", "max_iterations")}))
    stages = {}
    for stage, jobs in (("ext_canary", canary_jobs), ("ext_main", main_jobs)):
        files[MANIFEST[stage]] = manifest_text(stage, jobs).encode("utf-8")
        stages[stage] = {"kind": "hea", "manifest": MANIFEST[stage], "concurrency": len(jobs),
                         "wall_minutes": LIMITS[stage]["wall_minutes"], "jobs": jobs}
    pins = {path: cb.sha256(data) for path, data in files.items()}
    for relative in RUNNER_FILES:
        pins[relative] = cb.sha256((root / relative).read_bytes())
    for relative in SHARED_HELPERS:
        if pins[relative] != source_spec["files"][relative]:
            raise ValueError("helper changed since the production launch: " + relative)
    spent = spent_cpu_su(root)
    ceilings = {s: len(stages[s]["jobs"]) * LIMITS[s]["wall_minutes"] * 128 // 60 for s in stages}
    ceiling = sum(ceilings.values())
    campaign = source_spec["allocation"]["approved_campaign_ceiling_cpu_su"]
    if spent + ceiling > campaign:
        raise ValueError("the extension does not fit the approved arm-C campaign ceiling")
    source_readout = {"path": READOUT, "sha256": cb.sha256(readout_bytes)}
    spec = {
        "schema": "research-batch-2026-09-16",
        "np": 128,
        "exclusions": hd.EXCLUDE,
        "date": DATE,
        "design": "docs/research/s8-arm-c-extension-2026-10-08.md",
        "decision_ref": DECISION,
        "source_readout": source_readout,
        "allocation": {"account": "che260157", "partition": "wholenode", "cores_per_task": 128,
                       "approved_campaign_ceiling_cpu_su": campaign,
                       "spent_before_this_launch_cpu_su": spent,
                       "stage_ceilings_cpu_su": ceilings,
                       "this_launch_ceiling_cpu_su": ceiling},
        "qe_binaries_sha256": source_spec["qe_binaries_sha256"],
        "files": dict(sorted(pins.items())),
        "pseudo_md5": source_spec["pseudo_md5"],
        "stages": stages,
    }
    plan = {"schema": "s8-arm-c-ext-plan-v1", "date": DATE, "design": spec["design"], "decision_ref": DECISION,
            "source_readout": source_readout,
            "rule": ("every state still failed after the re-run round at a Cu8 or Fe25 support site, once, seeded from the "
                     "accepted state at the same site with the fewest differing atoms; production recipe plus startingpot = 'file'"),
            "status": "exploratory; arm C's registered readings stay final",
            "selection": plan_rows,
            "canary": [{"site": s, "state": st, "dir": f"{CANARY_ROOT}/{s}", "job": st + JOB_SUFFIX} for s, st in CANARY]}
    files[PACKAGE + "/ext_plan.json"] = (json.dumps(plan, indent=2) + "\n").encode("utf-8")
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
                      "spec_sha256": cb.sha256(files[PACKAGE + "/launch_spec.json"])}, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
