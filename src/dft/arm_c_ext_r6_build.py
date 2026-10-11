"""Build round 6 of the S8 arm-C extension: second starts of the slab and the OH at each value site where the two
states disagree away from the adsorbate, each from its own converged density with that atom's Hubbard occupations
and PAW block taken from the other state, the occupations held for the first iterations; launches nothing.

Decision of record: Frank, 2026-10-10, "Go ahead with other values", after round 5's readout. Round 5 found the Fe25
s25/2 production slab 259 meV above a slab whose Fe 22 sat in the configuration the site's OH shares, and Fe25's
value rose by that much. No other state behind an alloy's value had been started from a second configuration.

Screen. Step 1 (slab to OH) limits at all six complete sites behind the alloys' values, so the slab and the OH set
each value. At each site, every Hubbard atom more than 2.5 A from the adsorbate's O whose slab and OH occupations
(the saved occup.txt files of the accepted runs) differ by more than 0.2 is selected; the distance is the Frobenius
norm over both spins. The screen selects Cr 19 at Ni31 s1/0 and at Cu26 s1/0. The 0.2 was set after the scan, inside
the gap between those two atoms and every other atom away from the adsorbate; any value in the gap selects the same.

Runs. For each selected atom, two second starts: the slab with the atom's blocks (occup.txt, both spins; paw.txt,
both spins) from the OH, and the OH with them from the slab. Cr is an ultrasoft species here, so QE uses only its
occupations; its paw.txt block is carried for consistency with rounds 1-5 and has no effect. Each deck is the
production deck with round 5's changes (its own prefix, startingpot 'file', mixing_ndim 16, mixing_fixed_ns 5;
arm_c_ext_r5_build.r5_deck) and QE's own stop 600 s before the runner's SCF wall. Each starts from its own converged
save, which start_sources.json pins on Anvil: the density and XML are copied on Anvil, and occup.txt and paw.txt are
rebuilt. The walls follow each site's production iteration counts (Ni31 s1/0: 38 and 38; Cu26 s1/0: 76 and 119): one
array of two runs per site, 120 min at Ni31 s1/0 and 180 min at Cu26 s1/0, which fit the approved campaign ceiling.

The plan rows mark each run as a second start of an accepted state (second_start). The readout replaces a state only
if its run converges, after the held iterations, more than 1 meV lower (arm_c_readout.py).

    python src/dft/arm_c_ext_r6_build.py            # write the decks, occup.txt, paw.txt, manifest, plan, spec
    python src/dft/arm_c_ext_r6_build.py --check    # rebuild and compare with the files on disk
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arm_c_build as cb  # noqa: E402
import arm_c_ext_build as r1  # noqa: E402
import arm_c_ext_r2_build as r2  # noqa: E402
import arm_c_ext_r3_build as r3  # noqa: E402
import arm_c_ext_r4_build as r4  # noqa: E402
import arm_c_ext_r5_build as r5  # noqa: E402
import hea_deck as hd  # noqa: E402

ROOT = HERE.parents[1]
DATE = "2026-10-11"
PACKAGE = "results/arm_c_ext_r6_" + DATE
RUN_ROOT = "hea/arm_c_ext_r6_" + DATE
R5_SPEC = r5.PACKAGE + "/launch_spec.json"
R5_PLAN = r5.PACKAGE + "/ext_plan.json"
R5_READOUT = r5.PACKAGE + "/readout.json"
R5_COLLECTION = r5.PACKAGE + "/terminal_collection.json"
R5_TASKS = 1  # the one round-5 task accounted by sacct
PRODUCTION_SPEC = r1.SOURCE_SPEC
START_SOURCES = PACKAGE + "/start_sources.json"
MANIFEST = {"r6_ni31": "runs/m_arm_c_ext_r6_" + DATE + "_ni31.txt",
            "r6_cu26": "runs/m_arm_c_ext_r6_" + DATE + "_cu26.txt"}
DESIGN = r2.DESIGN
DECISION = "Frank, 2026-10-10: \"Go ahead with other values\" (after round 5's readout)"
STATES = ("slab", "OH")  # step 1 limits at every value site
SCREEN_MIN = 0.2  # set after the scan, in the gap between the selected atoms and every other atom away from O1
BONDED_A = 2.5  # the adsorbate's O binds one metal at 1.80-1.89 A; every other Hubbard atom lies 3.5 A or more away
TARGETS = (("Ni31Cr29Cu5Mn35__s1_site0", 19), ("Cu26Ni9Cr31Co33__s1_site0", 19))
STAGES = {"Ni31Cr29Cu5Mn35__s1_site0": "r6_ni31", "Cu26Ni9Cr31Co33__s1_site0": "r6_cu26"}
LABELS = {"Ni31Cr29Cu5Mn35__s1_site0": "Ni31Cr29Cu5Mn35 s1/0", "Cu26Ni9Cr31Co33__s1_site0": "Cu26Ni9Cr31Co33 s1/0"}
FE25 = "Fe25Co25Ni25Cr25__s25_site2"  # its slab and OH are committed: round 5's mirror and round 3's site files
JOB_SUFFIX = "_fixns5"
MIXING = dict(r5.MIXING)
QE_STOP_MARGIN = r3.LIMITS["r3_main"]["scf_seconds"] - r3.QE_MAX_SECONDS  # 600 s, as in rounds 3-5
# 1,100 s of each wall stays outside the SCF and projection walls, as in rounds 3-5
LIMITS = {"r6_ni31": {"max_iterations": 300, "scf_seconds": 5500, "projection_seconds": 600, "wall_minutes": 120},
          "r6_cu26": {"max_iterations": 300, "scf_seconds": 9100, "projection_seconds": 600, "wall_minutes": 180}}
QE_MAX_SECONDS = {stage: limits["scf_seconds"] - QE_STOP_MARGIN for stage, limits in LIMITS.items()}
REMOTE_FILES = r5.REMOTE_FILES  # copied on Anvil from each run's own save
PRINT_TOLERANCE = 6e-4  # QE prints the final occupations to 3 decimals
FINAL = "End of self-consistent calculation"
ATOM_HEAD = re.compile(r"-+ ATOM\s+(\d+) -+")
MATRIX = "occupation matrix ns (before diag.):"
MIRRORS = {"production": "results/arm_c_2026-10-07/raw_mirror/runs/",
           "rerun": "results/arm_c_2026-10-07_rerun/raw_mirror/runs/hea/arm_c_2026-10-07_rerun/"}


def r6_deck(text: str, job: str, max_seconds: int) -> str:
    """The production deck with round 5's changes and QE's own stop at max_seconds."""
    old = f"  max_seconds = {r3.QE_MAX_SECONDS}"
    deck = r5.r5_deck(text, job)
    if deck.split("\n").count(old) != 1:
        raise ValueError("round-5 deck lacks its max_seconds line")
    return deck.replace(old, f"  max_seconds = {max_seconds}")


def occupations(start: bytes, source: bytes, nat: int, atom: int) -> bytes:
    """The start's occupations with one atom's block (both spins) taken from the source state's."""
    ns, other = r1.numbers(start.decode("ascii")), r1.numbers(source.decode("ascii"))
    if len(ns) != nat * r1.NS_BLOCK or len(other) % r1.NS_BLOCK or len(other) < r1.SLAB_ATOMS * r1.NS_BLOCK:
        raise ValueError("occupation sizes do not match the atom counts")
    lo, hi = (atom - 1) * r1.NS_BLOCK, atom * r1.NS_BLOCK
    if not any(other[lo:hi]) or other[lo:hi] == ns[lo:hi]:
        raise ValueError("the source block is empty or already in place")
    return r1.render(ns[:lo] + other[lo:hi] + ns[hi:])


