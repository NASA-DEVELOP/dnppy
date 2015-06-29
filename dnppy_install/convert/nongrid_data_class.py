__author__ = 'jwely'
__all__ = ["nongrid_data"]

import numpy
import math

class nongrid_data():
    """
    This class houses non-gridded datasets. Its methods can be used
    to build a gridded dataset from a non gridded dataset or point data.
    It takes three array/matrix like inputs, lat, lon, and data values.
    These matrix like inputs are then processed into 1d-arrays with two
    sorting schemes.

    The three arrays are represented as:
        lat_array, lon_array, data_array

    where each array is of equal length, and the value of each row
    corresponds to the values in the same row of the other arrays.
    these arrays are then represented twice, sorted by lat, then lon.

    This sorting is done to optimize processing time when building
    a gridded dataset from what is effectively assumed to be point data.
    memory consumption is doubled, but processing time is decreased
    by a factor of order 10.
    """

    def __init__(self, lat, lon, data, unit = "Degree"):
        """
        each lat, lon and data input can be numpy arrays of any
        size, as long as all three inputs are identical shapes.
        If lat/lon are in units of radians, use "unit" input

        :param lat:     matrix of values representing latitude
        :param lon:     matrix of values representing longitude
        :param data:    matrix of values containing spatial data
        :param unit:    either "Degree" or "Radian"
        """

        # one dimensionalizes the inputs
        self.unit = unit
        self.lat = numpy.reshape(lat, -1)
        self.lon = numpy.reshape(lon, -1)
        self.data = numpy.reshape(data, -1)

        if not (len(self.lat) == len(self.lon) == len(self.data)):
            raise Exception("inputs are not the same dimensions!")

        # build sorted arrays of lat,lon,data inputs
        self.lat_sortlat  = sorted(self.lat)
        self.lon_sortlat  = [x for (y, x) in sorted(zip(self.lat, self.lon))]
        self.data_sortlat = [x for (y, x) in sorted(zip(self.lat, self.data))]
        self.lat_sortlon  = [x for (y, x) in sorted(zip(self.lon, self.lat))]
        self.lon_sortlon  = sorted(self.lon)
        self.data_sortlat = [x for (y, x) in sorted(zip(self.lon, self.data))]

        # delete original input arrays to save memory
        del self.lat, self.lon, self.data

        # get bounding box info
        self.min_lat = min(self.lat_sortlat)
        self.max_lat = max(self.lat_sortlat)
        self.min_lon = min(self.lon_sortlon)
        self.max_lon = max(self.lon_sortlon)

        # gives simple estimation of data resolution
        self.mean_lat_space = (self.max_lat - self.min_lat) / len(lat)
        self.mean_lon_space = (self.max_lon - self.min_lon) / len(lon)

        print self.mean_lat_space
        print self.mean_lon_space


    def distance(self, lat0, lon0, lat1, lon1):
        """
        computes the distance between two lat/lon coordinates in meters
        using the haversine formula
        """
        R = 6371000

        # convert to radians if needed
        if self.unit == "Degree":
            lat0 = math.radians(lat0)
            lon0 = math.radians(lon0)
            lat1 = math.radians(lat1)
            lon1 = math.radians(lon1)

        del_lat = lat1 - lat0
        del_lon = lon1 - lon0

        a = (math.sin(del_lat / 2) ** 2) + \
            (math.cos(lat0) * math.cos(lat1)) * (math.sin(del_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - 1))

        dist = R * c

        return dist


    def sample_by_grid(self, resolution, min_points):
        """
        Input a resolution (in degrees), and
        """

        pass

