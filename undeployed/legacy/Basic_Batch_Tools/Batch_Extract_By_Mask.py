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

#Masking file.
Mask_file= arcpy.GetParameterAsText(1)

#For all the rasters in the file, perform an extract by mask.
for rasters in arcpy.ListRasters():
    arcpy.AddMessage(rasters)
    #Out name is the Output File name. EBM stands for "Extract By Mask".
    Out_Name= "EBM_" + rasters
    outExtractByMask = ExtractByMask(rasters, Mask_file)
    outExtractByMask.save(Out_Name)
