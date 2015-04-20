#-------------------------------------------------------------------------------
# Name:        VIIRS Grid Tool
# Purpose:     This tool grids and georeferences VIIRS HDF data files from
#              the NOAA CLASS website
# Author:     Quinten Geddes Quinten.A.Geddes@nasa.gov
#               NASA DEVELOP Program
# Created:     09/15/2012

#-------------------------------------------------------------------------------

import numpy
from scipy.interpolate import griddata
import h5py
import os
import arcpy
from math import pi, sin, cos, tan, sqrt

from tempfile import TemporaryFile
import time
from textwrap import dedent
arcpy.env.overwriteOutput = True

#Variables-------------------------------------------------------------Variables


HDFfile      = arcpy.GetParameterAsText(0) #HDF file including
ArrayName    = arcpy.GetParameterAsText(1) #Data array in the HDF file that the user wishes to interpolate
psize        = float(arcpy.GetParameterAsText(2)) #Desired pixel size in degrees or meters if Project to UTM is True
Extent       = arcpy.GetParameterAsText(3)
SampleMethodInput = arcpy.GetParameterAsText(4)
ProjectToUTM = arcpy.GetParameterAsText(5) #Whether or not the user wants to project to UTM coordinates
ZoneNumber   = arcpy.GetParameterAsText(6)
Hemisphere   = arcpy.GetParameterAsText(7)
OutputFolder = arcpy.GetParameterAsText(8) #Folder to which GeoTIFF files will be saved


blockSize=500   #Length of each side of the iterating block.
                #This is related to memory limits and processing speed
sdistance = blockSize*psize*.6  #Determines size of sample taken from original
                                #data used to interpolate output block
                                #of size blockSize x blockSize

#Variables-------------------------------------------------------------Variables



#Functions-------------------------------------------------------------Functions
def LLtoUTM(Lat, Long):
#This function converts lat/long to UTM coords.  Equations from USGS Bulletin 1532
#East Longitudes are positive, West longitudes are negative.
#North latitudes are positive, South latitudes are negative
#Lat and Long are in decimal degrees
#Function was written by Chuck Gantz- chuck.gantz@globalstar.com
#for WGS 84 ellipsoid
    _deg2rad = pi / 180.0
    _rad2deg = 180.0 / pi
    a = 6378137
    eccSquared = 0.00669438
    k0 = 0.9996

#Make sure the longitude is between -180.00 .. 179.9
    LongTemp = (Long+180)-int((Long+180)/360)*360-180 # -180.00 .. 179.9

    LatRad = Lat*_deg2rad
    LongRad = LongTemp*_deg2rad

    LongOrigin = (int(ZoneNumber) - 1)*6 - 180 + 3 #+3 puts origin in middle of zone
    LongOriginRad = LongOrigin * _deg2rad

    eccPrimeSquared = (eccSquared)/(1-eccSquared)
    N = a/sqrt(1-eccSquared*sin(LatRad)*sin(LatRad))
    T = tan(LatRad)*tan(LatRad)
    C = eccPrimeSquared*cos(LatRad)*cos(LatRad)
    A = cos(LatRad)*(LongRad-LongOriginRad)

    M = a*((1
            - eccSquared/4
            - 3*eccSquared*eccSquared/64
            - 5*eccSquared*eccSquared*eccSquared/256)*LatRad
           - (3*eccSquared/8
              + 3*eccSquared*eccSquared/32
              + 45*eccSquared*eccSquared*eccSquared/1024)*sin(2*LatRad)
           + (15*eccSquared*eccSquared/256 + 45*eccSquared*eccSquared*eccSquared/1024)*sin(4*LatRad)
           - (35*eccSquared*eccSquared*eccSquared/3072)*sin(6*LatRad))

    UTMEasting = (k0*N*(A+(1-T+C)*A*A*A/6
                        + (5-18*T+T*T+72*C-58*eccPrimeSquared)*A*A*A*A*A/120)
                  + 500000.0)

    UTMNorthing = (k0*(M+N*tan(LatRad)*(A*A/2+(5-T+9*C+4*C*C)*A*A*A*A/24
                                        + (61
                                           -58*T
                                           +T*T
                                           +600*C
                                           -330*eccPrimeSquared)*A*A*A*A*A*A/720)))

    if Hemisphere=="S":
        UTMNorthing = UTMNorthing + 10000000.0; #10000000 meter offset for southern hemisphere
    return (UTMNorthing,UTMEasting)

VLLtoUTM=numpy.vectorize(LLtoUTM)

