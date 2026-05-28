from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from datasets.ingest_fomc import normalize_fomc_text


@dataclass(frozen=True)
class BeigeBookDocument:
    published_at: str
    title: str
    url: str
    text_sha256: str
    text: str


def normalize_beige_book_document(published_at: str, title: str, url: str, text: str) -> BeigeBookDocument:
    clean_text = normalize_fomc_text(text)
    digest = sha256(clean_text.encode("utf-8")).hexdigest()
    return BeigeBookDocument(published_at=published_at, title=title.strip(), url=url, text_sha256=digest, text=clean_text)
