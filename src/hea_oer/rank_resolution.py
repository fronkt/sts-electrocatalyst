"""Rank-resolution statistics for a decoration-sampled site census.

The screen assigns every composition one number, the minimum site overpotential
over its sampled decorations (random cation arrangements, keyed by ``seed``) and
cus sites.  This module asks two questions of such a census without changing the
banked rule: can the compositions be ordered at all, and how many decorations
would it take.

Inputs are lists of result dictionaries in the ``screen-diagnostic-v1`` schema
(``results[].row.per_site_records`` and ``results[].row.decoration_records``).
No file is read or written here; the core is pure ``numpy``/``scipy``.  The only
optional dependency is ``ase`` inside :func:`local_environment_features`.

Statistical constructions and their sources
-------------------------------------------
* Decorations as the sampling unit.  Svane and Rossmeisl (Angew. Chem. Int. Ed.
  61, e202201146, 2022) sampled random (110) slabs of a five-metal rutile oxide,
  fitted ~600 adsorption energies by ridge regression on nearest-neighbour metal
  composition, and reported activity as a distribution over local environments.
  Baek et al. (Nat. Commun. 2023, 10.1038/s41467-023-41359-7) enumerated 120
  nearest-neighbour permutations per active site and found a ~0.5 eV spread.
  Potter et al. (arXiv:2504.11587) report a site distribution (mean, sigma of
  0.19-0.27 eV) rather than one decoration.  Sites that share a decoration share
  one relaxed slab, so a decoration, not a site, is the exchangeable unit; the
  bootstrap here resamples decorations and keeps their sites together
  (a cluster bootstrap; Davison and Hinkley, *Bootstrap Methods and their
  Application*, 1997, section 3.8).
* The minimum is an extreme order statistic.  The nonparametric bootstrap of a
  sample extreme is not consistent (Bickel and Freedman, Ann. Statist. 9, 1196,
  1981), so under the banked ``min`` rule the resampling frequencies reported by
  :func:`adjacent_gap_resolvability` are descriptive, not calibrated
  probabilities; under ``mean``/``median``/``p10`` they are ordinary bootstrap
  estimates.  With D decorations the cluster bootstrap has only C(2D-1, D)
  distinct resamples (10 for D = 3), which :func:`bootstrap_support` reports.
* Power for a location shift.  :func:`decorations_needed` treats the two
  compositions' site overpotentials as independent normals with a common
  location shift equal to the gap.  For the mean the order probability is
  Phi(gap / sqrt((sa^2 + sb^2)/N)), exact for normal sites.  For the minimum,
  the median and the 10th percentile the sample statistic is simulated exactly
  through the joint distribution of consecutive uniform order statistics
  (U_(k) ~ Beta(k, N-k+1); U_(k+1) | U_(k) = U_(k) + (1-U_(k)) Beta(1, N-k);
  David and Nagaraja, *Order Statistics*, 3rd ed., 2003, section 2.2) and the
  normal quantile transform, so no array of N draws is ever formed.  The
  large-sample quantile variance p(1-p)/(N f(q)^2) (Serfling, *Approximation
  Theorems of Mathematical Statistics*, 1980, section 2.3) and the Gumbel
  leading-order variance (pi^2/6) sigma^2 / (2 ln N) of the normal maximum are
  kept as closed-form references only: with 12 sites the 10th percentile is a
  near-extreme order statistic and the asymptotic variance is not attained, and
  with sa != sb every order statistic other than the mean drifts with depth.
* One model per table.  A census may hold several checkpoints' results for the
  same (composition, seed); :func:`check_single_model` refuses a site table in
  which one decoration carries rows from two model files.
"""
from __future__ import annotations

from collections import OrderedDict
import math
from typing import Callable, Iterable, Mapping, Sequence

import numpy as np
from scipy.special import betaincinv, ndtr, ndtri

RULES = ("min", "median", "p10", "mean")
QUANTILE_P = {"min": 0.0, "median": 0.5, "p10": 0.1}
#: Sites below which the 10th percentile is a near-extreme order statistic (with 12
#: sites its numpy position is 1.1, i.e. the second-lowest site plus a tenth of the
#: distance to the third).
P10_NEAR_EXTREME_SITES = 50
#: Monte-Carlo tolerance on a P(order) difference between two grid points before a
#: curve is called non-monotone (about 3 binomial standard errors at n_sim = 20000).
REVERSAL_TOLERANCE = 0.01
MIN_DECORATIONS = 2
RIDGE_MIN_SITES = 30
DEFAULT_ELEMENTS = ("Fe", "Co", "Ni", "Cr", "Mn", "Cu")
NON_METALS = frozenset({"O", "H"})

# Large-sample variance multipliers c_rule such that Var(statistic) = c * sigma^2 / N
# for N i.i.d. normal sites (Serfling 1980, section 2.3.3 for the quantiles).
_Z10 = ndtri(0.10)
_PHI10 = math.exp(-0.5 * _Z10 * _Z10) / math.sqrt(2.0 * math.pi)
QUANTILE_VARIANCE_FACTOR = {
    "mean": 1.0,
    "median": math.pi / 2.0,
    "p10": 0.1 * 0.9 / (_PHI10 * _PHI10),
}


class InsufficientDecorationsError(ValueError):
    """Raised when a composition has fewer sampled decorations than the minimum."""


class MixedModelError(ValueError):
    """Raised when one (composition, seed) carries site rows from two model files."""


