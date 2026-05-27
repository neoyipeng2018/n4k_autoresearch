# Macro Framework

This document defines the house framework for generating and testing macro trade ideas.

The objective is not to summarize the macro environment. The objective is to identify **the best reward-to-risk macro trading idea for a retail quant with approximately $80k in an IB account**, caused by a gap between economic reality, market pricing, implementation constraints, and smart-money attention or crowding.

## Core research question

For every hypothesis, answer:

```text
What macro mechanism is likely to drive asset prices, what is the market currently pricing, why might sophisticated investors still be underweight, inattentive, constrained, crowded, or using the wrong expression, and is there a retail-implementable IB expression with superior reward-to-risk for an ~$80k account?
```

## Retail quant objective filter

Every hypothesis must pass a retail-account filter before it can be accepted:

- Can it be implemented at IB with approximately $80k without excessive leverage, borrow, financing, slippage, or operational complexity?
- Does the expression use liquid, transparent instruments that can be monitored and exited under stress?
- Is the expected reward-to-risk better than simpler alternatives such as cash/short-duration Treasury ballast, broad ETFs, trend/momentum rules, or lower-complexity relative-value expressions?
- Does the idea avoid crowded smart-money battlegrounds, or does it exploit a reason smart money may ignore, under-own, or mis-express the thesis?
- Can the trade be explained in plain language from macro mechanism to asset-price implication to invalidation criteria?

A strategy that is theoretically elegant but impractical for an $80k retail IB account is not a strong candidate here.

## Regime snapshot template

Each research cycle should summarize:

1. **Growth**
   - PMIs / ISM
   - payrolls / unemployment / claims
   - retail sales / consumption
   - industrial production
   - housing
   - global trade / freight

2. **Inflation**
   - headline and core CPI/PCE
   - sequential inflation momentum
   - wages
   - shelter
   - energy / food impulse
   - inflation expectations and breakevens

3. **Policy**
   - central-bank reaction functions
   - market-implied policy path
   - real rates
   - central-bank communication
   - fiscal / political constraints on policy

4. **Liquidity**
   - central-bank balance sheets
   - reserves / money market plumbing
   - Treasury issuance and liquidity drain
   - dollar funding stress
   - money supply / credit creation

5. **Fiscal impulse**
   - deficit path
   - issuance mix
   - spending impulse
   - tax/regulatory changes
   - election / political calendar

6. **Credit**
   - investment-grade and high-yield spreads
   - bank lending standards
   - default expectations
   - funding conditions

7. **FX / external balance**
   - current account / capital flows
   - reserve adequacy
   - real-rate differentials
   - terms of trade
   - FX intervention risk

8. **Commodities**
   - inventory cycle
   - supply disruptions
   - demand impulse
   - curve structure / carry
   - commodity FX linkages

9. **Positioning / valuation**
   - futures positioning
   - fund surveys if available
   - options skew / vol premia
   - valuation versus history or fair-value anchors
   - consensus narrative

10. **Volatility / risk appetite**
   - equity vol
   - rates vol
   - FX vol
   - credit vol / spread moves
   - cross-asset correlations

## Theory anchors

Every idea must name at least one anchor.

### Monetary policy reaction function

Market mispricing can arise when investors misunderstand how a central bank responds to inflation, growth, employment, financial conditions, currency pressure, or fiscal dominance.

Typical expressions:

- Rates futures
- Front-end duration
- Yield curve steepeners / flatteners
- FX against funding currencies
- Gold / real-rate-sensitive assets

### Growth cycle and demand impulse

Markets may underprice acceleration or deceleration in real activity, especially when soft and hard data diverge or when global linkages matter.

Typical expressions:

- Cyclicals versus defensives
- Equity index relative value
- Commodities
- Credit spreads
- Growth-sensitive FX
- Curve shape

### Inflation impulse and real-rate repricing

Inflation surprises can be expressed through nominal duration, breakevens, real rates, commodities, FX, and equity factors.

Pay attention to sequential inflation, not only year-over-year base effects.

### Balance of payments and external funding

Currencies and local assets can misprice current-account adjustment, portfolio flows, FX reserve dynamics, real yield differentials, external debt, or terms-of-trade shocks.

### Liquidity / credit / risk appetite

Risk premia can move when liquidity conditions change before growth or earnings data confirm the shift.

Distinguish real liquidity from loose proxies. A liquidity narrative without measurable transmission should be rejected.

### Fiscal impulse and political economy

Fiscal stance affects growth, inflation, rates, curve shape, FX, and sector dispersion. Pay special attention to fiscal dominance and issuance effects.

### Positioning / valuation / risk premium

An idea is more attractive when macro logic lines up with valuation and positioning asymmetry. Cheapness alone is not a catalyst.

## Smart-money-neglect checklist

Before developing an idea, identify at least one plausible reason it may be ignored or under-owned by sophisticated investors:

- Is the obvious version of the trade crowded, while a better relative-value expression is neglected?
- Does the idea sit between asset-class silos, making ownership unclear?
- Is the catalyst slow or path-dependent, making it unattractive to short-horizon funds?
- Does it require a non-consensus policy reaction function?
- Is the market focused on a first-order effect while missing a second-order effect?
- Are mandates, benchmark constraints, or liquidity concerns preventing large capital from expressing it?
- Is the data noisy, new, unglamorous, or under-covered?
- Is there a behavioral reason: recency bias, narrative anchoring, or career risk?

If no plausible neglect reason exists, the idea can still be considered, but it should face a higher evidence bar.

## Hypothesis workflow

For each candidate:

1. State the macro driver.
2. State the expected asset-price transmission.
3. Identify what the market likely prices today.
4. Identify why smart money may be missing, avoiding, or mis-expressing it.
5. List supporting evidence.
6. List contradictory evidence.
7. Compare at least two trade expressions.
8. Define invalidation criteria.
9. Score and classify as `accept`, `watchlist`, `needs_data`, or `reject`.

## Falsification discipline

Ask what should be observable if the thesis is false:

- Policy divergence thesis false if rate differentials move against it.
- Growth slowdown thesis false if hard activity and labor data reaccelerate.
- Inflation persistence thesis false if sequential core inflation decelerates and expectations remain anchored.
- Capital-flow thesis false if reserves stabilize, flows improve, and currency strengthens.
- Liquidity tightening thesis false if funding stress falls and credit spreads compress.

A thesis without observable failure conditions must be rejected.

## Data standards

- Use current data for tactical or 1-3 month horizons.
- For 3-6 month horizons, combine current data with medium-term trend indicators.
- For structural ideas, include valuation, flows, and regime evidence.
- If data is stale or incomplete, downgrade to `watchlist` or `needs_data`.
- Always note the latest available observation date when possible.

## Evidence hierarchy

Stronger evidence:

- Multiple independent indicators point in the same direction.
- Market pricing contradicts or underweights the data.
- Positioning is not already crowded in the thesis direction.
- The trade expression directly maps to the mechanism.
- Contradictory evidence is known and bounded.

Weaker evidence:

- Single data point.
- News headline.
- Price momentum alone.
- Backtest without causal explanation.
- Valuation with no catalyst.

## Output expectations

Each cycle should produce:

- Macro regime snapshot.
- 3-5 candidate hypotheses.
- Aggressive rejection of weak hypotheses.
- One fully developed surviving idea, or a clear decision that none survive.
- Log updates in `research_log.md`, `ideas.tsv`, and if applicable `ideas/<idea_id>.md` or `rejected_ideas.md`.
