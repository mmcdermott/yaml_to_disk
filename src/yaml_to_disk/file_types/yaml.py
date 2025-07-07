from pathlib import Path
from typing import Any, ClassVar

from yaml import dump

from .base import FileType

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper


class YAMLFile(FileType):
    """A class for validating and writing YAML files.

    Examples:
        >>> with tempfile.NamedTemporaryFile() as tmp_file:
        ...     fp = Path(tmp_file.name)
        ...     YAMLFile.write(fp, {"key": "value"})
        ...     print(fp.read_text().strip())
        key: value

    `YAMLFile` can accept a variety of data types, including lambda functions.

        >>> YAMLFile.validate("Hello!")
        >>> YAMLFile.validate(123)
        >>> YAMLFile.validate({"key": "value"})
        >>> YAMLFile.validate([1, 2, 3])
        >>> YAMLFile.validate({1, 2, 3})
        >>> YAMLFile.validate(lambda x: x)

    ``matches`` inspects the file suffix and accepts either ``.yaml`` or ``.yml``:

        >>> YAMLFile.matches(Path("foo.yaml"))
        True
        >>> YAMLFile.matches(Path("foo.yml"))
        True
        >>> YAMLFile.matches(Path("foo.txt"))
        False
    """

    extension: ClassVar[frozenset[str]] = frozenset({".yaml", ".yml"})

    @classmethod
    def validate(cls, contents: Any):
        dump(contents, Dumper=Dumper)

    @classmethod
    def write(cls, file_path: Path, contents: Any) -> None:
        file_path.write_text(dump(contents, Dumper=Dumper))
