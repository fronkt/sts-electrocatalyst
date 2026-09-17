"""Validate completed QE projections with spin and nonmagnetic Lowdin layouts.

QE 7.5 nonmagnetic output repeats each atom's total on separate s/p/d rows.
Those rows are one atom group, not duplicate atoms. Spin output commonly uses
one combined row. Coverage, totals, channel completeness and all numerical
failure checks remain strict; no scientific threshold is set here.
"""
from __future__ import annotations

from itertools import groupby
import math
import re

NUM = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][+-]?\d+)?"
FAIL = re.compile(r"convergence NOT achieved|Maximum (?:CPU|wall) time exceeded|"
                  r"Program stopped by user request|Error in routine|MPI_ABORT|"
                  r"SIGTERM|SIGINT|SIGSEGV|Segmentation fault|Floating point exception|"
                  r"IEEE_INVALID_FLAG|IEEE_OVERFLOW_FLAG|IEEE_DIVIDE_BY_ZERO|forrtl:\s*severe", re.I)


def number(token: str) -> float:
    if re.fullmatch(NUM, token) is None:
        raise ValueError("malformed projection value")
    value = float(token.replace("D", "e").replace("d", "e"))
    if not math.isfinite(value):
        raise ValueError("nonfinite projection value")
    return value


def projection_check(text: str, nat: int) -> dict:
    """Return validated atom-group metadata; raise on incomplete or bad output."""
    if type(nat) is not int or nat < 1:
        raise ValueError("invalid projection atom count")
    if (FAIL.search(text) or text.count("JOB DONE") != 1 or text.count("Lowdin Charges") != 1
            or re.search(r"\b(?:NaN|Inf(?:inity)?)\b", text, re.I)):
        raise ValueError("incomplete/failed projection")
    ieee = set(re.findall(r"\bIEEE_[A-Za-z0-9_]+\b", text))
    if ieee - {"IEEE_UNDERFLOW_FLAG", "IEEE_DENORMAL", "IEEE_INEXACT_FLAG"}:
        raise ValueError("severe or unknown IEEE projection flag")
    spilling = re.findall(r"(?m)^\s*Spilling Parameter:\s*(" + NUM + r")\s*$", text)
    if len(spilling) != 1 or text.count("Spilling Parameter") != 1:
        raise ValueError("missing or repeated spilling parameter")
    if not (text.index("Lowdin Charges") < text.index("Spilling Parameter") < text.index("JOB DONE")):
        raise ValueError("projection completion markers out of order")
    lowdin = text.split("Lowdin Charges", 1)[1].split("Spilling Parameter", 1)[0]
    for token in re.findall(r"=\s*([^,\s]+)", lowdin):
        number(token)
    for token in re.findall(NUM, text):
        number(token)
    rows = re.findall(r"(?m)^\s*Atom\s*#\s*(\d+)\s*:\s*total charge\s*=\s*("
                      + NUM + r")\s*,([^\n]*)", lowdin)
    # Do not let a malformed atom row disappear under the stricter value regex.
    headers = re.findall(r"(?m)^\s*Atom\s*#\s*(\d+)\s*:\s*total charge", lowdin)
    if len(rows) != len(headers):
        raise ValueError("malformed atom charge row")
    groups = [(atom, list(items)) for atom, items in groupby(rows, key=lambda row: int(row[0]))]
    if [atom for atom, _ in groups] != list(range(1, nat + 1)):
        raise ValueError("incomplete, repeated or out-of-order atom groups")
    angular = [int(n) for n in re.findall(r"state\s*#\s*\d+:[^\n]*\(l\s*=\s*(\d+)", text)]
    expected_channels = list("spdf"[:max(angular) + 1]) if angular and max(angular) <= 3 else None
    split_format = any(len(items) > 1 for _, items in groups)
    records = []
    for atom, items in groups:
        totals = [number(row[1]) for row in items]
        if len(set(totals)) != 1:
            raise ValueError("inconsistent repeated total charge")
        if split_format:
            channels = []
            for _, _, tail in items:
                channel = re.match(r"\s*([spdf])\s*=", tail)
                if channel is None:
                    raise ValueError("repeated atom row is not an angular channel")
                channels.append(channel[1])
            if expected_channels is None or channels != expected_channels:
                raise ValueError("missing, duplicate or out-of-order angular channel")
        elif expected_channels is not None:
            channels = re.findall(r"(?:^|,)\s*([spdf])\s*=", items[0][2])
            if channels != expected_channels:
                raise ValueError("incomplete combined angular channels")
        records.append({"atom": atom, "total_charge": totals[0], "rows": len(items)})
    return {"status": "VALID_PROJECTION", "nat": nat, "charge_rows": len(rows),
            "atom_groups": records, "spilling_parameter": number(spilling[0]),
            "format": "split-angular-channels" if split_format else "combined"}
