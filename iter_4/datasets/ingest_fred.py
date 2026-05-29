from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlencode
import os

import pandas as pd

from datasets.cache import FRED_DIR
from datasets.http import fetch_json_url

FRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"
ALFRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"
DEFAULT_FRED_SERIES = (
    "DGS10",
    "DGS2",
    "T10Y2Y",
    "BAA10Y",
)


class NeedsPublicDataError(RuntimeError):
    pass


@dataclass(frozen=True)
class FredSeriesSpec:
    series_id: str
    description: str
    vintage_safe: bool


@dataclass(frozen=True)
class FredObservation:
    series_id: str
    date: str
    realtime_start: str
    value: str
    source_url: str


def fred_observations_url(series_id: str, api_key: str, realtime_start: str | None = None) -> str:
    params = {"series_id": series_id, "api_key": api_key, "file_type": "json"}
    if realtime_start is not None:
        params["realtime_start"] = realtime_start
        params["realtime_end"] = realtime_start
    return FRED_OBSERVATIONS_URL + "?" + urlencode(params)


def observation_items(payload: object) -> list[dict[str, object]]:
    if not isinstance(payload, dict):
        raise ValueError("Expected FRED JSON object")
    observations = payload.get("observations")
    if not isinstance(observations, list):
        raise ValueError("Expected FRED observations list")
    rows: list[dict[str, object]] = []
    for observation in observations:
        if not isinstance(observation, dict):
            raise ValueError("Expected FRED observation object")
        rows.append(observation)
    return rows


def observation_text(row: dict[str, object], key: str) -> str:
    value = row.get(key)
    if isinstance(value, str):
        return value
    raise ValueError(f"Expected FRED text field {key}")


def parse_fred_observations(payload: object, series_id: str, source_url: str) -> list[FredObservation]:
    observations: list[FredObservation] = []
    for row in observation_items(payload):
        value = observation_text(row, "value")
        if value == ".":
            continue
        observations.append(
            FredObservation(
                series_id=series_id,
                date=observation_text(row, "date"),
                realtime_start=observation_text(row, "realtime_start"),
                value=value,
                source_url=source_url,
            )
        )
    return observations


def write_fred_observations(observations: list[FredObservation], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "fred_observations.tsv"
    pd.DataFrame([asdict(observation) for observation in observations]).to_csv(path, sep="\t", index=False)
    return path


def ingest_fred_series(
    specs: tuple[FredSeriesSpec, ...],
    output_dir: Path = FRED_DIR,
    api_key: str | None = None,
    fetcher: Callable[[str], object] = fetch_json_url,
) -> Path:
    resolved_key = api_key or os.environ.get("FRED_API_KEY")
    if not resolved_key:
        raise NeedsPublicDataError("needs_data: FRED_API_KEY is required for FRED/ALFRED ingestion")
    observations: list[FredObservation] = []
    for spec in specs:
        url = fred_observations_url(spec.series_id, resolved_key)
        source_url = fred_observations_url(spec.series_id, "[REDACTED]")
        observations.extend(parse_fred_observations(fetcher(url), spec.series_id, source_url))
    return write_fred_observations(observations, output_dir)


def default_fred_specs() -> tuple[FredSeriesSpec, ...]:
    return tuple(FredSeriesSpec(series_id, f"FRED series {series_id}", True) for series_id in DEFAULT_FRED_SERIES)
