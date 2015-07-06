"""
======================================================================================
                                   dnppy.raster
======================================================================================
This module is part of (dnppy) or "DEVELOP National Program py"
It is maintained by the Geoinformatics YP class.

It contains functions for fairly routine manipulations of raster data.
"""

__author__ = ["jwely",
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

