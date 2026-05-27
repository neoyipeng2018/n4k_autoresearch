# Idea: Retail tail-risk-aware ETF momentum with cash ballast

## One-line thesis
A rules-based, unlevered ETF allocation that owns at most the top two positive-trend assets from `SPY`, `USMV`, `GLD`, and `DBC`, caps each sleeve, and holds the residual in `SHY` offers a better retail risk/reward profile than equity-pair or outright directional ideas when the explicit objective is avoiding tail risk on an ~$80k account.

## Trade expression
- Instrument: Liquid ETFs only: `SPY`, `USMV`, `GLD`, `DBC`, and `SHY`.
- Direction: Systematic long-only rotation with cash/short-duration Treasury ballast.
- Time horizon: Strategic/tactical quant rule, reviewed monthly; expected holding horizon 1-12 months depending on signals.
- Preferred structure after robustness testing: Monthly rebalance. Select assets above a 100-150 day moving average with positive 6-9 month momentum; hold the top two by momentum; cap each active sleeve at roughly 33%; use volatility targeting as a secondary risk control; allocate unused capital to `SHY`.
- Robust default chosen for further testing: 150-day trend filter, 189-trading-day momentum, 126-day realized volatility, 10% target volatility, top 2 assets, 33% max sleeve.
- Current robust-default allocation from Yahoo Finance adjusted-close data through 2026-05-26: approximately `SPY` 33%, `DBC` 22.8%, `SHY` 44.2%.
- Alternative expressions:
  - `SPY` 200-day trend + 10% volatility cap, residual `SHY`: simpler, but lower cross-asset diversification.
  - Permanent portfolio (`SPY`/`TLT`/`GLD`/`SHY`): lower daily left-tail but less adaptive and more duration tail risk.
  - `RSP/QQQ` relative-value pair: current dislocation is interesting, but short-leg/margin/crowding risk is inferior for explicit tail-risk avoidance.
- Instruments to avoid: Leveraged ETFs, inverse ETFs, options, volatility ETPs, futures, single names, and unbounded short books.

## Theory anchor
Liquidity/credit/risk appetite; trend-following risk-premium; positioning/valuation/risk-premium; inflation/commodity impulse as one possible selected sleeve rather than a permanent narrative bet.

## Causal chain
1. Macro regimes change slowly enough that 6-month momentum and 200-day trend filters can avoid some large left-tail regimes without forecasting every catalyst.
2. A cross-asset sleeve set allows participation in equity, defensive equity, inflation/real-asset, and commodity regimes rather than forcing one macro narrative.
3. A volatility cap converts the signal from “own the winner at any risk” into a controlled-risk allocation.
4. Residual capital in `SHY` reduces crash exposure, financing complexity, and behavioral/operational stress for a retail account.
5. Monthly rebalancing keeps turnover manageable while still responding to regime deterioration.

## Why the market may be wrong
This is less a single mispriced macro trade than a retail implementation edge: many sophisticated investors already use trend/risk control, but retail accounts often overuse concentrated equity beta, leveraged products, options, or ad-hoc shorts. The opportunity is in avoiding bad implementation and large uncompensated tail risk, not in discovering an obscure asset.

## Supporting evidence
- Yahoo Finance adjusted-close ETF data accessed 2026-05-27, tested from 2016-01-01 through 2026-05-26.
- Initial 8% target-vol multi-asset top-two trend/momentum variant produced CAGR 8.15%, annualized volatility 7.75%, Sharpe 1.05, max drawdown -11.37%, Calmar 0.72, 1% daily CVaR -2.05%, worst day -3.19%, and worst month -6.01% in the first screen.
- A 2,112-row robustness grid over trend filters, momentum lookbacks, volatility lookbacks, target vol levels, top-N selection, and sleeve caps found 1,443 rows with CAGR >= 6% and max drawdown no worse than -15%.
- Qualifying-grid medians were CAGR 8.45%, vol 7.46%, Sharpe 1.16, max drawdown -11.26%, and Calmar 0.76.
- The more robust central default, rather than the top in-sample row, was 150-day trend / 189-day momentum / 126-day vol / 10% target vol / top 2 / 33% sleeve cap. It produced CAGR 10.33%, vol 6.88%, Sharpe 1.47, max drawdown -9.02%, Calmar 1.15, and 1% daily CVaR -1.74%.
- Subperiod checks for that robust default: 2016-2019 CAGR 7.85%, max drawdown -6.35%; 2020-2022 CAGR 9.66%, max drawdown -7.52%; 2023-now CAGR 13.99%, max drawdown -5.70%.
- By comparison, `SPY` buy-and-hold had higher CAGR 15.21% but much worse max drawdown -33.72%, 1% daily CVaR -4.76%, worst day -10.94%, and worst month -12.49%.
- `RSP/QQQ` dollar-neutral with `SHY` collateral looked unattractive historically in this simple screen: CAGR -2.66%, max drawdown -28.85%, despite low daily volatility; the tail problem is persistent relative underperformance rather than one-day VaR.