def paw(start: bytes, source: bytes, nat: int, nat_source: int, atom: int) -> bytes:
    """The start's becsum(171, nat, nspin=2) with one atom's block in each spin taken from the source state's."""
    bec, other = r1.numbers(start.decode("ascii")), r1.numbers(source.decode("ascii"))
    if len(bec) != r1.BEC_BLOCK * nat * 2 or len(other) != r1.BEC_BLOCK * nat_source * 2:
        raise ValueError("PAW sizes do not match the atom counts")
    for spin in range(2):
        lo, src = r1.BEC_BLOCK * (spin * nat + atom - 1), r1.BEC_BLOCK * (spin * nat_source + atom - 1)
        block = other[src:src + r1.BEC_BLOCK]
        if not any(block) or block == bec[lo:lo + r1.BEC_BLOCK]:
            raise ValueError("the source PAW block is empty or already in place")
        bec[lo:lo + r1.BEC_BLOCK] = block
    return r1.render(bec)


def matrices(data: bytes) -> np.ndarray:
    """ns as [atom][spin][m1][m2] (occup.txt is Fortran-ordered, m1 fastest)."""
    values = r1.numbers(data.decode("ascii"))
    if len(values) % r1.NS_BLOCK:
        raise ValueError("not a whole number of atom blocks")
    return np.array(values).reshape(-1, 2, 5, 5).transpose(0, 1, 3, 2)


