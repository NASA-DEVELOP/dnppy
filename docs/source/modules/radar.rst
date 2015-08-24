radar
=====

.. automodule:: dnppy.radar
    :members:

Examples
--------

.. rubric:: Building a header file for UAVSAR data
UAVSAR data comes in .grd files that require a text header file with metadata information in order to be displayed in GIS or image processing software. This simple script will read in a folder containing the data and create a header file for each .grd file in it.

.. code-block:: python

    from dnppy import radar

    folder = r"C:\folder"

    radar.create_header(folder)


.. rubric:: Converting backscatter values to decibels

Raw radar data has units of backscatter for its given polarization, but it is often more useful to convert these units to decibels (dB). This script will create a new tiff raster in decibel units from the original .grd file (which must also include the .hdr file).

.. code-block:: python

    from dnppy import radar

    filename = r"C:\folder\file.grd"

    radar.decibel_convert(filename)
