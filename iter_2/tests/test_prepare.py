from __future__ import annotations

import math

import pandas as pd

from prepare import (
    BENCHMARK_SYMBOL,
    RUIN_EQUITY_THRESHOLD,
    calculate_cagr,
    calculate_dbmf_benchmark,
    detect_ruin,
    format_result,
    run_backtest,
)


def make_prices() -> pd.DataFrame:
    dates = pd.bdate_range("2020-01-01", periods=320)
    spy = [100.0 + index * 0.10 for index in range(len(dates))]
    qqq = [100.0 + index * 0.20 for index in range(len(dates))]
    sgov = [100.0 + index * 0.01 for index in range(len(dates))]
    dbmf = [100.0 + index * 0.05 for index in range(len(dates))]
    return pd.DataFrame(
        {
            "SPY": spy,
            "QQQ": qqq,
            "SGOV": sgov,
            BENCHMARK_SYMBOL: dbmf,
        },
        index=dates,
    )


def test_calculate_cagr_is_zero_for_constant_equity() -> None:
    dates = pd.date_range("2020-01-01", periods=366, freq="D")
    equity = pd.Series([1.0] * len(dates), index=dates)
    assert calculate_cagr(equity) == 0.0


def test_calculate_cagr_is_positive_for_growth() -> None:
    dates = pd.date_range("2020-01-01", "2021-01-01", freq="D")
    equity = pd.Series([1.0, 1.21], index=[dates[0], dates[-1]])
    assert math.isclose(calculate_cagr(equity), 0.21, rel_tol=0.005)


def test_calculate_cagr_is_negative_for_decline() -> None:
    equity = pd.Series([1.0, 0.81], index=pd.to_datetime(["2020-01-01", "2021-01-01"]))
    assert calculate_cagr(equity) < 0.0


def test_calculate_cagr_returns_nan_for_invalid_curve() -> None:
    equity = pd.Series([1.0], index=pd.to_datetime(["2020-01-01"]))
    assert math.isnan(calculate_cagr(equity))


def test_detect_ruin_uses_threshold_and_invalid_values() -> None:
    safe = pd.Series([1.0, RUIN_EQUITY_THRESHOLD + 0.01], index=pd.date_range("2020-01-01", periods=2))
    ruined = pd.Series([1.0, RUIN_EQUITY_THRESHOLD], index=pd.date_range("2020-01-01", periods=2))
    assert not detect_ruin(safe, 0.01)
    assert detect_ruin(ruined, 0.01)
    assert detect_ruin(safe, float("nan"))


def test_dbmf_benchmark_uses_matched_window() -> None:
    prices = make_prices()
    aligned_index = prices.index[20:200]
    benchmark = calculate_dbmf_benchmark(prices, aligned_index)
    assert benchmark.equity.index[0] == aligned_index[0]
    assert benchmark.equity.index[-1] == aligned_index[-1]
    assert benchmark.equity.iloc[0] == 1.0
    assert math.isfinite(benchmark.cagr)


def test_run_backtest_uses_prior_day_signal_without_lookahead() -> None:
    prices = make_prices()
    seen_last_days: list[pd.Timestamp] = []

    def selector(day: pd.Timestamp, prices: pd.DataFrame) -> dict[str, float]:
        seen_last_days.append(prices.index[-1])
        assert prices.index[-1] == day
        return {"QQQ": 1.0}

    result = run_backtest(selector, symbols=["SPY", "QQQ", "SGOV"], prices=prices)
    assert seen_last_days
    assert not result.ruined
    assert math.isfinite(result.cagr)
    assert math.isfinite(result.dbmf_cagr)


def test_format_result_contains_parseable_required_lines() -> None:
    prices = make_prices()

    def selector(day: pd.Timestamp, prices: pd.DataFrame) -> dict[str, float]:
        del day, prices
        return {"SPY": 1.0}

    output = format_result(run_backtest(selector, symbols=["SPY", "SGOV"], prices=prices))
    assert "cagr:" in output
    assert "ruined:" in output
    assert "dbmf_cagr:" in output
    assert "dbmf_ruined:" in output
    assert "excess_cagr_vs_dbmf:" in output
