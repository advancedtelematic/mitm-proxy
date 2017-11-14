import os

from base64 import b64encode
from itertools import repeat

from .signature import KeyId, Signature, Signatures


def random_sig() -> Signature:
    key = KeyId.random()
    sig = b64encode(os.urandom(128)).decode("UTF-8")
    return Signature(key, sig)

def test_replace_sig() -> None:
    rand_sig = b64encode(os.urandom(128)).decode("UTF-8")
    sig = random_sig().replace_sig(rand_sig)
    assert sig.sig == rand_sig

def test_replace_key() -> None:
    rand_key = KeyId.random()
    sig = random_sig().replace_key(rand_key)
    assert sig.keyid == rand_key

def test_sigs_remove_key() -> None:
    sigs = Signatures([sig() for sig in repeat(random_sig, 3)])
    rand_key = sigs.random().keyid
    sigs = sigs.remove_key(rand_key)
    assert sigs.find(rand_key) is None
    assert len(sigs.sigs) == 2

def test_sigs_replace_key() -> None:
    sigs = Signatures([sig() for sig in repeat(random_sig, 3)])
    rand_key = sigs.random().keyid
    new_sig = random_sig()
    sigs = sigs.replace_key(rand_key, new_sig)
    assert sigs.find(rand_key) is None
    assert sigs.find(new_sig.keyid) is not None
    assert len(sigs.sigs) == 3

def test_sigs_duplicate_key() -> None:
    sigs = Signatures([sig() for sig in repeat(random_sig, 3)])
    rand_key = sigs.random().keyid
    sigs = sigs.duplicate_key(rand_key)
    assert sigs.find(rand_key) is not None
    assert len(sigs.sigs) == 4
