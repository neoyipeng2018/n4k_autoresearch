from __future__ import annotations

from datasets.ingest_prices import ingest_prices
from prepare import BENCHMARK_SYMBOL, DEFAULT_UNIVERSE


def main() -> None:
    symbols = list(dict.fromkeys([*DEFAULT_UNIVERSE, BENCHMARK_SYMBOL]))
    paths = ingest_prices(symbols)
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
