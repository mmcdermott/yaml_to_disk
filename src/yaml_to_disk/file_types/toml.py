from pathlib import Path
from typing import Any, ClassVar

import tomli_w

from .base import FileType


class TOMLFile(FileType):
    """A class for validating and writing TOML files.

    Examples:
        >>> with tempfile.NamedTemporaryFile() as tmp_file:
        ...     fp = Path(tmp_file.name)
        ...     TOMLFile.validate({"key": "value"})
        ...     TOMLFile.write(fp, {"key": "value"})
        ...     fp.read_text().strip()
        'key = "value"'

    Invalid inputs raise an ``AttributeError``:

        >>> TOMLFile.validate({1, 2})
        Traceback (most recent call last):
        ...
        AttributeError: 'set' object has no attribute 'items'
    """

    extension: ClassVar[str] = ".toml"

    @classmethod
    def validate(cls, contents: Any):
        tomli_w.dumps(contents)

    @classmethod
    def write(cls, file_path: Path, contents: Any) -> None:
        file_path.write_text(tomli_w.dumps(contents))
