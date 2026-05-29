# Maximum-validation-CAGR-without-ruin macro autoresearch

This repo runs autonomous strategy experiments for retail macro quant trading and financial-advice research artifacts. The objective is to maximize validation CAGR without ruin. Locked out-of-sample CAGR is a final test metric used to audit whether validation-selected ideas generalize; it is not the optimization target. Every run benchmarks against DBMF over the same OOS date window as a required diagnostic, not as the primary objective.

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
4. Reject the run if validation CAGR does not beat the previous best non-ruined validation CAGR.
5. Keep the highest validation CAGR among remaining runs.
6. Report OOS CAGR, benchmark OOS CAGR, and excess OOS CAGR versus DBMF as locked test diagnostics only. Do not use them to choose among candidates during the loop.

Do not rank strategies by OOS CAGR, Sharpe, volatility, drawdown, Calmar, CVaR, turnover, complexity, or excess return versus DBMF. Use diagnostics only to understand broken, ruined, or non-generalizing strategies after the validation-selected choice is made.

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
feature_usage_columns: <comma-separated actual public feature columns or none>
feature_source_artifacts: <comma-separated artifact paths or none>
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

- `keep`: validation gate passed and validation CAGR improved on the previous best.
- `discard`: non-ruined run that failed the validation gate or did not improve validation CAGR.
- `ruined`: run breached ruin criteria.
- `invalid_rationale`: rationale validation failed.

## Public dataset policy

Prioritize public datasets with clear publication timestamps and auditable source URLs. Text features must be lagged so the strategy never sees text before publication. FOMC minutes are aligned to minutes publication date, not meeting date.

## Available public datasets

Agents may inspect but must not edit `datasets/*`. Available datasets are registered in `datasets/registry.py` and include:

- daily ETF prices via `prices_yahoo`
- FOMC statements and minutes text via `fomc_text`
- Federal Reserve Beige Book text via `beige_book_text`
- SEC EDGAR filing text and metadata via `sec_edgar`
- FRED numeric macro series via `fred_numeric`

Text feature helpers live in `datasets/text_features.py`, including FOMC lexicon features such as `hawkish_minus_dovish` and `uncertainty_score`, Beige Book activity/price/labor lexicon features, SEC filing-count features, FRED spread features, plus `align_event_features_to_prices` for publication-lagged alignment. The train-safe API is `datasets.public_features.load_public_feature_frame(prices)`, and `prepare.py` joins available public features into the price frame automatically after benchmark alignment.

If an idea claims any non-price public dataset in `IDEA.feature_inputs`, the run is invalid unless `train.py` prints parseable `feature_usage_columns:` and `feature_source_artifacts:` lines showing that the claimed non-price feature columns were actually present and sourced from artifacts. Do not merely mention FOMC, Beige Book, SEC, or FRED in the rationale; the selected strategy must read and use the aligned columns.

When public artifacts exist, every five strategy attempts must include at least one rationale-backed non-price public-data variant unless the immediately preceding non-price attempt crashed or was ruined. Agents should preserve point-in-time alignment and keep `prepare.py`, `datasets/*`, and `ideas/schema.py` fixed during autonomous strategy experiments.

## Loop

1. Check `git status --short`.
2. Modify `train.py` with one rationale-backed validation-CAGR idea.
3. Run typecheck, lint, and tests.
4. Run `uv run train.py > run.log 2>&1`.
5. Verify that every non-price claim in `feature_inputs` appears in `feature_usage_columns` and has a corresponding source artifact line.
6. Inspect validation CAGR and ruin status for keep/discard; inspect OOS CAGR and DBMF diagnostic excess only as locked test diagnostics.
7. Append one unified `results.tsv` row.
8. Keep only validation-CAGR improvements that do not ruin.
9. Continue.

Ask before adding leveraged/inverse ETPs, options, futures, or short-only rules.