## Contradictory evidence
- Backtests over 2016-2026 may overfit the post-GFC/post-COVID ETF regime and may not capture earlier inflation, bond bear-market, or commodity-supercycle episodes.
- Trend filters can whipsaw and exit after part of the drawdown has already occurred.
- `DBC` has commodity futures roll/carry risk; a positive trend signal can still lose money if spot and roll dynamics diverge.
- `SHY` reduces risk but can drag returns in strong equity bull markets.
- A strategy can have low historical drawdown and still gap on event risk; the protection is probabilistic, not guaranteed.

## Catalyst path
The strategy does not require a discretionary catalyst. It works if realized cross-asset trends continue long enough to harvest momentum and if the volatility/cash ballast cuts exposure during high-volatility downtrends.

## Invalidation criteria
The thesis is wrong or needs redesign if:
- Live/forward max drawdown exceeds roughly 15% for the 8% target-vol rule without a clear data/execution error explanation.
- The strategy underperforms `SHY` over a full 12-month period while maintaining materially higher realized volatility.
- The selected ETFs become structurally unsuitable: poor liquidity, material tracking error, or commodity roll costs dominate `DBC` returns.
- Monthly rebalance signals become unstable because of bad data, stale prices, or corporate-action errors.
- Correlation across all risky sleeves rises persistently toward 1 during stress, reducing the value of cross-asset selection.

## Monitoring dashboard
Track:
- 100/150/200-day trend status for `SPY`, `USMV`, `GLD`, and `DBC`.
- 6-month and 9-month total return rankings for the same ETFs.
- 63-day and 126-day realized volatility per ETF and resulting target weights.
- Strategy drawdown versus its prior high-water mark.
- `SPY` trend and VIX as broad equity stress indicators.
- Real yields and breakevens for equity/gold regime context.
- Commodity curve/roll conditions for `DBC` if available.
- Execution slippage and bid/ask spreads at monthly rebalance.

## Risks
- Carry / roll / financing risk: No borrowing or short financing; `DBC` embeds commodity futures roll risk, and `SHY` carries low but nonzero rate sensitivity.
- Liquidity risk: ETFs are liquid enough for an ~$80k account; still use limit orders around rebalance.
- Policy risk: Abrupt policy shocks can gap equities, bonds, gold, or commodities before monthly signals react.
- Positioning risk: Momentum can crowd into the same winners owned by CTAs and risk-parity/vol-control flows.
- Correlation / cross-asset risk: In crisis, equities, commodities, and even gold can temporarily sell off together.
- Event risk: CPI/PCE, FOMC, payrolls, geopolitical commodity shocks.

## Expected payoff profile
- Base case: High single-digit annualized returns with substantially lower drawdown than full equity beta.
- Bull case: Low double-digit returns if trend persistence remains strong and commodity/equity sleeves alternate leadership.
- Bear case: Whipsaw losses and opportunity cost versus buy-and-hold in a straight-line equity rally; drawdown can still reach low/mid teens.
- Asymmetry: The attractive feature is not upside convexity; it is sacrificing some upside to reduce left-tail exposure, margin risk, and behavioral blow-up risk.

## Final judgment
Accepted as the better current retail-quant candidate for an ~$80k account when ranked by risk-adjusted return and tail-risk avoidance. This is research, not personalized investment advice.

Reason:
The explicit user criterion changed the ranking. `RSP/QQQ` remains an interesting tactical dislocation, but the $80k/tail-risk objective favors a long-only, capped, multi-asset trend rule that avoids shorts, leverage, options, futures margin, and single-theme dependence. The parameter-robustness pass strengthens this conclusion: performance is not confined to one exact parameter set, and the strongest region is top-two selection with moderate trend/momentum lookbacks and a hard sleeve cap.

## Scores
- Logic score: 4
- Theory score: 4
- Data score: 4
- Asymmetry score: 4
- Implementation score: 5
- Total: 21/25
