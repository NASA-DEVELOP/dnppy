"""
======================================================================================
                                   dnppy.core
======================================================================================
 This script is part of (dnppy) or "DEVELOP National Program py"
 It is maintained by the Geoinformatics YP class.

It contains some core functions to assist in data formatting , path manipulation, and
logical checks. It is commonly called by other modules in the dnppy package.


 Requirements:
   Python 2.7
   Arcmap 10.2 or newer for some functions

   Example:
   from dnppy import core
   Sample_Function('test',False)
"""

__author__ = ["Jeffry Ely, jeff.ely.08@gmail.com"]


# local imports
from .core import *
from .enforce import *




# standard imports
import os, datetime, sys, shutil


# arcpy imports
if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    from arcpy.sa import *
    from arcpy import env
    arcpy.env.overwriteOutput = True
