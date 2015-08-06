======
Design
======

There exists several design themes within dnppy, and an effort is (and should continue to be) made to follow these design themes to keep its use intuitive.

-----------------
functional format
-----------------

At heart, ``dnppy`` is a simple collection of classes and functions. Wherever possible, these functions are designed such that they can be assembled in simple "building block" style sequence to perform manipulation and analysis on many files, typically raster data from a NASA sensor. This approach makes otherwise complex programming tasks more accessible to novice programmers, and provides context for learning more foundational computer programming.

Many of the user oriented functions in dnppy are usually defined similar to the following:

.. code-block:: python

    def foo(input_filelist, other_argument):
        """ does something foo-ish """

        output_filelist = []
        for input_file in input_filelist:
            # do something to create an output_file
            output_filelist.append(output_file)

        return output_filelist


    def bar(input_filelist, other_argument):
        """ does something bar-ish """

        output_filelist = []
        for input_file in input_filelist:
            # do something to create an output_file
            output_filelist.append(output_file)

        return output_filelist

This allows the user to invoke these functions with

.. code-block:: python

    foo_outputs = foo(my_filelist, my_arg1)
    bar_outputs = bar(foo_outputs, my_arg2)

Where ``foo_outputs`` was directly fed into the inputs for function ``bar``

Of course, there also exist many classes within dnppy which are used in the conventional python fashion.

