Python Quick-Starter
====================

There are lots of python tutorials out there, and users just getting started with python, especially if it is your first programming language, are highly encouraged to check out some of the following tutorials before continuing. It won't take long, and it will get you primed and ready to learn intermediate concepts pretty quickly.

* `Learn X in Y minutes`_
* `Learn python in 10 minutes`_
* `Python for first time programmers`_
* `Code Academy`_
* `Learn Python`_
* `Think like a computer scientist`_

.. note:: You can start writing python code with the default interpreter called "IDLE"


The right mindset
-----------------

For starters, programming is usually pretty exciting with the right mindset. It's a rapidly accelerated environment where you get the chance to discover new things and apply your knowledge to solve immediate problems. You can spend hours making a computer accomplish a task that would only take you 15 minutes to do manually, but once you're finished you will have a complete understanding of the task, and be able to do it `thousands` of times faster from this moment forward. Once you use programming to accomplish a task, you can build upon it to solve slightly more complex tasks, and then continue to build upon that.

Sometimes new programmers struggle with the fact that something very intuitive for a human is NOT intuitive for the computer. You know what you want to do, but communicating this through the keyboard seems impossible. This is why we call them programming `languages`. Python is a language, and one can learn programming is the same way one learns a spoken language. First, you'll need to observe the work of other people through very simple tutorials. Next, you'll need to find answers to extremely simple questions like:

* `"how do I manipulate this variable?"`
* `"how do I do something to every item in a set of items?"`
* `"how do I define a function and refer to it later?"`

This is the programming equivalent of a parent telling a baby what color things are, and what noises an animal might make, but in this case you are the baby and it's your responsibility to `ask` what color the grass is and what noise the sheep makes. The best way to learn is to make an attempt at each small coding task one at a time, think of the simplest question you can ask, then just type that question into google. Writing software is 10% programming, and 90% Googling.

You can definitely do it, and the tutorials above can guide you through the first stages.

Frequent Pitfalls
-----------------

.. rubric:: Filepaths in python

A large number of dnppy functions use filepaths as inputs, and users on Windows systems are likely to encounter a problem with copy/paste filepaths from the explorer bar into code. This issue is that windows uses backslashes instead of forward slashes in its filepaths, and these backslashes are used to indicate special characters to python. For example "\\t" is a "tab", and "\\n" is a "new line". One fix is to manually replace the "\\" characeters with "/" characters, but this can get time consuming and tedious. The quick lesson? Prefix your strings with a lower case "r". So instead of

.. code-block:: python

    >>> filepath = "C:\Users\testuser\Desktop"
    >>> print filepath
    "C:\Users     estuser"

which has obviously interpreted our "\t" as a tab character, simply write

.. code-block:: python

    >>> filepath = r"C:\Users\testuser\Desktop"
    >>> print filepath
    "C:\Users\testuser\Desktop"

This lower case "r" out front tells python to interpret the string as "raw" without special characters.


Python Terminology
------------------


.. rubric:: Functions, Classes, Methods, and Objects


A function `does` something, and typically has inputs and outputs. A class `is` something, and has attributes that describe it, as well as methods that dictate its behavior, and define how its attributes are manipulated. An object is a specific instance of a "class". For example, a class might be "fruit" that has a bunch of attributes like color, size, weight, ripeness, and price/per pound. An object might be "Watermelon" which is a specific instance of a "fruit" class. Each of the watermelons attributes would have values that describe a watermelon. A "fruit" may also have a method; functions that are very specific to the class. An example of a class method perhaps would be "ripen" which would adjust the fruits ripeness as a function of time. Note that these principles are transferable to any other Object Oriented Programming (OOP) language, not just python. Below is example code on how each of these items are interacted with, using python syntax.

.. code-block:: python

    output     = a_function(args)   # call function on inputs, return outputs
    watermelon = fruit_class(args)  # creates a specific instance of a class
    watermelon.ripen(args)          # invokes ripen method on watermelon

    print watermelon.size           # view size attribute of watermelon
    print watermelon.ripeness       # view ripeness attribute of watermelon

And function, class, and method definitions would look something like this.

.. code-block:: python

    # a function
    def a_function(inputs):
        """ does something to these inputs to return these outputs """
        # do something
        return output

    # a class declaration
    class fruit_class:

        # A "magic" method, that creates the fruit_class instance
        def __init__(self, name, size, weight, price):
           """ dictates the initial attributes and arguments of the class """

           self.name     = name
           self.size     = size
           self.weight   = weight
           self.price    = price
           self.ripeness = 0

        # method
        def ripen(self, time):
            """  adds time to fruits ripeness value """
            self.ripeness += time
            return self.ripeness

.. rubric:: Magic Methods

Magic methods are special methods that allow custom classes to interact with python syntax in an almost "magical" way. They are always surrounded by double underscores, such as the very common ``__init__`` in the example above that governs the initialization behavior of a class. A great guide exists on the topic already by `Rafe Kettler`_.

.. rubric:: Keywords

Python keywords are all the short little words that have special meaning to python. These words can not be turned into variable names, as they are already reserved for the very specific function they serve in python. Keywords include things like "if, and, import, return, pass, def, class" and several others. This `zetcode tutorial`_ has some really great examples on each keyword and how they are used.

.. rubric:: Keyword Arguments

Keyword arguments are like local versions of pythons keywords, they have a special meaning, but `only` within a spefific functin or class. As an example, take a look at the definition for the ``core.list_files`` function.

.. code-block:: python

    def list_files(recursive, Dir, Contains = None, DoesNotContain = None):

When calling `list_files`, you could specify all four arguments in the order they are listed, but the two trailing arguments have a `default` value with special implications. If they are left blank, they take on the value of ``None``. In addition, key word arguments (any argument with a pre-existing value assigned with an ``=``) they can be defined in any order you wish. So, for example, if you had a criteria for ``DoesNotContain``, but not for ``Contains``, you could call this function successfully with

.. code-block:: python

    my_files = core.list_files(False, my_dir, DoesNotContain = ['dont_want','also_dont_want'])

without needing to give the ``Contains`` argument a value. This comes in handy for functions with 4 or more inputs where it can be tedious to pass every conceivable argument every time.



.. _learn X in Y minutes: http://learnxinyminutes.com/docs/python/
.. _learn python in 10 minutes: http://www.stavros.io/tutorials/python/
.. _python for first time programmers: https://wiki.python.org/moin/BeginnersGuide/NonProgrammers
.. _code academy: https://www.codecademy.com/tracks/python
.. _learn python: http://www.learnpython.org/
.. _learn python the hard way: http://learnpythonthehardway.org/book/
.. _think like a computer scientist: http://interactivepython.org/courselib/static/thinkcspy/toc.html

.. _Rafe Kettler: http://www.rafekettler.com/magicmethods.html
.. _zetcode tutorial: http://zetcode.com/lang/python/keywords/

