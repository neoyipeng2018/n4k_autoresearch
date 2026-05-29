from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from collections.abc import Iterable

import pandas as pd

from prepare import WeightSelector, evaluate_oos


@dataclass(frozen=True)
class StrategyParams:
    lookback_days: int
    top_n: int
    universe_name: str
    symbols: tuple[str, ...]
    rebalance_day: int = 1
    score_weighted: bool = True
    risk_cap: float = 1.0
    cash_symbol: str = "SGOV"


def lookback_return(series: pd.Series, lookback_days: int) -> float | None:
    clean = series.dropna()
    if len(clean) <= lookback_days:
        return None
    start = float(clean.iloc[-lookback_days - 1])
    end = float(clean.iloc[-1])
    if start <= 0.0 or end <= 0.0:
        return None
    return end / start - 1.0


def make_momentum_selector(params: StrategyParams) -> WeightSelector:
    def select_weights(day: pd.Timestamp, prices: pd.DataFrame) -> dict[str, float]:
        if params.rebalance_day > 1 and int(day.day) > params.rebalance_day:
            return {params.cash_symbol: 1.0}
        scores: list[tuple[float, str]] = []
        for symbol in params.symbols:
            if symbol == params.cash_symbol or symbol not in prices.columns:
                continue
            score = lookback_return(prices[symbol], params.lookback_days)
            if score is not None and score > 0.0:
                scores.append((score, symbol))
        selected = sorted(scores, reverse=True)[: params.top_n]
        if not selected:
            return {params.cash_symbol: 1.0}
        if params.score_weighted:
            total = sum(score for score, _symbol in selected)
            if total <= 0.0:
                return {params.cash_symbol: 1.0}
            weights = {symbol: params.risk_cap * score / total for score, symbol in selected}
        else:
            weights = {symbol: params.risk_cap / len(selected) for _score, symbol in selected}
        if params.risk_cap < 1.0:
            weights[params.cash_symbol] = 1.0 - params.risk_cap
        return weights

    return select_weights


def run_robustness_grid(params_grid: Iterable[StrategyParams], prices: pd.DataFrame | None = None) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for params in params_grid:
        result = evaluate_oos(make_momentum_selector(params), symbols=list(params.symbols), prices=prices)
        row: dict[str, object] = asdict(params)
        row.update(
            {
                "symbols": ",".join(params.symbols),
                "train_cagr": result.train_cagr,
                "validation_cagr": result.validation_cagr,
                "oos_cagr": result.oos_cagr,
                "benchmark_oos_cagr": result.benchmark_oos_cagr,
                "excess_oos_cagr_vs_dbmf": result.excess_oos_cagr_vs_dbmf,
                "ruined": result.ruined,
                "passed": result.passed,
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_robust_regions(results: pd.DataFrame, group_columns: list[str]) -> pd.DataFrame:
    clean = results.loc[~results["ruined"].astype(bool)].copy()
    grouped = clean.groupby(group_columns, dropna=False)
    summary = grouped.agg(
        trial_count=("validation_cagr", "size"),
        median_validation_cagr=("validation_cagr", "median"),
        p10_validation_cagr=("validation_cagr", lambda values: float(values.quantile(0.10))),
        p90_validation_cagr=("validation_cagr", lambda values: float(values.quantile(0.90))),
        median_oos_cagr=("oos_cagr", "median"),
    ).reset_index()
    summary["robustness_score"] = summary["median_validation_cagr"] * summary["trial_count"].clip(upper=2)
    return summary.sort_values(["trial_count", "median_validation_cagr"], ascending=[False, False]).reset_index(drop=True)


def write_robustness_tsv(frame: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, sep="	", index=False)
    return path
