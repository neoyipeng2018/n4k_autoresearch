from __future__ import annotations

from pathlib import Path

CACHE_ROOT = Path.home() / ".cache" / "macroresearch" / "iter_4"
MARKET_DIR = CACHE_ROOT / "market"
FOMC_DIR = CACHE_ROOT / "fomc"
BEIGE_BOOK_DIR = CACHE_ROOT / "beige_book"
SEC_DIR = CACHE_ROOT / "sec"
FRED_DIR = CACHE_ROOT / "fred"
FEATURE_DIR = CACHE_ROOT / "features"
MANIFEST_PATH = CACHE_ROOT / "artifact_manifest.tsv"
