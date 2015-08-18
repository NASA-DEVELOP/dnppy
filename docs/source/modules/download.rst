download
========

.. automodule:: dnppy_install.download
    :members:

Examples
--------

.. rubric:: Fetching MODIS

Automated download or "fetching" can be helpful for bulk data retrieval, or for enabling software to pull the most up to date data at runtime. This module has a few fetch functions for different NASA data platforms and products.
As an example, the proper syntax for the `fetch_MODIS` function to download all available data for 2015 (January 1st through December 31st) is

.. code-block:: python

    from dnppy import download
    from datetime import datetime

    product = "MYD11A1"                  # land surface temperature
    version = "041"                      # version 041
    tiles = ["h11v05", "h12v05"]         # two tiles of interest (SouthEast US)
    outdir = r"C:\Users\jwely\test"      # local path to save files
    start_dto = datetime(2015,1,1)       # datetime object of start date
    end_dto = datetime(2015,12,31)       # datetime object of end date

    download.fetch_MODIS(product, version, tiles, outdir, start_dto, end_dto)

The other fetching functions work similarly.


Code Help
---------

Auto-documentation for functions and classes within this module is generated below!

.. automodule:: dnppy_install.download.download_filelist
    :members:

.. automodule:: dnppy_install.download.download_url
    :members:

.. automodule:: dnppy_install.download.download_urls
    :members:

.. automodule:: dnppy_install.download.fetch_GPM_IMERG
    :members:

.. automodule:: dnppy_install.download.fetch_Landsat8
    :members:

.. automodule:: dnppy_install.download.fetch_LandsatWELD
    :members:

.. automodule:: dnppy_install.download.fetch_MODIS
    :members:

.. automodule:: dnppy_install.download.fetch_MPE
    :members:

.. automodule:: dnppy_install.download.fetch_SRTM
    :members:

.. automodule:: dnppy_install.download.fetch_TRMM
    :members:

.. automodule:: dnppy_install.download.list_http_e4ftl01
    :members:

.. automodule:: dnppy_install.download.list_http_waterweather
    :members:

.. automodule:: dnppy_install.download.list_ftp
    :members:


