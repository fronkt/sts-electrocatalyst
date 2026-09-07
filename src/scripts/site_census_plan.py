"""Layout and queue order of the 2026-09-06 site-integrity census (docs/91).

Shared by site_census_build_manifests.py (creates the manifests), site_census_runner.py
(runs them) and site_census_readout.py (aggregates the results). Nothing here evaluates a
model or touches a sealed module.
"""
from __future__ import annotations

import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
#: SITE_CENSUS_DIR relocates the whole tree (smoke tests run against a scratch root).
CENSUS_DIR = Path(os.environ.get("SITE_CENSUS_DIR") or (ROOT / "results/site_census_2026-09-06")).resolve()
MANIFEST_DIR = CENSUS_DIR / "manifests"
RESULT_DIR = CENSUS_DIR / "results"
LOG_DIR = CENSUS_DIR / "logs"
READOUT_DIR = CENSUS_DIR / "readout"
STATUS_FILE = CENSUS_DIR / "status.json"
STOP_FILE = CENSUS_DIR / "STOP"
MANIFEST_HASHES = CENSUS_DIR / "MANIFESTS.sha256"

#: Tracked LF copies of the source screens (sha256_lf recorded in every manifest).
BOX_SOURCE = ROOT / "results/ranking_adequacy_2026-09-06/inputs/r4_screen_box.json"
VALIDATE_SOURCE = ROOT / "results/ranking_adequacy_2026-09-06/inputs/r4_validate.json"
GATED_SOURCE = ROOT / "results/ranking_adequacy_2026-09-06/inputs/r4_gated.json"

#: MACE checkpoints by census tag -> cached filename under ~/.cache/mace (mace 0.3.15 names).
#: MACE-MH-1 (macemh1model) is a multi-head checkpoint that the sealed calculator
#: constructor (hea_oer.relax.make_mace_calculator, no `head` keyword) cannot load; it is
#: not a census tag (docs/91 §1, CENSUS-2).
MODEL_FILES = {
    "mpa0": "macempa0mediummodel",                 # MACE-MPA-0 medium (the screen's model)
    "omat0": "maceomat0mediummodel",               # MACE-OMAT-0 medium
    "mp0": "20231203mace128L1_epoch199model",      # MACE-MP-0 medium (2023-12-03, 128 L1)
    "matpes": "MACEmatpesr2scanomatftmodel",       # MACE-MATPES-r2SCAN-OMAT-ft
}
MODEL_LABELS = {
    "mpa0": "MACE-MPA-0 medium", "omat0": "MACE-OMAT-0 medium",
    "mp0": "MACE-MP-0 medium (2023-12-03 128 L1)", "matpes": "MACE-MATPES-r2SCAN-OMAT-ft",
}
ENSEMBLE_TAGS = ("omat0", "mp0", "matpes")


def model_cache_dir():
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(base) / "mace"


def model_path(tag):
    return model_cache_dir() / MODEL_FILES[tag]


#: The six gated compositions, in the order of results/r4_gated.json (eta ascending).
GATED_SIX = ("Ni31Cr29Cu5Mn35", "Fe25Co25Ni25Cr25", "Cu26Ni9Cr31Co33",
             "Ni34Fe6Cu29Co31", "Cu8Cr23Mn35Co34", "Cu22Fe30Co32Mn15")
#: The other six box compositions, in box (eta ascending) order.
OTHER_SIX = ("Cr33Co5Ni29Cu33", "Mn31Ni31Co33Cu6", "Fe31Cu25Cr13Ni31",
             "Mn34Cu7Fe33Cr27", "Co5Cu33Ni28Mn34", "Ni34Fe29Mn30Co7")
BOX_TWELVE = GATED_SIX + OTHER_SIX
#: Validation endmembers (r4_validate.json `pred` keys, in that order).
ENDMEMBERS = ("Cr", "Mn", "Fe", "Co", "Ni", "Ru", "Ir")

#: CENSUS-3 seeds 3..29, split into blocks of three so each manifest checkpoint is one
#: seed block (a killed process loses at most one block, not the whole 27-seed run).
EXT_SEEDS = tuple(range(3, 30))
EXT_BLOCKS = tuple(EXT_SEEDS[i:i + 3] for i in range(0, len(EXT_SEEDS), 3))

ENDMEMBER_MANIFEST = "endmember_2x2__mpa0"

_EXT = re.compile(r"^mpa0_ext__(?P<formula>[A-Za-z0-9]+)__s(?P<lo>\d{2})-(?P<hi>\d{2})$")
_STD = re.compile(r"^(?P<tag>mpa0|omat0|mp0|matpes)__(?P<formula>[A-Za-z0-9]+)$")


def ext_block_stem(formula, block):
    return f"mpa0_ext__{formula}__s{block[0]:02d}-{block[-1]:02d}"


def parse_stem(stem):
    """-> dict(arm, tag, formula|None, block|None) or raise ValueError for a foreign name."""
    if stem == ENDMEMBER_MANIFEST:
        return dict(arm="ENDMEMBER-2x2", tag="mpa0", formula=None, block=None)
    m = _EXT.match(stem)
    if m:
        lo, hi = int(m["lo"]), int(m["hi"])
        return dict(arm="CENSUS-3", tag="mpa0", formula=m["formula"], block=(lo, hi))
    m = _STD.match(stem)
    if m:
        arm = "CENSUS-1" if m["tag"] == "mpa0" else "CENSUS-2"
        return dict(arm=arm, tag=m["tag"], formula=m["formula"], block=None)
    raise ValueError("manifest name outside the census layout: " + stem)


def expected_stems():
    """Every manifest stem the census expects, in queue order."""
    order = [f"mpa0__{f}" for f in GATED_SIX]
    order += [f"mpa0__{f}" for f in OTHER_SIX]
    order.append(ENDMEMBER_MANIFEST)
    for tag in ENSEMBLE_TAGS:
        order += [f"{tag}__{f}" for f in GATED_SIX]
    for tag in ENSEMBLE_TAGS:
        order += [f"{tag}__{f}" for f in OTHER_SIX]
    for f in GATED_SIX:
        order += [ext_block_stem(f, block) for block in EXT_BLOCKS]
    return order


def queue_order(stems):
    """Order the given manifest stems by the census queue; refuse foreign names."""
    for stem in stems:
        parse_stem(stem)
    rank = {stem: k for k, stem in enumerate(expected_stems())}
    unknown = [s for s in stems if s not in rank]
    if unknown:
        raise ValueError("manifests outside the expected census set: " + ", ".join(sorted(unknown)))
    return sorted(stems, key=rank.__getitem__)


def result_path(stem):
    return RESULT_DIR / (stem + "_result.json")


def log_path(stem):
    return LOG_DIR / (stem + ".log")


def manifest_path(stem):
    return MANIFEST_DIR / (stem + ".json")
