# -*- coding: utf-8 -*-

"""Top-level package for putshebang."""

from .shebangs import ShebangedFile, UnshebangedFile, ShebangNotFoundError, which
from typing import List

__all__ = ["ShebangedFile", "UnshebangedFile", "ShebangNotFoundError", "which"]
__author__ = """Fady Adel"""
__email__ = '2masadel@gmail.com'
__version__ = '0.1.5'


def shebang(file_name, lang=None, get_versions=False, get_symlinks=False):
    # type: (str, str, bool, bool) -> List[str]
    """Get available shebangs associated with `file_name'
    :param file_name: the file name to get the extension from
    :param lang: forget about the extension and use `lang' as the interpreter name
    :param get_versions: use the regex that matches different versions of the same language
                         Example:
                            python: matches => (python, python3, python3.6, python2017.04, python-2.7, ...)
    :param get_symlinks: get the symlink even if the realpath of it already in the list
    :return: list of available shebangs on the system
    """
    return list(map(lambda s: "#!{}".format(s),
                    ShebangedFile.get_interpreter_path(file_name, lang, get_versions, get_symlinks)[1]["all"]
                    ))


__all__.append("shebang")
