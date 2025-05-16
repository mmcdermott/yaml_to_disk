import csv
import io
from pathlib import Path
from typing import Any, ClassVar

from .base import FileType


class CSVFile(FileType):
    """A class for validating and writing comma-separated-value (CSV) files in one of several representations.

    Examples:
        >>> str_data = '''
        ... Name, Age, City
        ... "Alice Smith", 30, New York
        ... "Bob Jones, Jr.", 25, Los Angeles
        ... '''
        >>> with tempfile.NamedTemporaryFile() as tmp_file:
        ...     CSVFile.write(Path(tmp_file.name), str_data)
        ...     print(Path(tmp_file.name).read_text())
        Name, Age, City
        "Alice Smith", 30, New York
        "Bob Jones, Jr.", 25, Los Angeles

    For string formatted data, errors are raised if any of the CSV rows have inconsistent fields:

        >>> str_data_invalid = '''
        ... Name, Age, City
        ... Alice, 30, New York, 43
        ... Bob, 25, Los Angeles
        ... '''
        >>> CSVFile.validate(str_data_invalid)
        Traceback (most recent call last):
            ...
        ValueError: A string CSV can't have inconsistent fields in rows; got
            Row 0 has extra columns; got ' 43'

    CSV files can also accommodate a dictionary of column names to column values. Note that as raw values are
    used here, the CSV file will not have the spaces in it the prior stringified version did, for example.

        >>> column_map_data = {
        ...     "Name": ["Alice Smith", "Bob Jones, Jr."],
        ...     "Age": [30, 25],
        ...     "City": ["New York", "Los Angeles"]
        ... }
        >>> with tempfile.NamedTemporaryFile() as tmp_file:
        ...     CSVFile.write(Path(tmp_file.name), column_map_data)
        ...     print(Path(tmp_file.name).read_text().strip())
        Name,Age,City
        Alice Smith,30,New York
        "Bob Jones, Jr.",25,Los Angeles

    In this format, we must (1) have all column names be strings:

        >>> column_map_data_invalid = {
        ...     "Name": ["Alice Smith", "Bob Jones, Jr."],
        ...     1: [30, 25],
        ...     "City": ["New York", "Los Angeles"]
        ... }
        >>> CSVFile.validate(column_map_data_invalid)
        Traceback (most recent call last):
            ...
        ValueError: Column-maps must have all string keys; got 1 (int)

    (2) Have all column values be lists of entries

        >>> column_map_data_invalid = {
        ...     "Name": ["Alice Smith", "Bob Jones, Jr."],
        ...     "Age": (30, 25),
        ...     "City": ["New York", "Los Angeles"]
        ... }
        >>> CSVFile.validate(column_map_data_invalid)
        Traceback (most recent call last):
            ...
        ValueError: Column-maps must have all list values; got cols Age (tuple)

    and (3) have all column values be lists of the same length:

        >>> column_map_data_invalid = {
        ...     "Name": ["Alice Smith", "Bob Jones, Jr."],
        ...     "Age": [30, 25, 40],
        ...     "City": ["New York", "Los Angeles"]
        ... }
        >>> CSVFile.validate(column_map_data_invalid)
        Traceback (most recent call last):
            ...
        ValueError: Column-maps must have all lists of the same length 2; got Age (3)

    Another accepted format is a list of rows mapping column name to row value:

        >>> list_rowmap_data = [
        ...     {"Name": "Alice", "Age": 30, "City": "New York"},
        ...     {"Name": "Bob", "Age": 25, "City": "Los Angeles"}
        ... ]
        >>> with tempfile.NamedTemporaryFile() as tmp_file:
        ...     CSVFile.write(Path(tmp_file.name), list_rowmap_data)
        ...     print(Path(tmp_file.name).read_text().strip())
        Name,Age,City
        Alice,30,New York
        Bob,25,Los Angeles

    In this format, we must have all rows have the same set of keys:

        >>> list_rowmap_data_invalid = [
        ...     {"Name": "Alice", "Age": 30, "City": "New York"},
        ...     {"Name": "Bob", "City": "Los Angeles", "Name2": "Bob2"},
        ... ]
        >>> CSVFile.validate(list_rowmap_data_invalid)
        Traceback (most recent call last):
            ...
        ValueError: Row-maps must be consistent; got
            Row 1 has extra keys ['Name2'], missing keys ['Age']

    Finally, we can also pass a list of rows with the first row being the header:

        >>> list_rows_data = [
        ...     ["Name", "Age", "City"],
        ...     ["Alice", 30, "New York"],
        ...     ["Bob", 25, "Los Angeles"]
        ... ]
        >>> with tempfile.NamedTemporaryFile() as tmp_file:
        ...     CSVFile.write(Path(tmp_file.name), list_rows_data)
        ...     print(Path(tmp_file.name).read_text().strip())
        Name,Age,City
        Alice,30,New York
        Bob,25,Los Angeles

    In this format, we must have the first row be a list of strings and all subsequent rows be lists of the
    same length:

        >>> list_rows_data_invalid = [
        ...     ["Name", "Age", 3],
        ...     ["Alice", 30, "New York"],
        ...     ["Bob", 25, "Los Angeles"]
        ... ]
        >>> CSVFile.validate(list_rows_data_invalid)
        Traceback (most recent call last):
            ...
        ValueError: A list of lines must have the first row as str headers; got ['Name', 'Age', 3]
        >>> list_rows_data_invalid = [
        ...     ["Name", "Age", "City"],
        ...     ["Alice", 30, "New York", 32],
        ...     ["Bob", 25, "Los Angeles"]
        ... ]
        >>> CSVFile.validate(list_rows_data_invalid)
        Traceback (most recent call last):
            ...
        ValueError: Rows must be consistent; got
            Row 0 has 4 columns; expected 3

    In any format, if the data is empty, it will yield an empty CSV file:
        >>> CSVFile._parse("")
        ''
        >>> CSVFile._parse({})
        ''
        >>> CSVFile._parse([])
        ''

    If the data is in none of these formats, it will not be accepted:

        >>> CSVFile.validate(123)
        Traceback (most recent call last):
            ...
        TypeError: Contents must be a string, dict, or list; got <class 'int'>
    """

    extension: ClassVar[str] = ".csv"
    separator: ClassVar[str] = ","

    @classmethod
    def validate(cls, contents: Any):
        cls._parse(contents)

    @classmethod
    def _parse_str(cls, contents: str) -> str:
        """Validates a string is a valid CSV file contents and returns it.

        Also strips leading and trailing whitespace from each line.
        """

        contents = "\n".join(line.strip() for line in contents.splitlines())

        data = csv.DictReader(contents.strip().splitlines(), delimiter=cls.separator, restkey="err")

        bad_rows = []
        for i, row in enumerate(data):
            if row.get("err", None) is not None:
                bad_rows.append(f"Row {i} has extra columns; got '{cls.separator.join(row['err'])}'")

        if bad_rows:
            bad_rows_str = "\n".join(bad_rows)
            raise ValueError(f"A string CSV can't have inconsistent fields in rows; got\n{bad_rows_str}")
        return contents.strip()

    @classmethod
    def __dict_rows_to_str(cls, fieldnames: list[str], rows: list[dict]) -> str:
        str_io = io.StringIO()
        writer = csv.DictWriter(str_io, fieldnames=fieldnames, delimiter=cls.separator)

        writer.writeheader()
        for row in rows:
            writer.writerow(row)

        return str_io.getvalue()

    @classmethod
    def _parse_dict(cls, contents: dict[str, list[Any]]) -> str:
        """Parses a dictionary of column names to column values into a CSV string."""

        bad_keys = [f"{k} ({type(k).__name__})" for k in contents if not isinstance(k, str)]
        if bad_keys:
            raise ValueError(f"Column-maps must have all string keys; got {', '.join(bad_keys)}")

        bad_keys = [f"{k} ({type(v).__name__})" for k, v in contents.items() if not isinstance(v, list)]
        if bad_keys:
            raise ValueError(f"Column-maps must have all list values; got cols {', '.join(bad_keys)}")

        N = len(next(iter(contents.values())))
        bad_keys = [f"{k} ({len(v)})" for k, v in contents.items() if len(v) != N]
        if bad_keys:
            bad_keys_str = ", ".join(bad_keys)
            raise ValueError(f"Column-maps must have all lists of the same length {N}; got {bad_keys_str}")

        fieldnames = list(contents.keys())
        rows = [dict(zip(fieldnames, row, strict=False)) for row in zip(*contents.values(), strict=False)]
        return cls.__dict_rows_to_str(fieldnames, rows)

    @classmethod
    def _parse_list_rows(cls, contents: list[dict[str, Any]]) -> str:
        """Parses a list of rows (as dictionaries) into a CSV string."""

        bad_keys = [k for k in contents[0] if not isinstance(k, str)]
        if bad_keys:
            raise ValueError(f"Column-maps must have all string keys; got {bad_keys}")

        fieldnames = list(contents[0].keys())

        bad_rows = []
        for i, row in enumerate(contents):
            missing_keys = set(fieldnames) - set(row.keys())
            extra_keys = set(row.keys()) - set(fieldnames)

            err_parts = []
            if extra_keys:
                err_parts.append(f"extra keys {sorted(extra_keys)}")
            if missing_keys:
                err_parts.append(f"missing keys {sorted(missing_keys)}")

            if err_parts:
                bad_rows.append(f"Row {i} has {', '.join(err_parts)}")

        if bad_rows:
            bad_rows_str = "\n".join(bad_rows)
            raise ValueError(f"Row-maps must be consistent; got\n{bad_rows_str}")

        return cls.__dict_rows_to_str(fieldnames, contents)

    @classmethod
    def _parse_list_lines(cls, contents: list[list[Any]]) -> str:
        """Parses a list of rows (as lists) into a CSV string, with the first row being the header."""

        fieldnames = contents[0]
        if not all(isinstance(item, str) for item in fieldnames):
            raise ValueError(f"A list of lines must have the first row as str headers; got {fieldnames}")

        N_cols = len(fieldnames)

        bad_rows = []
        rows_as_dicts = []
        for i, row in enumerate(contents[1:]):
            if not isinstance(row, list):
                bad_rows.append(f"Row {i} is not a list; got {type(row)}")
            if len(row) != N_cols:
                bad_rows.append(f"Row {i} has {len(row)} columns; expected {N_cols}")
            rows_as_dicts.append(dict(zip(fieldnames, row, strict=False)))

        if bad_rows:
            bad_rows_str = "\n".join(bad_rows)
            raise ValueError(f"Rows must be consistent; got\n{bad_rows_str}")

        return cls.__dict_rows_to_str(fieldnames, rows_as_dicts)

    @classmethod
    def _parse(cls, contents: Any) -> str:
        match contents:
            case str():
                return cls._parse_str(contents)
            case dict():
                return cls._parse_dict(contents) if contents else ""
            case list() if all(isinstance(item, dict) for item in contents):
                return cls._parse_list_rows(contents) if contents else ""
            case list() if all(isinstance(item, list) for item in contents):
                return cls._parse_list_lines(contents) if contents else ""
            case _:
                raise TypeError(f"Contents must be a string, dict, or list; got {type(contents)}")

    @classmethod
    def write(cls, file_path: Path, contents: Any) -> None:
        file_path.write_text(cls._parse(contents))
