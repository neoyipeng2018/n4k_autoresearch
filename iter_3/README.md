# macro-autoresearch iter_3

Autonomous retail macro quant strategy search that dispenses financial advice research artifacts. The objective is to maximize out-of-sample CAGR without ruin. DBMF is a required diagnostic benchmark, not the primary objective.

## Objective

1. Validate every idea has a human-auditable rationale before running.
2. Reject any run that crashes or ruins capital.
3. Rank non-ruined candidates by locked out-of-sample CAGR.
4. Use excess OOS CAGR versus DBMF as a diagnostic guardrail.

## Files

- `prepare.py`: fixed data loader, backtester, CAGR evaluator, OOS split evaluator, DBMF benchmark, and ruin detector.
- `datasets/`: public dataset registry, price ingestion, FOMC parsing, and lagged text features.
- `ideas/schema.py`: rationale and unified TSV ledger schema.
- `train.py`: editable strategy file plus required `IDEA` rationale metadata.
- `program.md`: autonomous agent operating instructions.
- `scripts/ingest_public_macro.py`: optional Yahoo Finance data ingestion into `~/.cache/macroresearch/iter_3/`.
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

A successful run prints matched-window diagnostics and OOS metrics:

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

## Unified experiment ledger

`results.tsv` is append-only and spreadsheet-friendly. Each row includes the rationale fields and result fields:

```text
commit	timestamp_utc	idea_id	title	evidence_type	mechanism	expected_assets	feature_inputs	oos_hypothesis	falsification	references	human_notes	train_cagr	validation_cagr	oos_cagr	benchmark_oos_cagr	excess_oos_cagr_vs_dbmf	ruined	status	description
```

## Autonomous loop

1. Modify only `train.py` with one rationale-backed idea.
2. Run `uv run pytest -q`, `uv run mypy .`, and `uv run ruff check .` continuously.
3. Run `uv run train.py > run.log 2>&1`.
4. Keep a run only if the OOS gate passes: no ruin, OOS CAGR improves, validation CAGR is positive, and excess OOS CAGR versus DBMF is positive.
5. Do not optimize Sharpe, drawdown, Calmar, CVaR, volatility, turnover, complexity, or DBMF excess return directly.
