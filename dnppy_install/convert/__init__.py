"""
dnppy convert contains functions for misc conversion between formats and types. 
"""

__author__ = ["Jwely"]

from datatype_library import *
from extract_GPM_IMERG import *
from extract_targz import *
from GCMO_NetCDF import *
from datatype_library import *

# filetype delcarations

HDF_EXTENSIONS = ["hdf", "h4", "hdf4", "he2", "h5", "hdf5", "he5", "rt-h5",
                  "HDF", "H4", "HDF4", "HE2", "H5", "HDF5", "HE5", "RT-H5"]

NETCDF_EXTENSIONS = ["nc", "cdf",
                     "NC", "CDF"]

