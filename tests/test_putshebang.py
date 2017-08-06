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

    def setUp(self):
        """Set up test fixtures, if any."""
        self.shebang_path = putshebang.shebang("temp.py")

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'putshebang.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
        assert check_output([shutil.which('env'), "python"]) == self.shebang_path
