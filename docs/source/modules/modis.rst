modis
=====

.. automodule:: dnppy.modis
    :members:


Examples
--------

.. rubric:: MODIS Extracting and mosaicing

This example is written to be a type a follow on to the Fetching MODIS example on the :doc:`download module page <download>` so that users wishing to follow along precisely may easily get example data to work with. So lets assume we have a directory of some MODIS hdf files and you have had some time to fiddle with one or two in arcmap to know which layers you want, but you'd like to quickly extract all the same layers from your directory full of hdfs.

.. code-block:: python

    from dnppy import modis

    indir  = r"C:\Users\jwely\test"      # input directory
    layers = [3]                         # MOD11A1 fractional snow cover index
    lnames = ["FracSnowCover"]           # how we want to name this layer
    tifdir = r"C:\Users\jwely\test_tifs" # directory to place output tifs.

    modis.extract_from_hdf(indir, layers, lnames, tifdir)

The ``indir`` input could be a file list, but to allow simple batching, most functions in dnppy will accept a folder as an input and automatically generate a list of all files in that folder. If you want to exercise more control over which files are placed into the function, you can call the ``core.list_files()`` function yourself and filter it down. In this case though, we are ok with simply running the operation on the whole directory. The ``layers`` and ``lnames`` inputs will depend on the specific MODIS product you are using, and both may be lists in case you want to extract multiple layers. The ``tifdir`` input may also be left blank, in which case files will simply be saved in the same directory as the input hdfs.

Next, we can mosaic very easily with

.. code-block:: python

    mosaicdir  = r"C:\Users\jwely\mosaics"  # directory to place MODIS mosaics
    pixel_type = "8_BIT_UNSIGNED"           # arcmap bitdepth to save rasters as

    modis.mosaic(tifdir, mosaicdir, pixel_type)


Where ``tifdir`` is used as the input directory, with the same value as in the previous code snippet. In this example, the MODIS data we are working with is only 8 bit unsigned integer data, so we manually specify this instead of allowing the default 32 bit float assignment, which will make the files unnecessarily large.

And thats it! You will notice it prints a summary of the different types of MODIS data it found to mosaic, including tiles, years, days, products, and suffixes (such as those generated during extraction). The mosiac function has a lot more optional inputs that a user may wish to use, but consulting help(modis.mosaic) is the best way to get all those details.

The :doc:`rast series example <raster>` will continue in the theme of this example MODIS dataset.

Code Help
---------

Auto-documentation for functions and classes within this module is generated below!

.. automodule:: dnppy.modis.modis_metadata
    :members:

.. automodule:: dnppy.modis.define_projection
    :members:

.. automodule:: dnppy.modis.extract_from_hdf
    :members:

.. automodule:: dnppy.modis.mosaic
    :members:
