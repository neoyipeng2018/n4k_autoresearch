# CAGR-without-Ruin Retail Macro Quant Autoresearch Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Convert `iter_2` from Karpathy's LLM-pretraining `autoresearch` baseline into a retail macro quant strategy-search repo where the autonomous objective is **maximize CAGR subject to avoiding ruin**.

**Architecture:** Preserve the original `autoresearch` pattern: `prepare.py` is the fixed environment, `train.py` is the only editable experiment target, `program.md` is the agent operating manual, and `results.tsv` logs trials. Replace the old LLM-training internals with a deterministic ETF/macro data loader and backtester. Use `iter_1` assets opportunistically, especially `scripts/retail_quant_screen.py`, `scripts/ingest_public_macro.py`, and framework docs, but simplify the scoring rule so the agent searches for ideas/data that maximize CAGR while treating ruin as a hard disqualifier.

**Tech Stack:** Python standard library + existing dependencies in `pyproject.toml` (`pandas`, `numpy`, `requests`, etc.). Avoid adding new dependencies unless absolutely necessary.

---

## Non-negotiable objective

The repo should optimize **maximum CAGR without ruin**. In this plan, ruin is not a secondary preference metric; it is a hard feasibility constraint. Among non-ruined strategies, rank only by CAGR.

That means:

- Primary optimization metric: `cagr`.
- Hard disqualifier: `ruined == True`. A trial is ruined if the equity curve crosses the configured ruin threshold, produces non-finite equity, bankrupts through leverage/short exposure, or otherwise cannot be implemented without total/near-total capital loss.
- Keep rule: keep a trial if and only if `ruined == False` and `cagr > best_cagr`.
- Discard rule: discard a trial if it crashes, is ruined, or has `cagr <= best_cagr`.
- Other diagnostics such as Sharpe, drawdown, Calmar, CVaR, and volatility may help the agent understand *how ruin happened*, but they must not be optimized directly. They are diagnostic sensors for ruin risk, not ranking objectives.
- The agent instructions must explicitly say it should research new ideas, instruments, regimes, filters, and datasets that could raise CAGR while preventing ruin.

This intentionally shifts the earlier retail-tail-risk framing into a CAGR-first mandate: seek maximum growth, but do not accept strategies that risk wiping out the account.

---

## Target end state

`iter_2` should look like this:

```text
iter_2/
  README.md                 # updated project overview
  program.md                # maximize-CAGR-without-ruin autonomous research instructions
  prepare.py                # fixed data/backtest/evaluation harness
  train.py                  # editable strategy/search logic
  analysis.ipynb            # optional; update later or leave for follow-up
  research.md               # existing research notes
  plan.md                   # this plan
  results.tsv               # generated locally; do not commit unless asked
  scripts/
    ingest_public_macro.py  # copied/adapted from iter_1 if useful
```

The implementation should remove all practical dependence on the old language-model training stack, including neural-network training code, attention kernels, BPE tokenizers, Hugging Face text shards, and validation BPB.

---

## Data policy

Use this priority order:

1. Existing local macro/market cache if present: `~/.cache/macroresearch/`.
2. Scripts from `iter_1/scripts/` to populate the cache.
3. Direct Yahoo Finance chart endpoint from the `iter_1` `retail_quant_screen.py` pattern as a fallback.
4. Always include `DBMF` (iMGP DBi Managed Futures Strategy ETF) in the benchmark data pull. DBMF is the required baseline benchmark for evaluating whether the autonomous strategy search is adding value versus a retail managed-futures ETF proxy.
5. If neither local nor remote data works, fail clearly and tell the user which ingestion command to run.

Useful `iter_1` files:

- `/Users/nyp/n4k_autoresearch/iter_1/scripts/retail_quant_screen.py`
  - already contains ETF data fetching, return construction, monthly rebalancing, and CAGR calculation.
- `/Users/nyp/n4k_autoresearch/iter_1/scripts/ingest_public_macro.py`
  - already writes macro and ETF CSVs to `~/.cache/macroresearch/`.
- `/Users/nyp/n4k_autoresearch/iter_1/universe.md`
  - useful for default ETF universe.
- `/Users/nyp/n4k_autoresearch/iter_1/robustness_grid.csv`
  - useful as historical context only, not as the fixed source of truth.

---

## Detailed implementation todo list

All phases below are completed.

Do **not** implement these items while writing this plan. This checklist exists so a future implementation pass can proceed phase-by-phase without guessing. Each checkbox should be completed, verified, and committed in order unless a later implementer explicitly documents why a different order is safer.

### Phase 0 — Pre-flight and scope lock

- [x] Confirm work is happening in `/Users/nyp/n4k_autoresearch/iter_2`.
- [x] Confirm `original/` remains a clean reference clone and is not edited.
- [x] Inspect `git status --short` at the repo root and inside `iter_2` before making code changes.
- [x] Re-read `research.md` and this `plan.md` before implementation.
- [x] Confirm the objective wording is consistent everywhere: **maximize CAGR without ruin**.
- [x] Confirm ruin is a hard disqualifier, not a ranking metric.
- [x] Confirm DBMF is the required benchmark baseline.
- [x] Decide whether `results.tsv` should remain local-only for this implementation run; default: keep local and ignored unless user asks to commit results.

### Phase 1 — Project/dependency cleanup

