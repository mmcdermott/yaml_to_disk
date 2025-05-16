import pickle
from pathlib import Path
from typing import Any, ClassVar

from .base import FileType


class PickleFile(FileType):
    """A class for validating and writing JSON files.

    Examples:
        >>> with tempfile.NamedTemporaryFile() as tmp_file:
        ...     fp = Path(tmp_file.name)
        ...     PickleFile.write(fp, {"key": "value"})
        ...     with open(fp, 'rb') as f:
        ...         print(pickle.load(f))
        {'key': 'value'}

    `PickleFile` can support any type that can be pickled:

        >>> PickleFile.validate("Hello!")
        >>> PickleFile.validate(123)
        >>> PickleFile.validate({"key": "value"})
        >>> PickleFile.validate([1, 2, 3])
        >>> PickleFile.validate({1, 2, 3})
        >>> PickleFile.validate(lambda x: x)
        Traceback (most recent call last):
            ...
        _pickle.PicklingError: Can't pickle <function <lambda> at ...>: ...
    """

    extension: ClassVar[str] = ".pkl"

    @classmethod
    def validate(cls, contents: Any):
        pickle.dumps(contents)

    @classmethod
    def write(cls, file_path: Path, contents: Any) -> None:
        with open(file_path, "wb") as f:
            pickle.dump(contents, f)
