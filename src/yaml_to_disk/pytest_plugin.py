from typing import Any

import pytest


@pytest.fixture(autouse=True)
def ___yaml_to_disk_add_doctest(doctest_namespace: dict[str, Any]) -> None:
    from .yaml_to_disk import yaml_disk

    doctest_namespace.update({"yaml_disk": yaml_disk})
