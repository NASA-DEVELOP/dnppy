============
Installation
============

This section will guide you through installing dnppy. You should find it is quite simple!

------------
Requirements
------------

* Python 2.7 (32 or 64 bit)
* arcpy (as distributed with ESRI's ArcMap software version 10.1 to 10.3)

At present, many of the dnppy functions call upon ``arcpy``, distributed with ESRI's commercial ArcMap software. By time ``dnppy`` is out of beta, the installation will be split such that users can still access the non ``arcpy`` dependent modules (such as those for downloading and formatting NASA satellite data) if they do not have ArcMap. In the long term, the modification of several key functions to use ``gdal`` should allow complete ``arcpy`` independence.

.. note:: it is highly advised to use 64-bit python 2.7 available through the "Background-Geoprocessing" package upon installation of ArcMap. A 32-bit installation may only consume 2GB of memory at once, which is an easy limit to hit when processing even modestly sized raster data sets.

There are no other requirements for ``dnppy`` which are not automatically retrieved on setup.

--------------
How to Install
--------------

Grab the master branch from our `GitHub`_ by clicking on the "download zip" button on the bottom right of the screen. Extract the archive and run ``setup.py``. Setup will fetch other dependencies from ``.whl`` files hosted in the release assets or from the python package index. Most of these ``.whl`` files were originally obtained from this `unofficial windows binaries index`_. Ta-da! You are ready to get started with ``dnppy`` and python programming with NASA data and GIS!

-----------------
Included Packages
-----------------
The following packages are installed with ``dnppy``.

* Using PyPI
    * psutil
    * requests
    * urllib3
    * wheel
* Using Binaries
    * cython
    * gdal
    * h5py
    * numpy
    * pip
    * pycurl
    * scipy
    * shapely

.. _GitHub: https://github.com/nasa-develop/dnppy
.. _unofficial windows binaries index: http://www.lfd.uci.edu/~gohlke/pythonlibs/