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

#Cell_Size
Cell_Size= arcpy.GetParameterAsText(1)

#Resample Type
Resample_Type= arcpy.GetParameterAsText(2)

#For each raster in the input folder, apply the resample.
for rasters in arcpy.ListRasters():
    out_name= "Resample_" + rasters[0:-4] + ".tif"
    arcpy.Resample_management(rasters, out_name, Cell_Size, Resample_Type)