def printed_final(text: str) -> dict:
    """Each atom's two matrices in QE's last printed HUBBARD OCCUPATIONS block, after convergence."""
    block = text[text.rindex(FINAL):]
    block = block[block.index("HUBBARD OCCUPATIONS"):]
    heads = [(m.start(), int(m.group(1))) for m in ATOM_HEAD.finditer(block)] + [(len(block), None)]
    found = {}
    for (a, atom), (b, _) in zip(heads, heads[1:]):
        lines = block[a:b].split("\n")
        mats = [[[float(x) for x in row.split()] for row in lines[i + 1:i + 6]]
                for i, line in enumerate(lines) if line.strip() == MATRIX]
        if len(mats) == 2:
            found[atom] = np.array(mats)
    return found


def distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b))


def accepted(site: dict, state: str) -> tuple:
    """The accepted run of a state and the layer it came from (arm C's production or re-run)."""
    job = site["states"][state]["job"]
    if any(a["job"] == job and a["accepted"] for a in site.get("extension_attempts", [])):
        return job, "extension"
    return job, ("rerun" if any(a["job"] == job and a["accepted"] for a in site.get("rerun_attempts", []))
                 else "production")


def value_sites(readout: dict) -> list:
    """The complete sites behind the alloys' values, in readout order."""
    used = {(a, s["site"]) for a, alloy in readout["alloys"].items() for s in alloy["supports"]
            if s["eta_dft_V"] is not None}
    return [s for s in readout["sites"] if (s["formula"], f"s{s['seed']}/{s['site_index']}") in used]


def screen_files(root: Path, readout: dict, pins: dict) -> dict:
    """(site, state) -> (job, layer, occup.txt path, committed output path) of every screened state."""
    r3_files = json.loads((root / r4.R3_SITE_OCCUPATIONS).read_text(encoding="utf-8"))["files"]
    found = {}
    for site in value_sites(readout):
        name = r1.site_name(site["dir"])
        for state in STATES:
            job, layer = accepted(site, state)
            if name == FE25:
                attempt = next(a for a in site["extension_attempts"] if a["job"] == job and a["accepted"])
                if state == "slab":
                    rows = [r for r in json.loads((root / R5_PLAN).read_text(encoding="utf-8"))["selection"]
                            if r["job"] == job]
                    occup = f"{r5.PACKAGE}/raw_mirror/runs/{rows[0]['dir']}/tmp_{job}/{job}.save/occup.txt"
                    out = f"{r5.PACKAGE}/raw_mirror/runs/{rows[0]['dir']}/{job}.out"
                else:
                    entry = next(f for f in r3_files if f["site"] == name and f["state"] == state and f["job"] == job)
                    occup = f"{r3.PACKAGE}/{entry['local']}"
                    out = f"{r2.PACKAGE}/raw_mirror/runs/{r2.RUN_ROOT}/{name}/{job}.out"
                if attempt.get("round") not in ((5,) if state == "slab" else (None,)):
                    raise ValueError(f"{name} {state}: unexpected extension round")
            else:
                entry = pins["saves"][f"{name}/{state}"]
                if (entry["job"], entry["layer"]) != (job, layer) or not entry["all_match"]:
                    raise ValueError(f"{name} {state}: the pinned save is not the accepted run's")
                occup = entry["fetched"]["occup.txt"]["local"]
                out = (MIRRORS[layer] + (site["dir"] if layer == "production" else name) + f"/{job}.out")
            found[(name, state)] = (job, layer, occup, out)
    return found


