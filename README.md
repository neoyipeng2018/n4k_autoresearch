# macroresearch

This repository is for autonomous macro research: generating, falsifying, scoring, and logging tradable macro ideas in order to find **the best macro trading idea for a retail quant with approximately $80k USD in an Interactive Brokers (IB/IBKR) account**.

The explicit research objective is to find **the best reward-to-risk macro trade that a retail quant can realistically implement**, while still being grounded in macro theory, current data, falsifiable logic, and a clear explanation of why the opportunity is not already fully harvested by smart money. The goal is not to beat hedge funds at their most crowded trades; it is to find expressions where retail account structure, smaller size, flexibility, or simpler implementation can avoid smart-money crowding and institutional mandate constraints.

This is research and education only. It is not investment advice, not a recommendation to trade, and not a substitute for independent risk review.

## What makes an idea interesting here

A candidate idea should combine six elements:

1. **Causal macro mechanism** — the trade must follow from a coherent economic or market-structure transmission channel.
2. **Evidence** — current data must support the mechanism, while contradictory evidence is explicitly addressed.
3. **Tradability** — the expression must be liquid enough, monitorable, and aligned with the thesis.
4. **Neglect / mispricing reason** — the idea should explain why smart money may not already fully own or price it.
5. **Retail IB suitability** — the trade must be realistic for about $80k at IB, including margin, borrow, financing, liquidity, taxes, fractional-share feasibility, and operational complexity.
6. **Reward-to-risk superiority** — the idea must compete against simpler alternatives on drawdown, tail risk, Calmar/Sharpe, carry, implementation costs, and explainability.

The fourth, fifth, and sixth requirements matter. A good macro narrative is not enough. The research should ask: *why would this opportunity still exist, why is it suitable for an $80k retail IB account, and why is its reward-to-risk better than simpler alternatives?*

## Sources of smart-money neglect

Use these as hypotheses, not excuses:

- **Mandate constraints**: large allocators cannot express niche relative-value trades or cross-asset overlays.
- **Benchmark pressure**: active managers avoid trades that create high tracking error despite good macro logic.
- **Crowding elsewhere**: attention and capital are concentrated in consensus trades, leaving second-order expressions underpriced.
- **Career risk**: unpopular ideas may be avoided until they become obvious.
- **Complexity / plumbing**: futures basis, roll, collateral, hedging, or local-market mechanics deter capital.
- **Time-horizon mismatch**: macro funds may be too short-term for slow-moving valuation/flow adjustments, or too long-term for tactical dislocations.
- **Data coverage gaps**: important indicators may be less followed, delayed, or hard to map to instruments.
- **Narrative dominance**: a dominant consensus story may obscure a contradictory but measurable mechanism.
- **Policy ambiguity**: markets may underprice nonlinear policy reaction functions or constraints.
- **Instrument mismatch**: the obvious trade may be crowded, while a cleaner relative-value expression is ignored.
- **Retail edge**: small account size can make simple, liquid, capacity-insensitive ETF or FX expressions viable while avoiding institutional crowding, mandate pressure, and complex derivative plumbing.

## Repository workflow

Each run happens on a branch named:

```text
macroresearch/<tag>
```

Run artifacts:

- `ideas.tsv` — local scratch ledger for candidate ideas and scores. Do not commit unless explicitly asked.
- `research_log.md` — running log of regime snapshot, hypotheses, decisions, open questions, and sources.
- `ideas/<idea_id>.md` — full memo for accepted or watchlist ideas.
- `rejected_ideas.md` — record of killed ideas and why they failed.

## Required context files

Before research begins, read:

- `README.md`
- `macro_framework.md`
- `universe.md`
- `risk_framework.md`
- `prior_ideas.tsv`
- `data_catalog.md`

## Data policy

Use local data in `~/.cache/macroresearch/` first. Supplement with public web sources only when local data is missing, stale, or insufficient, and record the source.

Research should be especially careful with current-data dependency. If data recency is not adequate for the proposed horizon, mark the idea `needs_data` or `watchlist`, not `accept`.

## Research standards

- Prefer mechanisms over narratives.
- Prefer relative-value expressions when they isolate the thesis better than outright direction.
- Prefer falsifiable hypotheses over conviction language.
- Prefer rejecting weak ideas over filling the log with mediocre trades.
- Always state why the opportunity may be ignored by smart money.
- Always compare at least two trade expressions before choosing one.
- Always include invalidation criteria and a monitoring dashboard.

## Stopping rules

Stop for human review after:

- 3 accepted ideas.
- 10 rejected ideas.
- A major data gap.
- A proposed idea requires instruments outside the approved universe.
- A proposed idea has material leverage, liquidity, or options-risk complexity.
- The research begins repeating the same thesis under different names.
