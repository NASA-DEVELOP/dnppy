# local imports
import arcpy
import numpy




def from_numpy(numpy_rast, metadata, outpath, NoData_Value = False, numpy_datatype = False):
    """
    Wrapper for arcpy.NumPyArrayToRaster function with better metadata handling
    
     this is just a wraper for the NumPyArrayToRaster function within arcpy. It is used in
     conjunction with to_numpy to streamline reading image files in and out of numpy
     arrays. It also ensures that all spatial referencing and projection info is preserved
     between input and outputs of numpy manipulations.

     inputs:
       numpy_rast          the numpy array version of the input raster
       metadata            The variable exactly as output from "to_numpy"
       outpath             output filepath of the individual raster
       NoData_Value        the no data value of the output raster
       numpy_datatype      must be a string equal to any of the types listed at the following
                           address [http://docs.scipy.org/doc/numpy/user/basics.types.html]
                           for example: 'uint8' or 'int32' or 'float32'

     Usage example:
       call to_numpy with  "rast,metadata = to_numpy(Raster)"
       perform numpy manipulations as you please
       then save the array with "raster.from_numpy(rast, metadata, output)"
    """

    if numpy_datatype:
        numpy_rast = numpy_rast.astype(numpy_datatype)

    if not NoData_Value:
        NoData_Value = metadata.NoData_Value
            
    llcorner = arcpy.Point(metadata.Xmin, metadata.Ymin)
    
    # save the output.
    if isinstance(numpy_rast, numpy.ma.core.MaskedArray):
        mask = numpy.ma.getmask(numpy_rast)
        data = numpy.ma.getdata(numpy_rast)
        data[mask] = metadata.NoData_Value

        OUT = arcpy.NumPyArrayToRaster(data, llcorner, metadata.cellWidth ,metadata.cellHeight)
        OUT.save(outpath)

    elif isinstance(numpy_rast, numpy.ndarray):
        OUT = arcpy.NumPyArrayToRaster(numpy_rast, llcorner, metadata.cellWidth ,metadata.cellHeight)
        OUT.save(outpath)

    # define its projection
    try:
        arcpy.DefineProjection_management(outpath, metadata.projection)
    except:
        pass

    # reset the NoData_Values
    try:
        arcpy.SetRasterProperties_management(outpath, data_type="#", statistics="#",
                    stats_file="#", nodata="1 " + str(NoData_Value))
    except:
        pass
    
    # do statistics and pyramids
    arcpy.CalculateStatistics_management(outpath)
    arcpy.BuildPyramids_management(outpath)
    
    print("Saved output file as {0}".format(outpath))

    return
