__author__ = 'jwely'

import gdal
import gdalconst
gdal.UseExceptions()
import struct

def extract_HDF5_layer(rasterpath, band_num, output_path):

    # open the raster file
    dataset = gdal.Open(rasterpath, gdalconst.GA_ReadOnly)
    driver  = dataset.GetDriver()
    band    = dataset.GetRasterBand(band_num)

    # reading the raster properties
    projection = dataset.GetProjection()
    geotransform = dataset.GetGeoTransform()
    xsize = band.GetXsize()
    ysize = band.GetYsize()
    datatype = band.DataType
    typename = gdal.GetDataTypeName(datatype)

    # reading the data
    values = band.ReadRaster(0, 0, xsize, ysize, xsize, ysize, datatype)

    typenames = {'Byte':'B',
                 'UInt16':'H',
                 'Int16':'h',
                 'UInt32':'I',
                 'Int32':'i',
                 'Float32':'f',
                 'Float64':'d'}

    values = struct.unpack(typenames[typename] * xsize * ysize, values)

    gtiff = gdal.GetDriverByName("GTiff")
    output_dataset = gtiff.Create(output_path, xsize, ysize, 4)
    output_dataset.SetProjection(projection)
    output_dataset.SetGeoTransform(geotransform)
    output_dataset.GetRasterBand(band_num).WriteRaster(0, 0, xsize, ysize, "")
    return

if __name__ == "__main__":
    rasterpath = r"C:\Users\jwely\Desktop\dnppytest\raw\GPM\2015-04-01\3B-HHR-L.MS.MRG.3IMERG.20150401-S000000-E002959.0000.V03E.RT-H5"
    band_num = 1
    output_path = r"C:\Users\jwely\Desktop\dnppytest\raw\GPM\2015-04-01\extracted\3B-HHR-L.MS.MRG.3IMERG.20150401-S000000-E002959.0000.V03E.RT-H5_01.tif"
    extract_HDF5_layer(rasterpath, band_num, output_path)