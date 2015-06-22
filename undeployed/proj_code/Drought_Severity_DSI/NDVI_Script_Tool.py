## NDVI
import fnmatch
import arcpy
import os
import gc
gc.disable()
from arcpy import env
from arcpy.sa import*
arcpy.CheckOutExtension("Spatial") #Turns on Spatial Analyst Extension
env.workspace = "C:\\Users\\Lance\\Desktop\\NDVI"#arcpy.GetParameterAsText(0) # TO BE PARAMETER## CHANGE YEAR AS NEEDED!!!!!###
env.overwriteOutput = True #If TRUE: when ran deletes data if it already exists. If FALSE: Does not delte data that already exists.
study_area = "C:\\Users\\Lance\\NASA\\Study_Area.mdb\\study_area" #arcpy.GetParameterAsText(1) # MUST BE IN GEODATABASE # TO BE PARAMETER


## HDF > RASTER TIFF
# creates list of hdf files that will be changed to tiff
# for loop states: for all hdf files in the list do the following
#output_rast = renaming the output raster for the loop
# arcpy.extractsub... arc tool to change hdf to tif
lst = arcpy.ListFiles("*.hdf")
for filez in lst:
    output_rast = filez[0:-4]+"_rasterN" + ".tif" 
    extracted = arcpy.ExtractSubDataset_management(filez,output_rast,"0;1")
    OutExtractByMask = ExtractByMask(extracted, study_area)
    OutExtractByMask.save((filez[0:-4]) + "_mosN.tif")
   
    

mosaiclist = arcpy.ListRasters("*mosN.tif")
M_Out = env.workspace     

i = 0
for raster in mosaiclist:
    while i < len(lst):
        currentPattern = lst[i]
        M_outname = currentPattern[0:-8] + "sa_N.tif"
        pattern = currentPattern[0:6]+"*.tif"
        group = fnmatch.filter(mosaiclist,pattern)
        print group
        if len(group) == 1:
            group.save(M_outname)##HOW TO SAVE CONTENT
            print "Group 1"
            i = i + 1
        elif len(group)== 2:
            arcpy.MosaicToNewRaster_management(group,M_Out,M_outname,"","16_BIT_UNSIGNED","","2")
            print "Group 2"
            i = i + 2
        elif len(group) == 3:
            arcpy.MosaicToNewRaster_management(group,M_Out,M_outname,"","16_BIT_UNSIGNED","","2")
            print "Group 3"
            i = i + 3
        else:
            break
       
for sa_rast in arcpy.ListRasters("*sa_N.tif"):
    red = sa_rast + "\Band_1"
    nir = sa_rast + "\Band_2"
    Num = arcpy.sa.Float(Raster(nir) - Raster(red))
    Denom = arcpy.sa.Float(Raster(nir) + Raster(red))
    NDVI_eqn = arcpy.sa.Divide(Num,Denom)
    NDVI = ATan(NDVI_eqn)
    NDVI.save(sa_rast[0:-8] + "_NDVI.tif")
            
for ndvi in arcpy.ListRasters("*NDVI.tif"):
    minRast = arcpy.GetRasterProperties_management(ndvi, "MINIMUM")
    minvalue = (minRast.getOutput(0))
    maxRast = arcpy.GetRasterProperties_management(ndvi, "MAXIMUM")
    maxvalue = (maxRast.getOutput(0))
    num = Minus(ndvi, float(minvalue))
    denom = float(maxvalue) - float(minvalue)
    scaledLST = arcpy.sa.Divide(num,denom)
    scaledoutplace = "C:\\Users\\Lance\\Desktop\\NDVI\\NDVI_Scaled" #arcpy.GetParameterAsText(2) # TO BE PARAMETER ## Change Year as Needed
    scaledLST.save(scaledoutplace + "\\" + ndvi[0:-4] + "_scaled.tif")
    
            
       
