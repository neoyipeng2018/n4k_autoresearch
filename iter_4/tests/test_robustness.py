from __future__ import annotations

import pandas as pd

from research.robustness import StrategyParams, make_momentum_selector, summarize_robust_regions


def test_make_momentum_selector_score_weights_positive_top_two() -> None:
    dates = pd.bdate_range("2024-01-01", periods=25)
    prices = pd.DataFrame(
        {
            "AAA": [100.0 + index for index in range(25)],
            "BBB": [100.0 + index * 0.5 for index in range(25)],
            "CCC": [100.0 - index * 0.1 for index in range(25)],
            "SGOV": [100.0 for _index in range(25)],
        },
        index=dates,
    )
    params = StrategyParams(lookback_days=21, top_n=2, universe_name="test", symbols=("AAA", "BBB", "CCC", "SGOV"), rebalance_day=1, score_weighted=True, risk_cap=1.0, cash_symbol="SGOV")

    weights = make_momentum_selector(params)(dates[-1], prices)

    assert set(weights) == {"AAA", "BBB"}
    assert weights["AAA"] > weights["BBB"]
    assert round(sum(weights.values()), 10) == 1.0


def test_summarize_robust_regions_prefers_median_not_top_row() -> None:
    frame = pd.DataFrame(
        {
            "family": ["spike", "robust", "robust"],
            "validation_cagr": [1.00, 0.20, 0.22],
            "oos_cagr": [0.0, 0.18, 0.19],
            "ruined": [False, False, False],
        }
    )

    summary = summarize_robust_regions(frame, ["family"])

    assert summary.iloc[0]["family"] == "robust"