def kendall_tau_a(order_a: Sequence[str], order_b: Sequence[str]) -> float:
    """Kendall tau-a between two total orders over the same labels."""
    if sorted(order_a) != sorted(order_b) or len(set(order_a)) != len(order_a):
        raise ValueError("orders must be permutations of one another")
    pos = {label: k for k, label in enumerate(order_b)}
    n = len(order_a)
    s = 0
    for i in range(n):
        for j in range(i + 1, n):
            d = pos[order_a[i]] - pos[order_a[j]]
            s += (d < 0) - (d > 0)
    pairs = n * (n - 1) / 2
    return s / pairs if pairs else float("nan")


# --------------------------------------------------------------------------- (a)
def iter_result_rows(result_jsons: Iterable[Mapping]) -> Iterable[tuple[int, Mapping, Mapping | None]]:
    """Yield ``(source_index, row, site_evidence)`` from a list of result payloads.

    Accepts full ``screen-diagnostic-v1`` payloads (``{"results": [{"row": ...}]}``),
    single result entries (``{"row": ...}``) or bare rows (``{"per_site_records": ...}``).
    """
    for k, payload in enumerate(result_jsons):
        if "results" in payload:
            entries = payload["results"]
        elif "row" in payload or "per_site_records" in payload:
            entries = [payload]
        else:
            raise ValueError(f"result {k}: no 'results', 'row' or 'per_site_records' key")
        for entry in entries:
            row = entry["row"] if "row" in entry else entry
            evidence = entry.get("site_evidence") if isinstance(entry, Mapping) else None
            yield k, row, evidence


def _evidence_status(evidence: Mapping | None) -> dict[tuple[int, int], str]:
    if not evidence or "sites" not in evidence:
        return {}
    return {(int(s["seed"]), int(s["site_index"])): str(s.get("status", "unknown"))
            for s in evidence["sites"]}


def _payload_model(payload: Mapping) -> tuple[str | None, str | None]:
    manifest = payload.get("manifest") if isinstance(payload, Mapping) else None
    model = (manifest or {}).get("model") or {}
    return model.get("filename"), model.get("sha256_bytes")


def load_site_table(result_jsons: Sequence[Mapping],
                    admitted: Callable[[Mapping], bool] | Mapping | None = None,
                    annotate: Callable[[dict, Mapping, Mapping], None] | None = None) -> list[dict]:
    """Flatten result payloads into one row per (composition, seed, site).

    Each row carries ``formula, seed, site_index, eta, eta_cus, pls, dG_OH, dG_O,
    dG_OOH, site_metal`` (the winning bond record's metal), ``initial_binding_metal``,
    ``final_binding_metals`` (per species, when retained), ``desorbed`` (list of
    species whose winning M-O distance reached the desorption cut),
    ``desorbed_any``, ``converged`` (all retained states converged by force, or
    None), ``evidence_status`` (from the payload's site-evidence block when
    present), ``model_filename``/``model_sha256`` (from the payload's manifest when
    present), ``declared_n_sites``/``declared_n_decorations`` and ``admitted``.

    ``annotate(rec, site_record, row)`` is called on every row before admission
    is decided; it may add keys (a site-integrity classification) or replace
    ``eta`` (a two-pathway value), ``eta_cus`` keeps the retained cus value.
    ``admitted`` is caller-supplied: a callable ``row -> bool``, a mapping keyed
    by ``(formula, seed, site_index)``, or None (every site admitted, which is
    the banked rule: the legacy winner is retained regardless of quality).
    """
    rows: list[dict] = []
    for source, row, evidence in iter_result_rows(result_jsons):
        formula = row["formula"]
        status = _evidence_status(evidence)
        model_file, model_sha = _payload_model(result_jsons[source])
        for site in row["per_site_records"]:
            states = site.get("relaxed_states") or {}
            conv = [st.get("converged_by_force") for st in states.values()]
            rec = OrderedDict(
                formula=formula,
                elements=list(row.get("elements", [])),
                fractions=[float(f) for f in row.get("fractions", [])],
                source=source,
                model_filename=model_file,
                model_sha256=model_sha,
                seed=int(site["seed"]),
                site_index=int(site["site_index"]),
                site_xy_A=list(site.get("site_xy_A", [])),
                eta=float(site["eta"]),
                eta_cus=float(site["eta"]),
                pls=int(site["pls"]),
                dG_OH=float(site["dG_OH"]),
                dG_O=float(site["dG_O"]),
                dG_OOH=float(site["dG_OOH"]),
                site_metal=(site.get("bonds") or {}).get("site_metal"),
                initial_binding_metal=site.get("initial_binding_metal"),
                initial_binding_metal_index=site.get("initial_binding_metal_index"),
                final_binding_metals={sp: st.get("final_binding_metal") for sp, st in states.items()},
                desorbed=list(site.get("desorbed") or []),
                desorbed_any=bool(site.get("desorbed")),
                converged=(all(bool(c) for c in conv) if conv and all(c is not None for c in conv) else None),
                evidence_status=status.get((int(site["seed"]), int(site["site_index"]))),
                declared_n_sites=row.get("n_sites"),
                declared_n_decorations=row.get("n_decorations"),
            )
            if annotate is not None:
                annotate(rec, site, row)
            if admitted is None:
                rec["admitted"] = True
            elif callable(admitted):
                rec["admitted"] = bool(admitted(rec))
            else:
                rec["admitted"] = bool(admitted.get((formula, rec["seed"], rec["site_index"]), False))
            rows.append(dict(rec))
    return rows


