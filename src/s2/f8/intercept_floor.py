"""Residual uses of the Divanis 3.18 +/- 0.12 eV intercept and the ~0.12 V code floor.

Dispositions under test (docs/43 :1945, round-2 synthesis :60 and :522):
the intercept is QUALITATIVE (it may be quoted as the paper's value, it anchors
no gate or sigma), and the ~0.12 V code-to-code floor is DEAD.

Every line in the scanned tree that matches ``PATTERNS`` is listed and carries a
class from ``data/intercept_floor_classes.json`` (a per-line entry with a verbatim
fragment, or a whole-file rule). A matching line with no class is counted as
UNCLASSIFIED on the face of the output.
"""
from __future__ import annotations

import fnmatch
import re
from collections import Counter
from pathlib import Path

from .common import read_lines, rel, REPO

PATTERNS = {
    "intercept_3.18": re.compile(r"3\.18(?!\d)"),
    # a 0.12 V/eV value, alone or as the lower end of a range ("0.12-0.30 V"), 120 mV,
    # or the floor named in words ("code-level floor", "irreducible band")
    "value_0.12": re.compile(r"±\s?0\.12(?!\d)|"
                             r"(?<![\d.])0\.12(?:\s*[-–—]\s*\d*\.?\d+)?\s*(?:V|eV)\b|"
                             r"(?<![\d.])120\s*mV\b|"
                             r"code[- ](?:to[- ]code |level )?floor|"
                             r"irreducible (?:code[- ]level )?(?:floor|band)"),
}

SCAN = [("docs", (".md", ".txt", ".json")), ("tasks", (".md", ".json", ".txt")),
        ("src", (".py",)), ("tests", (".py",))]
EXTRA_FILES = ["README.md", "CLAUDE.md"]
QUANTITATIVE = {"FROZEN_DEPOSITED_QUANTITATIVE", "ARCHIVE_COPY_QUANTITATIVE",
                "DATED_RECORD_QUANTITATIVE", "LIVE_QUANTITATIVE", "REGISTERED_OPTION_QUANTITATIVE"}


def scan_files(root: Path = REPO) -> list[Path]:
    out = []
    for d, exts in SCAN:
        for p in sorted((root / d).rglob("*")):
            if p.is_file() and p.suffix in exts and "s2" not in p.relative_to(root).parts \
                    and "__pycache__" not in p.parts:
                out.append(p)
    out += [root / f for f in EXTRA_FILES if (root / f).exists()]
    return out


def hits(paths: list[Path], root: Path = REPO) -> list[dict]:
    rows = []
    for p in paths:
        for i, t in enumerate(read_lines(p), 1):
            kinds = [k for k, rx in PATTERNS.items() if rx.search(t)]
            if kinds:
                first = min((rx.search(t).start() for k, rx in PATTERNS.items() if rx.search(t)))
                rows.append({"file": rel(p, root), "line": i, "patterns": kinds,
                             "excerpt": t[max(0, first - 200):first + 200]})
    return rows


SWEEP = re.compile(r"(?<![\d.])0\.12(?!\d)")


def sweep(paths: list[Path], root: Path = REPO) -> list[dict]:
    """Lines holding a bare 0.12 that no census pattern matches (units other than V/eV,
    table cells, file names). Listed unclassified so the pattern's reach can be audited."""
    rows = []
    for p in paths:
        for i, t in enumerate(read_lines(p), 1):
            m = SWEEP.search(t)
            if m and not any(rx.search(t) for rx in PATTERNS.values()):
                rows.append({"file": rel(p, root), "line": i, "excerpt": t[max(0, m.start() - 120):m.end() + 60]})
    return rows


def classify(rows: list[dict], classes: dict, root: Path = REPO) -> list[dict]:
    per_line = classes["lines"]
    per_file = classes["files"]
    out = []
    for r in rows:
        c = None
        for rule in per_file:
            if fnmatch.fnmatch(r["file"], rule["glob"]):
                c = {"class": rule["class"], "note": rule.get("note", ""), "rule": "file:" + rule["glob"]}
                break
        if c is None:
            for rule in per_line:
                if rule["file"] == r["file"] and rule["line"] == r["line"]:
                    text = read_lines(root / r["file"])[r["line"] - 1]
                    ok = rule["fragment"] in text
                    c = {"class": rule["class"] if ok else "FRAGMENT_MISMATCH",
                         "note": rule.get("note", ""), "rule": "line", "fragment": rule["fragment"]}
                    break
        if c is None:
            c = {"class": "UNCLASSIFIED", "note": "", "rule": ""}
        out.append({**r, **c, "quantitative_use": c["class"] in QUANTITATIVE})
    return out


def summarise(rows: list[dict]) -> dict:
    by_class = Counter(r["class"] for r in rows)
    by_class_pattern = Counter((r["class"], p) for r in rows for p in r["patterns"])
    quant = [r for r in rows if r["quantitative_use"]]
    return {"n_matching_lines": len(rows), "n_files": len({r["file"] for r in rows}),
            "by_class": dict(sorted(by_class.items())),
            "by_class_and_pattern": {f"{c}|{p}": n for (c, p), n in sorted(by_class_pattern.items())},
            "n_quantitative_lines": len(quant),
            "n_unclassified": by_class.get("UNCLASSIFIED", 0) + by_class.get("FRAGMENT_MISMATCH", 0)}
