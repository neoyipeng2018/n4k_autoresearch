from __future__ import annotations

from datasets.registry import DATASETS, CACHE_ROOT, DatasetSpec


def test_dataset_specs_have_audit_metadata() -> None:
    assert "prices_yahoo" in DATASETS
    assert "fomc_text" in DATASETS
    for spec in DATASETS.values():
        assert isinstance(spec, DatasetSpec)
        assert spec.source_url.startswith("http")
        assert spec.cache_subdir
        assert spec.timestamp_column
        assert spec.license_note
        assert spec.description


def test_iter4_cache_root_is_isolated() -> None:
    assert str(CACHE_ROOT).endswith("macroresearch/iter_4")


def test_fomc_spec_is_point_in_time_text() -> None:
    spec = DATASETS["fomc_text"]
    assert spec.kind == "text"
    assert spec.point_in_time_safe
    assert spec.timestamp_column == "published_at"
