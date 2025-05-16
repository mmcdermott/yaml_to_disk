from pathlib import Path
from typing import Any, ClassVar

from .base import FileType


class TextFile(FileType):
    """A class for validating and writing text files.

    Examples:
        >>> with tempfile.NamedTemporaryFile() as tmp_file:
        ...     fp = Path(tmp_file.name)
        ...     TextFile.write(fp, "Hello, World!")
        ...     fp.read_text()
        'Hello, World!'

    `TextFile` can only accept string contents.

        >>> TextFile.validate("Hello!")
        >>> TextFile.validate(123)
        Traceback (most recent call last):
            ...
        ValueError: Contents must be a string; got <class 'int'>
    """

    extension: ClassVar[str] = ".txt"

    @classmethod
    def validate(cls, contents: Any):
        if not isinstance(contents, str):
            raise ValueError(f"Contents must be a string; got {type(contents)}")

    @classmethod
    def write(cls, file_path: Path, contents: Any) -> None:
        file_path.write_text(contents)
