import os
import gc
import arcpy
from arcpy import env
from arcpy.sa import *
env.overwriteOutput = True
gc.disable()
arcpy.CheckOutExtension("Spatial")
env.workspace = "GENERAL WORKSPACE" ##SET AS PARAMETER

#Sum rasters
#change projection
#add color ramp

i = 0
j = 1
k = 2
dsilist = arcpy.ListRasters("*scaled.tif"):
    for rasters in dsilist:
        while i < len(dsilist) or j < len(dsilist) or k < len(dsilist):
            inRast1 = dsilist[i]
            inRast2 = dsilist[j]
            inRast3 = dsilist[k]
            LST = Times(0.25,inRast1)
            NDVI = Times(0.25,inRast2)
            Precip = Times(0.5,inRast3)
            cellstats = CellStatistics([LST,NDVI,Precip],"SUM", "NODATA")
            cellstats.save(inRast1[0:-11]+ "dsi.tif")
            print "Cell Stats:" + inRast1[0:-11] + "Complete"
            i = i + 3
            j = j + 3
            k = k + 3

       
            

            
                
                
                
            
           
            
            
