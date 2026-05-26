# macroresearch

This is an experiment to have the LLM do autonomous macro research and generate **macro trading ideas that are grounded in logic, theory, data, and falsifiable reasoning**.

The goal is not to produce a stream of clever narratives. The goal is to produce trade ideas where the causal mechanism is explicit, the theoretical anchor is clear, the data evidence is checkable, the trade expression is coherent, and the failure conditions are known in advance.

This document is for research and education only. It is not investment advice, a recommendation to trade, or a substitute for independent risk review.

---

## Setup

To set up a new macro research run, work with the user to:

1. **Agree on a run tag**  
   Propose a tag based on today's date and theme, for example:

   ```text
   may27-usd-rates
   may27-china-credit
   may27-energy-inflation
   ```

   The branch `macroresearch/<tag>` must not already exist. This should be treated as a fresh research run.

2. **Create the branch**

   ```bash
   git checkout -b macroresearch/<tag>` from current master
   ```

3. **Read the in-scope files**  
   Read these files for full context before generating ideas:

   - `README.md` — repository context, available data, and prior research conventions.
   - `macro_framework.md` — the house macro framework, preferred indicators, and economic models.
   - `universe.md` — tradable instruments, asset classes, ETFs, futures, FX pairs, rates products, and constraints.
   - `risk_framework.md` — sizing rules, drawdown limits, stop logic, liquidity constraints, and prohibited trades.
   - `prior_ideas.tsv` — previous ideas, outcomes, failures, and recurring mistakes.
   - `data_catalog.md` — available data sources and update frequency.

4. **Verify data exists**  
   Check that the local data directory contains the required macro data:

   ```text
   ~/.cache/macroresearch/
   ```

   At minimum, verify availability of:

   - Rates and yield curves.
   - Inflation data.
   - Growth data.
   - Central bank policy data.
   - FX data.
   - Equity index data.
   - Commodity data.
   - Credit spreads.
   - Positioning / sentiment data, if available.
   - Event calendar data, if available.

   If data is missing, tell the human exactly what is missing and which ingestion script should be run.

5. **Initialize `ideas.tsv`**  
   Create `ideas.tsv` with only the header row. Do not commit this file.

   ```text
   idea_id	status	asset_class	trade_expression	time_horizon	theory_anchor	logic_score	data_score	asymmetry_score	risk_score	total_score	description
   ```

6. **Initialize `research_log.md`**  
   Create a running research log with sections for:

   - Macro regime snapshot.
   - Candidate hypotheses.
   - Accepted ideas.
   - Rejected ideas.
   - Open questions.
   - Sources checked.

7. **Confirm and go**  
   Confirm that setup is complete, data exists, and the research constraints are clear.

Once setup is complete, begin the research loop.

---

## Research objective

The goal is simple:

> Find macro trading ideas that are logically grounded, theoretically coherent, empirically supported, tradable, and falsifiable.

A valid macro trade idea must answer six questions:

1. **What is the trade?**  
   The instrument, direction, time horizon, and expression.

2. **Why should it work?**  
   The economic mechanism, not just the narrative.

3. **What theory supports it?**  
   Examples: monetary policy reaction function, fiscal impulse, balance of payments, uncovered interest parity, purchasing power parity, real rates, term premium, liquidity cycle, credit cycle, inventory cycle, risk premium, convexity, or capital flows.

4. **What data supports or contradicts it?**  
   The evidence must be specific and current enough for the proposed horizon.

5. **What would prove it wrong?**  
   The invalidation criteria must be stated before the idea is accepted.

6. **Why is the trade expression appropriate?**  
   The chosen instrument must match the thesis, horizon, risk, convexity, and catalyst path.

---

## What counts as a good macro idea

A good idea should have most of the following properties:

- A clear causal chain from macro driver to asset price.
- A theoretical anchor, not only a chart pattern.
- A reason the market may be mispricing the outcome.
- A catalyst or path for repricing.
- A trade expression that isolates the thesis as cleanly as possible.
- A defined horizon.
- A known carry profile.
- A known downside scenario.
- A falsifiable stop or thesis-breaker.
- A way to monitor whether the thesis is strengthening or weakening.

A weak idea usually has one or more of these problems:

- It is just a headline summary.
- It says “X is strong, so buy X” without a transmission mechanism.
- It depends on a single noisy data point.
- It ignores positioning, valuation, carry, or policy reaction.
- It has no clear invalidation condition.
- The trade expression does not match the thesis.
- It is really a directional equity idea pretending to be macro.
- It relies on vague words like “uncertainty,” “momentum,” or “liquidity” without defining them.

---

## Macro theory anchors

Every idea must be grounded in at least one theory anchor. Use these as starting points, not as rigid templates.

### 1. Monetary policy reaction function

Core question:

> Is the market mispricing how the central bank will react to inflation, growth, employment, financial conditions, or currency pressure?

Common expressions:

- Rates futures.
- Yield curve steepeners / flatteners.
- Front-end duration.
- FX against funding currencies.
- Equity duration proxies.
- Gold or real-rate-sensitive assets.

Useful indicators:

- Inflation level and momentum.
- Wage growth.
- Unemployment and labor slack.
- Central bank communication.
- Market-implied policy path.
- Real rates.
- Financial conditions.

Failure modes:

- Central bank reaction function shifts.
- Inflation persistence is misread.
- Growth shock overwhelms inflation logic.
- Fiscal or political constraints dominate.

### 2. Growth cycle and demand impulse

Core question:

> Is the market underestimating an acceleration or deceleration in real activity?

Common expressions:

- Equity index direction.
- Cyclicals versus defensives.
- Commodities.
- Credit spreads.
- Yield curve shape.
- FX of growth-sensitive economies.

Useful indicators:

- PMIs.
- Retail sales.
- Industrial production.
- Employment.
- Housing.
- Credit growth.
- Freight / trade data.
- Earnings revisions.

Failure modes:

- Soft data diverges from hard data.
- Fiscal impulse offsets slowdown.
- Inventory cycle reverses quickly.
- Central bank easing preempts the downside.

### 3. Inflation impulse and real-rate repricing

Core question:

> Is inflation likely to surprise relative to what rates, FX, commodities, or equities are pricing?

Common expressions:

- Breakevens.
- Nominal duration.
- Real rates.
- Gold.
- Inflation-sensitive equities.
- Commodity baskets.
- FX in commodity exporters or importers.

Useful indicators:

- Core inflation momentum.
- Services inflation.
- Shelter inflation.
- Energy and food prices.
- Wage growth.
- Supply shocks.
- Inflation expectations.

Failure modes:

- One-off price shocks fade.
- Growth slowdown dominates inflation risk.
- Policy credibility anchors expectations.
- Base effects create misleading momentum.

### 4. Balance of payments and external funding

Core question:

> Is a currency or country asset mispriced given its current account, capital flows, reserve position, and external financing needs?

Common expressions:

- FX spot or forwards.
- Local rates.
- Sovereign credit.
- Equity index relative value.
- Commodity-linked FX pairs.

Useful indicators:

- Current account balance.
- Terms of trade.
- FX reserves.
- External debt maturity profile.
- Real yield differential.
- Portfolio and FDI flows.
- Import cover.

Failure modes:

- Policy intervention is stronger than expected.
- Capital controls distort adjustment.
- External funding pressure is delayed.
- Terms of trade shock reverses.

### 5. Liquidity, credit, and risk appetite

Core question:

> Is global or domestic liquidity becoming easier or tighter in a way that changes risk premia?

Common expressions:

- Equity index direction.
- Credit spreads.
- Volatility.
- High beta versus low beta.
- EM FX.
- Gold or crypto, depending on thesis.

Useful indicators:

- Central bank balance sheets.
- Bank reserves.
- Credit spreads.
- Lending standards.
- Money supply.
- Treasury issuance and liquidity drain.
- Dollar funding stress.
- Volatility term structure.

Failure modes:

- Liquidity proxy is stale or mismeasured.
- Earnings or growth fundamentals dominate.
- Policy backstop appears.
- Positioning is already crowded.

### 6. Fiscal impulse and political economy

Core question:

> Is the market mispricing the growth, inflation, rates, or FX impact of fiscal policy?

Common expressions:

- Duration.
- Curve steepeners.
- Inflation breakevens.
- Domestic equities.
- FX.
- Sector baskets tied to fiscal spending.

Useful indicators:

- Deficit trajectory.
- Treasury issuance.
- Government spending plans.
- Tax changes.
- Election calendar.
- Debt sustainability.
- Fiscal multiplier assumptions.

Failure modes:

- Implementation lags.
- Offsetting monetary tightening.
- Political reversal.
- Fiscal leakage through imports.

### 7. Positioning, valuation, and risk premium

Core question:

> Is the macro thesis underpriced or already fully reflected in positioning and valuation?

Common expressions:

- Relative value trades.
- Options structures.
- Mean-reversion trades.
- Trend-following overlays.
- Cross-asset hedges.

Useful indicators:

- Futures positioning.
- Options skew.
- Volatility risk premium.
- Real yield differentials.
- Equity risk premium.
- Credit spread percentile.
- FX valuation versus PPP / REER.

Failure modes:

- Cheap assets stay cheap for structural reasons.
- Crowded trades unwind violently.
- Valuation is irrelevant over the chosen horizon.
- Carry overwhelms expected convergence.

---

## Research constraints

### What you CAN do

- Generate macro trade hypotheses.
- Use economic theory to explain asset-price transmission.
- Compare multiple trade expressions for the same thesis.
- Use historical analogues, but only as supporting evidence.
- Use current data when the thesis depends on current conditions.
- Use simple statistical checks when useful.
- Use charts, tables, and source citations where available.
- Reject ideas aggressively if the logic is weak.
- Prefer relative value trades when they isolate the thesis better than outright directional trades.
- Prefer simpler ideas when two ideas have similar expected quality.

### What you CANNOT do

- Present a trade idea without a theory anchor.
- Present a trade idea without invalidation criteria.
- Rely only on recent price action.
- Rely only on news headlines.
- Ignore carry, roll-down, convexity, liquidity, or implementation costs.
- Use stale data when the idea depends on current conditions.
- Treat backtests as proof of a causal macro relationship.
- Recommend position sizing as personalized financial advice.
- Hide uncertainty.
- Generate ideas that cannot be monitored after entry.

---

## Idea format

Each accepted idea must be written in this structure.

```markdown
# Idea: <short descriptive title>

