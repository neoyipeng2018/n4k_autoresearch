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
    daily = events.set_index("effective_date")[feature_columns].groupby(level=0).last()
    aligned = daily.reindex(prices.index.union(daily.index)).ffill().reindex(prices.index)
    return aligned


def build_beige_book_features(events: pd.DataFrame) -> pd.DataFrame:
    required = {"published_at", "text"}
    missing = required.difference(events.columns)
    if missing:
        raise ValueError(f"Beige Book events missing required columns: {', '.join(sorted(missing))}")
    rows: list[dict[str, object]] = []
    expansion_terms = frozenset({"expanded", "growth", "grew", "strong", "improved", "increase", "increased"})
    contraction_terms = frozenset({"declined", "weak", "slowed", "contracted", "decrease", "decreased"})
    price_terms = frozenset({"price", "prices", "inflation", "cost", "costs", "wage", "wages"})
    labor_terms = frozenset({"employment", "jobs", "hiring", "labor", "unemployment"})
    for row in events.sort_values("published_at").itertuples(index=False):
        published_at = pd.Timestamp(getattr(row, "published_at"))
        text = str(getattr(row, "text"))
        tokens = tokenize(text)
        rows.append(
            {
                "published_at": published_at,
                "beige_token_count": len(tokens),
                "beige_activity_score": lexicon_score(text, expansion_terms, contraction_terms),
                "beige_price_pressure_score": lexicon_score(text, price_terms, frozenset[str]()),
                "beige_labor_score": lexicon_score(text, labor_terms, frozenset[str]()),
                "source_dataset": "beige_book_text",
                "feature_version": "beige_book_lexicon_v1",
                "lexicon_version": LEXICON_VERSION,
            }
        )
    return pd.DataFrame(rows)


def build_sec_features(filings: pd.DataFrame) -> pd.DataFrame:
    required = {"accepted_at", "form_type"}
    missing = required.difference(filings.columns)
    if missing:
        raise ValueError(f"SEC filings missing required columns: {', '.join(sorted(missing))}")
    frame = filings.copy()
    frame["published_at"] = pd.to_datetime(frame["accepted_at"], utc=True)
    frame["form_type"] = frame["form_type"].astype(str)
    rows: list[dict[str, object]] = []
    for day, group in frame.groupby(frame["published_at"].dt.normalize()):
        form_counts = group["form_type"].value_counts()
        rows.append(
            {
                "published_at": pd.Timestamp(day),
                "sec_filing_count": float(len(group.index)),
                "sec_10k_count": float(form_counts.get("10-K", 0)),
                "sec_10q_count": float(form_counts.get("10-Q", 0)),
                "sec_8k_count": float(form_counts.get("8-K", 0)),
            }
        )
    return pd.DataFrame(rows).sort_values("published_at").reset_index(drop=True)


def build_fred_features(observations: pd.DataFrame) -> pd.DataFrame:
    required = {"series_id", "date", "realtime_start", "value"}
    missing = required.difference(observations.columns)
    if missing:
        raise ValueError(f"FRED observations missing required columns: {', '.join(sorted(missing))}")
    frame = observations.copy()
    frame["published_at"] = pd.to_datetime(frame["realtime_start"], utc=True)
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame = frame.dropna(subset=["value"])
    pivot = frame.pivot_table(index="published_at", columns="series_id", values="value", aggfunc="last")
    pivot = pivot.sort_index()
    pivot.columns = [f"fred_{column}" for column in pivot.columns]
    pivot = pivot.reset_index()
    if {"fred_DGS10", "fred_DGS2"}.issubset(pivot.columns):
        pivot["fred_DGS10_minus_DGS2"] = pivot["fred_DGS10"] - pivot["fred_DGS2"]
    return pivot
