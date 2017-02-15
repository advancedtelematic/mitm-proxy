#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = [
            '--doctest-modules',
            '--strict',
            # '--fulltrace',  # useful for debugging
        ]

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(
    name="mitm-proxy",
    version="0.0.0",
    author="Eric Hartsuyker",
    author_email="eric.hartsuyker@advancedtelematic.com",
    license='MPL2',
    description="runs a MITM proxy for testing Uptane",
    cmdclass={'test': PyTest},
)
