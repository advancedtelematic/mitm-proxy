#!/usr/bin/env pipenv run python
import sys
sys.path.append("../../src")

from datatypes.signing import Rsa  # noqa


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: <key size> <output dir>")
    size = int(sys.argv[1])
    out_dir = sys.argv[2]

    keys = Rsa.generate(size)
    with open(f"{out_dir}/rsa_{size}.pub", "wb") as f:
        f.write(keys.pub.save_pkcs1())
    with open(f"{out_dir}/rsa_{size}.key", "wb") as f:
        f.write(keys.priv.save_pkcs1())