## One-line thesis
<One sentence explaining the trade and why it should work.>

## Trade expression
- Instrument:
- Direction:
- Time horizon:
- Preferred structure:
- Alternative expressions:
- Instruments to avoid:

## Theory anchor
<Which macro theory supports this idea?>

## Causal chain
1. <Macro condition or shock>
2. <Policy / growth / inflation / flow transmission>
3. <Asset-price implication>
4. <Expected market repricing>

## Why the market may be wrong
<Explain the disagreement versus consensus, pricing, positioning, or implied path.>

## Supporting evidence
- Evidence 1:
- Evidence 2:
- Evidence 3:

## Contradictory evidence
- Counterpoint 1:
- Counterpoint 2:
- Counterpoint 3:

## Catalyst path
<What causes the trade to work?>

## Invalidation criteria
The thesis is wrong if:
- <Specific data or market condition>
- <Specific policy condition>
- <Specific price / spread / rate condition>

## Monitoring dashboard
Track:
- <Indicator 1>
- <Indicator 2>
- <Indicator 3>
- <Market-implied pricing variable>
- <Positioning / sentiment measure>

## Risks
- Carry / roll risk:
- Liquidity risk:
- Policy risk:
- Positioning risk:
- Correlation / cross-asset risk:
- Event risk:

