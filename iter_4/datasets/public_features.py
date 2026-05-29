from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from datasets.cache import CACHE_ROOT
from datasets.loaders import (
    MissingPublicDataError,
    load_beige_book_events,
    load_fomc_events,
    load_fred_observations,
    load_sec_filings,
)
from datasets.text_features import (
    align_event_features_to_prices,
    build_beige_book_features,
    build_fomc_features,
    build_fred_features,
    build_sec_features,
)

PRICE_FEATURE_PREFIXES = ("price_", "score_", "equity_", "momentum_", "vol_", "trend_")


@dataclass(frozen=True)
class FeatureUsage:
    claimed_inputs: tuple[str, ...]
    actual_columns: tuple[str, ...]
    source_artifacts: tuple[str, ...]


def numeric_feature_columns(frame: pd.DataFrame) -> list[str]:
    return [column for column in frame.columns if column != "published_at" and pd.api.types.is_numeric_dtype(frame[column])]


def prefixed_numeric_events(prefix: str, events: pd.DataFrame) -> pd.DataFrame:
    numeric_columns = numeric_feature_columns(events)
    result = events[["published_at", *numeric_columns]].copy()
    rename = {column: f"{prefix}_{column}" for column in numeric_columns}
    return result.rename(columns=rename)


def align_numeric_events(prices: pd.DataFrame, events: pd.DataFrame, prefix: str) -> pd.DataFrame:
    return align_event_features_to_prices(prices, prefixed_numeric_events(prefix, events))


def combine_feature_frames(frames: Iterable[pd.DataFrame], index: pd.Index) -> pd.DataFrame:
    combined = pd.DataFrame(index=index)
    for frame in frames:
        if frame.empty:
            continue
        combined = combined.join(frame, how="left")
    return combined.sort_index(axis=1)


def load_fomc_feature_frame(prices: pd.DataFrame, cache_root: Path = CACHE_ROOT) -> pd.DataFrame:
    return align_numeric_events(prices, build_fomc_features(load_fomc_events(cache_root)), "fomc")


def load_beige_feature_frame(prices: pd.DataFrame, cache_root: Path = CACHE_ROOT) -> pd.DataFrame:
    return align_numeric_events(prices, build_beige_book_features(load_beige_book_events(cache_root)), "beige")


def load_sec_feature_frame(prices: pd.DataFrame, cache_root: Path = CACHE_ROOT) -> pd.DataFrame:
    return align_numeric_events(prices, build_sec_features(load_sec_filings(cache_root)), "sec")


def load_fred_feature_frame(prices: pd.DataFrame, cache_root: Path = CACHE_ROOT) -> pd.DataFrame:
    return align_numeric_events(prices, build_fred_features(load_fred_observations(cache_root)), "fred")


def load_public_feature_frame(prices: pd.DataFrame, cache_root: Path = CACHE_ROOT, require_all: bool = False) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    missing: list[str] = []
    loaders = (
        ("fomc", load_fomc_feature_frame),
        ("beige", load_beige_feature_frame),
        ("sec", load_sec_feature_frame),
        ("fred", load_fred_feature_frame),
    )
    for name, loader in loaders:
        try:
            frames.append(loader(prices, cache_root))
        except MissingPublicDataError as exc:
            missing.append(f"{name}: {exc}")
    if require_all and missing:
        raise MissingPublicDataError("; ".join(missing))
    return combine_feature_frames(frames, prices.index)


def is_non_price_feature(feature: str) -> bool:
    return not feature.startswith(PRICE_FEATURE_PREFIXES)


def validate_claimed_feature_usage(usage: FeatureUsage) -> None:
    claimed_non_price = {feature for feature in usage.claimed_inputs if is_non_price_feature(feature)}
    actual = set(usage.actual_columns)
    missing = claimed_non_price.difference(actual)
    if missing:
        raise ValueError(f"claimed non-price features were not used: {', '.join(sorted(missing))}")
    if claimed_non_price and not usage.source_artifacts:
        raise ValueError("claimed non-price features require source artifact reporting")


def format_feature_usage(usage: FeatureUsage) -> str:
    validate_claimed_feature_usage(usage)
    columns = ",".join(usage.actual_columns) if usage.actual_columns else "none"
    artifacts = ",".join(usage.source_artifacts) if usage.source_artifacts else "none"
    return f"feature_usage_columns: {columns}\nfeature_source_artifacts: {artifacts}"
