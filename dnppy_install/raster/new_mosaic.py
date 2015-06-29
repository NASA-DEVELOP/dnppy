__author__ = 'jwely'
__all__ = ["new_mosaci"]

from enf_rastlist import enf_rastlist
from to_numpy import to_numpy
from from_numpy import from_numpy
import numpy
import arcpy
import os


def new_mosaic(rasterpaths, output_path, mosaic_method = None, cell_size = None, number_of_bands = None):
    """
    Simply creates a new raster dataset mosaic of input rasters by wrapping the
    arcpy.MosaicToNewRaster_management function. learn more about the fields here

    http://help.arcgis.com/en/arcgisdesktop/10.0/help/index.html#//001700000098000000

    rasterpaths         list of complete filepaths to raster data to mosaic
    output_path         place to save new mosaic raster dataset
    mosaic_method       options are "FIRST", "LAST", "BLEND", "MEAN", "MINIMUM","MAXIMUM"
    cell_size           of format "[cellwidth] [cellheight]" in the appropriate linear units,
                        usually meters.
    """

    # set up input parameters
    if mosaic_method is None:
        mosaic_method = "FIRST"

    if cell_size is not None:
        print("using custom cell size of '{0}'".format(cell_size))

    if number_of_bands is None:
        number_of_bands = 1

    rasterpaths = enf_rastlist(rasterpaths)

    # get some metadata about the first raster in the mosaic
    numpy, meta = to_numpy(rasterpaths[0])

    # check output directories and set up inputs for arcpy function
    outdir, outname = os.path.split(output_path)

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    arcpy.MosaicToNewRaster_management(rasterpaths, outdir, outname,
                                        None,                # coordinate system
                                        meta.pixel_type,
                                        cell_size,
                                        str(number_of_bands),
                                        mosaic_method = mosaic_method)

    print("Created raster mosaic at {0}".format(output_path))
    return output_path



if __name__ == "__main__":

    adir = r"C:\Users\jwely\Desktop\Team_Projects\2015_sumer_CO_water\LiDAR_Format_Trial"
    outpath = os.path.join(adir, "mosaic", "test_mosaic.tif")
    new_mosaic(adir, outpath, mosaic_method = "FIRST" )

    rast, meta = to_numpy(outpath)
    rast.data[rast.data == numpy.nan] = 0
    rast.data[(2452 >= rast.data) & (rast.data >= 2450)] = numpy.nan
    rast.data[(2430 >= rast.data) & (rast.data >= 2428)] = numpy.nan
    rast.data[(2350 >= rast.data) & (rast.data >= 2348)] = numpy.nan
    from_numpy(rast, meta, outpath.replace(".tif","_gaps.tif"))