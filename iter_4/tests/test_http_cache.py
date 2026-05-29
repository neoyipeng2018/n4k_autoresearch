from __future__ import annotations

from pathlib import Path

from datasets.http_cache import cached_json_fetcher, cached_text_fetcher


def test_cached_text_fetcher_reuses_local_payload(tmp_path: Path) -> None:
    calls: list[str] = []

    def fetcher(url: str) -> str:
        calls.append(url)
        return f"payload for {url}"

    first = cached_text_fetcher("https://example.test/a", tmp_path, fetcher=fetcher)
    second = cached_text_fetcher("https://example.test/a", tmp_path, fetcher=fetcher)

    assert first == "payload for https://example.test/a"
    assert second == first
    assert calls == ["https://example.test/a"]
    assert len(list(tmp_path.glob("*.txt"))) == 1


def test_cached_json_fetcher_reuses_local_payload(tmp_path: Path) -> None:
    calls: list[str] = []

    def fetcher(url: str) -> object:
        calls.append(url)
        return {"url": url, "observations": [{"value": "1.0"}]}

    first = cached_json_fetcher("https://example.test/data", tmp_path, fetcher=fetcher)
    second = cached_json_fetcher("https://example.test/data", tmp_path, fetcher=fetcher)

    assert first == {"url": "https://example.test/data", "observations": [{"value": "1.0"}]}
    assert second == first
    assert calls == ["https://example.test/data"]
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_cached_fetchers_refresh_when_requested(tmp_path: Path) -> None:
    responses = ["old", "new"]

    def fetcher(url: str) -> str:
        del url
        return responses.pop(0)

    assert cached_text_fetcher("https://example.test/a", tmp_path, fetcher=fetcher) == "old"
    assert cached_text_fetcher("https://example.test/a", tmp_path, refresh=True, fetcher=fetcher) == "new"
