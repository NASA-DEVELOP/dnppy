__author__ = 'jwely'
__all__ = ["metadata"]

import arcpy

class metadata():
    """
    A dnppy standard class for storing raster metadata in a way
    that allows arcpy.Raster() object style handling while using numpy
    arrays for data manipulation.

    :param raster:  filepath to raster existing on disk

    typical attributes include the following

    =============== ===========================================================
    Attribute       Description
    =============== ===========================================================
    Xsize           x dimension of raster
    Ysize           y dimension of raster
    Zsize           z dimension of raster (number of bands)
    Xmin            lowest x coordinate
    Ymin            lowest y coordinate
    Xmax            largest x coordiante
    Ymax            largest y coordinate
    cellWidth       horizontal pixel resolution
    cellHeight      vertical pixel resolution
    desc_pixelType  pixel type description returned by arcpy.Describe()
    pixel_type      pixel type description that is actually accepted
                    as input by other ``arcpy`` functions. (ex "32_BIT_FLOAT")
    numpy_datatype  numpy accepted pixel type string. (ex "float32")
    projection      the projection of the raster (long string)
    NoData_Value    the value representing no data
    =============== ===========================================================
    """

    def __init__(self, raster = None, xs = None, ys = None, zs = None):

        # sets geometry information
        if zs is None:
            zs = 1

        self.Xsize  = xs
        self.Ysize  = ys
        self.Zsize  = zs

        # if a filepath to existing raster is input, build metadata from it
        if raster is not None:
            self._get_atts_from_raster(raster)
        return


    def _get_atts_from_raster(self, raster):
        """
        sets all required metadata attributes from an existing raster image
        """

        desc = arcpy.Describe(raster)
        self.cellWidth      = desc.meanCellWidth
        self.cellHeight     = desc.meanCellHeight
        self.Xmin           = desc.Extent.XMin
        self.Ymin           = desc.Extent.YMin
        self.desc_pixelType = desc.pixelType
        self.pixel_type     = self._get_pixel_type
        self.numpy_datatype = self._get_numpy_datatype

        self.Xmax           = self.Xmin + (self.Xsize * self.cellWidth)
        self.Ymax           = self.Ymin + (self.Ysize * self.cellHeight)

        self.rectangle      = ' '.join([str(self.Xmin),
                                        str(self.Ymin),
                                        str(self.Xmax),
                                        str(self.Ymax)])

        self.projection     = arcpy.Describe(raster).spatialReference
        self.NoData_Value   = arcpy.Describe(raster).noDataValue
        return


    @property
    def _get_pixel_type(self):
        """
        gets a "pixel_type" attribute that matches format of arcpy function
        inputs for manual datatype manipulations from the confusingly encoded
        "pixelType" variable associated with arcpy.Describe()

        as of arcpy 10.2.2
        """

        pt = self.desc_pixelType

        # determine bit depth
        if "64" in pt:
            return "64_BIT"
        elif "32" in pt:
            bits = 32
        elif "16" in pt:
            bits = 16
        elif "8" in pt:
            bits = 8
        elif "4" in pt:
            return "4_BIT"
        elif "2" in pt:
            return "2_BIT"
        elif "1" in pt:
            return "1_BIT"
        else:
            bits = "0"

        # determine numerical type
        if "U" in pt:
            type = "UNSIGNED"
        elif "S" in pt:
            type = "SIGNED"
        elif "F" in pt:
            type = "FLOAT"
        else:
            type = "UNKNOWN"

        pixel_type = "{0}_BIT_{1}".format(bits, type)

        return pixel_type


    @property
    def _get_numpy_datatype(self):
        """
        further translates the arcpy pixel_type format preferences into something
        that matches the format for numpy "datatype" arguments

        note that numpy does not do 4 and 2 bit integers
        """

        pt = self.desc_pixelType

        # determine bit depth
        if "128" in pt:
            bits = 128
        elif "64" in pt:
            bits = 64
        elif "32" in pt:
            bits = 32
        elif "16" in pt:
            bits = 16
        elif "8" in pt:
            bits = 8
        elif "4" in pt:
            bits = 8            # 4 bit not supported
        elif "2" in pt:
            bits = 8            # 2 bit not supported
        elif "1" in pt:
            return "bool_"      # only as bools
        else:
            bits = "0"

        # determine numerical type
        if "U" in pt:
            type = "uint"
        elif "S" in pt:
            type = "int"
        elif "F" in pt:
            type = "float"
        else:
            type = "UNKNOWN"

        numpy_datatype = "".join([type, str(bits)])

        return numpy_datatype




