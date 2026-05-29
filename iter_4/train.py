from __future__ import annotations

import math
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from datasets.cache import BEIGE_BOOK_DIR, FOMC_DIR, FRED_DIR, SEC_DIR
from datasets.public_features import FeatureUsage, format_feature_usage
from ideas.schema import IdeaRationale, append_result_row
from prepare import OOSResult, evaluate_oos, format_result, load_prices, run_backtest

SYMBOLS = ['XLK', 'XLY', 'XLC', 'XLI', 'XLF', 'XLV', 'XLP', 'XLU', 'XLE', 'SMH', 'SOXX', 'XBI', 'SGOV']
MOMENTUM_DAYS = 21
TOP_N = 1
CASH_SYMBOL = "SGOV"
TREND_DAYS = 0
RISK_CAP = 1.000000000000
USE_BLEND_SCORE = False
USE_VOL_ADJUSTED_SCORE = False
USE_SCORE_WEIGHTS = True
USE_SPY_GUARD = False
MIN_MOMENTUM = 0.000000000000
VOL_TARGET = 0.000000000000
USE_PUBLIC_GATE = False
BEST_VALIDATION_CAGR = 0.442277000000

IDEA = IdeaRationale(
    idea_id='067_sector_only_top_one_one_month_score_weighted',
    title='Pure sector top-one one-month momentum',
    evidence_type='replication_of_known_anomaly',
    mechanism='Retail-accessible ETF momentum can persist because macro regime information diffuses slowly across investor mandates, and a cash fallback avoids forced risk exposure when recent leadership is weak.',
    expected_assets=('XLK', 'XLY', 'XLC', 'XLI', 'XLF', 'XLV', 'XLP', 'XLU', 'XLE', 'SMH', 'SOXX', 'XBI', 'SGOV'),
    feature_inputs=('price_momentum_21d', 'score_weighted_top1'),
    oos_hypothesis="This retail ETF momentum variant can improve validation CAGR without ruin; locked OOS and DBMF excess remain diagnostics only.",
    falsification="Reject if it crashes, ruins, lacks actual public feature usage when claimed, has non-positive validation CAGR, or fails to improve on the prior best validation CAGR.",
    references=('Jegadeesh and Titman (1993), Returns to Buying Winners and Selling Losers', 'Moskowitz, Ooi, and Pedersen (2012), Time Series Momentum', 'Public Yahoo Finance ETF adjusted-close prices via fixed prepare.py cache'),
    human_notes='Top-1 21-day score-weighted ETF momentum, with SGOV fallback.',
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


def latest_numeric(history: pd.DataFrame, column: str) -> float | None:
    if column not in history.columns:
        return None
    clean = history[column].dropna()
    if clean.empty:
        return None
    value = float(clean.iloc[-1])
    if not math.isfinite(value):
        return None
    return value


def public_signal_multiplier(history: pd.DataFrame) -> float:
    multiplier = 1.0
    hawkish = latest_numeric(history, "fomc_hawkish_minus_dovish")
    uncertainty = latest_numeric(history, "fomc_uncertainty_score")
    beige_activity = latest_numeric(history, "beige_beige_activity_score")
    sec_filing_count = latest_numeric(history, "sec_sec_filing_count")
    if hawkish is not None and hawkish > 0.04:
        multiplier *= 0.75
    if uncertainty is not None and uncertainty > 0.03:
        multiplier *= 0.85
    if beige_activity is not None and beige_activity < 0.0:
        multiplier *= 0.80
    if sec_filing_count is not None and sec_filing_count > 12.0:
        multiplier *= 0.90
    return max(0.25, multiplier)


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
    if selected[0][0] <= MIN_MOMENTUM:
        return {CASH_SYMBOL: 1.0}
    gate_multiplier = public_signal_multiplier(prices) if USE_PUBLIC_GATE else 1.0
    effective_cap = RISK_CAP * gate_multiplier
    if VOL_TARGET > 0.0 and len(selected) == 1:
        selected_symbol = selected[0][1]
        selected_vol = realized_volatility(prices[selected_symbol])
        if selected_vol is not None:
            annualized_vol = selected_vol * math.sqrt(252.0)
            if annualized_vol > 0.0:
                effective_cap = min(effective_cap, VOL_TARGET / annualized_vol)
    if USE_SCORE_WEIGHTS:
        positive_scores = [(max(score, 0.0), symbol) for score, symbol in selected]
        total_score = sum(score for score, _symbol in positive_scores)
        if total_score <= 0.0:
            return {CASH_SYMBOL: 1.0}
        weights = {symbol: effective_cap * score / total_score for score, symbol in positive_scores}
    else:
        risk_weight = effective_cap / len(selected)
        weights = {symbol: risk_weight for _score, symbol in selected}
    if effective_cap < 1.0:
        weights[CASH_SYMBOL] = 1.0 - effective_cap
    return weights


def git_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "--short", "HEAD"], check=False, capture_output=True, text=True)
    commit = result.stdout.strip()
    return commit if result.returncode == 0 and commit else "uncommitted"


def result_status(oos: OOSResult) -> str:
    if oos.ruined:
        return "ruined"
    if oos.validation_cagr <= 0.0:
        return "discard"
    return "keep" if oos.validation_cagr > BEST_VALIDATION_CAGR else "discard"


PUBLIC_FEATURE_PREFIXES = ("fomc_", "beige_", "sec_", "fred_")


def source_artifacts() -> tuple[str, ...]:
    paths = (
        FOMC_DIR / "fomc_events.tsv",
        BEIGE_BOOK_DIR / "beige_book_events.tsv",
        SEC_DIR / "sec_filings.tsv",
        FRED_DIR / "fred_observations.tsv",
    )
    return tuple(str(path) for path in paths if path.exists())


def public_feature_columns(prices: pd.DataFrame) -> tuple[str, ...]:
    return tuple(column for column in prices.columns if column.startswith(PUBLIC_FEATURE_PREFIXES))


def current_feature_usage(prices: pd.DataFrame) -> FeatureUsage:
    return FeatureUsage(
        claimed_inputs=IDEA.feature_inputs,
        actual_columns=public_feature_columns(prices),
        source_artifacts=source_artifacts(),
    )


def append_current_result(oos: OOSResult, usage: FeatureUsage) -> None:
    usage_text = format_feature_usage(usage).replace("\n", " | ")
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
        "description": f"{IDEA.human_notes} | {usage_text}",
    }
    append_result_row(Path("results.tsv"), row)


def main() -> None:
    IDEA.validate()
    prices = load_prices(SYMBOLS)
    usage = current_feature_usage(prices)
    usage_text = format_feature_usage(usage)
    result = run_backtest(select_weights, symbols=SYMBOLS, prices=prices)
    oos = evaluate_oos(select_weights, symbols=SYMBOLS, prices=prices)
    print(format_result(result))
    print(usage_text)
    print(f"train_cagr:       {oos.train_cagr:.6f}")
    print(f"validation_cagr:  {oos.validation_cagr:.6f}")
    print(f"oos_cagr:         {oos.oos_cagr:.6f}")
    print(f"benchmark_oos_cagr: {oos.benchmark_oos_cagr:.6f}")
    print(f"excess_oos_cagr_vs_dbmf: {oos.excess_oos_cagr_vs_dbmf:.6f}")
    print(f"oos_passed:       {str(oos.passed).lower()}")
    if os.environ.get("SKIP_APPEND_RESULT") != "1":
        append_current_result(oos, usage)


if __name__ == "__main__":
    main()
