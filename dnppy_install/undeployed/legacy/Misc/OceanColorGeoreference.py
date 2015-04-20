#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      qgeddes
#
# Created:     11/06/2013
# Copyright:   (c) qgeddes 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy
import numpy

InputRaster=  arcpy.GetParameterAsText(0)
OutputFolder= arcpy.GetParameterAsText(1)
OutputName= arcpy.GetParameterAsText(2)
#---------------------------------------
#INPUTS
#InputRaster="C:\\Users\\qgeddes\\Downloads\\temptrash\\A2011008.L3m_DAY_CHL_chlor_a_4km.hdf"
#OutputRaster="C:\\Users\\qgeddes\\Downloads\\temptrash\\test7.tif"
#------------------------------------------------


OutputRaster=OutputFolder+"\\"+OutputName

proj="""GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]"""
pnt= arcpy.Point(-180,-90)

a=arcpy.RasterToNumPyArray(InputRaster)
xsize=360./a.shape[1]
ysize=180./a.shape[0]
newRaster=arcpy.NumPyArrayToRaster(a,pnt,xsize,ysize)


newRaster.save(OutputRaster)

arcpy.DefineProjection_management(OutputRaster,proj)

