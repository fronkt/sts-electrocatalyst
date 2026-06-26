"""Composition representation and HEA composition sampling."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

from .data import DEFAULT_ELEMENTS


@dataclass(frozen=True)
class Composition:
    """A normalized alloy composition over a fixed element ordering.

    Attributes
    ----------
    elements : tuple of element symbols (only those with non-zero fraction).
    fractions : atomic fractions, same order as `elements`, summing to 1.
    """

    elements: tuple[str, ...]
    fractions: tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.elements) != len(self.fractions):
            raise ValueError("elements and fractions length mismatch")
        s = sum(self.fractions)
        if not np.isclose(s, 1.0, atol=1e-6):
            raise ValueError(f"fractions must sum to 1 (got {s:.6f})")

    def as_dict(self) -> dict[str, float]:
        return dict(zip(self.elements, self.fractions))

    def formula(self, scale: int = 100) -> str:
        """Human-readable formula in at.% (e.g. 'Fe20Co20Ni20Cr20Mn20')."""
        return "".join(
            f"{el}{round(fr * scale):g}" for el, fr in zip(self.elements, self.fractions)
        )

    def vector(self, basis: Sequence[str]) -> np.ndarray:
        """Dense fraction vector over a given element basis (0 for absent)."""
        d = self.as_dict()
        return np.array([d.get(el, 0.0) for el in basis], dtype=float)

    @classmethod
    def equiatomic(cls, elements: Sequence[str]) -> "Composition":
        n = len(elements)
        return cls(tuple(elements), tuple([1.0 / n] * n))

    @classmethod
    def from_dict(cls, d: dict[str, float]) -> "Composition":
        items = [(el, fr) for el, fr in d.items() if fr > 0]
        total = sum(fr for _, fr in items)
        els = tuple(el for el, _ in items)
        frs = tuple(fr / total for _, fr in items)
        return cls(els, frs)


def sample_compositions(
    elements: Sequence[str] = DEFAULT_ELEMENTS,
    n_samples: int = 4000,
    *,
    k_choices: Iterable[int] = (4, 5),
    min_frac: float = 0.05,
    max_frac: float = 0.35,
    include_equiatomic: bool = True,
    seed: int = 0,
) -> list[Composition]:
    """Sample realistic HEA compositions over `elements`.

    Each sample: pick k principal elements (k in `k_choices`), draw a Dirichlet
    composition, and keep it only if every fraction lies in [min_frac, max_frac]
    (the conventional "5-35 at.%, ≥4 principal elements" HEA window). Deterministic
    for a given `seed`.
    """
    rng = np.random.default_rng(seed)
    elements = list(elements)
    out: list[Composition] = []
    seen: set[tuple] = set()

    def _add(comp: Composition) -> None:
        key = tuple(round(f, 4) for f in comp.vector(elements))
        if key not in seen:
            seen.add(key)
            out.append(comp)

    if include_equiatomic:
        # equiatomic alloys for each k-subset are canonical anchors
        from itertools import combinations

        for k in k_choices:
            for subset in combinations(elements, k):
                _add(Composition.equiatomic(subset))

    attempts = 0
    max_attempts = n_samples * 40
    k_choices = list(k_choices)
    while len(out) < n_samples and attempts < max_attempts:
        attempts += 1
        k = int(rng.choice(k_choices))
        subset = list(rng.choice(elements, size=k, replace=False))
        frac = rng.dirichlet(np.ones(k))
        if frac.min() < min_frac or frac.max() > max_frac:
            continue
        _add(Composition(tuple(subset), tuple(float(f) for f in frac)))

    return out
