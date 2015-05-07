# local imports
from dnppy import core



def find_overlap(file_A, NoData_A, file_B, NoData_B, outpath, Quiet=False):
    """
     Finds overlaping area between two raster images.
     
     this function examines two images and outputs a raster raster.identifying pixels where both
     rasters have non-NoData values. Output raster has 1's where both images have data and
     0's where one or both images are missing data.

     inputs:
       file_A      the first file
       NoData_A    the NoData value of file A
       file_B      the second file
       NoData_B    the NoData value of file B
       outpath     the output filename for the desired output. must end in ".tif"
    """
    
    # import modules
    if check_module('numpy'): import numpy
    if not raster.is_rast(file_A) or not raster.is_rast(file_B):
        print '{raster.find_overlap} both inputs must be rasters!'

    # spatially match the rasters
    print '{raster.find_overlap} preparing input rasters!'
    raster.clip_and_snap(file_A,file_B,file_B,False,NoData_B)
    
    # load the rasters as numpy arays.
    a,metaA = to_numpy(file_A)
    b,metaB = to_numpy(file_B)

    Workmatrix = numpy.zeros((metaA.Ysize,metaA.Xsize))
    Workmatrix = Workmatrix.astype('uint8')

    a[(a >= NoData_A * 0.99999) & (a <= NoData_A * 1.00001)] = int(1)
    b[(b >= NoData_B * 0.99999) & (b <= NoData_B * 1.00001)] = int(1)

    print 'Finding overlaping pixels!'
    Workmatrix = a + b
    Workmatrix[Workmatrix <  2] = int(0)
    Workmatrix[Workmatrix >= 2] = int(1)
                
    print 'Saving overlap file!'       
    raster.from_numpy(Workmatrix, metaA, outpath,'0','uint8',False)
    Set_Null_Values(outpath,0,False)
    arcpy.RasterToPolygon_conversion(outpath, outpath[:-4]+'.shp', 'NO_SIMPLIFY')
    
    return metaA, metaB
