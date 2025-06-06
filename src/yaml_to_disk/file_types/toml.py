from pathlib import Path
from typing import Any, ClassVar

try:
    import tomli_w
except Exception:  # pragma: no cover - tomli_w is optional
    tomli_w = None

from .base import FileType

__doctest_requires__ = {"TOMLFile.*": ["tomli_w"]}


class TOMLFile(FileType):
    """Validate and write TOML files.

    Examples:
        >>> import pytest
        >>> _ = pytest.importorskip("tomli_w")
        >>> with tempfile.NamedTemporaryFile() as tmp_file:
        ...     fp = Path(tmp_file.name)
        ...     TOMLFile.validate({"key": "value"})
        ...     TOMLFile.write(fp, {"key": "value"})
        ...     fp.read_text().strip()
        'key = "value"'

        Invalid inputs raise ``AttributeError``:

        >>> TOMLFile.validate({1, 2})
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
