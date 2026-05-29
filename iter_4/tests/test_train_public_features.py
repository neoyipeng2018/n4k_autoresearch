from __future__ import annotations

import pandas as pd

from train import public_signal_multiplier


def test_public_signal_multiplier_reduces_risk_for_hawkish_uncertain_text() -> None:
    history = pd.DataFrame(
        {
            "fomc_hawkish_minus_dovish": [0.2],
            "fomc_uncertainty_score": [0.1],
            "beige_beige_activity_score": [-0.1],
            "sec_sec_filing_count": [2.0],
        },
        index=pd.to_datetime(["2024-01-04"]),
    )

    assert public_signal_multiplier(history) < 1.0


def test_public_signal_multiplier_is_neutral_when_public_columns_absent() -> None:
    history = pd.DataFrame({"SPY": [1.0]}, index=pd.to_datetime(["2024-01-04"]))

    assert public_signal_multiplier(history) == 1.0
