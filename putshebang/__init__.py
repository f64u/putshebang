# -*- coding: utf-8 -*-

"""Top-level package for putshebang."""

from typing import List

from .shebangs import ShebangedFile, UnshebangedFile, ShebangNotFoundError, which, InterpreterPath, Interpreter

__all__ = ["ShebangedFile", "UnshebangedFile", "InterpreterPath", "Interpreter", "ShebangNotFoundError", "which"]
__author__ = """Fady Adel"""
__email__ = '2masadel@gmail.com'
__version__ = '0.1.6'


def shebang(file_name=None, interpreter=None, get_versions=False, get_links=0):
    # type: (str, str, bool, int) -> List[str]

    """Get available shebangs associated with `file_name' or `interpreter'.
    :param file_name: the file name to get the extension from
    :param interpreter: forget about the extension and use `lang' as the interpreter name
    :param get_versions: use the regex that matches different versions of the same language
                         Example:
                            'python': matches => (python, python3, python3.6, python2017.04, python-7.7, ...)
                            
                         however, if false, if `interpreter' or `the default interpreter' contains a version,
                         you'll receive it
    :param get_links: 0 means you'll get every thing as found on PATH (no action taken for links
                          1 means don't get links but get real paths even if they're not in PATHS
                          2 means same as 1 but exclude the ones that are not in PATH (that also means the ones already
                            exist (no multiple references for the same file))
    :return: list of available shebangs on the system
    """
    d = ShebangedFile.get_extension(file_name=file_name, interpreter=interpreter, get_versions=get_versions,
                                    get_links=get_links).interpreters
    all_paths = [str(p) for i in [l.all_paths for l in [d["default"] if d["default"] else []] + d["others"]] for p in i]

    return list(map(lambda p: "#!{}".format(p), all_paths))

__all__.append("shebang")