## Expected payoff profile
- Base case:
- Bull case:
- Bear case:
- Asymmetry:

## Final judgment
Accepted / rejected / watchlist.

Reason:
<Short explanation.>
```

---

## Scoring rubric

Each idea receives five scores from 1 to 5.

### 1. Logic score

Does the causal chain make sense?

- **1** — Vague narrative with no transmission mechanism.
- **3** — Plausible mechanism but with gaps.
- **5** — Clear, theory-grounded causal chain from macro driver to asset price.

### 2. Theory score

Is the idea anchored in a known macro, financial, or market-structure framework?

- **1** — No clear theory.
- **3** — Theory exists but is loosely applied.
- **5** — Theory directly explains the expected repricing.

### 3. Data score

Is the evidence current, relevant, and balanced?

- **1** — No data or cherry-picked data.
- **3** — Some relevant data, but incomplete.
- **5** — Multiple independent data points, including contradictory evidence.

### 4. Asymmetry score

Is the expected payoff attractive relative to the identifiable downside?

- **1** — Poor asymmetry or undefined downside.
- **3** — Reasonable but not compelling.
- **5** — Clear upside/downside asymmetry or convexity.

### 5. Implementation score

Does the trade expression cleanly match the thesis?

- **1** — Expression is noisy, expensive, or mismatched.
- **3** — Tradable but with meaningful basis or carry issues.
- **5** — Clean expression with known risks and monitoring variables.

The total score is:

```text
total_score = logic_score + theory_score + data_score + asymmetry_score + implementation_score
```

Interpretation:

```text
21-25: strong candidate
16-20: watchlist or needs better expression
11-15: weak idea; usually reject
 5-10: discard
