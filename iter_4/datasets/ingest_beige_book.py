from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
import csv
import re

import pandas as pd

from datasets.cache import BEIGE_BOOK_DIR
from datasets.http import fetch_text_url
from datasets.ingest_fomc import normalize_fomc_text

BEIGE_BOOK_INDEX_URL = "https://www.federalreserve.gov/monetarypolicy/beige-book-default.htm"


@dataclass(frozen=True)
class BeigeBookLink:
    published_at: str
    title: str
    url: str
    district: str = "National"


@dataclass(frozen=True)
class BeigeBookDocument:
    published_at: str
    title: str
    url: str
    text_sha256: str
    text: str
    district: str = "National"


class BeigeBookLinkParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self._active_href: str | None = None
        self._active_text: list[str] = []
        self.links: list[BeigeBookLink] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = ""
        for key, value in attrs:
            if key.lower() == "href" and value is not None:
                href = value
                break
        lower = href.lower()
        if "beigebook" in lower or "beige-book" in lower:
            self._active_href = href
            self._active_text = []

    def handle_data(self, data: str) -> None:
        if self._active_href is not None:
            self._active_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or self._active_href is None:
            return
        title = normalize_fomc_text(" ".join(self._active_text))
        href = self._active_href
        self._active_href = None
        self._active_text = []
        if not title:
            return
        published_at = publication_timestamp_from_beige_book(title, href)
        if published_at is None:
            return
        self.links.append(BeigeBookLink(published_at, title, urljoin(self.base_url, href)))


def publication_timestamp_from_beige_book(title: str, url: str) -> str | None:
    url_match = re.search(r"(20\d{2})(\d{2})(\d{2})", url)
    if url_match is not None:
        year, month, day = url_match.groups()
        return f"{year}-{month}-{day}T00:00:00Z"
    title_match = re.search(
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s+(20\d{2})",
        title,
        flags=re.IGNORECASE,
    )
    if title_match is None:
        return None
    month_name, day, year = title_match.groups()
    month = pd.Timestamp(f"{month_name} 1, {year}").month
    return f"{year}-{month:02d}-{int(day):02d}T00:00:00Z"


def parse_beige_book_index(html: str, base_url: str = BEIGE_BOOK_INDEX_URL) -> list[BeigeBookLink]:
    parser = BeigeBookLinkParser(base_url)
    parser.feed(html)
    seen: set[str] = set()
    links: list[BeigeBookLink] = []
    for link in parser.links:
        if link.url in seen:
            continue
        seen.add(link.url)
        links.append(link)
    return links


def normalize_beige_book_document(published_at: str, title: str, url: str, text: str, district: str = "National") -> BeigeBookDocument:
    clean_text = normalize_fomc_text(text)
    digest = sha256(clean_text.encode("utf-8")).hexdigest()
    return BeigeBookDocument(published_at=published_at, title=title.strip(), url=url, text_sha256=digest, text=clean_text, district=district)


def write_beige_book_events(documents: list[BeigeBookDocument], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "beige_book_events.tsv"
    pd.DataFrame([asdict(document) for document in documents]).to_csv(path, sep="\t", index=False, quoting=csv.QUOTE_MINIMAL, escapechar="\\")
    return path


def ingest_beige_book(output_dir: Path = BEIGE_BOOK_DIR, fetcher: Callable[[str], str] = fetch_text_url) -> Path:
    index_html = fetcher(BEIGE_BOOK_INDEX_URL)
    documents = [
        normalize_beige_book_document(link.published_at, link.title, link.url, fetcher(link.url), link.district)
        for link in parse_beige_book_index(index_html, BEIGE_BOOK_INDEX_URL)
    ]
    return write_beige_book_events(documents, output_dir)
