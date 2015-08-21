__author__ = 'jwely'
__all__ = ["nongrid_data"]

from ll_to_utm import *
import numpy
import math
from scipy import interpolate
import datetime

class nongrid_data():
    """
    This class houses non-gridded datasets. Its methods can be used
    to build a gridded dataset from a non gridded dataset or point data.
    It takes three array/matrix like inputs, lat, lon, and data values.
    These matrix like inputs are then processed into 1d-arrays with two
    sorting schemes.

    The three arrays are represented as (lat_array, lon_array, data_array)

    where each array is of equal shape, and the value of each row
    corresponds to the values in the same row of the other arrays.
    these arrays are then converted to UTM coordinates and sorted
    by the utm_x coordinate.

    This sorting is done to optimize processing time when building
    a gridded dataset from what is effectively assumed to be point data.

    :param lat:          matrix of values representing latitude
    :param lon:          matrix of values representing longitude
    :param data:         matrix of values containing spatial data
    :param hemisphere:   either "N" or "S"
    """

    def __init__(self, lat, lon, data, hemisphere):
        """
        each lat, lon and data input can be numpy arrays of any
        size, as long as all three inputs are identical shapes.
        please use inputs of "degree"
        """

        print("Loading non-gridded dataset")
        self.hemisphere = hemisphere

        # one dimensionalizes the inputs
        self.lat = numpy.reshape(lat, -1)
        self.lon = numpy.reshape(lon, -1)
        self.data = numpy.reshape(data, -1)
        del lat, lon, data

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

        self.utm_zone = int(((self.mid_lon - 3 + 180) / 6) + 1)

        # converts lat lon points to utmx and utmy points
        print("Converting to UTM coordinates")
        utmx, utmy = ll_to_utm(self.lat, self.lon, self.utm_zone, self.hemisphere)

        # sorts the data (transformed into utm space) by utmx
        self.utmx = sorted(utmx)
        self.utmy = [y for (x,y) in sorted(zip(utmx, utmy))]
        self.data = [d for (x,d) in sorted(zip(utmx, self.data))]

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


    def _sample_by_location(self, utmx_matrix, utmy_matrix, resolution):
        """
        performs grid interpolation for a smaller subset of the total dataset.
        utmx_matrix and utmy_matrix are the two components of a meshgrid
        """

        # establish a sample distance
        samp_dist = abs(3 * resolution)

        # sort out data that is too far from input grid points
        print("\t Subsetting samples...")
        lowx = numpy.min(utmx_matrix) - samp_dist
        highx = numpy.max(utmx_matrix) + samp_dist

        lowy = numpy.min(utmy_matrix) - samp_dist
        highy = numpy.max(utmy_matrix) + samp_dist

        # remove low x points
        lowxmask = numpy.where(numpy.array(self.utmx) > lowx)
        subutmx = numpy.array(self.utmx)[lowxmask]
        subutmy = numpy.array(self.utmy)[lowxmask]
        subdata = numpy.array(self.data)[lowxmask]

        # remove high x points
        highxmask = numpy.where(subutmx < highx)
        subutmx = subutmx[highxmask]
        subutmy = subutmy[highxmask]
        subdata = subdata[highxmask]

        # remove low y points
        lowymask = numpy.where(subutmy > lowy)
        subutmx = subutmx[lowymask]
        subutmy = subutmy[lowymask]
        subdata = subdata[lowymask]

        # remove high y points
        #highymask = numpy.where(subutmy < highy)
        #subutmx = subutmx[highymask]
        #subutmy = subutmy[highymask]
        #subdata = subdata[highymask]

        print("\t Performing interpolation across {1} grid with {0} points...".format(
                                            len(subdata), utmx_matrix.shape))

        # create single point meshgrid and interpolate its value from nearby points
        points = (subutmx, subutmy)
        meshgrid = (utmx_matrix, utmy_matrix)

        if subdata.shape[0] != 0:
            location_data_value = interpolate.griddata(points, subdata, meshgrid, method = "cubic")
            return location_data_value
        else:
            return utmx_matrix * 0



    def sample_by_grid(self, resolution):
        """
        Grids a dataset to the desired resolution in a UTM projection. input
        resolution is the length of one square pixel on a side in meters.
        """

        # build range arrays
        x_range = list(numpy.arange(self.min_utmx, self.max_utmx, resolution))
        y_range = list(numpy.arange(self.min_utmy, self.max_utmy, resolution))

        # build meshgrid
        x_mesh, y_mesh = numpy.mgrid[self.min_utmx:self.max_utmx:complex(0,len(x_range)),
                                     self.min_utmy:self.max_utmy:complex(0,len(y_range))]

        outgrid = numpy.zeros((len(x_range), len(y_range)))

        # divide into equal number of slices and chunks
        num_slices = int(((len(x_range) * len(y_range)) / 800000) * (2 ** 0.5))
        slice_width = len(x_range) / float(num_slices)

        num_chunks = num_slices
        chunk_height = len(y_range) / float(num_chunks)

        # perform griding for one slice of the output grid at a time.
        print("Dividing dataset into {0} pieces and griding to a matrix of size {1}".format(
                                                        num_slices * num_chunks, outgrid.shape))

        for aslice in range(num_slices):
            for chunk in range(num_chunks):

                print("processing chunk {0},{1}".format(aslice + 1, chunk + 1))

                chunkrange = slice(int(chunk * chunk_height),int((chunk + 1) * chunk_height))
                slicerange = slice(int(aslice * slice_width),int((aslice + 1) * slice_width))
                slice_x_mesh = x_mesh[chunkrange, slicerange]
                slice_y_mesh = y_mesh[chunkrange, slicerange]

                outslice = self._sample_by_location(slice_x_mesh, slice_y_mesh, resolution)
                outgrid[chunkrange, slicerange] = outslice

        print("100%")

        return outgrid


# testing area
if __name__ == "__main__":
    from _extract_HDF_layer_data import *

    start = datetime.datetime.now()
    rasterpath = r"C:\Users\jwely\Desktop\troubleshooting\HDF_tests\GDNBO-SVDNB_npp_d20150626_t0132557_e0138361_b18964_c20150626174428799822_noaa_ops.h5"
    layer_data = _extract_HDF_layer_data(rasterpath, [2, 4, 19])

    ngd = nongrid_data(layer_data[2].ReadAsArray(),
                        layer_data[4].ReadAsArray(),
                        layer_data[19].ReadAsArray(), "S")

    ngd.sample_by_grid(resolution = 1000)
    end = datetime.datetime.now()
    print end - start