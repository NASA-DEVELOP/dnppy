Building Docs
=============

One of the most important aspects of writing good software is documentation. This website is generated automatically from the source files in ``dnppy/docs/source`` with `Sphinx`_ and `graphviz`_. You can click on the "View page source" button in the top right corner to see the source code used to build this web page! Neat!

.. rubric:: Documentation source

These documentation pages are made into pretty html and css from a couple of different sources. The first of which are ``.rst`` files typed with `reStructuredText`_ markup. These files are all found in the ``docs/source`` folder, and the structure looks something like this::

    /source
        /_static
            <static content such as images>
        /dev_pages
            <rst files directed towards developers>
        /modules
            <one rst file for each module of dnppy>
        /trub
            <rst files directed at help and reference>
        design.rst
        index.rst
        install.rst
        modulesum.rst
        overview.rst

Documenting new additions
-------------------------

.. rubric:: A new function or class

When you add a new function or class to dnppy, you will have to add a couple lines to that modules ``.rst`` file in the modules folder. These few lines allow sphinx to parse the docstrings and arguments of that function or class definition and create help pages and add it to the index so users can find it in the search bar.

Its easiest to check the source for these very doc pages.

    1. Take a quick look at the `core module help page`_
    2. Now look at the ``.rst`` file used to `generate the core module help page`_. Notice that the entire "Code Help" section consists of just a few repeated calls to the ``automodule`` plugin.
    3. Back on the help page, notice that there is a small "source" button next to every function description.
    4. Now check out the `source code`_ for the ``create_outname`` function.

.. _source code: https://nasa-develop.github.io/dnppy/_modules/dnppy/core/create_outname.html#create_outname
.. _core module help page: https://nasa-develop.github.io/dnppy/modules/core.html
.. _generate the core module help page: https://nasa-develop.github.io/dnppy/_sources/modules/core.txt

You will notice in the source code for the core module help page a statement that looks like:

.. code-block:: rst

    .. automodule:: dnppy.core.create_outname
        :members:

Which invokes the automodule chain and parses the docstrings of the ``create_outname`` function. In order for the parser to successfully produce the pretty outputs, the docstrings should follow syntax such as that listed below.

.. code-block:: python

    def foo(self, x, y):
        """
        Description of function here

        :param int x: parameter x is an integer and does ....
        :param int y: parameter y is an integer and does ....
        :rtype: returns int
        """

For the code above defining a dummy function called ``foo``, the auto documentation tool chain will generate this:

.. py:function:: foo(self, x, y)
  :noindex:

  Description of function here

  :param int x: parameter x is an integer and does...
  :param int y: parameter y is an integer and does...
  :rtype: returns int

Ensure you write descriptive docstrings for your functions, and comment well, which are things you should definitely be doing anyway right? It is worth noting that PyCharm, our recommended IDE, automatically provides tooltips to encourage the user to document to this standard as quickly and easily as possible.

.. rubric:: A new module

When adding a new module to dnppy, you should create a new ``.rst`` file in ``docs/source/modules`` with an "Examples" and a "Code Help" section in the same way the other modules of dnppy are set up.


Checking the docs
-----------------

Once you've made some kind of edit to either a function docstring. We have a quick and dirty script located at ``dev/sphinx_build.py`` that you can run to create a local copy of this website in ``docs/build``. If you've made some substantial changes that you are unsure about, be sure to run this script and fix any warnings sphinx puts out. You can then choose to review your local update of the help doc website by simply opening up ``docs/build/index.html`` in your browser. If you're happy with how it looks here, then you're ready to build the docs.

.. note:: this ``docs/build`` folder is `intentionally` added to the ``.gitignore`` to prevent the master branch commits from getting cluttered with changes that do not need to be tracked. Otherwise, every minor code change would be accompanied by dozens of trivial automatic changes to the html code of these doc pages.


Building the docs
-----------------

Building the docs used to require keeping a local copy of the repository permanently set to use the ``gh-pages`` branch and follow the work-flows that can be found in the section below. However, I'm pleased to inform you that you do `not` need to do any special commits or setup of your development environment to automatically update these doc pages! All doc pages are automatically rebuilt every time someone commits to the master branch!

For reference, we used the following resources to set ourselves up.

    1. `documenting your project with sphinx`_
    2. `A custom built travis-sphinx tool`_
        * https://github.com/NASA-DEVELOP/dnppy/pull/55
        * https://github.com/NASA-DEVELOP/dnppy/pull/57

This process automatically tells `Travis-CI`_ to rebuild the documentation pages every time a commit is pushed to the master branch. This is done according to the `.travis.yml` file. It typically takes less than 2 minutes for the changes to go live.


.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://sphinx-doc.org/
.. _A custom built travis-sphinx tool: https://github.com/Syntaf/travis-sphinx
.. _Travis-CI: https://travis-ci.org/
.. _graphviz: http://www.graphviz.org/
.. _documenting your project with sphinx: https://pythonhosted.org/an_example_pypi_project/sphinx.html