- [x] Open `iter_2/pyproject.toml` and identify old language-model-training dependencies and scripts.
- [x] Replace the dependency set with lightweight data-analysis dependencies only: `pandas`, `numpy`, `requests`, and `pytest`/`ruff` as needed.
- [x] Preserve project metadata only if it still matches the new macro-autoresearch purpose.
- [x] Remove stale package index/source configuration that belongs only to the old training stack.
- [x] Run `uv sync` and verify dependency resolution succeeds.
- [x] Run `uv run python -c "import pandas, numpy, requests"` and verify imports succeed.
- [x] Commit the dependency cleanup with a focused docs/config commit message.

### Phase 2 — Data ingestion and cache policy

- [x] Create `iter_2/scripts/` if it does not exist.
- [x] Copy or adapt `/Users/nyp/n4k_autoresearch/iter_1/scripts/ingest_public_macro.py` into `iter_2/scripts/ingest_public_macro.py`.
- [x] Ensure the adapted ingestion script writes or reads from `~/.cache/macroresearch/` consistently.
- [x] Add `DBMF` to the market/ETF universe pulled by the ingestion path.
- [x] Ensure the ingestion script can fetch DBMF adjusted close data from Yahoo Finance chart endpoints.
- [x] Ensure missing DBMF history is handled explicitly, because DBMF has a shorter live history than older ETFs.
- [x] Add clear metadata/manifest output identifying source URLs, symbols, fetch dates, and observation ranges.
- [x] Run the ingestion command only when implementing, not while editing this plan.
- [x] Verify generated CSVs include enough columns for `prepare.py` to load prices by symbol.
- [x] Commit ingestion changes separately from evaluator changes.

### Phase 3 — Fixed evaluator/backtester design in `prepare.py`

- [x] Rewrite `iter_2/prepare.py` as the fixed data, benchmark, backtest, and evaluation harness.
- [x] Define a machine-readable `RUIN_EQUITY_THRESHOLD`, defaulting to `0.25` unless changed deliberately.
- [x] Implement deterministic daily adjusted-close loading for the strategy universe.
- [x] Implement deterministic daily adjusted-close loading for `DBMF` as the benchmark.
- [x] Align all symbols on valid trading dates without lookahead.
- [x] Implement `calculate_cagr(equity_curve)` in `prepare.py` only.
- [x] Implement `calculate_dbmf_benchmark(prices)` or equivalent helper that returns DBMF equity and CAGR over the same evaluation window as the tested strategy.
- [x] Implement a backtest function that accepts `train.py` weights/signals and produces a strategy equity curve.
- [x] Implement ruin detection for strategy equity: threshold breach, non-finite values, zero/negative equity, leverage/short bankruptcy conditions, and non-finite CAGR.
- [x] Implement comparable ruin detection for the DBMF benchmark for transparency, even though DBMF is a benchmark rather than a candidate strategy.
- [x] Print machine-parseable output lines for `cagr:`, `ruined:`, `ruin_threshold:`, `dbmf_cagr:`, `dbmf_ruined:`, and `excess_cagr_vs_dbmf:`.
- [x] Keep the keep/discard rule CAGR-first: a candidate is eligible only when `ruined == false`; among eligible candidates, rank by `cagr`.
- [x] Keep DBMF as a benchmark/reporting baseline, not a replacement objective unless explicitly specified later.
- [x] Remove stale text-token, model-training, and validation-BPB logic from `prepare.py`.
- [x] Commit the fixed evaluator rewrite separately.

### Phase 4 — Editable strategy file in `train.py`

- [x] Rewrite `iter_2/train.py` as the only editable strategy target.
- [x] Import fixed loader/backtester/evaluator helpers from `prepare.py`.
- [x] Define a default liquid retail macro ETF universe plus `DBMF` availability for benchmark loading.
- [x] Keep DBMF out of the candidate trading universe by default unless explicitly testing “buy DBMF” as a candidate; DBMF’s required role is benchmark baseline.
- [x] Implement the initial strategy as a simple, transparent baseline such as monthly top-1 or top-2 momentum across retail macro ETFs.
- [x] Ensure the initial strategy produces weights/signals only from information available before the rebalance date.
- [x] Ensure `uv run train.py` prints the parser lines emitted by `prepare.py`.
- [x] Ensure `train.py` does not compute its own CAGR ranking logic separate from `prepare.py`.
- [x] Commit the editable strategy rewrite separately.

### Phase 5 — Agent operating manual in `program.md`

- [x] Rewrite `iter_2/program.md` to describe the new autonomous macro strategy-search loop.
- [x] State that `prepare.py` is fixed and must not be edited by the experiment agent.
- [x] State that `train.py` is the only strategy file the experiment agent edits.
- [x] State the objective: maximize CAGR without ruin.
- [x] State the hard keep rule: keep only if `ruined == false` and `cagr > best_cagr`.
- [x] State the DBMF benchmark requirement: every run must report `dbmf_cagr` and `excess_cagr_vs_dbmf` over the same evaluation window.
- [x] State DBMF is not a second ranking metric by default; it is the benchmark baseline to beat and diagnose against.
- [x] Describe how to record `results.tsv` rows, including DBMF benchmark fields.
- [x] Remove stale BPB/tokenizer/model-training instructions.
- [x] Commit the `program.md` rewrite separately.

