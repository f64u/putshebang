# -*- coding: utf-8 -*-

"""Main module."""

from __future__ import print_function as _

import glob as _glob
import os as _os
import re as _re
import sys as _sys

from typing import List, Tuple, Any

from ._data import Data as _Data

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


def _warn(msg):
    # type: (str) -> None
    """prints a warning to stderr"""

    print("WARNING: %s" % msg, file=_sys.stderr)


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
        self.contents = ''
        self.created = False    # to delete it if we want to

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
        """create an empty file of the object's name, setting self.created into True.
         
        """
        self.created = True
        with open(self.name, 'w') as f:
            f.write('')

    def make_executable(self):
        # type: () -> None
        """change the stat of the object's file name to be executable
        Example: -rw-rw-rw becomes -rwxrwxrwx
                 -rw------ becomes -rwx------
        """
        mode = _os.stat(self.name).st_mode
        mode |= (mode & 0o444) >> 2
        _os.chmod(self.name, mode)


class ShebangedFile(object):
    """ The file that will implement the required shebang. """

    ALL_SHEBANGS = _Data.load()

    def __init__(self, unshebanged_file, lang):
        # type: (UnshebangedFile, str) -> ShebangedFile
        """
        :param unshebanged_file: the file to add the shebang into
        :param lang: the name of the programming language (the interpreter)
        """
        self.file = unshebanged_file
        self.shebang = ''  # it'll be set in $lang setter
        self.lang = lang

    @property
    def lang(self):
        return self._lang

    @lang.setter
    def lang(self, interpreter):
        # type: (str) -> Any
        """ the lang and shebang setter
        :param interpreter: name of the interpreter program
        """
        (extension,
         available_interpreters,
         available_paths) = ShebangedFile.get_interpreter_path(self.file.name, interpreter, get_versions=True)

        if interpreter:
            try:
                _Data.add_interpreter(_re.findall("\.(.+)$", self.file.name)[0], interpreter)
            except IndexError:
                pass

        l = len(available_paths)
        if l == 0:
            if len(available_interpreters) == 0:
                raise ShebangNotFoundException("The file name extension is not associated with any known interpreter name")
            else:
                s = '(' + _re.sub(", (.+)$", "or \1", str(available_interpreters)[1:-1]) + ')'
                raise ShebangNotFoundException("Interpreter for %s not found in this machine's PATH" % s)
        elif l == 1:
            path = available_paths[0]
        else:
            print("Found %d associated interpreters with .%s extension: " % (l, extension))
            for n, s in zip(range(1, l + 1), available_paths):
                print("\t[%d]: %s" % (n, s))

            r = int(input("Choose one of the above paths [1-%d] (default is 1): " % l) or 1)
            path = available_paths[r - 1]

        self._lang = _os.path.basename(path[0])
        self.shebang = "#!{}\n".format(path)

    def put_shebang(self, newline_count, overwrite):
        # type: (int, bool) -> bool
        """puts the shebang on the first line of self.file plus(newline character * newline_count)
        :param newline_count: number of '\n' appended after the shebang
        :param overwrite: overwrite if it's a broken shebang
        :return: the success of the method
        """

        self.shebang += '\n' * newline_count
        if not self.__check_shebang(overwrite):
            print("The contents of the file wasn't modified..")
            # we want to exit !
            return False

        with open(self.file.name, 'w') as f:
            f.write(self.shebang)
            f.write(self.file.contents)
        return True

    def remove_shebang(self):
        # type: () -> None
        """removes the first line of self.file.contents (it should be the shebang) plus the whitespaces
        """
        con = self.file.contents
        self.file.contents = con = con[con.find('\n') + 1:]
        self.file.contents = _re.sub("^\s*", '', con)

    def __check_shebang(self, overwrite):
        # type: () -> bool
        """Checks if a shebang does exist and reports its state. 
        :param overwrite: overwrite if it's a broken shebang
        :return: we want to exit or not
        """

        con = self.file.contents  # just a rename
        if con.startswith(self.shebang):
            _warn("File: {}: The shebang is already there.".format(self.file.name))
            return False

        elif con.startswith("#!"):
            if overwrite:
                self.remove_shebang()
                # True

            else:
                _warn("File: {}: There's a shebang already there but it's pointing to a wrong interpreter, "
                      "you can use the option --overwrite to overwrite it.".format(self.file.name))
                return False

        return True

    @staticmethod
    def print_known():
        import tabulate

        data = [
            (("." + ext), inter, ShebangedFile.get_interpreter_path("tmp.{}".format(ext), get_versions=True)[2])
            for ext, inter in ShebangedFile.ALL_SHEBANGS.items()
        ]

        print(tabulate.tabulate(
            data,
            headers=("Extension", "Interpreter Name(s)", "Available Path(s)"),
            tablefmt="fancy_grid"
        ))

    @staticmethod
    def get_interpreter_path(name, interpreter=None, get_versions=False):
        # type: (str, str, bool) -> Tuple[str, List[str], List[str]]
        """get path of interpreters 
        
        :param name: get interpreter path based on its extension
        :param interpreter: get interpreter path based on its name
        :param get_versions: get available versions
        :return: file extension, interpreters and their paths
        """

        extension = ''  # dummy variable for late reference
        if interpreter:
            interpreters = [interpreter]
        else:
            try:
                extension = _re.findall("\.(.+)$", name)[0]
                interpreters = ShebangedFile.ALL_SHEBANGS[extension]
            except(IndexError, KeyError):
                # couldn't find the extension in the file name or it doesn't exist in the json file
                return extension, [], []    # `extension` may actually change

        if not get_versions:
            return extension, interpreters, list(map(lambda l: which(l)[0], interpreters))

        # bring all the files that starts with each `interpreter` and see if it matches the regex
        #                   (the goal is to specify any version of it)
        # TODO: Try to find the list-comprehensions equivalent
        available_shebangs = []
        for i in interpreters:
            for p in which(i + "*"):
                if _re.match(r'^%s-?(\d\.\d(\.\d)?)?$' % i, _os.path.basename(p)):
                    available_shebangs.append(p)

        return extension, interpreters, available_shebangs
