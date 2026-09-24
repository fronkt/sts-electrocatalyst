"""Fetch selected small members of the Divanis 2020 katlaDB trajectories zip by HTTP Range and
extract them (saved + receipted). Then read the cell / species with ASE for the polymorph check.
"""
import json
import struct
import sys
import pathlib
import zlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from httpfetch import ROOT  # noqa: E402
from s04_erda_range import rng  # noqa: E402  (module-level listing code re-runs; acceptable, small)

LST = json.loads((ROOT / "divanis2020_erda_traj_listing.json").read_text(encoding="utf-8"))
WANT = sys.argv[1:] or [
    "TiO2_double_dopants/2Pt/clean/TiO2-fd.traj",
    "TiO2_double_dopants/2Pt/clean/TiO2-2Pt-3-fd.txt",
]
OUTD = ROOT / "files" / "divanis2020_erda_members"
OUTD.mkdir(parents=True, exist_ok=True)
for w in WANT:
    m = next(x for x in LST["members"] if x["name"] == w)
    st, hdr = rng(m["offset"], m["offset"] + 29, "lh_" + w.replace("/", "_")[-40:])
    nlen, elen = struct.unpack("<HH", hdr[26:30])
    start = m["offset"] + 30 + nlen + elen
    st, data = rng(start, start + m["csize"] - 1, "data_" + w.replace("/", "_")[-40:])
    raw = zlib.decompress(data, -15) if m["method"] == 8 else data
    p = OUTD / w.replace("/", "__")
    p.write_bytes(raw)
    print(w, m["method"], len(raw), p)
