"""
======================================================================================
                                   dnppy.calc
======================================================================================
 This script is part of (dnppy) or "DEVELOP National Program py"
 It is maintained by the Geoinformatics YP class.

It contains functions for specific mathematical opperations, typically on raster data.
Also see dnppy.raster

This is a likely location for project specific calculation scripts to wind up
"""

__author__ = ["Jeffry Ely, jeff.ely.08@gmail.com",
              "Lauren Makely, lmakely09@gmail.com"]


# local imports
from .apply_linear_correction import *
from .degree_days import *

# standard imports
from dnppy import core
from dnppy import raster

