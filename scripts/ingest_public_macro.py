#!/usr/bin/env python3
"""
Ingest public macro and market data into ~/.cache/macroresearch/.

Sources:
- FRED fredgraph CSV endpoints (no API key required for public series).
- Yahoo Finance chart endpoint for ETF/FX/index proxies.

This script is intentionally dependency-light and uses only the Python standard library.
It writes category-level CSV files plus metadata/source manifests.
"""
from __future__ import annotations

import csv
import json
import subprocess
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ROOT = Path.home() / ".cache" / "macroresearch"
NOW = datetime.now(timezone.utc).isoformat()

FRED_GROUPS: Dict[str, Dict[str, str]] = {
    "rates/us_treasury_yields.csv": {
        "DGS3MO": "US Treasury 3m yield",
        "DGS2": "US Treasury 2y yield",
        "DGS5": "US Treasury 5y yield",
        "DGS10": "US Treasury 10y yield",
        "DGS30": "US Treasury 30y yield",
        "T10Y2Y": "US 10y minus 2y Treasury spread",
        "T10Y3M": "US 10y minus 3m Treasury spread",
    },
    "rates/us_real_yields_breakevens.csv": {
        "DFII5": "5y TIPS real yield",
        "DFII10": "10y TIPS real yield",
        "T5YIE": "5y breakeven inflation",
        "T10YIE": "10y breakeven inflation",
        "T5YIFR": "5y5y forward inflation expectation rate",
    },
    "inflation/us_inflation.csv": {
        "CPIAUCSL": "CPI all urban consumers",
        "CPILFESL": "Core CPI",
        "PCEPI": "PCE price index",
        "PCEPILFE": "Core PCE price index",
        "MEDCPIM158SFRBCLE": "Median CPI annualized monthly change",
        "T10YIE": "10y breakeven inflation",
        "MICH": "University of Michigan inflation expectation",
    },
    "inflation/us_wages.csv": {
        "CES0500000003": "Average hourly earnings private production nonsupervisory",
        "ECIWAG": "Employment cost index wages and salaries",
    },
    "growth/us_activity.csv": {
        "GDPC1": "Real GDP",
        "INDPRO": "Industrial production index",
        "RSAFS": "Retail sales",
        "HOUST": "Housing starts",
        "PERMIT": "Building permits",
        "NAPM": "ISM manufacturing PMI",
    },
    "growth/us_labor.csv": {
        "PAYEMS": "Nonfarm payrolls",
        "UNRATE": "Unemployment rate",
        "ICSA": "Initial jobless claims",
        "JTSJOL": "Job openings",
    },
    "policy/policy_rates_balance_sheet.csv": {
        "FEDFUNDS": "Effective federal funds rate",
        "EFFR": "Effective federal funds rate daily",
        "SOFR": "Secured overnight financing rate",
        "WALCL": "Federal Reserve total assets",
        "RESPPLLOPNWW": "Reserve balances with Federal Reserve Banks",
        "RRPONTSYD": "Overnight reverse repurchase agreements",
    },
    "fx/major_fx.csv": {
        "DTWEXBGS": "Nominal broad US dollar index",
        "DEXUSEU": "USD per EUR",
        "DEXJPUS": "JPY per USD",
        "DEXUSUK": "USD per GBP",
        "DEXCAUS": "CAD per USD",
        "DEXUSAL": "USD per AUD",
        "DEXSZUS": "CHF per USD",
    },
    "equities/index_prices_fred.csv": {
        "SP500": "S&P 500 index",
        "NASDAQCOM": "NASDAQ Composite",
        "VIXCLS": "CBOE VIX",
        "WILL5000INDFC": "Wilshire 5000 full cap index",
    },
    "commodities/commodities_fred.csv": {
        "DCOILWTICO": "WTI crude oil spot",
        "DCOILBRENTEU": "Brent crude oil spot",
        "DHHNGSP": "Henry Hub natural gas spot",
        "GOLDAMGBD228NLBM": "Gold London AM fix",
        "PCOPPUSDM": "Global copper price",
        "PALLFNFINDEXM": "Global all commodities price index",
    },
    "credit/credit_spreads_conditions.csv": {
        "BAMLC0A0CM": "ICE BofA US corporate OAS",
        "BAMLH0A0HYM2": "ICE BofA US high yield OAS",
        "BAMLEMCBPITRIV": "ICE BofA EM corporate plus total return index value",
        "NFCI": "Chicago Fed National Financial Conditions Index",
        "DRTSCILM": "Senior loan officer tightening standards C&I large/medium firms",
    },
}

