# -*- coding: utf-8 -*-

"""Top-level package for putshebang."""

from .main import ShebangedFile, UnshebangedFile, ShebangNotFoundException

__all__ = ["ShebangedFile", "UnshebangedFile", "ShebangNotFoundException"]
__author__ = """Fady Adel"""
__email__ = '2masadel@gmail.com'
__version__ = '0.1.5'


def shebang(file_name, lang=None, get_versions=False):
    return list(map(lambda s: "#!{}".format(s), ShebangedFile.get_interpreter_path(file_name, lang, get_versions)[2]))

__all__.append("shebang")
