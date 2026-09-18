"""The 2026-09-16 operating decision for P-BUILDER as data (mirrors p-builder.md).

X (per family) is the HELD threshold on the retention rate of the upright adsorbates *O
and *OH (docs/43 :1902 operational definition). F is the falsification line: a rate at or
below F means the enumerator does not place a majority of upright configurations on a
force-zeroing element, i.e. the docs/43 :1923 FALSIFIED scope ("site selection is not a
propagation mechanism"). A rate strictly between F and X is reported as NOT HELD /
NOT FALSIFIED. Bent *OOH and the *O = *OH identity are construction checks, not
predictions: a violation voids that family's rows until explained.
"""
from __future__ import annotations

from fractions import Fraction

DATE = "2026-09-16"
F_LINE = Fraction(1, 2)

# Predicted retained count k of N for *O and *OH, per family, from the site-type argument
# in p-builder.md. N is read from the prestate denominators; k is the argument's minimum.
PREDICTED_MIN_RETAINED = {
    "rutile110": 9,      # non-blind: the disclosed 2026-08-15 count (docs/43 :1902)
    "perovskite001": 5,  # every enumerated site is a 4mm / 2mm / m position of p4mm
    "spinel001": 8,      # 3 ontop (each atom on one vertical mirror) + >=5 bridges (edge count)
    "fcc111": 4,         # ontop / bridge / fcc / hcp are 3m / m / 3m / 3m positions of p3m1
}

RATIONALE = {
    "rutile110": "non-blind reproduction of the disclosed arm; scored as a reproduction check",
    "perovskite001": "p4mm: ontop Ti (4mm), ontop O (2mm), bridges Ti-O (m), O-O (m), hole centre (4mm); "
                     "right-angle triangles are excluded as hollows by the enumerator",
    "spinel001": "p2mm (Pmm2, 4 ops): every top-layer atom lies on exactly one vertical mirror; 18 Delaunay "
                 "edges per cell in 8 classes of multiplicity 1/2/4 forces >=5 retained bridge classes",
    "fcc111": "p3m1: ontop, fcc and hcp hollows are 3m; the bridge is on a mirror; 12 edges and 8 faces "
              "per 2x2 cell leave no room for a general-position class",
}


# docs/43 :1902 registers the population as family x {*O, *OH, *OOH} and asks for "rate X per
# family" without saying whether the three adsorbates are scored separately or pooled.
READING = dict(
    decision="per adsorbate: X and the verdict apply to *O and to *OH separately (each over the N "
             "configurations of one adsorbate); bent *OOH is a construction check with expected rate 0",
    alternative_named="pooled: one rate per family over all 3N configurations of *O, *OH and *OOH",
    reason="the bent *OOH geometry retains no operation on any of the four cells by construction (OOH_bound), "
           "so pooling fixes one third of the population at zero through the chosen adsorbate geometry, not "
           "through site selection; the pooled rate is then (2/3) x the upright rate and a 1/2 line on it would "
           "falsify any family whose upright rate is at or below 3/4",
    pooled_rate_reporting="computed and reported next to the per-adsorbate rates, with no verdict",
)


def pooled_counterpart(k: int, n: int) -> dict:
    """What the pooled reading gives at the predicted minimum (k of N for *O and *OH, 0 for *OOH)."""
    rate = Fraction(2 * k, 3 * n)
    return dict(fraction=f"{2 * k}/{3 * n}", value=round(float(rate), 6),
                at_or_below_half_line=bool(rate <= F_LINE),
                min_upright_retained_above_half_line_if_pooled=min(
                    (r for r in range(n + 1) if Fraction(2 * r, 3 * n) > F_LINE), default=None))


def verdict(retained: int, n: int, k_pred: int) -> str:
    rate = Fraction(retained, n)
    if retained >= k_pred:
        return "HELD"
    if rate <= F_LINE:
        return "FALSIFIED"
    return "NOT HELD / NOT FALSIFIED"


def ooh_bound(denominators: dict) -> dict:
    """Why bent *OOH cannot retain an adsorbate-invariant operation on these cells.

    A normal-preserving operation R fixing O1 mod lattice moves O2 by R d - d, whose length is at
    most 2|d_lateral(O2)|. If that is shorter than every nonzero in-plane lattice vector, R fixes
    d(O2): R is the identity or the vertical mirror containing the O-O direction. That mirror moves
    H by twice its lateral distance from the O-O line, which is also shorter than every lattice vector.
    """
    import numpy as np
    from .registered import ADSORBATES
    c = np.array(ADSORBATES["OOH"][1], dtype=float)
    d_o2, d_h = c[1] - c[0], c[2] - c[0]
    lat_o2 = d_o2[:2]
    u = lat_o2 / np.linalg.norm(lat_o2)
    h_off = float(abs(d_h[0] * -u[1] + d_h[1] * u[0]))
    shortest = {f: r["slab"]["reduced_in_plane_basis"]["shortest_A"] for f, r in denominators["families"].items()}
    o2_max = float(2 * np.linalg.norm(lat_o2))
    return dict(O2_max_shift_A=o2_max, H_mirror_shift_A=2 * h_off, shortest_in_plane_vector_A=shortest,
                holds={f: bool(o2_max < v and 2 * h_off < v) for f, v in shortest.items()})


def decision_record(denominators: dict) -> dict:
    fams = {}
    for fam, rec in denominators["families"].items():
        n = rec["adsorbates"]["O"]["n_configurations"]
        k = PREDICTED_MIN_RETAINED[fam]
        f_max = max(i for i in range(n + 1) if Fraction(i, n) <= F_LINE)
        fams[fam] = dict(
            blind=rec["blind"], N=n,
            X=dict(fraction=f"{k}/{n}", value=round(k / n, 6), applies_to=["O", "OH"],
                   HELD_if_retained_at_least=k),
            FALSIFIED_if_retained_at_most=f_max,
            gap=[i for i in range(n + 1) if f_max < i < k],
            OOH=dict(expected_retained=0, kind="construction check",
                     violation="VOID for this family's rows until explained"),
            O_equals_OH=dict(kind="construction check", violation="VOID for this family's rows until explained"),
            pooled_reading_not_used=pooled_counterpart(k, n),
            rationale=RATIONALE[fam],
        )
    ooh = ooh_bound(denominators)
    return dict(date=DATE, docs43_lines=dict(spec="1900-1902", scope_row="1923"), OOH_bound=ooh,
                F_line=str(F_LINE), rule="HELD if retained >= k; FALSIFIED if rate <= 1/2; otherwise gap",
                reading=READING, families=fams)
