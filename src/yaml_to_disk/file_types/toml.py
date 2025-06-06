from pathlib import Path
from typing import Any, ClassVar

try:
    import tomli_w
except Exception:  # pragma: no cover - tomli_w is optional
    tomli_w = None

from .base import FileType


class TOMLFile(FileType):
    """A class for validating and writing TOML files.

    Examples:
        >>> with tempfile.NamedTemporaryFile() as tmp_file:  # doctest: +SKIP
        ...     fp = Path(tmp_file.name)
        ...     TOMLFile.validate({"key": "value"})  # doctest: +SKIP
        ...     TOMLFile.write(fp, {"key": "value"})  # doctest: +SKIP
        ...     fp.read_text().strip()  # doctest: +SKIP
        'key = "value"'

    Invalid inputs raise an ``AttributeError``:

        >>> TOMLFile.validate({1, 2})  # doctest: +SKIP
        Traceback (most recent call last):
        ...
        AttributeError: 'set' object has no attribute 'items'
    """

    extension: ClassVar[str] = ".toml"

    @classmethod
    def validate(cls, contents: Any):
        if tomli_w is None:
            raise ImportError("tomli-w is required to use TOMLFile")
        tomli_w.dumps(contents)

    @classmethod
    def write(cls, file_path: Path, contents: Any) -> None:
        if tomli_w is None:
            raise ImportError("tomli-w is required to use TOMLFile")
        file_path.write_text(tomli_w.dumps(contents))
