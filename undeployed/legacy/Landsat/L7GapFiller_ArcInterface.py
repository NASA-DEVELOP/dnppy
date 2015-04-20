#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      qgeddes
#
# Created:     25/04/2013
# Copyright:   (c) qgeddes 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import L7GapFiller


Scenes=arcpy.GetParameterAsText(0)
Scenes=Scenes.split(";")

OutputFolder=arcpy.GetParameterAsText(1)
OutputFile=   arcpy.GetParameterAsText(2)
Output=OutputFolder+"\\"+OutputFile
CloudMasks=   arcpy.GetParameterAsText(3)
CloudMasks=   CloudMasks.split(";")
Z=arcpy.GetParameter(4)

arcpy.AddMessage(Z)
arcpy.env.scratchWorkspace=OutputFolder
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput=True

L7GapFiller.L7GapFill(Scenes, Output,CloudMasks,Z)
