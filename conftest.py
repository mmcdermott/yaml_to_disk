"""Test set-up and fixtures code."""

import tempfile
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture(autouse=True)
def __setup_doctest_namespace(doctest_namespace: dict[str, Any]):
    doctest_namespace.update({"tempfile": tempfile, "Path": Path})
