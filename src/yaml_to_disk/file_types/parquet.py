from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except Exception:  # pragma: no cover - pyarrow is optional
    pa = None
    pq = None

from ..tabular_utils import validate_column_map, validate_row_map_list
from .base import FileType

__doctest_requires__ = {"ParquetFile.*": ["pyarrow"]}

if TYPE_CHECKING:  # pragma: no cover - for type hints
    from pathlib import Path


class ParquetFile(FileType):
    """Validate and write Parquet files.

    Examples:
        >>> import pytest
        >>> _ = pytest.importorskip("pyarrow")
        >>> col_map = {"a": [1, 2], "b": [3, 4]}
        >>> with tempfile.NamedTemporaryFile() as tmp_file:
        ...     fp = Path(tmp_file.name)
        ...     ParquetFile.write(fp, col_map)
        ...     pq.read_table(fp).to_pydict()
        {'a': [1, 2], 'b': [3, 4]}

        You can also pass an existing :class:`pyarrow.Table` directly:

        >>> table = pa.table(col_map)
        >>> ParquetFile.validate(table)

        Invalid inputs raise ``ValueError``:

        >>> bad = {"a": [1, 2], "b": [3]}
        >>> ParquetFile.validate(bad)
        Traceback (most recent call last):
        ...
        ValueError: Column-maps must have all lists of the same length 2; got b (1)
    """

    extension: ClassVar[str] = ".parquet"

    @classmethod
    def _parse(cls, contents: Any) -> pa.Table:
        """Validate and convert ``contents`` to a :class:`pyarrow.Table`."""

        if pa is None or pq is None:
            raise ImportError("pyarrow is required to use ParquetFile")

        match contents:
            case pa.Table():
                return contents
            case dict():
                validate_column_map(contents)
                return pa.table(contents) if contents else pa.table({})
            case list() if all(isinstance(item, dict) for item in contents):
                fieldnames = validate_row_map_list(contents)
                columns = (
                    {field: [row[field] for row in contents] for field in fieldnames} if contents else {}
                )
                return pa.table(columns)
            case _:
                raise TypeError(
                    "Contents must be a pyarrow.Table, dict of columns, or list of row dictionaries; "
                    f"got {type(contents)}"
                )

    @classmethod
    def validate(cls, contents: Any) -> None:
        cls._parse(contents)

    @classmethod
    def write(cls, file_path: Path, contents: Any) -> None:
        pq.write_table(cls._parse(contents), file_path)
