Intro to gdal
=============

The `geospatial data abstraction library (gdal)`_ is an open source translator library for raster and vector data formats. It is typically used as a `command line utility`_, but has `bindings`_ for many popular programming languages including python.

gdal utilities:
    * `Raster utilities`_
    * `Vector utilities`_


gdal with dnppy
---------------
As an example, ``download.fetch_SRTM`` has an option to mosaic the downloaded DEM tiles into one tif, and accomplishes this mosaic operation with a call to ```gdalwarp`_``. The syntax for this command is something like::

    gdalwarp image1 image2 output_mosaic

which is pretty easy to put together for any number of images if you have a list of images to mosaic, and an output name. There exists a function in the core module of dnppy for compiling more complex data structures into a simple string of space delimited arguments and running it called ``run_command``. In the case of ``download.fetch_SRTM``, the syntax looks like

.. code-block:: python

    core.run_command("gdalwarp", tile_list, out_mosaic)

which will work for an unlimited number of input image filepaths inside of ``tile_list``.


Using the osr to manage projections
-----------------------------------
gdal is actually distributed with osgeo, and another package in osgeo is the Object Spatial Reference library (osr). This library has all kinds of projection information stored within it in a text like format organized by EPSG number. A good way to find the EPSG number for a projection you are familiar with is to look it up on `spatialreference.org`_. These EPSG numbers are used almost exclusively by gdal when dealing with projections and coordinate systems. You can access the perhaps more familiar text version of the projection information from the osr library with.

.. code-block:: python

    from osgeo import osr

    my_projection_number = 4326         # EPSG for WGS 1984 geographic coordinate system

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(int(my_projecton_number))
    projection_text = srs.ExportToWkt()
    print(projection_text)


Geotransforms
-------------

There are a couple steps needed to map a location in real space on the surface of a spheroid (Earth) to a flat plane on your computer monitor. The first step is to use a geographic or projected coordinate system, that maps a real lat/lon coordinates on the earth to a flat set of grid points, your coordinate space. The second step is to map this coordinate space to the pixel or matrix space of the specific raster, so that it may be displayed on a monitor with every pixel in the correct location. Projection data contains all the information required for the first step, but geotransform data is required to accomplish the second. The information in a gdal geotransform is **similar** but **not identical** to the information used in `world files`_ with a ``.tfw`` extension. It is a set of 6 coefficients to a set of two equations that transform image space (i,j) matrix coordinates, into projected space (x,y) coordinates according to::

    x = A + iB + jC
    y = D + iE + jF

where the geotransform itself is simply listed as::

    [A, B, C, D, E, F]

In a raster image with adequate georeference information, this geotransform should be recognized by gdal when reading in any supported raster data format. Sometimes, the information is NOT embedded in a universal format, and the user has to define it based on the resolution and extents of the raster dataset. This is what we have done for a few NASA data formats in the ```datatype_library`_`` within the convert module.

.. _datatype_library: https://nasa-develop.github.io/dnppy/modules/convert.html#dnppy.convert.datatype_library.datatype_library
.. _world files: https://en.wikipedia.org/wiki/World_file
.. _spatialreference.org: http://spatialreference.org/
.. _gdalwarp: http://www.gdal.org/gdalwarp.html
.. _geospatial data abstraction library: http://www.gdal.org/
.. _command line utility: https://en.wikipedia.org/wiki/Command-line_interface
.. _bindings: https://en.wikipedia.org/wiki/Language_binding
.. _Raster utilities: http://www.gdal.org/gdal_utilities.html
.. _Vector utilities: http://www.gdal.org/ogr_utilities.html
.. _geospatial data abstraction library (gdal): http://www.gdal.org/