# -*- coding: utf-8 -*-

import random
import pytest

from tuf_mitm_proxy import create_app

# set the random seed to provide deterministic testing
random.seed(0)


@pytest.fixture()
def app():
    a = create_app('example.com', 80)
    with a.app_context():
        return a.test_client()
