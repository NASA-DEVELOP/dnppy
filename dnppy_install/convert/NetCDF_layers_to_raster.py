__author__ = ['jwely']

from dnppy import core
import gdal
import os
import geotransforms
import projections

def NetCDF_layers_to_raster(ncpath, layer_indexs = None,
                            cust_projection = None, cust_geotransform = None):
    """
    Extracts one or more layers from an HDF file and saves them as tifs

    """

    head, tail = os.path.split(ncpath)
    outraster_names = []

    return outraster_names


def convert_dtype(numpy_dtype_string):
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
    pass
