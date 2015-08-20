"""
The raster module is used to analyze raster data from non-specific sources. In an idealized
workflow, use of the convert and download modules can help users obtain and pre-process data
for use with functions in the raster module. The modules capabilities include statistics
generation, subsetting, reprojecting, null data management, correction functions, and others.
Top level functions in the raster module should all have batch processing capabilities bult in.

Requires ``arcpy``
"""

__author__ = ["Jwely",
              "lmakely"]


from apply_linear_correction import *
from clip_and_snap import *
from clip_to_shape import *
from degree_days import *
from degree_days_accum import *
from enf_rastlist import *
from from_numpy import *
from to_numpy import *
from grab_info import *
from in_dir import *
from is_rast import *
from many_stats import *
from null_define import *
from null_set_range import *
from project_resample import *
from raster_fig import *
from raster_overlap import *
from spatially_match import *
from gap_fill_temporal import *
from gap_fill_interpolate import *


# this code will test the raster module
# it assumes that some data is available in a dnppy_test directory
# this code should be migrated to a more permanent testing framework
if __name__ == "__main__":

    import os

    test_dir = r"C:\dnppy_test"
    va_shape = os.path.join(test_dir, 'VA_Orig.shp')

