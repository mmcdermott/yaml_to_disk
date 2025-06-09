from pathlib import Path
from typing import Any, ClassVar

from .base import FileType

tomli_w = None


def _load_tomli_w():
    """Lazily import ``tomli_w`` and cache the module."""
    global tomli_w
    if tomli_w is None:  # pragma: no cover - optional dependency
        try:
            import tomli_w as _tomli_w
        except Exception as e:  # pragma: no cover - optional dependency
            raise ImportError("tomli-w is required to use TOMLFile") from e

        tomli_w = _tomli_w
    return tomli_w


__doctest_requires__ = {"TOMLFile": ["tomli_w"]}


class TOMLFile(FileType):
    """Validate and write TOML files.

    Examples:
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
        toml_mod = _load_tomli_w()
        toml_mod.dumps(contents)

    @classmethod
    def write(cls, file_path: Path, contents: Any) -> None:
        toml_mod = _load_tomli_w()
        file_path.write_text(toml_mod.dumps(contents))
