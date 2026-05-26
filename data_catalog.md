# Data Catalog

This document describes expected local data for macroresearch runs.

Local data root:

```text
~/.cache/macroresearch/
```

Use local data first. If local data is missing or stale, public web sources may be used as a supplement, but the source and access date must be logged in `research_log.md`.

## Expected directory layout

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

Preferred file formats are CSV, Parquet, JSON, or SQLite. Each dataset should include observation dates and source metadata when possible.

## Required data categories

### Rates and yield curves

Expected contents:

- US Treasury yields: 3m, 2y, 5y, 10y, 30y.
- Yield curve spreads: 2s10s, 5s30s, 3m10y.
- Real yields if available.
- Breakevens if available.
- Policy-implied rates / futures if available.

Suggested public sources:

- FRED Treasury yield series.
- Treasury.gov yield curve data.
- CME / exchange data for futures pricing where accessible.

Possible local files:

- `rates/us_treasury_yields.csv`
- `rates/us_curve_spreads.csv`
- `rates/us_real_yields.csv`
- `rates/us_breakevens.csv`
- `rates/policy_implied_rates.csv`

### Inflation data

Expected contents:

- CPI headline and core.
- PCE headline and core.
- Wage indicators.
- Inflation expectations.
- Breakevens.
- Commodity inflation proxies.

Suggested public sources:

- FRED.
- BLS.
- BEA.
- University of Michigan inflation expectations.

Possible local files:

- `inflation/us_cpi.csv`
- `inflation/us_pce.csv`
- `inflation/us_wages.csv`
- `inflation/inflation_expectations.csv`

### Growth data

Expected contents:

- GDP / nowcast proxies.
- PMIs / ISM.
- Retail sales.
- Industrial production.
- Payrolls / unemployment / claims.
- Housing.
- Credit growth.
- Trade / freight if available.

Suggested public sources:

- FRED.
- Census.
- BLS.
- BEA.
- ISM / S&P Global where licensed.

Possible local files:

- `growth/us_activity.csv`
- `growth/us_labor.csv`
- `growth/us_housing.csv`
- `growth/global_pmi.csv`

### Central bank policy data

Expected contents:

- Policy rates.
- Meeting dates.
- Statements / minutes metadata if available.
- Market-implied policy paths.
- Central-bank balance sheets.

Suggested public sources:

- FRED.
- Federal Reserve.
- ECB / BoE / BoJ official sources.
- CME FedWatch if accessible.

Possible local files:

- `policy/policy_rates.csv`
- `policy/central_bank_balance_sheets.csv`
- `policy/meeting_calendar.csv`
- `policy/implied_policy_path.csv`

### FX data

Expected contents:

- Major FX spot rates.
- Dollar index.
- Real effective exchange rates if available.
- FX reserves for relevant countries.
- Carry / short-rate differentials.

Suggested public sources:

- FRED.
- BIS REER.
- IMF IFS if available.
- Yahoo Finance / Stooq for spot proxies.

Possible local files:

- `fx/major_fx.csv`
- `fx/dxy.csv`
- `fx/reer.csv`
- `fx/fx_reserves.csv`
- `fx/fx_carry.csv`

### Equity index data

Expected contents:

- Major equity indices and ETFs.
- Regional indices.
- Sector ETFs.
- Factor ETFs.
- Valuation metrics if available.
- Earnings revisions if available.

Suggested public sources:

- Yahoo Finance / Stooq.
- FRED for some index series.
- ETF provider data.

Possible local files:

- `equities/index_prices.csv`
- `equities/sector_etfs.csv`
- `equities/factor_etfs.csv`
- `equities/valuations.csv`

### Commodity data

Expected contents:

- Gold, silver, copper, WTI, Brent, natural gas.
- Broad commodity indices.
- Futures curve structure if available.
- Inventories where relevant.

Suggested public sources:

- FRED.
- EIA for energy.
- LME / CME where accessible.
- Yahoo Finance / Stooq for price proxies.

Possible local files:

- `commodities/spot_and_futures.csv`
- `commodities/energy.csv`
- `commodities/metals.csv`
- `commodities/inventories.csv`
- `commodities/curve_structure.csv`

