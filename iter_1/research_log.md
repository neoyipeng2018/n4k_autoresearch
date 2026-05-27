# Research Log: may27-cross-asset

Branch: `macroresearch/may27-cross-asset`
Status: first research cycle complete; one watchlist idea developed.

## Data ingestion

Created and ran `scripts/ingest_public_macro.py`.

Local data root:

```text
~/.cache/macroresearch/
```

Public sources ingested:

- FRED fredgraph CSV endpoints for rates, real yields, breakevens, inflation, wages, growth, labor, policy, Fed balance sheet, FX, equity indices, commodities, credit spreads, and financial conditions.
- CFTC financial futures 2026 history zip downloaded manually to `positioning/FinFutYY.txt`.
- Yahoo Finance endpoint attempted for ETFs but returned HTTP 429 rate-limit errors; FRED category data was sufficient to start a first pass.
- Event calendar is currently a local stub and should be supplemented from official sources for event-sensitive ideas.

Known data gaps:

- ETF proxy price ingestion from Yahoo failed due 429 rate limits.
- Positioning exists only as raw CFTC text; it has not been parsed into clean positioning metrics.
- Event calendar not yet populated from official sources.
- Commodity futures curve/inventory data not yet ingested.
- Treasury issuance/refunding/auction data not yet ingested.

## Macro regime snapshot

As of latest ingested observations:

### Growth

US hard activity is still resilient rather than recessionary. Real GDP latest observation was 2026-01-01; retail sales and industrial production were latest through 2026-04-01. Payrolls rose 115k in the latest monthly observation, unemployment was 4.3, initial claims were 209k on 2026-05-16, and job openings were 6866k in 2026-03.

### Inflation

Inflation remains above target. Headline CPI was 3.95% year over year in 2026-04; core CPI was 2.99%; core PCE was 3.20% in 2026-03. Median CPI annualized monthly change was 4.93 in 2026-04. Michigan inflation expectations were 4.7 in 2026-04.

### Policy

The effective fed funds rate was 3.62 on 2026-05-22. The front end has eased over the trailing year, but nominal yields have risen recently: 2y yield was 4.08 and up 65 bp over roughly 63 trading observations; 10y was 4.57 and up 54 bp over the same window.

### Liquidity

Fed balance sheet data is mixed/noisy but total assets were 6.713T on 2026-05-20. Financial conditions remain easy: NFCI was -0.523 on 2026-05-15.

### Fiscal impulse

Not enough local data yet. Treasury issuance/refunding and fiscal data should be ingested before accepting fiscal/term-premium ideas.

### Credit

Credit remains benign. IG OAS was 0.74 and HY OAS was 2.74 as of 2026-05-25, both compressed over the prior quarter. This argues against accepting short-credit ideas without stronger catalyst evidence.

### FX / external balance

The broad dollar index was 119.28 on 2026-05-15, down around 3.0% over trailing 252 trading observations but firmer over the past quarter. USDJPY was high at 158.69, raising intervention/crowding concerns.

### Commodities

Commodity impulse is the most striking feature. WTI was 112.25 on 2026-05-18 and up roughly 72.6% over trailing 252 trading observations. Brent was 116.73. Copper was up about 28.7% year over year as of 2026-03 and the broad commodity index was up about 30.5% year over year.

### Positioning

Raw CFTC financial futures data exists in `~/.cache/macroresearch/positioning/FinFutYY.txt`, but it has not yet been parsed. This limits confidence in any `accept` rating.

### Volatility / risk appetite

VIX was 16.59 on 2026-05-25 and down over the past quarter. S&P 500 and NASDAQ were strong, with SPX up around 27.9% over trailing 252 trading observations and NASDAQ up around 39.6%. Risk appetite appears strong despite higher oil and real yields.

## Candidate hypotheses

### 1. US 5-year breakevens on underpriced energy-led inflation persistence

- Asset class: rates / inflation.
- Direction: Long 5y breakevens.
- Theory anchor: inflation impulse / real-rate repricing.
- Causal chain: oil and commodities rise -> headline inflation and expectations persist -> inflation compensation reprices higher -> breakevens outperform nominal duration.
- Required evidence: CPI/PCE momentum, breakevens, real yields, energy prices, inflation expectations, positioning.
- Potential expression: Long 5y TIPS versus duration-matched nominal Treasuries; ETF proxy would require hedging.
- Smart-money neglect: obvious long-commodity trade looks extended; breakevens are less salient and harder to express cleanly.
- Decision: Developed as watchlist idea.

### 2. Long broad commodities after oil shock

