import os

from base64 import b64decode, b64encode
from binascii import hexlify
from cytoolz import concat, groupby, remove
from random import choice
from rsa import PublicKey
from typing import Any, Dict, List, Optional

from ..errors import InvalidKeyIdError
from ..utils import Encoded, contains


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

    @staticmethod
    def from_pub(pub: PublicKey) -> 'KeyId':
        # FIXME: ATS-specific keyid parsing
        return KeyId("0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")

    @staticmethod
    def random() -> 'KeyId':
        return KeyId(hexlify(os.urandom(32)).decode("UTF-8"))


class Signature(object):
    """A signature of the TUF metadata's "signed" object."""
    keyid: KeyId
    sig: str
    extra: Dict[str, Any]

    def __init__(self, keyid: KeyId, sig: str, *, extra: Dict[str, Any]={}) -> None:
        self.keyid = keyid
        self.sig = sig
        self.extra = extra

    @classmethod
    def from_dict(cls, obj: Dict[str, Any]) -> 'Signature':
        """Create a new instance from a metadata object."""
        contains(obj, "keyid", "sig")
        keyid = KeyId(obj.pop("keyid"))
        sig = obj.pop("sig")
        return cls(keyid, sig, extra=obj)

    @classmethod
    def from_bytes(cls, keyid: KeyId, sig: bytes, *, extra: Dict[str, Any]={}) -> 'Signature':
        """Create a new instance from a byte representation."""
        return cls(keyid, b64encode(sig).decode("UTF-8"), extra=extra)

    def as_bytes(self) -> bytes:
        """Return the decoded byte representation of the signature."""
        return b64decode(self.sig)

    def random_key(self) -> 'Signature':
        """Return a new instance with a random keyid value."""
        return self.replace_key(KeyId.random())

    def random_sig(self) -> 'Signature':
        """Return a new instance with a random sig value."""
        return self.replace_sig(b64encode(os.urandom(128)).decode("UTF-8"))

    def replace_key(self, keyid: KeyId) -> 'Signature':
        """Return a new signature with the keyid value replaced."""
        return Signature(keyid, self.sig, extra=self.extra)

    def replace_sig(self, sig: str) -> 'Signature':
        """Return a new signature with the sig value replaced."""
        return Signature(self.keyid, sig, extra=self.extra)

    def _append(self, obj: Dict[str, Any]) -> None:
        """Add additional metadata to the signature"""
        self.extra.update(obj)

    def _encode(self) -> Encoded:
        out: Dict[str, Any] = {"keyid": self.keyid, "sig": self.sig}
        out.update(self.extra)
        return out


class Signatures(object):
    """Methods for operating on a collection of signatures."""
    sigs: List[Signature]

    def __init__(self, sigs: List[Signature]) -> None:
        self.sigs = sigs

    @classmethod
    def from_dicts(cls, dicts: List[Dict[str, Any]]) -> 'Signatures':
        return cls([Signature.from_dict(obj) for obj in dicts])

    def find(self, key: KeyId) -> Optional[Signature]:
        """Return the first matching key if available."""
        matches: Dict[bool, List[Signature]] = groupby(lambda sig: sig.keyid == key, self.sigs)
        try:
            return matches[True][0]
        except KeyError:
            return None

    def random(self) -> Signature:
        """Return a random signature from the collection."""
        return choice(self.sigs)

    def remove_key(self, key: KeyId) -> 'Signatures':
        """Return a new object with matching keys removed."""
        return Signatures(list(remove(lambda sig: sig.keyid == key, self.sigs)))

    def remove_random(self) -> 'Signatures':
        """Return a new object with a random key removed."""
        return self.remove_key(self.random().keyid)

    def replace_key(self, key: KeyId, replace_with: Signature) -> 'Signatures':
        """Return a new object with the matching keys replaced."""
        matches: Dict[bool, List[Signature]] = groupby(lambda sig: sig.keyid == key, self.sigs)
        return Signatures(list(concat([matches[False], [replace_with]])))

    def replace_random(self, replace_with: Signature) -> 'Signatures':
        """Return a new object with a randomly selected key replaced."""
        return self.replace_key(self.random().keyid, replace_with)

    def _encode(self) -> Encoded:
        return [sig._encode() for sig in self.sigs]  # type: ignore
