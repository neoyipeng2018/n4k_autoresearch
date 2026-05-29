from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

EvidenceType = Literal[
    "economic_intuition",
    "academic_literature",
    "behavioral_finance",
    "market_microstructure",
    "policy_transmission",
    "replication_of_known_anomaly",
]
ResultStatus = Literal["proposed", "keep", "discard", "ruined", "invalid_rationale"]

RESULT_FIELDS: tuple[str, ...] = (
    "commit",
    "timestamp_utc",
    "idea_id",
    "title",
    "evidence_type",
    "mechanism",
    "expected_assets",
    "feature_inputs",
    "oos_hypothesis",
    "falsification",
    "references",
    "human_notes",
    "train_cagr",
    "validation_cagr",
    "oos_cagr",
    "benchmark_oos_cagr",
    "excess_oos_cagr_vs_dbmf",
    "ruined",
    "status",
    "description",
)


@dataclass(frozen=True)
class IdeaRationale:
    idea_id: str
    title: str
    evidence_type: EvidenceType
    mechanism: str
    expected_assets: tuple[str, ...]
    feature_inputs: tuple[str, ...]
    oos_hypothesis: str
    falsification: str
    references: tuple[str, ...]
    human_notes: str = ""

    def validate(self) -> None:
        required = (
            self.idea_id,
            self.title,
            self.evidence_type,
            self.mechanism,
            self.oos_hypothesis,
            self.falsification,
        )
        if any(not value.strip() for value in required):
            raise ValueError("IdeaRationale is incomplete")
        if not self.expected_assets:
            raise ValueError("At least one expected asset is required")
        if not self.feature_inputs:
            raise ValueError("At least one feature input is required")
        if not self.references:
            raise ValueError("At least one reference or source note is required")
        if any(not value.strip() for value in self.expected_assets):
            raise ValueError("Expected assets cannot contain blank values")
        if any(not value.strip() for value in self.feature_inputs):
            raise ValueError("Feature inputs cannot contain blank values")
        if any(not value.strip() for value in self.references):
            raise ValueError("References cannot contain blank values")

    def to_results_fields(self) -> dict[str, str]:
        self.validate()
        return {
            "idea_id": self.idea_id,
            "title": self.title,
            "evidence_type": self.evidence_type,
            "mechanism": self.mechanism,
            "expected_assets": ";".join(self.expected_assets),
            "feature_inputs": ";".join(self.feature_inputs),
            "oos_hypothesis": self.oos_hypothesis,
            "falsification": self.falsification,
            "references": ";".join(self.references),
            "human_notes": self.human_notes,
        }


def result_fieldnames() -> list[str]:
    return list(RESULT_FIELDS)


def append_result_row(path: Path, row: dict[str, str]) -> None:
    missing = [field for field in RESULT_FIELDS if field not in row]
    extra = [field for field in row if field not in RESULT_FIELDS]
    if missing:
        raise ValueError(f"Result row missing fields: {', '.join(missing)}")
    if extra:
        raise ValueError(f"Result row has unknown fields: {', '.join(extra)}")
    status = row["status"]
    valid_statuses = {"proposed", "keep", "discard", "ruined", "invalid_rationale"}
    if status not in valid_statuses:
        raise ValueError(f"Result row has unknown status: {status}")
    path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=result_fieldnames(), delimiter="\t", lineterminator="\n")
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
