## LAND SURFACE TEMPERATURE
import fnmatch
import arcpy
import os
import gc
gc.disable()
from arcpy import env
from arcpy.sa import*
arcpy.CheckOutExtension("Spatial") #Turns on Spatial Analyst Extension
env.workspace = arcpy.GetParameterAsText(0) # TO BE PARAMETER
env.overwriteOutput = True #If TRUE: when ran deletes data if it already exists. If FALSE: Does not delte data that already exists.
study_area = arcpy.GetParameterAsText(1) # MUST BE IN GEODATABASE # TO BE PARAMETER


## HDF > RASTER TIFF
lst = arcpy.ListFiles("*.hdf")
mosaiclist = []
for filez in lst:              
    output_rast = filez[0:-4]+"_raster" + ".tif" 
    extracted = arcpy.ExtractSubDataset_management(filez,output_rast,"0")
    OutExtractByMask = ExtractByMask(extracted, study_area)
    OutExtractByMask.save((filez[0:-4])+"_sa.tif")
   
   
## MOSAIC RASTERS TOGETHER

for dirname, dirnames, filenames in os.walk(env.workspace):
    for subdirname in dirnames:
        env.workspace = os.path.join(dirname, subdirname)
        
        mosaiclist = arcpy.ListRasters("*sa.tif")
        M_Out = env.workspace     
        i = 0
        for raster in mosaiclist:
            while i < len(lst):
                currentPattern = lst[i]
                M_outname = currentPattern[0:-8] + "_LST.tif"
                pattern = currentPattern[0:6]+"*.tif"
                group = fnmatch.filter(mosaiclist,pattern)
                print group
                arcpy.MosaicToNewRaster_management(group,M_Out,M_outname,"","16_BIT_UNSIGNED","","1")
                if len(group) == 1:
                    group.save(M_outname) ## HOW TO SAVE CONTENT
                    print "Group 1"
                    i = i + 1
                elif len(group)== 2:
                    arcpy.MosaicToNewRaster_management(group,M_Out,M_outname,"","16_BIT_UNSIGNED","","1")
                    print "Group 2"
                    i = i + 2
                elif len(group) == 3:
                    arcpy.MosaicToNewRaster_management(group,M_Out,M_outname,"","16_BIT_UNSIGNED","","1")
                    print "Group 3"
                    i = i + 3
                else:
                    break
            
        scalelist = arcpy.ListRasters("*LST.tif")
        for rasters in scalelist:
            minRast = arcpy.GetRasterProperties_management(rasters, "MINIMUM")
            minvalue = (minRast.getOutput(0))
            maxRast = arcpy.GetRasterProperties_management(rasters, "MAXIMUM")
            maxvalue = (maxRast.getOutput(0))
            num = Minus(float(maxvalue), rasters)
            denom = float(maxvalue)- float(minvalue)
            scaledLST = Divide(num,denom)
            scaledoutplace = arcpy.GetParameterAsText(2) #MAKE PARAMETER OUTPUTFOLDER 
            scaledLST.save(scaledoutplace + rasters[0:-4] + "_scaled.tif")
            
 

            

            

            
        

