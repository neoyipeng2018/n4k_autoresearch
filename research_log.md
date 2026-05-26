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
