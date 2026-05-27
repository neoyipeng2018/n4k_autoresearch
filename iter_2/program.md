# Maximum-CAGR-without-ruin macro autoresearch

This repo runs autonomous strategy experiments for retail macro quant trading. The objective is to maximize CAGR without ruin. Every run benchmarks against DBMF, the iMGP DBi Managed Futures Strategy ETF, over the same date window.

## Fixed files

Do not edit `prepare.py` during autonomous experiments. It owns data loading, backtesting, CAGR calculation, DBMF benchmarking, and ruin detection.

## Editable file

Edit only `train.py`. Change strategy logic, universe, parameters, ranking rules, rebalance behavior, allocation rules, and data filters to improve CAGR without ruin.

## Objective

The keep/discard decision is:

1. Reject the run if it crashes.
2. Reject the run if `ruined: true`.
3. Among non-ruined runs, keep only if `cagr` is higher than the previous best non-ruined `cagr`.

Do not rank strategies by Sharpe, volatility, drawdown, Calmar, CVaR, turnover, complexity, or excess return versus DBMF. Use diagnostics only to understand broken or ruined strategies.

DBMF is the required benchmark baseline and diagnostic comparison. It is not a second optimization metric unless the user explicitly changes the objective.

## Required output

Run:

```bash
uv run train.py > run.log 2>&1
```

The output must include these parseable lines:

```text
cagr:             <number>
ruined:           false
ruin_threshold:   <number>
dbmf_cagr:        <number>
dbmf_ruined:      false
excess_cagr_vs_dbmf: <number>
```

## results.tsv

Use tab-separated columns:

```text
commit	cagr	ruined	dbmf_cagr	dbmf_ruined	excess_cagr_vs_dbmf	status	description
```

Status is one of:

- `keep`: non-ruined run with CAGR above the previous best.
- `discard`: non-ruined run with CAGR not above the previous best, or a ruined run.
- `crash`: experiment failed to run.

## Loop

1. Check `git status --short`.
2. Modify `train.py` with one CAGR-oriented idea.
3. Run `uv run mypy prepare.py train.py scripts/ingest_public_macro.py`.
4. Run `uv run ruff check prepare.py train.py scripts/ingest_public_macro.py`.
5. Run `uv run train.py > run.log 2>&1`.
6. Extract `cagr`, `ruined`, `dbmf_cagr`, `dbmf_ruined`, and `excess_cagr_vs_dbmf`.
7. If `ruined` is `false` and CAGR improved, keep the commit.
8. If the run is ruined or CAGR did not improve, append a discard result and reset to the previous commit.
9. Continue.

## First experiment directions

Research and test ideas that could raise CAGR while avoiding account wipeout or near-wipeout:

- Momentum lookbacks: 3, 6, 9, and 12 months.
- Universe variants: sector ETFs, style ETFs, bond duration, gold, broad commodities, credit, and cash ballast.
- Selection variants: top-1, top-2, top-3, and score-weighted top-N.
- Risk filters used only as ruin guards: trend filters, crash filters, and cash fallback rules.
- Macro data filters: rates, inflation, dollar, commodities, and growth proxies from the local cache.

Every idea must state why it might improve CAGR without causing ruin and whether it beats or lags DBMF over the matched window.

Ask before adding leveraged/inverse ETPs, options, futures, or short-only rules.
