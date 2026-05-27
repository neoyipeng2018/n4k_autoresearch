#!/usr/bin/env python3
"""Quick retail ETF strategy screen for macroresearch.

Uses Yahoo Finance chart JSON for adjusted-close data. This is a research
screen, not a production backtester: it omits tax lots, commissions, detailed
slippage, borrow, and live data validation.
"""

from __future__ import annotations

import argparse
import bisect
import collections
import datetime as dt
import json
import math
import csv
import statistics
import urllib.request

SYMBOLS = [
    "SPY", "QQQ", "RSP", "IWM", "USMV", "QUAL", "MTUM", "VLUE",
    "IEF", "TLT", "SHY", "SGOV", "GLD", "DBC",
    "XLP", "XLU", "XLV", "XLF", "XLI", "XLK", "HYG", "LQD",
]


def fetch_yahoo(symbol: str, start: dt.date, end: dt.date) -> dict[dt.date, float]:
    period1 = int(dt.datetime(start.year, start.month, start.day, tzinfo=dt.timezone.utc).timestamp())
    period2 = int(dt.datetime(end.year, end.month, end.day, tzinfo=dt.timezone.utc).timestamp())
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?period1={period1}&period2={period2}&interval=1d&events=history&includeAdjustedClose=true"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 - public market-data endpoint
        data = json.load(resp)
    result = data["chart"]["result"][0]
    timestamps = result["timestamp"]
    adjusted = result["indicators"]["adjclose"][0]["adjclose"]
    return {
        dt.datetime.utcfromtimestamp(ts).date(): price
        for ts, price in zip(timestamps, adjusted)
        if price is not None
    }


def build_returns(prices: dict[str, dict[dt.date, float]]) -> dict[str, dict[dt.date, float]]:
    out: dict[str, dict[dt.date, float]] = {}
    for sym, series in prices.items():
        prev = None
        rets: dict[dt.date, float] = {}
        for day in sorted(series):
            if prev is not None and series[prev] > 0:
                rets[day] = series[day] / series[prev] - 1
            prev = day
        out[sym] = rets
    return out


def annualized_vol(values: list[float]) -> float:
    return statistics.pstdev(values) * math.sqrt(252) if len(values) > 1 else 0.0


