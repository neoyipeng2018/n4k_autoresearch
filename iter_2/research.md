# Research Notes: Adapting `autoresearch` to Retail Macro Quant Trading

## What the original codebase is

`autoresearch` is a tiny autonomous research harness for LLM pretraining experiments. Its core idea is not the model itself, but the workflow: give an agent a fixed evaluation environment, let it edit one target file, run a bounded experiment, score the result, keep improvements, discard failures, and log every attempt.

In `iter_2`, the original repo has been copied from `original/` as a baseline. The important files are:

- `README.md`: explains the autonomous experiment philosophy.
- `program.md`: the agent operating manual.
- `prepare.py`: fixed data prep, tokenizer, dataloader, and evaluation utilities.
- `train.py`: the editable experiment file containing model, optimizer, and training loop.
- `analysis.ipynb`: notebook for analyzing `results.tsv` experiment logs.
- `pyproject.toml`: Python/uv dependencies.

## How it works

### 1. `program.md` is the real control layer

The repo treats the agent instructions as the main “program.” The human edits `program.md`; the agent then follows it. The default instructions enforce:

1. create a fresh experiment branch,
2. read the in-scope files,
3. verify data exists,
4. initialize a results ledger,
5. run a baseline,
6. repeatedly edit `train.py`, run experiments, and keep only improvements.

For macro quant adaptation, this file should become the research charter: what data to use, what instruments are allowed, how to score strategies, what risks disqualify a result, and how to log accepted/rejected ideas.

### 2. `prepare.py` is the fixed environment

`prepare.py` is intentionally not edited during experiments. It defines the shared benchmark:

- cache root: `~/.cache/autoresearch/`
- data source: Karpathy `climbmix-400b-shuffle` parquet shards
- pinned validation shard: `shard_06542.parquet`
- tokenizer: custom 8192-token BPE via `rustbpe` + `tiktoken`
- context length: `MAX_SEQ_LEN = 2048`
- training time budget: `TIME_BUDGET = 300`
- evaluation metric: validation bits per byte, `val_bpb`

Its runtime utilities are:

- `Tokenizer`: wrapper around saved tiktoken encoding.
- `make_dataloader`: BOS-aligned packed document batches with no padding.
- `evaluate_bpb`: fixed validation metric using token-byte lengths.

For macro quant adaptation, `prepare.py` should become the stable data/evaluation layer: ingest macro/market data, clean it, define train/test splits, expose feature loaders, and compute fixed metrics such as CAGR, Sharpe, max drawdown, Calmar, CVaR, turnover, and cost-adjusted returns.

### 3. `train.py` is the editable experiment target

`train.py` is currently a single-GPU GPT pretraining script. It contains:

- GPT model definition.
- Flash Attention 3 kernel selection.
- RMSNorm, rotary embeddings, sliding-window attention, value embeddings.
- ReLU-squared MLP.
- Muon + AdamW optimizer.
- hardcoded hyperparameters.
- fixed 5-minute training loop.
- final evaluation and printed summary.

Important defaults:

- `DEPTH = 8`
- `ASPECT_RATIO = 64`
- `HEAD_DIM = 128`
- `WINDOW_PATTERN = "SSSL"`
- `TOTAL_BATCH_SIZE = 2**19`
- `DEVICE_BATCH_SIZE = 128`
- `EMBEDDING_LR = 0.6`
- `MATRIX_LR = 0.04`
- `WEIGHT_DECAY = 0.2`

The agent is expected to modify this file only, run `uv run train.py`, parse the printed result, and decide whether the change improved `val_bpb`.

For macro quant adaptation, `train.py` should become the editable strategy/search file: factor definitions, signal rules, portfolio construction, rebalance cadence, risk overlays, and parameter choices. The equivalent output should be a deterministic summary block with strategy metrics.

### 4. `analysis.ipynb` reads experiment history

The notebook expects `results.tsv` with columns:

```text
commit	val_bpb	memory_gb	status	description
```

It analyzes keep/discard/crash counts, best validation BPB over time, improvement trajectory, and top kept experiments.

For macro quant, this should become an experiment-analysis notebook over strategy trials, e.g.:

