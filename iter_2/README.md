# macro-autoresearch

Autonomous retail macro quant strategy search for maximum CAGR without ruin.

## Objective

Maximize CAGR without ruin. Ruin is a hard disqualifier. Among non-ruined strategies, rank by CAGR only.

DBMF, the iMGP DBi Managed Futures Strategy ETF, is the required matched-window benchmark baseline. Each run reports the strategy CAGR, DBMF CAGR, and excess CAGR versus DBMF. DBMF is a benchmark and diagnostic comparison, not a replacement ranking metric.

## Files

- `prepare.py`: fixed data loader, backtester, CAGR evaluator, DBMF benchmark, and ruin detector.
- `train.py`: editable strategy file.
- `program.md`: autonomous agent operating instructions.
- `scripts/ingest_public_macro.py`: optional Yahoo Finance data ingestion into `~/.cache/macroresearch/`.
- `results.tsv`: local experiment ledger, ignored by git unless the user asks to commit it.

## Setup

```bash
uv sync
uv run scripts/ingest_public_macro.py
uv run train.py
```

`train.py` can also fetch required Yahoo Finance data directly if the local cache is missing.

## Output

A successful run prints parseable lines:

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
```

## Experiment ledger

Use tab-separated columns:

```text
commit	cagr	ruined	dbmf_cagr	dbmf_ruined	excess_cagr_vs_dbmf	status	description
```

`results.tsv` is local by default.

## Autonomous loop

1. Modify only `train.py` with one idea.
2. Run typecheck and lint:

```bash
uv run mypy prepare.py train.py scripts/ingest_public_macro.py
uv run ruff check prepare.py train.py scripts/ingest_public_macro.py
```

3. Run the strategy:

```bash
uv run train.py > run.log 2>&1
```

4. Keep a run only if `ruined` is `false` and CAGR improves over the previous best.
5. Compare every run to DBMF over the same date window.
6. Do not optimize Sharpe, drawdown, Calmar, CVaR, volatility, turnover, complexity, or excess return versus DBMF directly.
