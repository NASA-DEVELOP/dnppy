import os
import gc
import arcpy
from arcpy import env
from arcpy import sa
from arcpy.sa import *
env.overwriteOutput = True
gc.disable()
arcpy.CheckOutExtension("Spatial")
env.workspace = arcpy.GetParameterAsText(0) ## PARAMETER: WORKSPACE
raw_precip_F = arcpy.GetParameterAsText(1) ##Folder: Containing raw_Precip
interp_F = arcpy.GetParameterAsText(2)## Folder: Containing Interpolated Precip Rasters
Rolling_sum_F = arcpy.GetParameterAsText(3) ##Folder: Containt Summed Precip Rasters
study_area = arcpy.GetParameterAsText(4) ## PARAMETER: STUDY AREA 
allpoint = arcpy.GetParameterAsText(5) ## PARAMETER: ORGINAL ALL POINT 


#####CREATE BUFFER AND JOIN POINTS

buff = arcpy.Buffer_analysis(study_area, "SA_Buff", "10000 Meters")
print "SA Buffer: Done"
dis = arcpy.Dissolve_management(buff,"SA_Dis")
print "SA Buffer: Done"
allpoint_Clip= arcpy.Clip_analysis(allpoint, dis, "AllPointClip")
print "SA Clip: Done"
print "work"



env.workspace = raw_precip_F ##SET AS PARAMETER FOLDER WITH PRECIPDATA
cliplist = arcpy.ListFeatureClasses("nws*.shp")
for files in cliplist:
    clip = arcpy.Clip_analysis(files,dis,"C:\\Users\\lewatkin\\Desktop\\PRISM\\2011\\Clip_Precip" + "\\" + files[25:33] + "SA.shp")
    print "Part I: Clip Complete"
    shp_layer = files[25:-33] + "layer"
    arcpy.MakeFeatureLayer_management(allpoint_Clip, "allpoint_layer")
    arcpy.MakeFeatureLayer_management(clip,shp_layer)
    print shp_layer + "Feature Layers Complete"
    allpoint_lyr = arcpy.AddJoin_management("allpoint_layer","Id",shp_layer,"Id")
    join = arcpy.CopyFeatures_management(allpoint_lyr, "C:\\Users\\lewatkin\\Desktop\\PRISM\\2011\\Interpolate" + "\\" + files[25:33] + "_join.shp")
    print "Part II: Join Complete"
    interpolation = NaturalNeighbor(join, str(files[25:33]) + "_6", 1.10376739501955E-03)
    interpolation.save("C:\\Users\\lewatkin\\Desktop\\PRISM\\2011\\Interpolate" + "\\" + files[25:33] + "int.tif")
    print  "Part III: Interpolation Complete"




env.workspace = interp_F ##SET AS PARAMETER
sumlist = arcpy.ListRasters("*int.tif")
print sumlist
for octad in range(len(sumlist)/8):
    firstraster = sumlist[octad*8]
    if octad*8 > 30: 
        last30days = sumlist[(octad*8)-29:(octad*8)+1]
        cellstats = CellStatistics(last30days, "SUM", "DATA")
        cellstats.save("C:\\Users\\lewatkin\\Desktop\\Lance_Precip\\2012\\Rolling_Sum_30" + "\\" + str(firstraster[0:-7]) + "_30Day_Sum.tif")
        print firstraster + "30 Day Summed"

            
##SCALLING 
          
env.workspace = Rolling_sum_F 
scalelist = arcpy.ListRasters()
print scalelist
for tif in scalelist:
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
    scaledLST.save("C:\\Users\\lewatkin\\Desktop\\Lance_Precip\\2012\\Scaled_Sum_30" + "\\" + tif[0:-7] + "precip_scaled.tif")
    print "HUZZAHH"
