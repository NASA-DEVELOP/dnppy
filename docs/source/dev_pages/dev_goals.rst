Future Development Goals
========================
dnppy has some long term goals in mind, goals that will take slow and continuous effort to achieve.

Shed arcpy
----------

The arcpy module is available only to users who purchase ESRI's ArcMap software. It's principle advantage over most other GIS programming tools or API's out there is that the user and help documentation is really good, and the "model builder" interface is a good baby step towards python programming, so it's a good place for burgeoning GIS programmers to start learning. Conversely, the gdal library is very powerful cross platform library with python bindings, but has disjointed documentation that can be intimidating and confusing.

dnppy's long term goal is to package the power of gdal into more easily understood functional wrappers akin to arcpy functions. Priority should always be placed on meeting the immediate needs of the GIS community and NASA data users, but the addition of new arcpy dependent functions should be avoided.

.. rubric:: Intro to ``gdal``

It would be rather inconsiderate of us to tell future developers, "please use gdal k-thanks" without giving them some kind of starter guide, so here is our stab at it. If you've installed dnppy, you've already got an arcpy compatible version of gdal installed, and many dnppy functions already use gdal!

.. note:: place magical gdal wisdom here

Python 3
--------
Once dnppy is no longer tied to arcpy (or perhaps when arcpy updates to python 3), we will be free to embrace the current and future of the Python programming language. In the mean-time, there are some things we can be doing `right now` that will make the transition to Python 3 significantly easier.

.. note:: A very complete and succinct list can be found at `python-future.org`_, but here are some high priority ones.

.. _python-future.org: http://python-future.org/compatible_idioms.html

.. rubric:: Printing string output

String manipulations are very common even at the most basic level.In Python 2, users can use ``print "my string"``, but in Python 3 this is no longer acceptable! The ``print`` keyword has become a function in python 3. Furthermore, in line substitutions abide by slightly different rules. So, in order to institute good practice for the inevitable update, it costs us very little to write print statements that work in `both` 2.7 and 3.0. Therefore we use the ``format`` method on a string.

.. code-block:: python

    my_name = "Jwely"
    my_age = 26

    print "my name is " + my_name + " and my age is " + str(my_age)     # this is BAD
    print("my name is {0} and my age is {1}".format(my_name, my_age))   # this is GOOD

Notice that you do not need to cast ``my_age`` as a string when using the ``format`` method, as it takes care of this on its own. You may find violations of this rule within dnppy, if you do, please fix it!
