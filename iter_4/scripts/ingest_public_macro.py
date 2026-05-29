from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from datasets.artifacts import PublicDataArtifact, write_artifact_manifest
from datasets.cache import FRED_DIR, MANIFEST_PATH, SEC_DIR
from datasets.ingest_beige_book import BEIGE_BOOK_INDEX_URL, ingest_beige_book
from datasets.ingest_fomc import FOMC_INDEX_URL, ingest_fomc
from datasets.ingest_fred import NeedsPublicDataError, default_fred_specs, ingest_fred_series
from datasets.ingest_prices import ingest_prices
from datasets.ingest_sec import DEFAULT_SEC_CIKS, SEC_SUBMISSIONS_BASE, ingest_sec_filings
from datasets.http_cache import cached_json_fetcher, cached_text_fetcher
from prepare import BENCHMARK_SYMBOL, DEFAULT_UNIVERSE


def load_local_env(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip():
            os.environ.setdefault(key.strip(), value.strip())


def refresh_public_data() -> bool:
    return os.environ.get("PUBLIC_DATA_REFRESH") == "1"


def text_fetcher() -> Callable[[str], str]:
    refresh = refresh_public_data()

    def fetch(url: str) -> str:
        return cached_text_fetcher(url, refresh=refresh)

    return fetch


def json_fetcher() -> Callable[[str], object]:
    refresh = refresh_public_data()

    def fetch(url: str) -> object:
        return cached_json_fetcher(url, refresh=refresh)

    return fetch


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def row_count(path: Path) -> int:
    if path.suffix == ".csv":
        return len(pd.read_csv(path).index)
    return len(pd.read_csv(path, sep="\t").index)


def artifact(dataset: str, source_url: str, started_at: str, finished_at: str, path: Path, point_in_time_safe: bool) -> PublicDataArtifact:
    return PublicDataArtifact(
        dataset=dataset,
        source_url=source_url,
        started_at=started_at,
        finished_at=finished_at,
        artifact_path=str(path),
        sha256=file_sha256(path),
        row_count=row_count(path),
        point_in_time_safe=point_in_time_safe,
    )


def ingest_price_artifacts(started_at: str) -> list[PublicDataArtifact]:
    symbols = list(dict.fromkeys([*DEFAULT_UNIVERSE, BENCHMARK_SYMBOL]))
    paths = ingest_prices(symbols)
    finished_at = utc_now()
    return [artifact("prices_yahoo", symbol, started_at, finished_at, path, True) for symbol, path in zip(symbols, paths)]


def main() -> None:
    load_local_env()
    started_at = utc_now()
    artifacts: list[PublicDataArtifact] = []
    artifacts.extend(ingest_price_artifacts(started_at))
    cached_text = text_fetcher()
    for dataset, source_url, ingest, point_in_time_safe in (
        ("fomc_text", FOMC_INDEX_URL, ingest_fomc, True),
        ("beige_book_text", BEIGE_BOOK_INDEX_URL, ingest_beige_book, True),
    ):
        try:
            path = ingest(fetcher=cached_text)
        except Exception as exc:
            print(f"needs_data: {dataset}: {exc}")
            continue
        artifacts.append(artifact(dataset, source_url, started_at, utc_now(), path, point_in_time_safe))
        print(path)
    try:
        sec_path = ingest_sec_filings(DEFAULT_SEC_CIKS, SEC_DIR, fetcher=json_fetcher())
    except Exception as exc:
        print(f"needs_data: sec_edgar: {exc}")
    else:
        artifacts.append(artifact("sec_edgar", SEC_SUBMISSIONS_BASE, started_at, utc_now(), sec_path, True))
        print(sec_path)
    try:
        fred_path = ingest_fred_series(default_fred_specs(), FRED_DIR, fetcher=json_fetcher())
        artifacts.append(artifact("fred_numeric", "FRED/ALFRED observations API", started_at, utc_now(), fred_path, True))
        print(fred_path)
    except NeedsPublicDataError as exc:
        print(str(exc))
    except Exception as exc:
        print(f"needs_data: fred_numeric: {exc}")
    manifest = write_artifact_manifest(artifacts, MANIFEST_PATH)
    print(manifest)


if __name__ == "__main__":
    main()
