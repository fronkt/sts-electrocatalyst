"""Round-2 active learning (scaffold).

After round-1 alloys are melted and their OER overpotentials measured, condition a
surrogate on the real data and propose the next compositions to melt. This is a
SCAFFOLD: a scikit-learn Gaussian-process surrogate + expected-improvement
acquisition (minimizing η), gated by formability. For true multi-objective
acquisition, swap in BoTorch qNEHVI (see src/README.md).
"""
from __future__ import annotations

import numpy as np

from .composition import Composition
from .data import DEFAULT_ELEMENTS
from .phase_stability import formability_score


def _features(comps, elements) -> np.ndarray:
    return np.array([c.vector(elements) for c in comps], dtype=float)


def expected_improvement(mu: np.ndarray, sigma: np.ndarray, best: float, xi: float = 0.01) -> np.ndarray:
    """EI for MINIMIZATION (we want low overpotential)."""
    from scipy.stats import norm

    sigma = np.maximum(sigma, 1e-9)
    imp = best - mu - xi
    z = imp / sigma
    return imp * norm.cdf(z) + sigma * norm.pdf(z)


def propose_round2(
    measured: list[tuple[Composition, float]],
    candidates: list[Composition],
    n_propose: int = 2,
    elements=DEFAULT_ELEMENTS,
    formability_min: float = 0.5,
    length_scale: float = 0.3,
    seed: int = 0,
) -> list[tuple[Composition, float, float, float]]:
    """Propose the next `n_propose` compositions to melt.

    Parameters
    ----------
    measured : list of (Composition, measured_eta_V) from round 1.
    candidates : compositions to choose among.

    Returns list of (Composition, predicted_eta, predicted_std, EI), best first.
    """
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import ConstantKernel, Matern

    Xtr = _features([c for c, _ in measured], elements)
    ytr = np.array([e for _, e in measured], dtype=float)

    kernel = ConstantKernel(1.0) * Matern(length_scale=length_scale, nu=2.5)
    gp = GaussianProcessRegressor(kernel=kernel, alpha=1e-4, normalize_y=True, random_state=seed)
    gp.fit(Xtr, ytr)

    Xc = _features(candidates, elements)
    mu, sigma = gp.predict(Xc, return_std=True)
    ei = expected_improvement(mu, sigma, best=float(ytr.min()))

    form = np.array([formability_score(c) for c in candidates])
    ei = np.where(form >= formability_min, ei, -np.inf)

    out: list[tuple[Composition, float, float, float]] = []
    for idx in np.argsort(-ei):
        if not np.isfinite(ei[idx]):
            break
        out.append((candidates[idx], float(mu[idx]), float(sigma[idx]), float(ei[idx])))
        if len(out) >= n_propose:
            break
    return out
