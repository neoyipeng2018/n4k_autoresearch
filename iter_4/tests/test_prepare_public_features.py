from __future__ import annotations

import pandas as pd
import pytest

from datasets.public_features import FeatureUsage, format_feature_usage
from prepare import add_public_features


def test_add_public_features_joins_numeric_public_frame(monkeypatch: pytest.MonkeyPatch) -> None:
    prices = pd.DataFrame({"SPY": [1.0, 1.1]}, index=pd.to_datetime(["2024-01-03", "2024-01-04"]))
    public = pd.DataFrame({"fomc_hawkish_minus_dovish": [0.1, 0.2]}, index=prices.index)

    def fake_loader(input_prices: pd.DataFrame) -> pd.DataFrame:
        assert input_prices.equals(prices)
        return public

    monkeypatch.setattr("prepare.load_public_feature_frame", fake_loader)

    joined = add_public_features(prices)

    assert list(joined.columns) == ["SPY", "fomc_hawkish_minus_dovish"]


def test_feature_usage_format_requires_real_non_price_columns() -> None:
    usage = FeatureUsage(
        claimed_inputs=("fomc_hawkish_minus_dovish",),
        actual_columns=("fomc_hawkish_minus_dovish",),
        source_artifacts=("fomc/fomc_events.tsv",),
    )

    assert "feature_usage_columns: fomc_hawkish_minus_dovish" in format_feature_usage(usage)
