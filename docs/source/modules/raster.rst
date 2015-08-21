raster
======

.. automodule:: dnppy.raster
    :members:

Examples
--------

.. rubric:: Using ``spatially_match``

Often times, one will want to perform an analysis which includes raster data from two different sources. This data usually has to converted to match the resolution, spatial extent, geographic reference, and projection. In order to do simple matrix type math, pixels must also be perfectly coincident, laying directly on top of one another. The ``spatially_match`` function was built for this purpose. It wraps other ``dnppy.raster`` functions, including `clip_and_snap` and ``project_resample`` and performs the necessary steps to make an input set of data match a reference file. Typically, all should be resampled and subseted to match that of the highest resolution layer, often times a Digital Elevation Model (DEM). One would use the syntax below to make a directory full of raster data match a reference tif, a DEM in this case.

Assume we have a DEM, and a few dozen MODIS images, which are much lower resolution. If you have been following some of the other examples in this wiki, you may have a MODIS data set prepared already. You can easily fetch a DEM using the ``fetch_SRTM`` function in the ``download`` module.

.. code-block:: python

    from dnppy import raster

    dempath  = r"C:\Users\jwely\test\SRTM_DEM.tif"    # filepath to DEM
    modisdir = r"C:\Users\jwely\test_tifs"            # directory with MODIS tifs
    smdir    = r"C:\Users\jwely\sm_tifs"              # dir for output sm tiffs.

    raster.spatially_match(dempath, modisdir, smdir)

The code block above will produce a folder full of tiffs at ``smdir`` that are spatially matched to the same resolution, extents, and projection of the ``dempath`` raster. The images are now ready for further numerical manipulation.


Code Help
---------

.. automodule:: dnppy.raster.apply_linear_correction
    :members:

.. automodule:: dnppy.raster.clip_and_snap
    :members:

.. automodule:: dnppy.raster.clip_to_shape
    :members:

.. automodule:: dnppy.raster.degree_days
    :members:

.. automodule:: dnppy.raster.degree_days_accum
    :members:

.. automodule:: dnppy.raster.enf_rastlist
    :members:

.. automodule:: dnppy.raster.from_numpy
    :members:

.. automodule:: dnppy.raster.gap_fill_temporal
    :members:

.. automodule:: dnppy.raster.gap_fill_interpolate
    :members:

.. automodule:: dnppy.raster.in_dir
    :members:

.. automodule:: dnppy.raster.is_rast
    :members:

.. automodule:: dnppy.raster.many_stats
    :members:

.. automodule:: dnppy.raster.metadata
    :members:

.. automodule:: dnppy.raster.new_mosaic
    :members:

.. automodule:: dnppy.raster.null_define
    :members:

.. automodule:: dnppy.raster.null_set_range
    :members:

.. automodule:: dnppy.raster.project_resample
    :members:

.. automodule:: dnppy.raster.raster_fig
    :members:

.. automodule:: dnppy.raster.raster_overlap
    :members:

.. automodule:: dnppy.raster.spatially_match
    :members:

.. automodule:: dnppy.raster.to_numpy
    :members:



