#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `putshebang` package."""

import unittest

from putshebang import shebang, which
from putshebang import __main__ as cli
from tempfile import gettempdir
from os.path import join


class TestPutshebang(unittest.TestCase):
    """Tests for `putshebang` package."""

    def test_command_line_interface(self):
        assert cli.main(["-l", "python", join(gettempdir(), "file.py")]) == 0
        assert "#!" + which("python")[0] in shebang("tmp.py", get_versions=True, get_symlinks=True)