- Asset class: commodities.
- Direction: Long commodities / oil.
- Theory anchor: inflation impulse / supply-demand.
- Kill test: This risks chasing an already large move without curve/inventory/carry evidence.
- Decision: Reject for now; prefer breakevens as cleaner second-order expression.

### 3. Short high-yield credit on higher rates and oil inflation

- Asset class: credit.
- Direction: Short HY credit.
- Theory anchor: liquidity / credit cycle.
- Kill test: Spreads are tight and compressing; financial conditions are easy; short-credit carry is costly.
- Decision: Reject for now.

### 4. USDJPY upside from real-rate divergence

- Asset class: FX / rates.
- Direction: Long USDJPY.
- Theory anchor: real-rate differential / policy divergence.
- Kill test: USDJPY is already high; intervention and crowding risk likely material; positioning not parsed.
- Decision: Watchlist but not developed.

### 5. US curve steepener on fiscal/term-premium risk

- Asset class: rates.
- Direction: 5s30s or 2s10s steepener.
- Theory anchor: fiscal impulse / term premium / policy reaction function.
- Kill test: Requires issuance/refunding/auction and positioning data not yet ingested.
- Decision: Watchlist but not developed.

## Accepted ideas

None.

## Watchlist ideas

- `US5Y-breakevens-energy-inflation-001` — Long US 5-year breakevens on underpriced energy-led inflation persistence.

## Rejected ideas

See `rejected_ideas.md`.

Rejected in cycle 1:

- Long broad commodities after the oil shock.
- Short high-yield credit on higher rates and oil inflation.

## Open questions

- Parse raw CFTC data into positioning indicators for Treasury, equity index, FX, and commodity futures.
- Add a stable market-price ingestion source not blocked by Yahoo 429.
- Ingest Treasury issuance/refunding/auction data.
- Ingest commodity futures curve and inventory data, especially oil.
- Add official event calendar data for CPI/PCE/FOMC/Treasury auctions.

## Sources checked

- `README.md`
- `macro_framework.md`
- `universe.md`
- `risk_framework.md`
- `prior_ideas.tsv`
- `data_catalog.md`
- `~/.cache/macroresearch/metadata/ingestion_manifest.json`
- FRED data files under `~/.cache/macroresearch/`
- CFTC financial futures raw file at `~/.cache/macroresearch/positioning/FinFutYY.txt`

## Continued research loop — 10 iterations completed

Date: 2026-05-26

### Additional data work

Parsed enough of the raw CFTC financial futures file to identify 2026 positioning percentiles for major FX, equity-index, rates, and SOFR/Fed Funds contracts. Key observations:

- Yen asset-manager net positioning was at the 5th percentile of 2026 observations; leveraged-money yen net was at the 30th percentile.
- NASDAQ mini asset-manager net positioning was at the 100th percentile; Russell E-mini leveraged-money net positioning was at the 5th percentile.
- 2y and 5y Treasury leveraged-money net shorts were at the 100th percentile of the 2026 sample; 10y leveraged-money net was at the 80th percentile.
- SOFR-3M leveraged-money net positioning was at the 5th percentile and had become more bearish over four weeks.

### Iteration outcomes

1. `IWM-vs-QQQ-neglected-breadth-reversal-001` — watchlist. Small-cap/equal-weight catch-up versus crowded mega-cap leadership.
2. `CADJPY-oil-yen-funding-001` — watchlist. Oil terms-of-trade support versus yen funding weakness.
3. `US2s10s-flattener-sticky-inflation-001` — watchlist. Sticky inflation front-end repricing versus long-end cap.
4. `Gold-inflation-hedge-001` — reject. Real yields are too strong an offset; breakevens are cleaner.
5. `Short-Nasdaq-outright-001` — reject. Outright short is too blunt; relative-value expression is better.
6. `AUD-commodity-growth-001` — reject. Copper/global growth data stale and AUD positioning extended.
7. `Long-oil-after-shock-001` — reject. First-order move likely already obvious; curve/inventory data missing.
8. `HY-credit-carry-001` — reject. Tight spreads offer poor margin of safety.
9. `Broad-USD-policy-divergence-001` — reject. Too many conflicting channels; cleaner expressions exist.
10. `Long-vol-complacency-001` — reject. Low VIX alone is not a catalyst and vol products require term-structure/skew data.

### Updated watchlist ideas

- `US5Y-breakevens-energy-inflation-001`
- `IWM-vs-QQQ-neglected-breadth-reversal-001`
- `CADJPY-oil-yen-funding-001`
- `US2s10s-flattener-sticky-inflation-001`

### Updated rejected count

New rejects in the 10-iteration continuation: 7.

