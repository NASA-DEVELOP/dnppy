#--------------------------------------
#Name: Batch NetCDF to Raster
#Purpose: Convert NetCDF files to Raster TIFFs
#Created: 2/24/2014
#Notes: Fill in text where designated by all Caps except for "BY_VALUE"
        #Variable name is the name of the scientific data set of interest (rainfall, temperature, etc.)
#---------------------------------------

import arcpy, sys, os, csv, string
from arcpy import env
from arcpy.sa import *

#######################################
# Input user parameters
arcpy.env.workspace = "INSERT PATH TO NETCDF FILES"
OutputFolder = "INSERT PATH TO OUTPUT TIFF FOLDER"
TempLayerFile = "INSERT VARIABLE NAME"
variable = "INSERT VARIABLE NAME"
XDimension = "INSERT LONGITUDE DIMENSION NAME"
YDimension = "INSERT LATITUDE DIMENSION NAME"
########################################

arcpy.env.overwriteOutput = True

# Loops through list of netCDF files
NCfiles = arcpy.ListFiles("*.nc")

# For each netCDF in Input Folder, convert to TIFF
for filename in NCfiles:
    print("Converting netCDF file " + filename + " to Raster")
    inNCfiles = arcpy.env.workspace + "/" + filename
    fileroot = filename[0:(len(filename)-3)]
    outRasterLayer = OutputFolder + "/" + fileroot
    bandDimension = ""
    dimensionValues = ""
    valueSelectionMethod = "BY_VALUE"

    # Process: Make NetCDF Raster Layer
    arcpy.MakeNetCDFRasterLayer_md(inNCfiles, variable, XDimension, YDimension, TempLayerFile, "", "", "BY_VALUE")   

    arcpy.CopyRaster_management(TempLayerFile, outRasterLayer + ".tif", "", "", "", "NONE", "NONE", "")

print "Done"
