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

#Output coordinate system.
OutSys= arcpy.GetParameterAsText(1)

#For all the shapefiles in the input folder, alter the projection.
for shps in arcpy.ListFeatureClasses():
    arcpy.AddMessage(shps)
    #Out name is the Output File name.
    Out_Name= "Prj_" + shps
    arcpy.Project_management(shps, Out_Name, OutSys)
        
