from __future__ import annotations

import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ideas.schema import IdeaRationale, append_result_row
from prepare import OOSResult, evaluate_oos, format_result, run_backtest

SYMBOLS = ["QQQ", "XLK", "XLY", "XLE", "MTUM", "QUAL", "HYG", "GLD", "DBC", "TLT", "SMH", "SOXX", "XLC", "XBI", "SGOV"]
MOMENTUM_DAYS = 21
TOP_N = 1
CASH_SYMBOL = "SGOV"
TREND_DAYS = 0
RISK_CAP = 1.0
USE_BLEND_SCORE = False
USE_VOL_ADJUSTED_SCORE = False
USE_SCORE_WEIGHTS = False
USE_SPY_GUARD = False
TEXT_TONE_COLUMN = "hawkish_minus_dovish"

IDEA = IdeaRationale(
    idea_id="fomc_hawkish_gold_rates_001",
    title="Fed hawkishness shifts allocation from duration to cash/commodities",
    evidence_type="policy_transmission",
    mechanism="Hawkish Fed language can raise expected real rates, pressure long-duration risk assets, and favor cash or inflation hedges.",
    expected_assets=("TLT", "QQQ", "GLD", "SGOV"),
    feature_inputs=("price_momentum_21d", "fomc_hawkish_minus_dovish"),
    oos_hypothesis="Lagged FOMC tone improves OOS CAGR versus price-only momentum without underperforming DBMF diagnostically.",
    falsification="Reject if OOS CAGR fails to improve, excess OOS CAGR versus DBMF is negative, or validation CAGR is non-positive.",
    references=(
        "Bernanke and Kuttner (2005), What Explains the Stock Market's Reaction to Federal Reserve Policy?",
        "Loughran-McDonald financial sentiment lexicons",
    ),
    human_notes="Transparent public-text overlay on the existing momentum baseline.",
)


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


def latest_text_tone(prices: pd.DataFrame) -> float:
    if TEXT_TONE_COLUMN not in prices.columns:
        return 0.0
    clean = prices[TEXT_TONE_COLUMN].dropna()
    if clean.empty:
        return 0.0
    value = float(clean.iloc[-1])
    return value if math.isfinite(value) else 0.0


def tone_adjusted_score(symbol: str, raw_score: float, text_tone: float) -> float:
    if text_tone > 0.0 and symbol in {"TLT", "QQQ", "XLK", "SMH", "SOXX", "XBI"}:
        return raw_score - min(text_tone, 0.05)
    if text_tone > 0.0 and symbol in {"GLD", "DBC", CASH_SYMBOL}:
        return raw_score + 0.5 * min(text_tone, 0.05)
    if text_tone < 0.0 and symbol in {"TLT", "QQQ", "XLK", "SMH", "SOXX", "XBI"}:
        return raw_score + 0.5 * min(abs(text_tone), 0.05)
    return raw_score


def select_weights(day: pd.Timestamp, prices: pd.DataFrame) -> dict[str, float]:
    del day
    if USE_SPY_GUARD and "SPY" in prices.columns and not is_above_average(prices["SPY"], 200):
        return {CASH_SYMBOL: 1.0}
    text_tone = latest_text_tone(prices)
    scores: list[tuple[float, str]] = []
    for symbol in SYMBOLS:
        if symbol == CASH_SYMBOL or symbol not in prices.columns:
            continue
        if TREND_DAYS > 0 and not is_above_average(prices[symbol], TREND_DAYS):
            continue
        score = momentum_score(prices[symbol])
        if score is not None:
            scores.append((tone_adjusted_score(symbol, score, text_tone), symbol))
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


def git_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "--short", "HEAD"], check=False, capture_output=True, text=True)
    commit = result.stdout.strip()
    return commit if result.returncode == 0 and commit else "uncommitted"


def result_status(oos: OOSResult) -> str:
    if oos.ruined:
        return "ruined"
    return "keep" if oos.passed else "discard"


def append_current_result(oos: OOSResult) -> None:
    row = IDEA.to_results_fields() | {
        "commit": git_commit(),
        "timestamp_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "train_cagr": f"{oos.train_cagr:.6f}",
        "validation_cagr": f"{oos.validation_cagr:.6f}",
        "oos_cagr": f"{oos.oos_cagr:.6f}",
        "benchmark_oos_cagr": f"{oos.benchmark_oos_cagr:.6f}",
        "excess_oos_cagr_vs_dbmf": f"{oos.excess_oos_cagr_vs_dbmf:.6f}",
        "ruined": str(oos.ruined).lower(),
        "status": result_status(oos),
        "description": IDEA.human_notes,
    }
    append_result_row(Path("results.tsv"), row)


def main() -> None:
    IDEA.validate()
    result = run_backtest(select_weights, symbols=SYMBOLS)
    oos = evaluate_oos(select_weights, symbols=SYMBOLS)
    print(format_result(result))
    print(f"train_cagr:       {oos.train_cagr:.6f}")
    print(f"validation_cagr:  {oos.validation_cagr:.6f}")
    print(f"oos_cagr:         {oos.oos_cagr:.6f}")
    print(f"benchmark_oos_cagr: {oos.benchmark_oos_cagr:.6f}")
    print(f"excess_oos_cagr_vs_dbmf: {oos.excess_oos_cagr_vs_dbmf:.6f}")
    print(f"oos_passed:       {str(oos.passed).lower()}")
    append_current_result(oos)


if __name__ == "__main__":
    main()
