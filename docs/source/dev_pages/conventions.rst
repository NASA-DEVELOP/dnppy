Coding Conventions
==================

.. note::

   We are now using the ``pep-0008`` style guide as referenced `here`_ . See the link for a full
   list of conventions

Below is a list of general guidelines for style and consistency to keep everything as readable as possible.

.. rubric:: Column Width

Code should be no longer than 100 characters, in the case your statement goes **over**, use a
new line or split your statement up.

.. rubric:: String Literals

String Literals are denoted with ``""`` or ``''``, docstrings should always be triple double quotes ``""``

.. code-block:: python

    var = "I'm a string!"
    var = 'I am also a string!'
    def foo():
        """ Here is a docstring """
        pass


.. rubric:: Variables

Variables should be lowercase and word separated with ``_``

.. code-block:: python

   var = 3
   another_var = 4
   more_words_than_previous_var = 5

.. rubric:: Functions

The same format as Variables, lowercase with ``_`` separating words should be used.

.. code-block:: python

   def func():
      # ...
   def adheres_to_coding_convention_func():
      # ...

.. rubric:: Comments

Simple comments should be placed to the right of the line when possible, or one comment should
be placed above a segment shortly explaining it's purpose

.. code-block:: python

    var = x - y + r * 2         # calculate ___ and place in var
    doFunc(var)                 # do some func with var param
    if var[-1] is not var[:3]:
      err()                     # error is var does not match criteria

    # does this and this and this
    var = x + 2
    x = var - 5
    if var == 0:
      err()


This documentation website is generated using docstrings from source, so **document** as you
code! The docstring markdown is reStructedText Primer and sphinx, when the doc chain is
generated it will use these docstrings from the code for the webpage.

.. code-block:: python

    class Foo(object):
        """
        Class description is placed here

        :param <name>: description of param 'name'
        """

        def __init__(self, name):
            # do some stuff

        def foo(self, x, y):
            """
            Description of function here

            :param int x: parameter x is an integer and does ....
            :param int y: parameter y is an integer and does ....
            :rtype: returns int
            """

The auto documentation tool chain will generate this as:

.. py:class:: Foo
   :noindex:

   Class description is placed here

   :param name: description of param 'name'

   .. py:function:: foo(self, x, y)
      :noindex:

      Description of function here

      :param int x: parameter x is an integer and does...
      :param int y: parameter y is an integer and does...
      :rtype: returns int

If you are developing in an existing file , the doc chain *should* find your new function/class
automatically. In the case you are creating a new module, you'll need to create a ``.rst`` file in the docs/source/modules folder to give a description of the module. You can refer to the existing .rst files for how to populate the docs.

.. _here: https://www.python.org/dev/peps/pep-0008/