```

A trade idea with no invalidation criteria is automatically rejected, regardless of score.

---

## Output format

Each research cycle should produce a short summary like this:

```text
---
idea_id:               USDJPY-real-rates-001
status:                watchlist
asset_class:           FX / rates
trade_expression:      Long USDJPY via options
horizon:               1-3 months
theory_anchor:         real-rate differential / monetary policy divergence
logic_score:           4
theory_score:          4
data_score:            3
asymmetry_score:       4
implementation_score:  3
total_score:           18
main_risk:             FX intervention or dovish Fed repricing
invalidation:          US real yields break lower while BoJ reprices hawkishly
```

Accepted ideas should also be saved as individual markdown files:

```text
ideas/<idea_id>.md
```

Rejected ideas should be summarized in:

```text
rejected_ideas.md
```

This is important because repeated rejection patterns are valuable research data.

---

## Logging results

When a research cycle is done, log the result to `ideas.tsv`.

The TSV has these columns:

```text
idea_id	status	asset_class	trade_expression	time_horizon	theory_anchor	logic_score	data_score	asymmetry_score	risk_score	total_score	description
```

Definitions:

1. `idea_id` — short unique identifier.
2. `status` — `accept`, `watchlist`, `reject`, or `needs_data`.
3. `asset_class` — rates, FX, equity index, commodity, credit, cross-asset, or multi-asset.
4. `trade_expression` — concise description of the implementation.
5. `time_horizon` — tactical, 1-3 months, 3-6 months, 6-12 months, or structural.
6. `theory_anchor` — the main macro theory behind the idea.
7. `logic_score` — 1 to 5.
8. `data_score` — 1 to 5.
9. `asymmetry_score` — 1 to 5.
10. `risk_score` — 1 to 5, where higher means risk is better understood and more bounded.
11. `total_score` — sum of the main scores.
12. `description` — short text description. Avoid commas if downstream parsing is fragile.

Example:

```text
idea_id	status	asset_class	trade_expression	time_horizon	theory_anchor	logic_score	data_score	asymmetry_score	risk_score	total_score	description
USDJPY-real-rates-001	watchlist	FX / rates	Long USDJPY via 3m call spread	1-3 months	real-rate differential	4	3	4	3	17	Policy divergence remains plausible but intervention risk is high
US2s10s-steepener-001	accept	rates	US 2s10s steepener	3-6 months	monetary policy reaction function	5	4	4	4	21	Front-end easing repricing with sticky long-end term premium
Copper-China-credit-001	reject	commodities	Long copper futures	1-3 months	China credit impulse	3	2	3	2	10	Narrative plausible but data confirmation is weak
```

---

## The research loop

The research run happens on a dedicated branch, for example:

```text
macroresearch/may27-usd-rates
```

LOOP UNTIL THE USER STOPS THE RUN:

1. **Check current state**  
   Look at the git state, current branch, existing ideas, and prior rejected ideas.

2. **Create a macro regime snapshot**  
   Summarize the current state of:

   - Growth.
   - Inflation.
   - Policy.
   - Liquidity.
   - Fiscal impulse.
   - Credit.
   - FX / external balance.
   - Commodities.
   - Positioning.
   - Volatility / risk appetite.

3. **Generate candidate hypotheses**  
   Produce 3-5 possible macro hypotheses. Each must have:

   - Asset class.
   - Direction.
   - Theory anchor.
   - Causal chain.
   - Required evidence.
   - Potential trade expression.

4. **Reject weak ideas first**  
   Before developing an idea, try to kill it. Ask:

   - Is this just a narrative?
   - Is the causal chain broken?
   - Is the data stale?
   - Is the trade already crowded?
   - Is the carry too expensive?
   - Is the trade expression too noisy?
   - Is there a better relative value version?

5. **Develop the best surviving idea**  
   Write the full idea memo using the idea format.

6. **Score the idea**  
   Assign logic, theory, data, asymmetry, and implementation scores.

7. **Decide status**

   - `accept` — strong logic, sufficient evidence, tradable expression, clear invalidation.
   - `watchlist` — strong logic but missing catalyst, data confirmation, or attractive entry.
   - `needs_data` — plausible but requires data not currently available.
   - `reject` — weak logic, weak evidence, poor expression, or no edge.

8. **Record the result**  
   Append the result to `ideas.tsv` and update `research_log.md`.

9. **Commit only research artifacts worth keeping**  
   Commit accepted or watchlist idea memos. Do not commit `ideas.tsv` if it is intended as a local scratch ledger.

10. **Continue**  
   Move to the next hypothesis. Do not repeat the same idea unless new data changes the conclusion.

---

## Falsification discipline

The LLM must actively look for reasons the idea is wrong.

For every idea, answer:

```text
What would I expect to observe if this thesis were false?
```

Examples:

- If the thesis is based on policy divergence, but rate differentials move against the trade, the thesis is weakening.
- If the thesis is based on growth acceleration, but hard data fails to follow soft data, the thesis is weakening.
- If the thesis is based on inflation persistence, but sequential core inflation decelerates, the thesis is weakening.
- If the thesis is based on capital outflows, but reserves stabilize and the currency strengthens, the thesis is weakening.
- If the thesis is based on liquidity tightening, but credit spreads compress and funding stress falls, the thesis is weakening.

Never accept an idea unless the thesis-breaker is explicit.

---

## Trade expression discipline

The trade expression must match the macro thesis.

Examples:

### Bad expression

```text
Thesis: US growth slows.
Trade: Short S&P 500.
```

Problem: This is too broad. The S&P 500 may rise if rates fall, AI earnings dominate, or liquidity improves.

### Better expressions

```text
- Long duration if the main channel is policy easing.
- Long 2s10s steepener if the main channel is front-end repricing.
- Long defensives versus cyclicals if the main channel is earnings dispersion.
- Long receiver swaptions if the thesis needs convexity around downside data.
- Short high-yield credit if the main channel is default risk and funding stress.
```

For each idea, compare at least two trade expressions before choosing one.

---

## Required checks before accepting an idea

Before an idea can be marked `accept`, verify:

```text
[ ] The causal chain is explicit.
[ ] The theory anchor is named.
[ ] The trade expression matches the thesis.
[ ] The horizon is stated.
[ ] The catalyst path is plausible.
[ ] The key data is current enough for the horizon.
[ ] Contradictory evidence is included.
[ ] Carry / roll / financing cost is considered.
[ ] Positioning and valuation are considered.
[ ] Invalidation criteria are explicit.
[ ] Monitoring indicators are listed.
[ ] The idea is not just a restatement of consensus.
```

If any of these are missing, the idea is `watchlist`, `needs_data`, or `reject`, not `accept`.

---

## Example candidate idea memo

```markdown
# Idea: US curve steepener on growth slowdown and front-end easing repricing

