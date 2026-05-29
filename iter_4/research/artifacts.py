from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Mapping


def _safe_component(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")
    return safe or "artifact"


def write_json(path: Path, payload: Mapping[str, object]) -> Path:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return path


def write_trial_artifact(
    root: Path,
    idea_id: str,
    timestamp_utc: str,
    params: Mapping[str, object],
    result_row: Mapping[str, object],
    data_manifest: Mapping[str, object],
    run_log_path: Path,
    commit: str,
) -> Path:
    artifact_name = f"{_safe_component(timestamp_utc)}_{_safe_component(idea_id)}"
    trial_dir = root / "artifacts" / "trials" / artifact_name
    trial_dir.mkdir(parents=True, exist_ok=True)
    write_json(trial_dir / "params.json", params)
    write_json(trial_dir / "result_row.json", result_row)
    write_json(trial_dir / "data_manifest.json", data_manifest)
    shutil.copyfile(run_log_path, trial_dir / "run.log")
    (trial_dir / "commit.txt").write_text(commit + "\n")
    return trial_dir
