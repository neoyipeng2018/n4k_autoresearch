from __future__ import annotations

from typing import cast

import pandas as pd

from datasets.ingest_fomc import parse_fomc_index, normalize_fomc_text
from datasets.text_features import (
    align_event_features_to_prices,
    build_fomc_features,
    lexicon_score,
    tokenize,
)


def test_tokenize_is_deterministic_and_lowercase() -> None:
    assert tokenize("Inflation, INFLATION-risk cut.") == ["inflation", "inflation-risk", "cut"]


def test_lexicon_score_handles_empty_text() -> None:
    assert lexicon_score("", {"hawkish"}, {"dovish"}) == 0.0


def test_lexicon_score_direction() -> None:
    hawkish = lexicon_score("inflation tightening restrictive", {"inflation", "tightening"}, {"cut"})
    dovish = lexicon_score("cut cut weakness", {"inflation", "tightening"}, {"cut", "weakness"})
    assert hawkish > 0
    assert dovish < 0


def test_build_fomc_features_is_deterministic() -> None:
    events = pd.DataFrame(
        {
            "published_at": ["2024-01-31T19:00:00Z"],
            "text": ["Inflation remains elevated. Policy may remain restrictive."],
        }
    )
    first = build_fomc_features(events)
    second = build_fomc_features(events)
    assert first.equals(second)
    assert cast(int, first.loc[0, "token_count"]) > 0
    assert "hawkish_minus_dovish" in first.columns


def test_event_features_do_not_look_ahead() -> None:
    prices = pd.DataFrame(index=pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]))
    events = pd.DataFrame(
        {
            "published_at": ["2024-01-03T20:00:00Z"],
            "hawkish_minus_dovish": [0.5],
        }
    )
    aligned = align_event_features_to_prices(prices, events)
    assert pd.isna(aligned.loc[pd.Timestamp("2024-01-02"), "hawkish_minus_dovish"])
    assert pd.isna(aligned.loc[pd.Timestamp("2024-01-03"), "hawkish_minus_dovish"])
    assert aligned.loc[pd.Timestamp("2024-01-04"), "hawkish_minus_dovish"] == 0.5


def test_parse_fomc_index_fixture() -> None:
    html = """
    <html><body>
      <a href='/newsevents/pressreleases/monetary20240131a.htm'>FOMC statement</a>
      <a href='/monetarypolicy/fomcminutes20240131.htm'>Minutes of the Federal Open Market Committee</a>
    </body></html>
    """
    docs = parse_fomc_index(html, "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm")
    assert len(docs) == 2
    assert docs[0].url.startswith("https://www.federalreserve.gov/")


def test_normalize_fomc_text_removes_extra_whitespace() -> None:
    assert normalize_fomc_text(" A\n\n  B\tC ") == "A B C"
