import abc
from pathlib import Path
from typing import Any, ClassVar


class FileType(abc.ABC):
    """Abstract base class for file types."""

    extension: ClassVar[str | frozenset[str] | None] = None

    def __init__(self):
        raise TypeError(f"{self.__class__.__name__} should not be instantiated")

    @classmethod
    def matches(cls, file_path: Path) -> bool:
        """Check if the file path matches the expected file type.

        Args:
            file_path: Path to the file.

        Returns:
            True if the file path matches the expected file type, False otherwise.
        """

        matching_extensions = cls.extension if isinstance(cls.extension, set | frozenset) else {cls.extension}
        return any("".join(file_path.suffixes) == ext for ext in matching_extensions)

    @classmethod
    @abc.abstractmethod
    def validate(cls, contents: Any) -> None:
        """Validate the contents of a file.

        Args:
            contents: Content to validate.

        Raises:
            Exception: If the contents are invalid.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def write(cls, file_path: Path, contents: Any) -> None:
        """Write content to a file.

        Args:
            file_path: Path to the file.
            contents: Content to write to the file.
        """
        pass
