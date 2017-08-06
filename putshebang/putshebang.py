# -*- coding: utf-8 -*-

"""Main module."""

import os
import re
import shutil


class UnshebangedFile(object):
    """ The file that requires the shebang. """

    def __init__(self, name, create):
        """
        :param name: name of the file to operate on
        :param create: a bool the specifies the creatability
        """
        self.name = name

        if not os.path.isfile(self.name):
            if create:
                self.__create()
                self.contents = ''

            else:
                print("File doesn't exist. Try using the --force option to force the script to create it for you.")
                exit(1)

        else:
            with open(self.name) as f:
                self.contents = f.read()

    def __create(self):
        with open(self.name, 'w') as f:
            f.write('')


class ShebangedFile(object):
    """ The file that will implement the required shebang. """

    # TODO: Learn from previous runs
    FILE_EXTENSIONS = {
        "py": "python",
        "rb": "ruby",
        "sh": "sh",
        "bash": "bash",
        "zsh": "zsh",
        "pl": "perl",
        "js": "node",
        "php": "php",
        "tcl": "tcl",
        "lua": "lua"
    }

    def __init__(self, unshebanged_file, lang):
        self.file = unshebanged_file
        self.shebang = None  # it'll be set in $lang setter
        self.lang = lang

    @property
    def lang(self):
        return self.lang

    @lang.setter
    def lang(self, prg_lang):

        if prg_lang:
            self.shebang = "#!{}\n".format(shutil.which(prg_lang))
        else:
            try:
                self.shebang = "#!{}\n".format(shutil.which(self.FILE_EXTENSIONS[re.findall("\.(\w+)$",
                                                                                            self.file.name)[0]]))

            except (IndexError, KeyError):
                # couldn't find the extension or it doesn't exist in the dict
                print("Couldn't guess the language from the file extension.")
                print("please use the --lang option to specify it.")
                exit(1)

    def make_executable(self):
        mode = os.stat(self.file.name).st_mode
        mode |= (mode & 0o444) >> 2
        os.chmod(self.file.name, mode)

    def put_shebang(self, newline_count, overwrite):
        """ puts the shebang on the first line of self.file plus (newline character * newline_count)
        :param newline_count: number of '\n' appended after the shebang (int)
        :param overwrite: overwrite if it's a broken shebang (True || False)
        :return: void
        """

        self.shebang += '\n' * newline_count
        self.__check_shebang(overwrite)

        with open(self.file.name, 'w') as f:
            f.write(self.shebang)
            f.write(self.file.contents)

    def print_known(self):
        print("\nExtension\tInterpreter name")
        print('=' * 35)
        for extension, lang in self.FILE_EXTENSIONS.items():
            print("{}\t\t{}".format(extension, lang))

    def __check_shebang(self, overwrite):
        """ Checks if a shebang does exist and reports its state. 
        :param overwrite: overwrite if it's a broken shebang (True || False)
        :return: void
        """

        con = self.file.contents  # just a rename
        if con.startswith(self.shebang):
            print("The shebang is already there.\nExiting...")
            exit()

        elif con.startswith("#!"):
            if overwrite:
                self.__remove_shebang()

            else:
                print("There's a shebang already there but it's pointing to a wrong interpreter.")
                print("Use the option --overwrite to overwrite it.")
                exit(1)

    def __remove_shebang(self):
        """ removes the first line of self.file plus the whitespaces.
        :return: 
        """
        con = self.file.contents
        self.file.contents = con = con[con.find('\n') + 1:]
        self.file.contents = re.sub("^\s*", '', con)

    @staticmethod
    def get_potential_shebang(name):
        sh = ShebangedFile(UnshebangedFile(name, create=True), None).shebang    # create = True? just temporary
        os.remove(name)
        return sh


def shebang(file_name):
    return ShebangedFile.get_potential_shebang(file_name)

