"""Count/finite-coordinate gate for the explicitly authorized S26411 check.

No phase, facet or eligibility inference. An incomplete POSCAR cannot be
reconstructed by assuming missing atoms, repeating cells or copying a parent.
"""
import hashlib
import json
import math
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent


def inspect_block(block):
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    if len(lines) < 8:
        raise ValueError("Incomplete POSCAR header")
    scale = float(lines[1])
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError("Expected positive finite scale")
    lattice = [[float(x) for x in line.split()] for line in lines[2:5]]
    if any(len(row) != 3 or not all(math.isfinite(x) for x in row) for row in lattice):
        raise ValueError("Invalid lattice")
    a, b, c = lattice
    determinant = sum(a[i] * (b[(i+1)%3] * c[(i+2)%3] - b[(i+2)%3] * c[(i+1)%3]) for i in range(3))
    if abs(determinant) < 1e-9:
        raise ValueError("Singular lattice")
    species = lines[5].split()
    counts = [int(x) for x in lines[6].split()]
    if len(species) != len(counts) or not counts or any(x <= 0 for x in counts):
        raise ValueError("Invalid species/count header")
    start = 7
    if lines[start].lower().startswith("s"):
        start += 1
    mode = lines[start].lower()
    if not mode.startswith(("cartesian", "direct")):
        raise ValueError("Unknown coordinate convention")
    coordinates = []
    for line in lines[start+1:]:
        parts = line.split()
        if len(parts) < 3:
            raise ValueError("Incomplete coordinate row")
        xyz = [float(x) for x in parts[:3]]
        if not all(math.isfinite(x) for x in xyz):
            raise ValueError("Nonfinite coordinate")
        coordinates.append(xyz)
    expected = sum(counts)
    complete = len(coordinates) == expected
    return {"header": lines[0], "species": species, "declared_counts": counts,
            "declared_atoms": expected, "coordinate_rows": len(coordinates),
            "coordinate_convention": lines[start], "lattice": lattice, "scale": scale,
            "complete": complete, "missing_coordinate_rows": max(0, expected-len(coordinates)),
            "identity_check": "READY_FOR_STRUCTURAL_REVIEW" if complete else "REFUSED_INCOMPLETE_COORDINATES"}


def inspect_source(path):
    raw = path.read_bytes()
    blocks = [part for part in re.split(r"\n\s*\n(?:\s*\n)*", raw.decode("utf-8").replace("\r\n", "\n")) if part.strip()]
    results = [inspect_block(block) for block in blocks]
    return {"screen_id": "S26411", "source": path.relative_to(HERE).as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), "blocks": results,
            "all_blocks_complete": bool(results) and all(row["complete"] for row in results),
            "phase_assigned": False, "facet_reconstructed": False, "missing_atoms_imputed": False,
            "scientific_effect": "No automated scientific ruling; reconciliation retains uncertainty if identity cannot be established."}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    result = inspect_source(HERE / "files_si" / "S26411_SI3.txt")
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
