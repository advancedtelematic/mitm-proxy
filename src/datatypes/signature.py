from cytoolz.itertoolz import remove
from random import choice
from typing import Any, Dict, List

from ..errors import InvalidKeyIdError
from ..utils import contains


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
    """A signature of the TUF metadata `signed` section."""
    keyid: KeyId
    sig: str
    extra: Dict[str, Any]

    def __init__(self, obj: Dict[str, Any]) -> None:
        contains(obj, "keyid", "sig")
        self.keyid = KeyId(obj.pop("keyid"))
        self.sig = obj.pop("sig")
        self.extra = obj

    def _encode(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"keyid": self.keyid, "sig": self.sig}
        out.update(self.extra)
        return out


def remove_sig_by_key(sigs: List[Signature], key: KeyId) -> List[Signature]:
    """Return a new list with all matching keys removed."""
    return list(remove(lambda s: s.keyid == key, sigs))

def remove_random_sig(sigs: List[Signature]) -> List[Signature]:
    """Return a new list with a random KeyId removed."""
    return remove_sig_by_key(sigs, choice(sigs).keyid)
