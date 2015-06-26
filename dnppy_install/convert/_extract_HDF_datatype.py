__author__ = 'jwely'
__all__ = ["_extract_HDF_datatype"]


from _extract_HDF_layer_data import _extract_HDF_layer_data
from _gdal_dataset_to_tif import _gdal_dataset_to_tif
from datatype_library import datatype_library

from dnppy import core


def _extract_HDF_datatype(hdf, layer_indexs, outdir, datatype):
    """
    This function wraps "_extract_HDF_layer_data" and "_gdal_dataset_to_tif"


    :param hdf:             a single hdf filepath
    :param layer_indexs:    list of int index values of layers to extract
    :param outdir:          filepath to output directory to place tifs
    :param datatype:
    :return:
    """

    # load the GPM datatype from the libarary
    datatype = datatype_library()["GPM_IMERG"]

    gpm_data = _extract_HDF_layer_data(hdf_list, layer_indexs)

    for li in layer_indexs:
        dataset = gpm_data[li]
        outpath = core.create_outname(outdir, hdf_list, str(li), "tif")
        print("creating dataset at {0}".format(outpath))
        _gdal_dataset_to_tif(dataset, outpath,
                            cust_projection = datatype.projectionTXT,
                            cust_geotransform = datatype.geotransform)


if __name__ == "__main__":
    rasterpath = r"C:\Users\jwely\Desktop\troubleshooting\3B-HHR-L.MS.MRG.3IMERG.20150401-S233000-E235959.1410.V03E.RT-H5"
    outdir     = r"C:\Users\jwely\Desktop\troubleshooting"
    extract_GPM_IMERG(rasterpath, [5], outdir)