class Screen:
    def __init__(self, prices: dict[str, dict[dt.date, float]], start: dt.date):
        self.prices = prices
        self.returns = build_returns(prices)
        self.dates = sorted(prices["SPY"])
        self.start = start
        self.month_ends = set(sorted({(d.year, d.month): d for d in self.dates if d >= start}.values()))
        self.price_dates = {sym: sorted(series) for sym, series in prices.items()}
        self.price_values = {sym: [prices[sym][day] for day in self.price_dates[sym]] for sym in prices}
        self.price_prefix = {}
        for sym, values in self.price_values.items():
            prefix = [0.0]
            running = 0.0
            for value in values:
                running += value
                prefix.append(running)
            self.price_prefix[sym] = prefix
        self.return_dates = {sym: sorted(series) for sym, series in self.returns.items()}
        self.return_values = {sym: [self.returns[sym][day] for day in self.return_dates[sym]] for sym in self.returns}

    def history(self, sym: str, day: dt.date) -> list[dt.date]:
        days = self.price_dates[sym]
        end = bisect.bisect_right(days, day)
        return days[:end]

    def _last_price_index(self, sym: str, day: dt.date) -> int:
        return bisect.bisect_right(self.price_dates[sym], day) - 1

    def sma(self, sym: str, day: dt.date, n: int) -> float | None:
        idx = self._last_price_index(sym, day)
        if idx + 1 < n:
            return None
        prefix = self.price_prefix[sym]
        return (prefix[idx + 1] - prefix[idx + 1 - n]) / n

    def lookback_return(self, sym: str, day: dt.date, n: int) -> float | None:
        idx = self._last_price_index(sym, day)
        if idx < n:
            return None
        values = self.price_values[sym]
        return values[idx] / values[idx - n] - 1

    def lookback_vol(self, sym: str, day: dt.date, n: int) -> float | None:
        days = self.return_dates[sym]
        idx = bisect.bisect_right(days, day) - 1
        vals = self.return_values[sym][idx + 1 - n:idx + 1]
        if len(vals) < n:
            return None
        return annualized_vol(vals)

    def backtest(self, name: str, selector):
        value = 1.0
        weights: dict[str, float] = {}
        daily = []
        allocations = []
        for day in self.dates:
            if day < self.start:
                continue
            if day in self.month_ends or not weights:
                weights = selector(day)
                allocations.append((day, dict(weights)))
            ret = 0.0
            for sym, weight in weights.items():
                if sym == "CASH":
                    asset_ret = 0.0
                elif sym == "SGOV" and day not in self.returns.get("SGOV", {}):
                    asset_ret = self.returns["SHY"].get(day, 0.0)
                else:
                    asset_ret = self.returns.get(sym, {}).get(day, 0.0)
                ret += weight * asset_ret
            value *= 1 + ret
            daily.append((day, ret, value))
        return self.metrics(name, daily, allocations)

    @staticmethod
    def metrics(name: str, daily, allocations):
        rets = [r for _, r, _ in daily]
        vals = [v for _, _, v in daily]
        dates = [d for d, _, _ in daily]
        years = (dates[-1] - dates[0]).days / 365.25
        cagr = vals[-1] ** (1 / years) - 1
        vol = annualized_vol(rets)
        sharpe = statistics.mean(rets) * 252 / vol if vol else 0.0
        peak = vals[0]
        max_dd = 0.0
        for val in vals:
            peak = max(peak, val)
            max_dd = min(max_dd, val / peak - 1)
        sorted_rets = sorted(rets)
        tail_n = max(1, int(0.01 * len(sorted_rets)))
        cvar1 = sum(sorted_rets[:tail_n]) / tail_n
        monthly_values = collections.OrderedDict()
        for day, _, val in daily:
            monthly_values[(day.year, day.month)] = val
        previous = None
        monthly_rets = []
        for val in monthly_values.values():
            if previous is not None:
                monthly_rets.append(val / previous - 1)
            previous = val
        return {
            "name": name,
            "cagr": cagr,
            "vol": vol,
            "sharpe": sharpe,
            "max_dd": max_dd,
            "calmar": cagr / abs(max_dd) if max_dd < 0 else 0.0,
            "cvar1": cvar1,
            "worst_day": min(rets),
            "worst_month": min(monthly_rets),
            "end_multiple": vals[-1],
            "current_allocation": allocations[-1][1],
        }

    def fixed(self, weights: dict[str, float]):
        return lambda _day: weights

    def single_asset_trend_vol(self, asset: str, target_vol: float):
        def selector(day: dt.date) -> dict[str, float]:
            ma = self.sma(asset, day, 200)
            latest = self.history(asset, day)[-1]
            if ma is None or self.prices[asset][latest] <= ma:
                return {"SHY": 1.0}
            realized = self.lookback_vol(asset, day, 63) or 0.20
            risky_weight = min(1.0, target_vol / realized)
            return {asset: risky_weight, "SHY": 1.0 - risky_weight}
        return selector

    def multi_asset_trend_momentum(
        self,
        target_vol: float,
        *,
        assets: list[str] | None = None,
        trend_days: int = 200,
        momentum_days: int = 126,
        vol_days: int = 63,
        top_n: int = 2,
        sleeve_cap: float = 0.50,
        ballast: str = "SHY",
    ):
        assets = assets or ["SPY", "USMV", "GLD", "DBC"]

        def selector(day: dt.date) -> dict[str, float]:
            eligible = []
            for asset in assets:
                ma = self.sma(asset, day, trend_days)
                mom = self.lookback_return(asset, day, momentum_days)
                latest_idx = self._last_price_index(asset, day)
                if ma is not None and mom is not None and self.price_values[asset][latest_idx] > ma and mom > 0:
                    eligible.append((mom, asset))
            selected = sorted(eligible, reverse=True)[:top_n]
            if not selected:
                return {ballast: 1.0}
            weights: dict[str, float] = {}
            for _mom, asset in selected:
                realized = self.lookback_vol(asset, day, vol_days) or 0.20
                weights[asset] = min(sleeve_cap, target_vol / realized / len(selected))
            weights[ballast] = 1.0 - sum(weights.values())
            return weights
        return selector

    def multi_asset_top2_trend_momentum(self, target_vol: float):
        return self.multi_asset_trend_momentum(target_vol)

    def dual_momentum(self):
        risk_assets = ["SPY", "QQQ", "RSP", "IWM", "IEF", "TLT", "GLD", "DBC"]

        def selector(day: dt.date) -> dict[str, float]:
            scores = [(self.lookback_return(asset, day, 126), asset) for asset in risk_assets]
            scores = [(score, asset) for score, asset in scores if score is not None]
            if not scores:
                return {"SHY": 1.0}
            score, asset = max(scores)
            return {asset: 1.0} if score > 0 else {"SHY": 1.0}
        return selector


