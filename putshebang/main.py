# -*- coding: utf-8 -*-

"""Main module."""

from __future__ import print_function as _

import glob as _glob
import os as _os
import pprint
import re as _re
import sys as _sys

from typing import List, Tuple, Any

from putshebang._data import Data as _Data

# compatibility
if _sys.version_info.major == 2:
    input = raw_input


def which(cmd):
    # type: (str) -> List[str]
    """like shutil.which, but uses globs, and less features"""

    paths = _os.environ.get("PATH", _os.defpath).split(":")
    l = []
    for path in paths:
        abs_path = _os.path.join(path, cmd)
        g = list(filter(lambda f: (not _os.path.isdir(f) and _os.access(f, _os.F_OK | _os.X_OK)), _glob.glob(abs_path)))
        if len(g) != 0:
            l.extend(g)
    return l


class ShebangNotFoundException(Exception):
    pass


class UnshebangedFile(object):
    """ The file that requires the shebang. """

    def __init__(self, name, strict, make_executable):
        # type: (str, bool, bool) -> UnshebangedFile
        """
        :param name: name of the file to operate on
        :param strict: a bool specifies the creatability
        :param make_executable: a bool specifies whether make the file executable or not (obviously)
        """
        self.name = name
        try:
            self.extension = _re.findall("\.(.+)$", self.name)[0]
        except IndexError:
            self.extension = ''
        self.contents = ''
        self.created = False  # to delete it if we want to

        if not _os.path.isfile(self.name):
            if not strict:
                self.create()
            else:
                raise ValueError("File name doesn't exist.")

        else:
            with open(self.name) as f:
                self.contents = f.read()

        if make_executable:
            self.make_executable()

    def create(self):
        # type: () -> None
        """create an empty file of the object's name, setting self.created into True."""
        self.created = True
        with open(self.name, 'w') as f:
            f.write('')

    def make_executable(self):
        # type: () -> None
        """change the stat of the object's file name to be executable
        
        Example:
             -rw-rw-rw becomes -rwxrwxrwx
             -rw------ becomes -rwx------
        """
        mode = _os.stat(self.name).st_mode
        mode |= (mode & 0o444) >> 2
        _os.chmod(self.name, mode)


class ShebangedFile(object):
    """ The file that will implement the required shebang.
        basic usage:
            >>> sf1 = ShebangedFile(UnshebangedFile("file.py", False, False))
            >>> sf1.put_shebang()
            0
            >>> print(sf1.shebang, end='')
            #!/usr/bin/python
            <BLANKLINE>
            >>> sf1.file.make_executable()
            >>> sf1.shebang = "#!/usr/bin/ruby\\n"
            >>> sf1.put_shebang()
            0
            >>> print(sf1.shebang, end='')
            #!/usr/bin/ruby
            <BLANKLINE>
    """

    ALL_SHEBANGS = _Data.load()

    def __init__(self, unshebanged_file):
        # type: (UnshebangedFile) -> ShebangedFile
        """
        :param unshebanged_file: the file to add the shebang into
        """
        self.file = unshebanged_file
        try:
            self.shebang = "#!{}\n".format(which(ShebangedFile.ALL_SHEBANGS[self.file.extension]["default"][0])[0])
        except (IndexError, KeyError):
            self.shebang = ''

    def put_shebang(self, newline_count=1, overwrite=True):
        # type: (int, bool) -> int
        """puts the shebang on the first line of self.file plus ('\n' * newline_count)
        :param newline_count: number of '\n' appended after the shebang
        :param overwrite: overwrite if it's a broken shebang
        :return: what __check_shebang() returns
        """

        self.shebang += '\n' * newline_count
        code = self.__check_shebang(overwrite)
        if code != 0:
            return code

        with open(self.file.name, 'w') as f:
            f.write(self.shebang)
            f.write(self.file.contents)
        return code  # which is 0

    def remove_shebang(self):
        # type: () -> None
        """removes the first line of self.file.contents (it should be the shebang) plus the whitespaces"""
        con = self.file.contents  # just a rename
        self.file.contents = con = con[con.find('\n') + 1:]
        self.file.contents = _re.sub("^\s*", '', con)

    def __check_shebang(self, overwrite):
        # type: (bool) -> int
        """Checks if a shebang does exist and reports its state. 
        :param overwrite: overwrite if it's a broken shebang
        :return:
            1 -> The correct the shebang is already there
            2 -> There's a shebang, but it's pointing to a wrong interpreter
            0 -> Don't care..
        """

        con = self.file.contents
        if con.startswith(self.shebang):
            return 1

        elif con.startswith("#!"):
            if overwrite:
                self.remove_shebang()
                # 0
            else:
                return 2

        return 0

    @staticmethod
    def print_known():
        import tabulate

        data = [
            (("." + ext), inter, ShebangedFile.get_interpreter_path("tmp.{}".format(ext), get_versions=True)[1])
            for ext, inter in ShebangedFile.ALL_SHEBANGS.items()
        ]

        print(tabulate.tabulate(
            data,
            headers=("Extension", "Interpreter Name(s)", "Available Path(s)"),
            tablefmt="fancy_grid"
        ))

    @staticmethod
    def get_interpreter_path(name, interpreter=None, get_versions=False, get_symlinks=True):
        # type: (str, str, bool, bool) -> Tuple[List[str], List[str]]
        """get path of interpreters 
        
        :param name: get interpreter path based on its extension
        :param interpreter: get interpreter path based on its name
        :param get_versions: get available versions
        :param get_symlinks: get the symlink even if the realpath of it is already in the `available_paths'
        :return: file extension, interpreters and their paths
        """

        if interpreter is not None:
            interpreters = [interpreter]
        else:
            try:
                interpreters = ShebangedFile.ALL_SHEBANGS[_re.findall("\.(.+)$", name)[0]]
                interpreters = [interpreters["default"][0]] + interpreters["other"]
            except(IndexError, KeyError):
                # couldn't find the extension in the file name or it doesn't exist in the json file
                return [], []

        # bring all the files that starts with each `interpreter' and see if it matches the regex
        #                   (the goal is to specify any version of it)
        # TODO: Try to find the list-comprehensions equivalent
        available_paths = []
        for i in interpreters:
            for p in which(i + "*"):
                if _re.match(r'^%s-?(\d{1,4}(\.\d{1,2}(\.\d)?)?)?$' % i, _os.path.basename(p)):
                    available_paths.append(p)
        if not get_versions:
            available_paths = filter(lambda path: not _re.match("^\w+\d+.*(?#:that's enough for me)", _os.path.basename(path)), available_paths)
        if not get_symlinks:
            dummy = available_paths
            available_paths = filter(lambda path: not(_os.path.islink(path) and _os.path.realpath(path) in dummy), available_paths)

        return interpreters, sorted(available_paths, reverse=True)
