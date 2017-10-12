import json
import logging

from enum import Enum
from errors import ContentTypeError, InvalidKeyIdError, UnknownRoleError
from mitmproxy.http import HTTPFlow
from my_types import Contains, Json, Readable, canonical
from typing import Optional, Sequence as Seq

log = logging.getLogger(__name__)


class Metadata(object):
    """Parsed TUF metadata."""
    signatures: Seq['Signature']
    role: 'Role'
    expires: str
    version: int
    targets: Seq['Target']
    extra: Json

    def __init__(self, meta: Json) -> None:
        Contains(meta)("signatures", "signed")
        self.signatures = [Signature(sig) for sig in meta.pop("signatures")]

        signed = meta.pop("signed")
        Contains(signed)("_type", "expires", "version")
        self.role = Role.parse(signed.pop("_type"))
        self.expires = signed.pop("expires")
        self.version = signed.pop("version")

        if self.role is Role.Targets:
            Contains(signed)("targets")
            self.targets = [Target(path, meta) for path, meta in signed.pop("targets").items()]

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
        """Convert this instance to a JSON bytes representation."""
        return canonical(self._encode())

    def _encode(self) -> Json:
        out: Json = {
            "signatures": [sig._encode() for sig in self.signatures],
            "signed": {
                "_type": self.role.name,
                "expires": self.expires,
                "version": self.version,
            }
        }

        if self.role is Role.Targets:
            out["signed"]["targets"] = {target.filepath: target._encode() for target in self.targets}

        out["signed"].update(self.extra)
        return out


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


class KeyId(str):
    """A valid KeyId of 64 hex digits"""
    def __new__(cls, keyid: str) -> str:
        try:
            int(keyid, 16)
        except ValueError:
            raise InvalidKeyIdError(keyid)
        if len(keyid) != 64:
            raise InvalidKeyIdError(keyid)
        return keyid


class Signature(object):
    """A signature of metadata."""
    keyid: KeyId
    sig: str
    extra: Json

    def __init__(self, meta: Json) -> None:
        Contains(meta)("keyid", "sig")
        self.keyid = KeyId(meta.pop("keyid"))
        self.sig = meta.pop("sig")
        self.extra = meta

    def _encode(self) -> Json:
        out: Json = {"keyid": self.keyid, "sig": self.sig}
        out.update(self.extra)
        return out


class Target(object):
    """An installation target."""
    filepath: str
    length: int
    hashes: Json
    custom: Optional[Json]
    extra: Json

    def __init__(self, filepath: str, meta: Json) -> None:
        Contains(meta)("length", "hashes")
        self.filepath = filepath
        self.length = meta.pop("length")
        self.hashes = meta.pop("hashes")
        self.custom = meta.pop("custom", None)
        self.extra = meta

    def _encode(self) -> Json:
        out: Json = {"length": self.length, "hashes": self.hashes}
        if self.custom:
            out["custom"] = self.custom
        out.update(self.extra)
        return out
