__author__ = 'jwely'
__all__ = ["_HDF_layer_to_tif"]

import gdal

def _HDF_layer_to_tif(gdal_dataset, outpath, cust_projection = None, cust_geotransform = None):
    """
    This function takes a gdal dataset object as returned from the
    "_extract_HDF_layer_data" function and writes it to tif with
    either the embedded projection and geotransform or custom ones

    :param gdal_dataset:            a gdal.Dataset object
    :param cust_projection:         a projection string, see datatype_library
    :param cust_geotransform:       a geotransform array, see datatype_library

    returns the local system filepath to output dataset.
    """

    # set up the projection
    if cust_projection is None:
        projection = gdal_dataset.GetProjection()
    else:
        projection = cust_projection

    # set up the geotransform
    if cust_geotransform is None:
        geotransform = gdal_dataset.GetGeoTransform()
    else:
        geotransform = cust_geotransform

    # set up the numpy array
    numpy_array = gdal_dataset.ReadAsArray()
    shape = numpy_array.shape

    if len(shape) == 2:
        xsize = shape[0]
        ysize = shape[1]
        numbands = 1
    elif len(shape) == 3:
        xsize = shape[1]
        ysize = shape[2]
        numbands = shape[0]
    else:
        raise Exception("cannot write 1 dimensional data to tif")

    # create the tiff
    gtiff = gdal.GetDriverByName("GTiff")
    outdata = gtiff.Create(outpath, xsize, ysize, 4)
    outdata.SetProjection(projection)
    outdata.SetGeoTransform(geotransform)

    for i in range(numbands):
        outdata.GetRasterBand(i + 1).WriteRaster(0,0, xsize, ysize)


    return outpath


