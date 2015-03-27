"""
======================================================================================
                                   dnppy.modis
======================================================================================

Collection of functions for handling the common MODIS data products

"""


__author__ = ["Jeffry Ely, jeff.ely.08@gmail.com"]

# local imports
from .mosaic import *
from .projection import *
from .extract_from_hdf import *

# standard imports
import sys, os,time

# arcpy imports
import arcpy
if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    from arcpy import sa,env
    arcpy.env.overwriteOutput = True
