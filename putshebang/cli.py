# -*- coding: utf-8 -*-

"""Console script for shebang."""

import argparse
import os
from putshebang.main import ShebangedFile, UnshebangedFile, _warn
from putshebang import __version__


def main():

    parser = argparse.ArgumentParser(
        description="A small utility helps in adding the appropriate shebang to FILEs.",
        add_help=False,
        usage="%(prog)s [OPTIONS] [FILE ...]"
    )

    parser.add_argument("file", metavar="FILE", nargs=argparse.ZERO_OR_MORE, help="name of the file(s)")

    info = parser.add_argument_group("INFO")
    info.add_argument("-k", "--known", action="store_true",  help="print known extensions")
    info.add_argument("-v", "--version", action="version", version="%(prog)s: {}".format(__version__))
    info.add_argument("-h", "--help", action="help", help="show this help message and exit")

    edit = parser.add_argument_group("EDITING")

    edit.add_argument("-x", "--executable", action="store_true",
                      help="make the file executable")
    edit.add_argument("-s", "--strict", action="store_true",
                      help="don't create the file if it doesn't exist")
    edit.add_argument("-o", "--overwrite", action="store_true",
                      help="overwrite the shebang if it's pointing to a wrong interpreter")
    edit.add_argument("-l", "--lang", metavar="LANG",
                      help="forces the name of the language interpreter to be LANG")
    edit.add_argument("-n", "--newline", metavar="N", type=int, default=1,
                      help="number of newlines to be put after the shebang; default is 1")

    args = parser.parse_args()

    rs = 0
    if args.known:
        ShebangedFile.print_known()
        return rs

    if len(args.file) == 0:
        # that's logically wrong, but it's easier :^)
        parser.exit(2, "error: the following argument is required: FILE\n")

    for f in args.file:
        try:
            usf = UnshebangedFile(f, args.strict, args.executable)
            shebanged_file = ShebangedFile(usf, args.lang)
        except Exception as e:
            if usf.created:
                os.remove(usf.name)
            _warn("File: {}: ".format(f) + str(e))
            rs = 1
            continue
        except KeyboardInterrupt:
            if usf.created:
                os.remove(usf.name)
            parser.exit(130, "\nAbort!\n")

        if not shebanged_file.put_shebang(newline_count=args.newline, overwrite=args.overwrite):
            # some error happened
            if usf.created:
                os.remove(f)
            rs = 1
            continue
    return rs

if __name__ == "__main__":
    main()
