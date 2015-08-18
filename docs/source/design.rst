======
Design
======

There exists several design themes within dnppy, and an effort is (and should continue to be) made to follow these design themes to keep its use intuitive.

Modules
-------

dnppy is divided into some thematic `modules`_ by purpose. Each module has its own page and some examples to get you started, but they are all used in a similar fashion. You can read more about each specific module on the :doc:`modules summary page <modulesum>`.

Functional Format
-----------------

At heart, dnppy is a simple collection of classes and functions. Wherever possible, these functions are designed such that they can be assembled together in simple "chain-link" style sequence to perform manipulation and analysis on many files, typically raster data from a NASA sensor, by feeding the outputs of one function into the inputs of another. This approach makes otherwise complex programming tasks more accessible to novice programmers, and provides context for learning more foundational computer programming.

In the example below, ``foo_outputs``, which is a list of the output files created by ``foo``, was directly fed into the inputs for function ``bar``

.. code-block:: python

    foo_outputs = foo(my_filelist, my_arg1)
    bar_outputs = bar(foo_outputs, my_arg2)

This is accomplished by defining functions in a manner similar to the following:

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


.. note:: Future developers should keep this in mind when building functions to operate on files. You can read more about the specifics on the module and developer pages.

.. _modules: https://docs.python.org/2/tutorial/modules.html




