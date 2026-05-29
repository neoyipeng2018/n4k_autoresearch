from __future__ import annotations

from pathlib import Path

import pandas as pd

from datasets.artifacts import PublicDataArtifact, write_artifact_manifest
from datasets.ingest_beige_book import normalize_beige_book_document, write_beige_book_events
from datasets.ingest_fomc import FomcDocument, write_fomc_events
from datasets.ingest_fred import FredObservation, write_fred_observations
from datasets.ingest_sec import EdgarFiling, write_sec_filings


def test_write_fomc_events_uses_supplied_fetcher_and_hash(tmp_path: Path) -> None:
    docs = [FomcDocument("https://example.com/fomc20240131.htm", "FOMC statement", "statement")]

    path = write_fomc_events(docs, tmp_path, lambda url: "Inflation remains elevated.")
    frame = pd.read_csv(path, sep="	")

    assert frame.loc[0, "published_at"] == "2024-01-31T00:00:00Z"
    assert len(str(frame.loc[0, "text_sha256"])) == 64


def test_public_artifact_manifest_round_trips(tmp_path: Path) -> None:
    artifact = PublicDataArtifact("fomc_text", "https://example.com", "2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z", "x.tsv", "a" * 64, 1, True)

    path = write_artifact_manifest([artifact], tmp_path / "manifest.tsv")
    frame = pd.read_csv(path, sep="	")

    assert frame.loc[0, "dataset"] == "fomc_text"


def test_other_public_dataset_writers_create_expected_columns(tmp_path: Path) -> None:
    beige = normalize_beige_book_document("2024-01-17T00:00:00Z", "Beige Book", "https://example.com", " A  B ", district="National")
    beige_path = write_beige_book_events([beige], tmp_path)
    fred_path = write_fred_observations([FredObservation("DGS10", "2024-01-01", "2024-01-02", "4.0", "https://fred")], tmp_path)
    sec_path = write_sec_filings([EdgarFiling("0000320193", "0001", "10-K", "2024-01-01T12:00:00Z", "https://sec")], tmp_path)

    assert set(pd.read_csv(beige_path, sep="	").columns) >= {"published_at", "district", "text_sha256", "text"}
    assert set(pd.read_csv(fred_path, sep="	").columns) >= {"series_id", "date", "realtime_start", "value"}
    assert set(pd.read_csv(sec_path, sep="	").columns) >= {"cik", "accession_number", "accepted_at"}
