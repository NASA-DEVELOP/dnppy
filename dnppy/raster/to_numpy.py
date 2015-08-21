__author__ = "jwely"
__all__ = ["to_numpy"]


from is_rast import is_rast
from metadata import metadata

import os
import arcpy
import numpy

def to_numpy(raster, numpy_datatype = None):

    """
    Wrapper for arcpy.RasterToNumpyArray with better metadata handling

    This is just a wraper for the RasterToNumPyArray function within arcpy, but it also
    extracts out all the spatial referencing information that will probably be needed
    to save the raster after desired manipulations have been performed.
    also see raster.from_numpy function in this module.

    :param raster:         Any raster supported by the arcpy.RasterToNumPyArray function
    :param numpy_datatype: must be a string equal to any of the types listed at the following
                           address [http://docs.scipy.org/doc/numpy/user/basics.types.html]
                           for example: 'uint8' or 'int32' or 'float32'

    :return numpy_rast:   the numpy array version of the input raster
    :return Metadata:     a metadata object. see ``raster.metadata``
    """

    # perform some checks to convert to supported data format
    if not is_rast(raster):
        try:
            print("Raster '{0}' may not be supported, converting to tif".format(raster))
            tifraster = raster + ".tif"
            if not os.path.exists(raster + ".tif"):
                arcpy.CompositeBands_management(raster, tifraster)

            raster = tifraster
        except:
            raise Exception("Raster type could not be recognized")


    # read in the raster as a numpy array
    numpy_rast  = arcpy.RasterToNumPyArray(raster)

    # build metadata for multi band raster
    if len(numpy_rast.shape) == 3:
        zs, ys, xs  = numpy_rast.shape
        meta = []

        for i in range(zs):
            bandpath = raster + "\\Band_{0}".format(i+1)
            meta.append(metadata(bandpath, xs, ys))

        if numpy_datatype is None:
            numpy_datatype = meta[0].numpy_datatype


    # build metadata for single band raster
    else:
        ys, xs  = numpy_rast.shape
        meta  = metadata(raster, xs, ys)

        if numpy_datatype is None:
            numpy_datatype = meta.numpy_datatype

    numpy_rast = numpy_rast.astype(numpy_datatype)

    # mask NoData values from the array
    if 'float' in numpy_datatype:
        numpy_rast[numpy_rast == meta.NoData_Value] = numpy.nan
        numpy_rast = numpy.ma.masked_array(numpy_rast, numpy.isnan(numpy_rast),
                                           dtype = numpy_datatype)

    elif 'int' in numpy_datatype: # (numpy.nan not supported by ints)
        mask = numpy.zeros(numpy_rast.shape)
        mask[numpy_rast != meta.NoData_Value] = False    # do not mask
        mask[numpy_rast == meta.NoData_Value] = True     # mask
        numpy_rast = numpy.ma.masked_array(numpy_rast, mask,
                                           dtype = numpy_datatype)

    return numpy_rast, meta


# testing area
if __name__ == "__main__":

    path = r"C:\Users\jwely\Desktop\troubleshooting\test\MOD10A1\frac_snow\MYD09GQ.A2015160.h18v02.005.2015162071112_000.tif"

    rast, meta = to_numpy(path)