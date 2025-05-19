from __future__ import annotations

import logging
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from yaml import load

from .file_matchers import FILE_TYPE_MATCHER

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

logger = logging.getLogger(__name__)

DISK_CONTENTS_T = str | Path | dict | list


@dataclass
class File:
    rel_path: Path
    contents: Any

    def write(
        self,
        root_dir: Path,
        do_overwrite: bool = False,
        use_txt_on_unk_str_files: bool = True,
    ):
        """Write the file to the specified directory."""

        file_path = root_dir / self.rel_path
        if file_path.exists():
            if not do_overwrite:
                raise FileExistsError(f"File already exists: {file_path}")
            elif file_path.is_dir():
                raise IsADirectoryError(f"Path exists and is a directory: {file_path}")
            else:
                file_path.unlink()

        file_path.parent.mkdir(parents=True, exist_ok=True)

        if self.contents is None:
            file_path.touch()
            return

        try:
            file_type = FILE_TYPE_MATCHER(self.rel_path)
        except ValueError:
            if isinstance(self.contents, str) and use_txt_on_unk_str_files:
                file_type = FILE_TYPE_MATCHER(".txt")
            else:
                raise

        try:
            file_type.validate(self.contents)
        except Exception as e:
            raise ValueError(f"Contents for {file_path} fail validation under {file_type.__name__}") from e

        file_type.write(file_path, self.contents)


@dataclass
class Directory:
    rel_path: Path
    contents: list[File | Directory]

    def write(self, root_dir: Path, **kwargs):
        """Write the directory and its contents to the specified directory."""

        new_root = root_dir / self.rel_path
        if new_root.exists() and new_root.is_file():
            raise NotADirectoryError(f"Path exists and is a file: {new_root}")

        for item in self.contents:
            item.write(new_root, **kwargs)


class YamlDisk:
    """A class to represent a collection of files in a root directory in a YAML or YAML-derived format.

    This class is a context manager and a functor, and can be used in either mode. It preserves no state
    beyond that required for context management. The singleton object released below should generally be used,
    rather than creating new instances.

    If this package is installed as a plugin, it will automatically be available as a doctest fixture.
    """

    _temp_dir: tempfile.TemporaryDirectory | None
    _FILENAME_REGEX: ClassVar[re.Pattern] = re.compile(r".*\.(yaml|yml)$")
    _USE_TXT_ON_UNK_STR_FILES: ClassVar[bool] = True

    def __init__(self):
        self._temp_dir = None

    def __enter__(self):
        # Create temporary directory
        self._temp_dir = tempfile.TemporaryDirectory()
        return self(self.disk_contents, root_dir=Path(self._temp_dir.name), **self._write_kwargs)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up temporary directory
        self._temp_dir.cleanup()

    def __call__(
        self,
        disk_contents: DISK_CONTENTS_T,
        root_dir: str | Path | None = None,
        do_overwrite: bool = False,
        **kwargs,
    ) -> Path | YamlDisk:
        if root_dir is None:
            # Here, we're just preparing for context manager mode -- not actually writing anything.
            self.disk_contents = disk_contents
            self._write_kwargs = kwargs
            return self

        match root_dir:
            case str():
                root_dir = Path(root_dir)
            case Path():
                pass
            case _:
                raise TypeError(f"root_dir must be a string or Path, got {type(root_dir)}")

        if not root_dir.exists():
            raise FileNotFoundError(f"root_dir does not exist: {root_dir}")
        elif not root_dir.is_dir():
            raise NotADirectoryError(f"root_dir is not a directory: {root_dir}")

        parsed_contents = self._parse(disk_contents)
        self._write(parsed_contents, root_dir, do_overwrite=do_overwrite, **kwargs)
        return root_dir

    @classmethod
    def _is_yaml_file(cls, path: str) -> bool:
        """Check if the given string represents a YAML file."""

        if not isinstance(path, str):
            raise TypeError(f"Expected a string, got {type(path)}")

        return cls._FILENAME_REGEX.match(path) is not None

    @classmethod
    def _read_yaml_file(cls, yaml_fp: Path) -> dict | list:
        """Read a YAML file and return its contents."""

        if not yaml_fp.is_file():
            raise FileNotFoundError(f"File not found: {yaml_fp}")
        return cls._read_yaml_str(yaml_fp.read_text())

    @classmethod
    def _read_yaml_str(cls, yaml_str: str) -> dict | list:
        """Load a YAML string and return its contents."""

        return load(yaml_str, Loader=Loader)

    @classmethod
    def _parse_yaml_contents(cls, yaml_contents: dict | list) -> list[File | Directory]:
        """Parse the YAML contents and return a list of File or Directory objects."""

        match yaml_contents:
            case dict() as yaml_dict:
                yaml_list = [({k: v} if v else k) for k, v in yaml_dict.items()]
            case list():
                yaml_list = yaml_contents
            case _:
                raise TypeError(f"YAML contents must be a dictionary or list; got {type(yaml_contents)}")

        parsed_contents = []
        for item in yaml_list:
            match item:
                case str() as dir_name if item.endswith("/"):
                    parsed_contents.append(Directory(rel_path=Path(dir_name), contents=[]))
                case str() as file_name:
                    parsed_contents.append(File(rel_path=Path(file_name), contents=None))
                case dict() if len(item) == 1 and isinstance(next(iter(item.keys())), str):
                    raw_name = next(iter(item.keys()))
                    contents = item[raw_name]

                    name = Path(raw_name)

                    is_dir_name = raw_name.endswith("/") or name.suffix == ""

                    if is_dir_name:
                        nested_contents = cls._parse_yaml_contents(contents)
                        parsed_contents.append(Directory(rel_path=name, contents=nested_contents))
                    else:
                        parsed_contents.append(File(rel_path=name, contents=contents))

                case dict():
                    raise ValueError(f"Invalid format: {item}. Expected a single key (str) - value pair.")
                case _:
                    raise TypeError(f"Invalid item type: {type(item)}. Expected str or dict.")

        return parsed_contents

    @classmethod
    def _parse(cls, disk_contents: DISK_CONTENTS_T) -> list[File | Directory]:
        match disk_contents:
            case str() as yaml_fp_str if cls._is_yaml_file(yaml_fp_str):
                logging.debug(f"Inferring passed string {yaml_fp_str} is a file path")
                yaml_contents = cls._read_yaml_file(Path(yaml_fp_str))
            case Path() as yaml_fp:
                yaml_contents = cls._read_yaml_file(yaml_fp)
            case str() as yaml_str:
                yaml_contents = cls._read_yaml_str(yaml_str)
            case dict() | list():
                yaml_contents = disk_contents
            case _:
                raise TypeError(
                    f"disk_contents must be a string, Path, dict, or list; got {type(disk_contents)}"
                )

        return cls._parse_yaml_contents(yaml_contents)

    @classmethod
    def _write(
        cls,
        parsed_contents: list[File | Directory],
        root_dir: Path,
        do_overwrite: bool = False,
        **kwargs,
    ):
        base = Directory(rel_path=Path(), contents=parsed_contents)

        if "use_txt_on_unk_str_files" not in kwargs:
            kwargs["use_txt_on_unk_str_files"] = cls._USE_TXT_ON_UNK_STR_FILES

        base.write(root_dir, do_overwrite=do_overwrite, **kwargs)


yaml_disk = YamlDisk()
