# Risk Framework

This document defines risk principles for macro research ideas. It is not portfolio advice and does not prescribe position sizing for the user.

The purpose is to force every idea to describe downside, path risk, carry, liquidity, retail implementation frictions, smart-money crowding, and invalidation before it can be marked `accept`. The default account lens is a retail quant with approximately $80k in an IB account seeking the best reward-to-risk macro idea, not maximum gross return or institutional complexity.

## Core rule

No idea can be accepted unless the following are explicit:

- Thesis invalidation criteria.
- Trade-level risk and adverse scenario.
- Carry / roll / financing cost.
- Liquidity and implementation constraints.
- Monitoring dashboard.
- Reason the trade expression matches the thesis.
- Reason smart money may be ignoring or under-owning the opportunity.
- Reason the trade is suitable for an ~$80k retail IB account.
- Reason the reward-to-risk is superior to simpler alternatives.

## Status definitions

### accept

Use only when:

- Causal chain is clear.
- Theory anchor is strong.
- Current evidence is sufficient and balanced.
- Contradictory evidence is addressed.
- Trade expression is liquid and appropriate.
- Invalidation criteria are observable.
- Risk is bounded or at least well understood.
- The idea is not simply consensus in another form.
- Retail IB implementation is realistic after margin, borrow, financing, liquidity, tax/turnover, and operational complexity.
- Expected reward-to-risk is strong versus simpler alternatives and tail risk is explicitly addressed.

### watchlist

Use when logic is strong but:

- Entry is unattractive.
- Catalyst is unclear.
- Positioning may already be crowded.
- Data is supportive but incomplete.
- Expression involves moderate complexity.
- Timing risk is high.

### needs_data

Use when the idea is plausible but cannot be evaluated because required data is absent, stale, or unreliable.

### reject

Use when:

- Causal chain is weak.
- Theory anchor is missing.
- Evidence is cherry-picked.
- Trade expression is noisy or mismatched.
- Carry/roll/liquidity costs dominate.
- Invalidation is vague.
- The idea is probably already crowded or consensus without compensation.

## Risk dimensions

Score risk understanding from 1 to 5, where higher means the risk is better understood and more bounded.

1. **Carry / roll / financing risk**
   - Rates: curve carry and roll-down.
   - FX: interest-rate differential and funding cost.
   - Commodities: futures curve structure and ETF roll.
   - Credit: spread carry versus mark-to-market risk.
   - Volatility: roll decay and variance risk premium.

2. **Liquidity risk**
   - Can the instrument gap or become hard to trade?
   - Is the proxy liquid but economically imprecise?
   - Are there event windows where liquidity disappears?

3. **Policy risk**
   - Central-bank reaction function changes.
   - FX intervention.
   - Fiscal or regulatory surprise.
   - Capital controls or sanctions.

4. **Positioning risk**
   - Is the trade crowded?
   - Is the unwind asymmetric?
   - Are CTAs / vol-control / risk-parity flows likely to amplify moves?

5. **Basis / expression risk**
   - Does the instrument actually capture the thesis?
   - Is the ETF/future/cross contaminated by unrelated drivers?
   - Is there a cleaner relative-value expression?

6. **Correlation / regime risk**
   - Does the trade fail in a risk-off shock?
   - Do correlations change under stress?
   - Does a hedge work only in benign environments?

7. **Event risk**
   - Data releases.
   - Central-bank meetings.
   - Elections.
   - Treasury refunding / auctions.
   - Geopolitical events.

8. **Retail implementation and tail risk**
   - Does the trade fit an ~$80k IB account without hidden leverage or forced liquidation risk?
   - Are borrow, margin, financing, ETF spread, tax/turnover, and execution costs small relative to the expected edge?
   - Does the strategy avoid gap risk, crowded unwind risk, and slow persistent drawdown risk?
   - Is there a simpler long-only, cash-ballast, or systematic alternative with better Calmar / drawdown / CVaR?

## Prohibited or restricted ideas

By default, do not mark as `accept` without explicit human review:

- Material leverage.
- Complex options structures.
- Volatility ETPs as non-tactical holdings.
- Illiquid EM local assets.
- Single-name equities.
- Short commodity ETFs as long-horizon expressions.
- Trades with undefined loss or path-dependent blow-up risk.
- Ideas requiring data that is not available or cannot be monitored.

## Invalidation standards

Invalidation criteria must be observable. Avoid vague statements like "if the macro thesis changes."

Good invalidation examples:

- Sequential core inflation falls below a specified threshold for multiple releases while breakevens decline.
- Policy path reprices opposite the thesis by a specified amount.
- Yield curve spread breaks a level inconsistent with the thesis.
- Credit spreads compress despite expected funding stress.
- FX reserves stabilize and capital-flow pressure eases.
- Commodity inventories rebuild while curve backwardation collapses.

## Monitoring dashboard standards

Each idea should list 5-8 indicators:

- At least two macro indicators.
- At least one market-pricing variable.
- At least one positioning/valuation/crowding variable if available.
- At least one trade-specific risk indicator.

## Smart-money crowding and neglect

The research goal is not just to find a good macro story. It is to find good macro stories that are **not already fully exploited by smart money**.

For every idea, classify the likely state:

- **Ignored**: the topic is not central to current consensus discussion.
- **Under-owned**: the topic is known but hard to express or unattractive under mandates.
- **Mis-expressed**: investors own the obvious expression but not the cleaner one.
- **Crowded**: the opportunity may be real but already over-owned.
- **Consensus trap**: the story is popular but risk/reward is poor.

Crowded or consensus-trap ideas should usually be rejected or watchlisted unless asymmetry is compelling.

## Scoring and acceptance discipline

A high total score is not enough. An idea is automatically not `accept` if:

- No invalidation criteria.
- No theory anchor.
- No current data for a current-data-dependent horizon.
- No discussion of carry/roll/financing.
- No plausible explanation of mispricing or neglect.
- Trade expression is outside the approved universe.
- It cannot be implemented cleanly in an ~$80k retail IB account.
- It has worse drawdown-adjusted reward-to-risk than a simpler liquid alternative.

## Human-review triggers

Stop and ask for review if:

- 3 accepted ideas are reached.
- 10 rejected ideas are reached.
- Major data gap blocks core analysis.
- Proposed idea requires instruments outside `universe.md`.
- Idea requires options, leverage, volatility ETPs, or complex derivative structures.
- Research begins repeating the same thesis under different labels.
