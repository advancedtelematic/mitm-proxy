import json
import logging

from enum import Enum
from errors import ContentTypeError, InvalidKeyIdError, UnknownRoleError
from mitmproxy.http import HTTPFlow
from my_types import Json, Readable
from typing import Optional, Sequence as Seq

log = logging.getLogger(__name__)


class Metadata(object):
    """Parsed TUF metadata."""
    signatures: Seq['Signature']
    role: 'Role'
    expires: str
    version: int
    targets: Seq['Target']

    def __init__(self, meta: Json) -> None:
        Json(meta).contains("signatures", "signed")
        self.signatures = [Signature(sig) for sig in meta["signatures"]]

        signed = Json(meta["signed"])
        signed.contains("_type", "expires", "version")
        self.role = Role.parse(signed["_type"])
        self.expires = signed["expires"]
        self.version = signed["version"]

        if self.role is Role.Targets:
            signed.contains("targets")
            self.targets = [Target(path, meta) for path, meta in signed["targets"].items()]

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
    """A signature of RawMetadata's signed field."""
    keyid: KeyId
    sig: str

    def __init__(self, meta: Json) -> None:
        Json(meta).contains("keyid", "sig")
        self.keyid = KeyId(meta["keyid"])
        self.sig = meta["sig"]

class Target(object):
    """An installation target."""
    filepath: str
    length: int
    hashes: Json
    custom: Optional[Json]

    def __init__(self, filepath: str, meta: Json) -> None:
        Json(meta).contains("length", "hashes")
        self.filepath = filepath
        self.length = meta["length"]
        self.hashes = meta["hashes"]
        self.custom = meta.get("custom")