def check_single_model(rows: Sequence[Mapping]) -> dict:
    """Refuse a site table in which one (formula, seed) carries rows from more than
    one model file, or in which two model files appear at all.  Returns
    ``{"models": [(filename, sha256)], "n_rows": ...}`` when the table is uniform."""
    per_dec: dict[tuple[str, int], set] = {}
    models: set = set()
    for r in rows:
        key = (r.get("model_filename"), r.get("model_sha256"))
        models.add(key)
        per_dec.setdefault((r["formula"], int(r["seed"])), set()).add(key)
    mixed = sorted((f, s, sorted(str(m[0]) for m in ms)) for (f, s), ms in per_dec.items() if len(ms) > 1)
    if mixed:
        text = "; ".join(f"{f}/seed={s}: {', '.join(m)}" for f, s, m in mixed)
        raise MixedModelError(f"mixed models within a decoration: {text}")
    if len(models) > 1:
        text = ", ".join(str(m[0]) for m in sorted(models, key=str))
        raise MixedModelError(f"mixed models across the table: {text}")
    return {"models": sorted(models, key=str), "n_rows": len(rows)}


def decoration_census(rows: Sequence[Mapping], admitted_only: bool = True) -> "OrderedDict[str, dict]":
    """Per composition: sorted seeds, sites per seed and admitted-site counts."""
    out: "OrderedDict[str, dict]" = OrderedDict()
    for r in rows:
        entry = out.setdefault(r["formula"], {"seeds": {}, "n_sites": 0, "n_admitted": 0})
        seed = entry["seeds"].setdefault(r["seed"], {"n_sites": 0, "n_admitted": 0})
        seed["n_sites"] += 1
        entry["n_sites"] += 1
        if r.get("admitted", True):
            seed["n_admitted"] += 1
            entry["n_admitted"] += 1
    for formula, entry in out.items():
        seeds = entry["seeds"]
        usable = [s for s, v in sorted(seeds.items()) if (v["n_admitted"] > 0 if admitted_only else v["n_sites"] > 0)]
        entry["seeds"] = OrderedDict(sorted(seeds.items()))
        entry["n_decorations"] = len(seeds)
        entry["n_decorations_usable"] = len(usable)
        entry["usable_seeds"] = usable
    return out


def check_decorations(rows: Sequence[Mapping], minimum: int = MIN_DECORATIONS) -> list[tuple[str, int]]:
    """Return ``[(formula, n_usable_decorations)]`` for compositions below ``minimum``."""
    census = decoration_census(rows)
    return [(f, e["n_decorations_usable"]) for f, e in census.items() if e["n_decorations_usable"] < minimum]


def bootstrap_support(n_decorations: int) -> int:
    """Number of distinct multisets a cluster bootstrap can draw: C(2D-1, D)."""
    d = int(n_decorations)
    return math.comb(2 * d - 1, d) if d >= 1 else 0


# --------------------------------------------------------------------------- (b)
def _statistic(values: np.ndarray, rule: str, axis: int | None = None):
    if rule == "min":
        return np.min(values, axis=axis)
    if rule == "mean":
        return np.mean(values, axis=axis)
    if rule == "median":
        return np.median(values, axis=axis)
    if rule == "p10":
        return np.percentile(values, 10, axis=axis)  # numpy default linear interpolation
    raise ValueError(f"unknown rule {rule!r}; choose from {RULES}")


def _grouped(rows: Sequence[Mapping]) -> "OrderedDict[str, OrderedDict[int, list[float]]]":
    groups: "OrderedDict[str, OrderedDict[int, list[float]]]" = OrderedDict()
    for r in rows:
        comp = groups.setdefault(r["formula"], OrderedDict())
        comp.setdefault(r["seed"], [])
        if r.get("admitted", True):
            comp[r["seed"]].append(float(r["eta"]))
    return groups


def composition_statistic(rows: Sequence[Mapping], rule: str) -> "OrderedDict[str, float]":
    """One number per composition from its admitted sites.

    ``min`` is the banked rule (the screen's answer is the lowest-eta site over
    all decorations and sites); ``median``, ``p10`` (10th percentile, linear
    interpolation) and ``mean`` are the alternative summaries of the same site
    distribution in the sense of Potter et al. and Svane and Rossmeisl.  A
    composition with no admitted site gets ``nan``.
    """
    if rule not in RULES:
        raise ValueError(f"unknown rule {rule!r}; choose from {RULES}")
    out: "OrderedDict[str, float]" = OrderedDict()
    for formula, seeds in _grouped(rows).items():
        values = np.array([v for vs in seeds.values() for v in vs], dtype=float)
        out[formula] = float(_statistic(values, rule)) if values.size else float("nan")
    return out


# --------------------------------------------------------------------------- (c)
def cluster_bootstrap(rows: Sequence[Mapping], B: int, rng_seed: int, rule: str = "min",
                      minimum: int = MIN_DECORATIONS) -> "OrderedDict[str, np.ndarray]":
    """Resample decorations with replacement within each composition.

    For a composition with usable decorations d = 1..D (a decoration is usable
    when at least one of its sites is admitted), each replicate draws D seeds
    with replacement, concatenates every admitted site of every drawn seed and
    recomputes the statistic.  Sites of one decoration are never separated.
    Returns ``formula -> array of B replicate statistics``.

    Raises :class:`InsufficientDecorationsError` if any composition has fewer
    than ``minimum`` usable decorations; an interval from one decoration would
    be invented, not estimated.
    """
    if rule not in RULES:
        raise ValueError(f"unknown rule {rule!r}; choose from {RULES}")
    if int(B) < 1:
        raise ValueError("B must be >= 1")
    deficient = check_decorations(rows, minimum)
    if deficient:
        text = ", ".join(f"{f} ({n})" for f, n in deficient)
        raise InsufficientDecorationsError(
            f"insufficient decorations: {text}; at least {minimum} usable decorations per composition are needed")
    rng = np.random.default_rng(rng_seed)
    out: "OrderedDict[str, np.ndarray]" = OrderedDict()
    for formula, seeds in _grouped(rows).items():
        arrays = [np.asarray(v, dtype=float) for v in seeds.values() if len(v) > 0]
        D = len(arrays)
        idx = rng.integers(0, D, size=(int(B), D))
        if len({a.size for a in arrays}) == 1:
            S = np.stack(arrays)                        # (D, n)
            samp = S[idx].reshape(int(B), -1)           # (B, D*n)
            out[formula] = np.asarray(_statistic(samp, rule, axis=1), dtype=float)
        else:
            vals = np.empty(int(B), dtype=float)
            for b in range(int(B)):
                vals[b] = _statistic(np.concatenate([arrays[j] for j in idx[b]]), rule)
            out[formula] = vals
    return out


