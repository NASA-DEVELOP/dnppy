__author__ = 'jwely'

from dnppy import core
from enf_rastlist import enf_rastlist

import os
import arcpy
from arcpy.sa import ExtractByMask

def clip_to_shape(rasterlist, shapefile, outdir = False):
    """
     Simple batch clipping script to clip rasters to shapefiles.

     Inputs:
       rasterlist      single file, list of files, or directory for which to clip rasters
       shapefile       shapefile to which rasters will be clipped
       outdir          desired output directory. If no output directory is specified, the
                       new files will simply have '_c' added as a suffix.
    """

    rasterlist = enf_rastlist(rasterlist)

    # ensure output directorycore.exists
    if outdir and not os.path.exists(outdir):
        os.makedirs(outdir)

    for raster in rasterlist:

        # create output filename with "c" suffix
        outname = core.create_outname(outdir,raster,'c')

        # perform double clip , first using clip_management (preserves no data values)
        # then using arcpy.sa module which can actually do clipping geometry unlike the management tool.
        arcpy.Clip_management(raster, "#", outname, shapefile, "ClippingGeometry")
        out = ExtractByMask(outname, shapefile)
        out.save(outname)
        print("Clipped and saved: {0}".format(outname))

    return
