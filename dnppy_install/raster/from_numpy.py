# local imports
from dnppy import core

import arcpy




def from_numpy(numpy_rast, Metadata, outpath, NoData_Value = False, num_type = False):
    """
    Wrapper for arcpy.NumPyArrayToRaster function with better metadata handling
    
     this is just a wraper for the NumPyArrayToRaster function within arcpy. It is used in
     conjunction with to_numpy to streamline reading image files in and out of numpy
     arrays. It also ensures that all spatial referencing and projection info is preserved
     between input and outputs of numpy manipulations.

     inputs:
       numpy_rast          the numpy array version of the input raster
       Metadata            The variable exactly as output from "to_numpy"
       outpath             output filepath of the individual raster
       NoData_Value        the no data value of the output raster
       num_type            must be a string equal to any of the types listed at the following
                           address [http://docs.scipy.org/doc/numpy/user/basics.types.html]
                           for example: 'uint8' or 'int32' or 'float32'

     Usage example:
       call to_numpy with  "rast,Metadata = to_numpy(Raster)"
       perform numpy manipulations as you please
       then save the array with "raster.from_numpy(rast, Metadata, output)"
    """

    if num_type:
        numpy_rast = numpy_rast.astype(num_type)

    if not NoData_Value:
        NoData_Value = Metadata.NoData_Value
            
    llcorner = arcpy.Point(Metadata.Xmin, Metadata.Ymin)
    
    # save the output.
    OUT = arcpy.NumPyArrayToRaster(numpy_rast, llcorner, Metadata.cellWidth ,Metadata.cellHeight)
    OUT.save(outpath)

    # define its projection
    try:
        arcpy.DefineProjection_management(outpath, Metadata.projection)
    except:
        pass

    # reset the NoData_Values
    try:
        arcpy.SetRasterProperties_management(outpath, data_type="#", nodata = "1 " + str(NoData_Value))
    except:
        pass
    
    # do statistics and pyramids
    arcpy.CalculateStatistics_management(outpath)
    arcpy.BuildPyramids_management(outpath)
    
    print("Saved output file as {0}".format(outpath))

    return
