dnppy 
(The DEVELOP National Program Python Package)

###Overview
The DEVELOP national program python package(dnppy) has a handful of directives for different user groups, serving related but distinct purposes.

##### As a python module

As a python module, ``dnppy`` serves as a simple collection of functions and classes that are useful for manipulation, formatting, conversion, and analysis of geospatial data, with a heavy emphasis on NASA satellite data from earth observing platforms and ancillary NOAA climate and weather data. This docsite should be able to guide you through using dnppy functions.


##### As an IDE modifier

The primary users within the DEVELOP program are operating on government computers without administrator elevation. So, ``dnppy`` installs itself, and many common libraries that GIS python programmers might need without requiring administrative access. With ``dnppy``, users can have ``arcpy``, ``gdal``, ``scipy``, and other libraries all working together with an ESRI ArcGIS installation of python. Think of it as a modification to the users Integrated Development Environment (IDE). See the :doc:`installation <install>` page to learn more.


##### To distribute DEVELOP project code

The DEVELOP program partners with external organizations to complete a wide variety of earth science based projects. Often times, these external organizations would like access to code created by these project teams, though the projects were not fundamentally computer science based. This code is placed in the ``undeployed`` folder within ``dnppy`` along with legacy code. Code in the ``undeployed`` folder is not installed and accessible from dnppy. This is done in part to overcome very significant bureaucratic hurdles associated with releasing software.

###Instalation
Run `setup.py` 

###Requirements

* Python 2.7 (32 or 64 bit)
* arcpy (as distributed with ESRI's ArcMap software version 10.1 to 10.3)

At present, many of the dnppy functions call upon ``arcpy``, distributed with ESRI's commercial ArcMap software. By time ``dnppy`` is out of beta, the installation will be split such that users can still access the non ``arcpy`` dependent modules (such as those for downloading and formatting NASA satellite data) if they do not have ArcMap. In the long term, the modification of several key functions to use ``gdal`` should allow complete ``arcpy`` independence.

There are no other requirements for ``dnppy`` which are not automatically retrieved on setup.