### Credit spreads

Expected contents:

- Investment-grade spreads.
- High-yield spreads.
- Financial conditions indices.
- Credit ETFs and duration proxies.
- Lending standards.

Suggested public sources:

- FRED ICE BofA indices.
- Federal Reserve Senior Loan Officer Opinion Survey.
- ETF market data.

Possible local files:

- `credit/ig_hy_spreads.csv`
- `credit/credit_etfs.csv`
- `credit/lending_standards.csv`
- `credit/financial_conditions.csv`

### Positioning / sentiment

Optional but highly valuable.

Expected contents:

- CFTC Commitment of Traders.
- Fund manager survey summaries if licensed.
- ETF flows.
- Options skew / put-call ratios.
- CTA trend estimates if available.

Suggested public sources:

- CFTC COT.
- ETF issuer flow data.
- Options data where accessible.

Possible local files:

- `positioning/cftc_cot.csv`
- `positioning/etf_flows.csv`
- `positioning/options_sentiment.csv`

### Event calendar

Optional but useful.

Expected contents:

- Central bank meetings.
- Major data releases.
- Treasury refunding / auctions.
- Elections / fiscal events.

Suggested public sources:

- Central bank calendars.
- Treasury auction calendar.
- Public economic calendars where accessible.

Possible local files:

- `calendar/economic_calendar.csv`
- `calendar/central_bank_meetings.csv`
- `calendar/treasury_auctions.csv`

## Ingestion scripts

Current script:

```text
scripts/ingest_public_macro.py
```

Current responsibilities:

- Ingests public FRED fredgraph CSV data with no API key for rates, real yields, breakevens, inflation, wages, growth, labor, policy, Fed balance sheet, FX, equity indices, commodities, credit spreads, and financial conditions.
- Attempts ETF proxy prices from Yahoo Finance chart endpoints, but this can be rate-limited with HTTP 429.
- Writes a local event-calendar stub until a stable official calendar source is added.
- Writes metadata manifests under `~/.cache/macroresearch/metadata/`.

Additional suggested future scripts:

```text
scripts/ingest_market_prices.py
scripts/ingest_cftc_cot.py
scripts/ingest_eia_energy.py
scripts/ingest_event_calendar.py
scripts/ingest_treasury_issuance.py
```

Suggested responsibilities:

- `ingest_market_prices.py`: ETF/index/FX/commodity proxy prices from a stable configured source not blocked by Yahoo rate limits.
- `ingest_cftc_cot.py`: CFTC futures positioning parsed into clean instrument-level metrics.
- `ingest_eia_energy.py`: EIA energy inventories and oil/gas data.
- `ingest_event_calendar.py`: central-bank meetings, macro release calendar, Treasury auctions.
- `ingest_treasury_issuance.py`: Treasury refunding, auction sizes, auction tails, and issuance mix.

## Freshness standards

- Market prices: latest available close, preferably within 1 business day.
- Rates and FX: latest available close, preferably within 1 business day.
- Inflation and growth macro data: latest official release.
- COT positioning: latest weekly release.
- Event calendar: upcoming 1-3 months.
- Fiscal / issuance: latest official update.

If freshness fails, mark affected ideas `watchlist` or `needs_data` unless the thesis is explicitly structural and stale data is not decisive.

## Data verification checklist

Before research begins, verify that `~/.cache/macroresearch/` exists and that at least one usable file exists for:

- Rates and yield curves.
- Inflation data.
- Growth data.
- Central bank policy data.
- FX data.
- Equity index data.
- Commodity data.
- Credit spreads.
- Positioning / sentiment if available.
- Event calendar if available.

If a required category is missing, report:

1. Missing category.
2. Expected path.
3. Suggested ingestion script.
4. Whether web supplementation is acceptable for the current run.

## Web supplementation policy

When supplementing with web/public sources:

- Record source URL or source name.
- Record access date.
- Prefer official sources over media summaries.
- Do not rely on headlines alone.
- If data cannot be independently checked, reduce data score.