### Phase 6 — README and user-facing documentation

- [x] Rewrite `iter_2/README.md` to explain the repo purpose: autonomous retail macro quant strategy search for maximum CAGR without ruin.
- [x] Document setup commands: `uv sync`, optional ingestion command, and baseline run command.
- [x] Document DBMF as the required benchmark baseline.
- [x] Document expected output lines from `uv run train.py`, including `dbmf_cagr` and `excess_cagr_vs_dbmf`.
- [x] Document that diagnostics may explain ruin but do not replace CAGR ranking.
- [x] Document that `results.tsv` is a local experiment ledger unless the user asks to commit it.
- [x] Commit README updates separately.

### Phase 7 — Test suite

- [x] Create `iter_2/tests/` if it does not exist.
- [x] Add tests for `calculate_cagr` on constant, positive-growth, declining, and invalid/empty equity curves.
- [x] Add tests for ruin detection at, above, and below `RUIN_EQUITY_THRESHOLD`.
- [x] Add tests that DBMF benchmark calculation uses the same start/end dates as the strategy equity curve.
- [x] Add tests that output parsing lines include `cagr`, `ruined`, `dbmf_cagr`, and `excess_cagr_vs_dbmf`.
- [x] Add a small synthetic-price backtest fixture to verify no lookahead at rebalance boundaries.
- [x] Run `uv run pytest -q` and verify all tests pass.
- [x] Commit tests separately.

### Phase 8 — Local-output hygiene

- [x] Update `iter_2/.gitignore` for local outputs: `results.tsv`, `run.log`, cache files, downloaded data snapshots if any, and temporary analysis artifacts.
- [x] Verify `.gitignore` does not hide source files, tests, docs, or the ingestion script.
- [x] Decide whether a sample `results.example.tsv` is useful; default: include only if docs need a concrete schema example.
- [x] Commit `.gitignore` changes separately.

### Phase 9 — Baseline benchmark run against DBMF

- [x] Run `uv run train.py > run.log 2>&1` after implementation.
- [x] Verify `run.log` contains `cagr:`, `ruined:`, `ruin_threshold:`, `dbmf_cagr:`, `dbmf_ruined:`, and `excess_cagr_vs_dbmf:`.
- [x] Verify the strategy and DBMF benchmark use the same evaluation start/end dates.
- [x] Verify DBMF’s shorter inception history does not accidentally give the strategy a different backtest window.
- [x] Record the first row in `results.tsv` with strategy CAGR, ruin flag, DBMF CAGR, DBMF ruin flag, excess CAGR versus DBMF, status, and description.
- [x] Do not claim success merely because the strategy CAGR is positive; confirm the strategy is not ruined and compare it to DBMF in the report.
- [x] Commit only source/doc/test changes, not local run logs or local ledgers unless the user explicitly asks.

### Phase 10 — First autonomous research iteration setup

- [x] Seed `program.md` with first experiment directions: momentum windows, universe variants, top-N selection, cash/ballast logic, regime filters, and macro data filters.
- [x] Require every future idea to state why it might improve CAGR without causing ruin.
- [x] Require every future idea to check whether it beats or lags DBMF over the matched window.
- [x] Keep future experiment commits small: one idea per commit.
- [x] Reset discarded commits after logging results.
- [x] Stop and ask the user before introducing leveraged/inverse ETPs, options, futures, or short-only rules.

### Phase 11 — Final verification before handing off implementation

- [x] Run `uv sync`.
- [x] Run `uv run pytest -q`.
- [x] Run `uv run train.py`.
- [x] Search active docs/source for stale old-objective terms: `val_bpb`, tokenizer, text shards, BPB, and old model-training instructions.
- [x] Search `plan.md`, `README.md`, and `program.md` for objective consistency: maximum CAGR without ruin, DBMF benchmark, hard ruin reject.
- [x] Review `git diff --stat` and full diff for accidental scope creep.
- [x] Prepare a concise implementation summary with test results, baseline CAGR, DBMF CAGR, excess CAGR versus DBMF, and ruin status.

---

# Task 1: Replace `pyproject.toml` dependencies with data-analysis dependencies

**Status:** Completed.

**Objective:** Remove unnecessary LLM-training dependencies and keep only what the macro backtester needs.

**Files:**

- Modify: `iter_2/pyproject.toml`

**Implementation:**

Replace the dependency block with something like:

```toml
[project]
name = "macro-autoresearch"
version = "0.1.0"
description = "Autonomous maximize-CAGR-without-ruin retail macro quant strategy search"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "numpy>=2.2.6",
    "pandas>=2.3.3",
    "requests>=2.32.0",
    "matplotlib>=3.10.8",
]
```

Remove any extra package-source/index blocks left over from the old model-training setup; the new project should not require a custom package index.

**Verification:**

Run:

```bash
cd /Users/nyp/n4k_autoresearch/iter_2
uv sync
```

Expected: dependencies install as a lightweight data-analysis project.

---

# Task 2: Add or copy data ingestion script from `iter_1`

**Status:** Completed.

**Objective:** Give `iter_2` a way to populate `~/.cache/macroresearch/` without depending on the old text-shard downloader.

**Files:**

- Create: `iter_2/scripts/ingest_public_macro.py`
- Source reference: `iter_1/scripts/ingest_public_macro.py`

**Implementation:**

