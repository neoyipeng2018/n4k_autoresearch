# Tradable Universe

This document defines the preferred universe for macro research. The goal is to keep ideas liquid, understandable, monitorable, and implementable for a retail quant with approximately $80k in an IB account, without relying on obscure instruments.

This is not a recommendation to trade any instrument. It is a research universe for idea generation.

## General principles

Prefer instruments that are:

- Liquid.
- Transparent.
- Easy to monitor with available data.
- Closely linked to the macro thesis.
- Reasonable for directional or relative-value expression.
- Not dependent on hidden leverage or inaccessible financing.
- Suitable for ~$80k retail IB implementation after commissions, spreads, borrow, margin, and tax/turnover frictions.
- Capacity-insensitive at small size and not dominated by crowded smart-money positioning.

Prefer relative-value trades when they isolate the thesis better than outright risk-on/risk-off direction, but do not accept a relative-value trade merely because it is elegant. If a long-only ETF, cash-ballast, or systematic trend expression has better drawdown-adjusted reward-to-risk for the retail account, prefer the simpler expression.

Avoid instruments where the macro signal is likely dominated by idiosyncratic company, regulatory, political, or liquidity risk.

For the default $80k retail objective, avoid or heavily penalize strategies requiring complex options, futures margin, leveraged/inverse ETPs, volatility ETPs, hard-to-borrow shorts, or unbounded loss. These may be discussed conceptually but require explicit human review before acceptance.

## Asset classes

### Rates

Allowed research expressions:

- US Treasury ETFs: `SHY`, `IEI`, `IEF`, `TLT`, `BIL`, `SGOV`.
- Treasury futures as conceptual expressions: 2y, 5y, 10y, Ultra 10y, bond futures.
- SOFR / Fed funds futures as conceptual expressions for policy path.
- Yield curve trades: 2s10s, 5s30s, 2s5s, 10s30s.
- Inflation-linked bonds / TIPS ETFs: `TIP`, `SCHP`, `VTIP`.

Preferred use:

- Monetary policy repricing.
- Term-premium / fiscal supply thesis.
- Real-rate and inflation repricing.
- Growth slowdown or acceleration expressed through policy path.

Constraints:

- For curve trades, describe duration neutrality conceptually.
- For futures, discuss roll and margin qualitatively.
- Options or swaptions require explicit complexity warning and human review before acceptance.

### FX

Allowed research expressions:

- Major FX: `EURUSD`, `USDJPY`, `GBPUSD`, `USDCHF`, `USDCAD`, `AUDUSD`, `NZDUSD`.
- Liquid crosses: `EURJPY`, `EURGBP`, `AUDJPY`, `CADJPY`, `AUDNZD`.
- Dollar index ETF/futures conceptual: `DXY`, `UUP`.
- Currency ETFs if needed: `FXE`, `FXY`, `FXB`, `FXA`, `FXC`, `FXF`.

Preferred use:

- Policy divergence.
- Real-rate differentials.
- Balance-of-payments pressure.
- Terms-of-trade shocks.
- Funding-currency dynamics.

Constraints:

- Always discuss carry.
- Always discuss intervention risk where relevant, especially JPY and CNH proxies.
- EM FX is out of scope unless explicitly approved.

### Equity indices and factors

Allowed research expressions:

- Broad ETFs: `SPY`, `QQQ`, `IWM`, `DIA`, `ACWI`, `EFA`, `EEM`.
- Regional ETFs: `FEZ`, `EWJ`, `EWU`, `EWG`, `EWU`, `EWZ`, `INDA`, `FXI`, `KWEB`.
- Sector ETFs: `XLF`, `XLK`, `XLE`, `XLI`, `XLP`, `XLU`, `XLV`, `XLY`, `XLB`, `XLRE`.
- Factor ETFs: `QUAL`, `MTUM`, `USMV`, `VLUE`, `IWD`, `IWF`, `IWM`, `RSP`.
- Relative-value pairs: cyclicals versus defensives, value versus growth, equal-weight versus cap-weight.

Preferred use:

- Growth cycle.
- Liquidity / financial conditions.
- Earnings sensitivity to macro shocks.
- Fiscal impulse sector effects.

