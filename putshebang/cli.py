# -*- coding: utf-8 -*-
import click
import putshebang
"""Console script for shebang."""


@click.command()
@click.argument("file", metavar="<FILE>")
@click.option("-x", "--executable", is_flag=True, help="make the file executable", default=False)
@click.option("-f", "--force", is_flag=True, help="force the creation of the file if it doesn't exist", default=False)
@click.option("-o", "--overwrite", is_flag=True, default=False)
@click.option("-l", "--lang", metavar="LANG", help="forces the name of the language interpreter to be LANG")
@click.option("-n", "--newline", metavar='N', default=1, help="number of newlines to be put after the shebang,\
              defaults to 1")
def main(file, executable, force, overwrite, lang, newline):
    """A small utility helps in adding the appropriate shebang to <FILE>."""
    shebanged_file = putshebang.ShebangedFile(putshebang.UnshebangedFile(file, force), lang)
    if executable:
        shebanged_file.make_executable()

    shebanged_file.put_shebang(newline_count=newline, overwrite=overwrite)

if __name__ == "__main__":
    main()
