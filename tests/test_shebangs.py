#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `putshebang` package."""

import unittest
from subprocess import check_output

from putshebang import shebang, which
from putshebang import __main__ as cli


class TestPutshebang(unittest.TestCase):
    """Tests for `putshebang` package."""

    def test_command_line_interface(self):
        assert cli.main() == 0
        assert "#!" + which("python")[0] in shebang("tmp.py", get_versions=True, get_symlinks=True)
