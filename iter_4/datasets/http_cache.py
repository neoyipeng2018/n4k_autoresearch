from __future__ import annotations

import json
from collections.abc import Callable
from hashlib import sha256
from pathlib import Path
from typing import cast

from datasets.cache import CACHE_ROOT
from datasets.http import fetch_json_url, fetch_text_url

HTTP_CACHE_DIR = CACHE_ROOT / "http"


def cache_path_for_url(url: str, suffix: str, cache_dir: Path = HTTP_CACHE_DIR) -> Path:
    return cache_dir / f"{sha256(url.encode('utf-8')).hexdigest()}{suffix}"


def cached_text_fetcher(
    url: str,
    cache_dir: Path = HTTP_CACHE_DIR,
    refresh: bool = False,
    fetcher: Callable[[str], str] = fetch_text_url,
) -> str:
    path = cache_path_for_url(url, ".txt", cache_dir)
    if path.exists() and not refresh:
        return path.read_text()
    text = fetcher(url)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return text


def cached_json_fetcher(
    url: str,
    cache_dir: Path = HTTP_CACHE_DIR,
    refresh: bool = False,
    fetcher: Callable[[str], object] = fetch_json_url,
) -> object:
    path = cache_path_for_url(url, ".json", cache_dir)
    if path.exists() and not refresh:
        return cast(object, json.loads(path.read_text()))
    payload = fetcher(url)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True))
    return payload
