#!/usr/bin/env python3
"""The A9.1 disjointness assertion: (AI-use log file list) INTERSECT (core path list) = {}.

Registered requirement, docs/43-prereg-week1-factorial.md :1840, as deposited
2026-08-23 (the prose was re-termed in place on 2026-09-03 -- "AI-use log" is now
"provenance record", docs/43:3287-3309 -- and the identifiers here were left as
they were, deliberately, docs/43:3311-3317):

    "CI asserts that the AI-use log's file list and the core path list are
     disjoint, and prints the assertion's status next to the controls, so that
     'AI never touched the core' is a checked fact and not a sentence."

WHAT THIS PROVES, AND WHAT IT DOES NOT
--------------------------------------
It proves that no file AI *declared* in the log is a core path. It cannot detect
undeclared AI authorship of a core file -- nothing inside the repo can. No CI
output, README or disclosure may claim more than: "every file AI logged is
outside the core." That sentence is the ceiling.

FAIL-CLOSED ON A MISSING OR EMPTY LOG
-------------------------------------
If the AI-use log does not exist, the log's file list is UNDEFINED, not empty.
A vacuous pass would make this check strongest exactly when nobody is logging,
so an absent or unreadable log is a FAILURE. So is a log that EXISTS but names
no file: :1840 attaches the duty "each logged in the AI-use log as produced",
and a log with no entries has not discharged it -- an empty file list is not a
disjoint file list.

The log's path and format are NOT registered. docs/43 names the log as an
obligation five times (:1322, :1443, :1445, :1828, :1840) and never gives it a
path. Electing one is the entrant's call, so this script does not: it takes
--log / $S1_AI_USE_LOG, else searches the tracked tree for an obvious name, and
if it finds nothing it says so and fails.

ALL matching logs are read, never just the first. Whether the log is one file or
many is itself an open registered question (spec_rulings.toml, id =
ai_use_log_path); taking the first match would answer it silently, and a core
path logged in the second file would sail through.

FORMAT-AGNOSTIC BY DESIGN
-------------------------
Because the log's format is unregistered too, this parses no schema. It extracts
every path-like token in the log and tests each against the five core patterns.
Over-extraction is the safe direction: a spurious token can only ever make the
assertion FAIL loudly, with the offending line printed. It can never make it pass.

AUTHORSHIP: written by AI as "the CI workflow" under the A9.1 :1840 permitted
list. It parses the AI-use log and file paths. It contains no pw.x reader, no
force-block parser and no census -- those are core (:1840) and are the entrant's.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CORE_PATHS = os.path.join(HERE, "core_paths.txt")

# A path-like token. Deliberately generous -- see "FORMAT-AGNOSTIC BY DESIGN".
# The backslash is IN the class on purpose: without it a core path logged in
# Windows form (silentgate\census.py) is chopped into harmless fragments and the
# assertion passes. normalise() then folds it to a forward slash.
TOKEN_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_./\\*+-]*")
PATHY_RE = re.compile(
    r"([/\\]|[.](?:py|toml|yml|yaml|txt|md|cfg|ini|json|sh|in|out|slurm|csv)$)"
)

# Names an AI-use log plausibly has, searched only when none is given explicitly.
LOG_NAME_RE = re.compile(r"ai[-_]?use|ai[-_]?log|use[-_]?log", re.I)


def load_core_patterns(path):
    pats = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                pats.append(line)
    if not pats:
        raise SystemExit("FATAL: %s declares no core patterns" % path)
    return pats


def tracked_files():
    try:
        out = subprocess.run(
            ["git", "ls-files"], capture_output=True, text=True, check=True
        )
    except Exception:
        return []
    return [f for f in out.stdout.split("\n") if f]


def find_logs(explicit):
    """Return (logs_found, candidates_searched). An empty list means FAILURE.

    ALL matching logs are read, not the first. "Where does the AI-use log live,
    and is it one file or many?" is an open registered question
    (tests/silentgate/spec_rulings.toml, id = ai_use_log_path). Returning the
    first match would silently answer "one", and a core path logged in the second
    file would pass the assertion. Multiple paths may be given, separated by the
    OS path separator or a comma.
    """
    def split(spec):
        parts = []
        for chunk in spec.replace(os.pathsep, ",").split(","):
            chunk = chunk.strip()
            if chunk:
                parts.append(chunk)
        return parts

    if explicit:
        cands = split(explicit)
        return [c for c in cands if os.path.exists(c)], cands
    env = os.environ.get("S1_AI_USE_LOG", "").strip()
    if env:
        cands = split(env)
        return [c for c in cands if os.path.exists(c)], cands
    cands = [f for f in tracked_files() if LOG_NAME_RE.search(os.path.basename(f))]
    return [c for c in cands if os.path.exists(c)], cands


def normalise(tok):
    tok = tok.strip().strip("`'\"(),;:[]")
    tok = tok.replace("\\", "/")
    while tok.startswith("./"):
        tok = tok[2:]
    return tok


def extract_paths(text):
    """Every path-like token in the log, with its 1-based line number."""
    found = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for m in TOKEN_RE.finditer(line):
            tok = normalise(m.group(0))
            if tok and PATHY_RE.search(tok):
                found.append((lineno, tok))
    return found


def matches_core(tok, patterns):
    """Match the token, and every path-component suffix of it, against the core.

    The suffix sweep catches a core path that arrives with a prefix on it -- a
    pasted diff's `a/silentgate/cli.py`, a repo-qualified
    `sts-electrocatalyst/silentgate/census.py`, an absolute path. Whole-token
    comparison alone lets all three through. Over-matching is the safe direction:
    a false hit fails the assertion loudly, with the offending line printed.
    """
    parts = tok.split("/")
    candidates = ["/".join(parts[i:]) for i in range(len(parts))]
    for cand in candidates:
        for pat in patterns:
            if cand == pat or fnmatch.fnmatchcase(cand, pat):
                return pat
            # A directory pattern such as silentgate/readers/* must also catch
            # the bare directory itself being logged.
            if pat.endswith("/*") and cand in (pat[:-2], pat[:-1]):
                return pat
    return None


def main():
    ap = argparse.ArgumentParser(description="A9.1 disjointness assertion")
    ap.add_argument("--log", default=None, help="path to the AI-use log")
    ap.add_argument("--core-paths", default=DEFAULT_CORE_PATHS)
    ap.add_argument("--json", default=None, help="write a machine-readable result here")
    args = ap.parse_args()

    patterns = load_core_patterns(args.core_paths)
    logs, candidates = find_logs(args.log)
    log_path = logs[0] if logs else None

    result = {
        "assertion": "ai_use_log_file_list INTERSECT core_path_list == EMPTY",
        "registered_at": "docs/43-prereg-week1-factorial.md:1840",
        "core_patterns": patterns,
        "log_path": log_path,
        "log_paths": logs,
        "status": None,
        "violations": [],
        "n_paths_in_log": 0,
    }

    def emit(rc):
        if args.json:
            with open(args.json, "w", encoding="utf-8") as fh:
                json.dump(result, fh, indent=1)
        return rc

    if not logs:
        result["status"] = "FAIL"
        result["reason"] = "AI-use log not found"
        print("DISJOINTNESS: FAIL -- AI-use log not found.")
        print("")
        print("  The log's PATH IS NOT REGISTERED. docs/43 names the log as an obligation")
        print("  at :1322, :1443, :1445, :1828 and :1840 and never gives it a path.")
        print("  Electing one is the entrant's call, so CI does not elect it -- and does")
        print("  not pass without it: an absent log leaves the log's file list UNDEFINED,")
        print("  not empty, and a vacuous pass would make this check strongest exactly")
        print("  when nobody is logging.")
        print("")
        print("  To clear: create the log, then either set $S1_AI_USE_LOG or give it a")
        print("  filename matching /ai[-_]?use|ai[-_]?log|use[-_]?log/ so it is found.")
        if candidates:
            print("  Searched: %s" % ", ".join(candidates[:10]))
        else:
            print("  Searched the tracked tree; no candidate filename matched.")
        return emit(1)

    total = 0
    for lp in logs:
        try:
            with open(lp, "r", encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError as exc:
            result["status"] = "FAIL"
            result["reason"] = "AI-use log unreadable: %s" % exc
            print("DISJOINTNESS: FAIL -- AI-use log %s is unreadable (%s)." % (lp, exc))
            return emit(1)
        paths = extract_paths(text)
        total += len(paths)
        for lineno, tok in paths:
            pat = matches_core(tok, patterns)
            if pat:
                result["violations"].append(
                    {"file": lp, "line": lineno, "path": tok, "pattern": pat}
                )
    result["n_paths_in_log"] = total

    if result["violations"]:
        result["status"] = "FAIL"
        print(
            "DISJOINTNESS: FAIL -- %d core path(s) appear in the AI-use log"
            % len(result["violations"])
        )
        print("")
        for v in result["violations"]:
            print(
                "  %s:%d  %s   (matches core pattern %s)"
                % (v["file"], v["line"], v["path"], v["pattern"])
            )
        print("")
        print("  Registered: the core is 'written and committed only by the entrant'")
        print("  (docs/43:1840). A core path logged as AI-produced contradicts that.")
        return emit(1)

    if total == 0:
        # A log that exists but names no file leaves the file list EMPTY-BY-
        # ACCIDENT, which is indistinguishable from nobody having logged
        # anything. :1840 attaches the duty "each logged in the AI-use log as
        # produced" -- a log with no entries has not discharged it, and passing
        # here would be the same vacuous pass a MISSING log is refused for.
        result["status"] = "FAIL"
        result["reason"] = "AI-use log names no files"
        print("DISJOINTNESS: FAIL -- %s contains no path-like token."
              % ", ".join(logs))
        print("")
        print("  An empty file list is not a disjoint file list. :1840 requires that")
        print("  each permitted artefact be 'logged in the AI-use log as produced',")
        print("  and a log naming nothing has not discharged that -- passing here")
        print("  would be exactly the vacuous pass a MISSING log is refused for.")
        return emit(1)

    result["status"] = "PASS"
    print(
        "DISJOINTNESS: PASS -- %s declare%s %d path token(s); none is a core path."
        % (", ".join(logs), "" if len(logs) > 1 else "s", total)
    )
    print("  Proves only: every file AI logged is outside the core. It cannot detect")
    print("  undeclared authorship, and no output may claim that it can.")
    return emit(0)


if __name__ == "__main__":
    sys.exit(main())
