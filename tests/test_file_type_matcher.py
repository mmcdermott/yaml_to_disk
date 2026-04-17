"""Unit tests for FileTypeMatcher paths that require mocking ``entry_points``.

Simpler behavior (known/unknown extensions, Path resolution, type checks) is covered by the
doctests on :class:`yaml_to_disk.file_matchers.FileTypeMatcher`.
"""

from unittest.mock import MagicMock, patch

import pytest

import yaml_to_disk.file_matchers as _fm  # Use the FileType that file_matchers actually references
from yaml_to_disk.file_matchers import FileTypeMatcher

_FileType = _fm.FileType


def _make_mock_eps(entries):
    """Build a mock entry_points result from a list of (name, load_result_or_exc) tuples."""
    eps_dict = {}
    for name, val in entries:
        ep = MagicMock()
        if isinstance(val, type) and issubclass(val, Exception):
            ep.load.side_effect = val("boom")
        elif isinstance(val, Exception):
            ep.load.side_effect = val
        else:
            ep.load.return_value = val
        eps_dict[name] = ep

    mock_eps = MagicMock()
    mock_eps.names = list(eps_dict.keys())
    mock_eps.__getitem__ = MagicMock(side_effect=lambda name: eps_dict[name])
    return mock_eps


def test_file_type_matcher_entry_point_load_failure():
    mock_eps = _make_mock_eps([("bad", RuntimeError)])
    with (
        patch("yaml_to_disk.file_matchers.importlib.metadata.entry_points", return_value=mock_eps),
        pytest.raises(ImportError, match="Failed to load entry point bad"),
    ):
        FileTypeMatcher()


def test_file_type_matcher_entry_point_not_subclass():
    mock_eps = _make_mock_eps([("bad", int)])
    with (
        patch("yaml_to_disk.file_matchers.importlib.metadata.entry_points", return_value=mock_eps),
        pytest.raises(TypeError, match="does not subclass FileType"),
    ):
        FileTypeMatcher()


def test_file_type_matcher_entry_point_no_extension():
    class NoExtType(_FileType):
        extension = None

        @classmethod
        def validate(cls, contents):
            pass

        @classmethod
        def write(cls, file_path, contents):
            pass

    mock_eps = _make_mock_eps([("noext", NoExtType)])
    with (
        patch("yaml_to_disk.file_matchers.importlib.metadata.entry_points", return_value=mock_eps),
        pytest.raises(ValueError, match="has no extension defined"),
    ):
        FileTypeMatcher()


def test_file_type_matcher_duplicate_extensions():
    class TypeA(_FileType):
        extension = ".dup"

        @classmethod
        def validate(cls, contents):
            pass

        @classmethod
        def write(cls, file_path, contents):
            pass

    class TypeB(_FileType):
        extension = ".dup"

        @classmethod
        def validate(cls, contents):
            pass

        @classmethod
        def write(cls, file_path, contents):
            pass

    mock_eps = _make_mock_eps([("a", TypeA), ("b", TypeB)])
    with (
        patch("yaml_to_disk.file_matchers.importlib.metadata.entry_points", return_value=mock_eps),
        pytest.raises(ValueError, match="Multiple file types registered"),
    ):
        FileTypeMatcher()


def test_file_type_matcher_single_match_via_matches_method():
    """When exactly one file type matches via .matches() but not by suffix, return it."""

    class TypeA(_FileType):
        extension = ".a"

        @classmethod
        def matches(cls, file_path):
            return str(file_path).endswith(".special")

        @classmethod
        def validate(cls, contents):
            pass

        @classmethod
        def write(cls, file_path, contents):
            pass

    mock_eps = _make_mock_eps([("a", TypeA)])
    with patch("yaml_to_disk.file_matchers.importlib.metadata.entry_points", return_value=mock_eps):
        matcher = FileTypeMatcher()
        assert matcher(".special") is TypeA


def test_file_type_matcher_multiple_matches_via_matches_method():
    """When multiple file types match via .matches() but not by suffix, raise ValueError."""

    class TypeA(_FileType):
        extension = ".a"

        @classmethod
        def matches(cls, file_path):
            return True

        @classmethod
        def validate(cls, contents):
            pass

        @classmethod
        def write(cls, file_path, contents):
            pass

    class TypeB(_FileType):
        extension = ".b"

        @classmethod
        def matches(cls, file_path):
            return True

        @classmethod
        def validate(cls, contents):
            pass

        @classmethod
        def write(cls, file_path, contents):
            pass

    mock_eps = _make_mock_eps([("a", TypeA), ("b", TypeB)])
    with patch("yaml_to_disk.file_matchers.importlib.metadata.entry_points", return_value=mock_eps):
        matcher = FileTypeMatcher()
        with pytest.raises(ValueError, match="Multiple file types found"):
            matcher(".unknown")