YAHOO_GROUPS: Dict[str, List[str]] = {
    "equities/etf_prices_yahoo.csv": [
        "SPY", "QQQ", "IWM", "ACWI", "EFA", "EEM", "EWJ", "FXI", "KWEB", "XLF", "XLK", "XLE", "XLP", "XLU", "RSP",
    ],
    "rates/rates_etf_prices_yahoo.csv": ["SHY", "IEF", "TLT", "TIP"],
    "commodities/commodity_etf_prices_yahoo.csv": ["DBC", "USO", "GLD", "SLV", "CPER"],
    "credit/credit_etf_prices_yahoo.csv": ["LQD", "HYG", "JNK"],
    "fx/fx_etf_prices_yahoo.csv": ["UUP", "FXE", "FXY", "FXA"],
}


def fetch_url(url: str, timeout: int = 15) -> bytes:
    # curl is more reliable than urllib against some HTTP/2 endpoints in this environment.
    proc = subprocess.run(
        ["curl", "--http1.1", "-L", "--fail", "--silent", "--show-error", "--max-time", str(timeout), url],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"curl failed rc={proc.returncode}: {proc.stderr.decode('utf-8', errors='replace')[:300]}")
    return proc.stdout


def parse_fred_csv(text: str, series_id: str) -> List[Tuple[str, str]]:
    rows = []
    reader = csv.DictReader(text.splitlines())
    for row in reader:
        date = row.get("observation_date") or row.get("DATE") or row.get("date")
        val = row.get(series_id)
        if date and val not in (None, "", "."):
            rows.append((date, val))
    return rows


