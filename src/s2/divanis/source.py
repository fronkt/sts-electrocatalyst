"""Re-select the registered rows from the pinned raw ESI text, then check identities."""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DEFAULT_SELECTION = REPO / "results/research_decisions_2026-09-16/divanis_selection.json"
SOURCE_SHA256 = "88bfcda9a5e70da10d3b2565af7cc09b7377578e4aac4dd5d9a74b42c0bd8bda"
NUM = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
ROW_RE = re.compile(rf"^\s*(\d+)\s+([A-Z][a-z]?O2b?)\s+({NUM})\s+({NUM})\s+({NUM})\s+({NUM})\s*$")
ARTICLE_NAMES = {1: "Man 2011", 7: "Mom 2014", 9: "Frydendal 2015"}


@dataclass(frozen=True)
class Row:
    row_id: str
    source_line: int
    article_id: int
    structure_token: str
    energies: tuple[Fraction, Fraction, Fraction, Fraction]
    energy_tokens: tuple[str, str, str, str]
    source_row: str


def parse_rows(text: str, first: int = 106, last: int = 644) -> list[Row]:
    """No article whitelist, energy filter or deduplication participates in selection."""
    rows = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not first <= line_number <= last:
            continue
        m = ROW_RE.fullmatch(line)
        if m:
            article, token, *energies = m.groups()
            rows.append(Row(f"divanis-si2-L{line_number}", line_number, int(article), token,
                            tuple(Fraction(x) for x in energies), tuple(energies), " ".join(line.split())))
    return rows


def load_population(selection_path: Path = DEFAULT_SELECTION, source_path: Path | None = None,
                    repo: Path = REPO) -> tuple[list[Row], dict]:
    selection_path = Path(selection_path)
    manifest_bytes = selection_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    source_path = Path(source_path) if source_path else repo / manifest["source"]["path"]
    raw = source_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SOURCE_SHA256 or digest != manifest["source"]["sha256"]:
        raise ValueError("raw Divanis ESI source hash does not match the frozen identity")
    if manifest["source"]["table"] != "SI-2" or manifest["source"]["line_range"] != [106, 644]:
        raise ValueError("selection manifest changed the frozen table bounds")
    pred = manifest["predicate"]
    if (pred["structure_token_regex"] != "^[A-Z][a-z]?O2b?$" or pred["row_token_count"] != 6 or
            pred["article_filter"] is not None or pred["energy_filter"] is not None or pred["deduplicate"]):
        raise ValueError("selection manifest changed the frozen selection predicate")
    rows = parse_rows(raw.decode("utf-8"))
    expected = manifest["rows"]
    if len(rows) != 38 or manifest["denominator"] != 38 or len(expected) != 38:
        raise ValueError("the frozen population requires all 38 source identities")
    for row, record in zip(rows, expected):
        actual = (row.row_id, row.source_line, row.article_id, row.structure_token, row.source_row)
        wanted = (record["row_id"], record["source_line"], record["article_id"], record["structure_token"],
                  " ".join(record["source_row"].split()))
        if actual != wanted:
            raise ValueError(f"selection identity mismatch at {row.row_id}")
        if row.energies[3] != Fraction("4.92"):
            raise ValueError(f"unexpected total-cycle source column at {row.row_id}")
    counts = {str(k): v for k, v in sorted(Counter(r.article_id for r in rows).items())}
    if counts != {"1": 26, "7": 11, "9": 1} or counts != manifest["per_article_counts"]:
        raise ValueError("selected article composition differs from the frozen 26/11/1")
    return rows, {
        "source_path": str(source_path), "source_sha256": digest,
        "selection_path": str(selection_path),
        "selection_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "denominator": 38, "article_denominators": counts,
        "independent_raw_reselection_matches_manifest": True,
        "interpretation_limits": manifest["interpretation_limits"],
    }
