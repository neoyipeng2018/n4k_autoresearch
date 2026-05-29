from __future__ import annotations

import time
from collections.abc import Callable

import requests

HTTP_HEADERS = {"User-Agent": "n4k-autoresearch/0.1 public-data research"}


def fetch_text_url(url: str, timeout: int = 30, delay_seconds: float = 0.2) -> str:
    response = requests.get(url, headers=HTTP_HEADERS, timeout=timeout)
    response.raise_for_status()
    if delay_seconds > 0.0:
        time.sleep(delay_seconds)
    text = response.text
    if not isinstance(text, str):
        raise TypeError("response.text was not text")
    return text


def fetch_json_url(url: str, timeout: int = 30, delay_seconds: float = 0.2) -> object:
    response = requests.get(url, headers=HTTP_HEADERS, timeout=timeout)
    response.raise_for_status()
    if delay_seconds > 0.0:
        time.sleep(delay_seconds)
    return response.json()


TextFetcher = Callable[[str], str]
JsonFetcher = Callable[[str], object]
