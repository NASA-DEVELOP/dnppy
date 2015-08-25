__author__ = ['jwely']
__all__ = ["_gdal_dataset_to_tif"]

import gdal
import os
from _convert_dtype import *

def _gdal_dataset_to_tif(gdal_dataset, outpath, cust_projection = None,
                         cust_geotransform = None, force_custom = False,
                         nodata_value = None):
    """
    This function takes a gdal dataset object as returned from the
    "_extract_HDF_layer_data" OR "_extractNetCDF_layer_data functions
    and writes it to tif with either the embedded projection and
    geotransform or custom ones. This function should be wrapped in another
    function for a specific datatype.

    :param gdal_dataset:        A gdal.Dataset object
    :param outpath:             Output filepath for this dataset (tif)
    :param cust_projection:     A projection string, see datatype_library
    :param cust_geotransform:   A geotransform array, see datatype_library
    :param force_custom:        If True, forces the custom geotransform and
                                projections to be used even if valid
                                geotransforms and projections can be read
                                from the gdal.dataset. If False, custom
                                projections and geotransforms will be ignored
                                if valid variables can be pulled from the
                                gdal.dataset metadata.
    :param nodata_value:        The value to set to Nodata

    :return outpath:            The local system filepath to output dataset
    """

    # create output directory if it doesnt exist;
    if not os.path.exists(os.path.dirname(outpath)):
        os.mkdir(os.path.dirname(outpath))

    # set up the projection and geotransform
    if force_custom is True:
        projection = cust_projection
        geotransform = cust_geotransform
    else:

        gdal_projection = gdal_dataset.GetProjection()

        # only uses the custom projection if gdal metadata is bad
        if gdal_projection == "":
            projection = cust_projection
        else:
            projection = gdal_projection

        gdal_geotransform = gdal_dataset.GetGeoTransform()

        # only uses the custom geotransform if gdal geotransform is default (bad)
        if gdal_geotransform == (0.0, 1.0, 0.0, 0.0, 0.0, 1.0):
            geotransform = cust_geotransform
        else:
            geotransform = gdal_geotransform


    # print update
    print("using projection {0}".format(projection))
    print("using geotransform {0}".format(geotransform))

    # set up the numpy array
    numpy_array = gdal_dataset.ReadAsArray()
    shape = numpy_array.shape

    # determine its shape
    if len(shape) == 2:
        xsize = shape[1]
        ysize = shape[0]
        numbands = 1
    elif len(shape) == 3:
        xsize = shape[2]
        ysize = shape[1]
        numbands = shape[0]
    else:
        raise Exception("cannot write 1 dimensional data to tif")

    # create the tiff
    gtiff = gdal.GetDriverByName("GTiff")
    outdata = gtiff.Create(outpath, xsize, ysize, numbands, _convert_dtype(numpy_array.dtype))
    outdata.SetProjection(projection)
    outdata.SetGeoTransform(geotransform)

    # write each band
    for i in range(numbands):
        outraster = outdata.GetRasterBand(i+1)
        outraster.WriteArray(numpy_array, 0, 0)
        if nodata_value is not None:
            outraster.SetNoDataValue(nodata_value)
        outraster.FlushCache()

    return outpath


