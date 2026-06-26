"""Multi-objective scoring and selection for round-1 candidates.

Objectives (all framed as "maximize"):
  * activity     -> from the OER theoretical overpotential (lower η is better)
  * formability  -> single-solid-solution score (meltable single-phase precursor)
  * abundance    -> composition-weighted crustal abundance (earth-abundance angle)

Round-1 logic (docs/12 §3): formability is a *gate*; among formable candidates we
rank by a weighted scalarization and report the Pareto-optimal, compositionally
diverse shortlist to melt.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .composition import Composition
from .adsorption import AdsorptionBackend
from .descriptors import oer_overpotential, descriptor_from_dG_OH
from .phase_stability import phase_stability, formability_score
from .data import CRUSTAL_ABUNDANCE_PPM, COST_USD_PER_KG, DEFAULT_ELEMENTS


def _abundance_score(comp: Composition, elements=DEFAULT_ELEMENTS) -> float:
    """Composition-weighted log-abundance, min-max normalized over `elements`."""
    logs = {el: np.log10(CRUSTAL_ABUNDANCE_PPM[el]) for el in elements}
    lo, hi = min(logs.values()), max(logs.values())
    val = sum(f * logs[el] for el, f in zip(comp.elements, comp.fractions))
    return float((val - lo) / (hi - lo)) if hi > lo else 1.0


def _cost(comp: Composition) -> float:
    return float(sum(f * COST_USD_PER_KG[el] for el, f in zip(comp.elements, comp.fractions)))


def pareto_mask(F: np.ndarray) -> np.ndarray:
    """Boolean mask of non-dominated rows of F (objectives to maximize)."""
    n = F.shape[0]
    mask = np.ones(n, dtype=bool)
    for i in range(n):
        if not mask[i]:
            continue
        dominates_i = np.all(F >= F[i], axis=1) & np.any(F > F[i], axis=1)
        if np.any(dominates_i):
            mask[i] = False
    return mask


def build_table(
    comps: list[Composition],
    backend: AdsorptionBackend,
    elements=DEFAULT_ELEMENTS,
) -> pd.DataFrame:
    """Evaluate every composition into a tidy DataFrame of properties + objectives."""
    rows = []
    for c in comps:
        dG_OH, dG_O, dG_OOH = backend.predict(c)
        oer = oer_overpotential(dG_OH, dG_O, dG_OOH)
        m = phase_stability(c)
        rows.append({
            "formula": c.formula(),
            "n_elements": len(c.elements),
            "dG_OH": dG_OH, "dG_O": dG_O, "dG_OOH": dG_OOH,
            "descriptor": descriptor_from_dG_OH(dG_OH, dG_O),
            "eta_V": oer.overpotential,
            "limiting_step": oer.potential_limiting_step,
            "formability": formability_score(c),
            "single_phase": m.single_solid_solution,
            "phase": m.phase_tendency,
            "delta_pct": m.delta, "omega": m.omega,
            "dHmix_kJ": m.dH_mix, "dSmix_J": m.dS_mix, "vec": m.vec,
            "abundance": _abundance_score(c, elements),
            "cost_usd_kg": _cost(c),
            "backend": backend.name,
            "_comp": c,
        })
    return pd.DataFrame(rows)


def rank(
    table: pd.DataFrame,
    weights: tuple[float, float, float] = (0.5, 0.3, 0.2),
    formability_min: float = 0.5,
) -> pd.DataFrame:
    """Gate by formability, then scalarize (activity, formability, abundance).

    Adds columns: `activity` (normalized, higher=better), `score`, `pareto`,
    `rank`. Returns the table sorted by score (best first).
    """
    df = table.copy()
    # activity: lower η is better -> min-max invert across the candidate set
    eta = df["eta_V"].to_numpy()
    span = eta.max() - eta.min()
    df["activity"] = (eta.max() - eta) / span if span > 1e-12 else 1.0

    formable = df["formability"] >= formability_min
    df["formable"] = formable

    wa, wf, wb = weights
    df["score"] = wa * df["activity"] + wf * df["formability"] + wb * df["abundance"]
    # candidates that fail the formability gate are pushed below all formable ones
    df.loc[~formable, "score"] = df.loc[~formable, "score"] - 1.0

    # Pareto front computed among formable candidates only
    df["pareto"] = False
    sub = df[formable]
    if len(sub) > 0:
        F = sub[["activity", "formability", "abundance"]].to_numpy()
        df.loc[sub.index[pareto_mask(F)], "pareto"] = True

    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    df["rank"] = np.arange(1, len(df) + 1)
    return df


def select_shortlist(
    ranked: pd.DataFrame,
    top_k: int = 4,
    elements=DEFAULT_ELEMENTS,
    score_margin: float = 0.15,
    max_pool: int = 25,
) -> pd.DataFrame:
    """Diverse top-k chosen *among strong candidates only*.

    To avoid spending a precious melt on a poor catalyst, diversity (greedy
    max-min over composition vectors) is applied to the pool of formable
    candidates within `score_margin` of the best score (capped at `max_pool`),
    not the whole Pareto front. The highest-scoring candidate always seeds the set.
    """
    formable = ranked[ranked["formable"]]
    base = formable if len(formable) > 0 else ranked
    best = float(base["score"].max())
    pool = base[base["score"] >= best - score_margin].sort_values("score", ascending=False)
    if len(pool) > max_pool:
        pool = pool.head(max_pool)
    if len(pool) == 0:
        pool = base.sort_values("score", ascending=False).head(max_pool)

    order = pool.index.tolist()  # already score-sorted (best first)
    vecs = {idx: ranked.loc[idx, "_comp"].vector(elements) for idx in order}
    chosen: list[int] = [order[0]]
    while len(chosen) < min(top_k, len(order)):
        best_idx, best_d = None, -1.0
        for idx in order:
            if idx in chosen:
                continue
            d = min(float(np.linalg.norm(vecs[idx] - vecs[c])) for c in chosen)
            if d > best_d:
                best_d, best_idx = d, idx
        chosen.append(best_idx)

    # top up by score if the pool was smaller than top_k
    if len(chosen) < top_k:
        for idx in base.sort_values("score", ascending=False).index:
            if idx not in chosen:
                chosen.append(idx)
            if len(chosen) >= top_k:
                break

    return ranked.loc[chosen].sort_values("rank").reset_index(drop=True)
