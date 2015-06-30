__author__ = 'jwely'
__all__ = ["_extract_NetCDF_datatype"]

from _extract_NetCDF_layer_data import *
from _gdal_dataset_to_tif import *

from dnppy import core

def _extract_NetCDF_datatype(netcdf, layer_indexs, outdir, datatype, force_custom = False):
    """
    This function wraps "_extract_NetCDF_layer_data" and "_gdal_dataset_to_tif"

    :param netcdf:          a single netcdf filepath
    :param layer_indexs:    list of int index values of layers to extract
    :param outdir:          filepath to output directory to place tifs
    :param datatype:        a dnppy.convert.datatype object created from an
                            entry in the datatype_library.csv
    :param force_custom:    if True, this will force the data to take on the
                            projection and geotransform attributes from
                            the datatype object, even if valid projection
                            and geotransform info can be pulled from the gdal
                            dataset. Should almost never be True.

    :return:                list of filepaths to output files
    """

    output_filelist = []

    data = _extract_NetCDF_layer_data(netcdf, layer_indexs)

    for layer_index in layer_indexs:
        dataset = data[layer_index]
        outpath = core.create_outname(outdir, netcdf, str(layer_index), "tif")
        print("creating dataset at {0}".format(outpath))
        _gdal_dataset_to_tif(dataset, outpath,
                            cust_projection = datatype.projectionTXT,
                            cust_geotransform = datatype.geotransform,
                            force_custom = force_custom)

        output_filelist.append(outpath)

    return output_filelist