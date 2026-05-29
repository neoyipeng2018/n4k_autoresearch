# macro-autoresearch iter_4

Autonomous retail macro quant strategy search for research artifacts. The objective is to maximize validation CAGR without ruin. Locked out-of-sample CAGR and DBMF excess return are final diagnostics used to audit generalization; they are not optimization targets.

## Objective

1. Validate every idea has a human-auditable rationale before running.
2. Reject any run that crashes or ruins capital.
3. Rank non-ruined candidates by validation CAGR only.
4. Report locked OOS CAGR, benchmark OOS CAGR, and excess OOS CAGR versus DBMF as diagnostics only.

## Files

- `prepare.py`: fixed data loader, backtester, validation-CAGR evaluator, locked OOS diagnostics, DBMF benchmark, and ruin detector.
- `datasets/`: public dataset registry, price ingestion, FOMC/Beige Book/FRED/SEC artifact writers, lagged text features, and data-quality checks.
- `research/`: robustness grids, walk-forward folds, trial artifacts, and anti-overfit reports.
- `ideas/schema.py`: rationale and unified TSV ledger schema.
- `train.py`: editable strategy file plus required `IDEA` rationale metadata.
- `program.md`: autonomous agent operating instructions.
- `scripts/ingest_public_macro.py`: optional Yahoo Finance data ingestion into `~/.cache/macroresearch/iter_4/`.
- `results.tsv`: local append-only experiment ledger with rationale and results in one row; ignored by git unless requested.

## Setup

```bash
uv sync
uv run scripts/ingest_public_macro.py
uv run train.py
```

`train.py` can fetch required Yahoo Finance data directly if the local cache is missing.

## Verification

```bash
uv run pytest -q
uv run mypy .
uv run ruff check .
uv run train.py > run.log 2>&1
```

## Output

A successful run prints matched-window diagnostics and split metrics:

```text
---
cagr:             0.123456
ruined:           false
ruin_threshold:   0.250000
dbmf_cagr:        0.075000
dbmf_ruined:      false
excess_cagr_vs_dbmf: 0.048456
end_multiple:     2.345678
start:            2019-05-08
end:              2026-05-28
observations:     1775
train_cagr:       0.100000
validation_cagr:  0.110000
oos_cagr:         0.120000
benchmark_oos_cagr: 0.090000
excess_oos_cagr_vs_dbmf: 0.030000
oos_passed:       true
```

`oos_passed` is retained for output compatibility but now means the validation gate passed: non-ruined, finite metrics, positive validation CAGR, and validation CAGR above the previous best. OOS and DBMF metrics do not affect keep/discard.

## Unified experiment ledger

`results.tsv` is append-only and spreadsheet-friendly. Each row includes the rationale fields and result fields:

```text
commit	timestamp_utc	idea_id	title	evidence_type	mechanism	expected_assets	feature_inputs	oos_hypothesis	falsification	references	human_notes	train_cagr	validation_cagr	oos_cagr	benchmark_oos_cagr	excess_oos_cagr_vs_dbmf	ruined	status	description
```

## Autonomous loop

1. Modify only `train.py` with one rationale-backed idea.
2. Run `uv run pytest -q`, `uv run mypy .`, and `uv run ruff check .` continuously.
3. Run `uv run train.py > run.log 2>&1`.
4. Keep a run only if it is non-ruined, validation CAGR is positive, finite metrics are produced, and validation CAGR improves on the previous best validation CAGR.
5. Do not use locked OOS CAGR or DBMF excess to choose candidates.
6. Do not optimize Sharpe, drawdown, Calmar, CVaR, volatility, turnover, complexity, or DBMF excess return directly.
