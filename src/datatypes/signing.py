from rsa import PrivateKey, PublicKey, key
from typing_extensions import Protocol


class Signer(Protocol):
    def sign(self, message: str) -> None:
        pass


class Rsa(object):
    """Stores an RSA keypair for metadata signing."""
    pub: PublicKey
    priv: PrivateKey

    def __init__(self, pub: PublicKey, priv: PrivateKey) -> None:
        self.pub = pub
        self.priv = priv

    @classmethod
    def from_files(cls, pub_path: str, priv_path: str, format: str='PEM') -> 'Rsa':
        """Parse an RSA keypair from existing files."""
        pub = PublicKey.load_pkcs1(pub_path, format=format)
        priv = PrivateKey.load_pkcs1(priv_path, format=format)
        return cls(pub, priv)

    @classmethod
    def generate(cls, size: int=2048) -> 'Rsa':
        """Generate a new RSA keypair of the given size."""
        return cls(*key.newkeys(size))
