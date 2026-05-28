from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode

FRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"
ALFRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"


@dataclass(frozen=True)
class FredSeriesSpec:
    series_id: str
    description: str
    vintage_safe: bool


def fred_observations_url(series_id: str, api_key: str, realtime_start: str | None = None) -> str:
    params = {"series_id": series_id, "api_key": api_key, "file_type": "json"}
    if realtime_start is not None:
        params["realtime_start"] = realtime_start
        params["realtime_end"] = realtime_start
    return FRED_OBSERVATIONS_URL + "?" + urlencode(params)
