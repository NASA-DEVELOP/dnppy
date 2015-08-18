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

Used to convert raw data products as they are distributed from their various Distributed Active Archive Centers (DAAC's) into more easily handled file types like GeoTiffs. This module is currently expanding to handle as many NASA data products as possible, particularly those in NetCDF and HDF5 formats with incomplete or implicit geographic referencing information. Each of these functions should allow easy batch processing on entire directories of similar files.

.. rubric:: :doc:`core <modules/core>`

The core module houses functions that assist in data formatting, input sanitation, path manipulations, file naming, logical checks, etc for use in other functions within dnppy. They are short and sweet, and can be used as examples to start defining your own functions!

.. rubric:: :doc:`download <modules/download>`

The download module houses many "fetch" functions for automatic retrieval of specific data products from ``http`` and ``ftp`` servers around the USA. While centered around NASA data products, some functions exist for fetching of ancillary NOAA climate products and others.

.. rubric:: :doc:`landsat <modules/landsat>`

Landsat imagery is pretty versatile and commonly used, so the landsat data has its own module for common tasks associated with this product. This includes things like converting to top-of-atmosphere reflectance, at-satellite brightness temperature, cloud masking, and others.

.. rubric:: :doc:`modis <modules/modis>`

Two satellites, Terra and Aqua, are home to a MODIS sensor, which has produced a large number of data products for over a full decade with minimal interruption. The modis module houses functions specifically related to processing and handling MODIS data, which includes handling of the MODIS sinusoidal projection, and mosaic operations.

.. rubric:: :doc:`raster <modules/raster>`

The raster module is used to analyze raster data from non-specific sources. In an idealized workflow, use of the convert and download modules can help users obtain and pre-process data for use with functions in the raster module. The modules capabilities include statistics generation, subsetting, reprojecting, null data management, correction functions, and others. Top level functions in the raster module should all have batch processing capabilities bult in.

.. rubric:: :doc:`solar <modules/solar>`

The solar module contains just one class definition, with many associated methods to perform a plethora of calculations based around the sun-earth relationship. It replicates the functionality of the `common NOAA excel calculator`_, including adjustments due to atmospheric refraction. Each method may be run independently as the user wishes, as each method will automatically invoke any other calculations that must be performed first, and it will not unnecessarily redo calculations that have already been completed.

A solar class object allows scalar or numpy array inputs for latitude and longitude values for per-pixel computation and improved accuracy when scene-center calculations are insufficient. The solar class is not yet capable of ingesting digital elevation models to calculate slope and aspect dependent parameters, but it is a planned addition.

.. rubric:: :doc:`textio <modules/textio>`

The textio module, read like "text I/O", is a repository of functions for reading specific `text` data formats as they are served up from their respective DAACs. Custom text file formats are common in historical weather data and other ground based data collection networks. This module aims to convert them to something more standardized. Currently, custom ``text_data_objects`` are used, but migrating to something based on standard `json`_ is envisioned.

.. rubric:: :doc:`time_series <modules/time_series>`

The time_series module is centered around the time_series class. One or more time_series objects should be central to any data analysis task that examines temporal relationships in data sets of raster or tabular format. This module also houses the rast_series class, which is an extension of time_series for handling filepaths to raster data.


.. _common NOAA excel calculator: http://www.esrl.noaa.gov/gmd/grad/solcalc/calcdetails.html
.. _json: http://json.org/
