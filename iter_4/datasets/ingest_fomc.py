from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
import csv
import re

import pandas as pd

from datasets.cache import FOMC_DIR
from datasets.http import fetch_text_url

FOMC_INDEX_URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"


@dataclass(frozen=True)
class FomcDocument:
    url: str
    title: str
    document_type: str


class FomcLinkParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self._active_href: str | None = None
        self._active_text: list[str] = []
        self.documents: list[FomcDocument] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = ""
        for key, value in attrs:
            if key.lower() == "href" and value is not None:
                href = value
                break
        if "fomc" in href.lower() or "monetary" in href.lower():
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
        lower = f"{href} {title}".lower()
        if re.search(r"20\d{6}", lower) is None:
            return
        if "minutes" in lower:
            doc_type = "minutes"
        elif "statement" in lower or "pressrelease" in lower or "monetary" in lower:
            doc_type = "statement"
        else:
            doc_type = "other"
        self.documents.append(FomcDocument(url=urljoin(self.base_url, href), title=title, document_type=doc_type))


def normalize_fomc_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_fomc_index(html: str, base_url: str) -> list[FomcDocument]:
    parser = FomcLinkParser(base_url)
    parser.feed(html)
    seen: set[str] = set()
    documents: list[FomcDocument] = []
    for document in parser.documents:
        if document.url in seen:
            continue
        seen.add(document.url)
        documents.append(document)
    return documents


def publication_timestamp_from_url(url: str) -> str:
    match = re.search(r"(20\d{2})(\d{2})(\d{2})", url)
    if match is None:
        raise ValueError(f"Cannot infer FOMC publication date from {url}")
    year, month, day = match.groups()
    return f"{year}-{month}-{day}T00:00:00Z"


def write_fomc_events(documents: list[FomcDocument], output_dir: Path, fetch_text: Callable[[str], str]) -> Path:
    rows: list[dict[str, object]] = []
    for document in documents:
        text = normalize_fomc_text(fetch_text(document.url))
        rows.append(
            {
                "published_at": publication_timestamp_from_url(document.url),
                "document_type": document.document_type,
                "title": document.title,
                "url": document.url,
                "text_sha256": sha256(text.encode("utf-8")).hexdigest(),
                "text": text,
            }
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "fomc_events.tsv"
    pd.DataFrame(rows).to_csv(path, sep="\t", index=False, quoting=csv.QUOTE_MINIMAL, escapechar="\\")
    return path


def ingest_fomc(output_dir: Path = FOMC_DIR, fetcher: Callable[[str], str] = fetch_text_url) -> Path:
    index_html = fetcher(FOMC_INDEX_URL)
    documents = [
        document
        for document in parse_fomc_index(index_html, FOMC_INDEX_URL)
        if document.document_type in {"statement", "minutes"}
    ]
    return write_fomc_events(documents, output_dir, fetcher)
