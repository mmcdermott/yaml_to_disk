import pytest

from yaml_to_disk.tabular_utils import validate_column_map, validate_row_map_list


def test_validate_column_map_valid():
    validate_column_map({"a": [1, 2], "b": [3, 4]})


def test_validate_column_map_bad_key():
    with pytest.raises(ValueError):
        validate_column_map({1: [1, 2]})


def test_validate_column_map_bad_value():
    with pytest.raises(ValueError):
        validate_column_map({"a": "x"})


def test_validate_column_map_bad_length():
    with pytest.raises(ValueError):
        validate_column_map({"a": [1, 2], "b": [3]})


def test_validate_row_map_list_valid():
    rows = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    assert validate_row_map_list(rows) == ["a", "b"]


def test_validate_row_map_list_inconsistent():
    rows = [{"a": 1, "b": 2}, {"a": 3}]
    with pytest.raises(ValueError):
        validate_row_map_list(rows)


def test_validate_row_map_list_bad_key():
    with pytest.raises(ValueError):
        validate_row_map_list([{1: 2}])
