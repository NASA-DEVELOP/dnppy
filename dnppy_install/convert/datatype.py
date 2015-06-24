__author__ = ['jwely']

__all__ = ["datatype"]

class datatype():
    """
    simple class for dnppy supported download and convert
    NASA/NOAA/WeatherService/USGS data types
    """

    def __init__(self, name= None, projectionID = None, geotransform = None, projectionTXT = None):
        """
        Inputs:
            name            (str) the product name, (descriptive)
            projectionID    (str) projection ID according to prj files
                                downloaded from "spatialreference.org"
            geotransform    (list floats) geotransform array, lsit of 6
                                float values in the gdal ordering:
                                [top left x,
                                w-e pixel resolution,
                                0,
                                top left y,
                                0,
                                n-s pixel resolution (negative value)]
        """

        self.name = name
        self.projectionID = projectionID
        self.geotransform = geotransform
        self.projectionTXT = projectionTXT