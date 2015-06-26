__author__ = ['jwely']

import gdal
import os

def NetCDF_layers_to_raster(ncpath, layer_indexs = None):
    """
    Extracts one or more layers from an NetCDF file and returns a dictionary with
    all the data available in the NetCDF layer for use in further format conversion
    to better supported formats.

    example:
    ncpath = filepath to an NetCDF file. (any HDF 4 or 5 datatype)
    layer indexs = [1,2,3]

    the output dict will have keys :
                    ["MasterMetadata", "1", "2", "3"]

    where the "MasterMetadata" values very widely in format depending on
    data source, but might contain georeferencing information and the like.
    Each of the values for those integer keys will simply be a gdal.dataset
    object.

    this function is the first step in the chain for turning HDF data into
    geotiff. the next step is to build an established datatype

    :param ncpath          filepath to any NetCDF formated file
    :param layer_indexs     list of integer index values for layers to extract
    """

    # output dict
    out_info = {}
    layer_names = []

    # opening the netcdf dataset
    nc_dataset = gdal.Open(ncpath)


    band         = nc_dataset.GetRasterBand(1)
    projection   = nc_dataset.GetProjection()
    geotransform = nc_dataset.GetGeoTransform()
    numpy_array  = band.ReadAsArray()

    dict = band.GetMetadata_Dict()
    for key in dict:
        print key," = ", dict[key]

    print projection
    print geotransform
    print numpy_array.shape


    return

if __name__ == "__main__":
    # try some MPE netcdf files
    ncfile = r"C:\Users\jwely\Desktop\troubleshooting\MPE\nws_precip_conus_20150101.nc"
    NetCDF_layers_to_raster(ncfile)
