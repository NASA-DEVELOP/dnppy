import arcpy
#Makes sure Spatial Analyst is turned on.
if arcpy.CheckExtension("Spatial")== "Available":
    arcpy.CheckOutExtension("Spatial")
    from arcpy.sa import *
else:
    arcpy.AddError("You do not have the Spatial Analyst Extension, and therefore cannot use this tool.")
    
#Input folder.
folder_path= r"H:\Spectral"
arcpy.env.workspace= folder_path

"""#Iso1
outUnsupervised = IsoClusterUnsupervisedClassification(("Clip_North_Hansen_2000Band5.tif","Clip_North_Hansen_2000Band7.tif","Clip_z2000_7_5.tif","Clip_zDivide200057.tif"), 30, 20, 10)
outUnsupervised.save("Iso1.tif")

#Iso2
outUnsupervised = IsoClusterUnsupervisedClassification(("Clip2_North_Hansen_2012Band5.tif","Clip2_North_Hansen_2012Band7.tif","Clip2_z2012_7_5.tif","Clip2_zDivide201257.tif"), 30, 20, 10)
outUnsupervised.save("Iso2.tif")

#Iso3
outUnsupervised = IsoClusterUnsupervisedClassification(("Clip_North_Hansen_2000Band3.tif","Clip_North_Hansen_2000Band4.tif","Clip_North_Hansen_2000Band5.tif","Clip_North_Hansen_2000Band7.tif","Clip_z2012_3_5.tif","Clip_z2012_5_4.tif","Clip_z2012_7_5.tif"), 30, 20, 10)
outUnsupervised.save("Iso3.tif")

#Iso4
outUnsupervised = IsoClusterUnsupervisedClassification(("Clip2_North_Hansen_2000Band3.tif","Clip2_North_Hansen_2000Band4.tif","Clip2_North_Hansen_2000Band5.tif","Clip2_North_Hansen_2000Band7.tif","Clip2_z2012_3_5.tif","Clip2_z2012_5_4.tif","Clip2_z2012_7_5.tif"), 30, 20, 10)
outUnsupervised.save("Iso4.tif")"""
Mask_file= "Caclulated_Mangroves.tif"

for rasters in arcpy.ListRasters():
    if rasters[0:5]== "Clip_":
        print rasters[5:]
        OutName= "WithoutMang_" + rasters[5:]
        outCon = Con("C:/Users/sbarron/Desktop/Delete_Folder/Mangroves_Null.tif", rasters, "", "VALUE = 1")
        outCon.save(OutName)
