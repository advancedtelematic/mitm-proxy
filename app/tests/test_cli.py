# -*- coding: utf-8 -*-

import pytest

from tuf_mitm_proxy import arg_parser


class TestCli:

    def test_cli(self):
        try:
            arg_parser('test').parse_args(['--help'])
            pytest.fail('expected system exit')  # pragma: no cover
        except SystemExit as e:
            if not e.code == 0:  # pragma: no cover
                raise e
