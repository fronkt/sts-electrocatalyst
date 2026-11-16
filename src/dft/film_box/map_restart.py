"""Build a startingpot='file' restart for an adslab from a converged slab save (amendment 9).

QE's read_scf needs, besides charge-density.hdf5, the per-atom files occup.txt (Hubbard ns,
shape (5, 5, nspin, nat)) and paw.txt (PAW becsum, shape (nij, nat, nspin)), both list-directed
in Fortran order. The slab and the adslab have different atom lists, so each adslab atom is
matched to the nearest slab atom of the same element (minimum image); the adsorbate atoms that
have no partner get ns = 0 (no U on O/H) and the becsum of the top-surface hydroxyl O / H.
Only the starting guess changes: the SCF solution is set by the adslab input.

  python3 map_restart.py SLAB_IN SLAB_OUT SLAB_SAVE ADSLAB_IN DEST_SAVE
"""
import re
import sys


def numbers(path):
    return [float(x.replace("D", "E").replace("d", "e")) for x in open(path).read().split()]


def cell(text):
    m = re.search(r"CELL_PARAMETERS\s+angstrom\s*\n((?:.*\n){3})", text)
    return [[float(v) for v in ln.split()[:3]] for ln in m.group(1).splitlines()]


def positions(text, nat, last=False):
    blocks = list(re.finditer(r"ATOMIC_POSITIONS\s*\(?angstrom\)?\s*\n", text))
    b = blocks[-1] if last else blocks[0]
    lines = text[b.end():].splitlines()[:nat]
    return [(ln.split()[0], [float(v) for v in ln.split()[1:4]]) for ln in lines]


def inv3(a):
    (a0, a1, a2), (b0, b1, b2), (c0, c1, c2) = a
    det = a0 * (b1 * c2 - b2 * c1) - a1 * (b0 * c2 - b2 * c0) + a2 * (b0 * c1 - b1 * c0)
    return [[(b1 * c2 - b2 * c1) / det, (a2 * c1 - a1 * c2) / det, (a1 * b2 - a2 * b1) / det],
            [(b2 * c0 - b0 * c2) / det, (a0 * c2 - a2 * c0) / det, (a2 * b0 - a0 * b2) / det],
            [(b0 * c1 - b1 * c0) / det, (a1 * c0 - a0 * c1) / det, (a0 * b1 - a1 * b0) / det]]


def main(slab_in, slab_out, slab_save, ads_in, dest):
    s_in, s_out, a_in = open(slab_in).read(), open(slab_out).read(), open(ads_in).read()
    lat = cell(a_in)
    assert lat == cell(s_in), "slab and adslab cells differ"
    ns_nat = int(re.search(r"nat\s*=\s*(\d+)", s_in).group(1))
    na_nat = int(re.search(r"nat\s*=\s*(\d+)", a_in).group(1))
    slab = positions(s_out, ns_nat, last=True)
    ads = positions(a_in, na_nat)
    ilat = inv3(lat)  # rows of lat are lattice vectors: r = f @ lat, so f = r @ inv(lat)

    def dist(p, q):
        d = [p[k] - q[k] for k in range(3)]
        f = [sum(d[i] * ilat[i][j] for i in range(3)) for j in range(3)]
        f = [x - round(x) for x in f]
        r = [sum(f[i] * lat[i][j] for i in range(3)) for j in range(3)]
        return sum(x * x for x in r) ** 0.5

    el = lambda s: re.sub(r"\d+$", "", s)
    pairs = sorted((dist(pa, ps), i, j) for i, (sa, pa) in enumerate(ads)
                   for j, (ss, ps) in enumerate(slab) if el(sa) == el(ss))
    amap, used = {}, set()
    for d, i, j in pairs:
        if i not in amap and j not in used:
            amap[i] = (j, d)
            used.add(j)
    # each adslab atom has a partner unless it is one of the na_nat - ns_nat extra atoms
    extra = [i for i in range(na_nat) if i not in amap]
    assert len(extra) == na_nat - ns_nat, (extra, na_nat, ns_nat)
    far = sorted(((d, i) for i, (j, d) in amap.items()), reverse=True)[:3]
    print("mapped", len(amap), "max d (A):", " ".join("%d:%.3f" % (i + 1, d) for d, i in far))
    # top-surface hydroxyl O of the slab and its H, as stand-ins for the adsorbate O and H
    hs = [j for j, (s, _) in enumerate(slab) if el(s) == "H"]
    ohs = [(slab[j][1][2], j, min(hs, key=lambda h: dist(slab[j][1], slab[h][1])))
           for j, (s, p) in enumerate(slab) if el(s) == "O"
           and min(dist(p, slab[h][1]) for h in hs) < 1.15]
    _, o_top, h_top = max(ohs)
    stand = {"O": o_top, "H": h_top}
    for i in extra:
        amap[i] = (stand[el(ads[i][0])], None)
        print("extra atom %d %s -> slab atom %d" % (i + 1, ads[i][0], amap[i][0] + 1))
    for i, (j, d) in sorted(amap.items()):
        if d is not None:
            assert d < 0.6, ("atom %d maps %.2f A away" % (i + 1, d))

    ns = numbers(slab_save + "/occup.txt")
    nspin = 2
    assert len(ns) == 25 * nspin * ns_nat, len(ns)
    bec = numbers(slab_save + "/paw.txt")
    nij = len(bec) // (ns_nat * nspin)
    assert nij * ns_nat * nspin == len(bec)
    blk = 25 * nspin
    ns_new, bec_new = [], []
    for i in range(na_nat):
        j, d = amap[i]
        ns_new += [0.0] * blk if d is None else ns[blk * j: blk * (j + 1)]
    for s in range(nspin):
        for i in range(na_nat):
            j = amap[i][0]
            off = nij * (j + ns_nat * s)
            bec_new += bec[off: off + nij]
    # the slab's O/H ns blocks must be zero (no U on them), else the zero fill is wrong
    for j, (s, _) in enumerate(slab):
        if el(s) in ("O", "H"):
            assert not any(ns[blk * j: blk * (j + 1)]), "nonzero ns on slab atom %d" % (j + 1)
    for name, arr in (("occup.txt", ns_new), ("paw.txt", bec_new)):
        with open(dest + "/" + name, "w") as fh:
            for k in range(0, len(arr), 4):
                fh.write(" ".join("%.17E" % x for x in arr[k:k + 4]) + "\n")
        print(name, len(arr))


if __name__ == "__main__":
    main(*sys.argv[1:6])
