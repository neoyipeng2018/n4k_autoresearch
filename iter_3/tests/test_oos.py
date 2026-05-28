from __future__ import annotations

import math

import pandas as pd

from prepare import (
    EvaluationSplit,
    OOSResult,
    evaluate_oos,
    passes_oos_gate,
    run_backtest,
)


def make_split_prices() -> pd.DataFrame:
    dates = pd.bdate_range("2019-01-01", "2025-04-30")
    qqq: list[float] = []
    sgov: list[float] = []
    dbmf: list[float] = []
    qqq_price = 100.0
    sgov_price = 100.0
    dbmf_price = 100.0
    for day in dates:
        if day < pd.Timestamp("2020-01-01"):
            qqq_ret = 0.0001
            dbmf_ret = 0.0001
        elif day < pd.Timestamp("2023-01-01"):
            qqq_ret = 0.0004
            dbmf_ret = 0.0002
        elif day < pd.Timestamp("2025-01-01"):
            qqq_ret = 0.0003
            dbmf_ret = 0.0001
        else:
            qqq_ret = 0.0006
            dbmf_ret = 0.0001
        sgov_ret = 0.00005
        qqq_price *= 1.0 + qqq_ret
        sgov_price *= 1.0 + sgov_ret
        dbmf_price *= 1.0 + dbmf_ret
        qqq.append(qqq_price)
        sgov.append(sgov_price)
        dbmf.append(dbmf_price)
    return pd.DataFrame({"QQQ": qqq, "SGOV": sgov, "DBMF": dbmf}, index=dates)


def qqq_selector(day: pd.Timestamp, prices: pd.DataFrame) -> dict[str, float]:
    del day, prices
    return {"QQQ": 1.0}


def test_evaluate_oos_reports_split_metrics() -> None:
    prices = make_split_prices()
    result = evaluate_oos(qqq_selector, symbols=["QQQ", "SGOV"], prices=prices)
    assert isinstance(result, OOSResult)
    assert result.train_cagr > 0.0
    assert result.validation_cagr > 0.0
    assert result.oos_cagr > result.benchmark_oos_cagr
    assert math.isclose(result.excess_oos_cagr_vs_dbmf, result.oos_cagr - result.benchmark_oos_cagr)
    assert not result.ruined


def test_evaluate_oos_uses_named_split_dates() -> None:
    prices = make_split_prices()
    splits = (
        EvaluationSplit("train", "2020-01-01", "2022-12-31", "train"),
        EvaluationSplit("validation", "2023-01-01", "2024-12-31", "validation"),
        EvaluationSplit("locked_oos", "2025-01-01", None, "oos"),
    )
    result = evaluate_oos(qqq_selector, symbols=["QQQ", "SGOV"], prices=prices, splits=splits)
    direct_oos = run_backtest(qqq_selector, symbols=["QQQ", "SGOV"], prices=prices.loc["2025-01-01":])
    assert math.isclose(result.oos_cagr, direct_oos.cagr)


def test_passes_oos_gate_prioritizes_oos_cagr() -> None:
    result = OOSResult(
        train_cagr=0.40,
        validation_cagr=0.05,
        oos_cagr=0.12,
        benchmark_oos_cagr=0.04,
        excess_oos_cagr_vs_dbmf=0.08,
        ruined=False,
        passed=False,
    )
    assert passes_oos_gate(result, previous_best_oos_cagr=0.10)
    assert not passes_oos_gate(result, previous_best_oos_cagr=0.12)


def test_passes_oos_gate_rejects_ruin_negative_validation_and_dbmf_underperformance() -> None:
    base = OOSResult(
        train_cagr=0.10,
        validation_cagr=0.02,
        oos_cagr=0.08,
        benchmark_oos_cagr=0.03,
        excess_oos_cagr_vs_dbmf=0.05,
        ruined=False,
        passed=False,
    )
    assert not passes_oos_gate(OOSResult(**(base.__dict__ | {"ruined": True})), 0.0)
    assert not passes_oos_gate(OOSResult(**(base.__dict__ | {"validation_cagr": -0.01})), 0.0)
    assert not passes_oos_gate(OOSResult(**(base.__dict__ | {"excess_oos_cagr_vs_dbmf": -0.01})), 0.0)
    assert not passes_oos_gate(OOSResult(**(base.__dict__ | {"oos_cagr": 0.01, "train_cagr": 0.20})), 0.0)
