from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from prepare import EvaluationSplit, OOSResult, WeightSelector, evaluate_oos


@dataclass(frozen=True)
class WalkForwardFold:
    name: str
    train: EvaluationSplit
    validation: EvaluationSplit
    oos: EvaluationSplit


def _date_after(year: int, month: int, day: int, embargo_days: int) -> str:
    return str((pd.Timestamp(year=year, month=month, day=day) + pd.Timedelta(days=embargo_days + 1)).date())


def make_rolling_folds(start_year: int, end_year: int, train_years: int, validation_years: int, oos_years: int, embargo_days: int = 0) -> tuple[WalkForwardFold, ...]:
    span = train_years + validation_years + oos_years
    folds: list[WalkForwardFold] = []
    for first_year in range(start_year, end_year - span + 2):
        train_end_year = first_year + train_years - 1
        validation_start_year = train_end_year + 1
        validation_end_year = validation_start_year + validation_years - 1
        oos_start_year = validation_end_year + 1
        oos_end_year = oos_start_year + oos_years - 1
        train = EvaluationSplit("train", f"{first_year}-01-01", f"{train_end_year}-12-31", "train")
        validation = EvaluationSplit("validation", _date_after(validation_start_year, 1, 1, embargo_days), f"{validation_end_year}-12-31", "validation")
        oos = EvaluationSplit("locked_oos", _date_after(oos_start_year, 1, 1, embargo_days), f"{oos_end_year}-12-31", "oos")
        folds.append(WalkForwardFold(f"wf_{first_year}_{oos_end_year}", train, validation, oos))
    return tuple(folds)


def evaluate_walk_forward(select_weights: WeightSelector, symbols: list[str], prices: pd.DataFrame, folds: tuple[WalkForwardFold, ...]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for fold in folds:
        result: OOSResult = evaluate_oos(select_weights, symbols=symbols, prices=prices, splits=(fold.train, fold.validation, fold.oos))
        rows.append({"fold": fold.name, "train_cagr": result.train_cagr, "validation_cagr": result.validation_cagr, "oos_cagr": result.oos_cagr, "benchmark_oos_cagr": result.benchmark_oos_cagr, "excess_oos_cagr_vs_dbmf": result.excess_oos_cagr_vs_dbmf, "ruined": result.ruined, "passed": result.passed})
    return pd.DataFrame(rows)


def write_walk_forward_tsv(frame: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, sep="	", index=False)
    return path