# --------------------------------------------------------------------------- (d)
def rank_probability_matrix(boot: Mapping[str, np.ndarray]) -> dict:
    """P(composition i has rank r) and pairwise P(stat_i < stat_j) over replicates.

    Rank 0 is the lowest statistic (best).  Ties split 1/2 each way in the
    pairwise matrix and are broken by stable argsort in the rank matrix.
    Replicates containing a non-finite value are dropped and counted.
    """
    formulas = list(boot.keys())
    M = np.column_stack([np.asarray(boot[f], dtype=float) for f in formulas])  # (B, K)
    ok = np.all(np.isfinite(M), axis=1)
    M = M[ok]
    B, K = M.shape
    order = np.argsort(M, axis=1, kind="stable")
    ranks = np.empty_like(order)
    rows_idx = np.arange(B)[:, None]
    ranks[rows_idx, order] = np.arange(K)[None, :]
    rank_matrix = np.stack([np.bincount(ranks[:, i], minlength=K) / B for i in range(K)])
    pairwise = np.empty((K, K))
    for i in range(K):
        for j in range(K):
            if i == j:
                pairwise[i, j] = 0.5
            else:
                pairwise[i, j] = np.mean(M[:, i] < M[:, j]) + 0.5 * np.mean(M[:, i] == M[:, j])
    return {"formulas": formulas, "rank_matrix": rank_matrix, "pairwise": pairwise,
            "n_replicates": int(B), "n_dropped": int((~ok).sum()),
            "expected_rank": rank_matrix @ np.arange(K)}


# --------------------------------------------------------------------------- (e)
def adjacent_gap_resolvability(boot: Mapping[str, np.ndarray], order: Sequence[str],
                               level: float = 0.90, point: Mapping[str, float] | None = None) -> list[dict]:
    """For each adjacent pair (a, b) in ``order`` (a ranked better, i.e. lower):
    P(order preserved) = P(stat_b - stat_a > 0) over replicates (ties count 1/2)
    and the central ``level`` percentile interval of the replicate gap.
    ``point`` (optional ``formula -> statistic``) adds the observed gap.
    """
    lo, hi = 100.0 * (1.0 - level) / 2.0, 100.0 * (1.0 + level) / 2.0
    out = []
    for a, b in zip(order[:-1], order[1:]):
        g = np.asarray(boot[b], dtype=float) - np.asarray(boot[a], dtype=float)
        g = g[np.isfinite(g)]
        entry = {"better": a, "worse": b, "level": level,
                 "p_order_preserved": float(np.mean(g > 0) + 0.5 * np.mean(g == 0)) if g.size else float("nan"),
                 "gap_interval_V": [float(v) for v in np.percentile(g, [lo, hi])] if g.size else [float("nan")] * 2,
                 "gap_replicate_median_V": float(np.median(g)) if g.size else float("nan"),
                 "n_replicates": int(g.size)}
        if point is not None:
            entry["gap_point_V"] = float(point[b]) - float(point[a])
        out.append(entry)
    return out


# --------------------------------------------------------------------------- (f)
def normal_maximum_from_uniform(u: np.ndarray, n: int | float) -> np.ndarray:
    """Quantile transform of the maximum of ``n`` i.i.d. standard normals.

    The maximum has CDF Phi(x)^n, so max = Phi^-1(u^(1/n)) for u ~ U(0, 1).
    Computed as -ndtri(-expm1(log(u)/n)) to stay accurate when u^(1/n) is
    within 1e-16 of 1 (n up to ~1e300).  Exact for any n, no array of n draws.
    """
    u = np.clip(np.asarray(u, dtype=float), np.finfo(float).tiny, 1.0 - 2.0 ** -53)
    return -ndtri(-np.expm1(np.log(u) / float(n)))


def normal_quantile_from_uniform(u1: np.ndarray, u2: np.ndarray, n: int, p: float) -> np.ndarray:
    """Exact sample of numpy's linear-interpolation ``p``-quantile of ``n`` i.i.d.
    standard normals, from two uniforms per replicate and no array of ``n`` draws.

    numpy's default method takes h = (n - 1) p, j = floor(h), g = h - j and returns
    X_(j+1) + g (X_(j+2) - X_(j+1)) over the sorted sample (1-indexed).  The uniform
    order statistic U_(j+1) is Beta(j+1, n-j); given U_(j+1) = u the next one is
    u + (1 - u) W with W ~ Beta(1, n-j-1) (David and Nagaraja 2003, section 2.2).
    Both are drawn by inverse CDF (``betaincinv``; 1 - (1 - v)^(1/m)) so common
    random numbers carry across depths.  p = 0 gives the minimum, p = 0.5 numpy's
    median (the average of the two middle sites when n is even).
    """
    n = int(n)
    if n < 1:
        raise ValueError("n must be >= 1")
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must lie in [0, 1]")
    u1 = np.clip(np.asarray(u1, dtype=float), np.finfo(float).tiny, 1.0 - 2.0 ** -53)
    u2 = np.clip(np.asarray(u2, dtype=float), np.finfo(float).tiny, 1.0 - 2.0 ** -53)
    h = (n - 1) * p
    j = int(math.floor(h + 1e-12))
    g = h - j
    if j >= n - 1:
        j, g = n - 1, 0.0
    if j == 0:                                       # U_(1) ~ Beta(1, n): 1 - (1-u)^(1/n)
        U1 = -np.expm1(np.log1p(-u1) / n)
    else:
        U1 = betaincinv(j + 1, n - j, u1)
    X1 = ndtri(np.clip(U1, np.finfo(float).tiny, 1.0 - 2.0 ** -53))
    if g <= 1e-12 or n - j - 1 < 1:
        return X1
    W = -np.expm1(np.log1p(-u2) / (n - j - 1))
    U2 = U1 + (1.0 - U1) * W
    X2 = ndtri(np.clip(U2, np.finfo(float).tiny, 1.0 - 2.0 ** -53))
    return X1 + g * (X2 - X1)