Copy the `iter_1` script nearly verbatim first. It is already dependency-light and writes useful CSVs.

Minimum adapted header:

```python
#!/usr/bin/env python3
"""
Ingest public macro and market data into ~/.cache/macroresearch/.

This is optional but recommended before running maximize-CAGR-without-ruin strategy search.
The strategy harness can also fetch Yahoo ETF prices directly when local CSVs
are absent.
"""
```

Keep its FRED and Yahoo groups, but consider expanding Yahoo groups to match the CAGR-search ETF universe:

```python
YAHOO_GROUPS = {
    "equities/etf_prices_yahoo.csv": [
        "SPY", "QQQ", "IWM", "RSP", "USMV", "QUAL", "MTUM", "VLUE",
        "XLF", "XLK", "XLE", "XLP", "XLU", "XLV", "XLI", "XLY", "XLB", "XLRE",
        "ACWI", "EFA", "EEM", "EWJ", "FXI", "KWEB",
    ],
    "rates/rates_etf_prices_yahoo.csv": ["SGOV", "BIL", "SHY", "IEI", "IEF", "TLT", "TIP", "VTIP"],
    "commodities/commodity_etf_prices_yahoo.csv": ["GLD", "IAU", "DBC", "USO", "SLV", "CPER"],
    "credit/credit_etf_prices_yahoo.csv": ["LQD", "HYG", "JNK", "BKLN"],
    "fx/fx_etf_prices_yahoo.csv": ["UUP", "FXE", "FXY", "FXB", "FXA", "FXC", "FXF"],
}
```

**Verification:**

Run:

```bash
cd /Users/nyp/n4k_autoresearch/iter_2
uv run scripts/ingest_public_macro.py
```

Expected: writes files under `~/.cache/macroresearch/metadata/coverage.json` and prints a JSON coverage summary.

---

# Task 3: Rewrite `prepare.py` as fixed CAGR evaluation harness

**Status:** Completed.

**Objective:** Replace LLM data/tokenizer/evaluation code with stable market-data loading, strategy backtesting, and CAGR calculation.

**Files:**

- Replace: `iter_2/prepare.py`

**Design:**

`prepare.py` should expose these stable APIs:

```python
CACHE_DIR = Path.home() / ".cache" / "macroresearch"
DEFAULT_START = "2016-01-01"
DEFAULT_DATA_START = "2015-01-01"
DEFAULT_UNIVERSE = ["SPY", "QQQ", "RSP", "IWM", "USMV", "QUAL", "MTUM", "VLUE", "IEF", "TLT", "SHY", "SGOV", "GLD", "DBC", "LQD", "HYG"]
BENCHMARK_SYMBOL = "DBMF"  # iMGP DBi Managed Futures Strategy ETF
RUIN_EQUITY_THRESHOLD = 0.25  # hard ineligibility guard: equity <= 25% of start is ruin

class MarketData:
    prices: dict[str, pd.Series]
    returns: pd.DataFrame

def load_market_data(symbols: list[str], data_start: str = DEFAULT_DATA_START) -> MarketData: ...
def backtest_strategy(selector, symbols: list[str], start: str = DEFAULT_START) -> dict: ...
def calculate_cagr(equity_curve: pd.Series) -> float: ...
def evaluate_cagr(selector, symbols: list[str] | None = None, start: str = DEFAULT_START) -> dict: ...
def print_summary(result: dict) -> None: ...
```

**Important:** `evaluate_cagr` must be the ground-truth metric. `train.py` may define strategies but must not redefine CAGR.

**Code skeleton:**