#this function used to find points within sdistance of a point (y,x)
#returns a one dimensional array with the Y,X coordinates of qualifying points
#and the assosicated data values
def findpoints(y,x,Data, nodata):
    subLatInd= numpy.where(abs(numpy.array(DataGridY)-y)<sdistance)
    subLong= numpy.array(DataGridX)[subLatInd]
    blockInd = numpy.where(abs(subLong- x)<sdistance)
    blocklong = subLong[blockInd]
    blocklat  = numpy.array(DataGridY)[subLatInd][blockInd]
    blockz= numpy.array(Data)[subLatInd][blockInd]
    nodatamask=numpy.where(eval(nodata))
    return blocklat[nodatamask], blocklong[nodatamask], blockz[nodatamask]
#Functions-------------------------------------------------------------Functions

#Check to make sure pixel units are appropriate for output coordinate system
if ProjectToUTM=="true" and psize<10:
    msg="Pixel Size must be in meters for UTM Projection"
    arcpy.AddError(msg)
    raise arcpy.ExecuteError
if ProjectToUTM =="false" and psize>10:
    msg="Pixel Size must be in decimal degrees for WGS84 grid"
    arcpy.AddError(msg)
    raise arcpy.ExecuteError


#Navigating the HDF file and marking the Geolocation band
Date=HDFfile.split("pp_")[1][0:18]
f=h5py.File(HDFfile, 'r')
hdfind1=list(f)[0]
bands = list(f[hdfind1])
arcpy.AddMessage(bands)
BandNum=0
for band in bands:
    if u'GEO' in band:
        GeoBand=bands.pop(BandNum)
    BandNum+=1
    
#Designating the Latitude and Longitude arrays
Latitude=f["/{0}/{1}/Latitude".format(hdfind1,GeoBand)]
Longitude=f["/{0}/{1}/Longitude".format(hdfind1,GeoBand)]

if Extent.upper()!="DEFAULT":
    extents  = Extent.split(" ")
    DataExtent= tuple(map(float,extents))
    if any([DataExtent[3]<numpy.min(Latitude),
             DataExtent[1]> numpy.max(Latitude),
             DataExtent[2]<numpy.min(Longitude),
             DataExtent[0]> numpy.max(Longitude)]):
        arcpy.AddError("Swath does not cover specified extent")
        raise arcpy.ExecuteError
    if ProjectToUTM=="true":
        minlist=LLtoUTM(DataExtent[1],DataExtent[0])
        maxlist=LLtoUTM(DataExtent[3],DataExtent[2])
        DataExtent = (minlist[1],minlist[0],maxlist[1],maxlist[0])
#Project to UTM
#If UTM projection is required, the Latitude and Longitude arrays are converted to UTMy and UTMx
if ProjectToUTM == "true":
    arcpy.AddMessage("Projecting to UTM...")
    if int(ZoneNumber)<10:
        ZoneNumber="0{0}".format(str(int(ZoneNumber)))
    UTMy=numpy.memmap(TemporaryFile(),"int32","w+",shape=Latitude.shape)
    UTMx=numpy.memmap(TemporaryFile(),"int32","w+",shape=Latitude.shape)
    for i in range(0,Latitude.shape[0],blockSize):
        if (i + blockSize) < Latitude.shape[0]:
            numRows = blockSize
        else:
            numRows = Latitude.shape[0] - i
        for j in range(0,Latitude.shape[1],blockSize):
            if (j + blockSize) < Latitude.shape[1]:
                numCols = blockSize
            else:
                numCols = Latitude.shape[1] - j
            subUTMy,subUTMx=VLLtoUTM(Latitude[i:i+numRows,j:j+numCols],
                                     Longitude[i:i+numRows,j:j+numCols])
            UTMy[i:i+numRows,j:j+numCols]=subUTMy
            UTMx[i:i+numRows,j:j+numCols]=subUTMx
            arcpy.AddMessage( "converting Decimal Degrees to UTM row {0} of {1}  column {2} of {3}".
                             format((i/blockSize+1),int(Latitude.shape[0]/blockSize+1),
                             (j/blockSize+1),int(Latitude.shape[1]/blockSize+1)))
            subUTMy,subUTMx=0,0

    DataGridY = UTMy
    DataGridX = UTMx
    if Hemisphere =="N":
        ESPGh="6"
    elif Hemishpere=="S":
        ESPGh="7"
    ESPG = "32{0}{1}".format(ESPGh,ZoneNumber)

else:
    DataGridY = Latitude
    DataGridX = Longitude
    ESPG="4326"

#The four corners of the output array are determined
#DataExtent=( Min X, Min Y, Max X, Max Y )
if Extent.upper()=="DEFAULT":
    DataExtent=(numpy.min(DataGridX),numpy.min(DataGridY),
                numpy.max(DataGridX),numpy.max(DataGridY))



#determining number of rows and columns in the output array
rows= int(abs(DataExtent[3]-DataExtent[1])/psize)+1
cols= int(abs(DataExtent[2]-DataExtent[0])/psize)+1

#check to see if computer can run fast version or must run slow version

