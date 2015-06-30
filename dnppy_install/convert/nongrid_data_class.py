__author__ = 'jwely'
__all__ = ["nongrid_data"]

from LLtoUTM import *
import numpy
import math
from scipy import interpolate

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
    Please note ALL angular data is internally stored in radians, even
    though lat/lon inputs are likely to be in degrees!
    """

    def __init__(self, lat, lon, data):
        """
        each lat, lon and data input can be numpy arrays of any
        size, as long as all three inputs are identical shapes.
        please use inputs of "degree"

        :param lat:     matrix of values representing latitude
        :param lon:     matrix of values representing longitude
        :param data:    matrix of values containing spatial data
        """

        # one dimensionalizes the inputs and converts to radians
        self.lat = numpy.reshape(lat, -1)
        self.lon = numpy.reshape(lon, -1)
        self.data = numpy.reshape(data, -1)

        if not (len(self.lat) == len(self.lon) == len(self.data)):
            raise Exception("inputs are not the same dimensions!")

        # get bounding box info
        self.min_lat = min(self.lat)
        self.max_lat = max(self.lat)
        self.min_lon = min(self.lon)
        self.max_lon = max(self.lon)

        # determine the UTM zone of the center point of this data.
        self.mid_lon = self.max_lon - self.min_lon / 2
        self.mid_lat = self.max_lat - self.min_lat / 2

        self.utm_zone   = int(((self.mid_lon - 3 + 180) / 6) + 1)
        if self.mid_lat < 0:
            self.hemisphere = "S"
        else:
            self.hemisphere = "N"

        # converts lat lon points to utmx and utmy points
        self.utmx, self.utmy = LLtoUTM(self.lat, self.lon, self.utm_zone, self.hemisphere)

        # find min and maximum utm coordinates
        self.min_utmx = numpy.min(self.utmx)
        self.min_utmy = numpy.min(self.utmy)
        self.max_utmx = numpy.max(self.utmx)
        self.max_utmy = numpy.max(self.utmy)

        # print a summary
        print("location: UTM zone {0}{1}".format(self.utm_zone, self.hemisphere))
        print("LL UTM coordinates: {0} , {1}".format(self.min_utmx, self.min_utmy))
        print("UR UTM coordinates: {0} , {1}".format(self.max_utmx, self.max_utmy))


    @staticmethod
    def distance_x_y(x0, y0, x1, y1):
        """
        computes the approx distance between two utmx, utmy locations
        """

        dist = (((x0 - x1) **2) + ((y0 - y1)**2)) ** 0.5
        return dist


    @staticmethod
    def distance_lat_lon(lat0, lon0, lat1, lon1):
        """
        computes the distance between two lat/lon coordinates in meters
        using the Haversine formula.
        """

        # radius of earth in meters
        R = 6371000

        # convert degree values to radians.
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


    def _sample_by_location(self, utmx0, utmy0, resolution):
        """ performs grid interpolation for a single location """

        # find points in the dataset that are near the input x,y

        #



        subutmx, subutmy, subdata = [(x, y, z) if self.distance_x_y(utmx0, utmy0, x, y) < (2 * resolution) else (None, None, None) \
                                   for x,y,z in zip(self.utmx, self.utmy, self.data)]

        # create single point meshgrid and interpolate its value from nearby points
        points = (subutmx, subutmy)
        meshgrid = numpy.mgrid(utmx0, utmy0)
        location_data_value = interpolate.griddata(points, subdata, meshgrid, method = "cubic")

        return location_data_value


    def sample_by_grid(self, resolution):
        """
        Grids a dataset to the desired resolution in a UTM projection. input
        resolution is the length of one square pixel on a side in meters.
        """

        xrange = numpy.arange(self.min_utmx, self.max_utmx, resolution)
        yrange = numpy.arange(self.min_utmy, self.max_utmy, resolution)

        outgrid = numpy.zeros((len(xrange), len(yrange)))
        print outgrid.shape
        print("griding dataset, this may take a while")
        for xi, x in enumerate(xrange):
            for yi, y in enumerate(yrange):
                outgrid[x,y] = self._sample_by_location(x, y, resolution)

        return outgrid


# testing area
if __name__ == "__main__":
    from _extract_HDF_layer_data import *

    rasterpath = r"C:\Users\jwely\Desktop\troubleshooting\HDF_tests\GDNBO-SVDNB_npp_d20150626_t0132557_e0138361_b18964_c20150626174428799822_noaa_ops.h5"
    layer_data = _extract_HDF_layer_data(rasterpath, [2, 4, 19])

    ngd = nongrid_data(layer_data[2].ReadAsArray(),
                        layer_data[4].ReadAsArray(),
                        layer_data[19].ReadAsArray())

    ngd.sample_by_grid(resolution = 10000)