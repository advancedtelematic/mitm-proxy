import json
import logging

from errors import ContentTypeError, MissingFieldError, UnknownRoleError
from mitmproxy.http import HTTPFlow
from my_types import Json, Readable
from typing import Sequence as Seq

log = logging.getLogger(__name__)


# Valid TUF metadata roles.
Roles = ["root", "snapshot", "targets", "timestamp"]


def get_flow_metadata(flow: HTTPFlow) -> Json:
    """Convert the HTTPFlow into valid signed TUF metadata."""
    content_type = flow.response.headers.get('Content-Type')
    if content_type != "application/json":
        raise ContentTypeError("application/json", content_type)
    return _read_metadata(flow.response.content)


def _read_metadata(data: Readable) -> Json:
    """Parse the JSON content as TUF metadata."""
    meta: Json = json.loads(data)
    _verify_metadata(meta)
    return meta

def _verify_metadata(meta: Json) -> None:
    """Verify the metadata is of the expected TUF format."""
    _has_fields(meta, ["signatures", "signed"])

    sigs: Seq[Json] = meta["signatures"]
    for sig in sigs:
        _has_fields(sig, ["keyid", "sig"])

    signed: Json = meta["signed"]
    _has_fields(signed, ["_type", "expires", "version"])

    role: str = signed["_type"]
    if role.lower() not in Roles:
        raise UnknownRoleError(signed["_type"])

def _has_fields(obj: Json, fields: Seq[str]) -> None:
    """Verify that each field exists in the object."""
    for field in fields:
        if field not in obj:
            raise MissingFieldError(repr(obj), field)
