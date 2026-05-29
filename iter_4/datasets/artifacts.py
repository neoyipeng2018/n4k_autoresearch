from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class PublicDataArtifact:
    dataset: str
    source_url: str
    started_at: str
    finished_at: str
    artifact_path: str
    sha256: str
    row_count: int
    point_in_time_safe: bool


def write_artifact_manifest(artifacts: list[PublicDataArtifact], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([asdict(artifact) for artifact in artifacts]).to_csv(path, sep="	", index=False)
    return path
