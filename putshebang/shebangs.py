# -*- coding: utf-8 -*-

"""Main module."""

from __future__ import print_function as _

import glob as _glob
import os as _os
import re as _re
import sys as _sys
from collections import namedtuple as _nt

from typing import List, Dict
from wcwidth import wcswidth as _wcswidth

from putshebang._data import Data as _Data


# compatibility
if _sys.version_info.major < 3:
    input = raw_input


# ========================== Some Utilities ==========================
def which(cmd):
    # type: (str) -> List[str]
    """Like shutil.which, but uses globs, and less features."""

    paths = _os.environ.get("PATH", _os.defpath).split(":")
    l = []
    for path in paths:
        abs_path = _os.path.join(path, cmd)
        g = list(filter(lambda f: (not _os.path.isdir(f) and _os.access(f, _os.F_OK | _os.X_OK)), _glob.glob(abs_path)))
        if len(g) != 0:
            l.extend(g)
    return l


class Style:
    """Decorator of text, mainly used as a callable"""

    def __init__(self, others=None):
        # type: (Dict) -> ...
        """Constructor.
        
        :param others: other colors to add
        """
        c = dict(
            list(zip([
                'DR',  # Dark Red
                'R',  # Red
                'G',  # Green
                'Y',  # Yellow
                'B',  # Blue
                'M',  # Magenta
                'C',  # Cyan
                'GR',  # Grey
            ],
                list(map(lambda n: "\033[%dm" % n, range(30, 38)))
            ))
        )
        c.update({"W": "\033[0m",  # normal
                  "BO": "\033[1m",  # bold
                  })

        self.colors = c

        # disable the colors
        if _os.getenv('ANSI_COLORS_DISABLED') is not None:
            self.colors = {color: '' for color in self.colors}

        b = {"ERR": "{R}[{Y}!{R}]{W}",
             "WARN": "{R}[{Y}*{R}]{W}",
             "INFO": "{G}[{Y}-{G}]{GR}",
             }
        self.beginnings = dict(map(lambda e: (e[0], e[1].format(**c)), b.items()))

        a = self.colors.copy()
        a.update(self.beginnings)
        if others is not None:
            a.update(others)
        self.all_of_them = a

    def __call__(self, text, **otherkeys):
        d = self.all_of_them.copy()
        d.update(otherkeys)
        text += "{W}"
        return text.format(**d)

style = Style()


def _get_terminal_size():
    import os
    env = os.environ

    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
                                                 '1234'))
        except:
            return
        return cr

    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))
    return int(cr[1]), int(cr[0])
# =====================================================================


class ShebangNotFoundError(Exception):
    pass


Extension = _nt("Extension", ["name", "interpreters"])
Extension.__doc__ = "The extension that will have all the associated interpreters."


class Interpreter(object):
    """The Interpreter"""

    def __init__(self, name, version='', extension='', default=False, paths=None):
        # type: (str, str, str, bool, List[InterpreterPath]) -> None
        """Constructor.
        
        :param name: the name of the interpreter
        :param version: the version of it (if desired)
        :param extension: the extension it's associated with
        :param default: whether it's considered a default interpreter or not
        :param paths: the paths that have been found of it
        """
        self.name = name
        self.extension = extension
        self.version = version
        self.default = default
        self.default_path = InterpreterPath('', default_for_inter=True)
        if paths is None:
            self.paths = []
        else:
            self.paths = paths
        # its old path
        self.backup = None

    @property
    def all_paths(self):
        return sorted(self.paths + [self.default_path] if self.default_path.path else [], reverse=True)

    @property
    def real_paths(self):
        l = []
        for i in self.all_paths:
            add = True
            for j in l:
                if i.realpath == j.realpath:
                    add = False
                    break
            if add:
                l.append(i)
        return l

    def realize_paths(self):
        """Makes all the paths real (rebasing links) and makes a backup for them"""
        self.backup = {"default": self.default_path, "paths": self.paths}

        self.default_path = InterpreterPath(self.default_path.realpath,
                                            self.default_path.default_for_inter,
                                            self.default_path.default_for_ext)

        self.paths = [InterpreterPath(p.realpath, p.default_for_ext, p.default_for_inter) for p in self.paths]

    def get_path(self, path):
        # type: (str) -> InterpreterPath

        for i in self.paths:
            if i.path == path:
                return i

    def __eq__(self, other):
        if isinstance(other, str):
            return bool(_re.match(r'{}-?{}'.format(self.name, self.extension), other))
        elif isinstance(other, Interpreter):
            return str(self) == str(other)
        else:
            raise TypeError("Cannot compare %r and %r" % (type(self).__name__, type(other).__name__))

    def __str__(self):
        return "".join((self.name, self.version))

    def __repr__(self):
        return '<%s name=%r, extension=%r, paths=%r, default=%r, default_path=%r>' % \
               (type(self).__name__, str(self), self.extension, self.paths, self.default, self.default_path)


