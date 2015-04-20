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

#Desired Projection
prjfile= arcpy.GetParameterAsText(1)

#Define projection to all datasets.
for shps in arcpy.ListFeatureClasses():
    arcpy.AddMessage(shps)
    arcpy.DefineProjection_management(shps, prjfile)