def _statistic_sample(rule: str, uniforms: tuple[np.ndarray, np.ndarray], n_sites: int) -> np.ndarray:
    """Exact replicate values of ``rule`` over ``n_sites`` standard normal sites."""
    if rule == "min":
        return -normal_maximum_from_uniform(uniforms[0], n_sites)
    return normal_quantile_from_uniform(uniforms[0], uniforms[1], n_sites, QUANTILE_P[rule])


def _closed_form_probability(rule: str, gap: float, sa: float, sb: float, N: int) -> float:
    """Large-sample reference value of P(order): normal approximation for mean/median/p10
    (exact for the mean), Gumbel leading order for the minimum."""
    s2sum = sa * sa + sb * sb
    if rule in QUANTILE_VARIANCE_FACTOR:
        se = math.sqrt(QUANTILE_VARIANCE_FACTOR[rule] * s2sum / N)
        return float(ndtr(gap / se)) if se > 0 else (1.0 if gap > 0 else 0.5)
    s2 = 0.5 * s2sum
    if s2 <= 0:
        return 1.0 if gap > 0 else 0.5
    if N > 1:
        return float(ndtr(gap * math.sqrt(6.0 * math.log(N)) / (math.pi * math.sqrt(s2))))
    return float(ndtr(gap / math.sqrt(2.0 * s2)))


def order_probability(rule: str, gap: float, sigma_a: float, sigma_b: float, n_sites: int,
                      rng: np.random.Generator | None = None, n_sim: int = 20000,
                      uniforms: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray] | None = None) -> dict:
    """P(statistic_A < statistic_B) when site eta_A ~ N(0, sa^2), eta_B ~ N(gap, sb^2),
    N i.i.d. sites each (no decoration random effect).

    ``mean``: closed form Phi(gap / sqrt((sa^2 + sb^2) / N)), exact.
    ``min``/``median``/``p10``: exact simulation of the sample statistic through
    :func:`normal_maximum_from_uniform` / :func:`normal_quantile_from_uniform`
    (``p_order_simulated``), with the closed-form large-sample value kept as
    ``p_order_analytic`` for reference only.  ``uniforms`` = (uA1, uA2, uB1, uB2)
    supplies common random numbers across depths.
    """
    N = int(n_sites)
    if N < 1:
        raise ValueError("n_sites must be >= 1")
    if rule not in RULES:
        raise ValueError(f"unknown rule {rule!r}; choose from {RULES}")
    sa, sb = float(sigma_a), float(sigma_b)
    rng = np.random.default_rng(0) if rng is None else rng
    out = {"rule": rule, "gap_V": float(gap), "sigma_a": sa, "sigma_b": sb, "n_sites": N,
           "p_order_analytic": _closed_form_probability(rule, float(gap), sa, sb, N)}
    if rule == "mean":
        out["p_order_simulated"] = None
        out["method"] = "normal closed form (exact for normal sites)"
        return out
    if uniforms is None:
        uniforms = tuple(rng.random(int(n_sim)) for _ in range(4))
    sA = sa * _statistic_sample(rule, (uniforms[0], uniforms[1]), N)
    sB = float(gap) + sb * _statistic_sample(rule, (uniforms[2], uniforms[3]), N)
    out["p_order_simulated"] = float(np.mean(sA < sB) + 0.5 * np.mean(sA == sB))
    out["n_sim"] = int(uniforms[0].size)
    out["method"] = ("exact order-statistic simulation (analytic value is the "
                     + ("Gumbel leading order" if rule == "min" else "large-sample quantile variance")
                     + ", reference only)")
    return out


