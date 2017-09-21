# -*- coding: utf-8 -*-

"""Console script for shebang."""
from __future__ import print_function

import argparse
import os
import re
import sys

from putshebang import __version__
from putshebang.shebangs import ShebangedFile, UnshebangedFile, ShebangNotFoundError, style


def info(msg):
    # type: (str) -> None
    """prints an info string to the stdout"""
    print(style("\n{INFO} {B}INFO{W}: {GR}{msg}", msg=msg))


def warn(msg):
    # type: (str) -> None
    """prints a warning to stderr"""

    print(style("\n{WARN} {R}WARNING{W}: {GR}{msg}", msg=msg),
          file=sys.stderr)


def error(err, exit_code=1):
    # type: (BaseException or str, int) -> None
    """prints an error to stderr and exits
    :param err: the exception that happened
    :param exit_code: the exit code to exit with
    """

    if isinstance(err, BaseException):
        fmt_str = "{Y}ERROR{Y}: {R}{error}{W}: {GR}{msg}"
    elif isinstance(err, str):
        fmt_str = "{Y}ERROR{W}: {GR}{msg}"
    else:
        raise TypeError()
    fmt_str = style(fmt_str, error=type(err).__name__, msg=err)
    print(style("\n{ERR} ") + fmt_str, file=sys.stderr)
    sys.exit(exit_code)


def cleanup(shebanged_file):
    # type: (ShebangedFile) -> None
    if shebanged_file is not None and shebanged_file.file.created:
        os.remove(shebanged_file.file.name)


def main(args_=None):
    """The main entry for the whole thing."""

    parser = argparse.ArgumentParser(
        description="A small utility helps in adding the appropriate shebang to FILEs.",
        add_help=False,
        usage="%s [OPTIONS] [FILE ...]" % ("putshebang" if __name__ == 'putshebang.cli' else "%(prog)s")
    )

    arguments = parser.add_argument_group("Arguments")
    arguments.add_argument("file", metavar="FILE", nargs=argparse.ZERO_OR_MORE,
                           # it's actually one or more, but the interface does't allow that
                           help="name of the file(s)")

    info_g = parser.add_argument_group("INFO")
    info_g.add_argument("-k", "--known", metavar="FORMAT",
                        help="print known extensions in the format of a FORMAT, "
                             "FORMAT can be 'tree' or 'table'")
    info_g.add_argument("-v", "--version", action="version", version="%(prog)s: {}".format(__version__))
    info_g.add_argument("-h", "--help", action="help", help="show this help message and exit")

    edit_g = parser.add_argument_group("EDITING")
    edit_g.add_argument("-x", "--executable", action="store_true",
                        help="make the file executable")
    edit_g.add_argument("-s", "--strict", action="store_true",
                        help="don't create the file if it doesn't exist")
    edit_g.add_argument("-o", "--overwrite", action="store_true",
                        help="overwrite the shebang if it's pointing to a wrong interpreter")
    edit_g.add_argument("-d", "--default", action="store_true",
                        help="use the default interpreter, "
                             "Firstly it will look for the path of the passed --lang, if not specified, "
                             "use the default for the extension")
    edit_g.add_argument("-F", "--no-links", metavar="MODE", default=0, type=int,
                        help="0 means you'll get every thing as found on PATH (no action taken for links), "
                             "1 means don't get links but get real paths even if they're not in PATHS, "
                             "2 means the same as 1 but exclude the ones that are not in PATH; default is 0, "
                             "however, 2 is recommended")
    edit_g.add_argument("-l", "--lang", metavar="LANG",
                        help="forces the name of the language's interpreter to be LANG")
    edit_g.add_argument("-n", "--newline", metavar="N", type=int, default=1,
                        help="number of newlines to be put after the shebang; default is 1")

    # data_g = parser.add_argument_group("DATA")
    # data_g.add_argument("-a", "--add", metavar="ext=inter")

    args = parser.parse_args(args=args_)

    # return status
    rs = 0
    if args.known:
        ShebangedFile.print_known(args.no_links, args.known)
        return rs

    if not args.file:
        parser.print_usage()
        error(argparse.ArgumentError(None, "FILE is required"), 2)

    sf = None
    for f in args.file:
        try:
            sf = ShebangedFile(UnshebangedFile(f, args.strict, args.executable))
            extension = sf.get_extension(interpreter=args.lang, get_versions=True,
                                         get_links=args.no_links)
            interpreters = extension.interpreters

            default_inter = interpreters["default"]
            all_inters = ([default_inter] if default_inter else []) + interpreters["others"]
            if not all_inters:
                raise ShebangNotFoundError(
                    "the file name extension is not associated with any known interpreter name"
                )

            all_paths = [p for i in [p.all_paths for p in all_inters] for p in i]
            if not all_paths:
                s = '(' + re.sub(", (.+)$", "or \1", str([str(i) for i in all_inters])[1:-1]) + ')'
                raise ShebangNotFoundError("interpreter for %s is not found in this machine's PATH" % s)

            default_path = ''
            comeout = False
            for i in all_inters:
                if comeout:
                    break
                for p in i.paths:
                    if p.default_for_file:
                        default_path = p.path
                        comeout = True
                        break
            if not default_path:
                if default_inter:
                    default_path = default_inter.default_path.path

            if args.default or len(all_paths) == 1:
                if not default_path:
                    raise ShebangNotFoundError("default interpreter not found on this machine's PATH")
                path = default_path
            else:
                print(style(
                    "{INFO} Found {G}{n}{GR} interpreters for file {C}{file!r}{GR}: ", n=len(all_paths), file=f
                ))

                n = 1
                for i in all_inters:
                    for p in i.all_paths:
                        default = ''
                        if p.default_for_ext:
                            default = style(" {M}(default for the extension {G}'.{ext}'{M})", ext=i.extension)
                        elif p.default_for_file:
                            default = style(" {M}(the default specified)")
                        elif p.default_for_inter:
                            default = style(' {M}(default for interpreter {G}{inter!r}{M})', inter=str(i.name))

                        print(style("\t{Y}[{G}{n}{Y}]{GR}: {B}{path}" + default,
                                    n=n, path=p.path))
                        n += 1

                print()
                r = input(style(
                    "{GR}Choose one of the above paths {Y}[{G}1{Y}-{G}{n}{Y}] {GR}({G}[{R}ENTER{G}]{GR}"
                    " is the same as {Y}-d{GR}): ",
                    n=n - 1)
                )

                if r == '':
                    path = default_path
                else:
                    path = all_paths[int(r) - 1]

            sf.shebang = "#!{}\n".format(path)
        except Exception as e:
            cleanup(sf)
            warn(style("file: {G}{file}{W}: {GR}{msg}", file=f, msg=e))
            rs = 1
            continue
        except KeyboardInterrupt:
            cleanup(sf)
            error(KeyboardInterrupt("Abort!"), 130)
        except BaseException as e:
            cleanup(sf)
            error(e, 2)

        code = sf.put_shebang(newline_count=args.newline, overwrite=args.overwrite)
        if code == 0:
            sf.file.save()
        elif code == 1:
            info(style("file: {G}{file}{W}: {GR}the correct shebang is already there.", file=f))
            rs = 0
        elif code == 2:
            warn(style(
                "file: {G}{file}{W}: {GR}There's a shebang in the file, but it's pointing to a wrong interpreter\n"
                "{INFO} use the option {G}--overwrite{GR} to overwrite it", file=f
            ))
            rs = 1
    return rs


if __name__ == "__main__":
    main()
