import importlib.metadata
import logging
from collections import defaultdict
from pathlib import Path

from .file_types.base import FileType

logger = logging.getLogger(__name__)


class FileTypeMatcher:
    """A class to match file types based on their extensions.

    This class checks the python entry points to identify all registered file types and loads them, then
    dynamically matches files specified via getitem to appropriate file type.

    The singleton :data:`FILE_TYPE_MATCHER` is constructed from the installed entry points and can be
    called with either an extension string or a :class:`pathlib.Path`:

        >>> from yaml_to_disk.file_matchers import FILE_TYPE_MATCHER
        >>> FILE_TYPE_MATCHER(".json").__name__
        'JSONFile'
        >>> FILE_TYPE_MATCHER(Path("foo.csv")).__name__
        'CSVFile'

    ``YAMLFile`` registers both ``.yaml`` and ``.yml``, so either resolves:

        >>> FILE_TYPE_MATCHER(Path("foo.yml")).__name__
        'YAMLFile'

    Extensions not claimed by any registered file type raise ``ValueError``:

        >>> FILE_TYPE_MATCHER(".unknown")
        Traceback (most recent call last):
            ...
        ValueError: No file type found for .unknown

    Keys that are neither a string nor a :class:`pathlib.Path` raise ``TypeError``:

        >>> FILE_TYPE_MATCHER(123)
        Traceback (most recent call last):
            ...
        TypeError: Key must be a string or Path; got <class 'int'>
    """

    def __init__(self):
        eps = importlib.metadata.entry_points(group="yaml_to_disk.file_types")

        file_types = defaultdict(list)

        for name in eps.names:
            try:
                file_type = eps[name].load()
            except Exception as e:
                raise ImportError(f"Failed to load entry point {name}") from e

            if not issubclass(file_type, FileType):
                raise TypeError(f"Entry point {name} does not subclass FileType")
            if file_type.extension is None:
                raise ValueError(f"FileType {name} has no extension defined")
            if isinstance(file_type.extension, set | frozenset):
                for ext in file_type.extension:
                    file_types[ext].append(file_type)
            else:
                file_types[file_type.extension].append(file_type)

        err_lines = [f"{ext}: {types}" for ext, types in file_types.items() if len(types) > 1]
        if err_lines:
            raise ValueError(
                f"Multiple file types registered for the same extension:\n{', '.join(err_lines)}"
            )

        self.file_types = {k: v[0] for k, v in file_types.items()}

    def __call__(self, key: str | Path) -> FileType:
        match key:
            case Path() as fp:
                key_suffix = "".join(fp.suffixes)
                key_path = fp
            case str() as suffix:
                key_suffix = suffix
                key_path = Path(suffix)
            case _:
                raise TypeError(f"Key must be a string or Path; got {type(key)}")

        if key_suffix in self.file_types:
            return self.file_types[key_suffix]

        matching_types = []
        for ext, file_type in self.file_types.items():
            if file_type.matches(key_path):
                logger.debug(f"File type {file_type.__name__} matches {key_path} though ext {ext} doesn't")
                matching_types.append(file_type)

        if len(matching_types) == 0:
            raise ValueError(f"No file type found for {key_suffix}")
        elif len(matching_types) == 1:
            return matching_types[0]
        else:
            raise ValueError(
                f"Multiple file types found for {key_suffix}: "
                f"{', '.join([type.__name__ for type in matching_types])}"
            )


FILE_TYPE_MATCHER = FileTypeMatcher()
