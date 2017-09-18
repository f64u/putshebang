=====
Usage
=====

To use putshebang in a script :

.. code-block:: python

    >>> from putshebang import shebang
    >>> shebang("file.py")
    ['#!/usr/bin/python']
    >>> shebang("file.py", get_versions=True, get_links=2)
    ['#!/usr/bin/python3.6', '#!/usr/bin/python2.7']
    >>> shebang("file.py", get_versions=True, get_links=0)
    ['#!/usr/bin/python3.6', '#!/usr/bin/python3', '#!/usr/bin/python2.7', '#!/usr/bin/python2', '#!/usr/bin/python']
    >>> shebang("file.rb")
    ["#!/usr/bin/ruby"]
    >>> shebang("file.rb", get_versions=True)
    ["#!/usr/bin/ruby"]
    >>> shebang("file.php")
    []


To use putshebang as a command-line utility:

.. code-block:: console

    $ putshebang file.py
    [-] Found 8 interpreters for file 'file.py':
        [1]: /usr/bin/python3.6 (default for extension '.py')
        [2]: /usr/bin/python3
        [3]: /usr/bin/python2.7
        [4]: /usr/bin/python2
        [5]: /usr/bin/python
        [6]: /usr/bin/pypy3 (default for interpreter 'pypy')
        [7]: /usr/bin/pypy
        [8]: /opt/jython/bin/jython (default for interpreter 'jython')

    Choose one of the above paths [1-8] (default is 1): ^C
    [!] ERROR: KeyboardInterrupt: Abort!
    $ putshebang --no-links 2 file.py
    [-] Found 5 interpreters for file 'file.py':
        [1]: /usr/bin/python3.6 (default for extension '.py')
        [2]: /usr/bin/python2.7
        [3]: /usr/bin/pypy3 (default for interpreter 'pypy')
        [4]: /usr/bin/pypy
        [5]: /opt/jython/bin/jython (default for interpreter 'jython')

    Choose one of the above paths [1-5] (default is 1): ^C
    [!] ERROR: KeyboardInterrupt: Abort!
    $ putshebang --default file.py
    $ cat file.py
    #!/usr/bin/python3.6

    $ putshebang file.rb
    $ # no output because there's only one interpreter on this machine
    $ cat file.rb
    #!/usr/bin/ruby

    $

