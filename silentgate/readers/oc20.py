"""Read OC20 extended-XYZ trajectories using explicit tags and constraints.

Indices are one-based. Invalid input is never a negative control: scorable is
false and issues explains why. No near-zero tolerance is applied.
AI implementation authorized 2026-09-13.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
import lzma
import math
from pathlib import Path
import shlex


def _properties(header):
    values = [part.split("=", 1)[1] for part in shlex.split(header)
              if part.startswith("Properties=")]
    if len(values) != 1:
        raise ValueError("frame must have exactly one Properties declaration")
    tokens = values[0].split(":")
    if len(tokens) % 3:
        raise ValueError("malformed Properties declaration")
    fields, offset = {}, 0
    for name, kind, count in zip(tokens[::3], tokens[1::3], tokens[2::3]):
        width = int(count)
        if not name or name in fields or width < 1 or kind not in {"S", "R", "I", "L"}:
            raise ValueError("invalid or duplicate property: " + name)
        fields[name] = (offset, width, kind)
        offset += width
    for name, width, kind in [("species", 1, "S"), ("pos", 3, "R"),
                              ("move_mask", 1, "L"), ("tags", 1, "I"),
                              ("forces", 3, "R")]:
        if name not in fields or fields[name][1:] != (width, kind):
            raise ValueError("missing or incompatible property: " + name)
    return fields, offset


def _real(token):
    # Float underflow must not invent exact zeros from nonzero decimal text.
    value = float(token)
    decimal = Decimal(token)
    if not math.isfinite(value) or not decimal.is_finite():
        raise ValueError("nonfinite real value")
    if value == 0.0 and decimal != 0:
        raise ValueError("nonzero real value underflows float precision")
    return value


def _logical(token):
    if token in {"T", "True", "true", "1"}:
        return True
    if token in {"F", "False", "false", "0"}:
        return False
    raise ValueError("invalid move_mask logical: " + token)


def read_oc20(path):
    """Return validated force steps, tag/mask selection and diagnostics.

    per_step_exact_zero_count sums components across all unconstrained atoms
    and all complete frames. On any issue the counts are partial diagnostics.
    """
    result = {
        "path": str(path), "force_steps": [], "adsorbate_indices": [],
        "n_if_pos_excluded": 0, "n_adsorbate_excluded": 0,
        "excluded_adsorbate_indices": [],
        "unidentified": False, "n_symops": None, "header_form": "force-only",
        "per_step_exact_zero_count": 0, "per_step_exact_zero_counts": [],
        "issues": [], "scorable": False,
    }
    reference = None
    frame_number = 0
    try:
        opener = lzma.open if Path(path).suffix.lower() == ".xz" else open
        with opener(path, "rt", encoding="utf-8") as handle:
            while True:
                line = handle.readline()
                if not line:
                    break
                if not line.strip():
                    continue
                frame_number += 1
                n_atoms = int(line.strip())
                if n_atoms < 1:
                    raise ValueError("atom count must be positive")
                header = handle.readline()
                if not header:
                    raise ValueError("truncated frame header")
                fields, width = _properties(header)
                atoms, forces, zeros = [], {}, 0
                for index in range(1, n_atoms + 1):
                    row = handle.readline()
                    if not row:
                        raise ValueError("truncated frame at atom %d" % index)
                    parts = row.split()
                    if len(parts) != width:
                        raise ValueError("atom %d has %d fields, expected %d" %
                                         (index, len(parts), width))
                    def field(name):
                        start, count, _kind = fields[name]
                        return parts[start:start + count]
                    species = field("species")[0]
                    tuple(_real(token) for token in field("pos"))
                    movable = _logical(field("move_mask")[0])
                    tag = int(field("tags")[0])
                    force = tuple(_real(token) for token in field("forces"))
                    atoms.append((species, tag, movable))
                    if movable:
                        forces[index] = force
                        zeros += sum(value == 0.0 for value in force)
                if reference is None:
                    reference = atoms
                    result["adsorbate_indices"] = [i for i, (_, tag, movable)
                                                    in enumerate(atoms, 1)
                                                    if tag == 2 and movable]
                    result["excluded_adsorbate_indices"] = [i for i, (_, tag, movable)
                                                             in enumerate(atoms, 1)
                                                             if tag == 2 and not movable]
                    result["n_if_pos_excluded"] = sum(not movable for _, _, movable in atoms)
                    result["n_adsorbate_excluded"] = len(result["excluded_adsorbate_indices"])
                    if not any(tag == 2 for _, tag, _ in atoms):
                        raise ValueError("no adsorbate atoms identified by tags == 2")
                elif atoms != reference:
                    raise ValueError("atom count, species, tags or constraints changed between frames")
                result["force_steps"].append(forces)
                result["per_step_exact_zero_counts"].append(zeros)
                result["per_step_exact_zero_count"] += zeros
        if not result["force_steps"]:
            raise ValueError("no complete force frames")
        if not result["adsorbate_indices"]:
            raise ValueError("no unconstrained adsorbate atoms")
    except (OSError, EOFError, UnicodeError, ValueError, InvalidOperation, lzma.LZMAError) as exc:
        result["issues"].append("OC20 frame %d: %s" % (frame_number, exc))
    result["unidentified"] = bool(result["issues"])
    result["fatal_issues"] = list(result["issues"])
    result["scorable"] = not result["issues"]
    return result