Total rejects logged in this run: 9, below the hard stop threshold of 10 rejected ideas. No ideas were marked `accept`, so the 3-accepted-ideas stop was not reached.

## Retail quant suitability pass — 2026-05-27

User constraint: implementable through IB Gateway with a small account (~$5k), favoring liquid ETFs, simple rules, no futures/options/leveraged products, and low operational complexity.

Additional market-price check:

- Yahoo Finance chart data accessed 2026-05-27 for `IWM`, `QQQ`, `RSP`, `SPY`, `TIP`, `IEF`, `SCHP`, and factor/sector ETFs through 2026-05-26.
- `RSP/QQQ` ratio was at a 252-trading-day z-score of -2.63, down 15.5% over 1 year and 21.3% over 2 years, and only 0.5% above its 2024-present trough.
- `IWM/QQQ` was less stretched at a 252-trading-day z-score of -0.66 and carries more real-yield/refinancing risk.
- `TIP/IEF` and `SCHP/IEF` are theoretically cleaner inflation-compensation proxies but already near high z-scores and likely too low-vol/hedge-complex for a $5k retail account.

Expression comparison:

1. `RSP/QQQ`: best balance of dislocation, liquidity, simplicity, and thesis purity for retail IB execution.
2. `IWM/QQQ`: more convex small-cap catch-up candidate but worse real-yield and refinancing sensitivity.
3. `CADJPY`: macro logic plausible but leverage/intervention/carry complexity is not ideal for a small account.
4. Breakeven/curve expressions: theoretically clean but harder to express without futures or imperfect ETF hedges.

Accepted idea:

- `RSP-vs-QQQ-retail-breadth-001` — accepted as best current retail-implementable research candidate, not personalized investment advice. Scores: Logic 4, Theory 4, Data 4, Asymmetry 4, Implementation 4, total 20/25.

### Repeated themes / risk of thesis duplication

The loop is beginning to cluster around one macro state: resilient nominal growth + commodity/inflation impulse + easy credit + high real yields + crowded mega-cap/yen/rates positioning. The next iteration should either add missing data to test these themes more rigorously or deliberately branch into non-US/non-energy hypotheses.

### Data gaps now most important

1. Treasury issuance/refunding and auction data for curve trades.
2. Commodity futures curve and inventory data for oil/energy trades.
3. Stable ETF/market price ingestion not blocked by Yahoo 429.
4. Official event calendar for CPI/PCE/FOMC/BoJ/BoC/Treasury auctions.
5. Clean parsed CFTC positioning time series beyond the current quick percentile scan.

## Retail quant tail-risk pass — 2026-05-27

Updated user constraint: retail quant strategy for approximately $80k, ranked primarily by risk/reward and avoidance of tail risk.

### Additional market-price check

- Yahoo Finance adjusted-close data accessed 2026-05-27 for `SPY`, `QQQ`, `RSP`, `IWM`, `USMV`, `QUAL`, `MTUM`, `VLUE`, `IEF`, `TLT`, `SHY`, `SGOV`, `GLD`, `DBC`, major sector ETFs, `HYG`, and `LQD`.
- Simple screen period: 2016-01-01 through 2026-05-26, monthly rebalance, no leverage in preferred strategy, no options/futures/volatility ETPs.
- Data caveat: this is a quick research backtest, not a production-grade engine. It does not yet include taxes, commissions, detailed slippage, ETF tracking error, or survivorship checks beyond using currently listed liquid ETFs.

### Strategy screen summary

Tail-risk-adjusted ranking favored a long-only, multi-asset trend/momentum rule over the previously accepted `RSP/QQQ` relative-value pair.

Key results from the quick screen:

| Strategy | CAGR | Vol | Sharpe | Max DD | Calmar | 1% daily CVaR | Worst day | Worst month |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Multi-asset top-2 trend/momentum + 8% vol cap | 8.15% | 7.75% | 1.05 | -11.37% | 0.72 | -2.05% | -3.19% | -6.01% |
| Multi-asset top-2 trend/momentum + 10% vol cap | 9.31% | 9.07% | 1.03 | -13.04% | 0.71 | -2.37% | -3.98% | -6.01% |
| USMV 200d trend + 8% vol cap | 7.01% | 7.84% | 0.91 | -11.84% | 0.59 | -2.17% | -4.52% | -5.84% |
| SPY 200d trend + 10% vol cap | 7.37% | 9.42% | 0.80 | -15.50% | 0.48 | -2.62% | -4.49% | -7.94% |
| 60/40 SPY/IEF monthly | 9.89% | 10.69% | 0.94 | -21.02% | 0.47 | -2.81% | -5.72% | -7.42% |
| Permanent portfolio SPY/TLT/GLD/SHY | 8.22% | 7.57% | 1.08 | -18.55% | 0.44 | -1.72% | -3.24% | -5.38% |
| SPY buy-and-hold | 15.21% | 17.86% | 0.88 | -33.72% | 0.45 | -4.76% | -10.94% | -12.49% |
| RSP/QQQ dollar-neutral pair with SHY collateral | -2.66% | 6.91% | -0.36 | -28.85% | -0.09 | -1.41% | -2.17% | -5.98% |

