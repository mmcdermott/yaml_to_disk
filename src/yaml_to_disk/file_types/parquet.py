from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from ..tabular_utils import validate_column_map, validate_row_map_list
from .base import FileType

pa = None
pq = None


def _load_pyarrow():
    """Lazily import ``pyarrow`` and cache the modules."""
    global pa, pq
    if pa is None or pq is None:
        try:
            import pyarrow as _pa
            import pyarrow.parquet as _pq
        except Exception as e:
            raise ImportError("pyarrow is required to use ParquetFile") from e

        pa = _pa
        pq = _pq
    return pa, pq


__doctest_requires__ = {"ParquetFile": ["pyarrow"]}

if TYPE_CHECKING:  # pragma: no cover - for type hints
    from pathlib import Path


class ParquetFile(FileType):
    """Validate and write Parquet files.

    Examples:
        >>> import pyarrow as pa
        >>> import pyarrow.parquet as pq
        >>> col_map = {"a": [1, 2], "b": [3, 4]}
        >>> with tempfile.NamedTemporaryFile() as tmp_file:
        ...     fp = Path(tmp_file.name)
        ...     ParquetFile.write(fp, col_map)
        ...     pq.read_table(fp).to_pydict()
        {'a': [1, 2], 'b': [3, 4]}

        A list of row dicts is also accepted, with keys becoming column names:

        >>> rows = [{"x": 1, "y": 2}, {"x": 3, "y": 4}]
        >>> with tempfile.NamedTemporaryFile() as tmp_file:
        ...     fp = Path(tmp_file.name)
        ...     ParquetFile.write(fp, rows)
        ...     pq.read_table(fp).to_pydict()
        {'x': [1, 3], 'y': [2, 4]}

        Existing :class:`pyarrow.Table` instances can be written directly, and
        validated without writing:

        >>> table = pa.table(col_map)
        >>> ParquetFile.validate(table)
        >>> with tempfile.NamedTemporaryFile() as tmp_file:
        ...     fp = Path(tmp_file.name)
        ...     ParquetFile.write(fp, pa.table({"c": [10, 20]}))
        ...     pq.read_table(fp).to_pydict()
        {'c': [10, 20]}

        Row-map lists also work with ``validate``:

        >>> ParquetFile.validate([{"a": 1}, {"a": 2}])

        Empty inputs (dict or list) produce empty tables:

        >>> with tempfile.NamedTemporaryFile() as tmp_file:
        ...     fp = Path(tmp_file.name)
        ...     ParquetFile.write(fp, {})
        ...     pq.read_table(fp).to_pydict()
        {}
        >>> with tempfile.NamedTemporaryFile() as tmp_file:
        ...     fp = Path(tmp_file.name)
        ...     ParquetFile.write(fp, [])
        ...     pq.read_table(fp).to_pydict()
        {}

        Ragged column-maps raise ``ValueError``:

        >>> bad = {"a": [1, 2], "b": [3]}
        >>> ParquetFile.validate(bad)
        Traceback (most recent call last):
        ...
        ValueError: Column-maps must have all lists of the same length 2; got b (1)

        Unsupported input types raise ``TypeError``:

        >>> ParquetFile.validate("not valid")
        Traceback (most recent call last):
        ...
        TypeError: Contents must be a pyarrow.Table, dict of columns, or list of row dictionaries;
        got <class 'str'>

    ``ParquetFile.matches`` can detect ``.parquet`` file names:

        >>> ParquetFile.matches(Path('foo.parquet'))
        True
        >>> ParquetFile.matches(Path('foo.txt'))
        False
    """

    extension: ClassVar[str] = ".parquet"

    @classmethod
    def _parse(cls, contents: Any) -> pa.Table:
        """Validate and convert ``contents`` to a :class:`pyarrow.Table`."""

        pa_mod, _ = _load_pyarrow()

        match contents:
            case pa_mod.Table():
                return contents
            case dict():
                validate_column_map(contents)
                return pa_mod.table(contents) if contents else pa_mod.table({})
            case list() if all(isinstance(item, dict) for item in contents):
                fieldnames = validate_row_map_list(contents)
                columns = (
                    {field: [row[field] for row in contents] for field in fieldnames} if contents else {}
                )
                return pa_mod.table(columns)
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
        _, pq_mod = _load_pyarrow()
        pq_mod.write_table(cls._parse(contents), file_path)
