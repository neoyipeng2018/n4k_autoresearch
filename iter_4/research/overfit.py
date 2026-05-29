from __future__ import annotations

import math
from pathlib import Path

import pandas as pd


def infer_family(idea_id: str) -> str:
    parts = idea_id.split("_")
    if len(parts) >= 2:
        return "_".join(parts[:2])
    return idea_id


def _as_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin(["true", "1", "yes"])


def selection_bias_summary(results: pd.DataFrame) -> dict[str, object]:
    clean = results.loc[~_as_bool(results["ruined"])].copy()
    clean["family"] = clean["idea_id"].astype(str).map(infer_family)
    best_index = clean["validation_cagr"].astype(float).idxmax()
    best = clean.loc[best_index]
    median_validation = float(clean["validation_cagr"].astype(float).median())
    return {
        "trial_count": int(len(clean)),
        "family_count": int(clean["family"].nunique()),
        "best_idea_id": str(best["idea_id"]),
        "best_validation_cagr": float(best["validation_cagr"]),
        "median_validation_cagr": median_validation,
        "best_minus_median_validation_cagr": float(best["validation_cagr"]) - median_validation,
        "median_oos_cagr": float(clean["oos_cagr"].astype(float).median()) if "oos_cagr" in clean else math.nan,
        "selection_bias_warning": "High trial counts inflate the best validation result; inspect family medians and locked OOS only after selection.",
    }


def write_overfit_report(results: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([selection_bias_summary(results)]).to_csv(path, sep="	", index=False)
    return path