def screen(root: Path, readout: dict, pins: dict) -> dict:
    """Each value site's Hubbard atoms away from the adsorbate, ranked by their slab-to-OH occupation distance."""
    files = screen_files(root, readout, pins)
    result = {}
    for site in value_sites(readout):
        name = r1.site_name(site["dir"])
        ns, printed = {}, {}
        for state in STATES:
            job, layer, occup, out = files[(name, state)]
            ns[state] = matrices((root / occup).read_bytes())
            final = printed_final((root / out).read_text(errors="replace"))
            gap = max(float(np.abs(ns[state][a - 1] - m).max()) for a, m in final.items())
            if gap > PRINT_TOLERANCE or len(final) != sum(1 for b in ns[state] if b.any()):
                raise ValueError(f"{name} {state}: occup.txt is not the accepted run's final occupations")
            printed[state] = round(gap, 6)
        deck = (root / f"runs/{site['dir']}/OH__atomic.in").read_text(encoding="utf-8")
        slab_deck = (root / f"runs/{site['dir']}/slab__atomic.in").read_text(encoding="utf-8")
        cell, atoms = r1.geometry(deck)
        _, slab_atoms = r1.geometry(slab_deck)
        if [a[0] for a in slab_atoms] != [a[0] for a in atoms[:r1.SLAB_ATOMS]] or atoms[r1.SLAB_ATOMS][0] != "O":
            raise ValueError(f"{name}: the slab and OH decks differ in their first {r1.SLAB_ATOMS} atoms")
        o1 = atoms[r1.SLAB_ATOMS][1]
        rows = []
        for i in range(r1.SLAB_ATOMS):
            if not ns["slab"][i].any() and not ns["OH"][i].any():
                continue
            rows.append({"atom": i + 1, "species": atoms[i][0],
                         "distance_to_O1_A": round(r1.in_plane_distance(cell, o1, atoms[i][1]), 3),
                         "slab_to_OH": round(distance(ns["slab"][i], ns["OH"][i]), 4)})
        rows.sort(key=lambda r: (-r["slab_to_OH"], r["atom"]))
        bonded = [r for r in rows if r["distance_to_O1_A"] <= BONDED_A]
        away = [r for r in rows if r["distance_to_O1_A"] > BONDED_A]
        if len(bonded) != 1 or min(r["distance_to_O1_A"] for r in away) < 3.0:
            raise ValueError(f"{name}: expected one metal bonded to the adsorbate and none between 2.5 and 3 A")
        result[name] = {"jobs": {s: files[(name, s)][0] for s in STATES},
                        "occupations": {s: files[(name, s)][2] for s in STATES},
                        "printed_final_max_difference": printed, "potential_limiting_step":
                        site["potential_limiting_step"], "hubbard_atoms": len(rows), "bonded": bonded[0],
                        "selected": [r for r in away if r["slab_to_OH"] > SCREEN_MIN],
                        "largest_unselected": next((r for r in away if r["slab_to_OH"] <= SCREEN_MIN), None)}
    return result


def r5_cpu_su(root: Path) -> float:
    """CPU SU of round 5: the sacct CPU time of its task (terminal_collection.json)."""
    collection = json.loads((root / R5_COLLECTION).read_text(encoding="utf-8"))
    rows = [line.split("|") for line in collection["sacct"].strip().splitlines()]
    seconds = [int(r[7]) for r in rows if "." not in r[0]]
    if len(seconds) != R5_TASKS:
        raise ValueError(f"expected {R5_TASKS} accounted round-5 task, found {len(seconds)}")
    return sum(seconds) / 3600


