__author__ = ['jwely']

import gdal
import os

def NetCDF_layers_to_raster(ncpath, layer_indexs = None):
    """
    Extracts one or more layers from an NetCDF file and returns a dictionary with
    all the data available in the NetCDF layer for use in further format conversion
    to better supported formats.

    example:
    ncpath = filepath to any netcdf filetype (usualy ".nc")
    layer indexs = [1,2,3]

    the output dict will have keys :
                    ["MasterMetadata", "1", "2", "3"]

    where the "MasterMetadata" values very widely in format depending on
    data source, but should contain georeferencing information and the like.
    Each of the values for those integer keys will be a list of
    values that looks like this.

        [layer name descriptor, projection, geotransform, numpy_array]

    gdal has proven annoying to use, but this function should help you
    get started with programming support for any HDF datatype. Building
    proper geotransormation will require info in the MasterMetadata most
    likely, but there is not an established naming convention that can be
    applied to all datatypes.
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
