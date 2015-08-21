__author__ = "jwely"
__all__ = ["from_numpy"]

import arcpy
arcpy.env.overwriteOutput = True
import numpy


def from_numpy(numpy_rast, metadata, outpath, NoData_Value = None):
    """
    Wrapper for arcpy.NumPyArrayToRaster function with better metadata handling

    this is just a wrapper for the NumPyArrayToRaster function within arcpy. It is used in
    conjunction with to_numpy to streamline reading image files in and out of numpy
    arrays. It also ensures that all spatial referencing and projection info is preserved
    between input and outputs of numpy manipulations.

    :param numpy_rast:      The numpy array version of the input raster
    :param metadata:        The variable exactly as output from "to_numpy"
    :param outpath:         Output filepath of the individual raster
    :param NoData_Value:    The no data value of the output raster

    :return outpath:        Same as input outpath, filepath to created file.

    Usage example
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
        mask = numpy_rast.mask
        data = numpy_rast.data
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

    return outpath
