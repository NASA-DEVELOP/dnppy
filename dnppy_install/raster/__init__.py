"""
======================================================================================
                                   dnppy.raster
======================================================================================
This script is part of (dnppy) or "DEVELOP National Program py"
It is maintained by the Geoinformatics YP class.

It contains functions for fairly routine manipulations of raster data.
"""

__author__ = ["Jeffry Ely, jeff.ely.08@gmail.com",
              "Lauren Makely, lmakely09@gmail.com"]

# local imports
from .figures import *
from .grab_data_info import *
from .null_values import *
from .project_resample import *
from .raster_clipping import *
from .raster_enforcement import *
from .raster_numpy_inter import *
from .raster_overlap import *
from .raster_stack import *
from .raster_statistics import *
from .temporal_fill import *


# standard imports
import os, shutil, time
import matplotlib.pyplot as plt
from dnppy import core

if core.check_module('numpy'): import numpy

# arcpy imports
import arcpy
if arcpy.CheckExtension('Spatial') == 'Available':
    arcpy.CheckOutExtension('Spatial')
    from arcpy import sa, env
    arcpy.env.overwriteOutput = True
    
