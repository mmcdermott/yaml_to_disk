"""Unit tests for ParquetFile internals that can't be expressed as doctests.

Public write/validate/matches behavior is covered by doctests on
:class:`yaml_to_disk.file_types.parquet.ParquetFile`.
"""

import pytest

import yaml_to_disk.file_types.parquet as parquet_mod

pytest.importorskip("pyarrow")
pytest.importorskip("pyarrow.parquet")


def test_load_pyarrow_returns_cached_modules():
    """_load_pyarrow returns the cached module objects once pyarrow has been imported."""
    pa_result, pq_result = parquet_mod._load_pyarrow()
    assert pa_result is not None
    assert pq_result is not None
