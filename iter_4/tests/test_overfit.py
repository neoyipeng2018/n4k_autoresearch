from __future__ import annotations

import pandas as pd

from research.overfit import infer_family, selection_bias_summary


def test_infer_family_uses_stable_prefix() -> None:
    assert infer_family("sector_top2_1m_scoreweight_024") == "sector_top2"


def test_selection_bias_summary_reports_best_vs_median() -> None:
    results = pd.DataFrame(
        {
            "idea_id": ["a_one", "b_two", "b_three"],
            "validation_cagr": [0.10, 0.20, 0.30],
            "oos_cagr": [0.11, 0.19, 0.01],
            "ruined": ["false", "false", "false"],
        }
    )

    summary = selection_bias_summary(results)

    assert summary["trial_count"] == 3
    assert summary["family_count"] == 3
    assert summary["best_idea_id"] == "b_three"
    assert summary["best_minus_median_validation_cagr"] == 0.09999999999999998
