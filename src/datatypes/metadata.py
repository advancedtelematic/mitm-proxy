import json

from enum import Enum
from mitmproxy.http import HTTPFlow
from typing import Any, Dict, List

from .signature import Signature
from .targets import Target
from ..errors import ContentTypeError, UnknownRoleError
from ..utils import Readable, canonical, contains


class Role(Enum):
    """Valid TUF metadata roles."""
    Root: str = "root"
    Snapshot: str = "snapshot"
    Targets: str = "targets"
    Timestamp: str = "timestamp"

    @classmethod
    def parse(cls, name: str) -> 'Role':
        try:
            return cls(name.lower())
        except ValueError:
            raise UnknownRoleError(name)


class Metadata(object):
    """Parsed TUF metadata."""
    signatures: List[Signature]
    role: Role
    expires: str
    version: int
    targets: List[Target]
    extra: Dict[str, Any]

    def __init__(self, meta: Dict[str, Any]) -> None:
        contains(meta, "signatures", "signed")
        self.signatures = [Signature(sig) for sig in meta.pop("signatures")]

        signed = meta.pop("signed")
        contains(signed, "_type", "expires", "version")
        self.role = Role.parse(signed.pop("_type"))
        self.expires = signed.pop("expires")
        self.version = signed.pop("version")

        if self.role is Role.Targets:
            contains(signed, "targets")
            targets = signed.pop("targets")
            self.targets = [Target(path, meta) for path, meta in targets.items()]

        self.extra = signed

    @classmethod
    def from_flow(cls, flow: HTTPFlow) -> 'Metadata':
        """Convert the HTTPFlow into a new instance."""
        content_type = flow.response.headers.get('Content-Type')
        if content_type != "application/json":
            raise ContentTypeError("application/json", content_type)
        return cls.from_readable(flow.response.content)

    @classmethod
    def from_readable(cls, data: Readable) -> 'Metadata':
        """Parse the readable JSON data into a new instance."""
        return cls(json.loads(data))

    def to_json(self) -> str:
        """Convert the instance back to JSON."""
        return canonical(self._encode())

    def _encode(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "signatures": [sig._encode() for sig in self.signatures],
            "signed": {
                "_type": self.role.name,
                "expires": self.expires,
                "version": self.version,
            }
        }

        if self.role is Role.Targets:
            out["signed"]["targets"] = {
                target.filepath: target._encode() for target in self.targets
            }

        out["signed"].update(self.extra)
        return out
