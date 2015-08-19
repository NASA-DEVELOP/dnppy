

__author__ = ["Daniel Jensen, danieljohnjensen@gmail.com",
                "Scott Baron"]

import arcpy
from arcpy.sa import *


def decibel_convert(filename):
    """
    Converts the input UAVSAR .grd file into units of decibels.

    *Note that a .hdr file must be created and accompany the .grd/.inc files for this to work

    Inputs:
        file:   the full file path string for the .grd data file
    """

    #arcpy.CheckOutExtension("Spatial")

    inRaster = arcpy.Raster(filename)
    dB_raster = 10 * Log10(inRaster)
    outname = filename.replace(".grd", "_dB.tif")
    dB_raster.save(outname)

    return