try: numpy.empty((rows,cols))
except:
    msg=dedent( """
                The output array is too large for this computer to process.
                Specify Extent variable in the tool to a smaller area in order
                to address this issue""")
    arcpy.AddError(msg)
    raise arcpy.ExecuteError
#calculating the Y and X values for each row and column respectively
#for the output grid
def makerowcoord(rown,maxval): return float(maxval - (rown*psize))
def makecolcoord(coln,minval): return float(minval + (coln*psize))
Vmakerowcoord=numpy.vectorize(makerowcoord)
Vmakecolcoord=numpy.vectorize(makecolcoord)
nrows,ncols=numpy.arange(rows),numpy.arange(cols)
rowcoord=Vmakerowcoord(nrows,DataExtent[3])
colcoord=Vmakecolcoord(ncols,DataExtent[0])
nrows,ncols=0,0

#setting the bottem left corner point for later georeferencing
pnt=arcpy.Point(colcoord[0]-(.5*psize),rowcoord[-1]-(.5*psize))

#Setting minimum pixels required by each interpolation method
sampledict={"linear":4,"cubic":9}
if SampleMethodInput=="nearest":
    SampleMethod="linear"
else:
    SampleMethod=SampleMethodInput
NeedForInterp=sampledict[SampleMethod]


#For each band an output array is created
#The output array is written by blocks of size "blockSize" by "blockSize".
#The extent of these blocks correspond output grid coordinates.
#Data points are retreived from the input HDF that have lat longs that
#fall within the extent of these blocks plus some slop.
#These collected data points are then used to interpolate and
#fill a block of the output array

for band in bands:
    arcpy.AddMessage("Writing Band {0}".format(str(band)))
    DataArray= f["/{0}/{1}/{2}".format(hdfind1,band,ArrayName)]
    DataType=numpy.dtype(DataArray).name
    OutputName="{0}_{1}_{2}".format(Date, str(band),ArrayName)
    OutputArray=numpy.memmap(TemporaryFile(),DataType,"w+",shape=(rows,cols))
    if "QF" in ArrayName:
        nodata="blockz>0"
    elif DataType=="uint16":
        nodata="blockz<65520"
    else:
        nodata="blockz>-999"
    interpcount=0

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
            centy= rowcoord[i+ (numRows/2)]
            centx= colcoord[j+ (numCols/2)]
            sampley, samplex,samplez= findpoints(centy, centx,DataArray,nodata)

            if len(sampley) <NeedForInterp:
                nopoints= "no points found in this block"

            else:
                datarows,datacols=numpy.mgrid[rowcoord[i]:rowcoord[i+numRows-1]:complex(0,numRows),
                                              colcoord[j]:colcoord[j+numCols-1]:complex(0,numCols)]
                outgrid = griddata((sampley,samplex),samplez,(datarows,datacols)
                                    ,method=SampleMethod,fill_value=0)

                if SampleMethodInput=="nearest":
                    outgrid2 = griddata((sampley,samplex),samplez,
                                        (datarows,datacols),method='nearest',fill_value=0)
                    outgrid2[outgrid==0]=0
                    outgrid=outgrid2
                OutputArray[i:i+numRows,j:j+numCols]=outgrid
                outgrid, outgrid2=0,0
                nopoints=""
                interpcount+=1
            arcpy.AddMessage("row {0} of {1}  column {2} of {3}  {4}"
                                .format((i/blockSize+1),int(rows/blockSize+1),
                                (j/blockSize+1),int(cols/blockSize+1),nopoints))
    if not interpcount:
        arcpy.AddError("No data found within the specified extent")
        raise arcpy.ExecuteError

    #Attempting to apply a scale to the dataset to attain the physical values for pixels
    try:
        ScaleArray=f["/{0}/{1}/{2}Factors".format(hdfind1,band,ArrayName)]
        Scale, Constant= ScaleArray[0],ScaleArray[1]
        arcpy.AddMessage("Pixel Unit Scale Factor Applied")
    except:
        try:
            ScaleArray= f["/{0}/{1}/{2}_Factors".format(hdfind1,band,ArrayName)]
            Scale, Constant= ScaleArray[0],ScaleArray[1]
            arcpy.AddMessage("Pixel Unit Scale Factor Applied")
        except:
            Scale,Constant=1.,0.
            arcpy.AddMessage("Pixel Unit Scale Factor NOT Applied")
    OutputArray=((OutputArray>0)*OutputArray*Scale)+Constant

    bandraster = arcpy.NumPyArrayToRaster(OutputArray,pnt, psize,psize,"#")
    arcpy.DefineProjection_management(bandraster, ESPG)
    bandraster.save("{0}\\{1}.tif".format(OutputFolder,OutputName))
    bandraster=0
    del OutputArray
#Finish by closing files and deleting temporary storage
f.close()
if ProjectToUTM ==True:
    del UTMy,UTMx

del rowcoord,colcoord
