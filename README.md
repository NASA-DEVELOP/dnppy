## dnppy 
(The DEVELOP National Program Python Package)

####Overview
The DEVELOP national program python package(dnppy) has a handful of directives for different user groups, serving related but distinct purposes.

##### As a python module

As a python module, ``dnppy`` serves as a simple collection of functions and classes that are useful for manipulation, formatting, conversion, and analysis of geospatial data, with a heavy emphasis on NASA satellite data from earth observing platforms and ancillary NOAA climate and weather data. This docsite should be able to guide you through using dnppy functions.


##### As an IDE modifier

The primary users within the DEVELOP program are operating on government computers without administrator elevation. So, ``dnppy`` installs itself, and many common libraries that GIS python programmers might need without requiring administrative access. With ``dnppy``, users can have ``arcpy``, ``gdal``, ``scipy``, and other libraries all working together with an ESRI ArcGIS installation of python. Think of it as a modification to the users Integrated Development Environment (IDE). See the :doc:`installation <install>` page to learn more.


##### To distribute DEVELOP project code

The DEVELOP program partners with external organizations to complete a wide variety of earth science based projects. Often times, these external organizations would like access to code created by these project teams, though the projects were not fundamentally computer science based. This code is placed in the ``undeployed`` folder within ``dnppy`` along with legacy code. Code in the ``undeployed`` folder is not installed and accessible from dnppy. This is done in part to overcome very significant bureaucratic hurdles associated with releasing software.

#####Instalation
Run `setup.py` 

#####Dependencies

Before dnppy can be installed, ESRI's Arcmap 10.2 or 10.3 must already be installed. ArcMap ships with a custom installation of python 2.7, and `dnppy` is built to modify that python installation.

1. Python 2.7
2. `arcpy`  (see ESRI's ArcMap software)

At present, the following third party packages are automatically installed with the setup file in the pre-existing ArcGIS python directory. Windows binaries for each of these resources were selected from [here](http://www.lfd.uci.edu/~gohlke/pythonlibs) and rehosted in the dnppy release assets. They are unofficial,  and are included only to provide convenient installation of common scientific packages for the custom ArcMap installation of python.

3. `pip`
4. `wheel`
5. `requests`
6. `numpy 1.9.2`
7. `gdal`
8. `h5py`

In each case, 64 bit binaries will be used if the target python installation is 64 bit. For most intended Arcmap users, this means 64 bit binaries will only be installed if the "64 bit background geoprocessing" add-in is available.
