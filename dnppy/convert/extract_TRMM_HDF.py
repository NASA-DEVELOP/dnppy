__author__ = 'jwely'
__all__ = ["extract_TRMM_HDF"]

from dnppy import core
from datatype_library import *
from _extract_HDF_datatype import *

def extract_TRMM_HDF(hdf_list, layer_indexs, outdir, resolution):
    """
    Extracts TRMM products from HDF to tif.
    http://pmm.nasa.gov/data-access/data-products

    :param hdf_list:        list of hdf files or directory with hdfs
    :param layer_indexs:    list of integer layer indexs
    :param outdir:          directory to place outputs
    :param resolution:      The size of a pixel in degrees, either
                            "0.25", "0.5", "1.0", "5.0" depending on
                            the specific TRMM product you are extracting.
    :return:                a list of all files created as output

    """

    hdf_list = core.enf_filelist(hdf_list)
    output_filelist = []

    # load the GPM datatype from the library
    datatype = datatype_library()["TRMM_{0}_GLOBAL".format(resolution)]

    # for every hdf file in the input list
    for hdf in hdf_list:
        # extract layers and add the new filepaths to the output filelist
        hdf_output_filelist =  _extract_HDF_datatype(hdf, layer_indexs, outdir, datatype)
        output_filelist +=  hdf_output_filelist

    return output_filelist


if __name__ == "__main__":
    rasterpath = r"C:\Users\jwely\Desktop\troubleshooting\3B42.20140101.00.7.HDF"
    outdir     = r"C:\Users\jwely\Desktop\troubleshooting"
    extract_TRMM_HDF(rasterpath, [0], outdir, "0.25")