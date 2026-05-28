from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urljoin
import re


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
