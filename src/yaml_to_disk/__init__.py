from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .yaml_to_disk import YamlDisk, yaml_disk

__all__ = ["YamlDisk", "yaml_disk"]


def __getattr__(name: str):
    if name in __all__:
        from .yaml_to_disk import YamlDisk, yaml_disk

        globals().update({"YamlDisk": YamlDisk, "yaml_disk": yaml_disk})
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
