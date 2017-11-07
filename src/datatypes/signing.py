import rsa

from rsa import PrivateKey, PublicKey
from typing_extensions import Protocol

from .signature import KeyId, Signature


class Signer(Protocol):
    def sign(self, message: bytes) -> Signature:
        pass

class Verifier(Protocol):
    @staticmethod
    def verify(sig: Signature, key: PublicKey, message: bytes) -> bool:
        pass


class Rsa(object):
    """Stores an RSA keypair for metadata signing."""
    pub: PublicKey
    priv: PrivateKey
    keyid: KeyId

    def __init__(self, pub: PublicKey, priv: PrivateKey) -> None:
        self.pub = pub
        self.priv = priv
        self.keyid = KeyId.from_pub(pub)

    @classmethod
    def generate(cls, size: int=2048) -> 'Rsa':
        """Generate a new RSA keypair of the given size."""
        return cls(*rsa.key.newkeys(size))

    @classmethod
    def from_files(cls, pub_path: str, priv_path: str, key_format: str='PEM') -> 'Rsa':
        """Parse an RSA keypair from existing files."""
        with open(pub_path, "rb") as f:
            pub = PublicKey.load_pkcs1(f.read(), format=key_format)
        with open(priv_path, "rb") as f:
            priv = PrivateKey.load_pkcs1(f.read(), format=key_format)
        return cls(pub, priv)

    @staticmethod
    def verify(sig: Signature, key: PublicKey, message: bytes) -> bool:
        """Verify that the signature matches the claimed message and key."""
        try:
            rsa.verify(message, sig.as_bytes(), key)
            return True
        except rsa.VerificationError:
            return False

    def sign(self, message: bytes) -> Signature:
        """Sign the message with our key."""
        return self._sign(message)

    def _sign(self, message: bytes, hash_format: str="SHA-256") -> Signature:
        sig = rsa.sign(message, self.priv, hash_format)
        return Signature.from_bytes(self.keyid, sig)
