__author__ = ["jwely", "djjensen"]
__all__ = ["gap_fill_temporal"]

import os

from dnppy import core
from enf_rastlist import *
from to_numpy import *
from from_numpy import *
from raster_fig import *


def gap_fill_temporal(rasterlist, outdir = None, continuous = True,  NoData_Value = None):
    """
    This function is designed to input a time sequence of rasters with partial voids and
    output a copy of each input image with every pixel equal to the last good value taken.
    This function will step forward in time through each raster and fill voids from the values
    of previous rasters. The resulting output image will contain all the data that was in the
    original image, with the voids filled with older data. A second output image will be
    generated where the pixel values are equal to the age of each pixel in the image. So
    if a void was filled with data that's 5 days old, the "age" raster will have a value of
    "5" at that location.

    Inputs:
    :param rasterlist:  a list of filepaths for rasters with which to fill gaps. THESE IMAGES
                        MUST BE ORDERED FROM OLDEST TO NEWEST (ascending time).
    :param outdir:      the path to the desired output folder, if left "None", outputs will be
                        saved right next to respective inputs.
    :param continuous:  if "True" an output raster will be generated for every single input raster,
                        which can be used to fill gaps in an entire time series. So, for example
                        output raster 2 will have all the good points in input raster 2, with gaps
                        filled with data from raster 1. output raster 3 will then be gap filled with
                        output raster 2, which might contain some fill values from raster 1, and so
                        forth. If "False" an output raster will only be generated for the LAST raster
                        in the input rasterlist.

    :returns            a list of filepaths to new files created by this function.
    """

    # enforce the list of rasters to ensure it's sanitized
    rasterlist = enf_rastlist(rasterlist)

    # create an empty list to store output arrays in
    output_filelist = []

    # grab the first raster, then start stepping through the list
    old_rast, old_meta = to_numpy(rasterlist[0])
    rastfig = raster_fig(old_rast)

    for i, araster in enumerate(rasterlist[1:]):

        new_rast, new_meta = to_numpy(araster)

        # combine new and old data and mask matrices
        outrast = new_rast
        outrast.data[new_rast.mask] = old_rast.data[new_rast.mask]
        outrast.mask[new_rast.mask] = old_rast.mask[new_rast.mask]

        # only save output if continuous is true or is last raster in series
        if continuous is True or i == (len(rasterlist[1:]) - 1):

            # create output name and save it
            if outdir is None:
                this_outdir = os.path.dirname(araster)
            else:
                this_outdir = outdir

            # update the figure
            rastfig.update_fig(outrast)

            outpath = core.create_outname(this_outdir, araster, "gft", "tif")
            print("Filled gaps in {0}".format(os.path.basename(araster)))
            from_numpy(outrast, new_meta, outpath, NoData_Value)
            output_filelist.append(outpath)

        # prepare for next time step by setting current to old
        old_rast = new_rast

    return output_filelist



if __name__ == "__main__":
    from null_set_range import *
    rastdir = r"C:\Users\jwely\Desktop\troubleshooting\Bender_TX_data\2010-11"
    rastlist = core.list_files(True, rastdir,["LST"], ["gft"])
    outlist = gap_fill_temporal(rastlist)
    null_set_range(outlist,low_thresh = -100)
