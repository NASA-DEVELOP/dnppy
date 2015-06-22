import os
import gc
import arcpy
from arcpy import env
from arcpy import sa
from arcpy.sa import *
env.overwriteOutput = True
gc.disable()
arcpy.CheckOutExtension("Spatial")
env.workspace = "C:/Users/torne/Documents/GP_Ag/Data/Precipitation/180day_script" ##WORKSPACE
raw_precip_F = "C:/Users/torne/Documents/GP_Ag/Data/Precipitation/180day_script/Raw_precip" ##Folder containing raw precip files
interp_F = "C:/Users/torne/Documents/GP_Ag/Data/Precipitation/180day_script/Raw_precip/Inter_precip" ##Folder to save interpolated precip rasters
study_area = "C:/Users/torne/Documents/GP_Ag/Data/Precipitation/180day_script/StudyArea/newgp_usgs.shp" ##STUDY AREA shpfile
allpoint = "C:/Users/torne/Documents/GP_Ag/Data/Precipitation/180day_script/Allpoint/allpoint_clip.shp" ##ALLPOINT file


#####CREATE BUFFER AND JOIN POINTS

buff = arcpy.Buffer_analysis(study_area, "SA_Buff", "10000 Meters")
print "SA Buffer: Done"
dis = arcpy.Dissolve_management(buff,"SA_Dis")
print "SA Buffer: Done"
allpoint_Clip= arcpy.Clip_analysis(allpoint, dis, "AllPointClip")
print "SA Clip: Done"
print "work"



env.workspace = raw_precip_F
cliplist = arcpy.ListFeatureClasses("nws*.shp")
for files in cliplist:
	clip = arcpy.Clip_analysis(files,dis,"C:\\Users\\torne\\Documents\\GP_Ag\\Data\\Precipitation\\180day_script\\Raw_precip\\Inter_precip" + "\\" + files[25:33] + "SA.shp")
	print "Part I: Clip Complete"
	shp_layer = files[25:-33] + "layer"
	arcpy.MakeFeatureLayer_management(allpoint_Clip, "allpoint_layer")
	arcpy.MakeFeatureLayer_management(clip,shp_layer)
	print shp_layer + "Feature Layers Complete"
	allpoint_lyr = arcpy.AddJoin_management("allpoint_layer","Id",shp_layer,"Id")
	join = arcpy.CopyFeatures_management(allpoint_lyr, "C:\\Users\\torne\\Documents\\GP_Ag\\Data\\Precipitation\\180day_script\\Raw_precip\\Inter_precip" + "\\" + files[25:33] + "_join.shp")
	print "Part II: Join Complete"
	interpolation = NaturalNeighbor(join, str(files[25:33]) + "_6", 1.10376739501955E-03)
	interpolation.save("C:\\Users\\torne\\Documents\\GP_Ag\\Data\\Precipitation\\180day_script\\Raw_precip\\Inter_precip" + "\\" + files[25:33] + "int.tif")
	print  "Part III: Interpolation Complete"

print "FIN"
