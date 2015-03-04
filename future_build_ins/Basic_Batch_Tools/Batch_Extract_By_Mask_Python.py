import arcpy
#Makes sure Spatial Analyst is turned on.
if arcpy.CheckExtension("Spatial")== "Available":
    arcpy.CheckOutExtension("Spatial")
    from arcpy.sa import *
else:
    arcpy.AddError("You do not have the Spatial Analyst Extension, and therefore cannot use this tool.")
    
#Input folder.
folder_path= raw_input("Please enter the name and location of the folder containing the data to be masked: ")
arcpy.env.workspace= r"%s" %folder_path

#Masking file.
Mask= raw_input("Please enter the name of the masking file: ")
Mask_file= r"%s" %Mask

#For all the rasters in the file, perform an extract by mask.
for rasters in arcpy.ListRasters():
    #Out name is the Output File name. EBM stands for "Extract By Mask".
    Out_Name= "EBM" + rasters[]
    print Out_Name
    outExtractByMask = ExtractByMask(rasters, Mask_file)
    outExtractByMask.save(Out_Name)
