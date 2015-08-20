import os
import gc
import arcpy
from arcpy import env
from arcpy import sa
from arcpy.sa import *
env.overwriteOutput = True
gc.disable()
arcpy.CheckOutExtension("Spatial")
env.workspace = "C:/Users/torne/Documents/GP_Ag/Data/Precipitation/180day_script" ## WORKSPACE
Rolling_sum_F = "C:/Users/torne/Documents/GP_Ag/Data/Precipitation/180day_script/Raw_precip/Inter_precip/Sum_precip" ##Folder containing precip sum rasters



env.workspace = Rolling_sum_F 
scalelist = arcpy.ListRasters()
print scalelist
for files in scalelist:
    minRast = arcpy.GetRasterProperties_management(tif, "MINIMUM")
    minvalue = (minRast.getOutput(0))
    maxRast = arcpy.GetRasterProperties_management(tif, "MAXIMUM")
    maxvalue = (maxRast.getOutput(0))
    print maxvalue + "_max"
    print minvalue + "_min"
    num = Minus(tif, float(minvalue))
    denom = float(maxvalue) - float(minvalue)
    print str(denom)
    scaledLST = arcpy.sa.Divide(num,denom)
    scaledLST.save("C:\\Users\\torne\\Documents\\GP_Ag\\Data\\Precipitation\\180day_script\\Raw_precip\\Inter_precip\\Sum_precip\\Scale_sum" + "\\" + files[0:-7] + "precip_scaled.tif")
    print "FIN"
