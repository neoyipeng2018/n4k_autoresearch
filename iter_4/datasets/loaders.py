from __future__ import annotations

from pathlib import Path

import pandas as pd

from datasets.cache import BEIGE_BOOK_DIR, CACHE_ROOT, FOMC_DIR, FRED_DIR, SEC_DIR


class MissingPublicDataError(RuntimeError):
    pass


def artifact_path(cache_root: Path, dataset_dir: str, filename: str) -> Path:
    return cache_root / dataset_dir / filename


def read_tsv(path: Path, required_columns: set[str]) -> pd.DataFrame:
    if not path.exists():
        raise MissingPublicDataError(f"needs_data: missing public data artifact: {path}")
    frame = pd.read_csv(path, sep="\t")
    missing = required_columns.difference(frame.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {', '.join(sorted(missing))}")
    return frame


def load_fomc_events(cache_root: Path = CACHE_ROOT) -> pd.DataFrame:
    default_path = FOMC_DIR / "fomc_events.tsv"
    path = default_path if cache_root == CACHE_ROOT else artifact_path(cache_root, "fomc", "fomc_events.tsv")
    return read_tsv(path, {"published_at", "document_type", "url", "text"})


def load_beige_book_events(cache_root: Path = CACHE_ROOT) -> pd.DataFrame:
    default_path = BEIGE_BOOK_DIR / "beige_book_events.tsv"
    path = default_path if cache_root == CACHE_ROOT else artifact_path(cache_root, "beige_book", "beige_book_events.tsv")
    return read_tsv(path, {"published_at", "district", "url", "text"})


def load_sec_filings(cache_root: Path = CACHE_ROOT) -> pd.DataFrame:
    default_path = SEC_DIR / "sec_filings.tsv"
    path = default_path if cache_root == CACHE_ROOT else artifact_path(cache_root, "sec", "sec_filings.tsv")
    return read_tsv(path, {"cik", "accession_number", "form_type", "accepted_at", "primary_document_url"})


def load_fred_observations(cache_root: Path = CACHE_ROOT) -> pd.DataFrame:
    default_path = FRED_DIR / "fred_observations.tsv"
    path = default_path if cache_root == CACHE_ROOT else artifact_path(cache_root, "fred", "fred_observations.tsv")
    return read_tsv(path, {"series_id", "date", "realtime_start", "value"})
