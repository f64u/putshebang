# -*- coding: utf-8 -*-

"""Console script for shebang."""

import argparse
import os
import re
import sys

from putshebang import __version__
from putshebang._data import Data
from putshebang.shebangs import ShebangedFile, UnshebangedFile, ShebangNotFoundError


def warn(msg):
    # type: (str) -> None
    """prints a warning to stderr"""

    print("WARNING: %s" % msg, file=sys.stderr)


def error(err, exit_code=1):
    # type: (BaseException or str, int) -> None
    """prints an error to stderr and exits
    :param err: the exception that happened
    :param exit_code: the exit code to exit with
    """

    if isinstance(err, BaseException):
        format = "ERROR: %(error)s: %(msg)s"
    elif isinstance(err, str):
        format = "ERROR: %(msg)s"
    else:
        raise TypeError()
    print(("\n" + format) % dict(error=type(err).__name__, msg=err))
    sys.exit(exit_code)


def main(args_=None):
    """The main entry for the whole thing."""

    parser = argparse.ArgumentParser(
        description="A small utility helps in adding the appropriate shebang to FILEs.",
        add_help=False,
        usage="%s [OPTIONS] [FILE ...]" % ("putshebang" if __name__ == '__main__' else "%(prog)s")
    )

    arguments = parser.add_argument_group("Arguments")
    arguments.add_argument("file", metavar="FILE", nargs=argparse.ZERO_OR_MORE,
                           # it's actually one or more, but the interface does't allow that
                           help="name of the file(s)")

    info = parser.add_argument_group("INFO")
    info.add_argument("-k", "--known", action="store_true", help="print known extensions")
    info.add_argument("-v", "--version", action="version", version="%(prog)s: {}".format(__version__))
    info.add_argument("-h", "--help", action="help", help="show this help message and exit")

    edit = parser.add_argument_group("EDITING")

    edit.add_argument("-x", "--executable", action="store_true",
                      help="make the file executable")
    edit.add_argument("-s", "--strict", action="store_true",
                      help="don't create the file if it doesn't exist")
    edit.add_argument("-o", "--overwrite", action="store_true",
                      help="overwrite the shebang if it's pointing to a wrong interpreter")
    edit.add_argument("-d", "--default", action="store_true",
                      help="use the default shebang")
    edit.add_argument("-F", "--no-symlinks", action="store_true",
                      help="don't get symlinks of paths that are already available")
    edit.add_argument("-l", "--lang", metavar="LANG",
                      help="forces the name of the language's interpreter to be LANG")
    edit.add_argument("-n", "--newline", metavar="N", type=int, default=1,
                      help="number of newlines to be put after the shebang; default is 1")

    args = parser.parse_args(args=args_)

    # return status
    rs = 0
    if args.known:
        ShebangedFile.print_known(args.no_symlinks)
        return rs

    if args.file is None:
        error(argparse.ArgumentError(args.file, "this argument is required"), 2)

    sf = None
    for f in args.file:
        try:
            sf = ShebangedFile(UnshebangedFile(f, args.strict, args.executable))
            (interpreters,
             paths) = ShebangedFile.get_interpreter_path(sf.file.name, args.lang, get_versions=True,
                                                         get_symlinks=not args.no_symlinks)

            all_paths = paths.get("all")
            all_inters = interpreters.get("all")
            if all_paths is None:
                if all_inters is None:
                    raise ShebangNotFoundError(
                        "The file name extension is not associated with any known interpreter name"
                    )
                else:
                    s = '(' + re.sub(", (.+)$", "or \1", str(all_inters)[1:-1]) + ')'
                    raise ShebangNotFoundError("Interpreter for %s not found in this machine's PATH" % s)

            if args.default or len(all_inters) == 1:
                path = paths["default"]
                if not path:
                    raise ShebangNotFoundError("Default interpreter not found on this machine's PATH")
            else:
                l = len(all_inters)  # saving resources
                print("Found %d interpreters for file %r: " % (l, sf.file.name))
                for n, s in zip(range(1, l + 1), all_paths):
                    print("\t[%d]: %s" % (n, s))

                r = int(input("Choose one of the above paths [1-%d] (default is 1): " % l) or 1)
                path = all_paths[r - 1]

            sf.shebang = "#!{}\n".format(path)
        except Exception as e:
            if sf is not None and sf.file.created:
                os.remove(sf.file.name)
            warn("File: {}: ".format(f) + str(e))
            rs = 1
            continue
        except KeyboardInterrupt:
            if sf is not None and sf.file.created:
                os.remove(sf.file.name)
            error(KeyboardInterrupt("Abort!"), 130)

        code = sf.put_shebang(newline_count=args.newline, overwrite=args.overwrite)
        if code == 0:
            sf.file.save()
        elif code == 1:
            warn("File: {}: The correct shebang is already there.".format(sf.file.name))
            rs = 0
        elif code == 2:
            warn("File: {}: There's a shebang, but it's pointing to a wrong interpreter, "
                 "use the option --overwrite to overwrite it".format(sf.file.name))
            rs = 1
    return rs


if __name__ == "__main__":
    main()
