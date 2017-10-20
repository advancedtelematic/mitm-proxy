from .signature import KeyId, Signature, remove_random_sig, remove_sig_by_key
from ..utils import assert_raises


KEY1 = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
KEY2 = "0000000000000000000000000000000000000000000000000000000000000000"
KEY3 = "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"

RSA1 = ""

SIG1 = Signature({"keyid": f"{KEY1}", "sig": "RSA1"})


def test_remove_signatures() -> None:
    for test in [
    ]:
        pass