def fmt_pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def robustness_grid(screen: Screen) -> list[dict]:
    rows = []
    for trend_days in [100, 150, 200, 250]:
        for momentum_days in [63, 126, 189, 252]:
            for vol_days in [21, 63, 126]:
                for target_vol in [0.06, 0.08, 0.10, 0.12]:
                    for top_n in [1, 2, 3]:
                        for sleeve_cap in [0.33, 0.50, 0.67, 1.00]:
                            if sleeve_cap * top_n < 0.50:
                                # Too cash-heavy by construction for this research question.
                                continue
                            name = (
                                f"trend={trend_days},mom={momentum_days},vol={vol_days},"
                                f"target={target_vol:.2f},top={top_n},cap={sleeve_cap:.2f}"
                            )
                            metrics = screen.backtest(
                                name,
                                screen.multi_asset_trend_momentum(
                                    target_vol,
                                    trend_days=trend_days,
                                    momentum_days=momentum_days,
                                    vol_days=vol_days,
                                    top_n=top_n,
                                    sleeve_cap=sleeve_cap,
                                ),
                            )
                            metrics.update(
                                {
                                    "trend_days": trend_days,
                                    "momentum_days": momentum_days,
                                    "vol_days": vol_days,
                                    "target_vol": target_vol,
                                    "top_n": top_n,
                                    "sleeve_cap": sleeve_cap,
                                }
                            )
                            rows.append(metrics)
    return rows


