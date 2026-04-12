"""Tests for file type handlers that require optional dependencies (pyarrow, tomli-w)."""

from pathlib import Path

import pytest

import yaml_to_disk.file_types.parquet as parquet_mod
import yaml_to_disk.file_types.toml as toml_mod

pa = pytest.importorskip("pyarrow")
pq = pytest.importorskip("pyarrow.parquet")
pytest.importorskip("tomli_w")

from yaml_to_disk.file_types.parquet import ParquetFile  # noqa: E402
from yaml_to_disk.file_types.toml import TOMLFile  # noqa: E402

# --- Lazy-import caching (requires the dep to be present) ---


class TestParquetLazyImportCaching:
    def test_load_pyarrow_caches(self):
        """_load_pyarrow returns cached modules on second call."""
        pa_result, pq_result = parquet_mod._load_pyarrow()
        assert pa_result is not None
        assert pq_result is not None


class TestTomlLazyImportCaching:
    def test_load_tomli_w_caches(self):
        """_load_tomli_w returns cached module on second call."""
        result = toml_mod._load_tomli_w()
        assert result is not None


# --- ParquetFile ---


class TestParquetFile:
    def test_write_and_read_column_map(self, tmp_path: Path):
        fp = tmp_path / "data.parquet"
        col_map = {"a": [1, 2], "b": [3, 4]}
        ParquetFile.write(fp, col_map)
        assert pq.read_table(fp).to_pydict() == col_map

    def test_write_and_read_row_map_list(self, tmp_path: Path):
        fp = tmp_path / "data.parquet"
        rows = [{"x": 1, "y": 2}, {"x": 3, "y": 4}]
        ParquetFile.write(fp, rows)
        assert pq.read_table(fp).to_pydict() == {"x": [1, 3], "y": [2, 4]}

    def test_write_pyarrow_table(self, tmp_path: Path):
        fp = tmp_path / "data.parquet"
        table = pa.table({"c": [10, 20]})
        ParquetFile.write(fp, table)
        assert pq.read_table(fp).to_pydict() == {"c": [10, 20]}

    def test_validate_column_map(self):
        ParquetFile.validate({"a": [1, 2], "b": [3, 4]})

    def test_validate_pyarrow_table(self):
        ParquetFile.validate(pa.table({"a": [1]}))

    def test_validate_row_map_list(self):
        ParquetFile.validate([{"a": 1}, {"a": 2}])

    def test_validate_bad_column_map(self):
        with pytest.raises(ValueError):
            ParquetFile.validate({"a": [1, 2], "b": [3]})

    def test_validate_invalid_type(self):
        with pytest.raises(TypeError, match="Contents must be"):
            ParquetFile.validate("not valid")

    def test_write_empty_column_map(self, tmp_path: Path):
        fp = tmp_path / "empty.parquet"
        ParquetFile.write(fp, {})
        assert pq.read_table(fp).to_pydict() == {}

    def test_write_empty_row_map_list(self, tmp_path: Path):
        fp = tmp_path / "empty.parquet"
        ParquetFile.write(fp, [])
        assert pq.read_table(fp).to_pydict() == {}

    def test_matches(self):
        assert ParquetFile.matches(Path("foo.parquet"))
        assert not ParquetFile.matches(Path("foo.txt"))


# --- TOMLFile ---


class TestTOMLFile:
    def test_write_and_read(self, tmp_path: Path):
        fp = tmp_path / "cfg.toml"
        TOMLFile.write(fp, {"key": "value"})
        assert fp.read_text().strip() == 'key = "value"'

    def test_validate_valid(self):
        TOMLFile.validate({"key": "value", "nested": {"a": 1}})

    def test_validate_invalid(self):
        with pytest.raises(AttributeError):
            TOMLFile.validate({1, 2})

    def test_matches(self):
        assert TOMLFile.matches(Path("foo.toml"))
        assert not TOMLFile.matches(Path("foo.txt"))
