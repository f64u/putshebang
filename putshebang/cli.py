# -*- coding: utf-8 -*-
import click
import sys
from putshebang import ShebangedFile, UnshebangedFile, _ShebangNotFoundException
"""Console script for shebang."""


@click.command()
@click.argument("file", metavar="<FILE>")
@click.option("-x", "--executable", is_flag=True, help="make the file executable", default=False)
@click.option("-s", "--strict", is_flag=True, help="don't create the file if it doesn't exist", default=False)
@click.option("-o", "--overwrite", is_flag=True, default=False)
@click.option("-l", "--lang", metavar="LANG", help="forces the name of the language interpreter to be LANG")
@click.option("-n", "--newline", metavar='N', default=1, help="number of newlines to be put after the shebang,\
              defaults to 1")
def main(file, executable, strict, overwrite, lang, newline):
    """A small utility helps in adding the appropriate shebang to <FILE>."""
    try:
        shebanged_file = ShebangedFile(UnshebangedFile(file, strict), lang)
    except _ShebangNotFoundException as e:
        print("Error: " + str(e))
        sys.exit(1)

    if not shebanged_file.put_shebang(newline_count=newline, overwrite=overwrite):
        # we want to exit
        sys.exit(1)

    if executable:
        shebanged_file.make_executable()

if __name__ == "__main__":
    main()
