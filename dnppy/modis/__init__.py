"""
Two satellites, Terra and Aqua, are home to a MODIS sensor, which has produced a large number
of data products for over a full decade with minimal interruption. The modis module houses
functions specifically related to processing and handling MODIS data, which includes handling
of the MODIS sinusoidal projection, and mosaic operations.

Requires ``arcpy``
"""

# created October 2014
__author__ = ["Jwely"]

# local imports
from mosaic import *
from define_projection import *
from extract_from_hdf import *