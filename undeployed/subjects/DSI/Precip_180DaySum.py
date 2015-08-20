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
interp_F = "C:/Users/torne/Documents/GP_Ag/Data/Precipitation/180day_script/Raw_precip/Inter_precip" ## Folder containing interpolated precip rasters
Rolling_sum_F = "C:/Users/torne/Documents/GP_Ag/Data/Precipitation/180day_script/Raw_precip/Inter_precip/Sum_precip" ##Folder to save precip sum rasters




env.workspace = interp_F
sumlist = arcpy.ListRasters("*int.tif")
print sumlist
for octad in range(len(sumlist)/8):
    firstraster = sumlist[octad*8]
    if octad*8 > 180: 
        last180days = sumlist[(octad*8)-179:(octad*8)+1]
        cellstats = CellStatistics(last180days, "SUM", "DATA")
        cellstats.save("C:\\Users\\torne\\Documents\\GP_Ag\\Data\\Precipitation\\Test_Script\\Sum_Precip" + "\\" + str(firstraster[0:-7]) + "_180Day_Sum.tif")
        print firstraster + "180 Day Summed"
    print "FIN"
