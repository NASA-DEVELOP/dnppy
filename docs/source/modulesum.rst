=====================
Exploring the modules
=====================

OK, so you have read the overview, maybe you've downloaded and installed the package, you read about the design and how how to use it, but what can dnppy *actually* do!? How do you access functions?! What can you do with NASA data? The next section of the sidebar breaks dnppy down into its individual modules with some introductory examples on how to use some of the functions and classes in each one. When accessing code from some remote location with python, we use the an ``import`` statement to bring the module contents into the current namespace of python.

.. code-block:: python

    from dnppy import core    # import the core module from dnppy
    help(core)                # print list of functions in core
    help(core.function)       # print detailed help for function "function"

    # collects the returned value from passing some arguments into our hypothetical function
    returned_value = core.function(*args)


Module Summary
--------------

.. rubric:: :doc:`convert <modules/convert>`

.. automodule:: dnppy.convert
    :members:

.. rubric:: :doc:`core <modules/core>`

.. automodule:: dnppy.core
    :members:

.. rubric:: :doc:`download <modules/download>`

.. automodule:: dnppy.download
    :members:

.. rubric:: :doc:`landsat <modules/landsat>`

.. automodule:: dnppy.landsat
    :members:

.. rubric:: :doc:`modis <modules/modis>`

.. automodule:: dnppy.modis
    :members:

.. rubric:: :doc:`radar <modules/radar>`

.. automodule:: dnppy.radar
    :members:

.. rubric:: :doc:`raster <modules/raster>`

.. automodule:: dnppy.raster
    :members:

.. rubric:: :doc:`solar <modules/solar>`

.. automodule:: dnppy.solar
    :members:

.. rubric:: :doc:`textio <modules/textio>`

.. automodule:: dnppy.textio
    :members:

.. rubric:: :doc:`time_series <modules/time_series>`

.. automodule:: dnppy.time_series
    :members:
