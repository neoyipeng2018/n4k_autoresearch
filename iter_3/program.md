# Maximum-OOS-CAGR-without-ruin macro autoresearch

This repo runs autonomous strategy experiments for retail macro quant trading and financial-advice research artifacts. The objective is to maximize locked out-of-sample CAGR without ruin. Every run benchmarks against DBMF over the same OOS date window as a required diagnostic, not as the primary objective.

## Fixed files

Do not edit `prepare.py`, `datasets/*`, or `ideas/schema.py` during autonomous strategy experiments. They own data loading, point-in-time public dataset rules, backtesting, OOS evaluation, DBMF benchmarking, rationale validation, and the unified results ledger.

## Editable file

Edit only `train.py`. Change one strategy idea at a time, including its `IDEA` rationale metadata.

## Rationale gate

Every idea must validate before execution and include:

- `idea_id`
- title
- evidence type
- economic, academic, behavioral, microstructure, policy, or known-anomaly mechanism
- expected affected assets
- feature inputs
- OOS hypothesis
- falsification criteria
- references or source notes

A run without a complete rationale is invalid.

## Objective

The keep/discard decision is:

1. Reject the run if it crashes.
2. Reject the run if `ruined: true`.
3. Reject the run if validation CAGR is non-positive.
4. Reject the run if OOS CAGR does not beat the previous best non-ruined OOS CAGR.
5. Reject the run if excess OOS CAGR versus DBMF is non-positive.
6. Among remaining runs, keep the highest OOS CAGR.

Do not rank strategies by Sharpe, volatility, drawdown, Calmar, CVaR, turnover, complexity, or excess return versus DBMF. Use diagnostics only to understand broken or ruined strategies.

## Required verification

Run continuously while editing:

```bash
uv run pytest -q
uv run mypy .
uv run ruff check .
```

Run the strategy:

```bash
uv run train.py > run.log 2>&1
```

The output must include parseable matched-window and OOS lines:

```text
cagr:             <number>
ruined:           false
ruin_threshold:   <number>
dbmf_cagr:        <number>
dbmf_ruined:      false
excess_cagr_vs_dbmf: <number>
train_cagr:       <number>
validation_cagr:  <number>
oos_cagr:         <number>
benchmark_oos_cagr: <number>
excess_oos_cagr_vs_dbmf: <number>
oos_passed:       <true|false>
```

## results.tsv

Use one unified tab-separated append-only ledger. Each row stores both the rationale and performance results:

```text
commit	timestamp_utc	idea_id	title	evidence_type	mechanism	expected_assets	feature_inputs	oos_hypothesis	falsification	references	human_notes	train_cagr	validation_cagr	oos_cagr	benchmark_oos_cagr	excess_oos_cagr_vs_dbmf	ruined	status	description
```

Status is one of:

- `keep`: OOS gate passed.
- `discard`: non-ruined run that failed the OOS gate.
- `ruined`: run breached ruin criteria.
- `invalid_rationale`: rationale validation failed.

## Public dataset policy

Prioritize public datasets with clear publication timestamps and auditable source URLs. Text features must be lagged so the strategy never sees text before publication. FOMC minutes are aligned to minutes publication date, not meeting date.

## Loop

1. Check `git status --short`.
2. Modify `train.py` with one rationale-backed OOS-CAGR idea.
3. Run typecheck, lint, and tests.
4. Run `uv run train.py > run.log 2>&1`.
5. Inspect OOS CAGR, ruin status, validation CAGR, and DBMF diagnostic excess.
6. Append one unified `results.tsv` row.
7. Keep only OOS-gate-passing improvements.
8. Continue.

Ask before adding leveraged/inverse ETPs, options, futures, or short-only rules.
