from __future__ import annotations

import pandas as pd

from research.walk_forward import make_rolling_folds


def test_make_rolling_folds_embargoes_between_roles() -> None:
    folds = make_rolling_folds(2018, 2024, train_years=2, validation_years=1, oos_years=1, embargo_days=21)
    first = folds[0]
    assert first.train.end is not None
    assert first.validation.end is not None

    assert pd.Timestamp(first.validation.start) > pd.Timestamp(first.train.end) + pd.Timedelta(days=21)
    assert pd.Timestamp(first.oos.start) > pd.Timestamp(first.validation.end) + pd.Timedelta(days=21)


def test_make_rolling_folds_names_are_stable() -> None:
    folds = make_rolling_folds(2018, 2022, train_years=2, validation_years=1, oos_years=1, embargo_days=5)

    assert tuple(fold.name for fold in folds) == ("wf_2018_2021", "wf_2019_2022")
