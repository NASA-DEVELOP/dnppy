============
Installation
============

This section will guide you through installing `dnppy`_. You should find it is quite simple!

------------
Requirements
------------

* Python 2.7 (32 or 64 bit)
* arcpy (as distributed with ESRI's ArcMap software version 10.1 to 10.3)
* Windows OS

At present, many of the dnppy functions call upon ``arcpy``, distributed with ESRI's commercial ArcMap software. By time dnppy is out of beta, the installation will be split such that users can still access the non ``arcpy`` dependent modules (such as those for downloading and formatting NASA satellite data) if they do not have ArcMap. In the long term, the modification of several key functions to use ``gdal`` should allow complete ``arcpy`` independence.

.. note:: it is highly advised to use 64-bit python 2.7 available through the "Background-Geoprocessing" package upon installation of ArcMap. A 32-bit installation may only consume 2GB of memory at once, which is an easy limit to hit when processing even modestly sized raster data sets.

There are no other requirements for ``dnppy`` which are not automatically retrieved on setup.

--------------
How to Install
--------------

.. rubric:: Manual download

Grab the master branch from our `GitHub`_ by clicking on the "download zip" button on the bottom right of the screen. Extract the archive and run ``easy_install.py``. Running this file may require opening up *IDLE* and loading the script, then hitting *F5* to execute it. Setup will fetch other dependencies from ``.whl`` files hosted in the release assets or from the python package index. Most of these ``.whl`` files were originally obtained from this `unofficial windows binaries index`_. Ta-da! You are ready to get started with ``dnppy`` and python programming with NASA data and GIS!

.. rubric:: With pip

If you've got ``pip``, you can use the following code snippet in the python console.

.. code-block:: python

    import pip
    pip.main(["install", "--upgrade", "https://github.com/NASA-DEVELOP/dnppy/archive/master.zip"])

or whichever `release tagged`_ branch you would like to install instead of master.

.. _release tagged: https://github.com/NASA-DEVELOP/dnppy/releases

-----------------
Included Packages
-----------------
The following packages are installed with dnppy.

* Using PyPI
    * `psutil`_
    * `requests`_
    * `urllib3`_
    * `wheel`_
* Using Binaries
    * `cython`_
    * `gdal`_
    * `h5py`_
    * `numpy`_
    * `pip`_
    * `pycurl`_
    * `scipy`_
    * `shapely`_

.. _psutil: https://github.com/giampaolo/psutil
.. _requests: https://github.com/kennethreitz/requests
.. _urllib3: https://github.com/shazow/urllib3
.. _wheel: https://wheel.readthedocs.org/en/latest/
.. _cython: https://github.com/cython/cython
.. _gdal: https://github.com/OSGeo/gdal
.. _h5py: https://github.com/h5py/h5py
.. _numpy: https://github.com/numpy/numpy
.. _pip: https://github.com/pypa/pip
.. _pycurl: https://github.com/pycurl/pycurl
.. _scipy: https://github.com/scipy/scipy
.. _shapely: https://github.com/Toblerity/Shapely


.. _dnppy: https://github.com/nasa-develop/dnppy
.. _GitHub: https://github.com/nasa-develop/dnppy
.. _unofficial windows binaries index: http://www.lfd.uci.edu/~gohlke/pythonlibs/