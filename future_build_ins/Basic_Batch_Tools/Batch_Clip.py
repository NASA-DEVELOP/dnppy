import arcpy
#Makes sure Spatial Analyst is turned on.
if arcpy.CheckExtension("Spatial")== "Available":
    arcpy.CheckOutExtension("Spatial")
    from arcpy.sa import *
else:
    arcpy.AddError("You do not have the Spatial Analyst Extension, and therefore cannot use this tool.")

#Input folder.
folder_path= arcpy.GetParameterAsText(0)
arcpy.env.workspace= folder_path

#Clipping file.
Clip_file= arcpy.GetParameterAsText(1)

#For all the shapefiles in the folder, perform a clip.
for shps in arcpy.ListFeatureClasses():
    if shps != Clip_file:
        arcpy.AddMessage(shps)
        #Out name is the Output File name.
        Out_Name= "Clip_" + shps
        arcpy.Clip_analysis(shps, Clip_file, Out_Name)
