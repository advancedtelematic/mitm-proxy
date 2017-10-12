import json
import os
import pytest

from errors import Error, InvalidKeyIdError, MissingFieldError, UnknownRoleError
from metadata import Metadata, Role
from my_types import canonical
from typing import Any, Callable, Type


META_DIR = "tests/metadata"
KEY_ID = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"


def assert_raises(e: Type[Error], f: Callable, *args: Any) -> None:
    with pytest.raises(e):
        f(*args)


def test_read_metadata() -> None:
    for test in [
        '{}',
        '{"signed": []}',
        '{"signatures": {}}',
        '{"signed": [], "signatures": {}}',
        '{"signatures": [{"keyid": "id"}], "signed": {"_type": "root", "expires": "", "version": "1"}}',
    ]:
        assert_raises(MissingFieldError, Metadata.from_readable, test)

    for test in [
        '''{"signatures": [{"keyid": "invalid", "sig": "foo"}],
            "signed": {"_type": "root", "expires": "", "version": 1}}'''
    ]:
        assert_raises(InvalidKeyIdError, Metadata.from_readable, test)

    for test in [
        f'''{{"signatures": [{{"keyid": "{KEY_ID}", "sig": "foo"}}],
              "signed": {{"_type": "bad", "expires": "", "version": 1}}}}'''
    ]:
        assert_raises(UnknownRoleError, Metadata.from_readable, test)

    ok = f'''{{"signatures": [{{"keyid": "{KEY_ID}", "sig": "foo"}}],
               "signed": {{"_type": "root", "expires": "", "version": 1}}}}'''
    meta = Metadata.from_readable(ok)
    assert meta.role == Role.Root
    assert meta.version == 1
    assert len(meta.signatures) == 1
    assert meta.signatures[0].keyid == KEY_ID


def test_targets_metadata() -> None:
    with open(f"{META_DIR}/targets.json", "rb") as fd:
        meta = Metadata.from_readable(fd.read())
        assert len(meta.targets) == 2
        target1 = meta.targets[0]
        target2 = meta.targets[1]

        assert target1.filepath == "/file1.txt"
        assert target1.length == 31
        assert target1.custom == {
            "file_permissions": "664"
        }
        assert len(target1.hashes) == 2
        assert target1.hashes == {
            "sha256": "65b8c67f51c993d898250f40aa57a317d854900b3a04895464313e48785440da",
            "sha512": "467430a68afae8e9f9c0771ea5d78bf0b3a0d79a2d3d3b40c69fde4dd42c461448aef76fcef4f5284931a1ffd0ac096d138ba3a0d6ca83fa8d7285a47a296f77"  # noqa: E501
        }

        assert target2.filepath == "/file2.txt"
        assert target2.length == 39
        assert target2.custom is None
        assert target2.hashes == {
            "sha256": "452ce8308500d83ef44248d8e6062359211992fd837ea9e370e561efb1a4ca99",
            "sha512": "052b49a21e03606b28942db69aa597530fe52d47ee3d748ba65afcd14b857738e36bc1714c4f4adde46c3e683548552fe5c96722e0e0da3acd9050c2524902d8"  # noqa: E501
        }


def test_encode_json() -> None:
    for _, [], files in os.walk(META_DIR):
        for filename in files:
            with open(f"{META_DIR}/{filename}", "rb") as fd:
                data = fd.read()
                meta_parsing = Metadata.from_readable(data).to_json()
                json_parsing = canonical(json.loads(data))
                assert meta_parsing == json_parsing
