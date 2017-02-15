# -*- coding: utf-8 -*-

import pytest
import requests_mock


class TestApp:

    def test_app_get(self, app):
        with requests_mock.mock() as r_mock:
            r_mock.get('http://example.com:80/', text='test',
                       headers={'Content-Type': 'text/plain'})
            resp = app.get('/')
            assert resp.status_code == 200

    def test_app_get_path(self, app):
        with requests_mock.mock() as r_mock:
            r_mock.get('http://example.com:80/some/path?a=b', text='test',
                       headers={'Content-Type': 'text/plain'})
            resp = app.get('/some/path?a=b')
            assert resp.status_code == 200

    def test_app_post(self, app):
        with requests_mock.mock() as r_mock:
            r_mock.post('http://example.com:80/', json={"wat": "ok"},
                        headers={'Content-Type': 'application/json'})
            resp = app.post('/', data={'abc': 123})
            assert resp.status_code == 200