def print_robustness(rows: list[dict], out_csv: str | None = None) -> None:
    rows = sorted(rows, key=lambda row: (row["calmar"], row["sharpe"], -abs(row["max_dd"])), reverse=True)
    print(f"Robustness grid count: {len(rows)}")
    print("Top 20 by Calmar, then Sharpe:")
    header = "Rank,Trend,Momentum,VolLookback,TargetVol,TopN,Cap,CAGR,Vol,Sharpe,MaxDD,Calmar,CVaR1,WorstMonth,CurrentAllocation"
    print(header)
    for i, row in enumerate(rows[:20], start=1):
        alloc = ";".join(f"{sym}:{weight:.2f}" for sym, weight in row["current_allocation"].items())
        print(
            f"{i},{row['trend_days']},{row['momentum_days']},{row['vol_days']},{row['target_vol']:.2f},"
            f"{row['top_n']},{row['sleeve_cap']:.2f},{fmt_pct(row['cagr'])},{fmt_pct(row['vol'])},"
            f"{row['sharpe']:.2f},{fmt_pct(row['max_dd'])},{row['calmar']:.2f},{fmt_pct(row['cvar1'])},"
            f"{fmt_pct(row['worst_month'])},{alloc}"
        )

    qualifying = [row for row in rows if row["max_dd"] >= -0.15 and row["cagr"] >= 0.06]
    print()
    print(f"Qualifying rows with CAGR >= 6% and max drawdown >= -15%: {len(qualifying)} / {len(rows)}")
    if qualifying:
        def median(vals: list[float]) -> float:
            return statistics.median(vals)

        print(
            "Qualifying medians: "
            f"CAGR {fmt_pct(median([r['cagr'] for r in qualifying]))}, "
            f"Vol {fmt_pct(median([r['vol'] for r in qualifying]))}, "
            f"Sharpe {median([r['sharpe'] for r in qualifying]):.2f}, "
            f"MaxDD {fmt_pct(median([r['max_dd'] for r in qualifying]))}, "
            f"Calmar {median([r['calmar'] for r in qualifying]):.2f}"
        )
        for field in ["trend_days", "momentum_days", "vol_days", "target_vol", "top_n", "sleeve_cap"]:
            counts = collections.Counter(row[field] for row in qualifying)
            print(f"Qualifying {field}: " + ", ".join(f"{key}={counts[key]}" for key in sorted(counts)))

    if out_csv:
        fieldnames = [
            "name", "trend_days", "momentum_days", "vol_days", "target_vol", "top_n", "sleeve_cap",
            "cagr", "vol", "sharpe", "max_dd", "calmar", "cvar1", "worst_day", "worst_month",
            "end_multiple", "current_allocation",
        ]
        with open(out_csv, "w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                out = {key: row[key] for key in fieldnames if key != "current_allocation"}
                out["current_allocation"] = json.dumps(row["current_allocation"], sort_keys=True)
                writer.writerow(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2016-01-01")
    parser.add_argument("--data-start", default="2015-01-01")
    parser.add_argument("--robustness", action="store_true", help="run multi-asset parameter robustness grid")
    parser.add_argument("--out-csv", help="optional CSV path for robustness grid output")
    args = parser.parse_args()

    start = dt.date.fromisoformat(args.start)
    data_start = dt.date.fromisoformat(args.data_start)
    data_end = dt.datetime.now(dt.timezone.utc).date() + dt.timedelta(days=2)

    prices = {sym: fetch_yahoo(sym, data_start, data_end) for sym in SYMBOLS}
    screen = Screen(prices, start)

    if args.robustness:
        rows = robustness_grid(screen)
        print_robustness(rows, args.out_csv)
        return

    strategies = [
        screen.backtest("SPY buy-hold", screen.fixed({"SPY": 1.0})),
        screen.backtest("60/40 SPY/IEF monthly", screen.fixed({"SPY": 0.6, "IEF": 0.4})),
        screen.backtest("Permanent portfolio SPY/TLT/GLD/SHY", screen.fixed({"SPY": 0.25, "TLT": 0.25, "GLD": 0.25, "SHY": 0.25})),
        screen.backtest("SPY 200d trend + 10% vol cap", screen.single_asset_trend_vol("SPY", 0.10)),
        screen.backtest("USMV 200d trend + 8% vol cap", screen.single_asset_trend_vol("USMV", 0.08)),
        screen.backtest("Monthly dual momentum best-of risky assets else SHY", screen.dual_momentum()),
        screen.backtest("Multi-asset top-2 trend/momentum + 8% vol cap", screen.multi_asset_top2_trend_momentum(0.08)),
        screen.backtest("Multi-asset top-2 trend/momentum + 10% vol cap", screen.multi_asset_top2_trend_momentum(0.10)),
        screen.backtest("RSP/QQQ dollar-neutral pair with SHY collateral", screen.fixed({"RSP": 0.5, "QQQ": -0.5, "SHY": 1.0})),
    ]

    print("Strategy,CAGR,Vol,Sharpe,MaxDD,Calmar,CVaR1,WorstDay,WorstMonth,EndMultiple,CurrentAllocation")
    for item in sorted(strategies, key=lambda row: (row["calmar"], row["sharpe"]), reverse=True):
        alloc = ";".join(f"{sym}:{weight:.2f}" for sym, weight in item["current_allocation"].items())
        print(
            f"{item['name']},{fmt_pct(item['cagr'])},{fmt_pct(item['vol'])},{item['sharpe']:.2f},"
            f"{fmt_pct(item['max_dd'])},{item['calmar']:.2f},{fmt_pct(item['cvar1'])},"
            f"{fmt_pct(item['worst_day'])},{fmt_pct(item['worst_month'])},{item['end_multiple']:.2f},{alloc}"
        )


if __name__ == "__main__":
    main()
