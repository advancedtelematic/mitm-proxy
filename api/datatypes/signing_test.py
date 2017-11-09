from .signing import Rsa


def get_rsa(size: int) -> Rsa:
    return Rsa.from_files(f"fixtures/rsa/rsa_{size}.pub", f"fixtures/rsa/rsa_{size}.key")

def test_sign_and_verify() -> None:
    for size in [512, 1024, 2047, 2048, 3072, 4096]:
        rsa = get_rsa(size)
        msg = "hello".encode("UTF-8")
        sig = rsa.sign(msg)
        assert(rsa.verify(sig, rsa.pub, msg))
