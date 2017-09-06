# -*- coding: utf-8 -*-

"""Main module."""

from __future__ import print_function

import glob
import os
import re
import tempfile
import logging
from .data import Data

logging.basicConfig(format="%(levelname)s: %(message)s")


def which(cmd):
    """like shutil.which, but uses globs, and less features"""

    paths = os.environ.get("PATH", os.defpath).split(":")
    for path in paths:
        abs_path = os.path.join(path, cmd)
        g = glob.glob(abs_path)
        if len(g) != 0:
            return list(filter(lambda f: (not os.path.isdir(f) and os.access(f, os.F_OK | os.X_OK)), g))
    return []


class ShebangNotFoundException(Exception):
    pass


class UnshebangedFile(object):
    """ The file that requires the shebang. """

    def __init__(self, name, strict):
        """
        :param name: name of the file to operate on
        :param strict: a bool that specifies the creatability
        """
        self.name = name

        if not os.path.isfile(self.name):
            if not strict:
                self.__create()
                self.contents = ''
            else:
                raise ValueError("File name doesn't exist.")

        else:
            with open(self.name) as f:
                self.contents = f.read()

    def __create(self):
        with open(self.name, 'w') as f:
            f.write('')


class ShebangedFile(object):
    """ The file that will implement the required shebang. """

    ALL_SHEBANGS = Data.load()

    def __init__(self, unshebanged_file, lang):
        self.file = unshebanged_file
        self.shebang = None  # it'll be set in $lang setter
        self.lang = lang

    @property
    def lang(self):
        return self.lang

    @lang.setter
    def lang(self, interpreter):
        if interpreter:
            Data.add_shebang(self.file.name)
            s = which(interpreter)
            if not s:
                raise ShebangNotFoundException("Interpreter for %s not found" % interpreter)
            if len(s) != 1:
                # use of globs when specifying the interpreter name
                raise ValueError("Use of globs is not permitted when specifying the interpreter name")
            path = s[0]

        else:
            try:
                interpreters = ShebangedFile.ALL_SHEBANGS[re.findall("\.(.+)$", self.file.name)[0]]
            except(IndexError, KeyError):
                # couldn't find the extension or it doesn't exist in the dict
                raise ShebangNotFoundException("Couldn't guess the language from the file extension")

            # bring all the files that starts with each $prg_lang and see if it matches the regex(that may specify
            # and version of it)
            # TODO: Try to find the list comprehensions equivalent
            available_shebangs = []
            for i in interpreters:
                for p in which(i + "*"):
                    if re.match(r'^%s(\d\.\d(\.\d)?)?$' % i, os.path.basename(p)):
                        available_shebangs.append(p)

            if not available_shebangs:
                raise ShebangNotFoundException("interpreter for the language %s not found on this machine" %
                                               interpreters[0])

            l = len(available_shebangs)
            if l > 1:
                print("Found %d associated interpreters with this extension: " % l)
                for n, s in zip(range(1, l + 1), available_shebangs):
                    print("\t[%d]: %s" %(n, s))

                r = int(input("Choose one of the above paths [1-%d](default is 1): " % l) or 1)
                path = available_shebangs[r - 1]
            else:
                path = available_shebangs[0]
        self.shebang = "#!{}\n".format(path)

    def make_executable(self):
        mode = os.stat(self.file.name).st_mode
        mode |= (mode & 0o444) >> 2
        os.chmod(self.file.name, mode)

    def put_shebang(self, newline_count, overwrite):
        """ puts the shebang on the first line of self.file plus(newline character * newline_count)
        :param newline_count: number of '\n' appended after the shebang(int)
        :param overwrite: overwrite if it's a broken shebang(bool)
        :return: bool specifies the success of the method
        """

        self.shebang += '\n' * newline_count
        if not self.__check_shebang(overwrite):
            print("The script didn't modify the file..")
            # we want to exit !
            return False

        with open(self.file.name, 'w') as f:
            f.write(self.shebang)
            f.write(self.file.contents)
        return True

    def print_known(self):
        print("\nExtension\tInterpreter name")
        print('=' * 35)
        for extension, lang in self.ALL_SHEBANGS.items():
            print("{}\t\t{}".format(extension, lang))

    def __check_shebang(self, overwrite):
        """ Checks if a shebang does exist and reports its state. 
        :param overwrite: overwrite if it's a broken shebang(True || False)
        :return: bool specifies whether we want to exit or not
        """

        con = self.file.contents  # just a rename
        if con.startswith(self.shebang):
            logging.warning("The shebang is already there.")
            return False

        elif con.startswith("#!"):
            if overwrite:
                self.__remove_shebang()
                # True

            else:
                logging.warning("There's a shebang already there but it's pointing to a wrong interpreter, "
                                "you can use the option --overwrite to overwrite it.")
                return False

        return True

    def __remove_shebang(self):
        """ removes the first line of self.file.contents (it should be the shebang) plus the whitespaces.
        :return: void
        """
        con = self.file.contents
        self.file.contents = con = con[con.find('\n') + 1:]
        self.file.contents = re.sub("^\s*", '', con)

    @staticmethod
    def get_interpreter_path(name, interpreter=None, get_versions=False):
        """get path of interpreters 
        
        :param name: get interpreter path based on its extension (str)
        :param interpreter: get interpreter path based on its name (str)
        :param get_versions: get available versions (bool)
        :return: 
        """
        if interpreter:
            interpreters = [interpreter]

        else:
            try:
                interpreters = ShebangedFile.ALL_SHEBANGS[re.findall("\.(.+)$", name)[0]]
            except(IndexError, KeyError):
                # couldn't find the extension or it doesn't exist in the json file
                return []

        if not get_versions:
            return list(map(lambda l: which(l)[0], interpreters))

        # bring all the files that starts with each $interpreter and see if it matches the regex(that may specify
        # and version of it)
        # TODO: Try to find the list comprehensions equivalent
        available_shebangs = []
        for i in interpreters:
            for p in which(i + "*"):
                if re.match(r'^%s(\d\.\d(\.\d)?)?$' % i, os.path.basename(p)):
                    available_shebangs.append(p)

        return available_shebangs


def shebang(file_name, lang=None, get_versions=False):
    return list(map(lambda s: "#!{}".format(s), ShebangedFile.get_interpreter_path(file_name, lang, get_versions)))
