__author__ = 'jwely'

import arcpy


def gap_fill_interpolate(in_rasterpath, out_rasterpath):
    """
    Fills gaps in raster data by spatial interpolation. This should only
    be used to fill small gaps in continuous datasets (like a DEM), and in
    instances where it makes sense. This function first converts all pixels
    in a raster which are not NoData to points, then performs a "kriging"
    interpolation on the point data to rebuild a uniform grid with a value
    at every location, thus filling gaps.

    inputs:
    """

    # make a point shapefile version of input raster
    shapepath = in_rasterpath + ".shp"
    arcpy.RasterToPoint_conversion(in_rasterpath, shapepath)




