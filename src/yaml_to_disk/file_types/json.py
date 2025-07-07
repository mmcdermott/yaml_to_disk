import json
from pathlib import Path
from typing import Any, ClassVar

from .base import FileType


class JSONFile(FileType):
    """A class for validating and writing JSON files.

    Examples:
        >>> with tempfile.NamedTemporaryFile() as tmp_file:
        ...     fp = Path(tmp_file.name)
        ...     JSONFile.write(fp, {"key": "value"})
        ...     fp.read_text()
        '{"key": "value"}'

    `JSONFile` can accept any type that is JSON serializable.

        >>> JSONFile.validate("Hello!")
        >>> JSONFile.validate(123)
        >>> JSONFile.validate({"key": "value"})
        >>> JSONFile.validate([1, 2, 3])
        >>> JSONFile.validate({1, 2, 3})
        Traceback (most recent call last):
            ...
        TypeError: Object of type set is not JSON serializable

    ``JSONFile.matches`` can detect ``.json`` file names:

        >>> JSONFile.matches(Path('foo.json'))
        True
        >>> JSONFile.matches(Path('foo.txt'))
        False
    """

    extension: ClassVar[str] = ".json"

    @classmethod
    def validate(cls, contents: Any):
        json.dumps(contents)

    @classmethod
    def write(cls, file_path: Path, contents: Any) -> None:
        file_path.write_text(json.dumps(contents))
