from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlencode

import pandas as pd

from datasets.cache import SEC_DIR
from datasets.http import fetch_json_url

SEC_SUBMISSIONS_BASE = "https://data.sec.gov/submissions/"
SEC_ARCHIVE_BASE = "https://www.sec.gov/Archives/edgar/data/"
DEFAULT_SEC_CIKS = ("0000320193", "0000789019", "0001018724")
DEFAULT_SEC_FORMS = frozenset({"10-K", "10-Q", "8-K"})


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


def filing_document_url(cik: str, accession_number: str, primary_document: str) -> str:
    accession_path = accession_number.replace("-", "")
    cik_path = str(int(normalize_cik(cik)))
    return f"{SEC_ARCHIVE_BASE}{cik_path}/{accession_path}/{primary_document}"


def nested_mapping(payload: object, key: str) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise ValueError("Expected JSON object")
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object at {key}")
    return value


def string_list(payload: dict[str, object], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise ValueError(f"Expected list at {key}")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"Expected string item at {key}")
        result.append(item)
    return result


def parse_recent_filings(payload: object, cik: str, forms: set[str] | frozenset[str], limit_per_cik: int) -> list[EdgarFiling]:
    recent = nested_mapping(nested_mapping(payload, "filings"), "recent")
    accession_numbers = string_list(recent, "accessionNumber")
    form_types = string_list(recent, "form")
    accepted_times = string_list(recent, "acceptanceDateTime")
    primary_documents = string_list(recent, "primaryDocument")
    filings: list[EdgarFiling] = []
    for accession_number, form_type, accepted_at, primary_document in zip(accession_numbers, form_types, accepted_times, primary_documents):
        if form_type not in forms:
            continue
        filings.append(
            EdgarFiling(
                cik=normalize_cik(cik),
                accession_number=accession_number,
                form_type=form_type,
                accepted_at=accepted_at,
                primary_document_url=filing_document_url(cik, accession_number, primary_document),
            )
        )
        if len(filings) >= limit_per_cik:
            break
    return filings


def write_sec_filings(filings: list[EdgarFiling], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "sec_filings.tsv"
    pd.DataFrame([asdict(filing) for filing in filings]).to_csv(path, sep="\t", index=False)
    return path


def ingest_sec_filings(
    ciks: tuple[str, ...] = DEFAULT_SEC_CIKS,
    output_dir: Path = SEC_DIR,
    fetcher: Callable[[str], object] = fetch_json_url,
    forms: set[str] | frozenset[str] = DEFAULT_SEC_FORMS,
    limit_per_cik: int = 8,
) -> Path:
    filings: list[EdgarFiling] = []
    for cik in ciks:
        filings.extend(parse_recent_filings(fetcher(submissions_url(cik)), cik, forms, limit_per_cik))
    return write_sec_filings(filings, output_dir)
