from typing import Any, Dict, List, Optional

from ..utils import Encoded, contains


class Target(object):
    """An installation target."""
    filepath: str
    length: int
    hashes: Dict[str, Any]
    custom: Optional[Dict[str, Any]]
    extra: Dict[str, Any]

    def __init__(self, filepath: str, meta: Dict[str, Any]) -> None:
        contains(meta, "length", "hashes")
        self.filepath = filepath
        self.length = meta.pop("length")
        self.hashes = meta.pop("hashes")
        self.custom = meta.pop("custom", None)
        self.extra = meta

    def _encode(self) -> Encoded:
        out: Dict[str, Any] = {"length": self.length, "hashes": self.hashes}
        if self.custom:
            out["custom"] = self.custom
        out.update(self.extra)
        return out


class Targets(object):
    """Methods for operating on a collection of targets."""
    items: List[Target]

    def __init__(self, targets: List[Target]) -> None:
        self.items = targets

    @classmethod
    def from_dict(cls, obj: Dict[str, Any]) -> 'Targets':
        return cls([Target(path, meta) for path, meta in obj.items()])

    def _encode(self) -> Encoded:
        return {target.filepath: target._encode() for target in self.items}