Constraints:

- Do not accept a broad equity index idea unless macro transmission dominates idiosyncratic/earnings/AI/liquidity noise.
- Prefer factor/sector/relative-value expressions when cleaner.

### Commodities

Allowed research expressions:

- Broad commodity ETF: `DBC`.
- Energy: WTI / Brent futures conceptually, `USO`, `BNO`, `XLE` as equity proxy only with caveats.
- Natural gas: futures conceptually, `UNG` only with strong roll-risk warning.
- Gold: futures conceptually, `GLD`, `IAU`.
- Silver: `SLV`.
- Copper: futures conceptually, `CPER`, miners only as noisy proxies.
- Agriculture broad expressions only with human review.

Preferred use:

- Inflation impulse.
- Real-rate repricing.
- Supply disruptions.
- Inventory cycle.
- China/global demand impulse.
- Terms-of-trade FX links.

Constraints:

- Always discuss curve structure, carry, and roll risk.
- Commodity ETFs can be poor long-horizon expressions because of roll decay.
- Producer equities are not pure commodity exposure.

### Credit

Allowed research expressions:

- Investment grade: `LQD`, `VCIT`.
- High yield: `HYG`, `JNK`.
- Senior loans: `BKLN`.
- Credit spread concepts: CDX IG/HY conceptually if data is available.

Preferred use:

- Credit cycle.
- Liquidity tightening/easing.
- Default risk repricing.
- Risk appetite.

Constraints:

- Credit ETFs include rate exposure; isolate spread versus duration where possible.
- Short credit via ETFs has borrow/path issues; discuss implementation friction.
- Do not accept credit ideas without spread, default, and liquidity evidence.

### Volatility

Allowed research expressions:

- VIX futures / options conceptually.
- `VIXY`, `VXX`, `UVXY` only as tactical instruments with strong roll-decay warnings.
- Options overlays conceptually.

Preferred use:

- Event risk.
- Volatility risk premium dislocations.
- Cross-asset hedges.

Constraints:

- Volatility products are complex and path-dependent.
- Any idea requiring options, leverage, or volatility ETPs should be `watchlist` pending human review unless explicitly approved.

### Crypto

Default status: out of scope for accepted macro ideas unless the user explicitly approves.

Crypto may appear in regime analysis as a liquidity/risk appetite indicator, but should not be the default trade expression.

## Instruments to avoid by default

- Single-name equities.
- Illiquid ETFs or local-market instruments without data.
- Leveraged ETFs except as conceptual short-horizon examples requiring review.
- Inverse ETFs except as conceptual short-horizon examples requiring review.
- Unlisted derivatives.
- Complex options structures without explicit human approval.
- Private credit, private funds, structured notes.
- Highly illiquid EM local assets.

## Required expression comparison

For each developed idea, compare at least two expressions. Example:

- Macro thesis: US growth slowdown with front-end easing repricing.
- Possible expressions:
  - Long 2y duration.
  - 2s10s steepener.
  - Long TLT.
  - Long defensives versus cyclicals.
- Preferred expression should isolate the thesis and avoid unnecessary equity/term-premium noise.

## Smart-money-neglect lens by asset class

Rates:

- Neglect may arise from consensus focus on the level of cuts rather than curve shape.
- Balance-sheet and issuance plumbing can be ignored by macro narratives.

FX:

- Carry and intervention risk can deter ownership even when directional macro logic is sound.
- Crosses can be overlooked when the market focuses on USD pairs.

Equities:

- Benchmark constraints can force crowding in index exposures while sector/factor dispersion is neglected.
- Macro funds may avoid equity-relative trades seen as micro/factor rather than macro.

Commodities:

- Inventory and curve mechanics can be ignored by cross-asset investors.
- ETF roll costs can make the obvious expression poor while another expression is better.

Credit:

- Spread products may react before rating/default data, but ETF duration exposure can obscure the signal.
- Smart money may avoid crowded short-credit trades if carry is expensive.

Volatility:

- Volatility carry and path dependence can hide convexity opportunities, but complexity requires caution.
