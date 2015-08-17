Developers Starter
==================

Firstly, if you haven't read through the entirety of the "Getting Started" sections, please do so before contributing to dnppy.


The way dnppy is developed is a little bit unique because it is so tightly integrated with the DEVELOP program. In the immediate future, the primary users will be internal to the DEVELOP program, though we expect this to change as dnppy matures. Future developers are likely to include a number of Geoinformatics Fellows who are themselves at an intermediate level of programming skill. These factors dictate a customized approach to further development of dnppy.


Environment
-----------
There are a few recommendations that can be made to those working to enhance their programming skills and get deeper into development. One of those is to spend some time selecting, and getting comfortable with an Integrated Development Environment (IDE).

We highly recommend users download `PyCharm`_ by JetBrains to work on sets of python code, but especially if working on dnppy. PyCharm gives the user tips and warnings when coding best practices are violated, which can encourage you to adopt more professional practice and learn things you didn't even think to ask about! It also has powerful refactoring tools and great error catching on the fly to help you spend less time fixing small mistakes. Pycharm works well on both Windows and Linux.

.. _PyCharm: https://www.jetbrains.com/pycharm/


Contributing through GitHub
---------------------------
All contributions to dnppy are managed through github, and there is a set of best practices to go along with it that warrants is own page on :doc:`GitHub best practices <contrib_git>`


Functional Coding Conventions
-----------------------------
There are a few conventions future developers should try to follow when contributing that go slightly beyond stylistic preference.

.. rubric:: Printing string output

In python 2.7, users can use ``print "my string"``, but in python 3.0 this is no longer acceptable! The ``print`` keyword has become a function in python 3.0. Furthermore, in line substitutions abide by slightly different rules. So, in order to institute good practice for the inevitable update to python 3.0+ it costs us very little to write print statements that work in `both` 2.7 and 3.0. Therefore we use the ``format`` method on a string.

.. code-block:: python

    my_name = "Jwely"
    my_age = 26

    print "my name is " + my_name + " and my age is " + str(my_age)     # this is BAD
    print("my name is {0} and my age is {1}".format(my_name, my_age))   # this is GOOD

Notice that you do not need to cast ``my_age`` as a string when using the ``format`` method, as it takes care of this on its own.

You may find violations of this rule within dnppy, if you do, please fix it!


Stylistic Coding Conventions
----------------------------
Stylistic conventions have no impact on a set of codes ability to run, but are arguably even more important than the technical capabilities of the code. Coding conventions make code more readable, easier to troubleshoot, easier to build upon, and more approachable by other programmers familiar with those conventions. Fortunately there exist some extremely common conventions, and in dnppy, we adhere to most of them, as listed below.

.. note::

   We are now using the ``pep-0008`` style guide as referenced `here`_ . See the link for a full
   list of conventions

Below is a list of general guidelines for style and consistency to keep everything as readable as possible.

.. rubric:: Column Width

Code should be no longer than 100 characters, in the case your statement goes **over**, use a
new line or split your statement up.

.. rubric:: String Literals

String Literals are denoted with ``""`` or ``''``, docstrings should always be triple double quotes ``"""``

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