#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `putshebang` package."""

import unittest
from subprocess import check_output

from putshebang.main import shebang, which


class TestPutshebang(unittest.TestCase):
    """Tests for `putshebang` package."""

    def test_command_line_interface(self):
        env_path = which("env")[0]
        """Test the CLI."""
        assert "#!" + str(check_output([env_path, "python2"]).strip()) == shebang("tmp.py", "python2")[0]
        assert "#!" + str(check_output([env_path, "python3"]).strip()) == shebang("tmp.py", "python3")[0]
