from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

DatasetKind = Literal["price", "text", "numeric", "metadata"]

CACHE_ROOT = Path.home() / ".cache" / "macroresearch" / "iter_3"


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    kind: DatasetKind
    source_url: str
    cache_subdir: str
    timestamp_column: str
    point_in_time_safe: bool
    license_note: str
    description: str


DATASETS: dict[str, DatasetSpec] = {
    "prices_yahoo": DatasetSpec(
        name="prices_yahoo",
        kind="price",
        source_url="https://query1.finance.yahoo.com/v8/finance/chart/",
        cache_subdir="market",
        timestamp_column="date",
        point_in_time_safe=True,
        license_note="Yahoo Finance adjusted-close data; cache locally for reproducibility.",
        description="Daily adjusted-close ETF prices used for tradable assets and DBMF benchmark.",
    ),
    "fomc_text": DatasetSpec(
        name="fomc_text",
        kind="text",
        source_url="https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
        cache_subdir="fomc",
        timestamp_column="published_at",
        point_in_time_safe=True,
        license_note="Federal Reserve public website text; use publication timestamp, not meeting date.",
        description="FOMC statements and minutes text for lagged monetary-policy tone features.",
    ),
    "beige_book_text": DatasetSpec(
        name="beige_book_text",
        kind="text",
        source_url="https://www.federalreserve.gov/monetarypolicy/beigebook/",
        cache_subdir="beige_book",
        timestamp_column="published_at",
        point_in_time_safe=True,
        license_note="Federal Reserve public website text; use release date only.",
        description="Beige Book regional anecdotal macro text for growth, inflation, and labor pressure.",
    ),
    "sec_edgar": DatasetSpec(
        name="sec_edgar",
        kind="text",
        source_url="https://www.sec.gov/edgar/search/",
        cache_subdir="sec",
        timestamp_column="accepted_at",
        point_in_time_safe=True,
        license_note="SEC EDGAR public filings; use accepted datetime and respect SEC fair-access rules.",
        description="Company filing text and metadata for sector-level risk and uncertainty features.",
    ),
    "fred_numeric": DatasetSpec(
        name="fred_numeric",
        kind="numeric",
        source_url="https://fred.stlouisfed.org/",
        cache_subdir="fred",
        timestamp_column="date",
        point_in_time_safe=False,
        license_note="FRED public data; prefer ALFRED vintages where available.",
        description="Macro numeric series such as rates, spreads, inflation, and labor indicators.",
    ),
}
