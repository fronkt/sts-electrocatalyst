#!/usr/bin/env python3
"""A test double standing in for `silentgate census`, so the CI machinery can be
proven correct BEFORE the core exists.

It emits canned JSON for whatever paths it is handed. It opens no pw.x output,
parses no force block, reads no symmetry header and computes no verdict -- it
looks each path up in .github/ci/populations.txt and emits the answer the
scenario names. There is no detector in here to be a second detector.

Scenarios (env FAKE_SCENARIO):

  all_pass              the registered outcome: 9/9 LOCKED, 0/11, partition 20/20,
                        n/n agreement, tag counts 20/20
  null_verdicts         every locked_force_only is null -- must be NOT MEASURED,
                        never "0/11 passes"
  one_locked_in_eleven  one nosym-present run locks -- the QE negative control fails
  partition_broken      one deck lands in the wrong half of the partition
  tag_mismatch          the adsorbate rule disagrees with the filename tag
  disagreement          header and force witnesses disagree on one classifiable row
  empty                 an empty runs array

AUTHORSHIP: written by AI as "tests and fixtures" under the A9.1 :1840 permitted
list.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
POPS = os.path.join(ROOT, ".github", "ci", "populations.txt")

TAGS = (("s0_OOH", 3), ("s0_OH", 2), ("s0_O", 1))


def load_pops():
    sets = {}
    with open(POPS, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                kind, path = line.split()
                sets[path] = kind
    return sets


def tag_count(path):
    base = os.path.basename(path)
    for tag, n in TAGS:
        if base.startswith(tag):
            return n
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paths-from", required=True)
    args = ap.parse_args()

    scenario = os.environ.get("FAKE_SCENARIO", "all_pass")
    pops = load_pops()
    with open(args.paths_from, "r", encoding="utf-8") as fh:
        paths = [l.strip() for l in fh if l.strip()]

    if scenario == "empty":
        json.dump({"runs": []}, sys.stdout)
        return 0

    runs = []
    flipped = {"locked": False, "partition": False, "tag": False, "disagree": False}
    for p in paths:
        kind = pops.get(p)
        if kind == "nosym_absent":
            locked, nosym = True, False
            n_symops = 4 if os.path.basename(p).startswith("s0_O.") else 2
        elif kind == "nosym_present":
            locked, nosym = False, True
            n_symops = 1
        else:
            # a classifiable CSV row outside the 20: agreeing, not locked
            locked, nosym, n_symops = False, True, 1

        tw = fo = locked
        n_ads = tag_count(p)

        if scenario == "null_verdicts":
            fo = None
        elif scenario == "one_locked_in_eleven" and kind == "nosym_present" and not flipped["locked"]:
            tw = fo = True
            flipped["locked"] = True
        elif scenario == "partition_broken" and kind == "nosym_present" and not flipped["partition"]:
            nosym = False
            flipped["partition"] = True
        elif scenario == "tag_mismatch" and kind == "nosym_absent" and not flipped["tag"]:
            n_ads = (n_ads or 1) + 7
            flipped["tag"] = True
        elif scenario == "disagreement" and kind is None and not flipped["disagree"]:
            tw, fo = True, False
            flipped["disagree"] = True

        runs.append({
            "path": p,
            "n_symops": n_symops,
            "nosym_in_deck": nosym,
            "locked_two_witness": tw,
            "locked_force_only": fo,
            "locked_axes": ["y"] if locked else [],
            "n_adsorbate": n_ads,
            "unidentified": False,
            "n_if_pos_excluded": 7,
            "header_form": "count-first, no-inversion, bare",
        })

    json.dump({"runs": runs}, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
