"""
dnppy convert contains functions for conversion between filetypes. Usually between
a file type distributed by a NASA Distributed Active Archive Center (DAAC) such as
NetCDF or HDF5 to geotiff. Due to differences in metadata standards, many of these
functions only operate successfully data from a specific source.

Requires ``arcpy``: Yes, slightly
"""

__author__ = ["Jwely",
              "djjensen"]

from extract_targz import *
from GCMO_NetCDF import *
from GRACE_DA_to_raster import *


