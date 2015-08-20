__author__ = 'jwely'
__all__ = ["extract_MPE_NetCDF"]

from dnppy import core
from datatype_library import *
from _extract_NetCDF_layer_data import *
from _gdal_dataset_to_tif import *


def extract_MPE_NetCDF(netcdf_list, layer_indexs, outdir, area):
    """
    extracts SMOS data from its native NetCDF format.

    :param netcdf_list:     list of hdf files or directory with netcdfs
    :param layer_indexs:    list of integer layer indexs
    :param outdir:          directory to place outputs
    :param area:            presently only suports "CONUS"

    :return:                a list of all files created as output
    """

    netcdf_list = core.enf_filelist(netcdf_list)
    output_filelist = []

    # load the GPM datatype from the library
    dtype = datatype_library()["MPE_HRAP_{0}".format(area)]

    # for every hdf file in the input list
    for netcdf in netcdf_list:
        data = _extract_NetCDF_layer_data(netcdf, layer_indexs)

        for layer_index in layer_indexs:

            dataset = data[layer_index]
            outpath = core.create_outname(outdir, netcdf, str(layer_index), "tif")

            print("creating dataset at {0}".format(outpath))

            _gdal_dataset_to_tif(dataset, outpath,
                                cust_projection = dtype.projectionTXT,
                                cust_geotransform = dtype.geotransform,
                                force_custom = False,
                                nodata_value = -1)

            output_filelist.append(outpath)

    return output_filelist


if __name__ == "__main__":

    filepath = r"C:\Users\jwely\Desktop\troubleshooting\MPE\nws_precip_conus_20150101.nc"
    od = r"C:\Users\jwely\Desktop\troubleshooting\MPE"
    extract_MPE_NetCDF(filepath, [0], od, "CONUS")