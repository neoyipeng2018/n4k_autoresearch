from __future__ import annotations

from pathlib import Path

import pandas as pd

from prepare import fetch_yahoo_prices
from datasets.registry import CACHE_ROOT

MARKET_DIR = CACHE_ROOT / "market"


def price_cache_path(symbol: str, market_dir: Path = MARKET_DIR) -> Path:
    return market_dir / f"{symbol}.csv"


def write_price_cache(symbol: str, prices: pd.Series, market_dir: Path = MARKET_DIR) -> Path:
    path = price_cache_path(symbol, market_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame({"date": prices.index, "adj_close": prices.astype(float).to_numpy()})
    frame.to_csv(path, index=False)
    return path


def ingest_prices(symbols: list[str], market_dir: Path = MARKET_DIR) -> list[Path]:
    paths: list[Path] = []
    for symbol in symbols:
        prices = fetch_yahoo_prices(symbol)
        paths.append(write_price_cache(symbol, prices, market_dir))
    return paths
