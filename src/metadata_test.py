import os
import pytest

from errors import MissingFieldError, UnknownRoleError
from metadata import _read_metadata
from my_types import Error
from typing import Any, Callable


META_DIR = "tests/metadata"

def assert_ok(f: Callable, *args: Any) -> None:
    try:
        f(*args)
    except Exception as e:
        pytest.fail(f"unexpected exception: {e}")

def assert_raises(e: Error, f: Callable, *args: Any) -> None:
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
        assert_raises(MissingFieldError, _read_metadata, test)

    for test in [
        '{"signatures": [{"keyid": "id", "sig": "foo"}], "signed": {"_type": "nope", "expires": "", "version": 1}}',
    ]:
        assert_raises(UnknownRoleError, _read_metadata, test)

    for test in [
        '{"signatures": [{"keyid": "id", "sig": "foo"}], "signed": {"_type": "root", "expires": "", "version": 1}}'
    ]:
        assert_ok(_read_metadata, test)

    for _, [], files in os.walk(META_DIR):
        for filename in files:
            with open(f"{META_DIR}/{filename}", "rb") as fd:
                assert_ok(_read_metadata, fd.read())