def decorations_needed(site_sigma: float | Sequence[float], gap: float, n_sites_per_decoration: int,
                       statistic: str, target_prob: float = 0.95, rng_seed: int = 0, n_sim: int = 20000,
                       max_decorations: int = 10000) -> dict:
    """Smallest number of decorations D (each contributing ``n_sites_per_decoration``
    i.i.d. sites) at which P(order preserved) >= ``target_prob`` for a location
    shift ``gap`` between two compositions whose site overpotentials have standard
    deviations ``site_sigma`` (one value, or a pair (sa, sb)).

    ``mean``: closed form.  N = (sa^2 + sb^2) (z_p / gap)^2, D = ceil(N / n),
    z_p = Phi^-1(target_prob); exact for normal sites.
    ``min``/``median``/``p10``: the exact-simulation curve P(D) is scanned on a
    geometric grid of D up to ``max_decorations`` with common random numbers,
    then bisected inside the first bracket that reaches the target.  The same
    bisection at target -/+ 2 binomial standard errors gives
    ``decorations_needed_bracket``, the Monte-Carlo uncertainty of the count.
    With sa == sb the curve is monotone under common random numbers; with
    sa != sb it is not: the order statistic of the wider site distribution
    drifts with depth, so the order at infinite depth is decided by the spread,
    not the location.  The scan is returned so that a non-monotone curve is
    visible; ``order_reverses_at_depth`` is set whenever P(max_decorations) falls
    more than ``REVERSAL_TOLERANCE`` below the best P on the grid, found or not.
    The large-sample closed form (quantile variance, or the Gumbel leading order
    for the minimum, valid only for sa == sb) is returned as
    ``decorations_needed_closed_form`` / ``log10_n_sites_asymptotic`` for
    reference.

    Returns a dict with ``decorations_needed`` (None when the target is not met
    on the grid), ``n_sites_needed``, ``achieved_prob`` and the scan.
    """
    if statistic not in RULES:
        raise ValueError(f"unknown rule {statistic!r}; choose from {RULES}")
    if not (0.5 < target_prob < 1.0):
        raise ValueError("target_prob must lie in (0.5, 1)")
    n = int(n_sites_per_decoration)
    if n < 1:
        raise ValueError("n_sites_per_decoration must be >= 1")
    gap = float(gap)
    if not gap > 0:
        raise ValueError("gap must be positive; a zero or negative gap cannot be resolved at any depth")
    if isinstance(site_sigma, (int, float)):
        sa = sb = float(site_sigma)
    else:
        sa, sb = (float(v) for v in site_sigma)
    if sa < 0 or sb < 0:
        raise ValueError("site_sigma must be non-negative")
    z = float(ndtri(target_prob))
    s2sum = sa * sa + sb * sb
    out = {"statistic": statistic, "gap_V": gap, "sigma_a": sa, "sigma_b": sb,
           "n_sites_per_decoration": n, "target_prob": float(target_prob),
           "equal_spreads": bool(sa == sb)}
    if statistic == "min":
        log10N = ((z * math.pi) ** 2 * s2sum / (12.0 * gap * gap)) / math.log(10.0) if s2sum > 0 else float("-inf")
        closed_form_method = "Gumbel leading order, location only, valid for sa == sb"
    else:
        c = QUANTILE_VARIANCE_FACTOR[statistic]
        N_real = c * s2sum * (z / gap) ** 2
        log10N = float(math.log10(N_real)) if N_real > 0 else float("-inf")
        closed_form_method = ("normal closed form (exact for normal sites)" if statistic == "mean"
                              else "large-sample quantile variance (Serfling 1980)")
    D_closed = (max(1, int(math.ceil(max(1.0, 10.0 ** log10N) / n))) if math.isfinite(log10N) and log10N < 15
                else None)   # None: not finite, or beyond any countable census (> 1e15 sites)
    out.update(log10_n_sites_asymptotic=float(log10N), decorations_needed_closed_form=D_closed,
               closed_form_method=closed_form_method)
    if statistic == "mean":
        N_real = s2sum * (z / gap) ** 2
        N_needed = max(1, int(math.ceil(N_real - 1e-12)))
        D = max(1, int(math.ceil(N_needed / n)))
        se = math.sqrt(s2sum / (D * n)) if s2sum > 0 else 0.0
        out.update(method=closed_form_method, n_sites_needed=N_needed, n_sites_needed_real=float(N_real),
                   decorations_needed=D, decorations_needed_bracket=[D, D],
                   achieved_prob=float(ndtr(gap / se)) if se > 0 else 1.0,
                   saturated=D > max_decorations, order_reverses_at_depth=False)
        return out
    # minimum / median / p10: exact order-statistic simulation with common random numbers
    rng = np.random.default_rng(rng_seed)
    uniforms = tuple(rng.random(int(n_sim)) for _ in range(4))
    cache: dict[int, float] = {}

    def p_at(D: int) -> float:
        if D not in cache:
            cache[D] = order_probability(statistic, gap, sa, sb, D * n, uniforms=uniforms)["p_order_simulated"]
        return cache[D]

    grid: list[int] = []
    d = 1
    while d < max_decorations:
        grid.append(d)
        d = max(d + 1, int(math.ceil(d * 1.5)))
    grid.append(int(max_decorations))
    scan = [(D, p_at(D)) for D in grid]

    def first_crossing(threshold: float) -> int | None:
        for k, (D, p) in enumerate(scan):
            if p >= threshold:
                lo, hi = (scan[k - 1][0] if k > 0 else 0), D
                while hi - lo > 1:
                    mid = (lo + hi) // 2
                    if p_at(mid) >= threshold:
                        hi = mid
                    else:
                        lo = mid
                return hi
        return None

    se = math.sqrt(target_prob * (1.0 - target_prob) / float(n_sim))
    found = first_crossing(target_prob)
    bracket = [first_crossing(target_prob - 2.0 * se), first_crossing(target_prob + 2.0 * se)]
    p_max = scan[-1][1]
    best = max(scan, key=lambda t: t[1])
    out.update(method="exact order-statistic simulation, common random numbers, geometric scan + bisection",
               n_sim=int(n_sim), max_decorations=int(max_decorations), binomial_se=float(se),
               decorations_needed=found, decorations_needed_bracket=bracket,
               n_sites_needed=(found * n if found is not None else None),
               achieved_prob=(p_at(found) if found is not None else None),
               prob_at_max_decorations=float(p_max), best_prob_on_grid=float(best[1]), best_decorations_on_grid=int(best[0]),
               saturated=found is None,
               order_reverses_at_depth=bool(best[1] - p_max > REVERSAL_TOLERANCE),
               near_extreme=(statistic == "p10" and found is not None and found * n < P10_NEAR_EXTREME_SITES),
               scan=[{"decorations": int(D), "p_order": float(p)} for D, p in scan])
    return out