def manifest_text(stage: str, site: str, jobs: list) -> str:
    head = ["# APPROVED 2026-10-10: " + DESIGN + " (Frank: \"Go ahead with other values\")",
            "# S8 arm C extension, round 6 (" + stage + "): second starts of the slab and the OH at " + site + ", each "
            "from its own converged density with Cr 19's occupations and PAW block from the other state, the "
            "occupations held for 5 iterations (mixing_fixed_ns), up to 300 iterations; exploratory; no automatic "
            "retries.",
            "# SUBMIT WITH EXCLUDE=" + hd.EXCLUDE,
            "# NP=128 NCONC=1"]
    return "\n".join(head + [f"{j['dir']} {j['job']} .in {j['nk']}" for j in jobs]) + "\n"


def build(root: Path = ROOT) -> dict:
    """Committed output path -> bytes; nothing is written here."""
    readout_bytes = (root / R5_READOUT).read_bytes()
    readout = json.loads(readout_bytes)
    r5_spec_bytes = (root / R5_SPEC).read_bytes()
    r5_spec = json.loads(r5_spec_bytes)
    production = json.loads((root / PRODUCTION_SPEC).read_text(encoding="utf-8"))
    pins = json.loads((root / START_SOURCES).read_text(encoding="utf-8"))
    for stage, limits in LIMITS.items():
        if not QE_MAX_SECONDS[stage] < limits["scf_seconds"]:
            raise ValueError("QE must stop itself before the runner's SCF wall")
        if not MIXING["mixing_fixed_ns"] < limits["max_iterations"]:
            raise ValueError("the occupations must be released before the iteration ceiling")
        if limits["wall_minutes"] * 60 - limits["scf_seconds"] - limits["projection_seconds"] != 1100:
            raise ValueError("each wall keeps rounds 3-5's 1,100 s outside the SCF and projection walls")
    if not pins["all_match"]:
        raise ValueError("a start source differs from Anvil")
    screened = screen(root, readout, pins)
    if any(s["potential_limiting_step"] != 1 for s in screened.values()):
        raise ValueError("step 1 must limit at every value site")
    selected = tuple((name, r["atom"]) for name, s in screened.items() for r in s["selected"])
    if selected != TARGETS:
        raise ValueError("the screen selects " + repr(selected))
    sites = {r1.site_name(s["dir"]): s for s in readout["sites"]}
    files, jobs, rows = {}, {stage: [] for stage in LIMITS}, []
    for name, atom in TARGETS:
        site, stage = sites[name], STAGES[name]
        hit = next(r for r in screened[name]["selected"] if r["atom"] == atom)
        for state, other in (("slab", "OH"), ("OH", "slab")):
            first, source = site["states"][state], site["states"][other]
            first_job = state + "__atomic"
            if (first["job"] != first_job or first["recipe"] != "production" or not first["accepted"]
                    or source["job"] != other + "__atomic"):
                raise ValueError(f"{name} {state}: expected production's accepted slab and OH")
            old = next(j for stage in production["stages"].values() for j in stage["jobs"]
                       if r1.site_name(j["dir"]) == name and j["job"] == first_job)
            source_deck = f"runs/{old['dir']}/{first_job}.in"
            old_deck = (root / source_deck).read_bytes()
            if cb.sha256(old_deck) != old["sha256"]:
                raise ValueError("production deck differs from its pin: " + source_deck)
            _, atoms = r1.geometry(old_deck.decode("utf-8"))
            if len(atoms) != r1.nat_of(state) or atoms[atom - 1][0] != hit["species"]:
                raise ValueError(f"{name} {state}: atom {atom} is not the screened {hit['species']}")
            own, src = pins["saves"][f"{name}/{state}"], pins["saves"][f"{name}/{other}"]
            save = own["save"]
            expected = (f"/anvil/projects/x-che260157/sts_arm_c_{cb.DATE}/runs/{old['dir']}/tmp_{first_job}/"
                        f"{first_job}.save")
            if save != expected or own["layer"] != "production" or set(own["files"]) != {*REMOTE_FILES, "occup.txt",
                                                                                       "paw.txt"}:
                raise ValueError(f"{name} {state}: the pinned save is not production's")
            data = {k: {n: (root / e["fetched"][n]["local"]).read_bytes() for n in ("occup.txt", "paw.txt")}
                    for k, e in (("own", own), ("src", src))}
            for k, e in (("own", own), ("src", src)):
                for n, blob in data[k].items():
                    if cb.sha256(blob) != e["fetched"][n]["sha256"] or cb.sha256(blob) != e["files"][n]["sha256"]:
                        raise ValueError(f"{name}: a mirrored {n} differs from its pin")
            label = hit["species"].lower() + str(atom) + other.lower()
            job_name = f"{first_job}_{label}{JOB_SUFFIX}"
            occup = occupations(data["own"]["occup.txt"], data["src"]["occup.txt"], r1.nat_of(state), atom)
            paw_text = paw(data["own"]["paw.txt"], data["src"]["paw.txt"], r1.nat_of(state), r1.nat_of(other), atom)
            job_dir = f"{RUN_ROOT}/{name}"
            deck = r6_deck(old_deck.decode("utf-8"), job_name, QE_MAX_SECONDS[stage]).encode("utf-8")
            bundle = f"{PACKAGE}/seeds/{name}/{state}"
            files.update({f"runs/{job_dir}/{job_name}.in": deck, f"{bundle}/occup.txt": occup,
                          f"{bundle}/paw.txt": paw_text})
            scratch = {f: own["files"][f]["sha256"] for f in REMOTE_FILES}
            scratch.update({"occup.txt": cb.sha256(occup), "paw.txt": cb.sha256(paw_text)})
            jobs[stage].append({"dir": job_dir, "job": job_name, "sha256": cb.sha256(deck), "nk": old["nk"],
                                **{k: LIMITS[stage][k] for k in ("scf_seconds", "projection_seconds", "max_iterations")},
                                "recipe": "seeded", "role": "extension", "source_deck": source_deck,
                                "seed": {"state": state, "job": first_job, "recipe": "production", "save_dir": save},
                                "scratch_source": {"save_dir": bundle, "files": dict(sorted(scratch.items()))}})
            rows.append({
                "site_dir": old["dir"], "formula": name.split("__")[0], "state": state, "second_start": True,
                "first": {"job": first_job, "recipe": first["recipe"], "E_eV": first["E_eV"],
                          "total_magnetization": first["total_magnetization"]},
                "seed": {"state": state, "job": first_job, "recipe": "production", "root": r1.PRODUCTION_ROOT,
                         "id": f"{name}__{first_job}"},
                "dir": job_dir, "job": job_name, "round": 6, "stage": stage, "qe_max_seconds": QE_MAX_SECONDS[stage],
                "seed_density": "own_converged", "bundle": bundle,
                "remote_copy": {f: save + "/" + f for f in REMOTE_FILES}, "mixing": dict(MIXING),
                "screen": dict(hit, half_way=round(hit["slab_to_OH"] / 2, 4)),
                "occupations": {"start": own["fetched"]["occup.txt"]["local"],
                                "start_sha256": own["fetched"]["occup.txt"]["sha256"], "atoms_replaced": [atom],
                                "from": {"state": other, "job": src["job"], "recipe": "production",
                                         "path": src["fetched"]["occup.txt"]["local"],
                                         "sha256": src["fetched"]["occup.txt"]["sha256"]},
                                "sha256": cb.sha256(occup)},
                "paw": {"start": own["fetched"]["paw.txt"]["local"], "start_sha256": own["fetched"]["paw.txt"]["sha256"],
                        "atoms_replaced": [atom],
                        "from": {"state": other, "job": src["job"], "path": src["fetched"]["paw.txt"]["local"],
                                 "remote": src["fetched"]["paw.txt"]["remote"],
                                 "sha256": src["fetched"]["paw.txt"]["sha256"]},
                        "sha256": cb.sha256(paw_text)},
                "density": {"source": save + "/" + r2.DENSITY, "sha256": own["files"][r2.DENSITY]["sha256"],
                            "bytes": own["files"][r2.DENSITY]["bytes"]}})
    stages = {stage: {"kind": "hea", "manifest": MANIFEST[stage], "concurrency": len(jobs[stage]),
                      "wall_minutes": LIMITS[stage]["wall_minutes"], "jobs": jobs[stage]} for stage in LIMITS}
    for name, stage in STAGES.items():
        files[MANIFEST[stage]] = manifest_text(stage, LABELS[name], jobs[stage]).encode("utf-8")
    stage_pins = {path: cb.sha256(data) for path, data in files.items()}
    for relative in r1.RUNNER_FILES:
        stage_pins[relative] = cb.sha256((root / relative).read_bytes())
        if stage_pins[relative] != r5_spec["files"][relative]:
            raise ValueError("runner file changed since round 5: " + relative)
    spent = round(r5_spec["allocation"]["spent_before_this_launch_cpu_su"] + r5_cpu_su(root), 1)
    ceilings = {s: len(stages[s]["jobs"]) * LIMITS[s]["wall_minutes"] * 128 // 60 for s in stages}
    ceiling = sum(ceilings.values())
    campaign = r5_spec["allocation"]["approved_campaign_ceiling_cpu_su"]
    if spent + ceiling > campaign:
        raise ValueError("round 6 does not fit the approved arm-C campaign ceiling")
    source_readout = {"path": R5_READOUT, "sha256": cb.sha256(readout_bytes)}
    spec = {
        "schema": "research-batch-2026-09-16",
        "np": 128,
        "exclusions": hd.EXCLUDE,
        "date": DATE,
        "design": DESIGN,
        "decision_ref": DECISION,
        "source_readout": source_readout,
        "allocation": {"account": "che260157", "partition": "wholenode", "cores_per_task": 128,
                       "approved_campaign_ceiling_cpu_su": campaign,
                       "spent_before_this_launch_cpu_su": spent,
                       "stage_ceilings_cpu_su": ceilings,
                       "this_launch_ceiling_cpu_su": ceiling},
        "qe_binaries_sha256": r5_spec["qe_binaries_sha256"],
        "files": dict(sorted(stage_pins.items())),
        "pseudo_md5": r5_spec["pseudo_md5"],
        "stages": stages,
    }
    plan = {"schema": "s8-arm-c-ext-plan-v1", "date": DATE, "design": DESIGN, "decision_ref": DECISION,
            "source_readout": source_readout, "round": 6,
            "round_5": {"spec": R5_SPEC, "spec_sha256": cb.sha256(r5_spec_bytes), "plan": R5_PLAN,
                        "main": "21234401 read out: the Fe25 s25/2 slab, restarted with Fe 22 in OH's configuration, "
                                "converged 259 meV below the production slab and replaced it; Fe25 0.893 -> 1.152 V"},
            "rule": ("second starts of the slab and the OH at each value site whose slab and OH occupations differ by "
                     f"more than {SCREEN_MIN} at a Hubbard atom more than {BONDED_A} A from the adsorbate's O: each "
                     "state's production deck with round 5's changes (mixing_ndim 16, mixing_fixed_ns 5, startingpot "
                     "'file') and QE's own stop 600 s before the runner's SCF wall (120 min per run at Ni31 s1/0, "
                     "180 min at Cu26 s1/0), from its own converged save (density and XML copied "
                     "on Anvil; occup.txt and paw.txt rebuilt) with that atom's Hubbard occupations and PAW block "
                     "(both spins; Cr is ultrasoft, so only its occupations act) from the other state; a run replaces "
                     "its state only if it converges after the held iterations more than 1 meV lower"),
            "screen": {"states": list(STATES), "min_distance": SCREEN_MIN, "bonded_A": BONDED_A, "sites": screened},
            "mixing": dict(MIXING), "qe_max_seconds": dict(QE_MAX_SECONDS),
            "status": "exploratory; arm C's registered readings stay final",
            "selection": rows}
    files[PACKAGE + "/ext_plan.json"] = (json.dumps(plan, indent=2) + "\n").encode("utf-8")
    files[PACKAGE + "/launch_spec.json"] = (json.dumps(spec, indent=2) + "\n").encode("utf-8")
    return files


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare a fresh build with the files on disk")
    args = parser.parse_args(argv)
    files = build()
    problems, written = [], []
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
            written.append(relative)
    print(json.dumps({"files": len(files), "mismatches": problems, "written": len(written),
                      "spec_sha256": cb.sha256(files[PACKAGE + "/launch_spec.json"])}, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
