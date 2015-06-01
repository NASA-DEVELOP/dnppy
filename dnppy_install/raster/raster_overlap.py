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
     
    this function examines two images and outputs a raster identifying pixels where both
    rasters have non-NoData values. Output raster has 1's where both images have data and
    0's where one or both images are missing data.

    inputs:
        file_A      the first file
        file_B      the second file
        outpath     the output filename for the desired output. must end in ".tif"
        NoData_A    the NoData value of file A
        NoData_B    the NoData value of file B

    This function automatically invokes
        clip_and_snap
        null_define
    """
    
    if not is_rast(file_A) or not is_rast(file_B):
        raise Exception(' both inputs must be rasters!')


    # load the rasters as numpy arays.
    a, metaA = to_numpy(file_A)
    b, metaB = to_numpy(file_B)

    # set no_datas
    if NoData_A is None:
        NoData_A = metaA.NoData_Value
    if NoData_B is None:
        NoData_B = metaB.NoData_Value

    # spatially match the rasters
    print('preparing input rasters!')
    clip_and_snap(file_A, file_B, outpath.replace(".shp",".tif"), NoData_B)

    # reload the rasters as numpy arrays now that spatial matching is done
    a, metaA = to_numpy(file_A)
    b, metaB = to_numpy(file_B)

    # create work matrix and find the overlap
    print('Finding overlaping pixels!')
    Workmatrix = a.mask + b.mask
    Workmatrix = Workmatrix.astype('uint8')
    Workmatrix[Workmatrix == 1] = 2
                
    print('Saving overlap file!')
    metaA.numpy_datatype = 'uint8'
    from_numpy(Workmatrix, metaA, outpath.replace(".shp",".tif"), NoData_Value = 2)
    arcpy.RasterToPolygon_conversion(outpath.replace(".shp",".tif"),
                                     outpath.replace(".tif",".shp"),
                                     'NO_SIMPLIFY')
    
    return metaA, metaB
