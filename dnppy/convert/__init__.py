"""
dnppy convert contains functions for conversion between filetypes. Usually between
a file type distributed by a NASA Distributed Active Archive Center (DAAC) such as
NetCDF or HDF5 to geotiff. Due to differences in metadata standards, many of these
functions only operate successfully data from a specific source.

Requires ``arcpy``
"""

__author__ = ["Jwely",
              "djjensen"]


from datatype_library import *
from extract_archive import *
from extract_GCMO_NetCDF import *
from extract_GPM_IMERG import *
from extract_GRACE_DA_binary import *
from extract_MPE_NetCDF import *
from extract_SMOS_NetCDF import *
from extract_TRMM_HDF import *
from extract_TRMM_NetCDF import *
from HDF5_to_numpy import *
from ll_to_utm import *
from nongrid_data import *

# special members
from _convert_dtype import *
from _extract_HDF_datatype import *
from _extract_HDF_layer_data import *
from _extract_NetCDF_datatype import *
from _extract_NetCDF_layer_data import *
from _gdal_dataset_to_tif import *

# file type declarations
HDF_EXTENSIONS = ["hdf", "h4", "hdf4", "he2", "h5", "hdf5", "he5", "rt-h5",
                  "HDF", "H4", "HDF4", "HE2", "H5", "HDF5", "HE5", "RT-H5"]

NETCDF_EXTENSIONS = ["nc", "cdf",
                     "NC", "CDF"]