```python
from __future__ import annotations

import json
import math
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import pandas as pd

CACHE_DIR = Path.home() / ".cache" / "macroresearch"
DEFAULT_START = "2016-01-01"
DEFAULT_DATA_START = "2015-01-01"
DEFAULT_UNIVERSE = [
    "SPY", "QQQ", "RSP", "IWM", "USMV", "QUAL", "MTUM", "VLUE",
    "IEF", "TLT", "SHY", "SGOV", "GLD", "DBC", "LQD", "HYG",
]
BENCHMARK_SYMBOL = "DBMF"  # iMGP DBi Managed Futures Strategy ETF
RUIN_EQUITY_THRESHOLD = 0.25  # hard ineligibility guard: equity <= 25% of start is ruin

Weights = dict[str, float]
Selector = Callable[[pd.Timestamp, pd.DataFrame], Weights]

@dataclass
class MarketData:
    prices: pd.DataFrame
    returns: pd.DataFrame


def fetch_yahoo_prices(symbol: str, start: str, end: str | None = None) -> pd.Series:
    start_ts = int(pd.Timestamp(start, tz="UTC").timestamp())
    end_ts = int(pd.Timestamp(end or datetime.now(timezone.utc).date().isoformat(), tz="UTC").timestamp())
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?period1={start_ts}&period2={end_ts}&interval=1d&events=history&includeAdjustedClose=true"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    result = data["chart"]["result"][0]
    idx = pd.to_datetime(result["timestamp"], unit="s", utc=True).tz_convert(None).normalize()
    adj = result["indicators"]["adjclose"][0]["adjclose"]
    return pd.Series(adj, index=idx, name=symbol).dropna()


def load_cached_yahoo_csv(symbols: list[str]) -> pd.DataFrame:
    frames = []
    for path in CACHE_DIR.glob("**/*_yahoo.csv"):
        df = pd.read_csv(path)
        if {"date", "symbol", "adj_close"}.issubset(df.columns):
            df = df[df["symbol"].isin(symbols)].copy()
            if not df.empty:
                df["date"] = pd.to_datetime(df["date"])
                frames.append(df.pivot(index="date", columns="symbol", values="adj_close"))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, axis=1).sort_index().loc[:, lambda x: ~x.columns.duplicated()]


def load_market_data(symbols: list[str], data_start: str = DEFAULT_DATA_START) -> MarketData:
    cached = load_cached_yahoo_csv(symbols)
    missing = [s for s in symbols if s not in cached.columns]
    fetched = []
    for sym in missing:
        try:
            fetched.append(fetch_yahoo_prices(sym, data_start))
        except Exception as exc:
            print(f"WARN: failed to fetch {sym}: {exc}")
    prices = pd.concat([cached] + fetched, axis=1) if fetched or not cached.empty else pd.DataFrame()
    prices = prices.sort_index().ffill().dropna(how="all")
    prices = prices[[s for s in symbols if s in prices.columns]].dropna(how="all")
    if prices.empty:
        raise RuntimeError("No usable market price data. Run scripts/ingest_public_macro.py or check network access.")
    returns = prices.pct_change().fillna(0.0)
    return MarketData(prices=prices, returns=returns)


def calculate_cagr(equity_curve: pd.Series) -> float:
    equity_curve = equity_curve.dropna()
    if len(equity_curve) < 2:
        return float("nan")
    years = (equity_curve.index[-1] - equity_curve.index[0]).days / 365.25
    if years <= 0 or equity_curve.iloc[0] <= 0 or equity_curve.iloc[-1] <= 0:
        return float("nan")
    return float((equity_curve.iloc[-1] / equity_curve.iloc[0]) ** (1 / years) - 1)


def month_end_dates(index: pd.DatetimeIndex) -> set[pd.Timestamp]:
    s = pd.Series(index=index, data=index)
    return set(s.groupby([s.index.year, s.index.month]).max())


def backtest_strategy(selector: Selector, symbols: list[str], start: str = DEFAULT_START) -> dict:
    data = load_market_data(symbols)
    prices = data.prices.loc[pd.Timestamp(start):]
    returns = data.returns.reindex(prices.index).fillna(0.0)
    rebalance_days = month_end_dates(prices.index)
    weights: Weights = {}
    equity = []
    current_value = 1.0
    allocations = []
    for day in prices.index:
        if day in rebalance_days or not weights:
            weights = selector(day, data.prices.loc[:day])
            allocations.append((day, dict(weights)))
        daily_ret = 0.0
        for sym, weight in weights.items():
            if sym == "CASH":
                asset_ret = 0.0
            elif sym in returns.columns:
                asset_ret = float(returns.loc[day, sym])
            else:
                asset_ret = 0.0
            daily_ret += weight * asset_ret
        current_value *= 1.0 + daily_ret
        equity.append((day, current_value))
    equity_curve = pd.Series({day: value for day, value in equity}).sort_index()
    cagr = calculate_cagr(equity_curve)
    ruined = bool((equity_curve <= RUIN_EQUITY_THRESHOLD).any()) or not math.isfinite(cagr)
    return {
        "cagr": cagr,
        "ruined": ruined,
        "ruin_threshold": RUIN_EQUITY_THRESHOLD,
        "end_multiple": float(equity_curve.iloc[-1]),
        "start": str(equity_curve.index[0].date()),
        "end": str(equity_curve.index[-1].date()),
        "current_allocation": allocations[-1][1] if allocations else {},
        "equity_curve": equity_curve,
    }


def evaluate_cagr(selector: Selector, symbols: list[str] | None = None, start: str = DEFAULT_START) -> dict:
    return backtest_strategy(selector, symbols or DEFAULT_UNIVERSE, start=start)


def print_summary(result: dict) -> None:
    print("---")
    print(f"cagr:             {result['cagr']:.6f}")
    print(f"ruined:           {str(result['ruined']).lower()}")
    print(f"ruin_threshold:   {result['ruin_threshold']:.6f}")
    print(f"end_multiple:     {result['end_multiple']:.6f}")
    print(f"start:            {result['start']}")
    print(f"end:              {result['end']}")
    print(f"allocation:       {json.dumps(result['current_allocation'], sort_keys=True)}")
```

**Verification:**

Add a temporary smoke-test block or run through `train.py` after Task 4. The summary must include a line starting exactly:

```text
cagr:
```

---

# Task 4: Rewrite `train.py` as editable strategy file

**Status:** Completed.

**Objective:** Replace GPT training code with a baseline strategy and a clear editable area for autonomous CAGR search.

**Files:**

- Replace: `iter_2/train.py`

**Design:**

`train.py` should:

1. import the fixed evaluator from `prepare.py`,
2. define the tradable universe,
3. define helper functions for SMA/momentum if needed,
4. define a `select_weights(day, prices)` function,
5. call `evaluate_cagr(select_weights, SYMBOLS)`,
6. print the canonical summary.

**Baseline strategy:** choose a CAGR-oriented baseline. Since the user only wants CAGR, start with an aggressive but still simple monthly relative-strength rule:

