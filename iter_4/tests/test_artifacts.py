from __future__ import annotations

from pathlib import Path

from research.artifacts import write_trial_artifact


def test_write_trial_artifact_creates_reproducibility_files(tmp_path: Path) -> None:
    run_log = tmp_path / "run.log"
    run_log.write_text("ok\n")

    trial_dir = write_trial_artifact(
        root=tmp_path,
        idea_id="idea_001",
        timestamp_utc="2026-01-01T00:00:00Z",
        params={"lookback": 21},
        result_row={"idea_id": "idea_001", "validation_cagr": "0.1"},
        data_manifest={"price_files": []},
        run_log_path=run_log,
        commit="abc123",
    )

    assert (trial_dir / "params.json").exists()
    assert (trial_dir / "result_row.json").exists()
    assert (trial_dir / "data_manifest.json").exists()
    assert (trial_dir / "run.log").read_text() == "ok\n"
    assert (trial_dir / "commit.txt").read_text() == "abc123\n"
