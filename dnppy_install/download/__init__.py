"""
The download module houses many "fetch" functions for automatic retrieval of specific data products from ``http`` and ``ftp`` servers around the USA. While centered around NASA data products, some functions exist for fetching of ancillary NOAA climate products and others.
"""

__author__ = ["Jwely"]

# local imports
from download_filelist import *
from download_url import *
from download_urls import *

from fetch_GPM_IMERG import *
from fetch_Landsat8 import *
from fetch_LandsatWELD import *
from fetch_MODIS import *
from fetch_MPE import *
from fetch_SRTM import *
from fetch_TRMM import *


from list_http_e4ftl01 import *
from list_http_waterweather import *
from list_ftp import *
