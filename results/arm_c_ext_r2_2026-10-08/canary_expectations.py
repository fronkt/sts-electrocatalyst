"""What QE should print right after reading each moved density (local; writes canary_expectations.json).

With startingpot = 'file', QE 7.5 prints "negative rho (up, down)" for the density it read (v_of_rho.f90,
v_xc: the valence density on the dense FFT grid, the core charge taken back out). It rescales the density,
with a "renormalised to" line, only if its charge is off by more than 1e-7 of itself (potinit.f90); every
moved density is within 1.2e-5 electrons. So each target's first lines after "The initial density is read
from file" are predictable. The same FFT on round 1's copied seeds reproduces what QE printed then
(6.936E-03 2.243E-02 and 4.593E-03 2.202E-02 after rescaling). The seeds' own values are listed for comparison.
"""
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
import qe_density_move as move  # noqa: E402

SPEC = json.loads((HERE / "launch_spec.json").read_text(encoding="utf-8"))
PLAN = json.loads((HERE / "ext_plan.json").read_text(encoding="utf-8"))


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def start_lines(density_path, xml_path):
    """negative rho (up, down) and the charge of a density file, on the run's dense FFT grid."""
    text = Path(xml_path).read_text()
    grid = [int(x) for x in re.search(r'<fft_grid nr1="(\d+)" nr2="(\d+)" nr3="(\d+)"', text).groups()]
    omega = abs(np.linalg.det(move.read_xml_cell(xml_path)))
    density = move.read_density(density_path)
    index = tuple((density["miller"] % np.array(grid)).T)
    fields = {}
    for name in ("rho", "mag"):
        dense = np.zeros(grid, dtype=np.complex128)
        dense[index] = density[name]
        fields[name] = (np.fft.ifftn(dense) * dense.size).real
        del dense
    dv = omega / fields["rho"].size
    up, down = fields["rho"] + fields["mag"], fields["rho"] - fields["mag"]
    return {"negative_rho_up": float(-up[up < 0].sum() * 0.5 * dv), "negative_rho_down": float(-down[down < 0].sum() * 0.5 * dv),
            "charge": float(fields["rho"].sum() * dv), "fft_grid": grid}


def main():
    jobs = {(j["dir"], j["job"]): j for j in SPEC["stages"]["r2_main"]["jobs"]}
    report = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "targets": {}, "seeds": {}}
    for row in PLAN["selection"]:
        job = jobs[(row["dir"], row["job"])]
        density = ROOT / row["upload"]["charge-density.hdf5"]
        if sha256(density) != job["scratch_source"]["files"]["charge-density.hdf5"]:
            raise SystemExit("moved density differs from its pin: " + str(density))
        seed_folder = HERE / "density_inputs" / row["seed"]["id"]
        xml = seed_folder / "data-file-schema.xml"
        report["targets"][row["job"] + "@" + row["dir"].rsplit("/", 1)[-1]] = dict(start_lines(density, xml), density_sha256=sha256(density))
        if row["seed"]["id"] not in report["seeds"]:
            report["seeds"][row["seed"]["id"]] = start_lines(seed_folder / "charge-density.hdf5", xml)
        print(row["dir"].rsplit("/", 1)[-1], row["job"], {k: round(v, 6) for k, v in report["targets"][row["job"] + "@" + row["dir"].rsplit("/", 1)[-1]].items()
                                                          if k.startswith("negative")}, flush=True)
    with (HERE / "canary_expectations.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