def power_table(gaps: Sequence[float], sigmas: Sequence[float | Sequence[float]], n_sites_per_decoration: int,
                rules: Sequence[str] = ("min", "mean"), target_prob: float = 0.95, labels: Sequence[str] | None = None,
                **kwargs) -> list[dict]:
    """Cartesian product of gaps x sigmas x rules through :func:`decorations_needed`.
    ``labels`` (optional, one per gap) names the pair the gap belongs to."""
    out = []
    for k, gap in enumerate(gaps):
        for sigma in sigmas:
            for rule in rules:
                res = decorations_needed(sigma, gap, n_sites_per_decoration, rule, target_prob, **kwargs)
                res["label"] = labels[k] if labels else None
                out.append(res)
    return out


# --------------------------------------------------------------------------- (h)
def variance_components(rows: Sequence[Mapping]) -> "OrderedDict[str, dict]":
    """One-way random-effects decomposition of site eta into within- and
    between-decoration variance per composition (method of moments; Searle,
    Casella and McCulloch, *Variance Components*, 1992, section 3.6):
    MS_between = SS_b/(k-1), MS_within = SS_w/(N-k), n0 = (N - sum n_i^2 / N)/(k-1),
    sigma_between^2 = max(0, (MS_b - MS_w)/n0), ICC = sigma_b^2/(sigma_b^2 + MS_w).
    Also returns the population (ddof=0, the banked ``eta_std`` convention) and
    sample (ddof=1) standard deviations over all admitted sites.
    """
    out: "OrderedDict[str, dict]" = OrderedDict()
    for formula, seeds in _grouped(rows).items():
        groups = [np.asarray(v, dtype=float) for v in seeds.values() if len(v) > 0]
        allv = np.concatenate(groups) if groups else np.array([], dtype=float)
        N, k = int(allv.size), len(groups)
        entry = {"n_sites": N, "n_decorations": k,
                 "site_sd_population": float(np.std(allv)) if N else float("nan"),
                 "site_sd_sample": float(np.std(allv, ddof=1)) if N > 1 else float("nan")}
        if k >= 2 and N > k:
            m = allv.mean()
            ns = np.array([g.size for g in groups], dtype=float)
            means = np.array([g.mean() for g in groups])
            ss_b = float(np.sum(ns * (means - m) ** 2))
            ss_w = float(sum(np.sum((g - g.mean()) ** 2) for g in groups))
            ms_b, ms_w = ss_b / (k - 1), ss_w / (N - k)
            n0 = (N - float(np.sum(ns ** 2)) / N) / (k - 1)
            sb2 = max(0.0, (ms_b - ms_w) / n0)
            entry.update(within_sd=math.sqrt(ms_w), between_sd=math.sqrt(sb2),
                         icc=(sb2 / (sb2 + ms_w) if (sb2 + ms_w) > 0 else float("nan")),
                         ms_between=ms_b, ms_within=ms_w, status="ok")
        else:
            entry.update(within_sd=None, between_sd=None, icc=None, status="insufficient decorations")
        out[formula] = entry
    return out


# --------------------------------------------------------------------------- (g)
def local_environment_features(slab_record: Mapping, site_xy: Sequence[float], cutoff_A: float,
                               center_index: int | None = None, elements: Sequence[str] | None = None) -> dict:
    """Counts of each metal element among the cation neighbours of the cus metal.

    ``slab_record`` is a retained ``relaxed_slab`` (``symbols, positions_A, cell_A,
    pbc``).  The centre is ``center_index`` when given (the site's
    ``initial_binding_metal_index``), else the top-half metal nearest to
    ``site_xy`` in the plane under the minimum-image convention.  Neighbours are
    every cation image within ``cutoff_A`` (``ase.neighborlist.neighbor_list``,
    periodic images counted separately, so a chain neighbour that is its own
    image across a short cell axis counts twice as it does physically).

    This is the feature construction of Svane and Rossmeisl 2022: the
    nearest-neighbour metal composition of a site, without spatial arrangement.
    On the two retained 2x2x4 rutile(110) slabs the cation distance ladder from
    the cus atom is 2.87-3.01 A (one edge-sharing chain partner, twice by image),
    3.42-3.60 A (six corner-sharing cations) and then 4.36-4.38 A, so a cutoff
    of 3.8 A closes the first two shells (8 neighbours).
    """
    from ase import Atoms
    from ase.geometry import find_mic
    from ase.neighborlist import neighbor_list

    atoms = Atoms(symbols=list(slab_record["symbols"]), positions=np.asarray(slab_record["positions_A"], dtype=float),
                  cell=np.asarray(slab_record["cell_A"], dtype=float), pbc=list(slab_record.get("pbc", [True, True, True])))
    symbols = atoms.get_chemical_symbols()
    metals = [i for i, s in enumerate(symbols) if s not in NON_METALS]
    if not metals:
        raise ValueError("slab has no cations")
    if center_index is None:
        z = atoms.positions[:, 2]
        zmid = 0.5 * (z[metals].max() + z[metals].min())
        top = [i for i in metals if z[i] >= zmid]
        vecs = np.zeros((len(top), 3))
        vecs[:, :2] = np.asarray(site_xy, dtype=float)[None, :] - atoms.positions[top, :2]
        _, dxy = find_mic(vecs, atoms.cell, atoms.pbc)
        center_index = int(top[int(np.argmin(dxy))])
        center_offset = float(dxy.min())
    else:
        center_index = int(center_index)
        vec = np.zeros((1, 3))
        vec[0, :2] = np.asarray(site_xy, dtype=float) - atoms.positions[center_index, :2]
        _, dxy = find_mic(vec, atoms.cell, atoms.pbc)
        center_offset = float(dxy[0])
    if symbols[center_index] in NON_METALS:
        raise ValueError(f"centre atom {center_index} is {symbols[center_index]}, not a cation")
    i_idx, j_idx, d_idx = neighbor_list("ijd", atoms, float(cutoff_A))
    mask = (i_idx == center_index) & np.isin(j_idx, metals)
    neigh_syms = [symbols[j] for j in j_idx[mask]]
    dists = sorted(float(d) for d in d_idx[mask])
    elements = list(elements) if elements is not None else sorted({symbols[i] for i in metals})
    counts = OrderedDict((el, sum(1 for s in neigh_syms if s == el)) for el in elements)
    unlisted = sorted({s for s in neigh_syms if s not in elements})
    return {"center_index": center_index, "center_metal": symbols[center_index], "center_offset_A": center_offset,
            "cutoff_A": float(cutoff_A), "n_neighbours": len(neigh_syms), "counts": counts,
            "distances_A": dists, "unlisted_neighbour_elements": unlisted}


