# local imports
import arcpy
import numpy


def from_numpy(numpy_rast, metadata, outpath, NoData_Value = None):
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

     Usage example:
       call to_numpy with  "rast,metadata = to_numpy(Raster)"
       perform numpy manipulations as you please
       then save the array with "raster.from_numpy(rast, metadata, output)"
    """

    numpy_rast = numpy_rast.astype(metadata.numpy_datatype)

    if NoData_Value is None:
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
        Warning("Unable to define the projection on {0}".format(outpath))

    # reset the NoData_Values
    try:
        arcpy.SetRasterProperties_management(
            outpath,
            data_type = "#",
            statistics = "#",
            stats_file = "#",
            nodata = "1 " + str(NoData_Value))

    except:
        Warning("Unable to establish NoData profile on {0}".format(outpath))
    
    # calculate statistics and pyramids
    arcpy.CalculateStatistics_management(outpath)
    arcpy.BuildPyramids_management(outpath)
    
    print("Saved output file as {0}".format(outpath))

    return
