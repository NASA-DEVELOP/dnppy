"""
======================================================================================
                                   dnppy.radar
======================================================================================
 The radar module is part of the "dnppy" package (develop national program py).
 This module houses python functions for performing preprocessing tasks radar data,
 including UAVSAR.

 If you wrote a function you think should be added to this module, or have an idea for one
 you wish was available, please email the Geoinformatics YP class or code it up yourself
 for future DEVELOP participants to use!

"""

__author__ = ["Daniel Jensen, danieljohnjensen@gmail.com",
              "Scott Baron"]

# local imports
from .uavsar import *

# standard imports
import os, sys, time, math, arcpy, shutil

# arcpy imports
if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    from arcpy.sa import *
    from arcpy import env
    arcpy.env.overwriteOutput = True