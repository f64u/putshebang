=====
Usage
=====

To use putshebang in a script :

.. code-block:: python

    >>> from putshebang import shebang
    >>> shebang("file.py")
    ['#!/usr/bin/python3.6', '#!/usr/bin/pypy3', '#!/opt/jython/bin/jython', '#!/usr/bin/ipython3']
    >>> shebang("file.py", get_versions=True)
    ['#!/usr/bin/python3.6', ..., '#!/usr/bin/python2', '#!/usr/bin/python', ..., '#!/usr/bin/pypy3', '#!/usr/bin/pypy', '#!/opt/jython/bin/jython', ...]
    >>> shebang("file.py", get_versions=True, get_links=2)
    ['#!/usr/bin/python3.6', '#!/usr/bin/python2.7', '#!/usr/bin/pypy3', '#!/usr/bin/pypy', '#!/opt/jython/bin/jython', '#!/usr/bin/ipython3',  ...]
    >>> shebang("file.rb")
    ["#!/usr/bin/ruby"]
    >>> shebang("file.rb", get_versions=True)
    ["#!/usr/bin/ruby"]
    >>> shebang("file.php")
    []


To use putshebang as a command-line utility:

.. code-block:: console

    $ cat file.py
    print("Hello, World")

    $ putshebang file.py
    [-] Found 11 interpreters for file 'file.py':
        [1]: /usr/bin/python3.6 (default for the extension '.py')
        [2]: /usr/bin/python3
        [3]: /usr/bin/python2.7
        [4]: /usr/bin/python2
        [5]: /usr/bin/python
        [6]: /usr/bin/pypy3 (default for interpreter 'pypy')
        [7]: /usr/bin/pypy
        [8]: /opt/jython/bin/jython (default for interpreter 'jython')
        [9]: /usr/bin/ipython3 (default for interpreter 'ipython')
        [10]: /usr/bin/ipython2
        [11]: /usr/bin/ipython

    Choose one of the above paths [1-11] ([ENTER] is the same as -d): 3
    $ cat file.py
    #!/usr/bin/python2.7

    print("Hello, World")

    $ putshebang --no-links 2 file.py
    [-] Found 8 interpreters for file 'file.py':
        [1]: /usr/bin/python3.6 (default for the extension '.py')
        [2]: /usr/bin/python2.7
        [3]: /usr/bin/pypy3 (default for interpreter 'pypy')
        [4]: /usr/bin/pypy
        [5]: /opt/jython/bin/jython (default for interpreter 'jython')
        [6]: /usr/bin/ipython3 (default for interpreter 'ipython')
        [7]: /usr/bin/ipython2
        [8]: /usr/bin/ipython

    Choose one of the above paths [1-8] ([ENTER] is the same as -d): 4

    [*] WARNING: file: file.py: There's a shebang in the file, but it's pointing to a wrong interpreter
    [-] use the option --overwrite to overwrite it
    $ putshebang -d --overwrite file.py
    $ # --default (which is the -d above) will use the `default for extension' interpreter, however, it has more
    $ # functionality than that when -l (--lang) option is specified (all of that exists in the help)
    $ cat file.py
    #!/usr/bin/python3.6

    print("Hello, World")

    $ putshebang file.rb
    $ # no output because there's only one interpreter for '.rb' on this machine
    $ cat file.rb
    #!/usr/bin/ruby

    $ putshebang file.php

    [*] WARNING: file: file.php: Interpreter for ('php') not found in this machine's PATH
    $
