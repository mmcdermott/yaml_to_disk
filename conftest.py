"""Test set-up and fixtures code."""

import importlib
import tempfile
from pathlib import Path
from typing import Any

import pytest

import yaml_to_disk
import yaml_to_disk.file_matchers
import yaml_to_disk.file_types
import yaml_to_disk.file_types.base
import yaml_to_disk.file_types.csv
import yaml_to_disk.file_types.json
import yaml_to_disk.file_types.pkl
import yaml_to_disk.file_types.txt
import yaml_to_disk.file_types.yaml
import yaml_to_disk.pytest_plugin
import yaml_to_disk.yaml_to_disk

importlib.reload(yaml_to_disk)
importlib.reload(yaml_to_disk.pytest_plugin)
importlib.reload(yaml_to_disk.yaml_to_disk)
importlib.reload(yaml_to_disk.file_matchers)
importlib.reload(yaml_to_disk.file_types)
importlib.reload(yaml_to_disk.file_types.base)
importlib.reload(yaml_to_disk.file_types.csv)
importlib.reload(yaml_to_disk.file_types.json)
importlib.reload(yaml_to_disk.file_types.yaml)
importlib.reload(yaml_to_disk.file_types.pkl)
importlib.reload(yaml_to_disk.file_types.txt)


@pytest.fixture(autouse=True)
def __setup_doctest_namespace(doctest_namespace: dict[str, Any]):
    doctest_namespace.update({"tempfile": tempfile, "Path": Path})
