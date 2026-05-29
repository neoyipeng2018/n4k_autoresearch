from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class PriceCoverageIssue:
    symbol: str
    severity: str
    message: str
    first_valid_date: str | None
    last_valid_date: str | None
    missing_count: int
    longest_missing_streak: int


def max_consecutive_missing(series: pd.Series) -> int:
    longest = 0
    current = 0
    for missing in series.isna().to_list():
        if bool(missing):
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def inspect_price_coverage(prices: pd.DataFrame, max_missing_streak: int = 5) -> list[PriceCoverageIssue]:
    issues: list[PriceCoverageIssue] = []
    for symbol in prices.columns:
        series = prices[symbol]
        valid = series.dropna()
        if valid.empty:
            issues.append(PriceCoverageIssue(symbol, "error", "no valid prices", None, None, int(series.isna().sum()), len(series)))
            continue
        active = series.loc[valid.index[0] : valid.index[-1]]
        streak = max_consecutive_missing(active)
        if streak >= max_missing_streak:
            issues.append(PriceCoverageIssue(symbol, "error", "long missing price stretch inside active history", str(valid.index[0].date()), str(valid.index[-1].date()), int(active.isna().sum()), streak))
        elif int(active.isna().sum()) > 0:
            issues.append(PriceCoverageIssue(symbol, "warning", "missing prices inside active history", str(valid.index[0].date()), str(valid.index[-1].date()), int(active.isna().sum()), streak))
    return issues


def price_coverage_manifest(prices: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for symbol in prices.columns:
        valid = prices[symbol].dropna()
        rows.append({"symbol": symbol, "first_valid_date": str(valid.index[0].date()) if not valid.empty else "", "last_valid_date": str(valid.index[-1].date()) if not valid.empty else "", "observations": int(valid.count()), "missing_count": int(prices[symbol].isna().sum()), "longest_missing_streak": max_consecutive_missing(prices[symbol])})
    return pd.DataFrame(rows)


def write_price_coverage_manifest(prices: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    price_coverage_manifest(prices).to_csv(path, sep="	", index=False)
    return path
