
__author__ = 'jwely'
__all__ = ["gap_fill_interpolate"]

from dnppy import core
from to_numpy import to_numpy
from is_rast import is_rast
import arcpy
import os


def gap_fill_interpolate(in_rasterpath, out_rasterpath, model = None,
                         max_cell_dist = None, min_points = None):
    """
    Fills gaps in raster data by spatial kriging interpolation. This should only
    be used to fill small gaps in continuous datasets (like a DEM), and in
    instances where it makes sense. This function creates a feature class
    layer of points where pixels are not NoData, then performs a "kriging"
    interpolation on the point data to rebuild a uniform grid with a value
    at every location, thus filling gaps.

    WARNING: This script is processing intensive and may take a while to run
    even for modestly sized datasets.

    :param in_rasterpath:   input filepath to raster to fill gaps
    :param out_rasterpath:  filepath to store output gap filled raster in
    :param model:           type of kriging model to run, options include
                            "SPHERICAL", "CIRCULAR", "EXPONENTIAL",
                            "GAUSSIAN", and "LINEAR"
    :param max_cell_dist:   The maximum number of cells to interpolate between,
                            data gaps which do not have at least "min_points"
                            points within this distance will not be filled.
    :param min_points:      Minimum number of surrounding points to use in determining
                            value at missing cell.

    :return out_rasterpath: Returns path to file created by this function
    """

    # check inputs
    if not is_rast(in_rasterpath):
        raise Exception("input raster path {0} is invalid!".format(in_rasterpath))

    if max_cell_dist is None:
        max_cell_dist = 10

    if min_points is None:
        min_points = 4

    if model is None:
        model = "SPHERICAL"

    # set environments
    arcpy.env.overwriteOutput = True
    arcpy.env.snapRaster = in_rasterpath
    arcpy.CheckOutExtension("Spatial")


    # make a point shapefile version of input raster
    print("Creating point grid from input raster")
    head, tail = os.path.split(in_rasterpath)
    shp_path = core.create_outname(head, tail, "shp", "shp")
    dbf_path = shp_path.replace(".shp",".dbf")
    field = "GRID_CODE"

    arcpy.RasterToPoint_conversion(in_rasterpath, shp_path, "VALUE")

    # find the bad rows who GRID_CODE is 1, these should be NoData
    print("Finding points with NoData entries")
    bad_row_FIDs = []

    rows = arcpy.UpdateCursor(dbf_path)

    for row in rows:
        grid_code = getattr(row, field)
        if grid_code == 1:
            bad_row_FIDs.append(row.FID)
    del rows

    # go back through the list and perform the deletions
    numbad = len(bad_row_FIDs)
    print("Deleting {0} points with NoData values".format(numbad))
    rows = arcpy.UpdateCursor(dbf_path)
    for i, row in enumerate(rows):
        if row.FID in bad_row_FIDs:
            rows.deleteRow(row)

    # set up the parameters for kriging
    print("Setting up for kriging")

    _, meta = to_numpy(in_rasterpath)

    model       = model
    cell_size   = meta.cellHeight                           # from input raster
    lagSize     = None
    majorRange  = None
    partialSill = None
    nugget      = None
    distance    = float(cell_size) * float(max_cell_dist)   # fn input
    min_points  = min_points                                # fn input

    a = arcpy.sa.KrigingModelOrdinary()
    kmodel = arcpy.sa.KrigingModelOrdinary("SPHERICAL",
                                           lagSize = lagSize,
                                           majorRange = majorRange,
                                           partialSill = partialSill,
                                           nugget = nugget)

    kradius = arcpy.sa.RadiusFixed(distance = distance,
                                   minNumberOfPoints = min_points)

    # execute kriging
    print("Performing interpolation by kriging, this may take a while!")
    outkriging = arcpy.sa.Kriging(shp_path, field, kmodel,
                                  cell_size = cell_size,
                                  search_radius = kradius)
    outkriging.save(out_rasterpath)

    return out_rasterpath


# testing area
if __name__ == "__main__":

    inraster  = r"C:\Users\jwely\Desktop\Team_Projects\2015_sumer_CO_water\LiDAR_Format_Trial\mosaic\test_mosaic_gaps.tif"
    outraster = r"C:\Users\jwely\Desktop\Team_Projects\2015_sumer_CO_water\LiDAR_Format_Trial\mosaic\test_mosaic_filled.tif"
    gap_fill_interpolate(inraster, outraster)