from __future__ import annotations

from pathlib import Path
from typing import cast

import pandas as pd
import pytest

from datasets.ingest_beige_book import ingest_beige_book, parse_beige_book_index
from datasets.ingest_fomc import ingest_fomc
from datasets.ingest_fred import FredSeriesSpec, NeedsPublicDataError, ingest_fred_series
from datasets.ingest_sec import ingest_sec_filings, parse_recent_filings
from datasets.loaders import MissingPublicDataError, load_fomc_events
from datasets.public_features import (
    FeatureUsage,
    load_public_feature_frame,
    validate_claimed_feature_usage,
)
from datasets.text_features import build_beige_book_features, build_fred_features, build_sec_features


def test_fomc_ingest_fetches_index_documents_and_writes_rows(tmp_path: Path) -> None:
    index_url = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
    statement_url = "https://www.federalreserve.gov/newsevents/pressreleases/monetary20240131a.htm"
    minutes_url = "https://www.federalreserve.gov/monetarypolicy/fomcminutes20240131.htm"
    pages = {
        index_url: f"""
        <a href='{statement_url}'>FOMC statement</a>
        <a href='{minutes_url}'>Minutes</a>
        """,
        statement_url: "Inflation remains elevated and policy is restrictive.",
        minutes_url: "Participants discussed uncertainty and downside risks.",
    }

    path = ingest_fomc(tmp_path, lambda url: pages[url])
    frame = pd.read_csv(path, sep="\t")

    assert len(frame.index) == 2
    assert set(frame["document_type"]) == {"statement", "minutes"}
    assert set(frame.columns) >= {"published_at", "url", "text_sha256", "text"}


def test_beige_book_ingest_parses_release_links_and_features(tmp_path: Path) -> None:
    index_url = "https://www.federalreserve.gov/monetarypolicy/beige-book-default.htm"
    doc_url = "https://www.federalreserve.gov/monetarypolicy/beigebook20240117.htm"
    html = f"<a href='{doc_url}'>January 17, 2024 Beige Book</a>"
    pages = {index_url: html, doc_url: "Employment grew while prices and uncertainty rose."}

    links = parse_beige_book_index(html, index_url)
    path = ingest_beige_book(tmp_path, lambda url: pages[url])
    frame = pd.read_csv(path, sep="\t")
    features = build_beige_book_features(frame)

    assert links[0].published_at == "2024-01-17T00:00:00Z"
    assert frame.loc[0, "district"] == "National"
    assert cast(float, features.loc[0, "beige_activity_score"]) > 0.0


def test_sec_and_fred_feature_builders_are_numeric_and_publication_lagged() -> None:
    sec = pd.DataFrame(
        {
            "cik": ["0000320193", "0000320193", "0000789019"],
            "accession_number": ["1", "2", "3"],
            "form_type": ["10-K", "10-Q", "8-K"],
            "accepted_at": ["2024-01-02T12:00:00Z", "2024-01-03T12:00:00Z", "2024-01-03T13:00:00Z"],
            "primary_document_url": ["u1", "u2", "u3"],
        }
    )
    fred = pd.DataFrame(
        {
            "series_id": ["DGS10", "DGS2", "DGS10", "DGS2"],
            "date": ["2024-01-02", "2024-01-02", "2024-01-03", "2024-01-03"],
            "realtime_start": ["2024-01-03", "2024-01-03", "2024-01-04", "2024-01-04"],
            "value": ["4.0", "3.5", "4.1", "3.4"],
            "source_url": ["u", "u", "u", "u"],
        }
    )

    sec_features = build_sec_features(sec)
    fred_features = build_fred_features(fred)

    assert sec_features.loc[0, "sec_10k_count"] == 1.0
    assert "fred_DGS10_minus_DGS2" in fred_features.columns
    assert float(cast(float, fred_features.loc[1, "fred_DGS10_minus_DGS2"])) == pytest.approx(0.7)


