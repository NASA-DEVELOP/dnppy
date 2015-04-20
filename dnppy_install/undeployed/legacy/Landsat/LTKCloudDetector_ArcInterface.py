#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      qgeddes
#
# Created:     26/04/2013
# Copyright:   (c) qgeddes 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import LTKCloudDetector

Band1path=arcpy.GetParameterAsText(0)
Band3path=arcpy.GetParameterAsText(1)
Band4path=arcpy.GetParameterAsText(2)
Band5path=arcpy.GetParameterAsText(3)

pixelvalue=arcpy.GetParameterAsText(4)
MetaData      =arcpy.GetParameterAsText(5)
OutputFolder    =arcpy.GetParameterAsText(6)
OutputFileName =arcpy.GetParameterAsText(7)

#Tool input is opposite of function input
SaveRefl  = arcpy.GetParameter(8)

ReflOutFolder=arcpy.GetParameterAsText(9)

L7bands=[Band1path,Band3path,Band4path,Band5path]

arcpy.env.scratchWorkspace=OutputFolder

LTKCloudDetector.LTKCloudDetector(L7bands,pixelvalue,OutputFolder+'\\'+OutputFileName,MetaData,SaveRefl,ReflOutFolder)