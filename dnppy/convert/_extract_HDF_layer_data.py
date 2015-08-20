__author__ = ['djjensen', 'jwely']

__all__ = ["_extract_HDF_layer_data"]

import gdal
import os

def _extract_HDF_layer_data(hdfpath, layer_indexs = None):
    """
    Extracts one or more layers from an HDF file and returns a dictionary with
    all the data available in the HDF layer for use in further format conversion
    to better supported formats.

    example:
    hdfpath = filepath to an hdf file. (any HDF 4 or 5 datatype)
    layer indexs = [1,2,3]

    the output dict will have keys :
                    ["MasterMetadata", "1", "2", "3"]

    where the "MasterMetadata" values very widely in format depending on
    data source, but might contain georeferencing information and the like.
    Each of the values for those integer keys will simply be a gdal.dataset
    object.

    this function is the first step in the chain for turning HDF data into
    geotiff. the next step is to build an established datatype

    :param hdfpath          filepath to any HDF formated file
    :param layer_indexs     list of integer index values for layers to extract
    """

    # output dict
    out_info = {}
    layer_names = []

    # open the HDF dataset
    hdf_dataset = gdal.Open(hdfpath)

    subdatasets = hdf_dataset.GetSubDatasets()

    # establish layer indices if left default
    if layer_indexs is None:
        layer_indexs = range(len(subdatasets))
    elif isinstance(layer_indexs, int):
        layer_indexs = [layer_indexs]

    # print a summary of the layer content
    print("Contents of {0}".format(os.path.basename(hdfpath)))
    for i, dataset_string in enumerate(subdatasets):
        print("  {0}  {1}".format(i, dataset_string[1]))
        if i in layer_indexs:
            layer_names.append(dataset_string[1])

    # give metadata info for the entire layer
    mdict = hdf_dataset.GetMetadata()
    out_info["MasterMetadata"] = mdict

    #for key in mdict:
       #print key," = ", mdict[key]

    # perform operation on each of the desired layers
    for layer in layer_indexs:
        subdataset  = gdal.Open(subdatasets[layer][0])
        out_info[layer] = subdataset

    return out_info



if __name__ == "__main__":
    #try MODIS
    #rasterpath = r"C:\Users\jwely\Desktop\troubleshooting\HDF_tests\MOD09A1.A2015033.h11v05.005.2015044233105.hdf"
    #_extract_HDF_layer_data(rasterpath)

    # try GPM
    #rasterpath = r"C:\Users\jwely\Desktop\troubleshooting\HDF_tests\3B-HHR-L.MS.MRG.3IMERG.20150401-S233000-E235959.1410.V03E.RT-H5"
    #_extract_HDF_layer_data(rasterpath)

    # try TRMM
    #rasterpath = r"C:\Users\jwely\Desktop\troubleshooting\HDF_tests\3B42.20140101.00.7.HDF"
    #_extract_HDF_layer_data(rasterpath)

    # try ASTER?
    #rasterpath = r"C:\Users\jwely\Desktop\troubleshooting\HDF_tests\AG100.v003.28.-098.0001.h5"
    #_extract_HDF_layer_data(rasterpath)

    # try VIIRS
    rasterpath = r"C:\Users\jwely\Desktop\troubleshooting\HDF_tests\GDNBO-SVDNB_npp_d20150626_t0132557_e0138361_b18964_c20150626174428799822_noaa_ops.h5"
    stuff = _extract_HDF_layer_data(rasterpath, [2, 4])

    print stuff[2].GetProjection()
    print stuff[2].GetGeoTransform()
    lat = stuff[2].ReadAsArray()
    lon = stuff[4].ReadAsArray()
    print lat[0, 0],lat[0, -1],lat[-1, 0],lat[-1, -1]
    print lon[0, 0],lon[0, -1],lon[-1, 0],lon[-1, -1]

