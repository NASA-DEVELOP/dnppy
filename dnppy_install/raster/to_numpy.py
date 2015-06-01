# local imports

from is_rast import is_rast
from metadata import metadata

import arcpy
import numpy

def to_numpy(raster, numpy_datatype = None):

    """
    Wrapper for arcpy.RasterToNumpyArray with better metadata handling
    
     This is just a wraper for the RasterToNumPyArray function within arcpy, but it also
     extracts out all the spatial referencing information that will probably be needed
     to save the raster after desired manipulations have been performed.
     also see raster.from_numpy function in this module.

     inputs:
       Raster              Any raster supported by the arcpy.RasterToNumPyArray function
       numpy_datatype      must be a string equal to any of the types listed at the following
                           address [http://docs.scipy.org/doc/numpy/user/basics.types.html]
                           for example: 'uint8' or 'int32' or 'float32'
     outputs:
       numpy_rast          the numpy array version of the input raster
       Metadata            An object with the following attributes.
           .Xmin            the left edge
           .Ymin            the bottom edge
           .Xmax            the right edge
           .Ymax            the top edge
           .Xsize           the number of columns
           .Ysize           the number of rows
           .cellWidth       resolution in x direction
           .cellHeight      resolution in y direction
           .projection      the projection information to give the raster
           .NoData_Value    the numerical value which represents NoData in this raster

     Usage example:
       call this function with  " rast,Metadata = to_numpy(Raster) "
       perform numpy manipulations as you please
       then save the array with " raster.from_numpy(rast,Metadata,output)   "
    """

    # create a metadata object and assign attributes to it


    # read in the raster as an array
    if is_rast(raster):

        numpy_rast  = arcpy.RasterToNumPyArray(raster)
        ys, xs      = numpy_rast.shape
        meta        = metadata(raster, xs, ys)

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

    else:  
        raise Exception("Raster '{0}'does not exist".format(raster))

    return numpy_rast, meta

if __name__ == "__main__":

    path = "C:/test.tif"
    rast, meta = to_numpy(path)

    print meta.desc_pixelType
    print meta.pixel_type
    print meta.numpy_datatype