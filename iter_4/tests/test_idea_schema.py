from __future__ import annotations

from pathlib import Path
from typing import get_args

import pytest

from ideas.schema import EvidenceType, IdeaRationale, ResultStatus, append_result_row, result_fieldnames


def make_idea() -> IdeaRationale:
    return IdeaRationale(
        idea_id="fomc_hawkish_gold_rates_001",
        title="Fed tone and duration risk",
        evidence_type="policy_transmission",
        mechanism="Hawkish monetary policy language raises expected real rates and can hurt duration assets.",
        expected_assets=("TLT", "QQQ", "GLD", "SGOV"),
        feature_inputs=("fomc_text", "price_momentum_21d"),
        oos_hypothesis="Lagged Fed tone improves OOS CAGR versus the price-only baseline.",
        falsification="Reject if OOS CAGR does not improve or excess CAGR versus DBMF is negative.",
        references=("Bernanke and Kuttner 2005",),
        human_notes="Initial transparent text feature.",
    )


def test_valid_idea_exports_results_fields() -> None:
    idea = make_idea()
    idea.validate()
    fields = idea.to_results_fields()
    assert fields["idea_id"] == "fomc_hawkish_gold_rates_001"
    assert fields["evidence_type"] == "policy_transmission"
    assert fields["expected_assets"] == "TLT;QQQ;GLD;SGOV"
    assert fields["feature_inputs"] == "fomc_text;price_momentum_21d"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("mechanism", ""),
        ("oos_hypothesis", ""),
        ("falsification", ""),
        ("references", ()),
        ("expected_assets", ()),
        ("feature_inputs", ()),
    ],
)
def test_idea_rejects_missing_required_fields(field: str, value: object) -> None:
    data = make_idea().__dict__ | {field: value}
    idea = IdeaRationale(**data)
    with pytest.raises(ValueError):
        idea.validate()


def test_evidence_and_status_literals_are_enumerated() -> None:
    assert "policy_transmission" in get_args(EvidenceType)
    assert "invalid_rationale" in get_args(ResultStatus)


def test_append_result_row_round_trips_tsv(tmp_path: Path) -> None:
    path = tmp_path / "results.tsv"
    row = make_idea().to_results_fields() | {
        "commit": "abc1234",
        "timestamp_utc": "2026-05-28T00:00:00Z",
        "train_cagr": "0.100000",
        "validation_cagr": "0.110000",
        "oos_cagr": "0.120000",
        "benchmark_oos_cagr": "0.090000",
        "excess_oos_cagr_vs_dbmf": "0.030000",
        "ruined": "false",
        "status": "keep",
        "description": "test row",
    }
    append_result_row(path, row)
    lines = path.read_text().splitlines()
    assert lines[0].split("\t") == result_fieldnames()
    assert len(lines) == 2
    assert "fomc_hawkish_gold_rates_001" in lines[1]


def test_append_result_row_rejects_missing_field(tmp_path: Path) -> None:
    row = {name: "x" for name in result_fieldnames()}
    del row["mechanism"]
    with pytest.raises(ValueError):
        append_result_row(tmp_path / "results.tsv", row)


def test_append_result_row_rejects_unknown_status(tmp_path: Path) -> None:
    row = {name: "x" for name in result_fieldnames()}
    row["status"] = "unknown_status"
    with pytest.raises(ValueError):
        append_result_row(tmp_path / "results.tsv", row)