- universe: equity/factor/sector/commodity/credit ETFs,
- monthly rebalance,
- rank by 6-month total return,
- hold top 1 asset at 100%,
- if all momentum is negative, still hold the top asset rather than going to cash unless the configured ruin guard is triggered, because the objective is maximum CAGR without ruin.

**Code skeleton:**

```python
"""
Maximize-CAGR-without-ruin autoresearch strategy file.

The agent may edit this file to maximize CAGR. Do not edit prepare.py.
Run: uv run train.py
"""

from __future__ import annotations

import pandas as pd

from prepare import evaluate_cagr, print_summary

SYMBOLS = [
    "SPY", "QQQ", "RSP", "IWM", "USMV", "QUAL", "MTUM", "VLUE",
    "XLK", "XLF", "XLE", "XLI", "XLY", "XLP", "XLU", "XLV",
    "IEF", "TLT", "GLD", "DBC", "LQD", "HYG",
]

MOMENTUM_DAYS = 126
TOP_N = 1


def lookback_return(series: pd.Series, n: int) -> float | None:
    series = series.dropna()
    if len(series) <= n:
        return None
    if series.iloc[-n - 1] <= 0:
        return None
    return float(series.iloc[-1] / series.iloc[-n - 1] - 1.0)


def select_weights(day: pd.Timestamp, prices: pd.DataFrame) -> dict[str, float]:
    scores = []
    for sym in SYMBOLS:
        if sym not in prices.columns:
            continue
        score = lookback_return(prices[sym], MOMENTUM_DAYS)
        if score is not None:
            scores.append((score, sym))
    if not scores:
        return {"SPY": 1.0}
    selected = [sym for _score, sym in sorted(scores, reverse=True)[:TOP_N]]
    weight = 1.0 / len(selected)
    return {sym: weight for sym in selected}


if __name__ == "__main__":
    result = evaluate_cagr(select_weights, SYMBOLS)
    print_summary(result)
```

**Verification:**

Run:

```bash
cd /Users/nyp/n4k_autoresearch/iter_2
uv run train.py
```

Expected output contains:

```text
---
cagr:             <number>
ruined:           false
ruin_threshold:   <number>
dbmf_cagr:        <number>
dbmf_ruined:      false
excess_cagr_vs_dbmf: <number>
end_multiple:     <number>
```

---

# Task 5: Rewrite `program.md` for maximum-CAGR-without-ruin autonomous loop

**Status:** Completed.

**Objective:** Make the agent instructions match the new objective and prevent accidental optimization of other metrics.

**Files:**

- Replace: `iter_2/program.md`

**Required content:**

The new `program.md` should explicitly say:

- This is an autonomous retail macro quant strategy search for maximum CAGR without ruin.
- `prepare.py` is fixed and must not be edited.
- `train.py` is the only editable experiment target.
- The objective is **higher CAGR subject to no ruin**.
- Treat ruin as a hard reject condition. Do not optimize Sharpe, drawdown, Calmar, CVaR, volatility, or transaction costs directly; use them only if they help identify ruin risk or broken strategies.
- The output parser reads `^cagr:`.
- `results.tsv` columns are `commit`, `cagr`, `ruined`, `dbmf_cagr`, `dbmf_ruined`, `excess_cagr_vs_dbmf`, `status`, `description`.

**Suggested `program.md` structure:**

```markdown
# Maximum-CAGR-without-ruin macro autoresearch

This repo runs autonomous strategy experiments for retail macro quant trading.
The objective is simple: maximize CAGR without ruin. The agent should actively research ideas, datasets, instruments, filters, and market regimes that could produce the highest CAGR while avoiding account wipeout or near-wipeout. Every run must benchmark against DBMF (iMGP DBi Managed Futures Strategy ETF) over the same date window.

## Fixed files

Do not edit `prepare.py`. It defines data loading, backtesting, and CAGR evaluation.

## Editable file

Edit only `train.py`. Change strategy logic, universe, parameters, ranking rules,
rebalance behavior, and allocation rules to improve CAGR.

## Metric

The ground-truth metric is the line printed by `uv run train.py`:

```text
cagr:             0.123456
```

Higher is better, unless the strategy is ruined.

Do not rank strategies by Sharpe, volatility, Calmar, CVaR, turnover, complexity, or excess return versus DBMF. However, reject a strategy if its equity curve indicates ruin or near-ruin under the configured hard guard. DBMF is the required benchmark baseline and diagnostic comparison; among non-ruined candidate strategies, ranking remains by CAGR.

## results.tsv

Use tab-separated columns:

```text
commit	cagr	ruined	dbmf_cagr	dbmf_ruined	excess_cagr_vs_dbmf	status	description
```

Status is one of:

- `keep`: CAGR improved versus previous best.
- `discard`: CAGR did not improve.
- `crash`: experiment failed to run.

## Loop

1. Check git state.
2. Modify `train.py` with one CAGR-oriented idea.
3. Commit.
4. Run `uv run train.py > run.log 2>&1`.
5. Extract `cagr` with `grep "^cagr:" run.log`.
6. Extract `ruined` with `grep "^ruined:" run.log`.
7. Extract `dbmf_cagr`, `dbmf_ruined`, and `excess_cagr_vs_dbmf` with `grep "^dbmf_cagr:\|^dbmf_ruined:\|^excess_cagr_vs_dbmf:" run.log`.
8. If `ruined` is `false` and CAGR improved, keep the commit.
9. If the run is ruined or CAGR did not improve, append discard result and reset to previous commit.
10. Continue.
```