```text
commit	cagr	sharpe	max_drawdown	calmar	cvar_1d	turnover	cost_bps	status	description
```

## Key design specifics worth preserving

The strongest transferable ideas are:

1. **Small surface area**: one fixed environment file, one editable experiment file, one instruction file.
2. **Fixed metric**: agents cannot redefine success after the fact.
3. **Bounded experiment loop**: every trial has a time/resource budget.
4. **Keep/discard discipline**: only objective improvements advance the branch.
5. **Human-readable logs**: every experiment has a short description and status.
6. **Branch isolation**: each research run happens on its own branch.
7. **Simplicity penalty**: small improvements that add ugly complexity are discouraged.

These are directly useful for systematic macro research, where overfitting and narrative drift are major risks.

## What does not transfer directly

The original code is specialized for CUDA LLM pretraining. For retail macro quant, these parts should be removed or replaced:

- PyTorch model architecture.
- Flash Attention kernels.
- Muon optimizer.
- BPE tokenizer.
- parquet text-shard downloader.
- validation bits-per-byte metric.
- 5-minute GPU training budget.
- VRAM/MFU reporting.

The autonomous research loop transfers; the neural network implementation mostly does not.

## Proposed retail macro quant structure

A good adaptation would keep the same conceptual layout:

```text
prepare.py      fixed data ingestion, cleaning, splits, metrics, backtest engine
train.py        editable strategy/search logic
program.md      agent research charter and constraints
analysis.ipynb  experiment log analysis
results.tsv     local experiment ledger
research.md     design notes and findings
```

Suggested macro data cache:

```text
~/.cache/macroresearch/
  rates/
  inflation/
  growth/
  policy/
  fx/
  equities/
  commodities/
  credit/
  positioning/
  calendar/
  metadata/
```

Suggested tradable universe for retail implementation:

- Treasury/cash ETFs: `SGOV`, `BIL`, `SHY`, `IEI`, `IEF`, `TLT`, `TIP`, `VTIP`
- Equity ETFs: `SPY`, `QQQ`, `IWM`, `RSP`, `USMV`, `MTUM`, `QUAL`, sector ETFs
- Commodities: `GLD`, `IAU`, `DBC`, `CPER` with roll-risk caveats
- Credit: `LQD`, `HYG`, `JNK`, `BKLN`
- FX ETFs or major FX only with explicit carry/intervention discussion

## Recommended evaluation metrics

For retail macro quant, the fixed score should not be raw return. It should be drawdown- and implementation-aware.

Minimum metrics:

- CAGR
- annualized volatility
- Sharpe
- max drawdown
- Calmar
- 1% daily CVaR
- worst day
- worst month
- turnover
- cost-adjusted CAGR under several transaction-cost assumptions
- percent time in risky assets
- number of trades/year

A trial should be rejected if it improves CAGR but worsens drawdown, tail risk, or complexity too much.

## Suggested first strategy baseline

The cleanest first baseline is a long-only ETF tactical allocation rule:

- monthly rebalance,
- universe such as `SPY`, `USMV`, `GLD`, `DBC`, with `SHY`/`SGOV` as ballast,
- require price above 200-day moving average,
- rank eligible assets by 6-month momentum,
- hold top 1–2 assets,
- volatility-cap risky allocation,
- residual allocation goes to cash/short-duration Treasuries.

This is a better first target than options, futures, leveraged ETFs, or short books because it matches the retail objective: liquid, explainable, lower operational risk, bounded loss, and implementable in an ~$80k IB account.

## Main adaptation risk

The biggest risk is converting a clean autonomous experiment harness into a narrative macro idea generator. The original repo succeeds because it enforces a fixed metric and mechanical keep/discard loop. The macro version must preserve that discipline by making every trial reproducible, cost-adjusted, and falsifiable.

## Bottom line

`autoresearch` is best understood as a minimal autonomous experimentation pattern, not as reusable trading code. The right adaptation is to replace the LLM-training internals with a fixed macro data/backtest/evaluation harness while preserving the agent loop: clear instructions, one editable strategy file, objective metrics, experiment ledger, branch isolation, and strict keep/discard rules.