### New accepted candidate

- `retail-tail-risk-momentum-001` — accepted as the better current retail-quant candidate for an ~$80k account when the explicit objective is tail-risk avoidance rather than maximum upside. Scores: Logic 4, Theory 4, Data 4, Asymmetry 4, Implementation 5, total 21/25.

Rule summary:

1. Monthly rebalance.
2. Candidate assets: `SPY`, `USMV`, `GLD`, `DBC`.
3. Eligible only if price is above 200-day moving average and 6-month momentum is positive.
4. Hold the top two eligible assets by 6-month momentum.
5. Volatility-cap each sleeve using 63-day realized volatility; 8% target-vol version selected for lower tail risk.
6. Allocate unused capital to `SHY`.

Current rule-implied allocation from the 8% target-vol variant: approximately `SPY` 28%, `DBC` 16%, `SHY` 56%.

### Status changes

- `RSP-vs-QQQ-retail-breadth-001` moved from `accept` to `watchlist` for the explicit $80k/tail-risk objective. It remains an interesting tactical dislocation, but the short leg, margin/financing, crowded-mega-cap squeeze risk, and poor historical tail-adjusted screen make it inferior to the long-only multi-asset strategy for this use case.

### Open follow-ups

- Reproducible quick screen added at `scripts/retail_quant_screen.py`; next improvement is adding transaction costs, slippage assumptions, and parameter-sensitivity tests.
- Add clean ETF price ingestion so the rule can be monitored without ad hoc Yahoo pulls.
- Replace or complement `DBC` with a better commodity exposure only if the approved universe and roll/carry data support it.

## Parameter robustness pass — 2026-05-27

Extended `scripts/retail_quant_screen.py` with `--robustness` mode and wrote full grid output to `robustness_grid.csv`.

Grid dimensions:

- Trend filter: 100, 150, 200, 250 trading days.
- Momentum lookback: 63, 126, 189, 252 trading days.
- Volatility lookback: 21, 63, 126 trading days.
- Target volatility: 6%, 8%, 10%, 12%.
- Number of selected assets: top 1, top 2, top 3.
- Max sleeve cap: 33%, 50%, 67%, 100%.
- Ballast: `SHY`.
- Universe: `SPY`, `USMV`, `GLD`, `DBC`.

Total tested rows: 2,112.

### Key robustness results

- 1,443 / 2,112 parameter sets had CAGR >= 6% and max drawdown no worse than -15%.
- Qualifying median results: CAGR 8.45%, vol 7.46%, Sharpe 1.16, max drawdown -11.26%, Calmar 0.76.
- Target-vol robustness: 6% and 8% targets had the highest qualification rates, but 10-12% targets can work if sleeve caps are tight.
- Sleeve-cap robustness: 33% cap was strongest for tail control; 375 / 384 rows qualified. Higher sleeve caps increased returns but worsened drawdown qualification rates.
- Top-N robustness: top 2 and top 3 were materially better than top 1. Top 2 is preferred for simplicity and lower concentration.
- Momentum robustness: 126-189 trading days were better than very short or very long extremes. 189-day momentum had the highest median CAGR/Calmar but a lower qualification rate than 63/126 because it can take more concentration risk.
- Trend robustness: 100-150 day filters ranked better than the original 200-day filter in this sample; 200-day remains acceptable but no longer looks like the best default.

### Top grid rows

The top in-sample row was:

- Trend 100d, momentum 189d, vol lookback 126d, target vol 12%, top 2, 33% sleeve cap.
- CAGR 11.07%, vol 6.93%, Sharpe 1.55, max drawdown -7.34%, Calmar 1.51, 1% daily CVaR -1.74%.
- Current allocation: `SPY` 33%, `DBC` 27.3%, `SHY` 39.7%.

Do not automatically adopt the top row; it may overfit. Prefer a central robust region.

### Preferred robust default for further testing

Selected default after robustness pass:

- Trend: 150 trading days.
- Momentum: 189 trading days.
- Volatility lookback: 126 trading days.
- Target vol: 10%.
- Selected assets: top 2.
- Sleeve cap: 33%.

