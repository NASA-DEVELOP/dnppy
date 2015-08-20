__author__ = ['jwely']
__all__ = ["_extract_NetCDF_layer_data"]

import gdal
import os

def _extract_NetCDF_layer_data(ncpath, layer_indexs = None):
    """
    Extracts one or more layers from an NetCDF file and returns a dictionary with
    all the data available in the NetCDF layer for use in further format conversion
    to better supported formats.

    example:
    ncpath = filepath to an NetCDF file. (any HDF 4 or 5 datatype)
    layer indexs = [1,2,3]

    the output dict will have keys :
                    ["MasterMetadata", "1", "2", "3"]

    where the "MasterMetadata" values very widely in format depending on
    data source, but might contain georeferencing information and the like.
    Each of the values for those integer keys will simply be a gdal.dataset
    object.

    this function is the first step in the chain for turning HDF data into
    geotiff. the next step is to build an established datatype

    :param ncpath          filepath to any NetCDF formated file
    :param layer_indexs     list of integer index values for layers to extract
    """

    # output dict
    out_info = {}
    layer_names = []

    # opening the netcdf dataset
    nc_dataset = gdal.Open('NETCDF:"{0}"'.format(ncpath))

    # if the netcdf has subdatasets
    if nc_dataset.GetSubDatasets():

        # build master metadata
        mdict = nc_dataset.GetMetadata_Dict()
        out_info["MasterMetadata"] = mdict

        subdatasets = nc_dataset.GetSubDatasets()

        # set layer indices if they were left default
        if layer_indexs is None:
            layer_indexs = range(len(subdatasets))
        elif isinstance(layer_indexs, int):
            layer_indexs = [layer_indexs]

        # print a summary of the layer content
        print("Contents of {0}".format(os.path.basename(ncpath)))
        for i, dataset_string in enumerate(subdatasets):
            print("  {0}  {1}".format(i, dataset_string[1]))
            if i in layer_indexs:
                layer_names.append(dataset_string[1])

        # grab the subdatasets
        for layer in layer_indexs:
            subdataset = gdal.Open(subdatasets[layer][0])
            out_info[layer] = subdataset


    # if only one layer exists in the netcdf
    else:
        # build master metadata
        mdict = nc_dataset.GetMetadata_Dict()
        out_info["MasterMetadata"] = mdict

        # grab the data layer
        out_info[0] = nc_dataset


    # print some of the master metadata
    #for key in mdict:
    #    print key," = ", mdict[key]

    return out_info


if __name__ == "__main__":
    # try some MPE netcdf files
    ncfile = r"C:\Users\jwely\Desktop\troubleshooting\MPE\nws_precip_conus_20150101.nc"

    # try some SMOS netcdf
    ncfile = r"C:\Users\jwely\Desktop\troubleshooting\SMOS\_NRTSM003D025A_ALL.nc"
    out = _extract_NetCDF_layer_data(ncfile)
    print out[0].GetGeoTransform()

