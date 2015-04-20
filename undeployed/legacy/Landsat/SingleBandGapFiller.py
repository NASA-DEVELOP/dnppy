#-------------------------------------------------------------------------------
# Name:        Single Band Gap Filler For Landsat 7
# Purpose:      To use cloud masks for three seperate scenes to fill gaps in data
#               due to SLC-induced gaps and clouds
# Author:      Quinten Geddes   Quinten.A.Geddes@nasa.gov
#               NASA DEVELOP PRogram
# Created:     12/04/2013

#-------------------------------------------------------------------------------

import arcpy
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True

#Registering the scenes of interest
Scene1    =   arcpy.Raster(arcpy.GetParameterAsText(0))
Scene2    =   arcpy.Raster(arcpy.GetParameterAsText(1))
Scene3    =   arcpy.Raster(arcpy.GetParameterAsText(2))

#establishing
CloudMaskpath1=   arcpy.GetParameterAsText(3)
CloudMaskpath2=   arcpy.GetParameterAsText(4)
CloudMaskpath3=   arcpy.GetParameterAsText(5)

OutputFolder= arcpy.GetParameterAsText(6)
OutputFile=   arcpy.GetParameterAsText(7)

#preempting scratch workspace errors
arcpy.env.scratchWorkspace=OutputFolder

#establishing gaps in each image
Mask1=Scene1>0
Mask2=Scene2>0
Mask3=Scene3>0

#Applying the Cloud mask if provided
for scene in [1,2,3]:
    try:
        exec("CloudMask{0}=arcpy.Raster(CloudMaskpath{0})".format(scene))
        exec("Mask{0}=Mask{0}*CloudMask{0}".format(scence))
    except:
        a=0

#keeping all good pixels for the first scene
Scene1Fill=Mask1*Scene1
#keeping good pixels for the 2nd scene where 1st pixels are bad
Scene2Fill=((Mask1==0)*Mask2)*Scene2
#keeping good pixels for the 3rd scene where 2nd and 1st pixels are bad
Scene3Fill=((Mask1==0)*(Mask2==0)*Mask3)*Scene3

#combining the kept pixels from each scene
FinalImage=Scene1Fill+Scene2Fill+Scene3Fill

FinalImage.save(OutputFolder+"\\"+OutputFile)
