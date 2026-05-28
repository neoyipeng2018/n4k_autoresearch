from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode

SEC_SUBMISSIONS_BASE = "https://data.sec.gov/submissions/"


@dataclass(frozen=True)
class EdgarFiling:
    cik: str
    accession_number: str
    form_type: str
    accepted_at: str
    primary_document_url: str


def normalize_cik(cik: str) -> str:
    digits = "".join(character for character in cik if character.isdigit())
    if not digits:
        raise ValueError("CIK must contain at least one digit")
    return digits.zfill(10)


def submissions_url(cik: str) -> str:
    return f"{SEC_SUBMISSIONS_BASE}CIK{normalize_cik(cik)}.json"


def company_search_url(query: str) -> str:
    return "https://www.sec.gov/edgar/search/#/" + urlencode({"q": query})