## One-line thesis
A US 2s10s steepener may benefit if slowing growth causes the market to price more front-end easing while long-end yields remain supported by fiscal supply and term-premium concerns.

## Trade expression
- Instrument: US Treasury curve
- Direction: Long 2-year duration / short 10-year duration equivalent, or receive 2y versus pay 10y
- Time horizon: 3-6 months
- Preferred structure: 2s10s steepener
- Alternative expressions: ED/SOFR futures steepener, receiver spread on front-end rates, long TLT hedged with short intermediate duration
- Instruments to avoid: Simple long duration if the thesis depends specifically on curve shape

## Theory anchor
Monetary policy reaction function plus term-premium / fiscal supply framework.

## Causal chain
1. Growth slows and labor-market slack rises.
2. The central bank reaction function shifts toward easing.
3. Front-end yields fall as the expected policy path reprices.
4. Long-end yields fall less, or remain sticky, because of fiscal supply and term-premium risk.
5. The 2s10s curve steepens.

## Why the market may be wrong
The market may be pricing the level of future cuts but underpricing the curve-shape effect if fiscal supply and term premium keep the long end from rallying as much as the front end.

## Supporting evidence
- Growth indicators are weakening.
- Labor-market data is softening.
- Long-end term premium remains sensitive to fiscal issuance.

