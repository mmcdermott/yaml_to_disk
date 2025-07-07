from pathlib import Path

import pytest

from yaml_to_disk.file_matchers import FILE_TYPE_MATCHER
from yaml_to_disk.file_types.csv import CSVFile
from yaml_to_disk.file_types.json import JSONFile


def test_file_type_matcher_known_extensions():
    assert FILE_TYPE_MATCHER(".json").__name__ == JSONFile.__name__
    assert FILE_TYPE_MATCHER(Path("foo.csv")).__name__ == CSVFile.__name__


def test_file_type_matcher_unknown_extension():
    with pytest.raises(ValueError):
        FILE_TYPE_MATCHER(".unknown")
