__author__ = ['djjensen', 'jwely']

from dnppy import core
import gdal
import os

def HDF_layers_to_raster(hdfpath, layer_indexs = None,
                         cust_projection = None, cust_geotransform = None):
    """
    Extracts one or more layers from an HDF file and saves them as tifs. Please note
    that most HDF5 formats will REQUIRE a custom projection or custom geotransform
    to produce good outputs.

    :param hdfpath:             filepath to an HDF5 file
    :param layer_indexs:        a list of integer values or layer names to extract
                                leave "None" to return numpy arrays for ALL layers

    :param cust_geotransform    custom array of 6 values that specify geotransformation

    :return:                    dict with band names as keys and numpy arrays as values
    """

    head, tail = os.path.split(hdfpath)
    outraster_names = []

    # open the HDF dataset
    hdf_dataset = gdal.Open(hdfpath)
    subdatasets = hdf_dataset.GetSubDatasets()

    print("Contents of {0}".format(os.path.basename(hdfpath)))
    for i, dataset_string in enumerate(subdatasets):
        print("  {0}  {1}".format(i, dataset_string[1]))

    if layer_indexs is None:
        layer_indexs = range(len(subdatasets))
    elif isinstance(layer_indexs, int):
        layer_indexs = [layer_indexs]

    # perform operation on each of the desired layers
    for i,layer in enumerate(layer_indexs):
        subdataset   = gdal.Open(subdatasets[layer][0])
        projection   = subdataset.GetProjection()
        geotransform = subdataset.GetGeoTransform()
        numpy_array  = subdataset.ReadAsArray()
        datatype     = numpy_array.dtype

        print projection
        print geotransform
        print


        # assemble raster properties based on dimensions
        dims = len(numpy_array.shape)
        if dims == 1:
            break

        elif dims == 2:
            xsize, ysize = numpy_array.shape
            bands = 1

        elif dims == 3:
            bands, xsize, ysize = numpy_array.shape

        # build the new geotiff
        gtiff       = gdal.GetDriverByName("GTiff")
        outraster   = core.create_outname(head, tail, layer, "tif")
        outdataset  = gtiff.Create(outraster, xsize, ysize, bands,  _convert_dtype(datatype))

        # if there is no projection found in the HDF metadata, assume its in WGS_1984
        if cust_projection is not None:
            outdataset.SetProjection(cust_projection)
        else:
            print("applying projection {0}".format(projection))
            outdataset.SetProjection(projection)

        # set the geometric transform
        if cust_geotransform is not None:
            outdataset.SetGeoTransform(cust_geotransform)
        else:
            print("applying geotransform {0}".format(geotransform))
            outdataset.SetGeoTransform(geotransform)

        # save the raster layer one band at a time
        if dims == 2:
            outdataset.GetRasterBand(1).WriteArray(numpy_array, xoff = 0, yoff = 0)

        elif dims == 3:
            for i in range(bands):
                outdataset.GetRasterBand(i+1).WriteArray(numpy_array[i,:,:])

        del outdataset
        outraster_names.append(outraster)

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
    # try MODIS
    #rasterpath = r"C:\Users\jwely\Desktop\troubleshooting\MOD09A1.A2015033.h11v05.005.2015044233105.hdf"
    #HDF_layers_to_raster(rasterpath)

    # try GPM
    #rasterpath = r"C:\Users\jwely\Desktop\troubleshooting\3B-HHR-L.MS.MRG.3IMERG.20150401-S233000-E235959.1410.V03E.RT-H5"
    #HDF_layers_to_raster(rasterpath, None, cust_geotransform = geotransforms.TRMM())

    # try TRMM
    #rasterpath = r"C:\Users\jwely\Desktop\troubleshooting\3B42.20140101.00.7.HDF"
    #HDF_layers_to_raster(rasterpath, cust_geotransform = geotransforms.TRMM())

    # try something else?
    #rasterpath = r"C:\Users\jwely\Desktop\troubleshooting\AG100.v003.28.-098.0001.h5"
    #HDF_layers_to_raster(rasterpath)
