#-------------------------------------------------------------------------------
# Name:        VIIRS Vegetation Index Quality Flag Reader
# Purpose:      To read quality flag information that is stored bitwise
#
# Author:      Quinten Geddes - NASA DEVELOP Program
#
# Created:     14/11/2012

#-------------------------------------------------------------------------------
import numpy as np
import arcpy
from tempfile import TemporaryFile

InputRaster=arcpy.GetParameterAsText(0)
FlagType=arcpy.GetParameterAsText(1)
OutputFolder=arcpy.GetParameterAsText(2)
OutputFileName=arcpy.GetParameterAsText(3)
blockSize=500

if not ".tif" in OutputFileName:
    OutputFileName+=".tif"

FlagIndex  = {"Land_Water":"0:3","Cloud_Cover":"3:5","Thin_Cirrus":"7"}
Land_Water = {"101":1,"011":2,"010":3,"001":4,"000":5,"100":0,"111":0}
Cloud_Cover= {"11":1,"10":2,"01":3,"00":4}
Thin_Cirris= {"0":1,"1":2}
FlagInd=FlagIndex[FlagType]


def bitreader(integer):
    binary='{0:08b}'.format(integer)
    exec("NewFlag={0}[binary[{1}]]".format(FlagType,FlagInd))
    return NewFlag


vbitreader = np.vectorize(bitreader)
inputdata=arcpy.RasterToNumPyArray(InputRaster)

OutputArray=np.memmap(TemporaryFile(),"uint8","w+",shape=inputdata.shape)

descData=arcpy.Describe(InputRaster+"\\Band_1")
cellSize=descData.meanCellHeight
sr= descData.spatialReference
extent=descData.Extent
pnt=arcpy.Point(extent.XMin,extent.YMin)
rows=inputdata.shape[0]
cols=inputdata.shape[1]

for i in range(0, rows, blockSize):
    if (i + blockSize) < rows:
        numRows = blockSize
    else:
        numRows = rows - i
    for j in range(0, cols, blockSize):
        if (j + blockSize) < cols:
            numCols = blockSize
        else:
            numCols = cols - j
        OutputArray[i:i+numRows,j:j+numCols]=vbitreader(inputdata[i:i+numRows,j:j+numCols])
        arcpy.AddMessage("row {0} of {1}  column {2} of {3}"
                                .format((i/blockSize+1),int(rows/blockSize+1),
                                (j/blockSize+1),int(cols/blockSize+1)))

outraster = arcpy.NumPyArrayToRaster(OutputArray,pnt, cellSize,cellSize,0)
outraster.save(OutputFolder+"\\"+OutputFileName)