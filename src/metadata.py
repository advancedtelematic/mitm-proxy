import json
import logging

from enum import Enum
from errors import ContentTypeError, InvalidKeyIdError, MissingFieldError, UnknownRoleError
from mitmproxy.http import HTTPFlow
from my_types import Json, Readable
from typing import Optional  # noqa: F401
from typing import Sequence as Seq, Type, TypeVar

log = logging.getLogger(__name__)


class Role(Enum):
    """Valid TUF metadata roles."""
    Root: str = "root"
    Snapshot: str = "snapshot"
    Targets: str = "targets"
    Timestamp: str = "timestamp"

def _parse_role(name: str) -> Role:
    for role in Role:
        if role.value == name.lower():
            return role
    raise UnknownRoleError(name)


class Target(object):
    """Parse TUF metadata for the Targets role."""
    filepath: str
    length: int
    hashes: Json
    custom: Optional[Json] = None

    def __init__(self, filepath: str, meta: Json) -> None:
        _has_fields(meta, ["hashes", "length"])
        self.filepath = filepath
        self.length = meta["length"]
        self.hashes = meta["hashes"]
        if "custom" in meta:
            self.custom = meta["custom"]


M = TypeVar('M', bound='Metadata')

class Metadata(object):
    signatures: Seq[Json]
    role: Role
    expires: str
    version: int
    targets: Seq[Target]

    def __init__(self, meta: Json) -> None:
        """Parse the TUF metadata into a new instance."""
        _has_fields(meta, ["signatures", "signed"])

        signatures: Seq[Json] = meta["signatures"]
        for sig in signatures:
            _has_fields(sig, ["keyid", "sig"])
            _valid_keyid(sig["keyid"])
        self.signatures = signatures

        signed: Json = meta["signed"]
        _has_fields(signed, ["_type", "expires", "version"])
        self.expires = signed["expires"]
        self.version = signed["version"]

        self.role = _parse_role(signed["_type"])
        if self.role is Role.Targets:
            _has_fields(signed, ["targets"])
            targets = signed["targets"].items()
            self.targets = [Target(filepath, meta) for filepath, meta in targets]

    @classmethod
    def from_flow(cls: Type[M], flow: HTTPFlow) -> M:
        """Convert the HTTPFlow into a new instance."""
        content_type = flow.response.headers.get('Content-Type')
        if content_type != "application/json":
            raise ContentTypeError("application/json", content_type)
        return cls.from_readable(flow.response.content)

    @classmethod
    def from_readable(cls: Type[M], data: Readable) -> M:
        """Parse the readable JSON data into a new instance."""
        return cls(json.loads(data))


def _has_fields(obj: Json, fields: Seq[str]) -> None:
    """Verify that each field exists in the object."""
    for field in fields:
        if field not in obj:
            raise MissingFieldError(repr(obj), field)

def _valid_keyid(keyid: str) -> None:
    """Verify the keyid is 64 hex digits"""
    if len(keyid) != 64:
        raise InvalidKeyIdError(keyid)
    try:
        int(keyid, 16)
    except ValueError:
        raise InvalidKeyIdError(keyid)