def write_long_csv(path: Path, rows: Iterable[Dict[str, str]], fieldnames: List[str]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
            count += 1
    return count


def ingest_fred() -> List[Dict[str, object]]:
    manifest = []
    for relpath, series_map in FRED_GROUPS.items():
        out_rows: List[Dict[str, str]] = []
        series_status = {}
        for sid, desc in series_map.items():
            url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={urllib.parse.quote(sid)}"
            try:
                text = fetch_url(url).decode("utf-8", errors="replace")
                rows = parse_fred_csv(text, sid)
                for date, value in rows:
                    out_rows.append({"date": date, "series_id": sid, "description": desc, "value": value, "source": "FRED", "source_url": url})
                series_status[sid] = {"ok": True, "rows": len(rows), "latest": rows[-1][0] if rows else None}
            except Exception as e:
                series_status[sid] = {"ok": False, "error": repr(e)}
            time.sleep(0.1)
        count = write_long_csv(ROOT / relpath, out_rows, ["date", "series_id", "description", "value", "source", "source_url"])
        manifest.append({"file": relpath, "source": "FRED", "rows": count, "series": series_status})
    return manifest


def yahoo_chart(symbol: str) -> List[Dict[str, str]]:
    enc = urllib.parse.quote(symbol, safe="")
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{enc}?range=2y&interval=1d&events=history&includeAdjustedClose=true"
    raw = fetch_url(url)
    data = json.loads(raw)
    result = data.get("chart", {}).get("result", [])
    if not result:
        err = data.get("chart", {}).get("error")
        raise RuntimeError(f"Yahoo no result for {symbol}: {err}")
    res = result[0]
    timestamps = res.get("timestamp", [])
    quote = (res.get("indicators", {}).get("quote") or [{}])[0]
    adj = (res.get("indicators", {}).get("adjclose") or [{}])[0].get("adjclose", [])
    rows = []
    for i, ts in enumerate(timestamps):
        date = datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()
        def get(arr):
            return arr[i] if i < len(arr) and arr[i] is not None else ""
        rows.append({
            "date": date,
            "symbol": symbol,
            "open": get(quote.get("open", [])),
            "high": get(quote.get("high", [])),
            "low": get(quote.get("low", [])),
            "close": get(quote.get("close", [])),
            "adj_close": get(adj),
            "volume": get(quote.get("volume", [])),
            "source": "Yahoo Finance",
            "source_url": url,
        })
    return rows


def ingest_yahoo() -> List[Dict[str, object]]:
    manifest = []
    for relpath, symbols in YAHOO_GROUPS.items():
        out_rows: List[Dict[str, str]] = []
        status = {}
        for sym in symbols:
            try:
                rows = yahoo_chart(sym)
                out_rows.extend(rows)
                status[sym] = {"ok": True, "rows": len(rows), "latest": rows[-1]["date"] if rows else None}
            except Exception as e:
                status[sym] = {"ok": False, "error": repr(e)}
            time.sleep(0.1)
        count = write_long_csv(ROOT / relpath, out_rows, ["date", "symbol", "open", "high", "low", "close", "adj_close", "volume", "source", "source_url"])
        manifest.append({"file": relpath, "source": "Yahoo Finance", "rows": count, "symbols": status})
    return manifest


def write_calendar_stub() -> Dict[str, object]:
    # Public no-key economic-calendar feeds are inconsistent. This file records that event-calendar data
    # should be supplemented manually/web during research until a stable source is added.
    relpath = "calendar/event_calendar_stub.csv"
    rows = [{
        "date": datetime.now(timezone.utc).date().isoformat(),
        "event": "Calendar ingestion not configured",
        "source": "local stub",
        "note": "Supplement with official central bank, Treasury auction, and economic calendar sources during research.",
    }]
    count = write_long_csv(ROOT / relpath, rows, ["date", "event", "source", "note"])
    return {"file": relpath, "source": "local stub", "rows": count}


def main() -> None:
    for d in ["rates", "inflation", "growth", "policy", "fx", "equities", "commodities", "credit", "positioning", "calendar", "metadata"]:
        (ROOT / d).mkdir(parents=True, exist_ok=True)

    manifest = {"ingested_at": NOW, "root": str(ROOT), "fred": [], "yahoo": [], "calendar": None, "notes": []}
    manifest["fred"] = ingest_fred()
    manifest["yahoo"] = ingest_yahoo()
    manifest["calendar"] = write_calendar_stub()
    manifest["notes"].append("Positioning data not ingested in this first pass; use CFTC COT web/manual supplement for ideas where positioning is decisive.")
    manifest["notes"].append("Event calendar is a stub; supplement with official calendars during research.")

    meta_path = ROOT / "metadata" / "ingestion_manifest.json"
    meta_path.write_text(json.dumps(manifest, indent=2, sort_keys=True))

    # Coverage summary
    categories = ["rates", "inflation", "growth", "policy", "fx", "equities", "commodities", "credit", "positioning", "calendar"]
    coverage = {}
    for cat in categories:
        files = [p for p in (ROOT / cat).glob("*") if p.is_file()]
        coverage[cat] = {"files": [str(p.relative_to(ROOT)) for p in files], "file_count": len(files)}
    (ROOT / "metadata" / "coverage.json").write_text(json.dumps(coverage, indent=2, sort_keys=True))

    print(json.dumps({"root": str(ROOT), "manifest": str(meta_path), "coverage": coverage}, indent=2))


if __name__ == "__main__":
    main()
