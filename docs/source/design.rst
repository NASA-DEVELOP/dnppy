======
Design
======

There exists several design themes within dnppy, and an effort is (and should continue to be) made to follow these design themes to keep its use intuitive.

Modules
-------

dnppy is divided into some thematic `modules`_ by purpose. Each module has its own page and some examples to get you started, but they are all used in a similar fashion. When accessing code from some remote location with python, we use the an ``import`` statement to bring the module contents into the current namespace of python. Once the functions are loaded into the namespace, you can invoke all functions in that module, and call ``help()`` on them to explore their contents from the console. All information displayed by a help command should be available in clean formatted text on these doc pages.

.. code-block:: python

    from dnppy import modis         # import the modis module from dnppy
    help(modis)                     # print list of functions in modis
    help(modis.mosaic_modis)        # print detailed help for this function
    modis.mosaic_modis(filelist)    # execute the mosaic_modis function

Notice that when we use `` from dnppy import modis`` we need to keep the modis name out front of all functions within it.

Functional Format
-----------------

At heart, ``dnppy`` is a simple collection of classes and functions. Wherever possible, these functions are designed such that they can be assembled together in simple "chain-link" style sequence to perform manipulation and analysis on many files, typically raster data from a NASA sensor, by feeding the outputs of one function into the inputs of another. This approach makes otherwise complex programming tasks more accessible to novice programmers, and provides context for learning more foundational computer programming.

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




