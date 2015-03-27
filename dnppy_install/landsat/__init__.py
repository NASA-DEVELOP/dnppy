"""
======================================================================================
                                   dnppy.landsat
======================================================================================
 The "landsat.py" module is part of the "dnppy" package (develop national program py).
 This module houses python functions for performing image processing tasks on Landsat 4,
 5, 7, and 8 data.

 If you wrote a function you think should be added to this module, or have an idea for one
 you wish was available, please email the Geoinformatics YP class or code it up yourself
 for future DEVELOP participants to use!

"""

__author__ = ["Daniel Jensen, danieljohnjensen@gmail.com",
              "Jeffry Ely, jeff.ely.08@gmail.com",
              "Quinten Geddes"]

# local imports
from .atsat_bright_temp import *
from .cloud_mask import *
from .grab_meta import *
from .ndvi import *
from .scene import *
from .surface_reflectance import *
from .surface_temp import *
from .toa_radiance import *
from .toa_reflectance import *

from dnppy import core

# standard imports
import os, sys, time, math, arcpy, shutil
if core.check_module("numpy"): import numpy

# arcpy imports
if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    from arcpy.sa import *
    from arcpy import env
    arcpy.env.overwriteOutput = True
