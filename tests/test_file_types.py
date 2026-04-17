"""Unit tests for paths that require mocking or module reloading and can't be expressed as doctests."""

import importlib
from unittest.mock import patch

import pytest

import yaml_to_disk.file_types.parquet as parquet_mod
import yaml_to_disk.file_types.toml as toml_mod
import yaml_to_disk.file_types.yaml
from yaml_to_disk.file_types.csv import CSVFile

# --- YAMLFile CDumper fallback ---


class TestYAMLFileDumperFallback:
    def test_cdumper_import_fallback(self):
        """When CDumper is unavailable, the module falls back to pure-Python Dumper."""
        import yaml

        original_cdumper = getattr(yaml, "CDumper", None)
        try:
            if hasattr(yaml, "CDumper"):
                delattr(yaml, "CDumper")
            importlib.reload(yaml_to_disk.file_types.yaml)
            from yaml_to_disk.file_types.yaml import YAMLFile as ReloadedYAML

            ReloadedYAML.validate({"key": "value"})
        finally:
            if original_cdumper is not None:
                yaml.CDumper = original_cdumper
            importlib.reload(yaml_to_disk.file_types.yaml)


# --- Lazy-import guards: missing-dependency error paths ---


class TestParquetLazyImportMissing:
    def test_load_pyarrow_when_missing(self):
        """_load_pyarrow raises ImportError when pyarrow is not installed."""
        saved_pa, saved_pq = parquet_mod.pa, parquet_mod.pq
        try:
            parquet_mod.pa = None
            parquet_mod.pq = None
            with (
                patch.dict("sys.modules", {"pyarrow": None, "pyarrow.parquet": None}),
                pytest.raises(ImportError, match="pyarrow is required"),
            ):
                parquet_mod._load_pyarrow()
        finally:
            parquet_mod.pa = saved_pa
            parquet_mod.pq = saved_pq


class TestTomlLazyImportMissing:
    def test_load_tomli_w_when_missing(self):
        """_load_tomli_w raises ImportError when tomli-w is not installed."""
        saved = toml_mod.tomli_w
        try:
            toml_mod.tomli_w = None
            with (
                patch.dict("sys.modules", {"tomli_w": None}),
                pytest.raises(ImportError, match="tomli-w is required"),
            ):
                toml_mod._load_tomli_w()
        finally:
            toml_mod.tomli_w = saved


# --- CSVFile internal branches not reachable through public API ---


class TestCSVFileEdgeCases:
    def test_parse_list_lines_row_not_a_list(self):
        """_parse_list_lines rejects a non-list row; not reachable via the public _parse dispatch."""
        with pytest.raises(ValueError, match="Row 0 is not a list"):
            CSVFile._parse_list_lines([["Name", "Age"], "not a list"])
