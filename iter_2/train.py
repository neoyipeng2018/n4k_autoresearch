from __future__ import annotations

import math

import pandas as pd
from prepare import format_result, run_backtest

SYMBOLS = ['QQQ', 'XLK', 'XLY', 'XLE', 'MTUM', 'QUAL', 'HYG', 'GLD', 'DBC', 'TLT', 'SGOV']
MOMENTUM_DAYS = 30
TOP_N = 1
CASH_SYMBOL = "SGOV"
TREND_DAYS = 0
RISK_CAP = 1.000000000000
USE_BLEND_SCORE = False
USE_VOL_ADJUSTED_SCORE = False
USE_SCORE_WEIGHTS = False
USE_SPY_GUARD = False


def lookback_return(series: pd.Series, lookback_days: int) -> float | None:
    clean = series.dropna()
    if len(clean) <= lookback_days:
        return None
    start = float(clean.iloc[-lookback_days - 1])
    end = float(clean.iloc[-1])
    if start <= 0.0 or end <= 0.0:
        return None
    return end / start - 1.0


def realized_volatility(series: pd.Series, lookback_days: int = 63) -> float | None:
    returns = series.dropna().pct_change(fill_method=None).dropna()
    if len(returns) < lookback_days:
        return None
    vol = float(returns.iloc[-lookback_days:].std())
    if not math.isfinite(vol) or vol <= 0.0:
        return None
    return vol


def is_above_average(series: pd.Series, lookback_days: int) -> bool:
    clean = series.dropna()
    if len(clean) < lookback_days:
        return False
    latest = float(clean.iloc[-1])
    average = float(clean.iloc[-lookback_days:].mean())
    return latest > average


def blended_score(series: pd.Series) -> float | None:
    short = lookback_return(series, 63)
    medium = lookback_return(series, 126)
    long = lookback_return(series, 252)
    if short is None or medium is None or long is None:
        return None
    return 0.25 * short + 0.50 * medium + 0.25 * long


def momentum_score(series: pd.Series) -> float | None:
    raw_score = blended_score(series) if USE_BLEND_SCORE else lookback_return(series, MOMENTUM_DAYS)
    if raw_score is None:
        return None
    if USE_VOL_ADJUSTED_SCORE:
        vol = realized_volatility(series)
        if vol is None:
            return None
        return raw_score / vol
    return raw_score


def select_weights(day: pd.Timestamp, prices: pd.DataFrame) -> dict[str, float]:
    del day
    if USE_SPY_GUARD and "SPY" in prices.columns and not is_above_average(prices["SPY"], 200):
        return {CASH_SYMBOL: 1.0}
    scores: list[tuple[float, str]] = []
    for symbol in SYMBOLS:
        if symbol == CASH_SYMBOL or symbol not in prices.columns:
            continue
        if TREND_DAYS > 0 and not is_above_average(prices[symbol], TREND_DAYS):
            continue
        score = momentum_score(prices[symbol])
        if score is not None:
            scores.append((score, symbol))
    if not scores:
        return {CASH_SYMBOL: 1.0}
    selected = sorted(scores, reverse=True)[:TOP_N]
    if selected[0][0] <= 0.0:
        return {CASH_SYMBOL: 1.0}
    if USE_SCORE_WEIGHTS:
        positive_scores = [(max(score, 0.0), symbol) for score, symbol in selected]
        total_score = sum(score for score, _symbol in positive_scores)
        if total_score <= 0.0:
            return {CASH_SYMBOL: 1.0}
        weights = {symbol: RISK_CAP * score / total_score for score, symbol in positive_scores}
    else:
        risk_weight = RISK_CAP / len(selected)
        weights = {symbol: risk_weight for _score, symbol in selected}
    if RISK_CAP < 1.0:
        weights[CASH_SYMBOL] = 1.0 - RISK_CAP
    return weights


def main() -> None:
    result = run_backtest(select_weights, symbols=SYMBOLS)
    print(format_result(result))


if __name__ == "__main__":
    main()
