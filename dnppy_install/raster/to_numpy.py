# local imports
from dnppy import core
from raster_enforcement import is_rast

import arcpy

def to_numpy(raster, num_type = False):

    """
    Wrapper for arcpy.RasterToNumpyArray with better metadata handling
    
     This is just a wraper for the RasterToNumPyArray function within arcpy, but it also
     extracts out all the spatial referencing information that will probably be needed
     to save the raster after desired manipulations have been performed.
     also see raster.from_numpy function in this module.

     inputs:
       Raster              Any raster suported by the arcpy.RasterToNumPyArray function
       num_type            must be a string equal to any of the types listed at the following
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
    class metadata:

        def __init__(self, raster, xs, ys):

            self.Xsize          = xs
            self.Ysize          = ys
            
            self.cellWidth      = arcpy.Describe(raster).meanCellWidth
            self.cellHeight     = arcpy.Describe(raster).meanCellHeight
            
            self.Xmin           = arcpy.Describe(raster).Extent.XMin
            self.Ymin           = arcpy.Describe(raster).Extent.YMin
            self.Xmax           = self.Xmin + (xs * self.cellWidth)
            self.Ymax           = self.Ymin + (ys * self.cellHeight)

            self.rectangle      = ' '.join([str(self.Xmin),
                                            str(self.Ymin),
                                            str(self.Xmax),
                                            str(self.Ymax)])
            
            self.projection     = arcpy.Describe(raster).spatialReference
            self.NoData_Value   = arcpy.Describe(raster).noDataValue
            return

    # read in the raster as an array
    if is_rast(raster):

        numpy_rast  = arcpy.RasterToNumPyArray(raster)
        ys, xs      = numpy_rast.shape
        meta        = metadata(raster, xs, ys)
        
        if num_type:
            numpy_rast = numpy_rast.astype(num_type)
            
    else:  
        print("Raster '{0}'does not exist".format(raster))

    return numpy_rast, meta
