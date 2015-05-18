# local imports

from to_numpy import to_numpy
from from_numpy import from_numpy
from is_rast import is_rast
from clip_and_snap import clip_and_snap
from null_define import null_define

import numpy
import arcpy


def raster_overlap(file_A, file_B, outpath, NoData_A = None, NoData_B = None):
    """
    Finds overlaping area between two raster images.
     
    this function examines two images and outputs a raster raster.identifying pixels where both
    rasters have non-NoData values. Output raster has 1's where both images have data and
    0's where one or both images are missing data.

    inputs:
        file_A      the first file
        file_B      the second file
        outpath     the output filename for the desired output. must end in ".tif"
        NoData_A    the NoData value of file A
        NoData_B    the NoData value of file B
    """
    
    if not is_rast(file_A) or not is_rast(file_B):
        print '{raster.raster_overlap} both inputs must be rasters!'


    # load the rasters as numpy arays.
    a, metaA = to_numpy(file_A)
    b, metaB = to_numpy(file_B)

    # set no_datas
    if NoData_A == None:
        NoData_A == metaA.NoData_Value
    if NoData_B == None:
        NoData_B == metaB.NoData_Value

    # spatially match the rasters
    print('preparing input rasters!')
    clip_and_snap(file_A, file_B, file_B, False, NoData_B)

    # reload the rasters as numpy arrays now that spatial matching is done
    a, metaA = to_numpy(file_A)
    b, metaB = to_numpy(file_B)

    # create work matrix and find the overlap
    Workmatrix = numpy.zeros((metaA.Ysize, metaA.Xsize))
    Workmatrix = Workmatrix.astype('uint8')

    a[(a >= NoData_A * 0.99999) & (a <= NoData_A * 1.00001)] = int(1)
    b[(b >= NoData_B * 0.99999) & (b <= NoData_B * 1.00001)] = int(1)

    print('Finding overlaping pixels!')
    Workmatrix = a + b
    Workmatrix[Workmatrix <  2] = int(0)
    Workmatrix[Workmatrix >= 2] = int(1)
                
    print('Saving overlap file!') 
    from_numpy(Workmatrix, metaA, outpath,'0','uint8')
    null_define(outpath, 0)
    arcpy.RasterToPolygon_conversion(outpath, outpath[:-4]+'.shp', 'NO_SIMPLIFY')
    
    return metaA, metaB
