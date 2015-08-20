====================
Purpose and Overview
====================

The `DEVELOP national program`_ python package(dnppy) has a handful of directives for different user groups, serving related but distinct purposes.

.. _Develop national program: http://develop.larc.nasa.gov/

.. rubric:: As a python module

As a python module, dnppy serves as a simple collection of functions and classes that are useful for manipulation, formatting, conversion, and analysis of geospatial data, with a heavy emphasis on NASA satellite data from earth observing platforms and ancillary NOAA climate and weather data. This docsite should be able to guide you through using dnppy functions.


.. rubric:: As an IDE modifier

The primary users within the DEVELOP program are operating on government computers without administrator elevation. So, dnppy installs itself, and many common libraries that GIS python programmers might need without requiring administrative access. With dnppy, users can have ``arcpy``, ``gdal``, ``scipy``, and other libraries all working together with an ESRI ArcGIS installation of python. Think of it as a modification to the users Integrated Development Environment (IDE). See the :doc:`installation <install>` page to learn more.


.. rubric:: To distribute DEVELOP project code

The DEVELOP program partners with external organizations to complete a wide variety of earth science based projects. Often times, these external organizations would like access to code created by these project teams, though the projects were not fundamentally computer science based. This code is placed in the ``undeployed`` folder within dnppy along with legacy code. Code in the ``undeployed`` folder is not installed and accessible from dnppy. This is done in part to overcome *unbelievably* restrictive bureaucratic hurdles associated with releasing software from NASA Langley Research Center where we are headquartered.

Scope
-----

All current and future actions related to dnppy must be within the following scope:

    1. To improve accessibility and utility of NASA data products
    2. To be as beginner friendly and approachable as possible

Support of this scope is why, for example, we chose to have dnppy fetch and install several third party libraries upon setup, to make life easier for people starting out who may struggle with setting up complex libraries like ``gdal`` along side the more familiar ``arcpy``. Support of these primary goals is part of why the download and convert modules for fetching and conversion of NASA data products to standard GeoTiffs are a center focus for further development.

Structure
---------

Each of the distinct directives results in a few different directories within dnppy. The package has the following file structure::

    dnppy
        \dnppy
        \docs
        \undeployed
            \legacy
            \proj_code
            \subjects
        \dev


.. rubric:: \\dnppy

Contains each module of dnppys main library which is installed on setup as ``dnppy``!
:doc:`Read more about the modules <modulesum>`

.. rubric:: \\docs

The folder containing the source rst files used to automatically generate these documentation pages.
:doc:`Read more about how docs are built and contributed to <dev_pages/doc>`

.. rubric:: \\undeployed

This folder holds code that is packaged with dnppy for good record keeping, but is NOT installed with the module. There are a few different categories that code like this falls within, and it is organized as such.

.. rubric:: \\legacy

This is old python code from before our days of configuration management that might have very useful snippets to pull into dnppy.

.. rubric:: \\proj_code

NASA DEVELOP project teams contribute specialized code to this directory for access by project partners. Project code is evaluated for its generality and moved up to the subjects folder, then into dnppy if some generalization is possible. Code in this directory may have a very narrow focus on the needs of the project partners and lack scalability, but may have utility for specific users or have syntactical reference value. Code in this directory may be in any programming language.

.. rubric:: \\subjects

This repository is filled with unstructured code for a generalized purpose that could be useful to refactor and add to the dnppy framework in the near future.

.. rubric:: \\dev

Tools for building the development environment and testing, includes setup of ``sphinx``. Read more about it in the section for developers.

