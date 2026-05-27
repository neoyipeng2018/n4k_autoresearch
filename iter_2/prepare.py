from __future__ import annotations

import math
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol
from urllib.parse import urlencode

import pandas as pd
import requests

HTTP_HEADERS = {"User-Agent": "Mozilla/5.0"}

CACHE_ROOT = Path.home() / ".cache" / "macroresearch"
MARKET_DIR = CACHE_ROOT / "market"
DEFAULT_DATA_START = "2018-01-01"
DEFAULT_UNIVERSE = [
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
BENCHMARK_SYMBOL = "DBMF"
RUIN_EQUITY_THRESHOLD = 0.25
TRADING_DAYS_PER_YEAR = 252.0
MIN_WEIGHT = -1.0
MAX_GROSS_EXPOSURE = 2.0

Weights = dict[str, float]


class WeightSelector(Protocol):
    def __call__(self, day: pd.Timestamp, prices: pd.DataFrame) -> Weights: ...


@dataclass(frozen=True)
class BenchmarkResult:
    equity: pd.Series
    cagr: float
    ruined: bool


@dataclass(frozen=True)
class BacktestResult:
    cagr: float
    ruined: bool
    ruin_threshold: float
    dbmf_cagr: float
    dbmf_ruined: bool
    excess_cagr_vs_dbmf: float
    end_multiple: float
    start: str
    end: str
    observations: int
    equity: pd.Series
    dbmf_equity: pd.Series


def yahoo_chart_url(symbol: str) -> str:
    params = urlencode(
        {
            "period1": 0,
            "period2": int(time.time()),
            "interval": "1d",
            "events": "history",
            "includeAdjustedClose": "true",
        }
    )
    return f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?{params}"


def fetch_yahoo_prices(symbol: str) -> pd.Series:
    response = requests.get(yahoo_chart_url(symbol), headers=HTTP_HEADERS, timeout=30)
    response.raise_for_status()
    payload = response.json()
    result = payload["chart"]["result"]
    if not result:
        raise RuntimeError(f"Yahoo returned no chart result for {symbol}")
    chart = result[0]
    timestamps = chart.get("timestamp", [])
    adjclose = chart["indicators"].get("adjclose", [])
    if not timestamps or not adjclose:
        raise RuntimeError(f"Yahoo returned no adjusted close data for {symbol}")
    values = adjclose[0].get("adjclose", [])
    rows: list[tuple[pd.Timestamp, float]] = []
    for timestamp, value in zip(timestamps, values):
        if value is None:
            continue
        day = pd.Timestamp(datetime.fromtimestamp(int(timestamp), timezone.utc).date())
        rows.append((day, float(value)))
    if not rows:
        raise RuntimeError(f"Yahoo adjusted close data was empty after filtering for {symbol}")
    series = pd.Series({day: value for day, value in rows}, name=symbol, dtype="float64")
    return series.sort_index()


def cache_path(symbol: str) -> Path:
    return MARKET_DIR / f"{symbol}.csv"


def read_cached_prices(symbol: str) -> pd.Series | None:
    path = cache_path(symbol)
    if not path.exists():
        return None
    frame = pd.read_csv(path)
    if "date" not in frame.columns:
        raise ValueError(f"Cached file {path} is missing date column")
    price_column = "adj_close" if "adj_close" in frame.columns else "close"
    if price_column not in frame.columns:
        raise ValueError(f"Cached file {path} is missing adj_close or close column")
    series = pd.Series(
        frame[price_column].astype(float).to_numpy(),
        index=pd.to_datetime(frame["date"]),
        name=symbol,
        dtype="float64",
    )
    return series.sort_index()


def load_symbol_prices(symbol: str) -> pd.Series:
    cached = read_cached_prices(symbol)
    if cached is not None and not cached.empty:
        return cached
    return fetch_yahoo_prices(symbol)


def load_prices(symbols: list[str], start: str = DEFAULT_DATA_START) -> pd.DataFrame:
    required_symbols = list(dict.fromkeys([*symbols, BENCHMARK_SYMBOL]))
    series_by_symbol: dict[str, pd.Series] = {}
    failures: dict[str, str] = {}
    for symbol in required_symbols:
        try:
            series_by_symbol[symbol] = load_symbol_prices(symbol)
        except Exception as exc:
            failures[symbol] = str(exc)
    if failures:
        details = "; ".join(f"{symbol}: {message}" for symbol, message in sorted(failures.items()))
        raise RuntimeError(f"Failed to load required market data. Run scripts/ingest_public_macro.py. {details}")
    prices = pd.concat(series_by_symbol.values(), axis=1).sort_index()
    prices = prices.loc[prices.index >= pd.Timestamp(start)]
    prices = prices.dropna(axis=0, how="all")
    if BENCHMARK_SYMBOL not in prices.columns:
        raise RuntimeError("DBMF benchmark prices are required")
    prices = prices.loc[prices[BENCHMARK_SYMBOL].notna()]
    if prices.empty:
        raise RuntimeError("No price data remains after DBMF benchmark alignment")
    return prices


def calculate_cagr(equity_curve: pd.Series) -> float:
    clean = equity_curve.dropna()
    if len(clean) < 2:
        return float("nan")
    start_value = float(clean.iloc[0])
    end_value = float(clean.iloc[-1])
    if start_value <= 0.0 or end_value <= 0.0:
        return float("nan")
    elapsed_days = max((clean.index[-1] - clean.index[0]).days, 1)
    years = elapsed_days / 365.25
    if years <= 0.0:
        return float("nan")
    result = (end_value / start_value) ** (1.0 / years) - 1.0
    return float(result)


def detect_ruin(equity_curve: pd.Series, cagr: float) -> bool:
    clean = equity_curve.dropna()
    if clean.empty or not math.isfinite(cagr):
        return True
    values = clean.astype(float)
    if not values.map(math.isfinite).all():
        return True
    if bool((values <= RUIN_EQUITY_THRESHOLD).any()):
        return True
    if bool((values <= 0.0).any()):
        return True
    return False


def validate_weights(weights: Weights, tradable_symbols: set[str]) -> Weights:
    filtered: Weights = {}
    for symbol, raw_weight in weights.items():
        if symbol not in tradable_symbols:
            continue
        weight = float(raw_weight)
        if not math.isfinite(weight):
            raise ValueError(f"Weight for {symbol} is not finite")
        if weight < MIN_WEIGHT:
            raise ValueError(f"Weight for {symbol} is below allowed minimum")
        if abs(weight) > MAX_GROSS_EXPOSURE:
            raise ValueError(f"Weight for {symbol} exceeds max gross exposure")
        if weight != 0.0:
            filtered[symbol] = weight
    gross = sum(abs(weight) for weight in filtered.values())
    if gross > MAX_GROSS_EXPOSURE:
        raise ValueError("Gross exposure exceeds max gross exposure")
    if not filtered:
        return {"SGOV": 1.0} if "SGOV" in tradable_symbols else {}
    return filtered


def daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change(fill_method=None).replace([math.inf, -math.inf], pd.NA).fillna(0.0)


def run_strategy_equity(
    select_weights: WeightSelector,
    prices: pd.DataFrame,
    symbols: list[str],
) -> pd.Series:
    tradable = [symbol for symbol in symbols if symbol in prices.columns]
    if not tradable:
        raise RuntimeError("No tradable strategy symbols are available")
    returns = daily_returns(prices[tradable])
    equity_values: list[float] = [1.0]
    equity_index: list[pd.Timestamp] = [prices.index[0]]
    current_weights: Weights = {}
    current_month: tuple[int, int] | None = None
    tradable_set = set(tradable)
    for offset in range(1, len(prices.index)):
        previous_day = prices.index[offset - 1]
        day = prices.index[offset]
        month_key = (int(day.year), int(day.month))
        if current_month != month_key:
            history = prices.loc[:previous_day, tradable]
            current_weights = validate_weights(select_weights(previous_day, history), tradable_set)
            current_month = month_key
        day_return = 0.0
        for symbol, weight in current_weights.items():
            if symbol in returns.columns:
                symbol_returns = returns[symbol]
                day_return += weight * float(symbol_returns.iloc[offset])
        next_equity = equity_values[-1] * (1.0 + day_return)
        if not math.isfinite(next_equity) or next_equity <= 0.0:
            next_equity = 0.0
        equity_values.append(next_equity)
        equity_index.append(day)
    return pd.Series(equity_values, index=equity_index, name="strategy", dtype="float64")


def calculate_dbmf_benchmark(prices: pd.DataFrame, aligned_index: pd.Index) -> BenchmarkResult:
    if BENCHMARK_SYMBOL not in prices.columns:
        raise RuntimeError("DBMF benchmark column is missing")
    dbmf = prices.loc[aligned_index, BENCHMARK_SYMBOL].dropna()
    if len(dbmf) < 2:
        raise RuntimeError("DBMF benchmark has insufficient matched-window history")
    equity = (dbmf / float(dbmf.iloc[0])).rename("DBMF")
    cagr = calculate_cagr(equity)
    ruined = detect_ruin(equity, cagr)
    return BenchmarkResult(equity=equity, cagr=cagr, ruined=ruined)


def run_backtest(
    select_weights: WeightSelector,
    symbols: list[str] | None = None,
    start: str = DEFAULT_DATA_START,
    prices: pd.DataFrame | None = None,
) -> BacktestResult:
    universe = DEFAULT_UNIVERSE if symbols is None else symbols
    market_prices = load_prices(universe, start=start) if prices is None else prices.copy()
    market_prices = market_prices.sort_index()
    market_prices = market_prices.loc[market_prices[BENCHMARK_SYMBOL].notna()]
    strategy_equity = run_strategy_equity(select_weights, market_prices, universe)
    benchmark = calculate_dbmf_benchmark(market_prices, strategy_equity.index)
    cagr = calculate_cagr(strategy_equity)
    ruined = detect_ruin(strategy_equity, cagr)
    excess = cagr - benchmark.cagr if math.isfinite(cagr) and math.isfinite(benchmark.cagr) else float("nan")
    return BacktestResult(
        cagr=cagr,
        ruined=ruined,
        ruin_threshold=RUIN_EQUITY_THRESHOLD,
        dbmf_cagr=benchmark.cagr,
        dbmf_ruined=benchmark.ruined,
        excess_cagr_vs_dbmf=excess,
        end_multiple=float(strategy_equity.iloc[-1]),
        start=str(strategy_equity.index[0].date()),
        end=str(strategy_equity.index[-1].date()),
        observations=len(strategy_equity),
        equity=strategy_equity,
        dbmf_equity=benchmark.equity,
    )


def format_result(result: BacktestResult) -> str:
    lines = [
        "---",
        f"cagr:             {result.cagr:.6f}",
        f"ruined:           {str(result.ruined).lower()}",
        f"ruin_threshold:   {result.ruin_threshold:.6f}",
        f"dbmf_cagr:        {result.dbmf_cagr:.6f}",
        f"dbmf_ruined:      {str(result.dbmf_ruined).lower()}",
        f"excess_cagr_vs_dbmf: {result.excess_cagr_vs_dbmf:.6f}",
        f"end_multiple:     {result.end_multiple:.6f}",
        f"start:            {result.start}",
        f"end:              {result.end}",
        f"observations:     {result.observations}",
    ]
    return "\n".join(lines)
