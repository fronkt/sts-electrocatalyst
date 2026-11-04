"""The exporter's --window filter: a C_dl CV that starts from and returns to open circuit keeps only the cycling
between its programmed vertices."""
import numpy as np
import pytest

pytest.importorskip("galvani")
from echem.s8_mpr_export import in_window  # noqa: E402


def test_window_drops_open_circuit_legs():
    # 0.05 -> -0.60 -> -0.40 -> -0.60 -> -0.40 -> 0.05 V, the shape of the 2026-11-03 code-E C_dl files
    legs = [np.linspace(0.05, -0.60, 66), np.linspace(-0.60, -0.40, 21)[1:], np.linspace(-0.40, -0.60, 21)[1:],
            np.linspace(-0.60, -0.40, 21)[1:], np.linspace(-0.40, 0.05, 46)[1:]]
    c = np.concatenate(legs)
    arrays = {"control/V": c, "Ewe/V": c + 1e-4, "<I>/mA": np.arange(len(c), dtype=float)}
    out, kept, dropped = in_window(arrays, -0.60, -0.40)
    assert kept + dropped == len(c)
    assert out["control/V"].min() >= -0.601 and out["control/V"].max() <= -0.399
    assert len(out["Ewe/V"]) == kept == len(out["<I>/mA"])
    assert dropped == int(((c > -0.399) | (c < -0.601)).sum())


def test_window_order_of_bounds_and_missing_column():
    arrays = {"control/V": np.array([-0.7, -0.5, -0.3])}
    assert in_window(arrays, -0.4, -0.6)[1] == 1
    with pytest.raises(ValueError):
        in_window({"Ewe/V": np.zeros(3)}, -0.6, -0.4)
