#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `putshebang` package."""


import unittest
from click.testing import CliRunner
from subprocess import check_output
import shutil
from putshebang import putshebang
from putshebang import cli


class TestPutshebang(unittest.TestCase):
    """Tests for `putshebang` package."""

    def test_command_line_interface(self):
        env_path = shutil.which("env")
        shebang = putshebang.shebang
        """Test the CLI."""
        assert "#!" + str(check_output([env_path, "python2"]).strip()) == shebang("tmp.py", "python2")
        assert "#!" + str(check_output([env_path, "python3"]).strip()) == shebang("tmp.py", "python3")
