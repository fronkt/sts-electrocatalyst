"""Round-1 orchestration: sample -> evaluate -> rank -> shortlist."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .composition import sample_compositions
from .adsorption import get_backend
from .objective import build_table, rank, select_shortlist
from .data import DEFAULT_ELEMENTS


@dataclass
class RoundResult:
    table: pd.DataFrame       # all candidates, ranked (best first)
    shortlist: pd.DataFrame   # top-k diverse compositions to melt
    backend: str
    n_candidates: int


def run_round1(
    elements=DEFAULT_ELEMENTS,
    n_samples: int = 4000,
    top_k: int = 4,
    seed: int = 0,
    backend: str = "heuristic",
    weights: tuple[float, float, float] = (0.5, 0.3, 0.2),
    formability_min: float = 0.5,
) -> RoundResult:
    """Run the round-1 selector end-to-end. Deterministic for a fixed `seed`.

    Returns a RoundResult with the full ranked table and a diverse top-k shortlist
    of single-phase, earth-abundant, predicted-active HEA compositions to melt.
    """
    comps = sample_compositions(elements, n_samples=n_samples, seed=seed)
    be = get_backend(backend)
    table = build_table(comps, be, elements)
    ranked = rank(table, weights=weights, formability_min=formability_min)
    shortlist = select_shortlist(ranked, top_k=top_k, elements=elements)
    return RoundResult(
        table=ranked, shortlist=shortlist, backend=be.name, n_candidates=len(comps),
    )
