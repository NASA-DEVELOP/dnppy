__author__ = ['jwely']

from dnppy import core
import gdal
import os
import numpy
import osr

def NetCDF_layers_to_raster(ncpath, layer_indexs = None,
                            cust_projection = None, cust_geotransform = None):
    """
    Extracts one or more layers from an HDF file and saves them as tifs

    """

    head, tail = os.path.split(ncpath)
    outraster_names = []

    # open the netcdf dataset
    print("opening {0}".format(ncpath))
    nc_dataset = gdal.Open(ncpath)
    print nc_dataset

    subdataset = nc_dataset.GetRasterBand(1)
    projection = nc_dataset.GetProjection()
    geotransform = nc_dataset.GetGeoTransform()

    print projection
    print geotransform



    return outraster_names


def _convert_dtype(numpy_dtype_string):
    """
    converts numpy dtype to a gdal data type object
    """

    ndt = str(numpy_dtype_string)

    if ndt == "float64":
        return gdal.GDT_Float64

    elif ndt == "float32":
        return gdal.GDT_Float32

    elif ndt == "uint32":
        return gdal.GDT_UInt32

    elif "unit" in ndt:
        return gdal.GDT_UInt16

    elif ndt == "int32":
        return gdal.GDT_Int32

    else:
        return gdal.GDT_Int16


if __name__ == "__main__":
    # try some MPE netcdf files
    ncfile = r"C:\Users\jwely\Desktop\troubleshooting\MPE\nws_precip_conus_20150101.nc"
    NetCDF_layers_to_raster(ncfile)