def test_load_public_feature_frame_combines_available_families(tmp_path: Path) -> None:
    cache_root = tmp_path / "cache"
    fomc_dir = cache_root / "fomc"
    beige_dir = cache_root / "beige_book"
    sec_dir = cache_root / "sec"
    fred_dir = cache_root / "fred"
    for path in (fomc_dir, beige_dir, sec_dir, fred_dir):
        path.mkdir(parents=True)
    pd.DataFrame(
        {
            "published_at": ["2024-01-03T20:00:00Z"],
            "document_type": ["statement"],
            "url": ["fomc"],
            "text": ["Inflation restrictive uncertainty"],
        }
    ).to_csv(fomc_dir / "fomc_events.tsv", sep="\t", index=False)
    pd.DataFrame(
        {
            "published_at": ["2024-01-03T20:00:00Z"],
            "district": ["National"],
            "url": ["beige"],
            "text": ["Employment expanded but uncertainty rose"],
        }
    ).to_csv(beige_dir / "beige_book_events.tsv", sep="\t", index=False)
    pd.DataFrame(
        {
            "cik": ["0000320193"],
            "accession_number": ["1"],
            "form_type": ["10-K"],
            "accepted_at": ["2024-01-03T20:00:00Z"],
            "primary_document_url": ["sec"],
        }
    ).to_csv(sec_dir / "sec_filings.tsv", sep="\t", index=False)
    pd.DataFrame(
        {
            "series_id": ["DGS10", "DGS2"],
            "date": ["2024-01-03", "2024-01-03"],
            "realtime_start": ["2024-01-03", "2024-01-03"],
            "value": ["4.0", "3.5"],
            "source_url": ["fred", "fred"],
        }
    ).to_csv(fred_dir / "fred_observations.tsv", sep="\t", index=False)
    prices = pd.DataFrame({"SPY": [1.0, 1.1, 1.2]}, index=pd.to_datetime(["2024-01-03", "2024-01-04", "2024-01-05"]))

    features = load_public_feature_frame(prices, cache_root=cache_root)

    assert set(features.columns) >= {
        "fomc_hawkish_minus_dovish",
        "beige_beige_activity_score",
        "sec_sec_10k_count",
        "fred_fred_DGS10_minus_DGS2",
    }
    assert pd.isna(features.loc[pd.Timestamp("2024-01-03"), "fomc_hawkish_minus_dovish"])
    assert cast(float, features.loc[pd.Timestamp("2024-01-04"), "fomc_hawkish_minus_dovish"]) > 0.0


def test_missing_loader_artifact_reports_needs_data(tmp_path: Path) -> None:
    with pytest.raises(MissingPublicDataError, match="needs_data"):
        load_fomc_events(cache_root=tmp_path)


def test_claimed_feature_usage_rejects_missing_non_price_features() -> None:
    usage = FeatureUsage(
        claimed_inputs=("fomc_hawkish_minus_dovish", "price_momentum_21d"),
        actual_columns=("price_momentum_21d",),
        source_artifacts=("market/SPY.csv",),
    )

    with pytest.raises(ValueError, match="claimed non-price features were not used"):
        validate_claimed_feature_usage(usage)


def test_sec_parser_and_fred_ingestion_needs_data_behavior(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    payload = {
        "filings": {
            "recent": {
                "accessionNumber": ["0000320193-24-000001"],
                "form": ["10-K"],
                "acceptanceDateTime": ["2024-01-31T12:00:00.000Z"],
                "primaryDocument": ["aapl-20231230.htm"],
            }
        }
    }

    filings = parse_recent_filings(payload, "0000320193", {"10-K"}, 4)

    assert filings[0].primary_document_url.endswith("/aapl-20231230.htm")
    with pytest.raises(NeedsPublicDataError, match="needs_data"):
        ingest_fred_series((FredSeriesSpec("DGS10", "10-year Treasury yield", True),), tmp_path, api_key=None)
    assert ingest_sec_filings(("0000320193",), tmp_path, lambda _url: payload).exists()


def test_fred_ingestion_redacts_api_key_in_artifact(tmp_path: Path) -> None:
    payload = {
        "observations": [
            {"date": "2024-01-01", "realtime_start": "2024-01-02", "value": "4.0"},
        ]
    }

    path = ingest_fred_series(
        (FredSeriesSpec("DGS10", "10-year Treasury yield", True),),
        tmp_path,
        api_key="secret-key",
        fetcher=lambda _url: payload,
    )

    text = path.read_text()
    assert "secret-key" not in text
    assert "api_key=" in text
