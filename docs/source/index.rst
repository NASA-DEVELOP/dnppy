.. dnppy documentation master file, created by
   sphinx-quickstart on Tue Aug 04 11:29:04 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the dnppy documentation page!
========================================

dnppy is a python package with two purposes.

The first is as a python package for the download, extraction, conversion, and analysis of NASA and NOAA earth observation data. It includes several modules to ease handling and analysis of common raster datatypes such as Landsat, MODIS, GPM, TRMM, ASTER, SRTM, and text datatypes such as weather records. It also houses modules such as the solar module, for calculating solar geometries for entire arrays of lat/lon coordinates, and the time_series module for handling temporal raster data.

The secondary purpose of dnppy is as a living codebase for the `DEVELOP National Program`_. DEVELOP is under NASA's "Capacity Building" program, and functions to educate its participants and its partners in multiple fields. Viewers will notice a very instructional approach to both user and developer documentation within these pages. dnppy was created to improve institutional knowledge retention, open the DEVELOP toolkit for public contributions and use, represent DEVELOP in the public domain, and put more power in the hands of new participants the first day the walk into the program. It is a social media, programming capacity building, and educational endeavor. Code specifically pertinent to our past project partners can be found in the /undeployed/proj_code folder.


Contents:
=========

.. toctree::
    :caption: Getting Started
    :maxdepth: 2

    overview
    design
    installation
    nowwhat

.. toctree::
    :caption: Examples by Module
    :maxdepth: 2

    convert
    core
    download
    landsat
    modis
    radar
    raster
    solar
    textio
    time_series


.. toctree::
    :caption: Developer Documentation
    :maxdepth: 2

    pythonstarter
    conventions
    ide
    docbuilding




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



.. _DEVELOP National Program: http://develop.larc.nasa.gov/