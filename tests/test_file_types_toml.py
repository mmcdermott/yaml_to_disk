"""Unit tests for TOMLFile internals that can't be expressed as doctests.

Public write/validate/matches behavior is covered by doctests on
:class:`yaml_to_disk.file_types.toml.TOMLFile`.
"""

import pytest

import yaml_to_disk.file_types.toml as toml_mod

pytest.importorskip("tomli_w")


def test_load_tomli_w_returns_cached_module():
    """_load_tomli_w returns the cached module once tomli_w has been imported."""
    result = toml_mod._load_tomli_w()
    assert result is not None