Full-sample quick-screen result:

- CAGR 10.33%, vol 6.88%, Sharpe 1.47, max drawdown -9.02%, Calmar 1.15, 1% daily CVaR -1.74%.
- Current allocation: `SPY` 33%, `DBC` 22.8%, `SHY` 44.2%.

Subperiod checks:

| Strategy | Period | CAGR | Vol | Sharpe | Max DD | Calmar | 1% daily CVaR | Worst month |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Robust default | 2016-2019 | 7.85% | 5.88% | 1.31 | -6.35% | 1.24 | -1.46% | -3.92% |
| Robust default | 2020-2022 | 9.66% | 7.69% | 1.23 | -7.52% | 1.28 | -1.94% | -2.88% |
| Robust default | 2023-now | 13.99% | 7.18% | 1.87 | -5.70% | 2.45 | -1.73% | -3.03% |

### Updated conclusion

The broad conclusion is strengthened: for an $80k tail-risk-aware retail quant, the best current direction remains a long-only ETF trend/momentum strategy with `SHY` ballast. The exact initial 200d/126d/8% setting is not the best robust default. The preferred region is:

```text
trend filter: 100-150 trading days
momentum: 126-189 trading days
selected assets: top 2
max sleeve: ~33%
target vol: 8-10%, with 10% acceptable because the 33% sleeve cap controls exposure
ballast: SHY
```

Next robustness work should test transaction costs/slippage, tax-aware turnover, longer historical ETF/proxy data before 2016, and alternatives to `DBC` that reduce commodity roll risk.

## Transaction-cost and universe sanity pass — 2026-05-27

Additional verification run used Yahoo Finance adjusted-close data through 2026-05-26 and the selected robust default: trend 150d, momentum 189d, vol lookback 126d, 10% target vol, top 2, 33% sleeve cap, `SHY` ballast.

### Turnover and cost sensitivity

The rule has meaningful but manageable monthly turnover: about 333% annual one-way notional turnover in the quick screen. Cost sensitivity remains acceptable for liquid ETFs:

| One-way cost assumption | CAGR | Vol | Sharpe | Max DD | Calmar | Current allocation |
|---:|---:|---:|---:|---:|---:|---|
| 0 bps | 10.33% | 6.88% | 1.47 | -9.02% | 1.15 | `SPY` 33.0%, `DBC` 22.8%, `SHY` 44.2% |
| 2 bps | 10.26% | 6.88% | 1.47 | -9.19% | 1.12 | same |
| 5 bps | 10.15% | 6.88% | 1.47 | -9.46% | 1.07 | same |
| 10 bps | 9.97% | 6.88% | 1.47 | -9.90% | 1.01 | same |
| 25 bps | 9.42% | 6.88% | 1.47 | -11.20% | 0.84 | same |

Interpretation: because the instruments are large liquid ETFs and the account size is only ~$80k, the strategy is not killed by reasonable spread/slippage assumptions. Taxes are still not modeled and remain an important real-world caveat.

### Alternative universe check

The core universe remains preferable to larger or more equity-heavy universes under the same robust default and 5 bps one-way cost assumption:

| Universe | CAGR | Vol | Sharpe | Max DD | Calmar | Comment |
|---|---:|---:|---:|---:|---:|---|
| `SPY`, `USMV`, `GLD`, `DBC` | 10.15% | 6.88% | 1.47 | -9.46% | 1.07 | Best balance of return, drawdown, simplicity, and macro diversification. |
| `SPY`, `USMV`, `GLD` | 8.09% | 6.53% | 1.25 | -12.23% | 0.66 | Removing `DBC` reduces commodity roll concern but worsens return and drawdown. |
| `SPY`, `USMV`, `QUAL`, `MTUM`, `GLD`, `DBC` | 9.80% | 7.65% | 1.29 | -9.00% | 1.09 | Similar Calmar but higher turnover and more factor complexity. |
| Broad equity styles + real assets | 7.93% | 8.59% | 0.96 | -10.87% | 0.73 | More moving parts and poorer reward-to-risk. |
| Sector ETFs + real assets | 6.35% | 8.68% | 0.78 | -15.10% | 0.42 | Too noisy/complex for this objective. |

### Updated conclusion

This pass strengthens rather than replaces `retail-tail-risk-momentum-001`. The best current idea remains the simple long-only core ETF trend/momentum rule, not an expanded sector/factor optimizer and not a discretionary macro pair. Main unresolved caveats: taxes, pre-2016 proxy history, `DBC` roll/carry mechanics, and production-grade data validation.
