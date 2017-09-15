=====
Usage
=====

To use putshebang in a project:

.. code:: python

    >>> from putshebang import shebang
    >>> shebang("file.py")
    ['#!/usr/bin/python']
    >>> shebang("file.py", get_versions=True)
    ['#!/usr/bin/python3.6', '#!/usr/bin/python2.7']
    >>> shebang("file.py", get_versions=True, get_symlinks=True)
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
