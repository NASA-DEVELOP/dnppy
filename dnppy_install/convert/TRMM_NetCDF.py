
# standard imports
import sys
import os

# dnppy imports
from dnppy import core

# arcpy imports
import arcpy
if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    from arcpy.sa import *
    from arcpy import env
    arcpy.env.overwriteOutput = True

    
def TRMM_NetCDF(filelist, outdir):

    """
     Function converts NetCDFs to tiffs. Designed to work with TRMM data.

     inputs:
       filelist    list of '.nc' files to conver to tifs.
       outdir      directory to which tif files should be saved
    """

    # Set up initial parameters.
    arcpy.env.workspace = outdir
    filelist    = core.enforce_list(filelist)

    # convert every file in the list "filelist"
    for infile in filelist:
        
        # use arcpy module to make raster layer from netcdf
        arcpy.MakeNetCDFRasterLayer_md(infile, "r", "longitude", "latitude", "r", "", "", "BY_VALUE")
        arcpy.CopyRaster_management("r", infile[:-3] + ".tif", "", "", "", "NONE", "NONE", "")
        print('{NetCDF} Converted netCDF file ' + infile + ' to Raster')

    return
