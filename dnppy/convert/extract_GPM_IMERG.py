__author__ = 'jwely'
__all__ = ["extract_GPM_IMERG"]

from dnppy import core
from datatype_library import *
from _extract_HDF_datatype import *

def extract_GPM_IMERG(hdf_list, layer_indexs, outdir, resolution):
    """
    Extracts GPM_IMERG data from its HDF5 format.

    :param hdf_list:        list of hdf files or directory with hdfs
    :param layer_indexs:    list of integer layer indexs
    :param outdir:          directory to place outputs
    :param resolution:      The size of a pixel in degrees, either
                            "0.1" or "0.15" depending on GPM product.
    :return:                a list of all files created as output

    Typical contents of a GPM HDF are:

    == =========== ================================ ==============
    ID  layer shape Layer name                       data type
    == =========== ================================ ==============
    0  [3600x1800] HQobservationTime                (16-bit int)
    1  [3600x1800] HQprecipSource                   (16-bit int)
    2  [3600x1800] HQprecipitation                  (32-bit float)
    3  [3600x1800] IRkalmanFilterWeight             (16-bit int)
    4  [3600x1800] IRprecipitation                  (32-bit float)
    5  [3600x1800] precipitationCal                 (32-bit float)
    6  [3600x1800] precipitationUncal               (32-bit float)
    7  [3600x1800] probabilityLiquidPrecipitation   (16-bit int)
    8  [3600x1800] randomError                      (32-bit float)
    == =========== ================================ ==============
    """

    hdf_list = core.enf_filelist(hdf_list)
    output_filelist = []

    # load the GPM datatype from the library
    datatype = datatype_library()["GPM_IMERG_{0}_GLOBAL".format(resolution)]

    # for every hdf file in the input list
    for hdf in hdf_list:
        # extract layers and add the new filepaths to the output filelist
        hdf_output_filelist =  _extract_HDF_datatype(hdf, layer_indexs, outdir, datatype)
        output_filelist +=  hdf_output_filelist

    return output_filelist


if __name__ == "__main__":
    rasterpath = r"C:\Users\jwely\Desktop\troubleshooting\3B-HHR-L.MS.MRG.3IMERG.20150401-S233000-E235959.1410.V03E.RT-H5"
    outdir     = r"C:\Users\jwely\Desktop\troubleshooting"
    extract_GPM_IMERG(rasterpath, [5], outdir, "0.1")