**Verification:**

Read `program.md` and confirm it does not retain `val_bpb`, tokenizer, or 5-minute LLM-training language.

---

# Task 6: Update `README.md`

**Status:** Completed.

**Objective:** Explain the new repo purpose and commands.

**Files:**

- Replace or heavily modify: `iter_2/README.md`

**Suggested content outline:**

```markdown
# macro-autoresearch

Autonomous retail macro quant strategy search for maximum CAGR without ruin.

## Objective

Maximize CAGR without ruin. Ruin is a hard disqualifier. DBMF is the required matched-window benchmark baseline, but candidate strategies are ranked by CAGR among non-ruined runs.

## Files

- `prepare.py`: fixed data/backtest/CAGR evaluator.
- `train.py`: editable strategy file.
- `program.md`: agent operating instructions.
- `results.tsv`: local experiment ledger.
- `scripts/ingest_public_macro.py`: optional data ingestion.

## Setup

```bash
uv sync
uv run scripts/ingest_public_macro.py  # optional but recommended
uv run train.py
```

## Output

```text
---
cagr:             0.123456
ruined:           false
ruin_threshold:   0.250000
dbmf_cagr:        0.075000
dbmf_ruined:      false
excess_cagr_vs_dbmf: 0.048456
end_multiple:     2.345678
start:            2016-01-01
end:              2026-05-27
allocation:       {"QQQ": 1.0}
```

## Autonomous loop

Follow `program.md`.
```

**Verification:**

Run:

```bash
grep -n "val_bpb\|tokenizer\|BPB\|LLM-training" README.md
```

Expected: no stale references unless they appear in a historical note.

---

# Task 7: Create a minimal test suite

**Status:** Completed.

**Objective:** Lock down CAGR calculation and basic backtest behavior so future agents do not accidentally redefine the objective.

**Files:**

- Create: `iter_2/tests/test_prepare.py`

**Test snippets:**

```python
import math
import pandas as pd

from prepare import calculate_cagr


def test_calculate_cagr_one_year_double():
    curve = pd.Series(
        [1.0, 2.0],
        index=[pd.Timestamp("2020-01-01"), pd.Timestamp("2020-12-31")],
    )
    assert math.isclose(calculate_cagr(curve), 1.0, rel_tol=0.02)


def test_calculate_cagr_four_year_16x():
    curve = pd.Series(
        [1.0, 16.0],
        index=[pd.Timestamp("2020-01-01"), pd.Timestamp("2024-01-01")],
    )
    assert math.isclose(calculate_cagr(curve), 1.0, rel_tol=0.01)
```

If using `pytest`, add it to dependencies:

```toml
"pytest>=8.0.0",
```

Alternatively, if avoiding pytest, create a simple `tests/run_tests.py` with plain asserts.

**Verification:**

Run:

```bash
cd /Users/nyp/n4k_autoresearch/iter_2
uv run pytest -q
```

Expected:

```text
2 passed
```

---

# Task 8: Initialize `results.tsv` format

**Status:** Completed.

**Objective:** Make the experiment ledger match the new metric and DBMF benchmark baseline.

**Files:**

- Create local file: `iter_2/results.tsv`

**Content:**

```text
commit	cagr	ruined	dbmf_cagr	dbmf_ruined	excess_cagr_vs_dbmf	status	description
```

**Important:** Decide whether this should be committed. The original repo treats result ledgers as local scratch files. I recommend adding `results.tsv` to `.gitignore` and not committing it unless the user asks.

**Verification:**

Run:

```bash
head -1 results.tsv
```

Expected:

```text
commit	cagr	ruined	dbmf_cagr	dbmf_ruined	excess_cagr_vs_dbmf	status	description
```

---

# Task 9: Update `.gitignore`

**Status:** Completed.

**Objective:** Ignore local experiment outputs.

**Files:**

- Modify: `iter_2/.gitignore`

**Add:**

```gitignore
# Local experiment outputs
results.tsv
run.log
*.log
__pycache__/
.pytest_cache/
```

**Verification:**

Run:

```bash
git status --short
```

Expected: `results.tsv` and `run.log` should not appear if present.

---

# Task 10: Run baseline and verify objective extraction

**Status:** Completed.

**Objective:** Confirm the new system runs end-to-end, prints a parseable CAGR, and benchmarks the baseline against DBMF.

**Commands:**

```bash
cd /Users/nyp/n4k_autoresearch/iter_2
uv run train.py > run.log 2>&1
grep "^cagr:" run.log
grep "^ruined:" run.log
grep "^dbmf_cagr:" run.log
grep "^dbmf_ruined:" run.log
grep "^excess_cagr_vs_dbmf:" run.log
```

Expected:

```text
cagr:             <float>
ruined:           false
dbmf_cagr:        <float>
dbmf_ruined:      false
excess_cagr_vs_dbmf: <float>
```

Then record baseline:

```bash
commit=$(git rev-parse --short HEAD)
cagr=$(grep "^cagr:" run.log | awk '{print $2}')
ruined=$(grep "^ruined:" run.log | awk '{print $2}')
dbmf_cagr=$(grep "^dbmf_cagr:" run.log | awk '{print $2}')
dbmf_ruined=$(grep "^dbmf_ruined:" run.log | awk '{print $2}')
excess=$(grep "^excess_cagr_vs_dbmf:" run.log | awk '{print $2}')
printf "%s\t%s\t%s\t%s\t%s\t%s\tkeep\tbaseline strategy benchmarked against DBMF\n" "$commit" "$cagr" "$ruined" "$dbmf_cagr" "$dbmf_ruined" "$excess" >> results.tsv
```

---

# Task 11: First maximum-CAGR-without-ruin experiment ideas

**Status:** Completed.

**Objective:** Give future agents initial directions that are aligned with the user's maximum-CAGR-without-ruin objective.

Because CAGR is the ranking metric, early experiments should include more aggressive return-seeking variants than the previous tail-risk framework, while keeping hard ruin guards in place.

Suggested `train.py` experiments:

1. **Top-1 6-month momentum across aggressive universe**
   - `QQQ`, `XLK`, `XLY`, `IWM`, `SPY`, `MTUM`, `HYG`, `GLD`, `DBC`.
2. **Top-1 12-month momentum**
   - Replace `MOMENTUM_DAYS = 126` with `252`.
3. **Top-2 equal weight**
   - Set `TOP_N = 2`; may reduce concentration but can lower CAGR, so keep only if CAGR improves.
4. **No cash rule**
   - Always hold the highest momentum asset even if momentum is negative.
5. **Sector rotation**
   - Add all sector ETFs and hold the strongest sector.
6. **Leveraged ETFs only if explicitly acceptable later**
   - Do not add by default unless user approves, because they introduce a qualitatively different product universe. If the user truly means unconstrained CAGR, this is the obvious next question.

Example code change for top-1 sector rotation:

```python
SYMBOLS = [
    "SPY", "QQQ", "IWM", "RSP",
    "XLK", "XLY", "XLF", "XLE", "XLI", "XLP", "XLU", "XLV", "XLB", "XLRE",
    "MTUM", "QUAL", "VLUE", "USMV",
    "GLD", "DBC", "HYG", "TLT",
]
MOMENTUM_DAYS = 126
TOP_N = 1
```

Example code change for weighted top-3 by momentum strength:

```python
def select_weights(day: pd.Timestamp, prices: pd.DataFrame) -> dict[str, float]:
    scores = []
    for sym in SYMBOLS:
        if sym not in prices.columns:
            continue
        score = lookback_return(prices[sym], MOMENTUM_DAYS)
        if score is not None:
            scores.append((max(score, 0.0), sym))
    if not scores:
        return {"SPY": 1.0}
    selected = sorted(scores, reverse=True)[:3]
    total = sum(score for score, _sym in selected)
    if total <= 0:
        return {selected[0][1]: 1.0}
    return {sym: score / total for score, sym in selected}
```

Remember: keep only if CAGR improves.

---

# Acceptance criteria

Implementation is complete when:

- `uv sync` succeeds as a lightweight data-analysis project.
- `uv run train.py` runs locally and prints `cagr:`, `ruined:`, `dbmf_cagr:`, and `excess_cagr_vs_dbmf:`.
- `prepare.py` owns CAGR calculation and evaluation.
- `train.py` is the only strategy file agents need to edit.
- `program.md` says CAGR is the optimization objective, ruin is a hard disqualifier, and DBMF is the required benchmark baseline.
- `results.tsv` format is `commit cagr ruined dbmf_cagr dbmf_ruined excess_cagr_vs_dbmf status description`.
- stale `val_bpb`, tokenizer, and LLM-training instructions are removed from active docs.
- tests verify `calculate_cagr`.

---

# Risks and open questions

1. **Maximum-CAGR-without-ruin optimization invites overfitting.** This is explicitly accepted by the latest instruction, but the repo should make that objective and hard ruin guard obvious.
2. **Data source reliability.** Yahoo can rate-limit. The local cache and `ingest_public_macro.py` reduce this problem.
3. **Survivorship bias.** ETF universe choices may include funds that did not exist for the full period. The loader should start evaluation only when enough data exists, or agents should handle missing symbols carefully.
4. **Ruin definition must be explicit.** The plan should choose a simple default such as `RUIN_EQUITY_THRESHOLD = 0.25`, meaning a strategy that loses 75% from starting equity is ineligible even if its final CAGR is high. The threshold can be changed later, but the evaluator must report it.
5. **Leveraged ETFs.** Leveraged ETFs may raise CAGR in backtests but can create path-dependent ruin. Do not include them unless the strategy evaluator has explicit ruin detection and the user approves the product universe.
6. **Transaction costs ignored unless they cause ruin.** For the first implementation, rank by raw CAGR among non-ruined strategies. If costs are added later, decide whether the metric is raw CAGR or cost-adjusted CAGR before experiments continue.

---

# Recommended implementation order

1. Update `pyproject.toml`.
2. Copy/adapt `scripts/ingest_public_macro.py`.
3. Rewrite `prepare.py`.
4. Rewrite `train.py`.
5. Rewrite `program.md`.
6. Update `README.md`.
7. Add tests for CAGR.
8. Initialize/ignore local outputs.
9. Run baseline and record `results.tsv`.
10. Run the first baseline and benchmark it against DBMF.
11. Begin autonomous maximum-CAGR-without-ruin experiments.