def feature_matrix(rows: Sequence[Mapping], environments: Sequence[Mapping], elements: Sequence[str] = DEFAULT_ELEMENTS,
                   include_center: bool = True) -> tuple[np.ndarray, list[str]]:
    """Design matrix from :func:`local_environment_features` outputs aligned with ``rows``:
    neighbour counts per element, plus (optionally) a one-hot of the centre metal.
    The centre one-hot is an extension of the Svane 2022 construction needed when
    one fit spans sites with different cus metals."""
    names = [f"n_{el}" for el in elements]
    if include_center:
        names += [f"center_{el}" for el in elements]
    X = np.zeros((len(rows), len(names)))
    for r, (row, env) in enumerate(zip(rows, environments)):
        for k, el in enumerate(elements):
            X[r, k] = env["counts"].get(el, 0)
            if include_center:
                X[r, len(elements) + k] = 1.0 if env["center_metal"] == el else 0.0
    return X, names


def ridge_model(rows: Sequence[Mapping], features: np.ndarray | Sequence[Sequence[float]], alpha: float = 1.0,
                target: str = "eta", feature_names: Sequence[str] | None = None,
                min_sites: int = RIDGE_MIN_SITES) -> dict:
    """Ridge regression of a site quantity on local-environment features.

    y_i = b0 + x_i . b + e_i, with b = (Xc'Xc + alpha I)^-1 Xc' yc on centred
    data and an unpenalised intercept (Hoerl and Kennard, Technometrics 12, 55,
    1970) - the variance-handling device of Svane and Rossmeisl 2022, who fitted
    ~600 adsorption energies this way.  Leave-one-out residuals use the linear-
    smoother identity e_loo,i = e_i / (1 - H_ii) with
    H = 11'/n + Xc (Xc'Xc + alpha I)^-1 Xc' (exact for penalised least squares).
    Reports coefficients, in-sample and LOO R^2, in-sample and LOO residual sigma.

    Fewer than ``min_sites`` sites (default 30, roughly the smallest census at
    which a six- to twelve-parameter fit says anything) gives
    ``status = "insufficient_sites"``; fewer than p + 2 gives
    ``status = "underdetermined"`` with no coefficients.  Nothing is fitted
    silently in either case.
    """
    X = np.asarray(features, dtype=float)
    if X.ndim != 2:
        raise ValueError("features must be a 2-D array (sites x features)")
    y = np.array([float(r[target]) for r in rows], dtype=float)
    n, p = X.shape
    if y.size != n:
        raise ValueError("features and rows are not aligned")
    names = list(feature_names) if feature_names is not None else [f"x{k}" for k in range(p)]
    if len(names) != p:
        raise ValueError("feature_names length does not match the feature columns")
    out = {"target": target, "alpha": float(alpha), "n_sites": int(n), "n_features": int(p),
           "min_sites": int(min_sites), "feature_names": names}
    if n < p + 2:
        out.update(status="underdetermined", meaningful=False,
                   message=f"{n} sites for {p} features: no fit; at least {p + 2} sites are needed and "
                           f"about {min_sites} before the model is meaningful",
                   coefficients=None, intercept=None, r2_in_sample=None, r2_loo=None,
                   sigma_in_sample=None, sigma_loo=None)
        return out
    xm, ym = X.mean(axis=0), y.mean()
    Xc, yc = X - xm, y - ym
    A = Xc.T @ Xc + float(alpha) * np.eye(p)
    Ainv = np.linalg.pinv(A) if alpha == 0 else np.linalg.inv(A)
    beta = Ainv @ Xc.T @ yc
    b0 = ym - xm @ beta
    yhat = b0 + X @ beta
    e = y - yhat
    H = np.full((n, n), 1.0 / n) + Xc @ Ainv @ Xc.T
    h = np.clip(np.diag(H), 0.0, 1.0 - 1e-12)
    e_loo = e / (1.0 - h)
    sst = float(np.sum(yc ** 2))
    r2 = 1.0 - float(np.sum(e ** 2)) / sst if sst > 0 else float("nan")
    r2_loo = 1.0 - float(np.sum(e_loo ** 2)) / sst if sst > 0 else float("nan")
    out.update(status=("ok" if n >= min_sites else "insufficient_sites"), meaningful=n >= min_sites,
               message=(None if n >= min_sites else
                        f"{n} sites is below the {min_sites}-site floor; coefficients are reported but not meaningful"),
               coefficients=OrderedDict(zip(names, (float(v) for v in beta))), intercept=float(b0),
               r2_in_sample=r2, r2_loo=r2_loo,
               sigma_in_sample=float(math.sqrt(np.mean(e ** 2))), sigma_loo=float(math.sqrt(np.mean(e_loo ** 2))),
               leverage_max=float(h.max()))
    return out
