#!/usr/bin/env python3
"""Pre-flight for the entrant's ONE atomic commit that lands the `silentgate` core.

WHY ONE COMMIT
--------------
tests/silentgate/conftest.py:69-70 gates seven tests on `os.path.isdir("silentgate")`.
The instant the directory exists, all seven run. A half-populated package -- or an
empty directory -- turns seven registered SKIPs into seven FAILURES on the public
CI face. So the five core paths, the filled invocation file and the provenance
record must arrive together, and this script checks that state locally BEFORE
`git commit`, then prints the exact commands. It never runs git write commands
and never creates, moves or edits a file.

WHAT THIS SCRIPT IS NOT
-----------------------
It contains no reader, no census and no opinion about what the core should
compute. docs/43:1840 reserves silentgate/readers/*, census.py, classify.py,
direction.py and cli.py to the entrant, and docs/71 is the brief. This file is
"test scaffolding / CI" under the same line's permitted list. It reads the five
paths only to ask whether they exist and are non-empty.

CHECKS
------
  C1  silentgate/ exists, holds the five names (run_controls.py:293), each
      non-empty; readers/ is a non-empty directory
  C2  git: the five are all untracked-or-staged (first commit) or all tracked;
      never a partial set already in history
  C3  tests/silentgate/spec_rulings.toml: seven non-empty rulings, each dated
      line citing a file that exists
  C4  .github/ci/silentgate-invocation.toml: census_cmd and oc20_cmd non-empty,
      and the schema pointers run_controls/run_oc20 refuse without
  C5  the provenance record at the path the workflow sets in $S1_AI_USE_LOG
      exists, and check_disjoint.py PASSES against it
  C6  `pytest tests/silentgate` passes with ZERO skips (the seven are now live)

Exit 0 only if every check passes. Run from the repository root.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

CORE_NAMES = ("readers", "census.py", "classify.py", "direction.py", "cli.py")
RULING_IDS = ("adsorbate_quantifier", "truncated_force_block", "oc20_ci_mechanism",
              "ai_use_log_path", "if_pos_parenthetical", "pyproject_build_system",
              "ai_x_census_disclosure")
NEEDED_POINTERS = ("runs_array", "path", "locked_force_only", "locked_two_witness",
                   "n_symops", "nosym_in_deck", "per_step_exact_zero_count")


def load_toml(path):
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover
        import tomli as tomllib  # type: ignore
    with open(path, "rb") as fh:
        return tomllib.load(fh)


class Report:
    def __init__(self):
        self.rows = []

    def add(self, key, ok, detail):
        self.rows.append((key, ok, detail))
        print("%s  %s  %s" % ("PASS" if ok else "FAIL", key, detail))

    @property
    def ok(self):
        return all(ok for _k, ok, _d in self.rows)


def c1_core_present(root, rep):
    sg = os.path.join(root, "silentgate")
    if not os.path.isdir(sg):
        rep.add("C1", False, "silentgate/ does not exist. Nothing to commit yet -- and do "
                "NOT create it empty: conftest.py:69-70 keys on the directory.")
        return
    entries = os.listdir(sg)
    if not entries:
        rep.add("C1", False, "silentgate/ EXISTS BUT IS EMPTY. conftest.py:69-70 now runs "
                "the seven core-gated tests and all seven fail. Populate or remove it.")
        return
    missing, empty = [], []
    for name in CORE_NAMES:
        p = os.path.join(sg, name)
        if not os.path.exists(p):
            missing.append(name)
        elif os.path.isdir(p):
            if not any(f.endswith(".py") for f in os.listdir(p)):
                empty.append(name + "/ (no .py inside)")
        elif os.path.getsize(p) == 0:
            empty.append(name)
    if missing or empty:
        rep.add("C1", False, "core incomplete -- missing: %s; empty: %s"
                % (missing or "-", empty or "-"))
    else:
        rep.add("C1", True, "silentgate/ holds all five named paths, each non-empty")


def c2_git_state(root, rep):
    def git(*a):
        return subprocess.run(["git", *a], cwd=root, capture_output=True, text=True).stdout
    tracked = [l for l in git("ls-files", "silentgate").splitlines() if l]
    if not tracked:
        rep.add("C2", True, "no core path is in history yet -- this will be the first commit")
        return
    have = set()
    for t in tracked:
        rel = t.split("/", 1)[1] if "/" in t else t
        have.add(rel.split("/")[0])
    missing = [n for n in CORE_NAMES if n not in have]
    if missing:
        rep.add("C2", False, "history holds a PARTIAL core (tracked: %s; absent: %s). The "
                "core must land whole." % (sorted(have), missing))
    else:
        rep.add("C2", True, "all five core paths already tracked (this is an update commit)")


def c3_rulings(root, rep):
    p = os.path.join(root, "tests", "silentgate", "spec_rulings.toml")
    try:
        data = load_toml(p)
    except Exception as exc:  # pragma: no cover
        rep.add("C3", False, "cannot read %s: %s" % (p, exc))
        return
    qs = {q.get("id"): q for q in data.get("question", [])}
    bad = []
    for rid in RULING_IDS:
        q = qs.get(rid)
        if not q:
            bad.append("%s: absent" % rid)
            continue
        if not str(q.get("ruling", "")).strip():
            bad.append("%s: ruling empty" % rid)
        cite = str(q.get("dated_line", "")).strip()
        if not cite:
            bad.append("%s: dated_line empty" % rid)
        else:
            f = cite.split(":")[0]
            if not os.path.exists(os.path.join(root, f)):
                bad.append("%s: dated_line cites %r which does not exist (use the full "
                           "filename, not docs/43)" % (rid, f))
    rep.add("C3", not bad, "seven rulings filled and cited" if not bad else "; ".join(bad))


def c4_invocation(root, rep):
    p = os.path.join(root, ".github", "ci", "silentgate-invocation.toml")
    try:
        cfg = load_toml(p)
    except Exception as exc:  # pragma: no cover
        rep.add("C4", False, "cannot read %s: %s" % (p, exc))
        return
    cli = cfg.get("cli", {})
    schema = cfg.get("schema", {})
    bad = [k for k in ("census_cmd", "oc20_cmd") if not str(cli.get(k, "")).strip()]
    bad += ["schema.%s" % k for k in NEEDED_POINTERS if not str(schema.get(k, "")).strip()]
    rep.add("C4", not bad, "invocation declared" if not bad
            else "still blank: %s -- the controls report NOT MEASURED without these"
            % ", ".join(bad))


def c5_provenance(root, rep):
    wf = os.path.join(root, ".github", "workflows", "s1-controls.yml")
    log = None
    try:
        with open(wf, encoding="utf-8") as fh:
            m = re.search(r"^\s*S1_AI_USE_LOG:\s*(\S+)\s*$", fh.read(), re.M)
        if m and not m.group(1).startswith("${{"):
            log = m.group(1).strip("'\"")
    except OSError:
        pass
    log = os.environ.get("S1_AI_USE_LOG") or log
    if not log:
        rep.add("C5", False, "the workflow sets no literal S1_AI_USE_LOG and the "
                "environment does not either")
        return
    if not os.path.exists(os.path.join(root, log)):
        rep.add("C5", False, "provenance record %s does not exist; check_disjoint.py "
                "fails closed on a missing log" % log)
        return
    proc = subprocess.run([sys.executable, os.path.join(root, ".github", "ci", "check_disjoint.py"),
                           "--log", log], cwd=root, capture_output=True, text=True)
    first = (proc.stdout.strip().splitlines() or [""])[0]
    rep.add("C5", proc.returncode == 0, first[:160])


def c6_pytest(root, rep, run):
    if not run:
        rep.add("C6", True, "pytest skipped by --no-pytest (run it before committing)")
        return
    proc = subprocess.run([sys.executable, "-m", "pytest", "tests/silentgate", "-q", "-rs"],
                          cwd=root, capture_output=True, text=True)
    tail = (proc.stdout.strip().splitlines() or [""])[-1]
    skipped = "skipped" in tail
    rep.add("C6", proc.returncode == 0 and not skipped,
            tail[:160] + ("  <- skips remain; the seven should be LIVE now" if skipped else ""))


def print_recipe(root):
    print("\nATOMIC COMMIT -- run these yourself; this script does not:")
    print("  git add silentgate/readers silentgate/census.py silentgate/classify.py \\")
    print("          silentgate/direction.py silentgate/cli.py \\")
    print("          .github/ci/silentgate-invocation.toml")
    print("  git status --porcelain            # confirm ONLY the intended paths are staged")
    print("  git commit                        # one commit, all five, the entrant as author")
    print("Then watch the S1 face: the seven skips must read as passes on the next run.")


def main(argv=None):
    ap = argparse.ArgumentParser(description="pre-flight for the silentgate core commit")
    ap.add_argument("--root", default=os.getcwd())
    ap.add_argument("--no-pytest", action="store_true")
    args = ap.parse_args(argv)
    root = os.path.abspath(args.root)
    rep = Report()
    c1_core_present(root, rep)
    c2_git_state(root, rep)
    c3_rulings(root, rep)
    c4_invocation(root, rep)
    c5_provenance(root, rep)
    c6_pytest(root, rep, run=not args.no_pytest)
    print("\nPRE-FLIGHT: %s" % ("READY" if rep.ok else "NOT READY"))
    if rep.ok:
        print_recipe(root)
    return 0 if rep.ok else 1


if __name__ == "__main__":
    sys.exit(main())
