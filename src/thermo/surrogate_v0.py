"""Strength + conductivity surrogate v0 for deformation-processed Cu-Fe(-X) wire
(docs/24 SS3.4: "the oracle does kappa from physics; strength is learned from the
loop" - this module is the *pre-loop* literature-calibrated seed for both, to be
refit on round-0 hardness/rho and then superseded channel-by-channel: rho_ss by
KKR-CPA + own 4-point data, strength by the round-0/1 regression).

Physics, longitudinal (wire-axis) transport:
    rho_matrix = rho_Cu(state) + sum_i dRho_i * c_i(at.%, in solution) + K_INT/lambda
    1/rho_comp = (1-f)/rho_matrix + f/rho_Fe          (parallel rule of mixtures)
    lambda(eta) = LAMBDA0 * exp(-eta/4)               (curled-ribbon spacing, Cu-Nb lit)
    kappa = L_SP*T*sigma + C_SP                       (Smith-Palmer, Cu-alloy class)
    UTS = sigma_Cu(eta) + K_HP * sqrt(f) / sqrt(lambda)   (filament barrier, Hall-Petch form)

Calibration anchors (docs/24 SS2): hard-drawn Cu 430 MPa @ 97 %IACS; best published
Cu-14Fe 907 MPa @ 54.3 %IACS (drawn, eta ~5). Solute coefficients are Linde-rule
residual resistivities per at.% in solution - the same numbers the MuST KKR-CPA
validation ladder (src/thermo/README.md) is gated against, so the CPA sweep can
replace this dict wholesale.
"""
from __future__ import annotations

import math

# --- constants -------------------------------------------------------------
MOLAR_MASS = {"Cu": 63.546, "Fe": 55.845, "Cr": 51.996, "Zr": 91.224, "Ag": 107.868}
DENSITY = {"Cu": 8.96, "Fe": 7.87}          # g/cm^3 (for volume fraction)

RHO_CU_ANNEALED = 1.7241                     # uOhm-cm (IACS definition)
RHO_CU_HARD = 1.777                          # uOhm-cm (~97 %IACS hard-drawn anchor)
RHO_FE_BULK = 9.7                            # uOhm-cm (bcc Fe filaments, bulk value)

# Linde residual resistivity of solutes in Cu, uOhm-cm per at.% IN SOLUTION.
# Ag being ~25x gentler than Fe is exactly why it is microalloy probe #1.
DRHO_SOLUTE = {"Fe": 9.3, "Cr": 4.0, "Zr": 8.0, "Ag": 0.355}

LAMBDA0_UM = 2.0        # as-cast Fe dendrite/particle spacing, um
K_INT = 0.30            # interface term, uOhm-cm*um (Cu-Nb lit range 0.1-0.4; fit)
C_SS_DEFAULT_WT = 0.05  # wt.% Fe left in solution after draw+age (schedule knob)

L_SP = 2.32e-8          # Smith-Palmer slope, W*Ohm/K^2 (Cu-alloy class fit)
C_SP = 6.9              # Smith-Palmer intercept, W/m/K
T_ROOM = 300.0

UTS_CU_ANNEALED = 220.0  # MPa
UTS_CU_WH_CAP = 230.0    # work-hardening cap: sigma_Cu(inf) = 450 MPa
ETA_WH = 2.0             # work-hardening saturation strain
K_HP = 895.0             # MPa*um^0.5 (fit to the Cu-14Fe anchor)

# (label, UTS MPa, %IACS) - docs/24 SS2 published Pareto anchors, for plots/tests.
ANCHORS = [
    ("hard-drawn Cu", 430.0, 97.0),
    ("C18150 Cu-Cr-Zr", 500.0, 85.0),
    ("Cu-14Fe (best published)", 907.0, 54.3),
    ("Cu-Nb microcomposite", 1100.0, 62.5),
    ("Cu-24Ag", 1500.0, 65.0),
]


