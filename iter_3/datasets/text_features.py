from __future__ import annotations

import re
from collections.abc import Iterable

import pandas as pd

HAWKISH_TERMS: frozenset[str] = frozenset(
    {
        "inflation",
        "restrictive",
        "tightening",
        "elevated",
        "overheating",
        "hike",
        "hikes",
        "firming",
    }
)
DOVISH_TERMS: frozenset[str] = frozenset(
    {
        "cut",
        "cuts",
        "weakness",
        "unemployment",
        "accommodative",
        "easing",
        "slack",
        "slowdown",
    }
)
UNCERTAINTY_TERMS: frozenset[str] = frozenset({"uncertain", "uncertainty", "risk", "risks", "volatile"})
FEATURE_VERSION = "fomc_lexicon_v1"
LEXICON_VERSION = "policy_terms_v1"
FEATURE_METADATA_COLUMNS: tuple[str, ...] = ("source_dataset", "feature_version", "lexicon_version")
TOKEN_PATTERN = re.compile(r"[a-z]+(?:-[a-z]+)?")


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def lexicon_score(text: str, positive_terms: Iterable[str], negative_terms: Iterable[str]) -> float:
    tokens = tokenize(text)
    if not tokens:
        return 0.0
    positive = set(positive_terms)
    negative = set(negative_terms)
    positive_count = sum(1 for token in tokens if token in positive)
    negative_count = sum(1 for token in tokens if token in negative)
    return (positive_count - negative_count) / len(tokens)


def build_fomc_features(events: pd.DataFrame) -> pd.DataFrame:
    required = {"published_at", "text"}
    missing = required.difference(events.columns)
    if missing:
        missing_columns = ", ".join(sorted(missing))
        raise ValueError(f"FOMC events missing required columns: {missing_columns}")
    rows: list[dict[str, object]] = []
    for row in events.sort_values("published_at").itertuples(index=False):
        published_at = pd.Timestamp(getattr(row, "published_at"))
        text = str(getattr(row, "text"))
        tokens = tokenize(text)
        hawkish_minus_dovish = lexicon_score(text, HAWKISH_TERMS, DOVISH_TERMS)
        uncertainty = lexicon_score(text, UNCERTAINTY_TERMS, frozenset[str]())
        rows.append(
            {
                "published_at": published_at,
                "token_count": len(tokens),
                "hawkish_minus_dovish": hawkish_minus_dovish,
                "uncertainty_score": uncertainty,
                "source_dataset": "fomc_text",
                "feature_version": FEATURE_VERSION,
                "lexicon_version": LEXICON_VERSION,
            }
        )
    return pd.DataFrame(rows)


def align_event_features_to_prices(prices: pd.DataFrame, event_features: pd.DataFrame) -> pd.DataFrame:
    if len(prices.index) == 0:
        return pd.DataFrame(index=prices.index)
    if len(event_features.index) == 0:
        feature_columns = [column for column in event_features.columns if column != "published_at"]
        return pd.DataFrame(index=prices.index, columns=feature_columns, dtype="float64")
    if "published_at" not in event_features.columns:
        raise ValueError("event_features must include published_at")
    feature_columns = [column for column in event_features.columns if column != "published_at"]
    events = event_features.copy()
    published = pd.to_datetime(events["published_at"], utc=True)
    events = events.assign(effective_date=published.dt.tz_convert(None).dt.normalize() + pd.Timedelta(days=1))
    events = events.sort_values("effective_date")
    daily = events.set_index("effective_date")[feature_columns]
    aligned = daily.reindex(prices.index.union(daily.index)).ffill().reindex(prices.index)
    return aligned
