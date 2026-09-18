"""Shared paths, hashing and JSON helpers for the low-tail DFT validation track.

Unit conversions are the values of record in src/dft/hea_force_audit.py:16-17 (the
parser that accepted every banked HEA single point); they are re-read from that file
at import so a drift between the two modules is an error rather than a silent change.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

_FORCE_AUDIT = ROOT / "src" / "dft" / "hea_force_audit.py"


def _constant(name: str) -> float:
    text = _FORCE_AUDIT.read_text(encoding="utf-8")
    match = re.search(rf"^{name}\s*=\s*([0-9.eE+-]+)\s*$", text, re.M)
    if match is None:
        raise RuntimeError(f"{name} not found in {_FORCE_AUDIT}")
    return float(match.group(1))


RY_TO_EV = _constant("RY_TO_EV")
RY_BOHR_TO_EV_A = _constant("RY_BOHR_TO_EV_A")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def rel(path) -> str:
    path = Path(path).resolve()
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def evidence(path) -> dict:
    path = Path(path)
    data = path.read_bytes()
    return dict(path=rel(path), sha256=sha256_bytes(data), bytes=len(data))


def read_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def finite_tree(obj) -> None:
    """Refuse NaN/inf anywhere in a JSON-bound tree."""
    if isinstance(obj, float) and not math.isfinite(obj):
        raise ValueError("nonfinite value in output tree")
    if isinstance(obj, dict):
        for value in obj.values():
            finite_tree(value)
    elif isinstance(obj, (list, tuple)):
        for value in obj:
            finite_tree(value)


def write_json(path, obj) -> str:
    """LF-terminated, deterministic key order as supplied; returns sha256 of the bytes."""
    finite_tree(obj)
    text = json.dumps(obj, indent=2, allow_nan=False) + "\n"
    data = text.encode("utf-8")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(data)
    return sha256_bytes(data)


def write_text_lf(path, text: str, *, refuse_different: bool = False) -> str:
    if "\r" in text:
        raise ValueError(f"{path}: refusing CR bytes")
    data = text.encode("utf-8")
    path = Path(path)
    if refuse_different and path.exists() and path.read_bytes() != data:
        raise ValueError(f"{path} exists with different bytes; refusing to overwrite")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(data)
    return sha256_bytes(data)


def md5_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()
