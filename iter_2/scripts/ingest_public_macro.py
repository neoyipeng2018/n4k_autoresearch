from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlencode

import requests

HTTP_HEADERS = {"User-Agent": "Mozilla/5.0"}

CACHE_ROOT = Path.home() / ".cache" / "macroresearch"
MARKET_DIR = CACHE_ROOT / "market"
METADATA_DIR = CACHE_ROOT / "metadata"
DEFAULT_SYMBOLS = [
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
    "XLK",
    "XLY",
    "XLF",
    "XLE",
    "XLI",
    "XLP",
    "XLU",
    "XLV",
    "XLB",
    "XLRE",
    "DBMF",
]


@dataclass(frozen=True)
class SymbolManifest:
    symbol: str
    rows: int
    start: str
    end: str
    source_url: str
    output_path: str


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


def fetch_yahoo_adjusted_close(symbol: str) -> tuple[list[tuple[str, float]], str]:
    url = yahoo_chart_url(symbol)
    response = requests.get(url, headers=HTTP_HEADERS, timeout=30)
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
    rows: list[tuple[str, float]] = []
    for timestamp, value in zip(timestamps, values):
        if value is None:
            continue
        date = datetime.fromtimestamp(int(timestamp), timezone.utc).date().isoformat()
        rows.append((date, float(value)))
    if not rows:
        raise RuntimeError(f"Yahoo adjusted close data was empty after filtering for {symbol}")
    return rows, url


def write_symbol_csv(symbol: str, rows: list[tuple[str, float]], source_url: str) -> SymbolManifest:
    MARKET_DIR.mkdir(parents=True, exist_ok=True)
    output_path = MARKET_DIR / f"{symbol}.csv"
    with output_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", "adj_close"])
        writer.writerows(rows)
    return SymbolManifest(
        symbol=symbol,
        rows=len(rows),
        start=rows[0][0],
        end=rows[-1][0],
        source_url=source_url,
        output_path=str(output_path),
    )


def ingest_symbols(symbols: Iterable[str]) -> list[SymbolManifest]:
    manifests: list[SymbolManifest] = []
    errors: dict[str, str] = {}
    for symbol in symbols:
        try:
            rows, source_url = fetch_yahoo_adjusted_close(symbol)
            manifests.append(write_symbol_csv(symbol, rows, source_url))
        except Exception as exc:
            errors[symbol] = str(exc)
    if errors:
        message = json.dumps(errors, indent=2, sort_keys=True)
        raise RuntimeError(f"Failed to ingest symbols:\n{message}")
    return manifests


def write_manifest(manifests: list[SymbolManifest]) -> None:
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "cache_root": str(CACHE_ROOT),
        "symbols": [manifest.__dict__ for manifest in manifests],
    }
    output_path = METADATA_DIR / "market_ingestion_manifest.json"
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def main() -> None:
    manifests = ingest_symbols(DEFAULT_SYMBOLS)
    write_manifest(manifests)
    print(f"ingested_symbols: {len(manifests)}")
    print(f"cache_root:       {CACHE_ROOT}")
    print("benchmark:        DBMF")


if __name__ == "__main__":
    main()