class InterpreterPath(object):
    """The interpreter's path and its state."""

    def __init__(self, path, default_for_inter=False, default_for_file=False, default_for_ext=False):
        # type: (str, bool, bool, bool) -> None
        """Constructor.
        :param path: the path of the interpreter
        :param default_for_inter: whether it's the default interpreter or not
        :param default_for_file: whether it's a default for specific file at run time
                                (as specified by the `interpreter' parameter in the `get_extension' function)
        :param default_for_ext: whether it's the default for an extension or not
        """

        self._path = path
        self.executable = _os.path.basename(self.path)
        self.default_for_ext = default_for_ext
        self.default_for_inter = default_for_inter
        self.default_for_file = default_for_file
        self.islink = _os.path.islink(path)
        self.realpath = _os.path.realpath(path) if path else ''

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, val):
        self._path = val
        self.islink = _os.path.islink(val)
        self.realpath = _os.path.realpath(val)

    def __str__(self):
        return str(self.path)

    def __repr__(self):
        return ('<%s path=%r, default_for_ext=%r, default_for_file=%r, default_for_inter=%r, islink=%r, realpath=%r>'
                % (type(self).__name__, self.path, self.default_for_ext, self.default_for_file, self.default_for_inter,
                   self.islink, self.realpath))

    def __eq__(self, other):
        return self.path == other.path

    def __gt__(self, other):
        return self.path > other.path

    def __lt__(self, other):
        return self.path < other.path

    def __hash__(self):
        return hash(self.path)


class UnshebangedFile(object):
    """The file that requires the shebang.

    Generally, it should only be used when it's passed to the `ShebangedFile` constructor
    """

    def __init__(self, name, strict=False, make_executable=False):
        # type: (str, bool, bool) -> None
        """Constructor.

        :param name: name of the file to operate on
        :param strict: a bool specifies the creatability
        :param make_executable: a bool specifies whether make the file executable or not (obviously)
        """

        if not name:
            raise ValueError("name can not be %r" % name)

        self.name = name
        try:
            self._extension = _re.findall("\.(.+)$", self.name)[0]
        except IndexError:
            self._extension = ''
        self.contents = ''
        self.created = False  # to delete it if we want to

        if _os.path.exists(self.name):
            if not _os.path.isfile(self.name):
                raise ValueError("file name {!r} is not valid".format(self.name))

            with open(self.name) as f:
                self.contents = f.read()
        else:
            if strict:
                raise ValueError("file name doesn't exist")
            self.create()

        if make_executable:
            self.make_executable()

    def create(self):
        # type: () -> None
        """create an empty file of the object's name, setting self.created into True."""
        self.created = True
        with open(self.name, 'w') as f:
            f.write('')

    def save(self):
        with open(self.name, 'w') as f:
            f.write(self.contents)

    def make_executable(self):
        # type: () -> None
        """change the stat of the object's file name to be executable

        Example:
             -rw-rw-rw- becomes -rwxrwxrwx
             -rw------ becomes -rwx------
        """
        mode = _os.stat(self.name).st_mode
        mode |= (mode & 0o444) >> 2
        _os.chmod(self.name, mode)


