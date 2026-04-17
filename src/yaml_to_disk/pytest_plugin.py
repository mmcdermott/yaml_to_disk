from typing import Any

import pytest


@pytest.fixture(autouse=True, scope="session")
def ___yaml_to_disk_add_doctest(doctest_namespace: dict[str, Any]) -> None:
    from .yaml_to_disk import yaml_disk

    doctest_namespace["yaml_disk"] = yaml_disk
