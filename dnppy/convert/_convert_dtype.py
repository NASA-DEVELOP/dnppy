__author__ = 'jwely'

import gdal

def _convert_dtype(numpy_dtype_string):
    """
    converts numpy dtype to a gdal data type object

    :param numpy_dtype_string
    :return gdal_datatype_object:
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