# --- helpers ---------------------------------------------------------------
def wt_to_at(wt: dict[str, float]) -> dict[str, float]:
    """wt.% dict (Cu = balance) -> at.% dict including Cu."""
    full = dict(wt)
    full["Cu"] = 100.0 - sum(wt.values())
    mol = {el: w / MOLAR_MASS[el] for el, w in full.items()}
    tot = sum(mol.values())
    return {el: 100.0 * m / tot for el, m in mol.items()}


def fe_volume_fraction(x_fe_wt: float) -> float:
    v_fe = x_fe_wt / DENSITY["Fe"]
    v_cu = (100.0 - x_fe_wt) / DENSITY["Cu"]
    return v_fe / (v_fe + v_cu)


def filament_spacing_um(eta: float) -> float:
    return LAMBDA0_UM * math.exp(-eta / 4.0)


def sigma_cu_mpa(eta: float) -> float:
    """Work-hardened Cu matrix flow stress (UTS basis), saturating Voce form."""
    return UTS_CU_ANNEALED + UTS_CU_WH_CAP * (1.0 - math.exp(-eta / ETA_WH))


# --- main model ------------------------------------------------------------
def predict(wt: dict[str, float], eta: float = 0.0,
            c_ss_fe_wt: float | None = None) -> dict[str, float]:
    """Predict wire properties for composition `wt` ({element: wt.%}, Cu balance)
    drawn to true strain `eta`. `c_ss_fe_wt` = wt.% Fe retained in solid solution
    (the anneal-schedule knob; default C_SS_DEFAULT_WT, capped at total Fe).

    Returns dict: rho_uOhm_cm, iacs_pct, kappa_W_mK, uts_MPa, fom_MPa_MSm.
    """
    x_fe = wt.get("Fe", 0.0)
    c_ss = C_SS_DEFAULT_WT if c_ss_fe_wt is None else c_ss_fe_wt
    c_ss = min(c_ss, x_fe)

    # matrix resistivity: cold-worked Cu + solutes in solution + interfaces
    rho_m = RHO_CU_ANNEALED + (RHO_CU_HARD - RHO_CU_ANNEALED) * (1.0 - math.exp(-eta / ETA_WH))
    # Fe in solution (at.% of the matrix ~ at.% overall at these dilutions)
    solutes = dict(wt, Fe=c_ss)
    at = wt_to_at({el: v for el, v in solutes.items() if v > 0})
    for el, dr in DRHO_SOLUTE.items():
        if el == "Cr":
            # Cr precipitates almost completely on aging (the C18150 mechanism)
            rho_m += dr * at.get(el, 0.0) * 0.1
        else:
            rho_m += dr * at.get(el, 0.0)
    f = fe_volume_fraction(x_fe - c_ss)
    if f > 0 and eta > 0:
        rho_m += K_INT / filament_spacing_um(eta)

    # longitudinal parallel mixture with the (resistive) Fe filaments
    sigma_recip = (1.0 - f) / rho_m + f / RHO_FE_BULK
    rho = 1.0 / sigma_recip                                  # uOhm-cm
    sigma_sm = 1.0 / (rho * 1e-8)                            # S/m
    iacs = 100.0 * RHO_CU_ANNEALED / rho
    kappa = L_SP * T_ROOM * sigma_sm + C_SP

    uts = sigma_cu_mpa(eta)
    if f > 0 and eta > 0:
        uts += K_HP * math.sqrt(f) / math.sqrt(filament_spacing_um(eta))
    # microalloy bumps (v0 placeholders; refit on round-0 hardness)
    uts += 30.0 * wt.get("Ag", 0.0) + 60.0 * wt.get("Cr", 0.0)

    return {
        "rho_uOhm_cm": rho,
        "iacs_pct": iacs,
        "kappa_W_mK": kappa,
        "uts_MPa": uts,
        "fom_MPa_MSm": uts * sigma_sm / 1e6,
    }
