"""
dnppy convert contains functions for conversion between filetypes. Usually between
a file type distributed by a NASA Distributed Active Archive Center (DAAC) such as
NetCDF or HDF5 to geotiff. Due to differences in metadata standards, many of these
functions only operate successfully data from a specific source.
"""

__author__ = ["Jeffry Ely, jeff.ely.08@gmail.com"]

from extract_targz import *
from GCMO_NetCDF import *