## Contradictory evidence
- Inflation may remain too sticky for front-end easing.
- A recession scare could cause the whole curve to bull-flatten first.
- Safe-haven demand could pull down 10-year yields more than expected.

## Catalyst path
Weak payrolls, softer inflation, dovish central bank communication, or a repricing lower in the expected policy path.

## Invalidation criteria
The thesis is wrong if:
- Inflation reaccelerates and front-end cuts are priced out.
- Growth remains resilient enough to keep policy restrictive.
- Long-end yields rally more than front-end yields because of recession hedging.

## Monitoring dashboard
Track:
- 2-year yield.
- 10-year yield.
- 2s10s spread.
- Market-implied policy path.
- Core inflation momentum.
- Payrolls and unemployment.
- Treasury issuance and auction tails.

## Risks
- Carry / roll risk: Curve may remain inverted longer than expected.
- Liquidity risk: Treasury liquidity can deteriorate around stress events.
- Policy risk: Central bank may push back against easing expectations.
- Positioning risk: Steepeners may already be crowded.
- Correlation risk: In acute recession shock, duration rally may dominate curve logic.

## Expected payoff profile
- Base case: Moderate steepening as front-end cuts are priced.
- Bull case: Sharp bull steepening after weak labor data.
- Bear case: Inflation reacceleration causes bear flattening.
- Asymmetry: Better if expressed through options when catalyst timing is uncertain.

## Final judgment
Watchlist.

Reason:
The logic is coherent, but entry quality depends on current market pricing, inflation trend, and curve positioning.
```

---

## Research quality rules

1. Prefer **mechanism over narrative**.
2. Prefer **relative value over blunt direction** when it better isolates the thesis.
3. Prefer **falsifiable hypotheses over vague conviction**.
4. Prefer **simple trade construction over clever complexity**.
5. Prefer **current data over stale analogies**.
6. Prefer **explicit uncertainty over false precision**.
7. Prefer **watchlist** over forced acceptance.
8. Prefer **rejecting bad ideas** over generating more ideas.

---

## NEVER DO THIS

Never output an idea like this:

```text
Inflation is sticky, so buy commodities.
```

This is not acceptable because it lacks:

- A theory anchor.
- A causal chain.
- A specific commodity or instrument.
- A horizon.
- A view on real rates and FX.
- A view on positioning.
- A catalyst.
- An invalidation condition.
- A risk framework.

A better version would ask:

```text
If inflation is sticky, is the market underpricing higher real rates, higher breakevens, commodity scarcity, or policy error? Which asset most cleanly expresses that view? What would make the thesis wrong?
```

---

## Stopping condition

Unlike model training experiments, macro research should not run forever without human review.

Stop and ask for review after any of the following:

- 3 accepted ideas.
- 10 rejected ideas.
- A major data gap is found.
- A proposed idea requires instruments outside the approved universe.
- A proposed idea has material leverage, liquidity, or options-risk complexity.
- The research begins repeating the same thesis under different names.

The goal is not endless output. The goal is a small number of high-quality, logically grounded, falsifiable macro trade ideas.
