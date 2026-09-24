"""Divanis 2020 (T04): read the author-deposited katlaDB 'trajectories' archive (3.5 GB zip, linked
from the article's own Conclusions / katlaDB entry) with HTTP Range requests only: fetch the zip
central directory, list members, then fetch a few small doped-TiO2 structure files to read the
cell. No full download. Every range response is saved and receipted.
"""
import io
import json
import struct
import sys
import pathlib
import zipfile
import zlib
import datetime
import hashlib

import requests

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from httpfetch import ROOT, UA, _append  # noqa: E402

URL = "https://sid.erda.dk/share_redirect/aXxuVfZEfX"
OUT = ROOT / "files" / "divanis2020_erda_traj_ranges"
OUT.mkdir(parents=True, exist_ok=True)


def rng(a, b, tag):
    t = datetime.datetime.now(datetime.timezone.utc).isoformat()
    r = requests.get(URL, headers={"User-Agent": UA, "Range": f"bytes={a}-{b}"}, timeout=120)
    body = r.content
    sha = hashlib.sha256(body).hexdigest()
    p = OUT / f"{tag}__{a}-{b}__{sha[:12]}.bin"
    p.write_bytes(body)
    _append({"label": f"divanis2020_erda_traj_range_{tag}", "request_url": URL, "range": f"{a}-{b}",
             "requested_utc": t, "status": r.status_code, "bytes": len(body), "sha256": sha,
             "local_path": str(p.relative_to(ROOT.parents[2])).replace("\\", "/")})
    return r.status_code, body


def main():
    size = int(requests.head(URL, headers={"User-Agent": UA}, allow_redirects=True, timeout=60).headers["Content-Length"])
    st, tail = rng(size - 65536, size - 1, "tail")
    i = tail.rfind(b"PK\x05\x06")
    cd_size, cd_off = struct.unpack("<II", tail[i + 12:i + 20])
    if cd_off == 0xFFFFFFFF:  # zip64
        j = tail.rfind(b"PK\x06\x06")
        cd_size, cd_off = struct.unpack("<QQ", tail[j + 40:j + 56])
    st, cd = rng(cd_off, cd_off + cd_size - 1, "central_directory")
    names = []
    p = 0
    while p < len(cd) and cd[p:p + 4] == b"PK\x01\x02":
        (comp, csz, usz, nlen, elen, clen) = struct.unpack("<HII" + "HHH", cd[p + 10:p + 12] + cd[p + 20:p + 28] + cd[p + 28:p + 34])
        lho = struct.unpack("<I", cd[p + 42:p + 46])[0]
        name = cd[p + 46:p + 46 + nlen].decode("utf-8", "replace")
        extra = cd[p + 46 + nlen:p + 46 + nlen + elen]
        # zip64 extra
        q = 0
        while q + 4 <= len(extra):
            hid, hl = struct.unpack("<HH", extra[q:q + 4])
            if hid == 1:
                vals = extra[q + 4:q + 4 + hl]
                k = 0
                if usz == 0xFFFFFFFF:
                    usz = struct.unpack("<Q", vals[k:k + 8])[0]; k += 8
                if csz == 0xFFFFFFFF:
                    csz = struct.unpack("<Q", vals[k:k + 8])[0]; k += 8
                if lho == 0xFFFFFFFF:
                    lho = struct.unpack("<Q", vals[k:k + 8])[0]; k += 8
            q += 4 + hl
        names.append({"name": name, "method": comp, "csize": csz, "usize": usz, "offset": lho})
        p += 46 + nlen + elen + clen
    (ROOT / "divanis2020_erda_traj_listing.json").write_text(json.dumps({"url": URL, "size": size, "n": len(names), "members": names}, indent=0), encoding="utf-8")
    print("members", len(names))
    for n in names[:40]:
        print(n["name"], n["usize"])


if __name__ == "__main__":
    main()
