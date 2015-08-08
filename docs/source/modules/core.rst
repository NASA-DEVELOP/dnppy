core
====

The ``core`` module houses functions that assist in data formatting, input sanitation, path manipulations, file naming, logical checks, etc for use in other functions within ``dnppy``. They are short and sweet, and can be used as examples to start defining your own functions!

Examples
--------

.. rubric:: Listing files in a directory

Perhaps the function with the greatest utility in the core module is the `list_files` function, which can crawl through a directory, or entire tree of directories (recursive) and find files that match a certain criteria in a beginner friendly way. The syntax is as follows

.. code-block:: python

    from dnppy import core

    recursive   = True             # will find files in directories subfolders
    directory   = r"C:\mydir"      # the directory that we would like to search
    contains    = ["this","that"]  # files must contain these strings
    not_contain = ["otherthing"]   # files must NOT contain these strings

    filelist = core.list_files(recursive, directory, contains, not_contain)

Note that both ``contains`` and ``not_contain`` may be either single strings, or lists of strings. This is a good way to filter down by NASA EOS product type, Landsat band index, or perhaps filter out files by extension. Users wishing to get a little more advanced should check out `regular expressions`_.

.. _regular expressions: https://docs.python.org/2/howto/regex.html

Code Help
---------

Auto-documentation for functions and classes within this module is generated below!

.. automodule:: dnppy_install.core
    :members:

.. automodule:: dnppy_install.core.create_outname
    :members:

.. automodule:: dnppy_install.core.enf_filelist
    :members:

.. automodule:: dnppy_install.core.enf_list
    :members:

.. automodule:: dnppy_install.core.exists
    :members:

.. automodule:: dnppy_install.core.install_from_wheel
    :members:

.. automodule:: dnppy_install.core.list_files
    :members:

.. automodule:: dnppy_install.core.move
    :members:

.. automodule:: dnppy_install.core.rename
    :members:
