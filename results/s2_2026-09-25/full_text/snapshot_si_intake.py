"""Reconstruct the completed-round v5 intake, without September 29 adjudications.

The current state files are never overwritten. This anchors audits to merged final
decisions, not raw reader labels or v5_final_before_si.
"""
import builtins
from unittest.mock import patch

import current_state


def main():
    actual_open = builtins.open

    def redirected_open(file, mode="r", *args, **kwargs):
        if mode.startswith("w"):
            for suffix in ("csv", "json"):
                original = current_state.HERE / "reconcile" / ("current_state." + suffix)
                if str(file) == str(original):
                    file = original.with_name("si_verification_intake_2026-09-29." + suffix)
                    break
        return actual_open(file, mode, *args, **kwargs)

    with patch("current_state.si_adjudications", return_value={}), patch("builtins.open", side_effect=redirected_open):
        current_state.main()


if __name__ == "__main__":
    main()
