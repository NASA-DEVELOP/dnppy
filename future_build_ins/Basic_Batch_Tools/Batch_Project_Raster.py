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

#Resampling Type
Resample= arcpy.GetParameterAsText(2)

#For all the rasters in the input folder, change the projection.
for rasters in arcpy.ListRasters():
    arcpy.AddMessage(rasters)
    Out_Name= "Prj_" + rasters[0:-4] + ".tif"
    arcpy.ProjectRaster_management(rasters, Out_Name, prjfile, Resample)
