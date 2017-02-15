# -*- coding: utf-8 -*-

import json
import pytest

from canonicaljson import encode_canonical_json
from flask import Response
from tuf_mitm_proxy.alteration import (Alteration, TwiddleJson, NoOpAlteration,
        AddSignatures, DeleteSignatures)


class TestAlteration:

    def test__twiddle_json_function(self):
        string = 'test'
        assert TwiddleJson._twiddle_json(string) != string

        num = 1
        assert TwiddleJson._twiddle_json(num) != num

        num = -0.5
        assert TwiddleJson._twiddle_json(num) != num

        bl = False
        assert TwiddleJson._twiddle_json(bl) != bl

        lst = [1, "stuff", True]
        assert TwiddleJson._twiddle_json(lst) != lst

        lst = []
        assert TwiddleJson._twiddle_json(lst) != lst

        dct = {'key': 'value', 'key2': 123}
        assert TwiddleJson._twiddle_json(dct) != dct

        dct = {}
        assert TwiddleJson._twiddle_json(dct) != dct

        assert TwiddleJson._twiddle_json(None) is not None

    def test_is_signed_json(self):
        jsn = {'signatures': [{'keyid': 'abc123', 'method': 'rsa', 'sig': 'aaa111'}],
               'signed': {'wat': 'lol'}}
        resp = Response(json.dumps(jsn))
        resp.headers['Content-Type'] = 'application/json'
        assert Alteration._is_signed_json(resp)

    def test_load_keys(self):
        for typ in ['rsa', 'ed25519']:
            for num in range(1, 7):
                for priv in [True, False]:
                    assert Alteration._get_key_material(typ, num, priv)


class TestNoOpAlteration:

    def test_apply(self):
        resp = Response('hello world')
        mod = NoOpAlteration.apply(resp)
        assert mod == resp


class TestTwiddleJson:

    def test_apply(self):
        jsn = {'test': 'wat'}
        resp = Response(json.dumps(jsn))
        resp.headers['Content-Type'] = 'application/json'
        mod = TwiddleJson.apply(resp)
        assert json.loads(mod.data.decode('utf-8')) != jsn


class TestAddSignatures:

    JSON = {'signatures': [{'keyid': 'abc123', 'method': 'rsa', 'sig': 'aaa111'}],
            'signed': {'wat': 'lol'}}

    def test_check(self):
        resp = Response(encode_canonical_json(self.JSON).decode('utf-8'))
        resp.headers['Content-Type'] = 'application/json'
        assert AddSignatures.check(resp)

    def test_apply(self):
        # do it many times to ensure all key types are tested
        for _ in range(0, 10):
            resp = Response(encode_canonical_json(self.JSON).decode('utf-8'))
            mod = AddSignatures.apply(resp)
            assert len(json.loads(mod.data.decode('utf-8'))['signatures']) == 2


class TestDeleteSignatures:

    JSON = {'signatures': [{'keyid': 'abc123', 'method': 'rsa', 'sig': 'aaa111'}],
            'signed': {'wat': 'lol'}}

    def test_check(self):
        resp = Response(encode_canonical_json(self.JSON).decode('utf-8'))
        resp.headers['Content-Type'] = 'application/json'
        assert AddSignatures.check(resp)

    def test_apply(self):
        resp = Response(encode_canonical_json(self.JSON).decode('utf-8'))
        mod = DeleteSignatures.apply(resp)
        assert not json.loads(mod.data.decode('utf-8'))['signatures']