class ShebangedFile(object):
    """The file that will implement the required shebang.
    
    basic usage:
        >>> sf = ShebangedFile(UnshebangedFile("file.py"))
        >>> sf.put_shebang()
        0
        >>> print(sf.shebang)
        #!/usr/bin/python
        <BLANKLINE>
        >>> sf.file.make_executable()
        >>> sf.shebang = "#!/usr/bin/ruby\\n"
        >>> sf.put_shebang()
        0
        >>> print(sf.shebang)
        #!/usr/bin/ruby
        <BLANKLINE>
        >>> sf.file.save()        
    """

    ALL_INTERS = _Data.load()

    def __init__(self, unshebanged_file):
        # type: (UnshebangedFile) -> None
        """Constructor.
        :param unshebanged_file: the file to add the shebang into
        """
        self.file = unshebanged_file
        try:
            self.shebang = "#!{}\n".format(which(ShebangedFile.ALL_INTERS[self.file._extension]["default"]["name"])[0])
        except (IndexError, KeyError):
            self.shebang = ''

    def put_shebang(self, newline_count=1, overwrite=True):
        # type: (int, bool) -> int
        """Puts the shebang on the first line of self.file plus ('\n' * newline_count).
        
        :param newline_count: number of '\n' appended after the shebang
        :param overwrite: overwrite if it's a broken shebang
        :return: what check_shebang returns
        """

        code = self.check_shebang()
        if code == 1:
            return code
        elif code == 2:
            if overwrite:
                self.remove_shebang()
            else:
                return code

        self.file.contents = (self.shebang + '\n' * newline_count) + self.file.contents
        return 0

    def remove_shebang(self):
        # type: () -> bool
        """Removes the shebang line from the file plus any whitespaces.
        
        :return: True -> successfully removed the shebang
                 False - did nothing
        """
        con = self.file.contents  # just an alias
        if con.startswith("#!"):
            con = con[con.find('\n') + 1:]
            self.file.contents = _re.sub("^\s*", '', con)
            return True

        return False

    def check_shebang(self):
        # type: (bool) -> int
        """Checks if a shebang does exist and reports its state. 
        
        :return:
            2 -> There's a shebang, but it's pointing to a wrong interpreter
            1 -> The correct the shebang is already there
            0 -> Don't care..
        """

        con = self.file.contents
        if con.startswith(self.shebang[:-1]):
            return 1

        elif con.startswith("#!"):
            return 2

        return 0

    def get_extension(self=None, file_name=None, interpreter=None, get_versions=False, get_links=0):
        # type: (str, str, bool, int) -> Extension
        """Get the extension of the file.

        This method can be called as a static method be specifying the `file_name` parameter
        and can be called on the object itself. If called by both `file_name` will take precedence.

        :param file_name: get the extension based on `file_name' rather than the actual file name
        :param interpreter: get extension based on the interpreter name (higher precedence than the file name (both))
        :param get_versions: get available versions of interpreters (however, if false, if `interpreter' or
                            `the default interpreter' contains a version, you'll receive it)
        :param get_links: 0 means you'll get every thing as found on PATH (no action taken for links
                          1 means don't get links but get real paths even if they're not in PATHS
                          2 means same as 1 but exclude the ones that are not in PATH (that also means the ones already
                            exist (no multiple references for the same file))
        :return: An `Extension' with it's all associated interpreters
        """

        if get_links not in range(0, 3):
            raise ValueError('get_links must be in the range of 0..2')
        if self is None and file_name is None:
            raise ValueError("either call it on a ShebangedFile object and/or specify the file name")

        if file_name is None:
            file_name = self.file.name

        version_regex = r'^%s-?(\d{1,4}(\.\d{1,2}(\.\d)?)?)?$'
        found_regex = r'^{}-?{}$'
        all_data = ShebangedFile.ALL_INTERS

        extension = ''
        pref_inter = {}
        # FIXME: we don't take action if `interpreter` itself is not associated with any extension and there's an
        #        extension in the file name
        if interpreter is not None:
            comeout = False
            given_name, given_version = _re.findall(version_regex % '(\w+)', interpreter)[0][:2]
            for ext in all_data:
                if comeout:
                    break

                entry = all_data[ext]
                default_inter = entry["default"]
                other_inters = entry["others"]
                all_inters = [default_inter] + other_inters
                for path in all_inters:
                    if path["name"] == given_name:
                        # the interpreter that the user 'prefers', it will be returned in the `others' key of the
                        # interpreters
                        pref_inter = {"name": given_name, "version": given_version, "isfound": True}
                        extension = ext
                        comeout = True
                        break
            else:
                # not found associated with any extension, then this interpreter is the only returned one
                pref_inter = {"name": given_name, "version": given_version, "isfound": False}

        # that means that interpreter wasn't 'found' or it wasn't set
        if not pref_inter:
            try:
                extension = _re.findall("\.(.+)$", file_name)[0]
            except IndexError:
                # couldn't find the extension in the file file_name, if we have the interpreter, just grab it and
                # its versions if required
                # NOTE: we won't do anything about links now, may be I should think of that
                ext = None
                if pref_inter:
                    try:
                        path = which(interpreter)[0]
                    except IndexError:
                        pass
                    else:
                        p = InterpreterPath(path, default_for_file=True)
                        inter = Interpreter(pref_inter["name"], pref_inter["version"])
                        inter.default_path = p
                        if get_versions:
                            for path in which(pref_inter["name"] + '*'):
                                if _re.match(version_regex % pref_inter["name"], _os.path.basename(path)):
                                    inter.paths.append(InterpreterPath(path))

                        ext = Extension('', interpreters={"default": None, "others": [inter]})
                if ext is None:
                    ext = Extension('', {"default": None, "others": []})
                return ext

        try:
            interpreters = all_data[extension]
            default = interpreters["default"]
            others = interpreters["others"]
        except KeyError:
            return Extension('', {"default": None, "others": []})

        default = Interpreter(extension=extension, default=True, **default)
        others = [Interpreter(extension=extension, **i) for i in others]
        interpreters = {"default": default, "others": others}

        if not get_versions:
            # we don't need it's function, so None it.
            version_regex = ''

        # === collecting all of the wanted data and storing them in the objects ===
        all_data = [interpreters["default"]] + interpreters["others"]
        for inter in all_data:

            # that would match all of python, python3.6, python-3.6
            # (`python' because `inter.version' might be empty)
            inter_regex = _re.compile(found_regex.format(inter.name, inter.version))

            seedefault = True
            seeprefered = pref_inter != {}
            for path in which(inter.name + "*"):
                executable = _os.path.basename(path)
                if seedefault and inter_regex.match(executable):
                    if inter == interpreters["default"]:
                        defpath = InterpreterPath(path, default_for_inter=True, default_for_ext=True)
                    else:
                        defpath = InterpreterPath(path, default_for_inter=True)
                    inter.default_path = defpath
                    seedefault = False
                elif seeprefered and _re.match(found_regex.format(pref_inter["name"], pref_inter["version"]),
                                               executable):
                    inter.paths.append(InterpreterPath(path, default_for_file=True))
                    seeprefered = False
                elif version_regex and _re.match(version_regex % inter.name, executable):
                    inter.paths.append(InterpreterPath(path))
        # =========================================================================

        if get_links == 1:
            for path in all_data:
                path.realize_paths()

        elif get_links == 2:
            for path in all_data:
                for p in path.paths[:]:
                    if p.islink and p.realpath in [s.path for s in path.all_paths]:
                        path.paths.remove(p)

        seen = set()
        defaults = {i.default_path for i in all_data}
        for path in all_data:
            defaults.add(path.default_path)
            for p in path.paths[:]:
                if p in seen or p in defaults:
                    path.paths.remove(p)
                seen.add(p)

        return Extension(name=extension, interpreters=interpreters)

    @staticmethod
    def print_known(get_links, format='tree'):
        """Prints a nice formatted string of known interpreters.
        
        :param get_links: 0 means you'll get every thing as found on PATH (no action taken for links
                          1 means don't get links but get real paths even if they're not in PATHS
                          2 means same as 1 but exclude the ones that are not in PATH (that also means the ones already
                            exist (no multiple references for the same file))
        :param format: the format of the output, can either be 'tree' or 'table'
        """
        import tabulate

        def _format_table(interpreters):
            inters = []
            inter_counter = 0
            all_inters = [interpreters["default"]] + interpreters["others"]
            for i in all_inters:
                path_counter = 0
                keyname = style("{C}" + i.name)
                inters.append({keyname: ''})
                for p in i.all_paths:
                    inters[inter_counter][keyname] += style("{B}" + p.path)
                    default = ''
                    if i.default and p.default_for_ext:
                        default = style(" {GR}(default for the extension {BO}{G}'.{ext}'{GR})", ext=i.extension)
                    elif p.default_for_inter:
                        default = style(' {GR}(default for the interpreter {BO}{G}{inter!r}{GR})', inter=str(i.name))

                    inters[inter_counter][keyname] += default
                    inters[inter_counter][keyname] += style('{Y}, ')
                    path_counter += 1

                inters[inter_counter][keyname] = (style('{Y}[ ')
                                                  + inters[inter_counter][keyname][:-len(style("{Y}, "))])
                inters[inter_counter][keyname] += style(" {Y}]")

                if path_counter >= 2:
                    inters[inter_counter][keyname] = " and".join(inters[inter_counter][keyname].rsplit(',', 1))

                inter_counter += 1

            return inters

        if format == 'table':
            rehearsal = 0
            headers = (style("{G}Interpreter Name"), style("{G}Available Path(s)"))
            while True:
                rehearsal += 1
                tables = ""
                for i in ShebangedFile.ALL_INTERS.keys():
                    extension = ShebangedFile.get_extension(file_name="file."+i, get_versions=True, get_links=get_links)
                    inters = _format_table(extension.interpreters)

                    tables += style("{INFO} Extension: {G}'.{ext}'\n", ext=extension.name)
                    data = [(inter, paths) for i in range(len(inters)) for inter, paths in inters[i].items()]
                    tables += tabulate.tabulate(data, headers=headers, tablefmt="fancy_grid") + "\n\n"

                max_col = max([_wcswidth(i) for i in tables.split('\n')])

                if _get_terminal_size()[0] < max_col:
                    if rehearsal == 1:
                        print(style("{WARN} {GR}Your terminal won't fit for the whole table"))
                        print(style("{INFO} {GR}Removing path links"))
                        print()
                        get_links = 2
                        continue
                    elif rehearsal == 2:
                        print(style("{WARN} {GR}Your terminal still won't fit for the whole table"))
                        print(style("{INFO} {GR}Try using the 'tree' format which doesn't occupy a lot of columns"))
                        break

                # we got here finally
                print(tables)
                break

        elif format == 'tree':
            all_of_it = ''
            for i in ShebangedFile.ALL_INTERS.keys():
                extension = ShebangedFile.get_extension(file_name="file."+i, get_versions=True, get_links=get_links)
                inters = extension.interpreters
                interpreter_counter = 1

                all_of_it += style("{INFO} Extension: {G}'.{ext}'\n", ext=extension.name)
                for i in [inters["default"]] + inters["others"]:
                    all_of_it += style("\t{Y}[{G}{n}{Y}]{GR}: {C}" + i.name + "{W}:\n",
                                       n=interpreter_counter)
                    path_counter = 1
                    for p in i.all_paths:
                        default = ''
                        if i.default and p.default_for_ext:
                            default = style(" {GR}(default for the extension {BO}{G}'.{ext}'{GR})", ext=i.extension)
                        elif p.default_for_inter:
                            default = style(' {GR}(default for the interpreter {BO}{G}{inter!r}{GR})',
                                            inter=str(i.name))
                        all_of_it += style("\t\t{Y}[{G}{n}{Y}]{GR}: {B}" + p.path + default
                                           + (style(" {Y}(links to {BO}{B}{p}{Y})", p=p.realpath) if p.islink
                                              else '')
                                           + "\n", n=path_counter)
                        path_counter += 1

                    if path_counter == 1:
                        all_of_it += style("\t\t{M}...\n")

                    all_of_it += "\n"
                    interpreter_counter += 1

            print(all_of_it)
        else:
            raise ValueError("format can be either 'tree' or 'table'")
