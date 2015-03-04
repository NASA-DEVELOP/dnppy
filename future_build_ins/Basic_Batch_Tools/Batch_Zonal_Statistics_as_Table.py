#---------------------------------
#Name: Zonal Statistics as Table
#Purpose: Summarizes the values of a raster within the zones of another dataset and reports the results to a table
#Notes: FieldName should be the field within the attribute table that defines the entire zone
#Created: 02/24/2014
#---------------------------------

import arcpy, arcgisscripting, sys, os, csv, string
from arcpy import env
from arcpy.sa import *

##################################
#Input user parameters
arcpy.env.workspace = r"INPUT PATH TO TIFF FOLDER HERE"
OutputFolder = r"INPUT PATH TO OUTPUT DBF FOLDER HERE"
ShapefileMask = r"INPUT SHAPEFILE NAME HERE (NOT FILE PATH, JUST NAME WITH '.SHP' ATTACHED"
FieldName = "SEE NOTES"
###################################

arcpy.env.overwriteOutput = True

# Loops through a list of files in the workspace
TIFfiles = arcpy.ListFiles("*.tif")

# Performs Zonal Statistics
for filename in TIFfiles:
    fileroot = filename[0:(len(filename)-3)]
    print ("Calculating zonal statistics on: " + filename + " using " + ShapefileMask)
    inValueRaster = arcpy.env.workspace + "/" + filename
    outTable = OutputFolder + "/" + fileroot

    arcpy.CheckOutExtension("Spatial")

    outZstat = ZonalStatisticsAsTable(ShapefileMask, FieldName, inValueRaster, outTable, "NODATA", "ALL")

print "Done!"
    
