from __future__ import annotations

import pandas as pd

from prepare import DEFAULT_UNIVERSE, format_result, run_backtest

SYMBOLS = [
    "SPY",
    "QQQ",
    "RSP",
    "IWM",
    "USMV",
    "QUAL",
    "MTUM",
    "VLUE",
    "IEF",
    "TLT",
    "SHY",
    "SGOV",
    "GLD",
    "DBC",
    "LQD",
    "HYG",
]
MOMENTUM_DAYS = 126
TOP_N = 1
CASH_SYMBOL = "SGOV"


def lookback_return(series: pd.Series, lookback_days: int) -> float | None:
    clean = series.dropna()
    if len(clean) <= lookback_days:
        return None
    start = float(clean.iloc[-lookback_days - 1])
    end = float(clean.iloc[-1])
    if start <= 0.0 or end <= 0.0:
        return None
    return end / start - 1.0


def select_weights(day: pd.Timestamp, prices: pd.DataFrame) -> dict[str, float]:
    del day
    scores: list[tuple[float, str]] = []
    for symbol in SYMBOLS:
        if symbol not in prices.columns:
            continue
        score = lookback_return(prices[symbol], MOMENTUM_DAYS)
        if score is not None:
            scores.append((score, symbol))
    if not scores:
        return {CASH_SYMBOL: 1.0} if CASH_SYMBOL in DEFAULT_UNIVERSE else {"SPY": 1.0}
    selected = sorted(scores, reverse=True)[:TOP_N]
    if selected[0][0] <= 0.0 and CASH_SYMBOL in prices.columns:
        return {CASH_SYMBOL: 1.0}
    weight = 1.0 / len(selected)
    return {symbol: weight for _score, symbol in selected}


def main() -> None:
    result = run_backtest(select_weights, symbols=SYMBOLS)
    print(format_result(result))


if __name__ == "__main__":
    main()
