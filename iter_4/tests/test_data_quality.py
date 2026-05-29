from __future__ import annotations

import pandas as pd
import pytest

from datasets.quality import inspect_price_coverage, max_consecutive_missing
from prepare import run_strategy_equity


class ConstantQqqSelector:
    def __call__(self, day: pd.Timestamp, prices: pd.DataFrame) -> dict[str, float]:
        del day, prices
        return {"QQQ": 1.0}


def test_max_consecutive_missing_counts_longest_streak() -> None:
    series = pd.Series([1.0, None, None, 2.0, None])

    assert max_consecutive_missing(series) == 2


def test_inspect_price_coverage_flags_internal_missing_streak_but_not_pre_inception() -> None:
    dates = pd.bdate_range("2024-01-01", periods=10)
    prices = pd.DataFrame({"SPY": [None, None, 100.0, 101.0, None, None, None, None, 102.0, 103.0]}, index=dates)

    issues = inspect_price_coverage(prices, max_missing_streak=3)

    assert issues[0].symbol == "SPY"
    assert issues[0].severity == "error"


def test_run_strategy_errors_when_holding_missing_active_return() -> None:
    dates = pd.bdate_range("2024-01-01", periods=6)
    prices = pd.DataFrame(
        {
            "QQQ": [100.0, 101.0, 102.0, None, 104.0, 105.0],
            "SGOV": [100.0 for _date in dates],
            "DBMF": [100.0 for _date in dates],
        },
        index=dates,
    )

    with pytest.raises(RuntimeError, match="Missing return for held symbol QQQ"):
        run_strategy_equity(ConstantQqqSelector(), prices, ["QQQ", "SGOV"])
